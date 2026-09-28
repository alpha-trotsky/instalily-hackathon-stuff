"""Gray-box market simulator. Standard library only, so it can be copied into the submission folder.

All three observables are simulated in log space. Controls are normalized: r = rate/0.1, tau = tax/0.05.

  reset transient  z: starts at 1 and decays; shifts every target at the start of an episode
  price            pipeline-delayed target (orders: preparation -> execution), then relaxation
  M1 funding lock  F: locks quickly while the rate is on, releases slowly (settlement); lowers price
  tax transient    'hump': high-pass of tax on the price target (symmetric on/off)
  depth withdrawal 'withdraw': leaky memory of depth *falls* pushes the price target (one-sided)
  M2 risk capacity leaky memories of price falls and rises; lower depth
  M3 momentum      leaky memory of returns, fed back into price
  volume           relaxes toward base * (1 + b_up*rise + b_dn*fall) of the current price move
  depth            relaxes (in linear units) toward exp(c_d) * (1 + tax effect - capacity loss)
"""
import math

# name -> (initial value in natural units, transform)
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
}
# Parameters owned by each switchable module, and the gains that turn it off.
MODULES = {
    'm1': (['w_f', 'k_in', 'k_out'], {'w_f': 0.0}),
    'm2': (['a_c', 'm_up', 'm_dn'], {'m_up': 0.0, 'm_dn': 0.0}),
    'm3': (['a_m', 'g_m'], {'g_m': 0.0}),
    'hump': (['w_h', 'a_h'], {'w_h': 0.0}),
    'withdraw': (['w_w', 'a_w'], {'w_w': 0.0}),
}
GAIN_MAX = 0.9


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'gain':
        return GAIN_MAX * _sigmoid(raw)
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        return math.log(value / (1.0 - value))
    if kind == 'gain':
        return math.log(value / (GAIN_MAX - value))
    return value


def params_for(modules, fitted=None):
    """Full natural-unit parameter dict: SPEC defaults, disabled modules zeroed, fitted values on top."""
    params = {name: value for name, (value, _) in SPEC.items()}
    for module, (_, off) in MODULES.items():
        if module not in modules:
            params.update(off)
    params.update(fitted or {})
    return params


def free_names(modules):
    """Names fitted for a given module set: everything except parameters of disabled modules."""
    disabled = {name for module, (names, _) in MODULES.items() if module not in modules for name in names}
    return [name for name in SPEC if name not in disabled]


def _clip(x, low, high):
    return low if x < low else high if x > high else x


def simulate(p, initial, actions):
    """Roll the model from a noisy initial reading through normalized (r, tau) actions.

    Returns a list of (price, volume, depth) tuples, one per action.
    """
    lp = math.log(max(initial['price'], 1e-6))
    lv = math.log(max(initial['volume'], 1e-6))
    d = max(initial['depth'], 1e-6)
    q1 = q2 = lp            # order pipeline starts empty: pending orders sit at the current price
    z = 1.0                 # reset transient
    f = s_tau = 0.0         # M1 funding lock, slow tax filter
    c_up = c_dn = 0.0       # M2 capacity loss memories
    mom = 0.0               # M3 momentum
    wd = 0.0                # memory of depth withdrawals
    base_v = math.exp(p['c_v'])
    out = []
    for r, tau in actions:
        f += p['k_in'] * max(r - f, 0.0) - p['k_out'] * max(f - r, 0.0)
        s_tau += p['a_h'] * (tau - s_tau)
        target = (p['c_p'] - p['w_r'] * r - p['w_f'] * f + p['w_tau'] * tau
                  + p['w_h'] * (tau - s_tau) + p['w_w'] * wd + p['lam_p'] * z)
        q1 += p['a1'] * (target - q1)
        q2 += p['a2'] * (q1 - q2)
        dp = p['k_p'] * (q2 - lp) + p['g_m'] * mom
        lp = _clip(lp + dp, -2.0, 12.0)
        mom += p['a_m'] * (dp - mom)
        rise, fall = max(dp, 0.0), max(-dp, 0.0)
        c_up += p['a_c'] * (rise - c_up)
        c_dn += p['a_c'] * (fall - c_dn)
        d_target = math.exp(p['c_d']) * (1.0 + p['w_dtau'] * tau - p['m_up'] * c_up - p['m_dn'] * c_dn
                                         + p['lam_d'] * z)
        d_new = _clip(d + p['k_d'] * (d_target - d), 1e-3, 1e5)
        wd += p['a_w'] * (max(d - d_new, 0.0) / d - wd)
        d = d_new
        v_target = math.log(max(base_v * (1.0 + p['b_up'] * rise + p['b_dn'] * fall), 1e-6)) + p['lam_v'] * z
        lv = _clip(lv + p['k_v'] * (v_target - lv), -8.0, 12.0)
        z *= 1.0 - p['a_z']
        out.append((math.exp(lp), math.exp(lv), d))
    return out


def normalize(action, bounds):
    return tuple(action[name] / bounds[name][1] for name in ('interest_rate', 'transaction_tax'))
