"""Traffic gray-box model: demand -> route split -> committed travel pipeline -> junction queues -> exits.

Written for plans/traffic-plan.md (Phase A). Interface: greybox/common/fit.py. Uses only math/numpy.

Controls, normalized u = (value - recovery)/(pulse - recovery), CONTROLS order:
  u_sig  = (0.5 - signal)/0.35   (>0: A gets less green)       u_lane = lane/0.65
  u_free = (5 - toll)/5          (1 = no toll: more, heavier demand)
  u_ramp = ramp                  (0 = nothing admitted: empty network at recovery, B1)
  u_fr   = (freight - 0.5)/0.5   u_crew = 1 - clearance (1 = crew at the intersection)

Base structure (always on):
  demand      D = d0 * ramp^gam * (1 + wt*u_free)
  split       pA = sigmoid(b0 + L)       (L = route-learning memory, 0 unless m1)
  diversion   waiting drivers divert: a share dv*Q_r/(Q_r+qd) of route r's arrivals goes to the other route
  pipeline    admitted vehicles are committed for DT ticks (shift register, B2), then join queue Q_r
  capacity    C_r = exp(c_r + wg_r*log(green_r/0.5) - wl_r*u_lane - wh_r*u_free + wc_r*u_crew + wf_r*u_fr)
                    * exp(-M2 - M3 terms);   served_r = min(Q_r, C_r);  flow_r = served_r
  buffer      Q_r <= qmax (excess arrivals rejected)
  speed       V_r = vf_r * exp(-al_r*n_r/100 - be_r*Q_r/100 - ws_r*u_sig(+/-) - vh_r*u_free - vc_r*u_crew
                    - g3v*F_r);   v_r <- v_r + kv*(V_r - v_r), starting from the noisy reading
Mechanisms (theses in the plan):
  m1 route learning   L <- L + a1*(g1*tanh((v_a - v_b)/10) - L)
  m2 crew fatigue/switching   S <- (1-a2s)*S + |d u_crew|;  Fg <- Fg + a2f*(work - Fg),
                      work = (1-u_crew)*(served_a+served_b)/24;  capacities * exp(-g2s*S - g2f*Fg)
  m3 spillback fronts F_r <- F_r + (a3u if Q_r/QF > F_r else a3d)*(Q_r/QF - F_r);
                      own capacity * exp(-g3c*F_r), other capacity * exp(-g3x*F_other), speed exp(-g3v*F_r)
"""
import math
import numpy as np

OBSERVABLES = ('flow_a', 'flow_b', 'speed_a', 'speed_b')
CONTROLS = ('signal_timing', 'lane_closure', 'toll', 'ramp_metering', 'freight_priority', 'clearance_effort')
RECOVERY = {'signal_timing': 0.5, 'lane_closure': 0.0, 'toll': 5.0, 'ramp_metering': 0.0,
            'freight_priority': 0.5, 'clearance_effort': 1.0}
PULSE = {'signal_timing': 0.15, 'lane_closure': 0.65, 'toll': 0.0, 'ramp_metering': 1.0,
         'freight_priority': 1.0, 'clearance_effort': 0.0}
UNITS = {'flow_a': 'linear', 'flow_b': 'linear', 'speed_a': 'linear', 'speed_b': 'linear'}
NOISE = {'flow_a': 1.0, 'flow_b': 1.0, 'speed_a': 0.3, 'speed_b': 0.3}
CLAMP = {'flow_a': [0.0, 200.0], 'flow_b': [0.0, 200.0], 'speed_a': [0.5, 80.0], 'speed_b': [0.5, 80.0]}
DT = 11          # committed travel ticks before the junction queue (flows appear 11 ticks after ramp on)
QF = 100.0       # queue scale of the spillback front
R = ('A', 'B')

SPEC = {
    # demand and split
    'd0': (24.0, 'pos'), 'gam': (1.0, 'pos'), 'wt': (0.38, 'free'), 'b0': (0.0, 'free'),
    'dv': (0.3, 'unit'), 'qd': (50.0, 'pos'), 'qmax': (600.0, 'pos'),
    # capacities
    'c_A': (math.log(22.0), 'free'), 'c_B': (math.log(12.6), 'free'),
    'wg_A': (0.5, 'free'), 'wg_B': (0.5, 'free'), 'wl_A': (0.05, 'free'), 'wl_B': (0.05, 'free'),
    'wh_A': (0.05, 'free'), 'wh_B': (0.05, 'free'), 'wc_A': (0.0, 'free'), 'wc_B': (0.0, 'free'),
    'wf_A': (0.0, 'free'), 'wf_B': (0.0, 'free'),
    # speeds
    'vf_A': (49.0, 'pos'), 'vf_B': (49.0, 'pos'), 'al_A': (0.38, 'free'), 'al_B': (0.38, 'free'),
    'be_A': (0.2, 'free'), 'be_B': (0.2, 'free'), 'ws_A': (0.18, 'free'), 'ws_B': (0.03, 'free'),
    'vh_A': (0.05, 'free'), 'vh_B': (0.05, 'free'), 'vc_A': (0.0, 'free'), 'vc_B': (0.0, 'free'),
    'kv': (0.12, 'unit'),
    # m1 route learning
    'a1': (0.03, 'unit'), 'g1': (0.3, 'free'),
    # m2 crew fatigue / switching
    'a2s': (0.1, 'unit'), 'g2s': (0.1, 'free'), 'a2f': (0.02, 'unit'), 'g2f': (0.1, 'free'),
    # m3 spillback fronts
    'a3u': (0.1, 'unit'), 'a3d': (0.005, 'unit'), 'g3c': (0.1, 'free'), 'g3x': (0.05, 'free'),
    'g3v': (0.05, 'free'),
}
MODULES = {
    'm1': (['a1', 'g1'], {'g1': 0.0}),
    'm2': (['a2s', 'g2s', 'a2f', 'g2f'], {'g2s': 0.0, 'g2f': 0.0}),
    'm3': (['a3u', 'a3d', 'g3c', 'g3x', 'g3v'], {'g3c': 0.0, 'g3x': 0.0, 'g3v': 0.0}),
}


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


