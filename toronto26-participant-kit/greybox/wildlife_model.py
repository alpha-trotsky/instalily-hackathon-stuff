"""Wildlife gray-box model: two-region consumer-resource (food -> prey -> predator) model with a corridor
transit pipeline and three pluggable mechanisms (m1 patch occupancy, m2 juvenile/nursery, m3 settlement
competition). Written from the pre-registered theses in plans/wildlife-plan.md, after Run 1 showed:
  * prey overshoot after deep depletion (reset, full hunting) but not after mild depletion or a habitat pulse
    -> a hidden, finite, renewing food stock (brief: "Food renewal shares a finite resource");
  * habitat pulse lowers the prey level, more in the north -> habitat scales food renewal per region;
  * opening the corridor lowers ALL four totals (animals in transit are not counted), closing it gives
    a lagged refill and overshoot -> transit stocks (brief: "already travelling animals can still arrive");
  * predators decay slowly from the reset reading toward ~2.4 and barely follow prey.
Relaxation-to-target (the template) cannot produce the food-driven overshoot, hence this structure.

Per tick and region r in (N, S); u = normalized controls (uq hunting = quota/7, uh habitat = (1-prot)/0.9,
uc corridor), all states >= 0:
  food       F <- F + gF_r (1 - hF_r uh) (1 - F) - cF (X/100) I,   intake I = F / (F + kF) (Holling II)
  exposure   ex = (1 + eH_r uh) (1 - g1 P)            (m1: P = sheltering memory, fades to uq)
  harvest    H = 7 uq ex X / (X + Xh)
  predation  Pd = aP Y ex X / (X + Xp)
  births     B = bX X I (1 - g1f P)  -> m2 off: recruited at once;  m2 on: juvenile pool J,
             NJ-stage pipeline J1..J3 (each drains at a_m2), nursery-limited entry B / (1 + iRm B),
             recruits = a_m2 J3   (nursery competition + Erlang maturation delay)
  prey       X <- X + recruits - mX X - Pd - H - mvX_r uc X + arrivals_X
  predator   Y <- Y + eY Pd - dY Y - dY2 Y^2 - mvY uc Y + arrivals_Y
  transit    T_(r->r') <- T (1 - aT) + departures;  arrivals into r' = aT T * s,
             s = 1 / (1 + cS X_r'/100)  (m3 settlement competition; unsettled arrivals are lost; off: s = 1)
Reset convention: F = F0 (fixed reference), J = j0 X0 (deterministic in the initial reading), P = T = 0,
X and Y start at the noisy reading.
"""
import math
import numpy as np

OBSERVABLES = ('prey_north', 'predator_north', 'prey_south', 'predator_south')
CONTROLS = ('hunting_quota', 'habitat_protection', 'corridor_access')
RECOVERY = {'hunting_quota': 0.0, 'habitat_protection': 1.0, 'corridor_access': 0.0}
PULSE = {'hunting_quota': 7.0, 'habitat_protection': 0.1, 'corridor_access': 1.0}
UNITS = {o: 'log' for o in OBSERVABLES}
NOISE = {o: 0.01 for o in OBSERVABLES}   # residual scale (true noise ~0.45%; misfit dominates)
NJ = 3   # juvenile pipeline stages (m2)
CLAMP = {'prey_north': [0.01, 2000.0], 'predator_north': [0.001, 500.0],
         'prey_south': [0.01, 2000.0], 'predator_south': [0.001, 500.0]}

