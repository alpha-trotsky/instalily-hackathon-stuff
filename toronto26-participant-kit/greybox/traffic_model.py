"""Traffic grey-box model v1 (Phase C). The reviewer's revised base (fits/traffic/review/traffic_model_rv.py,
plans/traffic-review.md G2) plus the Phase C changes. The pre-review model is kept as greybox/traffic_model_v0.py.

Base (from rv):
  * two vehicle classes: heavy share h = sigmoid(h0 + h1*u_free); queues and capacities in PCU (heavy = pce PCU),
    so a toll-0 mix congests at an unchanged vehicle total; freight priority weights heavy service.
  * junction capacity exp(c_r) * (green_r/0.5)^wg_r * (1 - wl_r*lane) * exp(wc_r*u_crew) * exit-occupancy factor.
  * exit stage with shared occupancy E_A+E_B; admissions scale with (1 - E/Emax).
  * speed = vf / time-factor, time factor = 1 + al*(n/100)^pa + sg*(0.5/green - 1) + queue, exit, heavy-mix and
    completed-journey (J) delays.
Phase C changes:
  * G3/G5: per-route approach buffers qmax_A, qmax_B.
  * G4: instantaneous spillback in the base: capacity * exp(-sp_r * fullness_r), fullness = Q_r/qmax_r.
  * G3/G4: m3 rewritten as a persistent front: F_r builds (a3u) while the queue on r exceeds q3 PCU and recedes
    (a3d) only once the queue is below q3. F_r cuts its own capacity (g3c), the other route's (g3x) and its speed
    (g3v). With a3d small this makes a self-sustaining standing queue (bistable) possible.
  * Stability: all speed delay gains are 'pos' (physical sign), the time factor is floored at 0.95, so a speed
    never exceeds 1.05*vf (the gaining-green bonus, B16) and never goes below vf/60.
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
DT = 11

SPEC = {
    'd0': (24.0, 'pos'), 'wt': (1.47, 'free'), 'h0': (-2.46, 'free'), 'h1': (1.86, 'free'), 'pce': (3.0, 'pos'),
    'kf': (2.2, 'free'), 'b0': (0.0, 'free'), 'dv': (0.08, 'unit'), 'qd': (1.0, 'pos'),
    'qmax_A': (600.0, 'pos'), 'qmax_B': (300.0, 'pos'), 'sp_A': (0.2, 'pos'), 'sp_B': (0.2, 'pos'),
    'c_A': (3.26, 'free'), 'c_B': (2.83, 'free'), 'wg_A': (0.58, 'free'), 'wg_B': (0.58, 'free'),
    'wl_A': (0.01, 'unit'), 'wl_B': (0.04, 'unit'), 'wc_A': (0.24, 'free'), 'wc_B': (0.18, 'free'),
    'e_A': (3.6, 'free'), 'e_B': (3.15, 'free'), 'ke': (0.63, 'free'), 'Emax': (16.6, 'pos'),
    'vf_A': (49.9, 'pos'), 'vf_B': (50.2, 'pos'), 'al_A': (0.56, 'pos'), 'al_B': (0.48, 'pos'), 'pa': (0.54, 'pos'),
    'sg_A': (0.11, 'pos'), 'sg_B': (0.045, 'pos'), 'be_A': (0.55, 'pos'), 'be_B': (0.09, 'pos'),
    'bx': (0.07, 'pos'), 'vh_A': (0.09, 'pos'), 'vh_B': (1.3, 'pos'), 'bj_A': (0.2, 'pos'), 'bj_B': (0.1, 'pos'),
    'kJ': (0.5, 'unit'), 'kv': (0.09, 'unit'),
    # m1 route learning
    'a1': (0.03, 'unit'), 'g1': (0.3, 'free'),
    # m2 crew switching / fatigue
    'a2s': (0.1, 'unit'), 'g2s': (0.1, 'pos'), 'a2f': (0.02, 'unit'), 'g2f': (0.1, 'pos'),
    # m3 persistent spillback fronts (build while a queue exists, recede only after it clears)
    'a3u': (0.05, 'unit'), 'a3d': (0.02, 'unit'), 'q3': (20.0, 'pos'),
    'g3c': (0.2, 'pos'), 'g3x': (0.05, 'pos'), 'g3v': (0.3, 'pos'),
}
MODULES = {
    'm1': (['a1', 'g1'], {'g1': 0.0}),
    'm2': (['a2s', 'g2s', 'a2f', 'g2f'], {'g2s': 0.0, 'g2f': 0.0}),
    'm3': (['a3u', 'a3d', 'q3', 'g3c', 'g3x', 'g3v'], {'g3c': 0.0, 'g3x': 0.0, 'g3v': 0.0}),
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
        return math.log(max(value, 1e-12))
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
    d0, wt, h0, h1, pce, kf = min(g('d0'), 500.0), g('wt'), g('h0'), g('h1'), min(max(g('pce'), 1.0), 20.0), g('kf')
    b0, dv, qd = g('b0'), g('dv'), g('qd')
    qmax = [min(max(g('qmax_A'), 1.0), 1e5), min(max(g('qmax_B'), 1.0), 1e5)]
    sp = [min(g('sp_A'), 20.0), min(g('sp_B'), 20.0)]
    c = [g('c_A'), g('c_B')]; wg = [g('wg_A'), g('wg_B')]; wl = [g('wl_A'), g('wl_B')]; wc = [g('wc_A'), g('wc_B')]
    e = [g('e_A'), g('e_B')]; ke, Emax = g('ke'), min(max(g('Emax'), 1.0), 1e5)
    vf = [min(g('vf_A'), 75.0), min(g('vf_B'), 75.0)]; al = [g('al_A'), g('al_B')]; pa = min(g('pa'), 3.0)
    sg = [g('sg_A'), g('sg_B')]; be = [g('be_A'), g('be_B')]; bx = g('bx')
    vh = [g('vh_A'), g('vh_B')]; bj = [g('bj_A'), g('bj_B')]; kJ, kv = g('kJ'), g('kv')
    a1, g1 = g('a1'), min(max(g('g1'), -5.0), 5.0)
    a2s, g2s, a2f, g2f = g('a2s'), min(g('g2s'), 5.0), g('a2f'), min(g('g2f'), 5.0)
    a3u, a3d, q3 = g('a3u'), g('a3d'), g('q3')
    g3c, g3x, g3v = min(g('g3c'), 5.0), min(g('g3x'), 5.0), min(g('g3v'), 20.0)

    def _init(name, default):
        try:
            v = float(initial[name])
            return v if math.isfinite(v) else default
        except (KeyError, TypeError, ValueError):
            return default
    v = [min(max(_init('speed_a', vf[0]), 0.5), 80.0), min(max(_init('speed_b', vf[1]), 0.5), 80.0)]
    pl = [[0.0] * DT, [0.0] * DT]; ph = [[0.0] * DT, [0.0] * DT]
    nl = [0.0, 0.0]; nh = [0.0, 0.0]
    Ql = [0.0, 0.0]; Qh = [0.0, 0.0]; E = [0.0, 0.0]; J = [0.0, 0.0]
    L = S = Fg = 0.0
    F = [0.0, 0.0]
    prev_crew = 0.0
    head = 0
    for t in range(T):
        us, ul, uf, ur, ufr, uc = actions[t]
        ur = min(max(ur, 0.0), 1.0)
        lane = 0.65 * ul
        D = d0 * ur * max(1.0 + wt * uf, 0.0)
        h = _sigmoid(h0 + h1 * uf)
        pA = _sigmoid(b0 + L)
        Qp = [Ql[0] + pce * Qh[0], Ql[1] + pce * Qh[1]]
        dA = dv * Qp[0] / (Qp[0] + qd + 1e-9)
        dB = dv * Qp[1] / (Qp[1] + qd + 1e-9)
        arr = [D * (pA * (1 - dA) + (1 - pA) * dB), D * ((1 - pA) * (1 - dB) + pA * dA)]
        green = [min(max(0.5 - 0.35 * us, 0.05), 0.95), 0.0]
        green[1] = 1.0 - green[0]
        wH = _ex(kf * ufr)
        mech = g2s * S + g2f * Fg
        occ = max(0.0, 1.0 - (E[0] + E[1]) / Emax)
        served = [0.0, 0.0]; exits = [0.0, 0.0]
        for r in (0, 1):
            rl, rh = pl[r][head], ph[r][head]
            pl[r][head] = arr[r] * (1 - h); ph[r][head] = arr[r] * h
            nl[r] += pl[r][head] - rl; nh[r] += ph[r][head] - rh
            # finite approach buffer (PCU): reject the excess
            space = max(qmax[r] - Qp[r], 0.0)
            need = rl + pce * rh
            acc = 1.0 if need <= space or need <= 0 else space / need
            Ql[r] += rl * acc; Qh[r] += rh * acc
            full = min((Ql[r] + pce * Qh[r]) / qmax[r], 1.0)
            cap = _ex(c[r] + wg[r] * math.log(green[r] / 0.5) + wc[r] * uc - mech - sp[r] * full
                      - g3c * F[r] - g3x * F[1 - r])
            cap *= max(1.0 - wl[r] * lane, 0.02) * occ
            hp = pce * Qh[r]
            den = wH * hp + Ql[r]
            sh_share = wH * hp / den if den > 1e-12 else 0.0
            hs = min(hp, sh_share * cap)
            ls = min(Ql[r], cap - hs)
            hs = min(hp, cap - ls)
            sv_h = hs / pce
            Ql[r] = max(Ql[r] - ls, 0.0); Qh[r] = max(Qh[r] - sv_h, 0.0)
            served[r] = ls + sv_h
            E[r] += served[r]
            ecap = _ex(e[r] - ke * uc - mech)
            exits[r] = min(E[r], ecap)
            E[r] -= exits[r]
        head = (head + 1) % DT
        for r in (0, 1):
            Qp_r = Ql[r] + pce * Qh[r]
            ntot = nl[r] + nh[r]
            hn = (nh[r] + Qh[r]) / (ntot + Ql[r] + Qh[r] + 1e-9)
            wait = Qp_r / max(served[r], 0.5)
            w = exits[r] / (exits[r] + 1.0)
            J[r] += kJ * w * (min(wait, 500.0) - J[r])
            tf = (1.0 + al[r] * (max(ntot, 0.0) / 100.0) ** pa + sg[r] * (0.5 / green[r] - 1.0)
                  + be[r] * min(Qp_r, 2000.0) / 100.0 + bx * E[r] / 10.0 + vh[r] * hn + bj[r] * J[r] / 10.0
                  + g3v * F[r])
            V = vf[r] / min(max(tf, 0.95), 60.0)
            v[r] += kv * (V - v[r])
            v[r] = min(max(v[r], 0.5), 80.0)
        L += a1 * (g1 * math.tanh((v[0] - v[1]) / 10.0) - L)
        S = (1 - a2s) * S + abs(uc - prev_crew)
        prev_crew = uc
        work = (1 - min(max(uc, 0.0), 1.0)) * (exits[0] + exits[1]) / 24.0
        Fg += a2f * (min(work, 5.0) - Fg)
        for r in (0, 1):
            if Ql[r] + pce * Qh[r] > q3:
                F[r] += a3u * (1.0 - F[r])
            else:
                F[r] -= a3d * F[r]
        out[t, 0], out[t, 1], out[t, 2], out[t, 3] = exits[0], exits[1], v[0], v[1]
    return out
