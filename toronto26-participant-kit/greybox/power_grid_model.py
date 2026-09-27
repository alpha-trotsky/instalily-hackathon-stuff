"""power_grid gray-box model v1 (Phase C modeler). Based on the reviewer's v1s (multiplicative share, no cap;
fits/power_grid/review/pg_model_v1s.py) with the review's structural fixes G3, G5, G6, G8. The v0 researcher model is
kept at fits/power_grid/power_grid_model_v0.py.

Controls (normalize): p = price_signal (physical, 0..2), r = reserve_dispatch / 150, ch = charging_allowance,
x = interconnector (physical, 0..1).  up = (1.5 - p) / 1.5 is the demand-raising price coordinate
(0 at recovery 1.5, 1 at pulse 0, 0.467 at the reset reference price 0.8, -0.33 at price 2).

BASE (always on)
  load     L = yL + wLi*up + [M1 resonator] + [M2 charging draw] + (L0 - Lref0)*qi^(t+1)
           yL <- yL + kL (cL + wLp*up - yL)          price-dependent demand level
           Reset convention: price before tick 0 is 0.8, yL starts at its 0.8 equilibrium.  The initial load
           reading's deviation from the fixed reference Lref0 fades geometrically (G8).
  reserve  Rd = r * avail  (avail = 1 without M2)
  share    S = cS * (1 - wSx(1-x) - wSx2(1-x)^2) * (1 + wSL (L-100)/100) * exp(-wSG G/100)
               * exp(wSB (B - D)) / (1 + wSr Rd) * [M3 curtailment]          (multiplicative, no cap)
           D = max(f - 50, 0) frequency surplus; B <- B + kb (D - B) its lagged memory (G5: onset undershoot /
           release overshoot, sized by the surplus depth before the switch).
  freq     I = cI + 150 wIr Rd + wIS 100 (S - cS) - (L - 100) + G + Z
           f <- f + kf (50 + bI I - f), clipped [FMIN, FMAX]
           governor  G <- G + kg (clip(-gam (f-50), -Gm, Gm) - G)       (finite response, output limit)
           secondary Z <- (1 - dz) Z - kz (f - 50), clipped +-Zm            (slow leaky integral loop, G6)

MECHANISMS (gain 0 = off)
  m1  thermostat synchronisation: damped resonator driven by the price step du, with a price-dependent period and
      damping (G3): kap = kap1 exp(kk1 up), rho = rho1^(1 + kr1 up)
         s <- rho s - kap o + du ;  o <- o + s ;  L += g1 o
  m2  reserve energy: E in [0,1], starts 1.  E <- E - d2 Rd + c2 ch (1-E);  avail = clip(E/e2, 0, 1);
         charging draws load: L += g2L c2 ch (1-E) 100.  d2 is capped at D2MAX (G2).
  m3  interconnector heat: H <- H + a3 (S x - H);  share *= 1 - g3 max(H - h3, 0)
Stability: sigmoid rates, rho < 1, kap <= 0.5, clips on every state, bounded drivers.
"""
import math
import numpy as np

OBSERVABLES = ('load', 'frequency', 'renewable_share')
CONTROLS = ('price_signal', 'reserve_dispatch', 'charging_allowance', 'interconnector')
UNITS = {'load': 'linear', 'frequency': 'linear', 'renewable_share': 'linear'}
NOISE = {'load': 0.5, 'frequency': 0.03, 'renewable_share': 0.003}
CLAMP = {'load': [20.0, 300.0], 'frequency': [47.0, 53.0], 'renewable_share': [0.0, 1.0]}
FMIN, FMAX = 47.97, 52.03
UP_RESET = (1.5 - 0.8) / 1.5
D2MAX = 3.3e-4   # G2: at most ~5% reserve fade per 150 ticks of full dispatch without charging (R2c probe: no fade)