SPEC = {
    # food and prey
    'gF_N': (0.05, 'unit'), 'gF_S': (0.04, 'unit'), 'hF_N': (0.5, 'unit'), 'hF_S': (0.4, 'unit'),
    'cF': (0.08, 'pos'), 'F0': (0.9, 'unit'), 'kF': (0.2, 'pos'), 'bX': (0.3, 'pos'), 'mX': (0.1, 'unit'),
    # hunting / exposure
    'Xh': (40.0, 'pos'), 'eH_N': (0.1, 'pos'), 'eH_S': (0.1, 'pos'),
    # predators
    'aP': (0.05, 'pos'), 'Xp': (50.0, 'pos'), 'eY': (0.5, 'unit'), 'dY': (0.01, 'unit'), 'dY2': (0.003, 'pos'),
    # corridor transit
    'mvX_N': (0.05, 'unit'), 'mvX_S': (0.1, 'unit'), 'mvY': (0.1, 'unit'), 'aT': (0.1, 'unit'),
    # m1 patch occupancy (sheltering under hunting pressure)
    'a_m1': (0.05, 'unit'), 'g1': (0.2, 'unit'), 'g1f': (0.1, 'unit'),
    # m2 juvenile / nursery
    'a_m2': (0.3, 'unit'), 'iRm': (0.1, 'pos'), 'j0': (0.3, 'pos'),
    # m3 settlement competition
    'cS': (0.3, 'pos'),
}
MODULES = {
    'm1': (['a_m1', 'g1', 'g1f'], {'g1': 0.0, 'g1f': 0.0}),
    'm2': (['a_m2', 'iRm', 'j0'], {'a_m2': 1.0, 'iRm': 0.0, 'j0': 0.0}),
    'm3': (['cS'], {'cS': 0.0}),
}


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(max(raw, -50.0), 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        v = min(max(value, 1e-9), 1 - 1e-9)
        return math.log(v / (1 - v))
    if kind == 'pos':
        return math.log(max(value, 1e-22))
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
    gF = (p['gF_N'], p['gF_S'])
    hF = (p['hF_N'], p['hF_S'])
    eH = (p['eH_N'], p['eH_S'])
    mvX = (p['mvX_N'], p['mvX_S'])
    cF, bX, mX, Xh = p['cF'], p['bX'], p['mX'], p['Xh']
    aP, Xp, eY, dY, dY2 = p['aP'], p['Xp'], p['eY'], p['dY'], p['dY2']
    mvY, aT = p['mvY'], p['aT']
    a1, g1, g1f = p['a_m1'], p['g1'], p['g1f']
    a2, iRm, j0 = p['a_m2'], p['iRm'], p['j0']
    kF = p['kF']
    cS = p['cS']
    X = [_init(initial, 'prey_north', 85.0, 0.1, 2000.0), _init(initial, 'prey_south', 85.0, 0.1, 2000.0)]
    Y = [_init(initial, 'predator_north', 11.0, 0.01, 500.0), _init(initial, 'predator_south', 11.0, 0.01, 500.0)]
    F = [p['F0'], p['F0']]
    J = [[j0 * X[0]] * NJ, [j0 * X[1]] * NJ]
    P = [0.0, 0.0]
    TX = [0.0, 0.0]   # prey in transit leaving region r
    TY = [0.0, 0.0]
    out = np.empty((T, 4))
    for t in range(T):
        uq, uh, uc = actions[t]
        uq = min(max(uq, 0.0), 1.2)
        uh = min(max(uh, 0.0), 1.2)
        uc = min(max(uc, 0.0), 1.0)
        newX, newY = [0.0, 0.0], [0.0, 0.0]
        arrX = [aT * TX[1], aT * TX[0]]    # arrivals into r come from transit leaving the other region
        arrY = [aT * TY[1], aT * TY[0]]
        for r in (0, 1):
            x, y, f = X[r], Y[r], F[r]
            ex = (1.0 + eH[r] * uh) * (1.0 - g1 * P[r])
            harv = min(7.0 * uq * ex * x / (x + Xh), 0.9 * x)
            pred = min(aP * y * ex * x / (x + Xp), 0.5 * x)
            intake = f / (f + kF + 1e-9)
            births = bX * x * intake * (1.0 - g1f * P[r])
            if a2 < 1.0 or iRm > 0.0:
                # NJ-stage juvenile pipeline (Erlang delay, mean NJ / a2 ticks); nursery survival at entry
                jr = J[r]
                inflow = births / (1.0 + iRm * births)
                for k in range(NJ):
                    move = a2 * jr[k]
                    jr[k] = min(max(jr[k] + inflow - move, 0.0), 5000.0)
                    inflow = move
                recruits = inflow
            else:
                recruits = births
            s = 1.0 / (1.0 + cS * x / 100.0) if cS else 1.0
            depX = mvX[r] * uc * x
            depY = mvY * uc * y
            nx = x + recruits - mX * x - pred - harv - depX + s * arrX[r]
            ny = y + eY * pred - dY * y - dY2 * y * y - depY + s * arrY[r]
            newX[r] = min(max(nx, 0.01), 2000.0)
            newY[r] = min(max(ny, 0.001), 500.0)
            nf = f + gF[r] * max(1.0 - hF[r] * uh, 0.0) * (1.0 - f) - cF * (x / 100.0) * intake
            F[r] = min(max(nf, 0.0), 1.0)
            P[r] += a1 * (uq - P[r])
            TX[r] = TX[r] * (1.0 - aT) + depX
            TY[r] = TY[r] * (1.0 - aT) + depY
        X, Y = newX, newY
        out[t, 0], out[t, 1], out[t, 2], out[t, 3] = X[0], Y[0], X[1], Y[1]
    return out
