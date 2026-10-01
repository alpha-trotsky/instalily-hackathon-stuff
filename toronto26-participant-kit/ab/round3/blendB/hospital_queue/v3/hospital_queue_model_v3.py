"""hospital_queue gray-box model v3 (round 3). Copied from v2 (greybox/hospital_queue_model_v2.py, unchanged).

v3 change (plans/hospital_queue-plan.md, "Round 3 model (v3)"). Round-3 finding: after long overloads WITH electives
the queue drains at the v2 rate (~2/tick) down to a residual plateau (R4c ~100 -> 91.5 over 100 ticks, R1 ~99,
R2c 34.5 after an overtime drain), while R1's staffing-5 pulse without electives drains fully to 23. A pool that takes
part in the drain (round-2 archive v2pool, and a gated round-3 version, fits/hospital_queue/round3/
hospital_queue_model_v3pool.py) was switched off by every fit: the data drain the TOTAL at the v2 rate, so the
residual must be invisible while the line is long. v3 therefore adds a residual stock R that acts as a floor on
the waiting line in the queue output only:
    queue = W_floor + Xa + Bk + Xt + nsv D,   W_floor = W + softplus(R - W)   (~ max(W, R))
    R += fr * e * (W / Wmax)^2 * (Rmax - R)          fills while electives arrive into a nearly full line
    R -= (the + ko * ot * (s / 20)^2) * R            slow drain; overtime at high staffing clears it (R2c)
Wait and discharges are v2's (the floor patients neither wait in the FIFO nor change discharges). Bounded: R <= Rmax.

v2 description follows.

Changes from v1 (plans/hospital_queue-round2-diagnosis.md section 5; record in plans/hospital_queue-plan.md, "Round 2
model (v2)"):
  1. Elective work penalty removed. v1 made every patient heavier with the elective share (wpp = 1 + we*phi, we 2.0)
     and compensated with a 2.5x too fast leaving rate. v2 has no phi, we, qe, ww or phi-driven long-stay Lq:
     electives are extra arrivals Ae*e into the shared line with routine work. (A separate finite elective
     long-stay pool, diagnosis 5.1, was built and fitted: the optimizer collapsed it on all data (Pmax ~ 10) and it did
     not improve held-out scores, so it was dropped. Archived in fits/hospital_queue/round2/v2/.)
  2. m2 handover: deficit proportional to the staffing increase, bounded explicitly:
       H <- (1 - a2) H + max(s - s_prev, 0);  s_eff = s * (1 - g2 * min(H / s, 1))     (g2 in (0, 1): sigmoid)
     (v1's reassignment term k2d fitted to 0 everywhere and is dropped.)
  3. wait_time is the realized FIFO wait: the age of the oldest cohort still waiting in W (a cohort queue; leaving
     and overflow referral remove the newest cohorts, so at steady state the wait is W / admissions, Little's law,
     and in a drain it is the age of patients who joined when the line was longer), times W/(W+1) so an empty line
     reads 0, times gw * exp(wu (up - 0.6)) with |wu| <= 1.5, through an output EMA with rate kw.

BASE (always on)
  arrivals   A = A0 + Ae*e + Ret                 (Ret = M3 returns)
  crowding   Z <- Z + az (W/(W + Kz) - Z);  wpp = 1 + wd Z                (congestion work, as v1)
  capacity   mu = kmu s_eff (1 + wo ot)(1 - g1 F)(1 - wf fu) / wpp ;  mua = mu d ca/0.4 ; mut = mu (1-d) ct/0.6
  tandem     W -> chairs Xa (cap Ca, incl. blocked Bk) -> beds Xt (cap Cb) -> D   (as v1)
  leaving    W -= theta W ; W <= Wmax (overflow referral)
  outputs    queue = W + Xa + Bk + Xt + nsv D ; discharges = D ; wait = EMA of the FIFO wait
MECHANISMS: m1 fatigue (as v1), m2 handover (above), m3 returns (as v1, adds arrivals).
Stability: rates are sigmoids, gains capped, all states clipped; cohort queue bounded by W.
"""
import math
from collections import deque
import numpy as np

OBSERVABLES = ('wait_time', 'queue', 'discharges')
CONTROLS = ('staffing', 'elective_scheduling', 'diagnostic_allocation', 'urgent_priority', 'overtime',
            'followup_capacity')
