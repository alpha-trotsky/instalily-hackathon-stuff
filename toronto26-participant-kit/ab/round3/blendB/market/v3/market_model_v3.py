"""Gray-box market simulator, round 3 (v3 = v2 plus the round-3 modules rz, zdm, klin). Standard library only, so it can be copied into the submission folder.

Starts from v1 (greybox/market_model.py). All three observables are simulated in log space (depth in linear
units internally). Controls are normalized: r = rate/0.1, tau = tax/0.05.

v1 structure (unchanged unless a v2 module below is active):
  reset transient  z: starts at 1 and decays; shifts every target at the start of an episode
  price            pipeline-delayed target (orders: preparation -> execution), then relaxation
  M1 funding lock  F: locks quickly while the rate is on, releases slowly (settlement); lowers price
  depth withdrawal 'withdraw': leaky memory of depth *falls* pushes the price target (one-sided)
  M2 risk capacity leaky memories of price falls and rises; lower depth
  volume           relaxes toward base * (1 + b_up*rise + b_dn*fall) of the current price move
  depth            relaxes (linear units) toward exp(c_d) * tax_factor * capacity

v2 modules (round-2 diagnosis, plans/market-round2-diagnosis.md section 5):
  conv   rate enters as r**p_r (convex rate -> price map, B18)
  gate   M1 release is gated by tax: k_out * exp(-g_tau*tau) (settlement needs trading, B15)
  dmap   depth tax factor 1/(1 + w_dh*tau) instead of (1 + w_dtau*tau) (concave, B17)
  m2mult M2 capacity loss is multiplicative on the tax-reduced depth, floored (B20)
  inv    reset inventory I (starts at 1, unwinds by trading at k_I*(1-tau)) under funding pressure drains
         dealer capital K in (0, 1]: dK = b_K*(1-K) - a_K*r*I*K. K scales depth, slows price discovery
         (k_p*K**n_K) and forced selling r*I raises volume (B11, B12, B13, B16 from reset)
  jx     joint price interaction -w_x * r**4 * tau (B21)
  vjx    slow volume decline under joint control: s += a_sv*(r*tau - s); log volume target -w_sv*s (B16)
  vfl    volume from partial-tax settlement flow: log(1 + b_fl*4*tau*(1-tau)*max(F-r,0)) (B16, C 375-500)

v3 modules (round-3 run D: tax 1 from reset for 80 ticks, then joint 1 for 120; plans/round3-findings.md):
  rz     the reset price-target shift lam_p*z scales with the initial price deviation (lp0 - c_p)/0.15, so a
         reset that starts near equilibrium (D: 95) has no dip (v2 dipped to 90); A-C (lp0 - c_p ~ 0.15) unchanged
  zdm    the reset depth bump is multiplicative on the tax/capital-reduced level (1 + lam_d*z) instead of additive,
         so tax from reset settles depth quickly (D 0-60)
  klin   reset-inventory capital drain reshaped: the funding pressure acts through a lagged rate rL (a_L; D's drain
         starts ~10-20 ticks after the rate), the drain is ~linear in K (a_K*rL*I*K/(K+K_h); B and D both lose
         ~0.005 of K per tick at every K down to 0.3), and the capital refill needs settlement, so it is gated by
         tax: b_K*(1-tau)**g_K*(1-K), g_K fixed at 1 (an exp(-g_K*tau) gate pinned g_K at its bound 12 and left
         K unrefilled for 4,000 ticks at tau 0.7-0.85, which no data supports). Tax 1: no refill, K_eff floors at K_min
  wx     the depth-withdrawal price push needs unwound reset inventory: w_w*(1-I)*wd. Tax from reset (D, B) gives
         no price hump, tax after trading (A 325, C 125) does
  tz     tax during the reset transient slows price discovery: k_p/(1 + b_z*tau*z) (B 0-60 blocked while K is
         still high; D's rate response 80 ticks later is not)
  kfl    the capital block on price discovery has a floor: k_p*(phi_K + (1-phi_K)*K**n_K); B and D keep falling
         slowly (~0.07/tick) at low K instead of freezing
  kmin   depth and the price block see K_eff = K_min + (1-K_min)*K, a bounded floor for 4,000-tick holds of tax 1
         + rate from reset (B stops at K ~ 0.3 still falling, so the floor is weakly identified)
"""
import math

