"""Gray-box model for ad_auction: nested audience rings, budget-paced auction, committed-purchase pipeline.

Interface: greybox/common/fit.py (SPEC, MODULES, to_natural, to_raw, normalize, simulate). stdlib + numpy only;
copied as-is into the submission folder.

Structure (base, from the brief's facts and Run-1 behaviours B1-B12, plans/ad_auction-plan.md):
  audience   nested rings r over breadth edges EDGES; targeting breadth b covers ring r by
             cov_r = clip((b - lo_r)/(hi_r - lo_r), 0, 1) (ring 0 always). Ring size n_r = width_r * exp(nu*m_r),
             m_r = ring mid - 0.55. Available fraction a_r = max(0, 1 - X_r - F_r).
  auction    opportunities o_r = N0 n_r cov_r a_r; win prob p_r = bid^h / (bid^h + K_r^h),
             K_r = K0 exp(kap m_r + g1 R_r); price pi_r = pi0 (bid/1.5)^rho exp(kp m_r).
  pacing     uncapped spend S_u = sum p_r o_r pi_r; throttle th = (1 + (S_u/cap)^SMOOTH)^(-1/SMOOTH);
             impressions I_r = th p_r o_r; spend = th S_u; win_rate = sum I_r / sum o_r   (B2, B5).
  purchases  J_r = I_r q0 exp(qm m_r) (1 + g3 P)                  ('started purchases remain committed')
  pipeline   DEAD-tick shift register -> prepare stage (rate a_p) -> fulfillment queue with work
             w_r = exp(om m_r) per purchase ('different audiences require different amounts of work');
             done work = smooth-min(capf, kf * Qw); conversions = done * Qn / Qw        (B6, B7a).
  pool       X_r (unavailable: committed / converted people) += eps_x J_r/(N0 n_r) (1 - X_r - F_r),
             returns at rate ret ('converted customers take time to become available again')   (B3, B4).
Mechanism modules (written from the theses in plans/ad_auction-plan.md before fitting):
  m1 rival capital: R_r <- R_r + a_m1 (spend_r/(n_r*SREF) - R_r); raises the competing threshold K_r by exp(g1 R_r).
  m2 exposure fatigue: F_r <- F_r + e2 I_r/(N0 n_r) (1 - X_r - F_r) - a_m2 F_r  (exposure removes reachable people).
  m3 broad priming: P <- P + a_m3 (E - P), E = broad-ring exposure sum_r I_r max(m_r, 0)/(N0*0.1); purchases x(1 + g3 P).
Reset convention: X = F = R = P = 0, pipeline empty (the initial reading is ignored, B1).
"""
import math
import numpy as np

OBSERVABLES = ('win_rate', 'spend', 'conversions')
CONTROLS = ('bid', 'budget_cap', 'targeting_breadth')
BOUNDS = {'bid': (0.0, 5.0), 'budget_cap': (0.0, 100.0), 'targeting_breadth': (0.1, 1.0)}
UNITS = {'win_rate': 'linear', 'spend': 'linear', 'conversions': 'linear'}
NOISE = {'win_rate': 0.0047, 'spend': 0.066, 'conversions': 0.0123}
CLAMP = {'win_rate': [0.0, 1.0], 'spend': [0.0, 100.0], 'conversions': [0.0, 50.0]}
EDGES = (0.0, 0.1, 0.325, 0.55, 0.775, 1.0)
N0 = 100.0
SREF = 25.0
SMOOTH = 12.0
DEAD = 2

