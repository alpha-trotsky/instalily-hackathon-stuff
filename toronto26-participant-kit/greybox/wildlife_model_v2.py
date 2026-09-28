"""Wildlife gray-box model v2 (round 2, after plans/wildlife-round2-diagnosis.md). v1 is greybox/wildlife_model.py.

Round-2 changes (each has an "off" value that recovers v1 behaviour, used for ablations):
  P1 predator target on a SHARED prey signal (mean prey of both regions, Hill n = 1 + nP, half-saturation Xp)
     with a bounded maximum prey depression dP (review B17/B30), and a PERSISTENT corridor depression cY*uc
     inside the target (B22); the two depressions compose as a q-norm (q = 1 + qC; large q = max-type, B23).
     off: dP = 0 and cY = 0 -> constant target (then v1's local-prey Y* is not reproduced; v1 is kept separately).
  P2 the reserve Z relaxes faster when the target is depressed: kZ_eff = kZ (1 + kZp dep) (numerical response,
     B17: the reset tail falls faster under control). Linear in Z at a given prey path (keeps review R2). off kZp = 0.
  P3 concave habitat map: every habitat use sees s(uh) = uh (1 + ch)/(uh + ch) (B21). off: ch at its cap (~linear).
  P5 habitat raises adult prey mortality directly: mX (1 + hM s(uh)) (B21: a fast, direct carrying-level effect;
     renewal-only habitat was too weak and too slow). off hM = 0.
  P4 J0 cap raised to 60 (it was pinned at 30); fitted with the from-reset-under-control runs (B16).

v1 docstring follows.

The previous version is greybox/wildlife_model_v0.py (the fits in fits/wildlife/*_r1.json and *_all_quick.json
refer to that version).

Mechanism triple rebuilt per review G1 (the brief's competition sentence): "Food renewal shares a finite
resource, young animals compete for nursery food, and arrivals compete for settlement space."
  mA food renewal  : a finite, renewing food stock F per region (Holling-II intake, kF >= 0.05).
                     off: logistic births with a habitat-dependent carrying capacity (no hidden stock).
  mB nursery       : births pass a NJ-stage juvenile pipeline with nursery-capped entry B / (1 + iRm B),
                     fixed reset J0 per stage (review G5), maturation rate a_m2 in [0.15, 1].
                     off: births recruited at once.
  mC settlement    : arrivals settle at rate 1 / (1 + cS X_dest / 100) (prey) and 1 / (1 + cSY Y_dest)
                     (predators); the rest WAIT in transit (a queue, review G6). off: all arrivals settle.
Base (always on): two regions, patch exposure as an instant hunting/habitat effect (patch occupancy is base
structure, review G1), per-region harvest with a refuge Xr (review G3: harvest and predation act only on
X - Xr), transit pipeline (animals in transit are not counted), and a LINEAR two-state predator block
(review G2): Y relaxes at kY toward a hidden reserve Z, Z relaxes at kZ toward Y* = yb Xe/(Xe + Xp)
(1 + eHY uh); reset Z0 = Yref + zf (Y0 - Yref), so the transient is affine in (Y0 - Yref).

u = normalized controls: uq hunting = quota/7, uh habitat = (1 - protection)/0.9, uc corridor.
"""
import math
import numpy as np

OBSERVABLES = ('prey_north', 'predator_north', 'prey_south', 'predator_south')
CONTROLS = ('hunting_quota', 'habitat_protection', 'corridor_access')
RECOVERY = {'hunting_quota': 0.0, 'habitat_protection': 1.0, 'corridor_access': 0.0}
PULSE = {'hunting_quota': 7.0, 'habitat_protection': 0.1, 'corridor_access': 1.0}
UNITS = {o: 'log' for o in OBSERVABLES}
NOISE = {o: 0.01 for o in OBSERVABLES}   # residual scale (true noise ~0.45%; misfit dominates)
NJ = 6   # juvenile pipeline stages (mB)
CLAMP = {'prey_north': [0.01, 2000.0], 'predator_north': [0.001, 500.0],
         'prey_south': [0.01, 2000.0], 'predator_south': [0.001, 500.0]}

