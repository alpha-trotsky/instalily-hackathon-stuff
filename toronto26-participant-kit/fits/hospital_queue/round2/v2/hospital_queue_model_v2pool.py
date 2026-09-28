"""hospital_queue gray-box model v2 (round 2). v1 is greybox/hospital_queue_model.py (left unchanged).

Changes from v1 (plans/hospital_queue-round2-diagnosis.md, section 5):
  1. Electives get their own long-stay service track instead of the elective work penalty (we*phi removed,
     together with phi, qe, ww and the phi-driven long-stay residual Lq).
       elective arrivals  Ae*e  enter a finite pool P (cap Pmax, soft minimum); the excess overflows into the shared
       waiting line W.  Pool patients are counted in `queue`, are discharged at rate P/Le (length of stay), but only
       from treatment capacity the routine flow leaves unused (lower priority, work ce per elective discharge), and
       leave the pool at a small rate the (slow residual drain).  With no spare capacity (flood, drain, or recovery
       with capacity ~ arrivals) the pool freezes: this gives the post-pulse ~100 plateau (B32) and R2c's residual.
     Crowding work Z tracks the total occupancy W + P (not W alone), so a filling pool erodes capacity (B22).
     The waiting-room cap applies to W + P (the ceiling does not grow with the pool).
  2. m2 handover: the deficit is proportional to the staffing increase and bounded explicitly:
       H <- (1 - a2) H + max(s - s_prev, 0);  s_eff = s * (1 - g2 * min(H / s, 1))       (g2 < 1: sigmoid)
  3. wait_time is the realized FIFO wait: the age of the oldest cohort still waiting in W (cohort ring buffer;
     leaving and overflow referral remove the newest cohorts; proportional leaving capped the head-of-line age
     and under-predicted wait ~2x in a first fit), scaled by W/(W+1) so an empty
     line reads 0, times exp(wu (up - 0.6)), then an output EMA with rate kw.

BASE (always on)
  arrivals   A = A0 + Ret  (routine; Ret = M3 returns)            electives Ae*e -> pool / overflow into W
  crowding   Z <- Z + az ((W + P)/(W + P + Kz) - Z);  wpp = 1 + wd Z
  capacity   mu = kmu s_eff (1 + wo ot)(1 - g1 F)(1 - wf fu) / wpp ;  mua = mu d ca/0.4 ; mut = mu (1-d) ct/0.6
  tandem     W -> chairs Xa (cap Ca, incl. blocked Bk) -> beds Xt (cap Cb) -> D   (as v1)
  leaving    W -= theta W ; W <= max(Wmax - P, 0)
  pool       De = smin(P/Le, spare/ce), spare = max(mut - D, 0) ; P -= De + the P
  outputs    queue = W + Xa + Bk + Xt + nsv D + P ; discharges = D + De ; wait = EMA of the FIFO wait
MECHANISMS: m1 fatigue (as v1), m2 handover (above), m3 returns (as v1, adds to routine arrivals).
Stability: rates are sigmoids, gains capped, all states clipped.
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
    # elective track
    'Pmax': (90.0, 'pos'), 'Le': (17.0, 'pos'), 'ce': (1.0, 'pos'), 'the': (0.003, 'unit'),
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
}
FIXED = ('A0', 'kmu', 'nsv', 'wf')

MODULES = {
    'm1': (['a1u', 'a1d', 'g1'], {'g1': 0.0}),
    'm2': (['a2', 'g2'], {'g2': 0.0}),
    'm3': (['g3', 'a3', 'Pc'], {'g3': 0.0}),
    'urg': (['wu'], {'wu': 0.0}),
}


WU_MAX = 1.5   # |urgent-priority wait exponent| bound (v1's free wu pinned at the +5 clip in a first v2 fit)


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


def simulate(p, initial, actions):
    T = len(actions)
    out = np.empty((T, 3))
    if T == 0:
        return out
    A0, Ae = min(p['A0'], 500.0), min(p['Ae'], 500.0)
    Pmax, Le, ce, the = min(p['Pmax'], 2000.0), min(max(p['Le'], 1.0), 1000.0), min(max(p['ce'], 0.05), 50.0), p['the']
    kmu, wo, wf, ca, ct = p['kmu'], max(min(p['wo'], 10.0), -0.9), p['wf'], min(p['ca'], 50.0), min(p['ct'], 50.0)
    Ca, Cb, Wmax, theta = min(p['Ca'], 5000.0), min(p['Cb'], 5000.0), min(p['Wmax'], 5000.0), p['theta']
    nsv = min(p['nsv'], 20.0)
    kw, gw, wu = p['kw'], min(p.get('gw', 1.0), 20.0), max(min(p['wu'], 5.0), -5.0)
    a1u, a1d, g1 = p['a1u'], p['a1d'], p['g1']
    a2, g2 = p['a2'], min(max(p['g2'], 0.0), 1.0)
    g3, a3, Pc = p['g3'], p['a3'], p['Pc']
    wd, az, Kz = min(p['wd'], 20.0), p['az'], max(p['Kz'], 1e-3)
    Z = P = 0.0
    W = min(max(_f(initial.get('queue') if isinstance(initial, dict) else None, 40.0), 0.0), 1000.0)
    v = min(max(_f(initial.get('wait_time') if isinstance(initial, dict) else None, 3.0), 0.0), 1000.0)
    # FIFO cohorts of W: [arrival tick, size / G]; G is a global survival scale for proportional leaving
    coh = deque()
    G = 1.0
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
        A = A0 + Ret
        # --- elective pool admission, overflow joins the shared line
        ea = Ae * e
        pin = max(_smin(ea, max(Pmax - P, 0.0)), 0.0) if ea > 0.0 else 0.0
        over = ea - pin
        P += pin
        occ = W + P
        Z += az * (occ / (occ + Kz) - Z)
        wpp = 1.0 + wd * Z
        mu = max(kmu * s_eff * (1.0 + wo * ot) * (1.0 - g1 * F) * (1.0 - wf * fu) / wpp, 0.0)
        mua = mu * d * ca / 0.4
        mut = mu * (1.0 - d) * ct / 0.6
        # --- routine flows
        inflow = A + over
        W += inflow
        if inflow > 0.0:
            coh.append([float(t), inflow / G])
        free = max(Ca - Xa - Bk, 0.0)
        adm = min(max(_smin(W, free), 0.0), W)
        W -= adm
        need = adm
        while need > 0.0 and coh:
            c = coh[0]
            avail = c[1] * G
            if avail <= need:
                need -= avail
                coh.popleft()
            else:
                c[1] -= need / G
                need = 0.0
        # leaving (theta) and overflow referral both remove the most recent arrivals, so the head of the line
        # keeps its age (steady state: FIFO wait = W / admissions, Little's law)
        need = theta * W
        W -= need
        cap = max(Wmax - P, 0.0)
        if W > cap:
            need += W - cap
            W = cap
        if need > 0.0:
            while need > 0.0 and coh:
                c = coh[-1]
                avail = c[1] * G
                if avail <= need:
                    need -= avail
                    coh.pop()
                else:
                    c[1] -= need / G
                    need = 0.0
        if G < 1e-50:
            for c in coh:
                c[1] *= G
            G = 1.0
        while coh and coh[0][1] * G < 1e-3:
            coh.popleft()
        if not coh:
            W = 0.0 if W < 1e-3 else W
        Xa += adm
        da = max(_smin(Xa, mua), 0.0)
        Xa -= da
        Bk += da
        tb = max(_smin(Bk, max(Cb - Xt, 0.0)), 0.0)
        Bk -= tb
        Xt += tb
        D = max(_smin(Xt, mut), 0.0)
        Xt -= D
        # --- elective pool service from spare treatment capacity
        spare = max(mut - D, 0.0)
        De = max(_smin(P / Le, spare / ce), 0.0) if P > 0.0 else 0.0
        De = min(De, P)
        P -= De
        P -= the * P
        P = min(max(P, 0.0), 2000.0)
        Dt = D + De
        # --- m3 returns pipeline
        if g3 > 0.0:
            r = g3 * max(Dt - fu * Pc, 0.0)
            L1 += a3 * (r - L1)
            L2 += a3 * (L1 - L2)
        # --- realized FIFO wait of the patients now at the head of the line
        age = (t - coh[0][0]) if coh else 0.0
        target = gw * age * W / (W + 1.0) * math.exp(wu * (up - 0.6))
        v += kw * (target - v)
        v = min(max(v, 0.0), 1000.0)
        out[t, 0] = v
        out[t, 1] = W + Xa + Bk + Xt + nsv * D + P
        out[t, 2] = Dt
    return out
