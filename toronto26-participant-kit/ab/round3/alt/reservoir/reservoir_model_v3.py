"""reservoir gray-box model v3 (round 3; copied from greybox/reservoir_model_v2.py, which is unchanged).

ROUND-3 CHANGES (plans/round3-findings.md, R6XD / R7XS: short anoxic pulse leaves no offset; XD < XS):
  lag  overshoot driver is a fading memory of delivered outflow, F <- F + aF (D/12 - F), used as
       lam_q z (1 + lz F) (aF = 1 is v2's instantaneous D/12). R7XS: quality stays high after release drops.
  dep  deep withdrawal adds deposit material: Cm build rate ap * drive * max(1 + hp ud, 0) (hp = 0 is v2).
  seq  pool fed through the anoxia state: drive = (1 - sq) uae + sq Dm (short pulses build little pool).
  lay  stored-layer memory of deep withdrawal L <- L + aL (ud - L); visible only when drawing shallow:
       quality target -= gL L (1 - ud) (R6XD and R1 450: deep -> shallow lowers later surface quality).
  All off-values reproduce v2 exactly.

(v2 notes follow)

ROUND-2 CHANGES (plans/reservoir-round2-diagnosis.md):
  Q1 reset transient: z decays fast (a_z in [0.02, 0.2], no clock-like slow drift) onto a free baseline cq (~0.950); overshoot amplitude
     lam_q * (1 + lz * D/12) grows with delivered outflow. No time-since-reset drift.
  Q2 post-anoxia offset rebuilt as a flushed deposit pool Cm (replaces v1's G3 remobilization):
       Cm <- Cm + ap * uae * (1 - Cm) - (kfl * ud * D/V + dC) * Cm     (builds under anoxia, removed by deep
       withdrawal flow, slow decay dC >= 0.002); it is released into the outlet when the column is mixed:
       quality target -= gC * Cm * (1 - uae)   (visible once aeration returns, at any depth).
     The anoxia state Dm (slow build a3, fast fade a3d, -g3 Dm (1 + h3 ud)) is kept; g3, gC >= 0. The linear
     direct aeration terms wqa, wqx are fixed at 0 (Dm's asymmetric rates already make the response convex).
  Q3 convex aeration: every "no aeration" term uses uae = ua**gam (gam in [1, 5]).
  W1 groundwater reset store: extra inflow gr * max(Hr - V0, 0) * rho**(t-1) (fast, reset only).


Controls (normalize, u = (value - recovery)/(pulse - recovery)):
  ur = (release - 2)/10  (physical release R = 2 + 10 ur, range 0..12)
  ui = irrigation/8      (physical I = 8 ui)
  ud = withdrawal_depth  (0 shallow, 1 deep)
  ua = 1 - aeration      (0 = aerated (recovery), 1 = no aeration)
Ticks t = 1, 2, ... (observation index + 1); the season is tied to time since reset.

BASE (always on)
  river    Rv(t) = c_in + A_s sin(2 pi t/P)   (G2: c_in, A_s, P fixed at the direct fit, cos/harmonics 0)
  capacity C = qmax * (V/940)^beta                           delivered D = smin(R + I, C)
           (screen fouling dropped: capacity identical with and without aeration, fitted af -> 0)
  water    V' = V + inflow - D - loss,  loss = e0 + e1 (V - 940)/100
           spill S = ks * max(V' - Vs, 0);  V <- V' - S;  outflow = D + S
  quality  q <- q + kq (Tq - q),  Tq = cq + wqa ua + wqd ud + wqx ua ud + wqr ur + wqi ui + lam_q z,
           z <- (1 - a_z) z (reset transient: internal layers start from the reference profile)
MECHANISMS (gain 0 = off): "Groundwater, irrigated land and deposited material may return water or
contaminants after a delay."
  m1 groundwater (G1 reshape, R3 evidence):
       fast bank head hf <- hf + af1 (V - hf) - b1 hf (leak to deep groundwater), hf0 = H0 (fixed reset convention, NOT the reading);
         signed exchange Qf = gf1 (hf - V)/100: Qf > 0 adds to inflow, Qf < 0 is extra loss
         (R3 from level 404: +2.3 excess at tick 1 decaying ~0.25/tick; R1 from 515: +0.7; R2 from 601: 0)
       slow aquifer head hs <- hs + a1 (V - hs), hs0 = initial level; return G = g1 max(hs - V - th1, 0)/100
         adds to inflow (persists while the level stays low; cut off quickly when V rises past hs - th1);
         seepage loss g1s max(V - hs, 0)/100
  m2 irrigated land: two lag stages s1 <- s1 + a2 (Idel/8 - s1), s2 <- s2 + a2 (s1 - s2);
         return G2 = g2 * 8 * max(s2 - th2, 0) adds to inflow; quality target -= g2q * s2
  m3 deposited material: anoxic release pool Dm <- Dm + a3 ua (1 - Dm) - a3d (1 - ua) Dm (grows without aeration
         at rate a3, fades with it at a3d);
         quality target -= g3 * Dm * (1 + h3 * ud)  (worse when drawing the deep layer)
       G3 remobilization: aeration on while deep moves the pool into the column:
         Cm <- Cm + kr * Dm * ud * (1 - ua) * (1 - Cm) - dC * Cm;  quality target -= gC * Cm
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
    # river season (G2: fixed at the direct fit, phase 0)
    'c_in': (11.2801, 'free'), 'A_s': (2.2527, 'free'), 'A_c': (0.0, 'free'), 'P': (67.7547, 'free'),
    'B_s': (0.0, 'free'), 'B_c': (0.0, 'free'),
    # water balance
    'Vs': (941.6, 'free'), 'ks': (0.99, 'unit'), 'e0': (1.14, 'free'), 'e1': (0.15, 'free'),
    'qmax': (16.49, 'pos'), 'beta': (0.334, 'free'), 'af': (0.0, 'unit'), 'gf': (0.0, 'unit'),
    # quality
    'cq': (0.9475, 'free'), 'kq': (0.13, 'unit'), 'wqa': (-0.0085, 'free'), 'wqd': (0.0, 'free'),
    'wqx': (-0.005, 'free'), 'wqr': (0.0, 'free'), 'wqi': (0.0, 'free'),
    'a_z': (0.04, 'az'), 'lam_q': (-0.3, 'free'),
    # m1 groundwater: slow aquifer head
    'a1': (0.01, 'unit'), 'g1': (0.3, 'pos'), 'th1': (50.0, 'free'), 'g1s': (0.1, 'pos'),
    # m1 groundwater: fast bank head with a fixed reset head
    'af1': (0.25, 'unit'), 'gf1': (1.5, 'pos'), 'H0': (560.0, 'free'), 'b1': (0.006, 'unit'),
    # m2 irrigated land
    'a2': (0.05, 'unit'), 'g2': (0.0, 'free'), 'th2': (0.3, 'unit'), 'g2q': (0.005, 'free'),
    # m3 deposited material
    'a3': (0.03, 'unit'), 'a3d': (0.05, 'unit'), 'g3': (0.01, 'pos'), 'h3': (0.5, 'free'),
    'kr': (0.0, 'unit'), 'dC': (0.003, 'dC'), 'gC': (0.015, 'pos'),
    # round 2
    'ap': (0.02, 'unit'), 'gam': (3.0, 'gam'), 'lz': (0.0, 'free'), 'kfl': (0.5, 'pos'),
    'gr': (0.0149, 'pos'), 'Hr': (561.0, 'free'), 'rho': (0.65, 'unit'),
    # round 3
    'aF': (0.3, 'unit'), 'hp': (0.0, 'free'), 'sq': (0.5, 'unit'), 'aL': (0.03, 'unit'), 'gL': (0.004, 'pos'),
}
MODULES = {
    'm1': (['a1', 'g1', 'th1', 'g1s', 'af1', 'gf1', 'H0', 'b1'], {'g1': 0.0, 'g1s': 0.0, 'gf1': 0.0}),
    'm2': (['a2', 'g2', 'th2', 'g2q'], {'g2': 0.0, 'g2q': 0.0}),
    'm3': (['a3', 'a3d', 'g3', 'h3', 'ap', 'dC', 'gC', 'kfl'], {'g3': 0.0, 'gC': 0.0}),
    'reset': (['gr', 'Hr', 'rho'], {'gr': 0.0}),
    'conv': (['gam'], {'gam': 1.0}),
    'lz': (['lz'], {'lz': 0.0}),
    'harm2': (['B_s', 'B_c'], {'B_s': 0.0, 'B_c': 0.0}),
    'lag': (['aF'], {'aF': 1.0}),
    'dep': (['hp'], {'hp': 0.0}),
    'seq': (['sq'], {'sq': 0.0}),
    'lay': (['aL', 'gL'], {'gL': 0.0}),
}
# G2 season fixed; fouling dropped (af = 0); spill instantaneous; M2 inflow return unsupported (G4: quality
# branch only).
FIXED = ('c_in', 'A_s', 'A_c', 'P', 'B_s', 'B_c', 'ks', 'af', 'gf', 'g2', 'th2', 'kr', 'wqa', 'wqx')


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
    if kind == 'gam':
        return 1.0 + 4.0 * _sigmoid(raw)
    if kind == 'az':
        return 0.02 + 0.18 * _sigmoid(raw)
    if kind == 'dC':
        return 0.002 + 0.2 * _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(raw, 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _logit(value)
    if kind == 'gam':
        return _logit((value - 1.0) / 4.0)
    if kind == 'az':
        return _logit((value - 0.02) / 0.18)
    if kind == 'dC':
        return _logit((value - 0.002) / 0.2)
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


def simulate(p, initial, actions, trace=None):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 4))
    V = min(max(float(initial['level']), 0.0), 1200.0)
    q = min(max(float(initial['quality']), 0.0), 1.0)
    hs = V
    H0 = min(max(float(p.get('H0', 560.0)), 0.0), 1200.0)
    hf = H0
    f = 0.0
    s1 = s2 = 0.0
    Dm = 0.0
    Cm = 0.0
    z = 1.0
    P = max(float(p['P']), 5.0)
    w1, w2 = 2 * math.pi / P, 4 * math.pi / P
    qmax, beta = p['qmax'], p['beta']
    Vs, ks, e0, e1 = p['Vs'], p['ks'], p['e0'], p['e1']
    af, gf = p['af'], p['gf']
    kq, cq = p['kq'], p['cq']
    a_z, lam_q = p['a_z'], p['lam_q']
    a1, g1, th1, g1s = p['a1'], p['g1'], p['th1'], p['g1s']
    af1, gf1, b1 = p.get('af1', 0.25), p.get('gf1', 0.0), p.get('b1', 0.0)
    a3d = p.get('a3d', p['a3'])
    a2, g2, th2, g2q = p['a2'], p['g2'], p['th2'], p['g2q']
    a3, g3, h3 = p['a3'], p['g3'], p['h3']
    ap, dC, gC = p.get('ap', 0.0), max(p.get('dC', 0.002), 0.002), p.get('gC', 0.0)
    wqa, wqd, wqx, wqr, wqi = p['wqa'], p['wqd'], p['wqx'], p['wqr'], p['wqi']
    gam = min(max(float(p.get('gam', 1.0)), 1.0), 5.0)
    lz, kfl = p.get('lz', 0.0), p.get('kfl', 0.0)
    aF = min(max(float(p.get('aF', 1.0)), 0.0), 1.0)
    hp = float(p.get('hp', 0.0))
    sq = min(max(float(p.get('sq', 0.0)), 0.0), 1.0)
    aL, gL = min(max(float(p.get('aL', 0.03)), 0.0), 1.0), p.get('gL', 0.0)
    F = 0.0
    L = 0.0
    rho = min(max(float(p.get('rho', 0.0)), 0.0), 0.99)
    Qr = p.get('gr', 0.0) * max(p.get('Hr', 561.0) - V, 0.0)
    Qr = min(Qr, 20.0)
    rows = np.empty((T, 4))
    for i in range(T):
        ur, ui, ud, ua = actions[i]
        t = i + 1
        R = 2.0 + 10.0 * ur
        Iq = 8.0 * ui
        river = p['c_in'] + p['A_s'] * math.sin(w1 * t) + p['A_c'] * math.cos(w1 * t) \
            + p['B_s'] * math.sin(w2 * t) + p['B_c'] * math.cos(w2 * t)
        # m1 groundwater exchange: slow aquifer head (thresholded return, seepage) + fast bank head (signed)
        G1 = g1 * max(hs - V - th1, 0.0) / 100.0 if g1 else 0.0
        seep = g1s * max(V - hs, 0.0) / 100.0 if g1s else 0.0
        Qf = gf1 * (hf - V) / 100.0 if gf1 else 0.0
        Qf = min(max(Qf, -20.0), 20.0)
        # m2 irrigation return
        G2 = g2 * 8.0 * max(s2 - th2, 0.0) if g2 else 0.0
        inflow = max(river + G1 + G2 + max(Qf, 0.0) + Qr, 0.0)
        Qr *= rho
        uae = max(ua, 0.0) ** gam
        # delivery limited by head (and fouling, off by default)
        C = qmax * (max(V, 1.0) / 940.0) ** beta * (1.0 - f)
        req = max(R + Iq, 0.0)
        D = max(_smin(req, C), 0.0)
        D = min(D, max(V, 0.0) + inflow)
        loss = max(e0 + e1 * (V - 940.0) / 100.0, 0.0) + seep + max(-Qf, 0.0)
        Vn = V + inflow - D - loss
        S = ks * max(Vn - Vs, 0.0)
        Vn = min(max(Vn - S, 0.0), 1200.0)
        out = D + S
        # quality
        F += aF * (D / 12.0 - F)
        Tq = cq + wqa * uae + wqd * ud + wqx * uae * ud + wqr * ur + wqi * ui + lam_q * z * (1.0 + lz * F)
        if gL:
            Tq -= gL * L * (1.0 - ud)
        if g2q:
            Tq -= g2q * s2
        if g3:
            Tq -= g3 * Dm * (1.0 + h3 * ud)
        if gC:
            Tq -= gC * Cm * (1.0 - uae)
        q = min(max(q + kq * (Tq - q), 0.0), 1.0)
        # memories (after outputs)
        Idel = Iq * (D / req) if req > 1e-9 else 0.0
        hs += a1 * (Vn - hs)
        hf += af1 * (Vn - hf) - b1 * hf
        s1 += a2 * (Idel / 8.0 - s1)
        s2 += a2 * (s1 - s2)
        drive = (1.0 - sq) * uae + sq * Dm
        Cm += ap * drive * max(1.0 + hp * ud, 0.0) * (1.0 - Cm) - (min(kfl * ud * D / max(V, 50.0), 0.5) + dC) * Cm
        L += aL * (ud - L)
        L = min(max(L, 0.0), 1.0)
        Cm = min(max(Cm, 0.0), 1.0)
        Dm += a3 * uae * (1.0 - Dm) - a3d * (1.0 - uae) * Dm
        Dm = min(max(Dm, 0.0), 1.0)
        f += af * (gf * ua - f)
        f = min(max(f, 0.0), 0.9)
        z *= (1.0 - min(max(a_z, 0.02), 0.2))
        V = Vn
        rows[i, 0] = V
        rows[i, 1] = inflow
        rows[i, 2] = out
        rows[i, 3] = q
        if trace is not None:
            trace.append((Tq, z, Dm, Cm, D, V, uae))
    return rows