SPEC = {
    'a_z': (0.05, 'unit'), 'lam_p': (0.0, 'free'), 'lam_v': (0.4, 'free'), 'lam_d': (0.1, 'free'),
    'c_p': (math.log(93.0), 'free'), 'k_p': (0.1, 'unit'), 'a1': (0.15, 'unit'), 'a2': (0.15, 'unit'),
    'w_r': (0.12, 'free'), 'w_tau': (0.012, 'free'),
    'w_h': (0.07, 'free'), 'a_h': (0.03, 'unit'),
    'w_w': (1.0, 'free'), 'a_w': (0.03, 'unit'),
    'w_f': (0.12, 'free'), 'k_in': (0.1, 'unit'), 'k_out': (0.02, 'unit'),
    'a_c': (0.05, 'unit'), 'm_up': (5.0, 'free'), 'm_dn': (10.0, 'free'),
    'a_m': (0.1, 'unit'), 'g_m': (0.1, 'gain'),
    'c_d': (math.log(91.0), 'free'), 'w_dtau': (-0.55, 'free'), 'k_d': (0.125, 'unit'),
    'c_v': (math.log(1.78), 'free'), 'k_v': (0.3, 'unit'), 'b_up': (90.0, 'free'), 'b_dn': (57.0, 'free'),
    # v2
    'p_r': (1.3, 'r:0.5:4'),
    'g_tau': (4.0, 'r:0:12'),
    'w_dh': (1.19, 'r:0:5'),
    'm2mult': (1.0, 'flag'),
    'a_K': (0.1, 'unit'), 'b_K': (0.03, 'unit'), 'k_I': (0.05, 'unit'), 'n_K': (1.0, 'r:0:8'), 'b_I': (5.0, 'r:0:400'),
    'w_x': (0.05, 'r:0:0.5'),
    'a_sv': (0.02, 'unit'), 'w_sv': (0.1, 'r:0:1'),
    'b_fl': (50.0, 'r:0:1000'),
    # v3
    'rz': (1.0, 'flag'), 'zdm': (1.0, 'flag'), 'klin': (1.0, 'flag'),
    'a_L': (0.1, 'unit'), 'K_h': (0.1, 'r:0.01:3'), 'g_K': (1.0, 'r:0:4'),
    'wx': (1.0, 'flag'), 'b_z': (2.0, 'r:0:30'),
    'phi_K': (0.05, 'unit'), 'K_min': (0.1, 'r:0:0.5'),
}
MODULES = {
    'm1': (['w_f', 'k_in', 'k_out'], {'w_f': 0.0}),
    'm2': (['a_c', 'm_up', 'm_dn'], {'m_up': 0.0, 'm_dn': 0.0}),
    'm3': (['a_m', 'g_m'], {'g_m': 0.0}),
    'hump': (['w_h', 'a_h'], {'w_h': 0.0}),
    'withdraw': (['w_w', 'a_w'], {'w_w': 0.0}),
    'conv': (['p_r'], {'p_r': 1.0}),
    'gate': (['g_tau'], {'g_tau': 0.0}),
    'dmap': (['w_dh'], {'w_dh': 0.0}),
    'm2mult': ([], {'m2mult': 0.0}),
    'inv': (['a_K', 'b_K', 'k_I', 'n_K', 'b_I'], {'a_K': 0.0, 'n_K': 0.0, 'b_I': 0.0}),
    'jx': (['w_x'], {'w_x': 0.0}),
    'vjx': (['a_sv', 'w_sv'], {'w_sv': 0.0}),
    'vfl': (['b_fl'], {'b_fl': 0.0}),
    'rz': ([], {'rz': 0.0}),
    'zdm': ([], {'zdm': 0.0}),
    'klin': (['a_L', 'K_h', 'g_K'], {'klin': 0.0}),
    'wx': ([], {'wx': 0.0}),
    'tz': (['b_z'], {'b_z': 0.0}),
    'kfl': (['phi_K'], {'phi_K': 0.0}),
    'kmin': (['K_min'], {'K_min': 0.0}),
}
FIXED = ('m2mult', 'rz', 'zdm', 'klin', 'wx', 'g_K')
OBSERVABLES = ('price', 'volume', 'depth')
UNITS = {'price': 'log', 'volume': 'log', 'depth': 'log'}
NOISE = {'price': 0.004, 'volume': 0.004, 'depth': 0.004}
GAIN_MAX = 0.9


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def _range(kind):
    _, lo, hi = kind.split(':')
    return float(lo), float(hi)


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'gain':
        return GAIN_MAX * _sigmoid(raw)
    if kind.startswith('r:'):
        lo, hi = _range(kind)
        return lo + (hi - lo) * _sigmoid(raw)
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        value = min(max(value, 1e-9), 1 - 1e-9)
        return math.log(value / (1.0 - value))
    if kind == 'gain':
        value = min(max(value, 1e-9), GAIN_MAX - 1e-9)
        return math.log(value / (GAIN_MAX - value))
    if kind.startswith('r:'):
        lo, hi = _range(kind)
        f = min(max((value - lo) / (hi - lo), 1e-9), 1 - 1e-9)
        return math.log(f / (1.0 - f))
    return value


def params_for(modules, fitted=None):
    """Full natural-unit parameter dict: SPEC defaults, fitted values on top, disabled modules switched off last."""
    params = {name: value for name, (value, _) in SPEC.items()}
    params.update(fitted or {})
    for module, (_, off) in MODULES.items():
        if module not in modules:
            params.update(off)
    if 'dmap' in modules:
        params['w_dtau'] = 0.0
    return params


def free_names(modules):
    disabled = {name for module, (names, _) in MODULES.items() if module not in modules for name in names}
    if 'dmap' in modules:
        disabled.add('w_dtau')
    return [name for name in SPEC if name not in disabled and name not in FIXED]


