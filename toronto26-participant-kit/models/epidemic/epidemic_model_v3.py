"""Epidemic gray-box model (round-3 "v3" module, copied from epidemic_model_v2.py).
Round-3 changes vs v2: (1) the fatigue memory F is driven by closure only when mix_m1 = 1 (R6 verdict: a
120-tick mask-only hold keeps its full effect; v3 fits fix mix_m1 = 1); (2) dsh (share of closed-school child
contacts moved into the household/proportional-mixing term) may exceed 1 (transform 'pos', capped at 5), so
closure can raise elderly exposure and beds more than a 1:1 displacement (v2 open issue: dsh pinned at 1);
(3) optional closure-slowed discharges (staff absent for childcare): dis_t = dis / (1 + kd * cl), kd >= 0 capped
at 5 (kd = 0 is v2). A fit that fixes dsh = 1 and kd = 0 is exactly v2 (checked on final_v2: identical scores).
Everything else is v2. The v2 docstring follows.

Epidemic gray-box model (round-2 "v2" module; the docstring below describes the v1 base).
Round-2 changes: doses weighted (1, 1, pe) over the non-infected of each group (only S takes effect);
fatigue scales the mask effect by fmask_m1 (v1 = 1); optional bed-load clinic throttle kH (v1 = 0).

Epidemic gray-box model v2: three-age-group SEIRS (children / adults / elderly) with vaccination, a hospital
referral queue with a fixed bed capacity, an importation floor and three pluggable history mechanisms
(m1 behaviour, m2 developing immunity, m3 postponed gatherings).

v1 (single population, kept in greybox/epidemic_model_single.py) could not fit the first wave and the
restricted floor/plateau of Run 2 at once (review G1). v2 answers the review:
  G1  age structure: closure removes child-child school contacts and moves part of them into households
      (child activity in the proportional-mixing term rises by dsh * closure); each group has its own
      severity (replaces the data-driven hc of v1).
  G2  the transmission scale is parameterised directly (log transform) and S0 starts in the interior, so the
      high-R0 / low-S0 regime (endemic level insensitive to restrictions) is reachable.
  G3  importation: new infections += eps * susceptible, so cases never die out.
  Hcap is FIXED at the observed 155.2 and the queue abandonment rate has a floor of 0.005.
  G5  clinic throttling is driven by the waiting list Q (only > 0 at the cap): thr = 1 / (1 + kappa Q / Hcap).
  G4  m1 has a risk-driven term: contacts * exp(-gR * Hm / Hcap), Hm = fading memory of hospital load.

Per tick (fractions of a population of 1; groups g = 0 child, 1 adult, 2 elderly, shares NPOP):
  closure lag   cl <- cl + a_c (u_c - cl);  effective restriction  ce = cl * fat, me = u_m * fat
  multiplier    G = (1 - wm me) (1 - wc ce) exp(-gL F) exp(-gR Hm/Hcap) (1 + g3 (1 - rho3) B)
  activity      act = (a0 (1 + dsh ce), 1, a2)
  force         lam_g = bh G act_g sum_j act_j I_j / sum_j act_j n_j  +  [g = 0] bs (1 - ce) G I_0 / n_0
  infection     new_g = (lam_g + eps) (S_g + W_g); onset_g = sigE E_g; rec = gam I; waning = omega R
  vaccination   doses = 0.003 u_v ev thr, split over groups in proportion to S_g; m2: S -> W -> R at a_m2
  cases         daily_cases = K sum_g onset_g
  hospital      P <- P + a_h (sum_g sev_g K onset_g - P); Q += h P; admissions = min(Q, Hcap - H (1 - dis))
                H <- H (1 - dis) + adm; Q <- (Q - adm)(1 - qab)
  memories      m1: F <- F + a_m1 (mix1 cl + (1 - mix1) u_m - F);  Hm <- Hm + aR (H - Hm)
                m3: B <- B + ain rho3 (1 - B) - aout (1 - rho3) B,  rho3 = mix3 u_c + (1 - mix3) u_m
Reset convention: infected age mix proportional to n_g act_g; E0 = c0/(K sigE), I = rI E; S_g = s0 n_g;
W = Q = F = B = cl = 0; Hm = H0; P0 = fp c0; H0 = initial reading.
"""
import math
import numpy as np

