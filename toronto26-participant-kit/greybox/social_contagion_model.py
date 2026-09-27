"""Social contagion gray-box model v0: two communities x two audience types, onboarding queue with a
workforce shared with existing members, a disappointed pool that reconsiders after a delay, and three
pluggable history mechanisms (m1 credibility, m2 incentive expectations, m3 cross-community ties).

Controls (normalized): us = seeding/9, ui = incentive/2, ub = bridge_outreach/0.6; bridge fraction b = 0.6 ub
(clipped to [0, 1]). Local effort sl = us (1 - b), bridge effort sb = us b.
Outreach effort passes through ND first-order lag stages (a_d) before it creates interest (dead time B3).

Per community c in (A, B), types k in (r = relationship/deliberative, i = incentive-led):
  potential N_ck = N_c * (1 - phi_c | phi_c);  susceptible S_ck = max(N_ck - M_ck - Q_ck - D_ck, 0)
  force     f_c = beta_c M_c / N_c + sig_c sl_lag + tau_c sb_lag M_o / N_o + g3 R M_o / N_o (m3) + eps
  interest  new_cr = h(f_c * cred) S_cr ;  new_ci = h((shi f_c + iota ui) * cred) S_ci,  h(x) = 1 - exp(-x)
  queue     Q_ck += new_ck ; onboarding capacity cap_c = kap_c / (1 + om M_c / 100) (workforce shared with
            members); onboarded_c = cap_c Q_c / (cap_c + Q_c) split by type; queue abandonment qa -> D
  churn     M_ck -> D_ck at h(d_k exp(-gret ui) + g2 max(E - ui, 0))    (g2 term: m2 disappointment)
  reconsider D_ck -> S at rho
  m1        Cm <- Cm + a1 (waiting - Cm), waiting = Q_tot / cap_tot / 10; cred = exp(-g1 Cm)
  m2        E <- E + a2 (ui - E), E(0) = e0 (reference expectation at reset)
  m3        R <- R + a3u sb (1 - R) - a3d R
Output adopters_c = M_cr + M_ci.
Reset: M_ci = psi_c * reading_c, M_cr = (1 - psi_c) reading_c; Q = D = lags = Cm = R = 0; E = e0.
"""
import math
import numpy as np

OBSERVABLES = ('adopters_a', 'adopters_b')
CONTROLS = ('seeding', 'incentive', 'bridge_outreach')
RECOVERY = {'seeding': 0.0, 'incentive': 0.0, 'bridge_outreach': 0.0}
PULSE = {'seeding': 9.0, 'incentive': 2.0, 'bridge_outreach': 0.6}
UNITS = {'adopters_a': 'log', 'adopters_b': 'log'}
NOISE = {'adopters_a': 0.01, 'adopters_b': 0.01}   # residual scale (true noise 0.25%; misfit dominates)
CLAMP = {'adopters_a': [0.1, 5000.0], 'adopters_b': [0.1, 5000.0]}
ND = 2
FIXED = ()