SPEC = {
    # load
    'cL': (94.2, 'free'), 'wLp': (8.8, 'free'), 'wLi': (22.8, 'free'), 'kL': (0.7, 'unit'),
    'Lref0': (108.0, 'free'), 'qi': (0.83, 'unit'),
    # share
    'cS': (0.363, 'free'), 'wSr': (4.3, 'pos'), 'wSx': (0.33, 'free'), 'wSx2': (0.2, 'free'), 'wSL': (0.06, 'free'),
    'wSG': (0.65, 'free'), 'kS': (0.99, 'unit'), 'wSB': (0.1, 'free'), 'kb': (0.15, 'unit'),
    # frequency / governor / secondary
    'cI': (6.2, 'free'), 'wIr': (0.64, 'free'), 'wIS': (1.7, 'free'), 'bI': (0.041, 'pos'),
    'kf': (0.42, 'unit'), 'kg': (0.16, 'unit'), 'gam': (45.6, 'pos'), 'Gm': (16.5, 'pos'),
    'kz': (0.02, 'unit'), 'dz': (0.02, 'unit'), 'Zm': (10.0, 'pos'),
    # m1
    'rho1': (0.963, 'unit'), 'kap1': (0.0068, 'unit'), 'g1': (3.77, 'free'), 'kk1': (0.5, 'free'), 'kr1': (0.0, 'free'),
    # m2
    'd2': (0.001, 'unit'), 'c2': (0.02, 'unit'), 'e2': (0.3, 'unit'), 'g2L': (0.0, 'free'),
    # m3
    'a3': (0.053, 'unit'), 'g3': (1.34, 'free'), 'h3': (0.339, 'free'),
}
MODULES = {
    'm1': (['rho1', 'kap1', 'g1', 'kk1', 'kr1'], {'g1': 0.0}),
    'm2': (['d2', 'c2', 'e2', 'g2L'], {'d2': 0.0, 'g2L': 0.0}),
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


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 3))
    cL, wLp, wLi, kL = p['cL'], p['wLp'], p['wLi'], p['kL']
    Lref0, qi = p['Lref0'], min(p['qi'], 0.99)
    cS, wSr, wSx, wSx2, wSL, wSG, kS = p['cS'], p['wSr'], p['wSx'], p['wSx2'], p['wSL'], p['wSG'], p['kS']
    wSB, kb = _clip(p['wSB'], -3.0, 3.0), p['kb']
    cI, wIr, wIS, bI, kf, kg, gam, Gm = p['cI'], p['wIr'], p['wIS'], p['bI'], p['kf'], p['kg'], p['gam'], p['Gm']
    kz, dz, Zm = p['kz'], max(p['dz'], 1e-3), min(p['Zm'], 100.0)
    rho1, kap1, g1 = p['rho1'], min(p['kap1'], 0.5), p['g1']
    kk1, kr1 = _clip(p['kk1'], -3.0, 3.0), _clip(p['kr1'], -3.0, 10.0)
    d2, c2, e2, g2L = min(p['d2'], D2MAX), p['c2'], max(p['e2'], 1e-3), p['g2L']
    a3, g3, h3 = p['a3'], p['g3'], p['h3']
    try:
        L0 = float(initial['load'])
        f0 = float(initial['frequency'])
    except (KeyError, TypeError, ValueError):
        L0, f0 = Lref0, 50.0
    if not (math.isfinite(L0) and math.isfinite(f0)):
        L0, f0 = Lref0, 50.0
    dev0 = _clip(L0 - Lref0, -60.0, 60.0)
    yL = cL + wLp * UP_RESET                        # equilibrium at the reset reference price 0.8
    up_prev = UP_RESET
    s = o = 0.0
    E = 1.0
    S = cS                                          # the share ignores its initial reading (B4)
    H = S
    f = _clip(f0, FMIN, FMAX)
    G = Z = 0.0
    B = 0.0
    decay = 1.0
    out = np.empty((T, 3))
    for t in range(T):
        pr, r, ch, x = actions[t]
        up = (1.5 - pr) / 1.5
        # --- load
        yL += kL * (cL + wLp * up - yL)
        du = up - up_prev
        up_prev = up
        if g1 != 0.0:
            kap = _clip(kap1 * math.exp(kk1 * up), 1e-6, 0.5)
            rho = _clip(rho1 ** (1.0 + kr1 * up), 0.0, 0.995) if rho1 > 0.0 else 0.0
            s = rho * s - kap * o + du
            o = _clip(o + s, -50.0, 50.0)
            s = _clip(s, -50.0, 50.0)
        # --- reserve (m2)
        avail = _clip(E / e2, 0.0, 1.0) if d2 > 0.0 else 1.0
        Rd = r * avail
        charge = c2 * ch * (1.0 - E)
        E = _clip(E - d2 * Rd + charge, 0.0, 1.0)
        decay *= qi
        L = yL + wLi * up + g1 * o + g2L * charge * 100.0 + dev0 * decay
        L = _clip(L, 20.0, 300.0)
        # --- share
        D = f - 50.0 if f > 50.0 else 0.0
        cx = 1.0 - x
        Sx = cS * _clip(1.0 - wSx * cx - wSx2 * cx * cx, 0.0, 3.0)
        fac = _clip(1.0 + wSL * (L - 100.0) / 100.0, 0.05, 5.0)
        fac *= math.exp(_clip(-wSG * G / 100.0 + wSB * (B - D), -3.0, 3.0))
        fac /= (1.0 + wSr * Rd)
        if g3 != 0.0:
            fac *= _clip(1.0 - g3 * max(H - h3, 0.0), 0.0, 1.0)
        St = Sx * fac
        S += kS * (St - S)
        S = _clip(S, 0.0, 1.0)
        B += kb * (D - B)
        if g3 != 0.0:
            H += a3 * (S * x - H)
        # --- frequency
        I = cI + 150.0 * wIr * Rd + wIS * 100.0 * (S - cS) - (L - 100.0) + G + Z
        f += kf * (50.0 + bI * I - f)
        f = _clip(f, FMIN, FMAX)
        G += kg * (_clip(-gam * (f - 50.0), -Gm, Gm) - G)
        Z = _clip((1.0 - dz) * Z - kz * (f - 50.0), -Zm, Zm)
        out[t, 0] = L
        out[t, 1] = f
        out[t, 2] = S
    return out
