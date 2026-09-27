"""reservoir gray-box model (Phase A researcher, v0; written from the theses in plans/reservoir-plan.md).

Controls (normalize, u = (value - recovery)/(pulse - recovery)):
  ur = (release - 2)/10  (physical release R = 2 + 10 ur, range 0..12)
  ui = irrigation/8      (physical I = 8 ui)
  ud = withdrawal_depth  (0 shallow, 1 deep)
  ua = 1 - aeration      (0 = aerated (recovery), 1 = no aeration)
Ticks t = 1, 2, ... (observation index + 1); the season is tied to time since reset.

BASE (always on)
  river    Rv(t) = c_in + A_s sin(2 pi t/P) + A_c cos(2 pi t/P) + B_s sin(4 pi t/P) + B_c cos(4 pi t/P)
  capacity C = qmax * (V/940)^beta * (1 - f)                 delivered D = smin(R + I, C)
           fouling f <- f + af (gf * ua - f)  (biomass on screens grows without aeration), f in [0, 0.9]
  water    V' = V + inflow - D - loss,  loss = e0 + e1 (V - 940)/100
           spill S = ks * max(V' - Vs, 0);  V <- V' - S;  outflow = D + S
  quality  q <- q + kq (Tq - q),  Tq = cq + wqa ua + wqd ud + wqx ua ud + wqr ur + wqi ui + lam_q z,
           z <- (1 - a_z) z (reset transient: internal layers start from the reference profile)
MECHANISMS (gain 0 = off): "Groundwater, irrigated land and deposited material may return water or
contaminants after a delay."
  m1 groundwater: bank head H <- H + a1 (V - H) (H0 = initial level);  return G = g1 * max(H - V - th1, 0)/100
         adds to inflow; seepage out when V > H: loss += g1s * max(V - H, 0)/100
  m2 irrigated land: two lag stages s1 <- s1 + a2 (Idel/8 - s1), s2 <- s2 + a2 (s1 - s2);
         return G2 = g2 * 8 * max(s2 - th2, 0) adds to inflow; quality target -= g2q * s2
  m3 deposited material: anoxic release pool Dm <- Dm + a3 (ua - Dm) (grows without aeration, fades with it);
         quality target -= g3 * Dm * (1 + h3 * ud)  (worse when drawing the deep layer)
Stability: all rates are sigmoids; states clipped; no feedback loops except level-limited outflow.
"""
import math
import numpy as np

OBSERVABLES = ('level', 'inflow', 'outflow', 'quality')
CONTROLS = ('release_rate', 'irrigation_allocation', 'withdrawal_depth', 'aeration')
RECOVERY = {'release_rate': 2.0, 'irrigation_allocation': 0.0, 'withdrawal_depth': 0.0, 'aeration': 1.0}
PULSE = {'release_rate': 12.0, 'irrigation_allocation': 8.0, 'withdrawal_depth': 1.0, 'aeration': 0.0}
UNITS = {'level': 'linear', 'inflow': 'linear', 'outflow': 'linear', 'quality': 'linear'}
NOISE = {'level': 4.4, 'inflow': 0.075, 'outflow': 0.05, 'quality': 0.0055}
CLAMP = {'level': [0.0, 1200.0], 'inflow': [0.0, 40.0], 'outflow': [0.0, 60.0], 'quality': [0.0, 1.0]}

SPEC = {
    # river season
    'c_in': (11.278, 'free'), 'A_s': (2.25, 'free'), 'A_c': (0.0, 'free'), 'P': (67.75, 'free'),
    'B_s': (0.0, 'free'), 'B_c': (0.0, 'free'),
    # water balance
    'Vs': (938.0, 'free'), 'ks': (0.5, 'unit'), 'e0': (1.2, 'free'), 'e1': (0.0, 'free'),
    'qmax': (17.0, 'pos'), 'beta': (0.3, 'free'), 'af': (0.02, 'unit'), 'gf': (0.1, 'unit'),
    # quality
    'cq': (0.95, 'free'), 'kq': (0.05, 'unit'), 'wqa': (-0.01, 'free'), 'wqd': (0.0, 'free'),
    'wqx': (-0.005, 'free'), 'wqr': (0.0, 'free'), 'wqi': (0.0, 'free'),
    'a_z': (0.2, 'unit'), 'lam_q': (-0.3, 'free'),
    # m1 groundwater
    'a1': (0.02, 'unit'), 'g1': (0.3, 'pos'), 'th1': (50.0, 'free'), 'g1s': (0.1, 'pos'),
    # m2 irrigated land
    'a2': (0.05, 'unit'), 'g2': (0.05, 'free'), 'th2': (0.3, 'unit'), 'g2q': (0.005, 'free'),
    # m3 deposited material
    'a3': (0.03, 'unit'), 'g3': (0.01, 'free'), 'h3': (0.5, 'free'),
}
MODULES = {
    'm1': (['a1', 'g1', 'th1', 'g1s'], {'g1': 0.0, 'g1s': 0.0}),
    'm2': (['a2', 'g2', 'th2', 'g2q'], {'g2': 0.0, 'g2q': 0.0}),
    'm3': (['a3', 'g3', 'h3'], {'g3': 0.0}),
    'harm2': (['B_s', 'B_c'], {'B_s': 0.0, 'B_c': 0.0}),
}
FIXED = ()


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def _logit(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1.0 - p))


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
        return _logit(value)
    if kind == 'pos':
        return math.log(max(value, 1e-300))
    return value