SPEC = {
    # auction / audience
    'K0': (2.5, 'pos'), 'h': (2.0, 'pos'), 'kap': (1.0, 'free'), 'nu': (0.0, 'free'),
    'pi0': (2.0, 'pos'), 'rho': (0.8, 'free'), 'kp': (0.5, 'free'),
    # purchases / pipeline
    'q0': (0.5, 'pos'), 'qm': (0.0, 'free'), 'om': (1.0, 'free'), 'capf': (5.0, 'pos'),
    'kf': (0.15, 'unit'), 'a_p': (0.5, 'unit'),
    # pool depletion by committed / converted people
    'eps_x': (0.3, 'pos'), 'ret': (0.02, 'unit'),
    # mechanisms
    'a_m1': (0.05, 'unit'), 'g1': (0.2, 'free'),
    'a_m2': (0.03, 'unit'), 'e2': (0.05, 'pos'),
    'a_m3': (0.02, 'unit'), 'g3': (0.2, 'free'),
}
MODULES = {
    'm1': (['a_m1', 'g1'], {'g1': 0.0}),
    'm2': (['a_m2', 'e2'], {'e2': 0.0}),
    'm3': (['a_m3', 'g3'], {'g3': 0.0}),
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
        return math.exp(min(max(raw, -50.0), 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _logit(value)
    if kind == 'pos':
        return math.log(max(value, 1e-300))
    return value


def normalize(action, bounds):
    """Physical action dict -> (bid, budget_cap, breadth), clipped to bounds (the model works in physical units)."""
    out = []
    for c in CONTROLS:
        lo, hi = (bounds or {}).get(c, BOUNDS[c])
        out.append(min(max(float(action[c]), lo), hi))
    return tuple(out)


def _rings():
    lo, hi = EDGES[:-1], EDGES[1:]
    mids = [0.5 * (a + b) - 0.55 for a, b in zip(lo, hi)]
    return list(lo), list(hi), mids


def simulate(p, initial, actions):
    T = len(actions)
    out = np.zeros((T, 3))
    if T == 0:
        return out
    lo, hi, mids = _rings()
    nr = len(mids)
    widths = [b - a for a, b in zip(lo, hi)]
    n = [w * math.exp(min(max(p['nu'] * m, -30), 30)) for w, m in zip(widths, mids)]
    Kbase = [p['K0'] * math.exp(min(max(p['kap'] * m, -30), 30)) for m in mids]
    pim = [math.exp(min(max(p['kp'] * m, -30), 30)) for m in mids]
    qr = [p['q0'] * math.exp(min(max(p['qm'] * m, -30), 30)) for m in mids]
    wr = [math.exp(min(max(p['om'] * m, -30), 30)) for m in mids]
    broad = [max(m, 0.0) for m in mids]
    h, pi0, rho = p['h'], p['pi0'], p['rho']
    capf, kf, a_p = p['capf'], p['kf'], p['a_p']
    eps_x, ret = p['eps_x'], p['ret']
    a1, g1, a2, e2, a3, g3 = p['a_m1'], p['g1'], p['a_m2'], p['e2'], p['a_m3'], p['g3']
    X = [0.0] * nr
    F = [0.0] * nr
    R = [0.0] * nr
    P = 0.0
    shift_n = [0.0] * DEAD
    shift_w = [0.0] * DEAD
    Pn = Pw = 0.0          # prepare stage (purchases, work)
    Qn = Qw = 0.0          # fulfillment queue
    for t in range(T):
        bid, cap, b = actions[t]
        cap = max(cap, 0.0)
        bidh = bid ** h if bid > 0 else 0.0
        bidprice = pi0 * (bid / 1.5) ** rho if bid > 0 else 0.0
        o = [0.0] * nr
        pw = [0.0] * nr
        su = 0.0
        osum = 0.0
        for r in range(nr):
            if r == 0:
                cov = 1.0
            else:
                cov = min(max((b - lo[r]) / (hi[r] - lo[r]), 0.0), 1.0)
            if cov <= 0.0:
                continue
            a = 1.0 - X[r] - F[r]
            if a <= 0.0:
                continue
            o[r] = N0 * n[r] * cov * a
            K = Kbase[r] * math.exp(min(max(g1 * R[r], -30.0), 30.0)) if g1 else Kbase[r]
            pr = bidh / (bidh + K ** h) if bidh > 0 else 0.0
            pw[r] = pr
            su += pr * o[r] * bidprice * pim[r]
            osum += o[r]
        if su > 0.0 and cap > 0.0:
            ratio = min(su / cap, 1e6)
            th = (1.0 + ratio ** SMOOTH) ** (-1.0 / SMOOTH)
        else:
            th = 0.0 if cap <= 0.0 else 1.0
        spend = th * su
        imp_tot = 0.0
        jn = jw = 0.0
        E = 0.0
        for r in range(nr):
            if o[r] <= 0.0:
                I = 0.0
            else:
                I = th * pw[r] * o[r]
            imp_tot += I
            J = I * qr[r] * (1.0 + g3 * P) if g3 else I * qr[r]
            if J < 0.0:
                J = 0.0
            jn += J
            jw += J * wr[r]
            E += I * broad[r]
            size = N0 * n[r]
            free = 1.0 - X[r] - F[r]
            if free < 0.0:
                free = 0.0
            dx = eps_x * J / size * free
            df = e2 * I / size * free if e2 else 0.0
            if dx + df > free:
                s = free / (dx + df)
                dx *= s
                df *= s
            X[r] += dx - ret * X[r]
            if e2:
                F[r] += df - a2 * F[r]
            if g1:
                sp = th * pw[r] * o[r] * bidprice * pim[r]
                R[r] += a1 * (sp / (n[r] * SREF) - R[r])
        if g3:
            P += a3 * (E / (N0 * 0.1) - P)
        win = imp_tot / osum if osum > 0.0 else 0.0
        # pipeline: dead-time shift register -> prepare -> fulfillment queue
        if DEAD:
            en, ew = shift_n[0], shift_w[0]
            shift_n = shift_n[1:] + [jn]
            shift_w = shift_w[1:] + [jw]
        else:
            en, ew = jn, jw
        mn, mw = a_p * Pn, a_p * Pw
        Pn += en - mn
        Pw += ew - mw
        Qn += mn
        Qw += mw
        if Qw > 1e-12:
            want = kf * Qw
            done = (want ** -4 + capf ** -4) ** -0.25 if want > 0 else 0.0
            if done > Qw:
                done = Qw
            conv = done * Qn / Qw
            Qn -= conv
            Qw -= done
        else:
            conv = 0.0
        out[t, 0] = min(max(win, 0.0), 1.0)
        out[t, 1] = min(max(spend, 0.0), 100.0)
        out[t, 2] = min(max(conv, 0.0), 50.0)
    return out
