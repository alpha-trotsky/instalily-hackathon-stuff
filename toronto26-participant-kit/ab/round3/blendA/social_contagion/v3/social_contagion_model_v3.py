"""Social contagion gray-box model v3 (round 3): the shipped v2 (= the v1 module with M1 off, M2 linear gap) plus a
promise-at-recruitment term.

v3 change (round-3 run R6: the same u.7 action gives 164 / 101 with incentive from reset (R4) but ~200 / 136 when the
incentive is added 60 ticks after recruitment began): every waiting cohort and member carries the promise (the
normalized incentive) in force when it entered the queue; initial members carry none ("no paid promises"). Per
community the promise mass is tracked through the queue (Pq) and the member stock (Pm, removed pro rata by churn and
disappointment), so P_c = Pm_c / M_c is the members' mean promise. The surplus s_c = max(ui - P_c, 0) (members paid
more than they were promised) lowers churn, h(dr exp(-gret ui - gs s_c)), and lifts word of mouth,
beta_c Mt_c/N_c (1 + gw s_c). Members who carry a promise churn faster, exp(gp P_c) (the incentive-led audience is
less loyal), so incentive given with recruitment buys less than incentive given after it. Under a constant hold the surplus fades as members turn over (no integrator); both gains
are boxed. gs and gw are owned by m2 (incentive expectations).

v1 header follows.
Social contagion gray-box model v1 (Phase C; v0 is kept in fits/social_contagion/social_contagion_model_v0.py).

Changes from v0 (review G1-G3, G7, G8): bounded ('box') parameters everywhere, finite pools, one audience per
community (the v0 type split was not identified), the capacity-limited onboarding queue replaced by a first-order
onboarding stage (kap/om/qa were pinned), a separate 3-stage lag on the bridge-introduction path (G3), a bounded
direct incentive recruitment per community (G7), the reset transient as an explicit initial "expectant" share that
leaves through a ramping hazard (G8; E starts at 0), and a core of K_c members that M2 disappointment never
touches (G2; owned by m2).

Controls (normalized): us = seeding/9, ui = incentive/2, ub = bridge/0.6; b = clip(0.6 ub, 0, 1).
Local effort sl = us (1 - b) through ND lag stages (a_d); bridge effort sb = us b through NB lag stages (a_b).

Per community c (o = other community):
  members  Mt_c = M_c + X_c  (X_c = initial expectant members, psi_c of the reading at reset)
  force    f_c = beta_c Mt_c/N_c + sig_c sl + tau_c sb Mt_o/N_o + g3 R Mt_o/N_o (m3) + eps
  interest new_c = h((f_c + iota_c ui) cred) S_c,  S_c = max(N_c - Mt_c - Q_c - D_c, 0),  h(x) = 1 - exp(-x)
  onboard  on_c = kon Q_c
  churn    M_c -> D_c at h(dr exp(-gret ui));  X_c -> D_c at h(kr L), L <- L + ar (1 - L), L(0) = 0
  m2       disappointment h(g2 max(E - ui, 0)) max(M_c - K_c, 0) -> D_c;  E <- E + a2 (ui - E), E(0) = 0
  reconsider D_c -> S at rho
  m1       Cm <- Cm + a1 (departures / members * 10 - Cm); cred = exp(-g1 Cm)
  m3       R <- R + a3u sb (1 - R) - a3d R;  R(0) = 0
Output adopters_c = M_c + X_c.
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
ND = 2          # local outreach lag stages
NB = 3          # bridge-introduction lag stages (G3)
FIXED = ()

# name: (initial natural value, (lo, hi)) -- every parameter is a box through a sigmoid
SPEC = {
    'NA': (400.0, (80.0, 3000.0)), 'NB': (300.0, (60.0, 3000.0)),
    'betaA': (0.03, (0.0, 2.0)), 'betaB': (0.03, (0.0, 2.0)),
    'sigA': (0.02, (0.0, 1.0)), 'sigB': (0.008, (0.0, 1.0)),
    'tauA': (0.02, (0.0, 1.0)), 'tauB': (0.03, (0.0, 1.0)),
    'iotaA': (0.003, (0.0, 0.1)), 'iotaB': (0.005, (0.0, 0.1)),
    'eps': (1e-4, (0.0, 0.01)),
    'a_d': (0.35, (0.02, 1.0)), 'a_b': (0.25, (0.02, 1.0)), 'kon': (0.3, (0.01, 1.0)),
    'dr': (0.02, (0.0, 0.3)), 'gret': (1.0, (0.0, 8.0)), 'rho': (0.03, (0.0, 0.5)),
    'psiA': (0.25, (0.0, 0.8)), 'psiB': (0.25, (0.0, 0.8)), 'kr': (0.2, (0.0, 1.0)), 'ar': (0.3, (0.01, 1.0)),
    # m1 credibility
    'a1': (0.05, (0.001, 1.0)), 'g1': (1.0, (0.0, 20.0)),
    # m2 incentive expectations (+ core that is never disappointed)
    'a2': (0.03, (0.001, 1.0)), 'g2': (0.1, (0.0, 1.0)), 'KA': (43.0, (0.0, 200.0)), 'KB': (31.0, (0.0, 200.0)),
    # v3 promise surplus (members recruited before the incentive rose): retention and word-of-mouth gains
    'gs': (1.0, (0.0, 8.0)), 'gw': (0.3, (0.0, 5.0)), 'gp': (0.0, (0.0, 4.0)),
    # m3 cross-community ties
    'a3u': (0.01, (0.0005, 1.0)), 'a3d': (0.005, (0.0002, 0.5)), 'g3': (0.05, (0.0, 3.0)),
}
MODULES = {
    'm1': (['a1', 'g1'], {'g1': 0.0}),
    'm2': (['a2', 'g2', 'KA', 'KB', 'gs', 'gw', 'gp'], {'g2': 0.0, 'gs': 0.0, 'gw': 0.0, 'gp': 0.0}),
    'm3': (['a3u', 'a3d', 'g3'], {'g3': 0.0}),
}


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def to_natural(name, raw):
    lo, hi = SPEC[name][1]
    return lo + (hi - lo) * _sigmoid(raw)


def to_raw(name, value):
    lo, hi = SPEC[name][1]
    v = min(max((value - lo) / (hi - lo), 1e-9), 1 - 1e-9)
    return math.log(v / (1 - v))


def at_bounds(p, tol=0.002):
    """Parameters within tol (relative to the box width) of a box edge."""
    out = []
    for n, v in p.items():
        if n in SPEC:
            lo, hi = SPEC[n][1]
            if (v - lo) / (hi - lo) < tol or (hi - v) / (hi - lo) < tol:
                out.append(n)
    return out


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


def _lag(arr, rate, stages):
    out = np.array(arr, dtype=float)
    for _ in range(stages):
        q = 0.0
        for t in range(len(out)):
            q += rate * (out[t] - q)
            out[t] = q
    return out


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 2))
    U = np.nan_to_num(np.asarray(actions, dtype=float).reshape(T, 3))
    us, ui, ub = np.clip(U[:, 0], 0, 2), np.clip(U[:, 1], 0, 1), np.clip(U[:, 2], 0, 2)
    b = np.clip(0.6 * ub, 0.0, 1.0)
    sl = _lag(us * (1.0 - b), p['a_d'], ND).tolist()
    sb = _lag(us * b, p['a_b'], NB).tolist()
    ui = ui.tolist()
    N = (p['NA'], p['NB'])
    beta, sig, tau = (p['betaA'], p['betaB']), (p['sigA'], p['sigB']), (p['tauA'], p['tauB'])
    iota, eps = (p['iotaA'], p['iotaB']), p['eps']
    kon, dr, gret, rho = p['kon'], p['dr'], p['gret'], p['rho']
    kr, ar = p['kr'], p['ar']
    a1, g1 = p['a1'], p['g1']
    a2, g2, K = p['a2'], p['g2'], (p['KA'], p['KB'])
    a3u, a3d, g3 = p['a3u'], p['a3d'], p['g3']
    gs, gw, gp = p.get('gs', 0.0), p.get('gw', 0.0), p.get('gp', 0.0)

    r0 = (_init(initial, 'adopters_a', 50.0), _init(initial, 'adopters_b', 37.0))
    psi = (p['psiA'], p['psiB'])
    M = [r0[0] * (1 - psi[0]), r0[1] * (1 - psi[1])]
    X = [r0[0] * psi[0], r0[1] * psi[1]]
    Q = [0.0, 0.0]
    D = [0.0, 0.0]
    Pq = [0.0, 0.0]     # promise mass of waiting cohorts
    Pm = [0.0, 0.0]     # promise mass of members (initial members carry none)
    L, Cm, E, R = 0.0, 0.0, 0.0, 0.0
    out = np.empty((T, 2))
    for t in range(T):
        uit, slt, sbt = ui[t], sl[t], sb[t]
        cred = math.exp(-g1 * Cm) if g1 > 0 else 1.0
        L += ar * (1.0 - L)
        hx = _h(kr * L)
        hd = _h(g2 * (E - uit)) if (g2 > 0 and E > uit) else 0.0
        Mt = (M[0] + X[0], M[1] + X[1])
        dep_tot = 0.0
        newM, newX = [0.0, 0.0], [0.0, 0.0]
        for c in range(2):
            Pc = min(Pm[c] / M[c], 1.0) if M[c] > 1e-9 else 0.0
            sur = uit - Pc if uit > Pc else 0.0
            hc = _h(dr * math.exp(-gret * uit - gs * sur + gp * Pc))
            fo = Mt[1 - c] / N[1 - c]
            f = beta[c] * Mt[c] / N[c] * (1.0 + gw * sur) + sig[c] * slt + tau[c] * sbt * fo + g3 * R * fo + eps
            S = N[c] - Mt[c] - Q[c] - D[c]
            new = _h((f + iota[c] * uit) * cred) * S if S > 0 else 0.0
            on = kon * Q[c]
            xl = hx * X[c]
            ch = hc * M[c]
            ds = hd * (M[c] - K[c]) if M[c] > K[c] else 0.0
            rc = rho * D[c]
            pon = kon * Pq[c]
            Pq[c] = max(Pq[c] + new * uit - pon, 0.0)
            keep = max(1.0 - (ch + ds) / M[c], 0.0) if M[c] > 1e-9 else 0.0
            Pm[c] = Pm[c] * keep + pon
            Q[c] = max(Q[c] + new - on, 0.0)
            newM[c] = min(max(M[c] + on - ch - ds, 0.0), 1e5)
            newX[c] = max(X[c] - xl, 0.0)
            D[c] = min(max(D[c] + xl + ch + ds - rc, 0.0), 1e5)
            dep_tot += xl + ch + ds
        if g1 > 0:
            Cm += a1 * (10.0 * dep_tot / max(Mt[0] + Mt[1], 1.0) - Cm)
        E += a2 * (uit - E)
        if g3 > 0:
            R += a3u * sbt * (1.0 - R) - a3d * R
        M, X = newM, newX
        out[t, 0] = M[0] + X[0]
        out[t, 1] = M[1] + X[1]
    return np.clip(out, 0.1, 5000.0)
