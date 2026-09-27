"""Epidemic gray-box model: single-population SEIRS with vaccination, a hospital referral queue with a hard
bed capacity, and three pluggable history mechanisms (m1 behaviour, m2 developing immunity, m3 postponed
gatherings). Written from the pre-registered theses in plans/epidemic-plan.md BEFORE fitting.

Why not the relaxation template: Run 1 shows epidemic waves (cases 114 -> 500 -> 45 -> 207 -> 88 ...) that
are driven by a hidden susceptible pool, and a hard ceiling on hospital_load (~155 beds) with a waiting list.
A relaxation-to-target model cannot produce either.

Per tick (fractions of a population of 1; u = normalized controls, 0 = recovery, 1 = pulse):
  closure lag     cl <- cl + a_c (u_c - cl)                     (closure acts gradually: no jump in R1)
  transmission    beta = beta0 * (1 - wm u_m fat) * (1 - wc cl fat) * exp(-gL F) * (1 + g3 (1 - rho3) B)
                  fat = 1 - gF F   (m1 fatigue erodes the restriction effect; gL = lingering caution)
  infection       new = beta (S + W) I,  onset = sigE E,  recovery = gam I,  waning = omega R
  vaccination     doses = 0.003-equivalent u_v * ev * thr * S / (S + W + R),  thr = 1 / (1 + kappa H / Hcap)
                  m2 on:  S -> W (still susceptible) -> R at rate a_m2;   m2 off: S -> R directly (a_m2 = 1)
  cases           daily_cases = K * onset
  hospital        P <- P + a_h (cases - P)   (severity/referral lag), referrals = h (1 + hc cl) P into queue Q
                  (hc: closure moves contacts into households -> more severe age mix; catalogue B4);
                  admissions = min(Q, Hcap - H (1 - dis)); H <- H (1 - dis) + adm; Q <- (Q - adm)(1 - qab)
  memories        m1: F <- F + a_m1 (rho1 - F),  rho1 = mix1 cl + (1 - mix1) u_m     (driver: restriction)
                  m3: B <- B + a_in rho3 (1 - B) - a_out (1 - rho3) B, rho3 = mix3 u_c + (1 - mix3) u_m;
                      the release term (1 - rho3) B boosts contacts after restrictions lift (one-sided).
Reset convention: E0 = c0 / (K sigE), I0 = rI E0, S0 fitted, W = Q = F = B = cl = 0, P0 = fp * c0, H0 = h0.
"""
import math
import numpy as np

OBSERVABLES = ('daily_cases', 'hospital_load')
CONTROLS = ('school_closure', 'mask_mandate', 'vaccination_rate')
RECOVERY = {'school_closure': 0.0, 'mask_mandate': 0.0, 'vaccination_rate': 0.0}
PULSE = {'school_closure': 1.0, 'mask_mandate': 1.0, 'vaccination_rate': 0.003}
UNITS = {'daily_cases': 'log', 'hospital_load': 'log'}
NOISE = {'daily_cases': 0.01, 'hospital_load': 0.01}   # residual scale (true noise ~0.2%; misfit dominates)
CLAMP = {'daily_cases': [0.01, 20000.0], 'hospital_load': [0.01, 2000.0]}