def _ex(x):
    return math.exp(min(max(x, -50.0), 50.0))


def simulate(p, initial, actions):
    T = len(actions)
    out = np.zeros((T, 4))
    if T == 0:
        return out
    g = lambda n: float(p[n])
    d0, gam, wt, b0 = g('d0'), g('gam'), g('wt'), g('b0')
    dv, qd, qmax = g('dv'), g('qd'), g('qmax')
    c = [g('c_A'), g('c_B')]
    wg = [g('wg_A'), g('wg_B')]; wl = [g('wl_A'), g('wl_B')]; wh = [g('wh_A'), g('wh_B')]
    wc = [g('wc_A'), g('wc_B')]; wf = [g('wf_A'), g('wf_B')]
    vf = [g('vf_A'), g('vf_B')]; al = [g('al_A'), g('al_B')]; be = [g('be_A'), g('be_B')]
    ws = [g('ws_A'), -g('ws_B')]; vh = [g('vh_A'), g('vh_B')]; vc = [g('vc_A'), g('vc_B')]
    kv = g('kv')
    a1, g1 = g('a1'), g('g1')
    a2s, g2s, a2f, g2f = g('a2s'), g('g2s'), g('a2f'), g('g2f')
    a3u, a3d, g3c, g3x, g3v = g('a3u'), g('a3d'), g('g3c'), g('g3x'), g('g3v')

    def _init(name, default):
        try:
            v = float(initial[name])
            return v if math.isfinite(v) else default
        except (KeyError, TypeError, ValueError):
            return default
    v = [min(max(_init('speed_a', vf[0]), 0.5), 80.0), min(max(_init('speed_b', vf[1]), 0.5), 80.0)]
    pipe = [[0.0] * DT, [0.0] * DT]     # committed vehicles, index = ticks until the junction
    n = [0.0, 0.0]                      # vehicles in transit
    Q = [0.0, 0.0]
    L = S = Fg = 0.0
    F = [0.0, 0.0]
    prev_crew = 0.0
    head = 0
    for t in range(T):
        us, ul, uf, ur, ufr, uc = actions[t]
        ur = min(max(ur, 0.0), 1.0)
        D = d0 * (ur ** gam if ur > 0 else 0.0) * max(1.0 + wt * uf, 0.0)
        pA = _sigmoid(b0 + L)
        dA = dv * Q[0] / (Q[0] + qd)
        dB = dv * Q[1] / (Q[1] + qd)
        arr = [D * (pA * (1 - dA) + (1 - pA) * dB), D * ((1 - pA) * (1 - dB) + pA * dA)]
        # pipeline: vehicles admitted now reach the junction after DT ticks
        green = [0.5 - 0.35 * us, 0.5 + 0.35 * us]
        m2 = g2s * S + g2f * Fg
        served = [0.0, 0.0]
        for r in (0, 1):
            reach = pipe[r][head]
            pipe[r][head] = arr[r]
            n[r] += arr[r] - reach
            Q[r] = min(Q[r] + reach, qmax)
            cap = _ex(c[r] + wg[r] * math.log(max(green[r], 0.05) / 0.5) - wl[r] * ul - wh[r] * uf
                      + wc[r] * uc + wf[r] * ufr - m2 - g3c * F[r] - g3x * F[1 - r])
            served[r] = min(Q[r], cap)
            Q[r] -= served[r]
        head = (head + 1) % DT
        for r in (0, 1):
            V = vf[r] * _ex(-al[r] * n[r] / 100.0 - be[r] * Q[r] / 100.0 - ws[r] * us - vh[r] * uf
                            - vc[r] * uc - g3v * F[r])
            v[r] += kv * (V - v[r])
            v[r] = min(max(v[r], 0.5), 80.0)
        # memories (after outputs moved)
        L += a1 * (g1 * math.tanh((v[0] - v[1]) / 10.0) - L)
        S = (1 - a2s) * S + abs(uc - prev_crew)
        prev_crew = uc
        work = (1 - min(max(uc, 0.0), 1.0)) * (served[0] + served[1]) / 24.0
        Fg += a2f * (min(work, 5.0) - Fg)
        for r in (0, 1):
            qn = min(Q[r] / QF, 20.0)
            F[r] += (a3u if qn > F[r] else a3d) * (qn - F[r])
        out[t, 0], out[t, 1], out[t, 2], out[t, 3] = served[0], served[1], v[0], v[1]
    return out
