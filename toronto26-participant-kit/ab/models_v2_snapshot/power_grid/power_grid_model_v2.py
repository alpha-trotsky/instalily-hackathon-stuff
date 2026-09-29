"""power_grid gray-box model v2 (round 2 modeler). Starts from v1 (greybox/power_grid_model.py) and applies the
round-2 diagnosis (plans/power_grid-round2-diagnosis.md §5):

  1. frequency = first-order lag to a static droop map (no governor/secondary integral loop, B23-B25)
  2. load = bounded (soft-clipped) resonator: floor Lmin, ceiling Lmin + Lspan (B20); price level flattens for p > 1.5
     via a separate slope on the negative side of `up` (B22)
  3. share: renewable power P = smax(P_free - kR*Rs, floor), share = P / L (B26); release memory B kept (B28)
  4. reset: the initial-load reference is the model's own price-0.8 equilibrium, not a fitted Lref0 (B19)

Controls (normalize): p = price_signal (0..2), r = reserve_dispatch / 150, ch = charging_allowance, x = interconnector.
up = (1.5 - p) / 1.5 (0 at recovery 1.5, 1 at price 0, 0.467 at the reset reference 0.8, -0.33 at price 2).

BASE
  load   upl = up (up >= 0) or rn*up (up < 0)
         yL <- yL + kL (cL + wLp upl - yL)
         Llin = yL + wLi upl + g1 o + (L0 - Leq08) qi^(t+1),   Leq08 = cL + (wLp + wLi) up(0.8)
         L = softclip(Llin, Lmin, Lmin + Lspan)
  reserve Rd = 150 r (M2 is inactive: three nulls, H3);  Rs = smooth-min(Rd, Rsat)
  share  Pfree = L cS (1 - wSx cx - wSx2 cx^2)(1 + wSL (L-100)/100),  cx = 1 - x
         Pfl   = F0 (1 - F1 Rs/150)(1 - Fx cx)
         P = smax(Pfree - kR Rs, Pfl) (only when Rd > 0; else Pfree)
         S* = P/L * exp(wSB (B - D)) * [m3];  S <- S + kS (S* - S);  D = max(f-50, 0),  B <- B + kb (D - B)
  freq   f* = f0 - bL (L-100) - bD (L - Lf) + br Rs - (ax1 cx + ax2 cx^2)(1 - kx Rs/150)
         f <- f + kf (f* - f), clipped [FMIN, FMAX];   Lf <- Lf + kd (L - Lf)  (lagged load: transient droop)
MECHANISMS (gain 0 = off)
  m1  damped price-step resonator (as v1): kap = kap1 exp(kk1 up), rho = rho1^(1 + kr1 up)
         s <- rho s - kap o + du ;  o <- o + s ;  load term g1 o
  m3  interconnector heat (as v1): H <- H + a3 (S x - H);  share *= 1 - g3 max(H - h3, 0)
"""
import math
import numpy as np

OBSERVABLES = ('load', 'frequency', 'renewable_share')
CONTROLS = ('price_signal', 'reserve_dispatch', 'charging_allowance', 'interconnector')
UNITS = {'load': 'linear', 'frequency': 'linear', 'renewable_share': 'linear'}
NOISE = {'load': 0.55, 'frequency': 0.019, 'renewable_share': 0.0038}   # 0.25 x score sigma
CLAMP = {'load': [20.0, 300.0], 'frequency': [47.0, 53.0], 'renewable_share': [0.0, 1.0]}
FMIN, FMAX = 47.97, 52.03
UP_RESET = (1.5 - 0.8) / 1.5
WCLIP = 3.0     # load soft-clip width
WR = 8.0        # reserve saturation smoothing
WP = 1.0        # share floor smoothing