SPEC = {
    # populations and mixes
    'NA': (400.0, 'pos'), 'NB': (250.0, 'pos'), 'phiA': (0.3, 'unit'), 'phiB': (0.4, 'unit'),
    'psiA': (0.25, 'unit'), 'psiB': (0.25, 'unit'),
    # interest
    'betaA': (0.02, 'pos'), 'betaB': (0.02, 'pos'), 'sigA': (0.05, 'pos'), 'sigB': (0.02, 'pos'),
    'tauA': (0.02, 'pos'), 'tauB': (0.05, 'pos'), 'shi': (1.0, 'pos'), 'iota': (0.01, 'pos'),
    'eps': (1e-4, 'pos'), 'a_d': (0.4, 'unit'),
    # onboarding
    'kapA': (8.0, 'pos'), 'kapB': (4.0, 'pos'), 'om': (0.3, 'pos'), 'qa': (0.01, 'unit'),
    # churn and reconsideration
    'dr': (0.01, 'unit'), 'di': (0.05, 'unit'), 'gret': (2.0, 'pos'), 'rho': (0.02, 'unit'),
    # m1 credibility
    'a1': (0.05, 'unit'), 'g1': (0.3, 'pos'),
    # m2 incentive expectations
    'a2': (0.05, 'unit'), 'g2': (0.05, 'pos'), 'e0': (0.3, 'unit'),
    # m3 cross-community ties
    'a3u': (0.05, 'unit'), 'a3d': (0.01, 'unit'), 'g3': (0.05, 'pos'),
}
MODULES = {
    'm1': (['a1', 'g1'], {'g1': 0.0}),
    'm2': (['a2', 'g2', 'e0'], {'g2': 0.0, 'e0': 0.0}),
    'm3': (['a3u', 'a3d', 'g3'], {'g3': 0.0}),
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
        lo, hi = bounds.get(c, (RECOVERY[c], PULSE[c]))
        v = min(max(float(action[c]), lo), hi)
        out.append((v - RECOVERY[c]) / (PULSE[c] - RECOVERY[c]))
    return tuple(out)


def _h(x):
    return 1.0 - math.exp(-min(max(x, 0.0), 50.0))


def _init(initial, name, default):
    try:
        v = float(initial[name])
    except (KeyError, TypeError, ValueError):
        v = default
    if not math.isfinite(v):
        v = default
    return min(max(v, 0.1), 5000.0)


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 2))
    U = np.asarray(actions, dtype=float).reshape(T, 3)
    us, ui, ub = U[:, 0], U[:, 1], U[:, 2]
    b = np.clip(0.6 * ub, 0.0, 1.0)
    sl, sb = us * (1.0 - b), us * b
    a_d = p['a_d']
    for _ in range(ND):                       # outreach lag stages start empty
        for arr in (sl, sb):
            q = 0.0
            for t in range(T):
                q += a_d * (arr[t] - q)
                arr[t] = q
    N = (min(p['NA'], 1e5), min(p['NB'], 1e5))
    phi = (p['phiA'], p['phiB'])
    Nk = ((N[0] * (1 - phi[0]), N[0] * phi[0]), (N[1] * (1 - phi[1]), N[1] * phi[1]))
    beta = (min(p['betaA'], 10.0), min(p['betaB'], 10.0))
    sig = (min(p['sigA'], 10.0), min(p['sigB'], 10.0))
    tau = (min(p['tauA'], 10.0), min(p['tauB'], 10.0))
    shi, iota, eps = min(p['shi'], 100.0), min(p['iota'], 10.0), min(p['eps'], 1.0)
    kap = (min(p['kapA'], 1e4), min(p['kapB'], 1e4))
    om, qa = min(p['om'], 100.0), p['qa']
    dr, di, gret, rho = p['dr'], p['di'], min(p['gret'], 50.0), p['rho']
    a1, g1 = p['a1'], min(p['g1'], 50.0)
    a2, g2, e0 = p['a2'], min(p['g2'], 10.0), p['e0']
    a3u, a3d, g3 = p['a3u'], p['a3d'], min(p['g3'], 10.0)

    init = (_init(initial, 'adopters_a', 50.0), _init(initial, 'adopters_b', 37.0))
    psi = (p['psiA'], p['psiB'])
    M = [[init[c] * (1 - psi[c]), init[c] * psi[c]] for c in range(2)]
    Q = [[0.0, 0.0], [0.0, 0.0]]
    D = [[0.0, 0.0], [0.0, 0.0]]
    Cm, E, R = 0.0, e0, 0.0
    out = np.empty((T, 2))
    for t in range(T):
        uit, slt, sbt = ui[t], sl[t], sb[t]
        cred = math.exp(-g1 * Cm) if g1 > 0 else 1.0
        Mtot = (M[0][0] + M[0][1], M[1][0] + M[1][1])
        chr_ = [dr * math.exp(-gret * uit), di * math.exp(-gret * uit)]
        dis = g2 * max(E - uit, 0.0)
        caps, qtot = [0.0, 0.0], 0.0
        newM = [[0.0, 0.0], [0.0, 0.0]]
        for c in range(2):
            o = 1 - c
            fo = Mtot[o] / N[o]
            f = beta[c] * Mtot[c] / N[c] + sig[c] * slt + tau[c] * sbt * fo + g3 * R * fo + eps
            new_r = _h(f * cred) * max(Nk[c][0] - M[c][0] - Q[c][0] - D[c][0], 0.0)
            new_i = _h((shi * f + iota * uit) * cred) * max(Nk[c][1] - M[c][1] - Q[c][1] - D[c][1], 0.0)
            cap = kap[c] / (1.0 + om * Mtot[c] / 100.0)
            qc = Q[c][0] + Q[c][1]
            onb = cap * qc / (cap + qc) if qc > 1e-12 else 0.0
            frac = onb / qc if qc > 1e-12 else 0.0
            caps[c] = cap
            qtot += qc
            for k, new in ((0, new_r), (1, new_i)):
                on_k = frac * Q[c][k]
                ab_k = qa * (Q[c][k] - on_k)
                lv_k = _h(chr_[k] + dis) * M[c][k]
                rc_k = rho * D[c][k]
                Q[c][k] = max(Q[c][k] + new - on_k - ab_k, 0.0)
                newM[c][k] = min(max(M[c][k] + on_k - lv_k, 0.0), 1e5)
                D[c][k] = max(D[c][k] + lv_k + ab_k - rc_k, 0.0)
        M = newM
        if g1 > 0:
            Cm += a1 * (qtot / max(caps[0] + caps[1], 1e-6) / 10.0 - Cm)
        E += a2 * (uit - E)
        if g3 > 0:
            R += a3u * sbt * (1.0 - R) - a3d * R
        out[t, 0] = M[0][0] + M[0][1]
        out[t, 1] = M[1][0] + M[1][1]
    return np.clip(out, 0.1, 5000.0)
