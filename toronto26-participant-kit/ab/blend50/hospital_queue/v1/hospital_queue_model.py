"""hospital_queue gray-box model v1 (Phase C: + deterioration Z, long-stay residual Lq, wf fixed 0; v0 in hospital_queue_model_v0.py)
(v0 by the Phase A researcher): tandem fluid queue + wait estimate + 3 mechanism modules.

Controls (normalize, physical units kept): s = staffing [1, 20], e = elective_scheduling / 20, d = diagnostic_allocation,
up = urgent_priority, ot = overtime, fu = followup_capacity.

BASE (from the brief's structure; always on)
  arrivals   A = A0 + Ae*e + Ret                                   (Ret = M3 returns, 0 when M3 is off)
  mix        phi <- phi + aphi (Ae*e/A - phi)                      elective share of the patients in the system
  deterior.  Z <- Z + az (W/(W+Kz) - Z)       backlog-age proxy (0 at reset: fresh initial patients are light)
  work/pt    wpp = 1 + we*phi + wd*Z
  long-stay  Lq <- Lq + aqu*max(gq*phi - Lq, 0) - aqd*Lq ; counted in queue only (residual occupancy after load, G4)
  capacity   mu = kmu * s_eff * (1 + wo*ot) * (1 - g1*F) * (1 - wf*fu) / wpp      patients' work per tick
  split      mua = mu * d * ca / 0.4 ; mut = mu * (1 - d) * ct / 0.6          (diagnostic allocation divides staff)
  stages     W waiting, Xa in assessment (chairs, cap Ca, includes Bk = assessed patients holding a chair),
             Xt in treatment (beds, cap Cb).  Per tick:
               adm  = min(W + A, Ca - Xa - Bk)       admitted to a free chair
               W    = W + A - adm ; W -= theta*W (patients leave) ; W = min(W, Wmax) (overflow referred elsewhere)
               da   = min(Xa, mua) ; Xa -= da ; Bk += da            assessment completions wait for a bed in their chair
               tb   = min(Bk, Cb - Xt) ; Bk -= tb ; Xt += tb
               D    = min(Xt, mut) ; Xt -= D                          discharges (gross)
  outputs    queue = W + Xa + Bk + Xt + nsv*D + Lq + qe*phi   (qe: elective patients in beds, decouples the ceiling from throughput, G2) (patients being served this tick) ; discharges = D
             wait: v <- v + kw (W / max(Dm, 0.5) * exp(wu*(up-0.6)) * (1 + ww*phi) - v)   (ww: elective-mix wait factor, G2/G7),  Dm <- Dm + kd (D - Dm)
  reset      W0 = initial queue reading (all waiting), services empty, v0 = initial wait reading, Dm0 = A0.

MECHANISMS (gain 0 = off; drivers written from the theses before fitting)
  m1 fatigue      F <- F + (a1u if ot > F else a1d) (ot - F);   capacity *= (1 - g1 F)
  m2 handover     H <- (1 - a2) H + max(s - s_prev, 0) + k2d * s * |d - d_prev| / 0.35;
                  s_eff = max(s - g2 H, 0.1 s)    new / reassigned staff are not yet fully effective
  m3 returns      at-risk flow r = g3 * max(D - fu*Pc, 0);  two lag stages L1, L2 (rate a3);  Ret = L2 adds arrivals,
                  and heavier case mix: phi also tracks wr*Ret/A
Stability: every state clipped to [0, caps]; rates are sigmoids; capacities positive.
"""
import math
import numpy as np

OBSERVABLES = ('wait_time', 'queue', 'discharges')
CONTROLS = ('staffing', 'elective_scheduling', 'diagnostic_allocation', 'urgent_priority', 'overtime',
            'followup_capacity')
UNITS = {'wait_time': 'linear', 'queue': 'linear', 'discharges': 'linear'}
NOISE = {'wait_time': 1.0, 'queue': 3.0, 'discharges': 1.0}
CLAMP = {'wait_time': [0.0, 1000.0], 'queue': [0.0, 1000.0], 'discharges': [0.0, 200.0]}

SPEC = {
    'A0': (11.5, 'pos'), 'Ae': (20.0, 'pos'), 'aphi': (0.05, 'unit'), 'we': (0.3, 'free'),
    'kmu': (0.65, 'pos'), 'wo': (1.0, 'free'), 'wf': (0.0, 'unit'),
    'wd': (0.4, 'pos'), 'az': (0.03, 'unit'), 'Kz': (60.0, 'pos'),
    'qe': (1e-3, 'pos'), 'ww': (0.0, 'free'), 'gq': (20.0, 'pos'), 'aqu': (0.02, 'unit'), 'aqd': (0.001, 'unit'),
    'ca': (1.0, 'pos'), 'ct': (1.0, 'pos'),
    'Ca': (30.0, 'pos'), 'Cb': (30.0, 'pos'), 'Wmax': (270.0, 'pos'), 'theta': (0.02, 'unit'),
    'nsv': (2.0, 'pos'), 'kw': (0.1, 'unit'), 'kd': (0.1, 'unit'), 'wu': (0.0, 'free'),
    # m1 fatigue
    'a1u': (0.02, 'unit'), 'a1d': (0.01, 'unit'), 'g1': (0.2, 'unit'),
    # m2 handover
    'a2': (0.08, 'unit'), 'g2': (0.8, 'unit'), 'k2d': (0.3, 'pos'),
    # m3 returns
    'g3': (0.1, 'unit'), 'a3': (0.05, 'unit'), 'Pc': (12.0, 'pos'), 'wr': (0.5, 'free'),
}
FIXED = ('A0', 'kmu', 'nsv', 'wf')   # G1: follow-up has no capacity cost (R9); visible P0 constants