UNITS = {'wait_time': 'linear', 'queue': 'linear', 'discharges': 'linear'}
NOISE = {'wait_time': 1.0, 'queue': 3.0, 'discharges': 1.0}
CLAMP = {'wait_time': [0.0, 1000.0], 'queue': [0.0, 1000.0], 'discharges': [0.0, 200.0]}

SPEC = {
    'A0': (11.5, 'pos'), 'Ae': (17.6, 'pos'),
    'kmu': (0.65, 'pos'), 'wo': (1.0, 'free'), 'wf': (0.0, 'unit'),
    'wd': (0.4, 'pos'), 'az': (0.5, 'unit'), 'Kz': (300.0, 'pos'),
    'ca': (1.0, 'pos'), 'ct': (1.0, 'pos'),
    'Ca': (20.0, 'pos'), 'Cb': (80.0, 'pos'), 'Wmax': (280.0, 'pos'), 'theta': (0.013, 'unit'),
    'nsv': (2.0, 'pos'), 'kw': (0.12, 'unit'), 'gw': (1.0, 'pos'), 'wu': (0.0, 'sym'),
    # m1 fatigue
    'a1u': (0.5, 'unit'), 'a1d': (0.035, 'unit'), 'g1': (0.2, 'unit'),
    # m2 handover
    'a2': (0.08, 'unit'), 'g2': (0.8, 'unit'),
    # m3 returns
    'g3': (0.1, 'unit'), 'a3': (0.05, 'unit'), 'Pc': (12.0, 'pos'),
    # v3 residual floor
    'Rmax': (75.0, 'pos'), 'fr': (0.05, 'unit'), 'the': (0.0008, 'unit'), 'ko': (0.1, 'unit'),
}
FIXED = ('A0', 'kmu', 'nsv', 'wf')

MODULES = {
    'm1': (['a1u', 'a1d', 'g1'], {'g1': 0.0}),
    'm2': (['a2', 'g2'], {'g2': 0.0}),
    'm3': (['g3', 'a3', 'Pc'], {'g3': 0.0}),
    'urg': (['wu'], {'wu': 0.0}),
}

WU_MAX = 1.5   # bound on the urgent-priority wait exponent (a free wu pinned at +5 in a first v2 fit)


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(raw, 50.0))
    if kind == 'sym':
        return WU_MAX * math.tanh(raw)
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        v = min(max(value, 1e-9), 1 - 1e-9)
        return math.log(v / (1 - v))
    if kind == 'pos':
        return math.log(max(value, 1e-300))
    if kind == 'sym':
        return math.atanh(min(max(value / WU_MAX, -0.999999), 0.999999))
    return value


DEFAULT_BOUNDS = {'staffing': (1.0, 20.0), 'elective_scheduling': (0.0, 20.0), 'diagnostic_allocation': (0.1, 0.8),
                  'urgent_priority': (0.0, 1.0), 'overtime': (0.0, 1.0), 'followup_capacity': (0.0, 1.0)}


def normalize(action, bounds):
    out = []
    for c in CONTROLS:
        lo, hi = bounds.get(c, DEFAULT_BOUNDS[c])
        v = min(max(float(action[c]), lo), hi)
        out.append(v / 20.0 if c == 'elective_scheduling' else v)
    return tuple(out)


SM = 0.5   # smoothing width (patients) of the soft minimum used for every capacity limit


def _smin(a, b):
    return 0.5 * (a + b - math.sqrt((a - b) * (a - b) + SM * SM))


def _f(x, default):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return default
    return x if math.isfinite(x) else default


def _take(coh, need, front):
    """Remove `need` patients from the oldest (front) or newest cohorts of the FIFO cohort queue."""
    while need > 0.0 and coh:
        c = coh[0] if front else coh[-1]
        if c[1] <= need:
            need -= c[1]
            if front:
                coh.popleft()
            else:
                coh.pop()
        else:
            c[1] -= need
            need = 0.0


