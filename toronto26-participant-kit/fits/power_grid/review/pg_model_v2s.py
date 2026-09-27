"""REVIEWER VARIANT v2s (multiplicative share, no hard cap, bounded conventional-backoff state Gs driving share). Based on power_grid gray-box model (Phase A researcher, v0; written from the theses in plans/power_grid-plan.md).

Controls (normalize): p = price_signal (physical, 0..2), r = reserve_dispatch / 150, ch = charging_allowance,
x = interconnector (physical, 0..1).  up = (1.5 - p) / 1.5 is the demand-raising price coordinate
(0 at recovery 1.5, 1 at pulse 0, 0.467 at the reset reference price 0.8).

BASE (always on)
  load     L = yL + wLi*up + [M1 resonator] + [M2 charging draw]
           yL <- yL + kL (cL + wLp*up - yL)          slow price-dependent demand level
           Reset convention: the price before tick 0 is 0.8 and yL starts at its 0.8 equilibrium; the
           initial reading shifts the baseline by b_init*(L_init - 105) ('init' module, needs >= 2 resets).
  reserve  Rd = r * avail  (avail = 1 without M2)      delivered reserve, fraction of 150
  share    S <- S + kS (S* - S),  S* = cS + wSr*Rd + wSx*(1-x) + wSL*(L - 100)/100 - wSG*G/100 + [M3],
           clipped above at Smax (the observed curtailment plateau)
  freq     imbalance I = cI + 150*wIr*Rd + wIS*100*(S - cS) - (L - 100) + G
           f <- f + kf (50 + bI*I - f),  clipped to [FMIN, FMAX]
           governor G <- G + kg (clip(-gam*(f - 50), -Gm, Gm) - G)   (finite response, output limits)

MECHANISMS (gain 0 = off)
  m1  thermostat synchronisation: damped resonator driven by the price step du = up_t - up_{t-1}
         s <- rho1*s - kap1*o + du ;  o <- o + s ;  L += g1*o          (rebound / ringing)
  m2  reserve energy: E in [0,1], starts 1.  E <- E - d2*Rd + c2*ch*(1-E);  avail = clip(E/e2, 0, 1)
         (delivered reserve fades when energy is low); charging draws load: L += g2L*c2*ch*(1-E)*100
  m3  interconnector heat: H <- H + a3*(flow - H), flow = S*x (renewable import through the line);
         S* -= g3*max(H - h3, 0) (curtailment when the line is hot)
Stability: all rates are sigmoids, resonator kappa < 1 with rho < 1, clips on every state.
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

SPEC = {
    # load
    'cL': (94.4, 'free'), 'wLp': (8.0, 'free'), 'wLi': (22.0, 'free'), 'kL': (0.8, 'unit'),
    # share
    'cS': (0.37, 'free'), 'wSr': (4.0, 'pos'), 'wSx': (0.55, 'free'), 'wSx2': (0.0, 'free'), 'wSL': (-0.2, 'free'),
    'wSG': (0.3, 'free'), 'kS': (0.9, 'unit'), 'kgs': (0.08, 'unit'), 'gms': (2.0, 'pos'),
    # frequency / governor
    'cI': (7.0, 'free'), 'wIr': (0.75, 'free'), 'wIS': (1.4, 'free'), 'bI': (0.03, 'pos'),
    'kf': (0.43, 'unit'), 'kg': (0.05, 'unit'), 'gam': (30.0, 'pos'), 'Gm': (30.0, 'pos'),
    # init
    'b_init': (0.0, 'free'),
    # m1
    'rho1': (0.962, 'unit'), 'kap1': (0.0066, 'unit'), 'g1': (3.9, 'free'),
    # m2
    'd2': (0.01, 'unit'), 'c2': (0.02, 'unit'), 'e2': (0.3, 'unit'), 'g2L': (0.0, 'free'),
    # m3
    'a3': (0.05, 'unit'), 'g3': (0.5, 'free'), 'h3': (0.3, 'free'),
}
MODULES = {
    'init': (['b_init'], {'b_init': 0.0}),
    'm1': (['rho1', 'kap1', 'g1'], {'g1': 0.0}),
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
    cS, wSr, wSx, wSx2, wSL, wSG, kS = p['cS'], p['wSr'], p['wSx'], p['wSx2'], p['wSL'], p['wSG'], p['kS']
    kgs, gms = p['kgs'], p['gms']
    Gs = 0.0
    cI, wIr, wIS, bI, kf, kg, gam, Gm = p['cI'], p['wIr'], p['wIS'], p['bI'], p['kf'], p['kg'], p['gam'], p['Gm']
    rho1, kap1, g1 = p['rho1'], min(p['kap1'], 0.9), p['g1']
    d2, c2, e2, g2L = p['d2'], p['c2'], max(p['e2'], 1e-3), p['g2L']
    a3, g3, h3 = p['a3'], p['g3'], p['h3']
    try:
        L0 = float(initial['load'])
        f0 = float(initial['frequency'])
        S0 = float(initial['renewable_share'])
    except (KeyError, TypeError, ValueError):
        L0, f0, S0 = 105.0, 50.0, 0.3
    if not (math.isfinite(L0) and math.isfinite(f0) and math.isfinite(S0)):
        L0, f0, S0 = 105.0, 50.0, 0.3
    base = cL + p['b_init'] * (L0 - 105.0)
    yL = base + wLp * UP_RESET                      # equilibrium at the reset reference price 0.8
    up_prev = UP_RESET
    s = o = 0.0
    E, H = 1.0, _clip(S0, 0.0, 1.0)
    S = _clip(S0, 0.0, 1.0)
    f = _clip(f0, FMIN, FMAX)
    G = 0.0
    L = L0
    out = np.empty((T, 3))
    for t in range(T):
        pr, r, ch, x = actions[t]
        up = (1.5 - pr) / 1.5
        # --- load
        yL += kL * (base + wLp * up - yL)
        du = up - up_prev
        up_prev = up
        s = rho1 * s - kap1 * o + du
        o = _clip(o + s, -50.0, 50.0)
        s = _clip(s, -50.0, 50.0)
        # --- reserve (m2)
        avail = _clip(E / e2, 0.0, 1.0) if d2 > 0.0 else 1.0
        Rd = r * avail
        charge = c2 * ch * (1.0 - E)
        E = _clip(E - d2 * Rd + charge, 0.0, 1.0)
        L = yL + wLi * up + g1 * o + g2L * charge * 100.0
        L = _clip(L, 20.0, 300.0)
        # --- share
        cx = 1.0 - x
        Sx = cS * _clip(1.0 - wSx * cx - wSx2 * cx * cx, 0.0, 3.0)          # interconnector opening
        fac = _clip(1.0 + wSL * (L - 100.0) / 100.0, 0.05, 5.0)            # load dilution
        fac *= math.exp(_clip(wSG * Gs, -3.0, 3.0))                          # conventional backed off -> share up
        fac /= (1.0 + wSr * Rd)                                              # reserve displaces renewables
        if g3 != 0.0:
            fac *= _clip(1.0 - g3 * max(H - h3, 0.0), 0.0, 1.0)             # hot line curtails
        St = Sx * fac
        S += kS * (St - S)
        S = _clip(S, 0.0, 1.0)
        if g3 != 0.0:
            H += a3 * (S * x - H)
        # --- frequency
        I = cI + 150.0 * wIr * Rd + wIS * 100.0 * (S - cS) - (L - 100.0) + G
        f += kf * (50.0 + bI * I - f)
        f = _clip(f, FMIN, FMAX)
        G += kg * (_clip(-gam * (f - 50.0), -Gm, Gm) - G)
        Gs += kgs * (_clip(gms * (f - 50.0), -1.0, 1.0) - Gs)                 # bounded backoff memory (share only)
        out[t, 0] = L
        out[t, 1] = f
        out[t, 2] = S
    return out