SPEC = {
    # load
    'cL': (94.6, 'free'), 'wLp': (8.4, 'free'), 'wLi': (22.8, 'free'), 'kL': (0.49, 'unit'), 'rn': (0.99, 'unit'),
    'qi': (0.94, 'unit'), 'Lmin': (64.0, 'pos'), 'Lspan': (106.0, 'pos'),
    # share
    'cS': (0.362, 'free'), 'wSx': (0.22, 'free'), 'wSx2': (0.32, 'free'), 'wSL': (0.064, 'free'),
    'kS': (0.9, 'unit'), 'wSB': (0.2, 'free'), 'kb': (0.32, 'unit'),
    'kR': (0.7, 'pos'), 'F0': (11.0, 'pos'), 'F1': (0.35, 'unit'), 'Fx': (0.3, 'unit'),
    # frequency
    'f0': (50.05, 'free'), 'bL': (0.026, 'pos'), 'bD': (0.015, 'free'), 'kd': (0.3, 'unit'),
    'br': (0.0145, 'pos'), 'Rsat': (125.0, 'pos'), 'ax1': (1.2, 'free'), 'ax2': (-0.4, 'free'), 'kx': (0.5, 'unit'),
    'kf': (0.5, 'unit'),
    # m1
    'rho1': (0.963, 'unit'), 'kap1': (0.0068, 'unit'), 'g1': (3.77, 'free'), 'kk1': (0.5, 'free'), 'kr1': (0.0, 'free'),
    # m3
    'a3': (0.053, 'unit'), 'g3': (1.34, 'free'), 'h3': (0.339, 'free'),
}
MODULES = {
    'm1': (['rho1', 'kap1', 'g1', 'kk1', 'kr1'], {'g1': 0.0}),
    'm3': (['a3', 'g3', 'h3'], {'g3': 0.0}),
}


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(raw, 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        v = min(max(value, 1e-9), 1 - 1e-9)
        return math.log(v / (1 - v))
    if kind == 'pos':
        return math.log(max(value, 1e-300))
    return value


def normalize(action, bounds):
    out = []
    for c in CONTROLS:
        lo, hi = bounds.get(c, (0.0, 150.0 if c == 'reserve_dispatch' else 2.0))
        v = min(max(float(action[c]), lo), hi)
        out.append(v / 150.0 if c == 'reserve_dispatch' else v)
    return tuple(out)


def _clip(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _sp(z, w):
    """softplus with width w: ~max(z, 0)."""
    z = z / w
    if z > 30.0:
        return z * w
    if z < -30.0:
        return 0.0
    return w * math.log1p(math.exp(z))


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 3))
    cL, wLp, wLi, kL, rn, qi = p['cL'], p['wLp'], p['wLi'], p['kL'], p['rn'], min(p['qi'], 0.99)
    Lmin, Lmax = _clip(p['Lmin'], 20.0, 150.0), _clip(p['Lmin'], 20.0, 150.0) + _clip(p['Lspan'], 10.0, 200.0)
    cS, wSx, wSx2, wSL, kS = p['cS'], p['wSx'], p['wSx2'], p['wSL'], p['kS']
    wSB, kb = _clip(p['wSB'], -3.0, 3.0), p['kb']
    kR, F0, F1, Fx = _clip(p['kR'], 0.0, 3.0), _clip(p['F0'], 0.0, 60.0), p['F1'], p['Fx']
    f0, bL, bD, kd = p['f0'], _clip(p['bL'], 0.0, 0.2), _clip(p['bD'], -0.2, 0.2), p['kd']
    br, Rsat = _clip(p['br'], 0.0, 0.05), _clip(p['Rsat'], 10.0, 400.0)
    ax1, ax2, kx, kf = _clip(p['ax1'], -5.0, 5.0), _clip(p['ax2'], -5.0, 5.0), p['kx'], p['kf']
    rho1, kap1, g1 = p['rho1'], min(p['kap1'], 0.5), p['g1']
    kk1, kr1 = _clip(p['kk1'], -3.0, 3.0), _clip(p['kr1'], -3.0, 10.0)
    a3, g3, h3 = p['a3'], p['g3'], p['h3']
    upl0 = UP_RESET
    Leq08 = cL + (wLp + wLi) * upl0
    try:
        L0 = float(initial['load'])
        f0r = float(initial['frequency'])
    except (KeyError, TypeError, ValueError):
        L0, f0r = Leq08, 50.0
    if not (math.isfinite(L0) and math.isfinite(f0r)):
        L0, f0r = Leq08, 50.0
    dev0 = _clip(L0 - Leq08, -60.0, 60.0)
    yL = cL + wLp * upl0
    up_prev = UP_RESET
    s = o = 0.0
    S = cS
    H = S
    f = _clip(f0r, FMIN, FMAX)
    Lf = _clip(L0, 20.0, 300.0)
    B = 0.0
    decay = 1.0
    out = np.empty((T, 3))
    for t in range(T):
        pr, r, ch, x = actions[t]
        up = (1.5 - pr) / 1.5
        upl = up if up >= 0.0 else rn * up
        # --- load
        yL += kL * (cL + wLp * upl - yL)
        du = up - up_prev
        up_prev = up
        if g1 != 0.0:
            kap = _clip(kap1 * math.exp(kk1 * up), 1e-6, 0.5)
            rho = _clip(rho1 ** (1.0 + kr1 * up), 0.0, 0.995) if rho1 > 0.0 else 0.0
            s = rho * s - kap * o + du
            o = _clip(o + s, -50.0, 50.0)
            s = _clip(s, -50.0, 50.0)
        decay *= qi
        Llin = _clip(yL + wLi * upl + g1 * o + dev0 * decay, -200.0, 500.0)
        L = Lmin + _sp(Llin - Lmin, WCLIP) - _sp(Llin - Lmax, WCLIP)
        L = _clip(L, 20.0, 300.0)
        # --- reserve
        Rd = 150.0 * r
        Rs = 0.5 * (Rd + Rsat - math.sqrt((Rd - Rsat) ** 2 + WR * WR)) if Rd > 0.0 else 0.0
        Rs = max(Rs, 0.0)
        # --- share
        D = f - 50.0 if f > 50.0 else 0.0
        cx = 1.0 - x
        Pfree = L * cS * _clip(1.0 - wSx * cx - wSx2 * cx * cx, 0.0, 3.0) * _clip(1.0 + wSL * (L - 100.0) / 100.0, 0.05, 5.0)
        if Rd > 0.0:
            Pfl = F0 * (1.0 - F1 * Rs / 150.0) * (1.0 - Fx * cx)
            Pr = Pfree - kR * Rs
            P = Pfl + _sp(Pr - Pfl, WP)
        else:
            P = Pfree
        fac = math.exp(_clip(wSB * (B - D), -3.0, 3.0))
        if g3 != 0.0:
            fac *= _clip(1.0 - g3 * max(H - h3, 0.0), 0.0, 1.0)
        St = _clip(P / L * fac, 0.0, 1.0)
        S += kS * (St - S)
        B += kb * (D - B)
        if g3 != 0.0:
            H += a3 * (S * x - H)
        # --- frequency
        fs = f0 - bL * (L - 100.0) - bD * (L - Lf) + br * Rs - (ax1 * cx + ax2 * cx * cx) * (1.0 - kx * Rs / 150.0)
        f += kf * (fs - f)
        f = _clip(f, FMIN, FMAX)
        Lf += kd * (L - Lf)
        out[t, 0] = L
        out[t, 1] = f
        out[t, 2] = S
    return out