def simulate(p, initial, actions):
    T = len(actions)
    out = np.empty((T, 3))
    if T == 0:
        return out
    A0, Ae = min(p['A0'], 500.0), min(p['Ae'], 500.0)
    kmu, wo, wf = p['kmu'], max(min(p['wo'], 10.0), -0.9), p['wf']
    ca, ct = min(p['ca'], 50.0), min(p['ct'], 50.0)
    Ca, Cb, Wmax, theta = min(p['Ca'], 5000.0), min(p['Cb'], 5000.0), min(p['Wmax'], 5000.0), p['theta']
    nsv = min(p['nsv'], 20.0)
    kw, gw, wu = p['kw'], min(p.get('gw', 1.0), 20.0), max(min(p['wu'], WU_MAX), -WU_MAX)
    a1u, a1d, g1 = p['a1u'], p['a1d'], p['g1']
    a2, g2 = p['a2'], min(max(p['g2'], 0.0), 1.0)
    g3, a3, Pc = p['g3'], p['a3'], p['Pc']
    wd, az, Kz = min(p['wd'], 20.0), p['az'], max(p['Kz'], 1e-3)
    Rmax, fr, the, ko = min(p['Rmax'], 1000.0), p['fr'], p['the'], p['ko']
    Z = R = 0.0
    W = min(max(_f(initial.get('queue') if isinstance(initial, dict) else None, 40.0), 0.0), 1000.0)
    v = min(max(_f(initial.get('wait_time') if isinstance(initial, dict) else None, 3.0), 0.0), 1000.0)
    coh = deque()                       # FIFO cohorts of W: [arrival tick, patients]
    if W > 0.0:
        coh.append([0.0, W])
    Xa = Bk = Xt = 0.0
    F = H = L1 = L2 = 0.0
    s_prev = None
    for t in range(T):
        s, e, d, up, ot, fu = actions[t]
        # --- mechanisms on capacity
        if g2 > 0.0:
            if s_prev is None:
                s_prev = s
            H = min((1.0 - a2) * H + max(s - s_prev, 0.0), 40.0)
            s_eff = s * (1.0 - g2 * min(H / max(s, 1e-6), 1.0))
        else:
            s_eff = s
        s_prev = s
        if g1 > 0.0:
            F += (a1u if ot > F else a1d) * (ot - F)
        Ret = L2 if g3 > 0.0 else 0.0
        A = A0 + Ae * e + Ret
        Z += az * (W / (W + Kz) - Z)
        wpp = 1.0 + wd * Z
        mu = max(kmu * s_eff * (1.0 + wo * ot) * (1.0 - g1 * F) * (1.0 - wf * fu) / wpp, 0.0)
        mua = mu * d * ca / 0.4
        mut = mu * (1.0 - d) * ct / 0.6
        # --- waiting line (FIFO cohorts)
        W += A
        if A > 0.0:
            coh.append([float(t), A])
        free = max(Ca - Xa - Bk, 0.0)
        adm = min(max(_smin(W, free), 0.0), W)
        W -= adm
        _take(coh, adm, True)
        # leaving and overflow referral remove the most recent arrivals (the head of the line keeps its age)
        gone = theta * W
        W -= gone
        if W > Wmax:
            gone += W - Wmax
            W = Wmax
        _take(coh, gone, False)
        while coh and coh[0][1] < 1e-3:
            coh.popleft()
        # --- service stages
        Xa += adm
        da = max(_smin(Xa, mua), 0.0)
        Xa -= da
        Bk += da
        tb = max(_smin(Bk, max(Cb - Xt, 0.0)), 0.0)
        Bk -= tb
        Xt += tb
        D = max(_smin(Xt, mut), 0.0)
        Xt -= D
        # --- m3 returns pipeline
        if g3 > 0.0:
            r = g3 * max(D - fu * Pc, 0.0)
            L1 += a3 * (r - L1)
            L2 += a3 * (L1 - L2)
        # --- v3 residual floor (queue output only)
        ov = min(W / max(Wmax, 1.0), 1.0)
        R += fr * e * ov * ov * (Rmax - R)
        R -= (the + ko * ot * (s / 20.0) ** 2) * R
        R = min(max(R, 0.0), Rmax)
        dx = R - W
        Wf = W + (dx if dx > 30.0 else math.log1p(math.exp(dx)) if dx > -30.0 else 0.0)
        # --- realized FIFO wait of the patients at the head of the line
        age = (t - coh[0][0]) if coh else 0.0
        target = gw * age * W / (W + 1.0) * math.exp(wu * (up - 0.6))
        v += kw * (target - v)
        v = min(max(v, 0.0), 1000.0)
        out[t, 0] = v
        out[t, 1] = Wf + Xa + Bk + Xt + nsv * D
        out[t, 2] = D
    return out