SPEC = {
    # mA food stock
    'gF_N': (0.02, 'unit'), 'gF_S': (0.012, 'unit'), 'hF_N': (0.6, 'unit'), 'hF_S': (0.48, 'unit'),
    'cF': (0.034, 'c2'), 'F0': (0.99, 'unit'), 'kF': (0.03, 'pos'),          # kF used as 0.05 + kF
    # logistic alternative (only fitted when mA is off)
    'K_N': (130.0, 'c2000'), 'K_S': (105.0, 'c2000'), 'hK_N': (0.45, 'unit'), 'hK_S': (0.35, 'unit'),
    # prey base
    'bX': (0.6, 'c5'), 'mX': (0.11, 'unit'), 'Xh': (36.0, 'c300'), 'Xr': (2.0, 'c30'),
    'eH_N': (0.02, 'c20'), 'eH_S': (0.05, 'c20'), 'g1': (0.19, 'unit'), 'g1f': (0.5, 'unit'),
    'aP': (0.02, 'c3'), 'Xq': (2.0, 'c300'),
    # predators (linear two-state)
    'kY': (0.05, 'unit'), 'kZ': (0.02, 'unit'), 'yb': (2.4, 'c20'), 'Xp': (15.0, 'c300'), 'eHY': (0.05, 'c5'),
    'Yref': (2.3, 'c20'), 'zf': (0.5, 'c3'),
    # round 2: predator target (P1), rate (P2), habitat concavity (P3)
    'nP': (1.0, 'c4'), 'dP': (0.3, 'unit'), 'cY': (0.2, 'unit'), 'qC': (3.0, 'c20'), 'kZp': (1.0, 'c100'),
    'ch': (1.0, 'c20'), 'hM': (0.0, 'c3'),
    # corridor transit
    'mvX_N': (0.017, 'unit'), 'mvX_S': (0.047, 'unit'), 'mvY': (0.03, 'unit'), 'aT': (0.045, 'unit'),
    # mB nursery
    'a_m2': (0.6, 'unit'), 'iRm': (0.04, 'c2'), 'J0': (3.0, 'c60'),         # a_m2 used as 0.15 + 0.85 a
    # mC settlement
    'cS': (0.3, 'c20'), 'cSY': (0.2, 'c20'),
}
FOOD = ['gF_N', 'gF_S', 'hF_N', 'hF_S', 'cF', 'F0', 'kF']
LOGI = ['K_N', 'K_S', 'hK_N', 'hK_S']
MODULES = {
    'mA': (FOOD, {'F0': -1.0}),                      # F0 < 0 flags "food off" (logistic births)
    'mB': (['a_m2', 'iRm', 'J0'], {'a_m2': -1.0, 'iRm': 0.0}),   # a_m2 < 0 flags "no pipeline"
    'mC': (['cS', 'cSY'], {'cS': 0.0, 'cSY': 0.0}),
    'hmort': (['hM'], {'hM': 0.0}),   # P5, round-2 variant v2b (not in the shipped v2: failed held-out)
}


def free_names(modules):
    disabled = {n for m, (names, _) in MODULES.items() if m not in modules for n in names}
    if 'mA' in modules:
        disabled |= set(LOGI)
    return [n for n in SPEC if n not in disabled]


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(max(raw, -30.0), 12.0))
    if kind[0] == 'c':   # capped gain in (0, cap)
        return float(kind[1:]) * _sigmoid(raw)
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        v = min(max(value, 1e-9), 1 - 1e-9)
        return math.log(v / (1 - v))
    if kind == 'pos':
        return math.log(max(value, 1e-13))
    if kind[0] == 'c':
        v = min(max(value / float(kind[1:]), 1e-9), 1 - 1e-9)
        return math.log(v / (1 - v))
    return value


def normalize(action, bounds):
    out = []
    for c in CONTROLS:
        lo, hi = bounds.get(c, (min(RECOVERY[c], PULSE[c]), max(RECOVERY[c], PULSE[c])))
        v = min(max(float(action[c]), lo), hi)
        out.append((v - RECOVERY[c]) / (PULSE[c] - RECOVERY[c]))
    return tuple(out)