def _clip(x, low, high):
    return low if x < low else high if x > high else x


def simulate(p, initial, actions):
    """Roll the model from a noisy initial reading through normalized (r, tau) actions.

    Returns a list of (price, volume, depth) tuples, one per action.
    """
    lp = math.log(max(initial['price'], 1e-6))
    lv = math.log(max(initial['volume'], 1e-6))
    d = max(initial['depth'], 1e-6)
    q1 = q2 = lp
    z = 1.0
    f = s_tau = 0.0
    c_up = c_dn = 0.0
    mom = 0.0
    wd = 0.0
    inv, cap = 1.0, 1.0     # reset inventory, dealer capital
    s_v = 0.0               # joint-control volume memory
    base_v = math.exp(p['c_v'])
    base_d = math.exp(p['c_d'])
    p_r, g_tau, w_dh, w_x = p['p_r'], p['g_tau'], p['w_dh'], p['w_x']
    a_K, b_K, k_I, n_K, b_I = p['a_K'], p['b_K'], p['k_I'], p['n_K'], p['b_I']
    m2mult = p['m2mult'] > 0.5
    rz, zdm, klin, wx = p['rz'] > 0.5, p['zdm'] > 0.5, p['klin'] > 0.5, p['wx'] > 0.5
    a_L, K_h, g_K = p['a_L'], p['K_h'], p['g_K']
    r_lag = 0.0
    lam_p = p['lam_p'] * (lp - p['c_p']) / 0.15 if rz else p['lam_p']
    out = []
    for r, tau in actions:
        r = _clip(r, 0.0, 1.0)
        tau = _clip(tau, 0.0, 1.0)
        re = r ** p_r if r > 0.0 else 0.0
        k_out = p['k_out'] * math.exp(-g_tau * tau)
        f += p['k_in'] * max(re - f, 0.0) - k_out * max(f - re, 0.0)
        # reset inventory and dealer capital
        if klin:
            r_lag += a_L * (r - r_lag)
            drain = a_K * r_lag * inv
            cap = _clip(cap + b_K * (1.0 - tau) ** g_K * (1.0 - cap) - drain * cap / (cap + K_h), 1e-3, 1.0)
        else:
            drain = a_K * r * inv
            cap = _clip(cap + b_K * (1.0 - cap) - drain * cap, 1e-3, 1.0)
        inv -= k_I * (1.0 - tau) * inv
        s_tau += p['a_h'] * (tau - s_tau)
        target = (p['c_p'] - p['w_r'] * re - p['w_f'] * f + p['w_tau'] * tau - w_x * r ** 4 * tau
                  + p['w_h'] * (tau - s_tau) + p['w_w'] * (1.0 - inv if wx else 1.0) * wd + lam_p * z)
        q1 += p['a1'] * (target - q1)
        q2 += p['a2'] * (q1 - q2)
        k_eff = p['K_min'] + (1.0 - p['K_min']) * cap
        kp = (p['k_p'] * (p['phi_K'] + (1.0 - p['phi_K']) * (k_eff ** n_K if n_K > 0.0 else 1.0))
              / (1.0 + p['b_z'] * tau * z))
        dp = kp * (q2 - lp) + p['g_m'] * mom
        lp = _clip(lp + dp, -2.0, 12.0)
        mom += p['a_m'] * (dp - mom)
        rise, fall = max(dp, 0.0), max(-dp, 0.0)
        c_up += p['a_c'] * (rise - c_up)
        c_dn += p['a_c'] * (fall - c_dn)
        loss = p['m_up'] * c_up + p['m_dn'] * c_dn
        tax_factor = (1.0 + p['w_dtau'] * tau) / (1.0 + w_dh * tau)
        if m2mult:
            level = tax_factor * max(1.0 - loss, 0.05)
        else:
            level = tax_factor - loss
        if zdm:
            d_target = base_d * level * k_eff * (1.0 + p['lam_d'] * z)
        else:
            d_target = base_d * (level * k_eff + p['lam_d'] * z)
        d_new = _clip(d + p['k_d'] * (d_target - d), 1e-3, 1e5)
        wd += p['a_w'] * (max(d - d_new, 0.0) / d - wd)
        d = d_new
        s_v += p['a_sv'] * (r * tau - s_v)
        extra = 1.0 + p['b_fl'] * 4.0 * tau * (1.0 - tau) * max(f - re, 0.0) + b_I * drain
        v_target = (math.log(max(base_v * (1.0 + p['b_up'] * rise + p['b_dn'] * fall) * extra, 1e-6))
                    + p['lam_v'] * z - p['w_sv'] * s_v)
        lv = _clip(lv + p['k_v'] * (v_target - lv), -8.0, 12.0)
        z *= 1.0 - p['a_z']
        out.append((math.exp(lp), math.exp(lv), d))
    return out


def normalize(action, bounds):
    return tuple(action[name] / bounds[name][1] for name in ('interest_rate', 'transaction_tax'))