def normalize(action, bounds):
    out = []
    for c in CONTROLS:
        lo, hi = bounds.get(c, (min(RECOVERY[c], PULSE[c]), max(RECOVERY[c], PULSE[c])))
        v = min(max(float(action[c]), lo), hi)
        out.append((v - RECOVERY[c]) / (PULSE[c] - RECOVERY[c]))
    return tuple(out)


def _smin(a, b, w=0.3):
    """Smooth minimum (softplus blend), exact far from the corner."""
    d = (a - b) / w
    if d > 30:
        return b
    if d < -30:
        return a
    return a - w * math.log1p(math.exp(d))


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 4))
    V = min(max(float(initial['level']), 0.0), 1200.0)
    q = min(max(float(initial['quality']), 0.0), 1.0)
    H = V
    f = 0.0
    s1 = s2 = 0.0
    Dm = 0.0
    z = 1.0
    P = max(float(p['P']), 5.0)
    w1, w2 = 2 * math.pi / P, 4 * math.pi / P
    qmax, beta = p['qmax'], p['beta']
    Vs, ks, e0, e1 = p['Vs'], p['ks'], p['e0'], p['e1']
    af, gf = p['af'], p['gf']
    kq, cq = p['kq'], p['cq']
    a_z, lam_q = p['a_z'], p['lam_q']
    a1, g1, th1, g1s = p['a1'], p['g1'], p['th1'], p['g1s']
    a2, g2, th2, g2q = p['a2'], p['g2'], p['th2'], p['g2q']
    a3, g3, h3 = p['a3'], p['g3'], p['h3']
    wqa, wqd, wqx, wqr, wqi = p['wqa'], p['wqd'], p['wqx'], p['wqr'], p['wqi']
    rows = np.empty((T, 4))
    for i in range(T):
        ur, ui, ud, ua = actions[i]
        t = i + 1
        R = 2.0 + 10.0 * ur
        Iq = 8.0 * ui
        river = p['c_in'] + p['A_s'] * math.sin(w1 * t) + p['A_c'] * math.cos(w1 * t) \
            + p['B_s'] * math.sin(w2 * t) + p['B_c'] * math.cos(w2 * t)
        # m1 groundwater exchange
        G1 = g1 * max(H - V - th1, 0.0) / 100.0 if g1 else 0.0
        seep = g1s * max(V - H, 0.0) / 100.0 if g1s else 0.0
        # m2 irrigation return
        G2 = g2 * 8.0 * max(s2 - th2, 0.0) if g2 else 0.0
        inflow = max(river + G1 + G2, 0.0)
        # delivery limited by head and fouling
        C = qmax * (max(V, 1.0) / 940.0) ** beta * (1.0 - f)
        req = max(R + Iq, 0.0)
        D = max(_smin(req, C), 0.0)
        D = min(D, max(V, 0.0) + inflow)
        loss = max(e0 + e1 * (V - 940.0) / 100.0, 0.0) + seep
        Vn = V + inflow - D - loss
        S = ks * max(Vn - Vs, 0.0)
        Vn = min(max(Vn - S, 0.0), 1200.0)
        out = D + S
        # quality
        Tq = cq + wqa * ua + wqd * ud + wqx * ua * ud + wqr * ur + wqi * ui + lam_q * z
        if g2q:
            Tq -= g2q * s2
        if g3:
            Tq -= g3 * Dm * (1.0 + h3 * ud)
        q = min(max(q + kq * (Tq - q), 0.0), 1.0)
        # memories (after outputs)
        Idel = Iq * (D / req) if req > 1e-9 else 0.0
        H += a1 * (Vn - H)
        s1 += a2 * (Idel / 8.0 - s1)
        s2 += a2 * (s1 - s2)
        Dm += a3 * (ua - Dm)
        f += af * (gf * ua - f)
        f = min(max(f, 0.0), 0.9)
        z *= (1.0 - a_z)
        V = Vn
        rows[i, 0] = V
        rows[i, 1] = inflow
        rows[i, 2] = out
        rows[i, 3] = q
    return rows