def _init(initial, name, default, lo, hi):
    try:
        v = float(initial[name])
    except (KeyError, TypeError, ValueError):
        v = default
    if not math.isfinite(v):
        v = default
    return min(max(v, lo), hi)


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 4))
    food_on = p['F0'] >= 0.0
    pipe_on = p['a_m2'] >= 0.0
    gF = (p['gF_N'], p['gF_S'])
    hF = (p['hF_N'], p['hF_S'])
    K = (p['K_N'], p['K_S'])
    hK = (p['hK_N'], p['hK_S'])
    eH = (p['eH_N'], p['eH_S'])
    mvX = (p['mvX_N'], p['mvX_S'])
    cF, kF = p['cF'], 0.05 + p['kF']
    bX, mX, Xh, Xr, g1, g1f = p['bX'], p['mX'], p['Xh'], p['Xr'], p['g1'], p['g1f']
    aP, Xq = p['aP'], p['Xq']
    kY, kZ, yb, Xp, eHY = p['kY'], p['kZ'], p['yb'], p['Xp'], p['eHY']
    mvY, aT = p['mvY'], p['aT']
    a2 = 0.15 + 0.85 * p['a_m2'] if pipe_on else 1.0
    iRm, J0 = p['iRm'], p['J0']
    cS, cSY = p['cS'], p['cSY']
    nH = 1.0 + p['nP']
    XpN = p['Xp'] ** nH
    dP, cY, qq, kZp, ch = p['dP'], p['cY'], 1.0 + p['qC'], p['kZp'], p['ch']
    hM = p.get('hM', 0.0)
    X = [_init(initial, 'prey_north', 85.0, 0.1, 2000.0), _init(initial, 'prey_south', 85.0, 0.1, 2000.0)]
    Y = [_init(initial, 'predator_north', 11.0, 0.01, 500.0), _init(initial, 'predator_south', 11.0, 0.01, 500.0)]
    Yref, zf = p['Yref'], p['zf']
    Z = [max(Yref + zf * (Y[0] - Yref), 0.001), max(Yref + zf * (Y[1] - Yref), 0.001)]
    F = [p['F0'], p['F0']] if food_on else [1.0, 1.0]
    J = [[J0] * NJ, [J0] * NJ]
    TX = [0.0, 0.0]   # prey in transit leaving region r (heading to the other region)
    TY = [0.0, 0.0]
    out = np.empty((T, 4))
    for t in range(T):
        uq, uh, uc = actions[t]
        uq = min(max(uq, 0.0), 1.2)
        uh = min(max(uh, 0.0), 1.2)
        uc = min(max(uc, 0.0), 1.0)
        uh = uh * (1.0 + ch) / (uh + ch)          # P3 concave habitat map, s(0) = 0, s(1) = 1
        # P1/P2 predator target on the shared prey signal, corridor depression, q-norm composition
        pm = max(0.5 * (X[0] + X[1]), 0.0) ** nH
        dpp = dP * XpN / (pm + XpN)
        dcc = cY * uc
        dep = min((dpp ** qq + dcc ** qq) ** (1.0 / qq), 0.95) if (dpp > 0.0 or dcc > 0.0) else 0.0
        ystar = yb * (1.0 - dep) * (1.0 + eHY * uh)
        kz = min(kZ * (1.0 + kZp * dep), 0.5)
        newX, newY = [0.0, 0.0], [0.0, 0.0]
        setX, setY = [0.0, 0.0], [0.0, 0.0]
        for r in (0, 1):
            src = 1 - r   # arrivals into r come from transit leaving the other region
            sx = 1.0 / (1.0 + cS * X[r] / 100.0) if cS > 0 else 1.0
            sy = 1.0 / (1.0 + cSY * Y[r]) if cSY > 0 else 1.0
            setX[r] = aT * sx * TX[src]
            setY[r] = aT * sy * TY[src]
        for r in (0, 1):
            x, y = X[r], Y[r]
            xe = max(x - Xr, 0.0)
            ex = (1.0 + eH[r] * uh) * (1.0 - g1 * min(uq, 1.0))
            # exponential (monotone) removal: no period-2 sawtooth when the harvest slope is steep
            xe1 = xe * math.exp(-7.0 * uq * ex / (xe + Xh + 1e-9))
            harv = xe - xe1
            pred = xe1 * (1.0 - math.exp(-aP * y * ex / (xe1 + Xq + 1e-9)))
            if food_on:
                f = F[r]
                intake = f / (f + kF)
                phi = intake
            else:
                kr = max(K[r] * (1.0 - hK[r] * min(uh, 1.1)), 1.0)
                phi = max(1.0 - x / kr, 0.0)
            births = bX * x * phi * max(1.0 - g1f * uq, 0.0)
            if pipe_on:
                jr = J[r]
                inflow = births / (1.0 + iRm * births)
                for k in range(NJ):
                    move = a2 * jr[k]
                    jr[k] = min(max(jr[k] + inflow - move, 0.0), 5000.0)
                    inflow = move
                recruits = inflow
            else:
                recruits = births
            depX = mvX[r] * uc * x
            depY = mvY * uc * y
            nx = x + recruits - mX * (1.0 + hM * uh) * x - pred - harv - depX + setX[r]
            ny = y + kY * (Z[r] - y) - depY + setY[r]
            Z[r] = min(max(Z[r] + kz * (ystar - Z[r]), 0.001), 500.0)
            newX[r] = min(max(nx, 0.01), 2000.0)
            newY[r] = min(max(ny, 0.001), 500.0)
            if food_on:
                nf = F[r] + gF[r] * max(1.0 - hF[r] * uh, 0.0) * (1.0 - F[r]) - cF * (x / 100.0) * intake
                F[r] = min(max(nf, 0.0), 1.0)
        for r in (0, 1):
            src = 1 - r
            TX[r] = min(TX[r] - setX[src] + mvX[r] * uc * X[r], 5000.0)
            TY[r] = min(TY[r] - setY[src] + mvY * uc * Y[r], 500.0)
            TX[r] = max(TX[r], 0.0)
            TY[r] = max(TY[r], 0.0)
        X, Y = newX, newY
        out[t, 0], out[t, 1], out[t, 2], out[t, 3] = X[0], Y[0], X[1], Y[1]
    return out