OBSERVABLES = ('daily_cases', 'hospital_load')
CONTROLS = ('school_closure', 'mask_mandate', 'vaccination_rate')
RECOVERY = {'school_closure': 0.0, 'mask_mandate': 0.0, 'vaccination_rate': 0.0}
PULSE = {'school_closure': 1.0, 'mask_mandate': 1.0, 'vaccination_rate': 0.003}
UNITS = {'daily_cases': 'log', 'hospital_load': 'log'}
NOISE = {'daily_cases': 0.01, 'hospital_load': 0.01}   # residual scale (true noise ~0.3%; misfit dominates)
CLAMP = {'daily_cases': [0.01, 20000.0], 'hospital_load': [0.01, 2000.0]}
NPOP = (0.2, 0.6, 0.2)
FIXED = ('Hcap',)

SPEC = {
    # epidemic core
    'bh': (0.9, 'pos'), 'bs': (0.4, 'pos'), 'a0': (1.3, 'pos'), 'a2': (0.6, 'pos'), 'dsh': (1.0, 'pos'),
    'sigE': (0.35, 'unit'), 'gam': (0.25, 'unit'), 'omega': (0.01, 'unit'), 'K': (15000.0, 'pos'),
    's0': (0.45, 'unit'), 'rI': (1.2, 'pos'), 'eps': (2e-5, 'pos'),
    # controls
    'wm': (0.3, 'unit'), 'wc': (0.05, 'unit'), 'a_c': (0.15, 'unit'), 'ev': (0.8, 'unit'), 'kappa': (0.5, 'pos'),
    # v2: elderly-priority vaccination weight (v1 = 1), bed-load clinic throttle (v1 = 0)
    'pe': (6.0, 'pos'), 'kH': (1e-6, 'pos'),
    # hospital
    'h': (0.05, 'pos'), 'sev0': (0.3, 'unit'), 'sev2': (3.0, 'pos'), 'a_h': (0.15, 'unit'), 'dis': (0.07, 'unit'),
    'Hcap': (155.2, 'pos'), 'qab': (0.02, 'unit'), 'fp': (0.05, 'unit'), 'kd': (0.05, 'pos'),
    # m1 behaviour (fatigue gF, lingering caution gL, risk response gR)
    'a_m1': (0.03, 'unit'), 'gF_m1': (0.2, 'unit'), 'gL_m1': (0.05, 'pos'), 'mix_m1': (0.5, 'unit'),
    'gR_m1': (0.2, 'pos'), 'aR_m1': (0.05, 'unit'), 'fmask_m1': (0.5, 'unit'),
    # m2 developing immunity
    'a_m2': (0.1, 'unit'),
    # m3 postponed gatherings
    'ain_m3': (0.03, 'unit'), 'aout_m3': (0.1, 'unit'), 'g_m3': (0.2, 'pos'), 'mix_m3': (0.5, 'unit'),
}
MODULES = {
    'm1': (['a_m1', 'gF_m1', 'gL_m1', 'mix_m1', 'gR_m1', 'aR_m1', 'fmask_m1'], {'gF_m1': 0.0, 'gL_m1': 0.0, 'gR_m1': 0.0}),
    'kH': (['kH'], {'kH': 0.0}),
    'm2': (['a_m2'], {'a_m2': 1.0}),
    'm3': (['ain_m3', 'aout_m3', 'g_m3', 'mix_m3'], {'g_m3': 0.0}),
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


def simulate(p, initial, actions):
    T = len(actions)
    if T == 0:
        return np.zeros((0, 2))
    n0, n1, n2 = NPOP
    bh, bs, a0, a2, dsh = min(p['bh'], 20.0), min(p['bs'], 20.0), min(p['a0'], 10.0), min(p['a2'], 10.0), min(p['dsh'], 5.0)
    sigE, gam, om, K, rI = p['sigE'], p['gam'], p['omega'], p['K'], min(p['rI'], 50.0)
    eps = min(p['eps'], 0.01)
    wm, wc, a_c, ev, kap = p['wm'], p['wc'], p['a_c'], p['ev'], min(p['kappa'], 1e3)
    h, sev0, sev2, a_h, dis, Hcap = p['h'], p['sev0'], min(p['sev2'], 100.0), p['a_h'], p['dis'], p['Hcap']
    qab = max(p['qab'], 0.005)
    kd = min(p.get('kd', 0.0), 5.0)
    a1, gF, gL, mix1 = p['a_m1'], p['gF_m1'], min(p['gL_m1'], 50.0), p['mix_m1']
    gR, aR = min(p['gR_m1'], 50.0), p['aR_m1']
    fmask = p.get('fmask_m1', 1.0)
    pe, kH = min(p.get('pe', 1.0), 200.0), min(p.get('kH', 0.0), 50.0)
    a2m = p['a_m2']
    ain, aout, g3, mix3 = p['ain_m3'], p['aout_m3'], min(p['g_m3'], 50.0), p['mix_m3']
    c0 = float(initial['daily_cases'])
    c0 = min(max(c0 if math.isfinite(c0) else 150.0, 1.0), 5000.0)
    h0 = float(initial['hospital_load'])
    h0 = min(max(h0 if math.isfinite(h0) else 40.0, 0.0), 2000.0)
    npop = (n0, n1, n2)
    act0 = (a0, 1.0, a2)
    wsum = n0 * a0 + n1 + n2 * a2
    E0 = c0 / (K * sigE)
    S, E, I, R, W = [0.0] * 3, [0.0] * 3, [0.0] * 3, [0.0] * 3, [0.0] * 3
    s0 = p['s0']
    for g in range(3):
        mixg = npop[g] * act0[g] / wsum
        E[g] = min(E0 * mixg, 0.3 * npop[g])
        I[g] = min(rI * E[g], 0.3 * npop[g])
        S[g] = min(s0 * npop[g], npop[g] - E[g] - I[g])
        R[g] = max(npop[g] - S[g] - E[g] - I[g], 0.0)
    sev = (sev0, 1.0, sev2)
    P = p['fp'] * c0
    Q, H, Hm = 0.0, h0, h0
    cl = F = B = 0.0
    out = np.empty((T, 2))
    lam = [0.0, 0.0, 0.0]
    for t in range(T):
        uc, um, uv = actions[t]
        cl += a_c * (uc - cl)
        fat = 1.0 - gF * F
        ce, me = cl * fat, um * (1.0 - fmask * gF * F)
        G = (1.0 - wm * me) * (1.0 - wc * ce)
        if gL:
            G *= math.exp(-min(gL * F, 50.0))
        if gR:
            G *= math.exp(-min(gR * Hm / Hcap, 50.0))
        rho3 = mix3 * uc + (1.0 - mix3) * um
        if g3:
            G *= 1.0 + g3 * (1.0 - rho3) * B
        G = max(G, 0.0)
        ac0 = a0 * (1.0 + dsh * ce)
        den = n0 * ac0 + n1 + n2 * a2
        mixI = (ac0 * I[0] + I[1] + a2 * I[2]) / den
        hb = bh * G * mixI
        lam[0] = hb * ac0 + bs * max(1.0 - ce, 0.0) * G * I[0] / n0
        lam[1] = hb
        lam[2] = hb * a2
        thr = 1.0 / (1.0 + kap * Q / Hcap + kH * H / Hcap)
        # doses are offered to the non-infected of each group with weight (1, 1, pe); only S takes effect
        nonI0, nonI1, nonI2 = S[0] + W[0] + R[0], S[1] + W[1] + R[1], S[2] + W[2] + R[2]
        wtot = nonI0 + nonI1 + pe * nonI2
        dose_rate = 0.003 * uv * ev * thr / wtot if wtot > 1e-12 else 0.0
        onset_tot = 0.0
        sev_cases = 0.0
        for g in range(3):
            sus = S[g] + W[g]
            new = min((lam[g] + eps) * sus, 0.9 * sus)
            newS = new * S[g] / sus if sus > 0 else 0.0
            newW = new - newS
            onset = sigE * E[g]
            rec = gam * I[g]
            wane = om * R[g]
            doses = min(dose_rate * (pe if g == 2 else 1.0) * S[g], 0.9 * max(S[g] - newS, 0.0))
            dev = a2m * W[g]
            S[g] = max(S[g] - newS - doses + wane, 0.0)
            W[g] = max(W[g] - newW + doses - dev, 0.0)
            E[g] = max(E[g] + new - onset, 0.0)
            I[g] = max(I[g] + onset - rec, 0.0)
            R[g] = max(R[g] + rec + dev - wane, 0.0)
            onset_tot += onset
            sev_cases += sev[g] * onset
        cases = K * onset_tot
        P += a_h * (K * sev_cases - P)
        Q += h * P
        dis_t = dis / (1.0 + kd * cl)
        room = max(Hcap - H * (1.0 - dis_t), 0.0)
        adm = min(Q, room)
        H = H * (1.0 - dis_t) + adm
        Q = min((Q - adm) * (1.0 - qab), 1e6)
        F += a1 * ((mix1 * cl + (1.0 - mix1) * um) - F)
        Hm += aR * (H - Hm)
        B += ain * rho3 * (1.0 - B) - aout * (1.0 - rho3) * B
        B = min(max(B, 0.0), 1.0)
        out[t, 0] = min(max(cases, CLAMP['daily_cases'][0]), CLAMP['daily_cases'][1])
        out[t, 1] = min(max(H, CLAMP['hospital_load'][0]), CLAMP['hospital_load'][1])
    return out