MODULES = {
    'm1': (['a1u', 'a1d', 'g1'], {'g1': 0.0}),
    'm2': (['a2', 'g2', 'k2d'], {'g2': 0.0}),
    'm3': (['g3', 'a3', 'Pc', 'wr'], {'g3': 0.0}),
    'urg': (['wu'], {'wu': 0.0}),
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
    """Smooth min(a, b) (differentiable, <= min + SM/2); keeps least_squares gradients alive at capacity kinks."""
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
    A0, Ae, aphi, we = p['A0'], p['Ae'], p['aphi'], p['we']
    kmu, wo, wf, ca, ct = p['kmu'], p['wo'], p['wf'], p['ca'], p['ct']
    Ca, Cb, Wmax, theta = min(p['Ca'], 5000.0), min(p['Cb'], 5000.0), min(p['Wmax'], 5000.0), p['theta']
    nsv = min(p['nsv'], 20.0)
    kw, kd, wu = p['kw'], p['kd'], max(min(p['wu'], 5.0), -5.0)
    a1u, a1d, g1 = p['a1u'], p['a1d'], p['g1']
    a2, g2, k2d = p['a2'], p['g2'], min(p['k2d'], 20.0)
    g3, a3, Pc, wr = p['g3'], p['a3'], p['Pc'], p['wr']
    wd, az, Kz = min(p.get('wd', 0.0), 20.0), p.get('az', 0.03), max(p.get('Kz', 60.0), 1e-3)
    gq, aqu, aqd = min(p.get('gq', 0.0), 500.0), p.get('aqu', 0.02), p.get('aqd', 0.001)
    qe = min(p.get('qe', 0.0), 500.0)
    ww = min(max(p.get('ww', 0.0), -0.9), 20.0)
    Z = Lq = 0.0
    W = min(max(_f(initial.get('queue') if isinstance(initial, dict) else None, 40.0), 0.0), 1000.0)
    v = min(max(_f(initial.get('wait_time') if isinstance(initial, dict) else None, 3.0), 0.0), 1000.0)
    Xa = Bk = Xt = 0.0
    Dm = A0
    phi = 0.0
    F = H = L1 = L2 = 0.0
    s_prev, d_prev = None, None
    for t in range(T):
        s, e, d, up, ot, fu = actions[t]
        # --- mechanisms that act on capacity
        if g2 > 0.0:
            if s_prev is None:
                s_prev, d_prev = s, d
            H = (1.0 - a2) * H + max(s - s_prev, 0.0) + k2d * s * abs(d - d_prev) / 0.35
            H = min(H, 40.0)
            s_eff = max(s - g2 * H, 0.1 * s)
        else:
            s_eff = s
        s_prev, d_prev = s, d
        if g1 > 0.0:
            F += (a1u if ot > F else a1d) * (ot - F)
        Ret = L2 if g3 > 0.0 else 0.0
        A = A0 + Ae * e + Ret
        drv = (Ae * e + wr * Ret) / max(A, 1e-6)
        phi += aphi * (min(max(drv, -1.0), 2.0) - phi)
        Z += az * (W / (W + Kz) - Z)
        wpp = max(1.0 + we * phi + wd * Z, 0.1)
        mu = kmu * s_eff * (1.0 + wo * ot) * (1.0 - g1 * F) * (1.0 - wf * fu) / wpp
        mu = max(mu, 0.0)
        mua = mu * d * ca / 0.4
        mut = mu * (1.0 - d) * ct / 0.6
        # --- flows
        free = max(Ca - Xa - Bk, 0.0)
        adm = max(_smin(W + A, free), 0.0)
        W = W + A - adm
        W -= theta * W
        if W > Wmax:
            W = Wmax
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
        # --- long-stay residual occupancy
        Lq += aqu * max(gq * phi - Lq, 0.0) - aqd * Lq
        Lq = min(max(Lq, 0.0), 500.0)
        # --- wait estimate
        Dm += kd * (D - Dm)
        v += kw * (W / max(Dm, 0.5) * math.exp(wu * (up - 0.6)) * (1.0 + ww * phi) - v)
        v = min(max(v, 0.0), 1000.0)
        out[t, 0] = v
        out[t, 1] = W + Xa + Bk + Xt + nsv * D + Lq + qe * phi
        out[t, 2] = D
    return out