SPEC = {
    # epidemic core
    'beta0': (0.55, 'pos'), 'sigE': (0.35, 'unit'), 'gam': (0.25, 'unit'), 'omega': (0.004, 'unit'),
    'K': (40000.0, 'pos'), 'S0': (0.55, 'unit'), 'rI': (1.2, 'pos'),
    # controls
    'wm': (0.3, 'unit'), 'wc': (0.2, 'unit'), 'a_c': (0.1, 'unit'), 'ev': (0.8, 'unit'), 'kappa': (0.5, 'pos'),
    # hospital
    'h': (0.035, 'pos'), 'a_h': (0.2, 'unit'), 'dis': (0.06, 'unit'), 'Hcap': (155.3, 'pos'),
    'qab': (0.02, 'unit'), 'fp': (0.1, 'unit'), 'hc': (0.0, 'free'),
    # m1 behaviour
    'a_m1': (0.03, 'unit'), 'gF_m1': (0.2, 'unit'), 'gL_m1': (0.05, 'pos'), 'mix_m1': (0.5, 'unit'),
    # m2 developing immunity
    'a_m2': (0.1, 'unit'),
    # m3 postponed gatherings
    'ain_m3': (0.03, 'unit'), 'aout_m3': (0.1, 'unit'), 'g_m3': (0.2, 'pos'), 'mix_m3': (0.5, 'unit'),
}
MODULES = {
    'm1': (['a_m1', 'gF_m1', 'gL_m1', 'mix_m1'], {'gF_m1': 0.0, 'gL_m1': 0.0}),
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
    beta0, sigE, gam, om = p['beta0'], p['sigE'], p['gam'], p['omega']
    K, rI = p['K'], p['rI']
    wm, wc, a_c, ev, kap = p['wm'], p['wc'], p['a_c'], p['ev'], p['kappa']
    h, a_h, dis, Hcap, qab = p['h'], p['a_h'], p['dis'], p['Hcap'], p['qab']
    hc = p.get('hc', 0.0)
    a1, gF, gL, mix1 = p['a_m1'], p['gF_m1'], p['gL_m1'], p['mix_m1']
    a2 = p['a_m2']
    ain, aout, g3, mix3 = p['ain_m3'], p['aout_m3'], p['g_m3'], p['mix_m3']
    c0 = float(initial['daily_cases'])
    c0 = min(max(c0 if math.isfinite(c0) else 150.0, 1.0), 5000.0)
    h0 = float(initial['hospital_load'])
    h0 = min(max(h0 if math.isfinite(h0) else 40.0, 0.0), 2000.0)
    E = c0 / (K * sigE)
    I = rI * E
    S = p['S0']
    tot = S + E + I
    if tot > 0.999:
        S, E, I = S / tot * 0.999, E / tot * 0.999, I / tot * 0.999
    R = max(1.0 - S - E - I, 0.0)
    W = 0.0
    P = p['fp'] * c0
    Q, H = 0.0, h0
    cl = F = B = 0.0
    out = np.empty((T, 2))
    for t in range(T):
        uc, um, uv = actions[t]
        cl += a_c * (uc - cl)
        fat = 1.0 - gF * F
        mult = (1.0 - wm * um * fat) * (1.0 - wc * cl * fat)
        if gL:
            mult *= math.exp(-min(gL * F, 50.0))
        rho3 = mix3 * uc + (1.0 - mix3) * um
        if g3:
            mult *= 1.0 + g3 * (1.0 - rho3) * B
        beta = beta0 * max(mult, 0.0)
        sus = S + W
        new = min(beta * sus * I, 0.9 * sus)
        newS = new * S / sus if sus > 0 else 0.0
        newW = new - newS
        onset = sigE * E
        rec = gam * I
        wane = om * R
        thr = 1.0 / (1.0 + kap * H / Hcap)
        nonI = S + W + R
        doses = 0.003 * uv * ev * thr * (S / nonI if nonI > 1e-12 else 0.0)
        doses = min(doses, 0.9 * max(S - newS, 0.0))
        dev = a2 * W
        S = max(S - newS - doses + wane, 0.0)
        W = max(W - newW + doses - dev, 0.0)
        E = max(E + new - onset, 0.0)
        I = max(I + onset - rec, 0.0)
        R = max(R + rec + dev - wane, 0.0)
        cases = K * onset
        P += a_h * (cases - P)
        Q += h * max(1.0 + hc * cl, 0.0) * P
        room = max(Hcap - H * (1.0 - dis), 0.0)
        adm = min(Q, room)
        H = H * (1.0 - dis) + adm
        Q = (Q - adm) * (1.0 - qab)
        F += a1 * ((mix1 * cl + (1.0 - mix1) * um) - F)
        B += ain * rho3 * (1.0 - B) - aout * (1.0 - rho3) * B
        B = min(max(B, 0.0), 1.0)
        out[t, 0] = min(max(cases, CLAMP['daily_cases'][0]), CLAMP['daily_cases'][1])
        out[t, 1] = min(max(H, CLAMP['hospital_load'][0]), CLAMP['hospital_load'][1])
    return out
