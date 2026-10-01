"""Gray-box model for ad_auction, v3 (round 3, plans/round3-findings.md; copy of v2 with one switchable addition):
   - module zs: ring-dependent purchase-fatigue driver, Z_r += e_z * exp(dz * m_r) * I_r/size_r * (1 - Z_r) - a_z Z_r
     (dz = 0 reproduces v2 exactly). R5 segment 1 (rested broad start, cap 100) showed v2's fatigue biting too early
     at broad breadth; dz lets the per-member fatigue rate differ between narrow and broad rings.
v2 description:
Gray-box model for ad_auction, v2 (round 2, plans/ad_auction-round2-diagnosis.md):
  v2 changes against v1 (greybox/ad_auction_model.py), each switchable so v1 is recovered exactly:
   - queue smoothing exponent `qx` (v1: 4; a large value gives a hard capacity plateau, B22/B23);
   - module fz: purchase-side exposure fatigue Z_r (driver: impressions per ring member, acts on purchases only,
     rate a_z in [0.01, 0.1]), J_r *= (1 - Z_r)  (B25/B26/B35);
   - module cm: people with pending purchases are unavailable: a_r -= kc * C_r / size_r, C_r = per-ring
     purchases in the pipeline (pooled FIFO mixing)  (B24);
   - module pm: auction win probability ceiling pmax (B29).
v1 description:
Gray-box model for ad_auction: nested audience rings, budget-paced auction, committed-purchase pipeline.

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
  m1 rival capital: R_r <- R_r + a_m1 (win share_r - R_r); scales the competing threshold K_r by exp(clip(g1 R_r, +-3))
     (free-sign gain; v0 used spend density, contradicted by R1 vs R2, review G3).
  m2 exposure fatigue: F_r <- F_r + e2 I_r/(N0 n_r) (1 - X_r - F_r) - a_m2 F_r  (exposure removes reachable people).
  m3 broad priming: P <- P + a_m3 (E - P), E = broad-ring exposure sum_r I_r max(m_r, 0)/(N0*0.1);
     purchases x(1 + 0.8 tanh(g3 P)), bounded in [0.2, 1.8] so priming can never switch purchases off (review §5).
Review responses (plans/ad_auction-review.md): G1 readiness pool Y_r (fast, acts on purchases only:
  J_r = I_r q_r (1 - Y_r)); G2 second, fast opportunity pool X2_r next to the slow X_r.
Reset convention: X = X2 = Y = F = R = P = 0, pipeline empty (the initial reading is ignored, B1).
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
    # pool depletion by committed / converted people: slow (eps_x, ret) + fast (eps_x2, ret2) opportunity pools (G2)
    'eps_x': (0.3, 'pos'), 'ret': (0.02, 'unit'),
    'eps_x2': (0.0, 'pos'), 'ret2': (0.04, 'unit'),   # fitted eps_x2 -> 0 (G2 rejected): held off
    # purchase readiness pool (G1): acts on purchases only
    'eps_y': (1.0, 'pos'), 'ret_y': (0.05, 'unit'),
    # mechanisms
    'a_m1': (0.05, 'unit'), 'g1': (0.2, 'free'),
    'a_m2': (0.03, 'unit'), 'e2': (0.05, 'pos'),
    'a_m3': (0.02, 'unit'), 'g3': (0.2, 'free'),
    # v2
    'qx': (4.0, 'pos'),
    'e_z': (1.0, 'pos'), 'a_z': (0.03, 'rz'),
    'kc': (1.0, 'pos'),
    'pmax': (0.9, 'unit'),
    # v3
    'dz': (0.0, 'free'),
}
FIXED = ('eps_x2', 'ret2')
MODULES = {
    'm1': (['a_m1', 'g1'], {'g1': 0.0}),
    'm2': (['a_m2', 'e2'], {'e2': 0.0}),
    'm3': (['a_m3', 'g3'], {'g3': 0.0}),
    'fz': (['e_z', 'a_z'], {'e_z': 0.0}),
    'cm': (['kc'], {'kc': 0.0}),
    'pm': (['pmax'], {'pmax': 1.0}),
    'zs': (['dz'], {'dz': 0.0}),
}
AZ_LO, AZ_HI = 0.01, 0.1


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def _logit(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1.0 - p))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'rz':
        return AZ_LO + (AZ_HI - AZ_LO) * _sigmoid(raw)
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(max(raw, -50.0), 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'rz':
        return _logit((value - AZ_LO) / (AZ_HI - AZ_LO))
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
    eps_x2, ret2 = p['eps_x2'], p['ret2']
    eps_y, ret_y = p['eps_y'], p['ret_y']
    a1, g1, a2, e2, a3, g3 = p['a_m1'], p['g1'], p['a_m2'], p['e2'], p['a_m3'], p['g3']
    qx = min(max(p.get('qx', 4.0), 1.0), 60.0)
    e_z, a_z = p.get('e_z', 0.0), p.get('a_z', 0.03)
    dz = min(max(p.get('dz', 0.0), -8.0), 8.0)
    zr = [e_z * math.exp(dz * m) for m in mids]
    kc = p.get('kc', 0.0)
    pmax = p.get('pmax', 1.0)
    sizes = [N0 * nn for nn in n]
    Z = [0.0] * nr
    C = [0.0] * nr
    X = [0.0] * nr
    X2 = [0.0] * nr
    Y = [0.0] * nr
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
            a = 1.0 - X[r] - X2[r] - F[r]
            if kc:
                a -= kc * C[r] / sizes[r]
            if a <= 0.0:
                continue
            o[r] = N0 * n[r] * cov * a
            K = Kbase[r] * math.exp(min(max(g1 * R[r], -3.0), 3.0)) if g1 else Kbase[r]
            pr = pmax * bidh / (bidh + K ** h) if bidh > 0 else 0.0
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
            J = I * qr[r] * (1.0 - Y[r])
            if e_z:
                J *= 1.0 - Z[r]
                Z[r] += zr[r] * I / sizes[r] * (1.0 - Z[r]) - a_z * Z[r]
                Z[r] = min(max(Z[r], 0.0), 1.0)
            if g3:
                J *= 1.0 + 0.8 * math.tanh(g3 * P)      # bounded priming: multiplier in [0.2, 1.8]
            if J < 0.0:
                J = 0.0
            if kc:
                C[r] += J
            jn += J
            jw += J * wr[r]
            E += I * broad[r]
            size = N0 * n[r]
            free = 1.0 - X[r] - X2[r] - F[r]
            if kc:
                free -= kc * C[r] / size
            if free < 0.0:
                free = 0.0
            dx = eps_x * J / size * free
            dx2 = eps_x2 * J / size * free
            df = e2 * I / size * free if e2 else 0.0
            if dx + dx2 + df > free:
                s = free / (dx + dx2 + df)
                dx *= s
                dx2 *= s
                df *= s
            X[r] += dx - ret * X[r]
            X2[r] += dx2 - ret2 * X2[r]
            dy = eps_y * J / size
            Y[r] += dy * (1.0 - Y[r]) - ret_y * Y[r]
            if Y[r] < 0.0:
                Y[r] = 0.0
            elif Y[r] > 1.0:
                Y[r] = 1.0
            if e2:
                F[r] += df - a2 * F[r]
            if g1:
                R[r] += a1 * (th * pw[r] - R[r])      # G3 variant (b): driver = our win share in ring r
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
            if want > 0:
                lo_, hi_ = (want, capf) if want < capf else (capf, want)
                done = lo_ * (1.0 + (lo_ / hi_) ** qx) ** (-1.0 / qx)
            else:
                done = 0.0
            if done > Qw:
                done = Qw
            conv = done * Qn / Qw
            Qn -= conv
            Qw -= done
        else:
            conv = 0.0
        if kc:
            ctot = sum(C)
            if ctot > 1e-12:
                keep = max(0.0, 1.0 - conv / ctot)
                for r in range(nr):
                    C[r] *= keep
        out[t, 0] = min(max(win, 0.0), 1.0)
        out[t, 1] = min(max(spend, 0.0), 100.0)
        out[t, 2] = min(max(conv, 0.0), 50.0)
    return out
