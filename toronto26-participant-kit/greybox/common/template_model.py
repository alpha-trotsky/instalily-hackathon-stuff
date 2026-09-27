"""TEMPLATE gray-box model: first-order relaxation + delay stages + pluggable mechanism memories.

COPY this file to greybox/<system>_model.py and edit the "SYSTEM DESCRIPTION" block. Everything below
it is generic and loops over OBSERVABLES / CONTROLS / MEMORIES, so most systems need no code changes;
add hand-written structure (couplings, saturations, pipelines) in `simulate` only when a backtest needs it.
Uses only math/numpy/scipy (it is copied into the submission folder). Interface: see greybox/common/fit.py.

Model, per tick (all observables update simultaneously from the previous state):
  controls    u_j = (value - RECOVERY_j) / (PULSE_j - RECOVERY_j)       (0 = recovery, 1 = pulse)
  delay       DELAY[c] first-order lag stages, q <- q + a_<c> (input - q), starting EMPTY (= recovery);
              the last stage is the effective control ue_j.
  units       y_i is log(obs) for UNITS 'log', obs for 'linear'. S_i = 1 (log) or LEVEL_i (linear), so
              every effect coefficient is relative (w = -0.2 means "-20% of the level").
  target      T_i = c_i + S_i * [ G_i * sum_j w_ij ue_j  + sum x_ijk ue_j ue_k        ('inter' module)
                                  + sum_m g_mi M_m   (mode 'target' memories)
                                  + lam_i z ]                                          ('reset' module)
              G_i = max(0, 1 + sum g_mi M_m) over mode 'gain' memories (they scale control effects).
  rate        k_i = sigmoid(logit(k_i) + sum_j kr_ij ue_j ('krate' module) + sum g_mi M_m (mode 'rate'))
  update      y_i <- clip(y_i + k_i (T_i - y_i)),   z <- (1 - a_z) z   (reset transient, z0 = 1)
  memories    M_m <- M_m + a_m (D_m - M_m), after the outputs moved, with a bounded driver D_m:
                'control' ue of a control         'level'  (y_src - c_src) / S_src
                'rate'    dy_src / S_src          'absrate' |dy| / S    'rise' max(dy, 0) / S
                'fall'    max(-dy, 0) / S         (all divided by `scale`, then clipped to +-DRIVER_CAP)
              'asym': True uses a_m_up when D > M (build) and a_m_dn when D < M (fade), e.g. a funding
              lock that locks fast and releases slowly.
Stability by construction: every rate is a sigmoid in (0, 1), memories fade with bounded drivers, states
are clipped to CLAMP. Gains of feedback memories (source observable among its own targets) use the
capped transform 'sgain' (|g| <= GAIN_MAX); the stability gate (gates.py stability) is still required.

Modules (fit with e.g. --modules m1,m2,reset,inter): every key of MEMORIES, plus 'reset', 'inter', 'krate'.
Base parameters (always fitted): c_<obs>, k_<obs>, w_<obs>_<ctrl>, a_<ctrl> for delayed controls.
"""
import math
import numpy as np
from scipy.signal import lfilter

# =============================================================== SYSTEM DESCRIPTION (EDIT THIS BLOCK)
# The values below describe market as a worked example.
OBSERVABLES = ('price', 'volume', 'depth')              # simulate() output column order
CONTROLS = ('interest_rate', 'transaction_tax')         # normalize() output order
RECOVERY = {'interest_rate': 0.0, 'transaction_tax': 0.0}   # brief "Reference recovery action"
PULSE = {'interest_rate': 0.1, 'transaction_tax': 0.05}     # brief "Reference pulse action"
UNITS = {'price': 'log', 'volume': 'log', 'depth': 'linear'}  # from the on/off symmetry test
NOISE = {'price': 0.004, 'volume': 0.004, 'depth': 0.3}  # sigma in UNITS (log: relative); fit residual scale
LEVEL = {'price': 93.0, 'volume': 1.8, 'depth': 91.0}    # settled level at recovery: start value and scale
CLAMP = {'price': [1.0, 2000.0], 'volume': [1e-3, 500.0], 'depth': [0.0, 2000.0]}  # physical output range
DELAY = {'interest_rate': 2, 'transaction_tax': 0}       # first-order lag stages per control
EFFECTS = None   # optional {obs: [controls]} limiting direct control effects; None = every pair
MEMORIES = {     # mechanism modules, written from the theses BEFORE fitting
    'm1': {'driver': 'control', 'source': 'interest_rate', 'targets': ('price',), 'mode': 'target',
           'asym': True, 'a': 0.05},
    'm2': {'driver': 'fall', 'source': 'price', 'targets': ('depth',), 'mode': 'target', 'scale': 0.01, 'a': 0.05},
    'm3': {'driver': 'rate', 'source': 'price', 'targets': ('price',), 'mode': 'target', 'scale': 0.01, 'a': 0.1},
    # couplings between outputs found in the behaviour catalogue are modules too (keep them always on):
    'vol_speed': {'driver': 'absrate', 'source': 'price', 'targets': ('volume',), 'scale': 0.01, 'a': 0.3},
    'withdraw': {'driver': 'fall', 'source': 'depth', 'targets': ('price',), 'scale': 0.01, 'a': 0.03},
}
# =============================================================== GENERIC PART
GAIN_MAX = 0.9
DRIVER_CAP = 10.0
RATE_DRIVERS = ('rate', 'absrate', 'rise', 'fall')


def _scale(obs):
    return 1.0 if UNITS[obs] == 'log' else max(abs(LEVEL[obs]), 1e-9)


def _unit_value(obs, value):
    return math.log(max(value, 1e-12)) if UNITS[obs] == 'log' else value


def _build_spec():
    spec, modules = {}, {}
    for o in OBSERVABLES:
        spec[f'c_{o}'] = (_unit_value(o, LEVEL[o]), 'free')
        spec[f'k_{o}'] = (0.1, 'unit')
        for c in (EFFECTS.get(o, CONTROLS) if EFFECTS else CONTROLS):
            spec[f'w_{o}_{c}'] = (0.0, 'free')
    for c in CONTROLS:
        if DELAY.get(c, 0):
            spec[f'a_{c}'] = (0.2, 'unit')
    reset = ['a_z'] + [f'lam_{o}' for o in OBSERVABLES]
    spec['a_z'] = (0.1, 'unit')
    spec.update({f'lam_{o}': (0.0, 'free') for o in OBSERVABLES})
    modules['reset'] = (reset, {f'lam_{o}': 0.0 for o in OBSERVABLES})
    pairs = [(a, b) for i, a in enumerate(CONTROLS) for b in CONTROLS[i + 1:]]
    inter = [f'x_{o}_{a}_{b}' for o in OBSERVABLES for a, b in pairs]
    spec.update({n: (0.0, 'free') for n in inter})
    modules['inter'] = (inter, {n: 0.0 for n in inter})
    krate = [f'kr_{o}_{c}' for o in OBSERVABLES for c in CONTROLS]
    spec.update({n: (0.0, 'free') for n in krate})
    modules['krate'] = (krate, {n: 0.0 for n in krate})
    for m, cfg in MEMORIES.items():
        rates = [f'a_{m}_up', f'a_{m}_dn'] if cfg.get('asym') else [f'a_{m}']
        for r in rates:
            spec[r] = (cfg.get('a', 0.05), 'unit')
        feedback = cfg['driver'] in RATE_DRIVERS + ('level',) and cfg['source'] in cfg['targets']
        gains = [f'g_{m}_{o}' for o in cfg['targets']]
        for g in gains:
            spec[g] = (cfg.get('g', 0.05), 'sgain' if feedback else 'free')
        modules[m] = (rates + gains, {g: 0.0 for g in gains})
    return spec, modules


SPEC, MODULES = _build_spec()


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
    if kind == 'sgain':
        return GAIN_MAX * math.tanh(raw)
    if kind == 'pos':
        return math.exp(min(raw, 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'unit':
        return _logit(value)
    if kind == 'sgain':
        return math.atanh(min(max(value / GAIN_MAX, -0.999999), 0.999999))
    if kind == 'pos':
        return math.log(max(value, 1e-300))
    return value


def normalize(action, bounds):
    """Physical action dict -> tuple of u in CONTROLS order (clipped to bounds first)."""
    out = []
    for c in CONTROLS:
        lo, hi = bounds.get(c, (min(RECOVERY[c], PULSE[c]), max(RECOVERY[c], PULSE[c])))
        v = min(max(float(action[c]), lo), hi)
        span = PULSE[c] - RECOVERY[c]
        out.append((v - RECOVERY[c]) / span if abs(span) > 1e-12 else v)
    return tuple(out)


def simulate(p, initial, actions):
    """Roll the model from a (noisy) initial reading; returns a (T, n_obs) array of natural values.

    State-independent parts (delay stages, control effects, reset term, control-dependent rates) are
    computed vectorized up front; only the state recursion runs in the Python loop.
    """
    T, no = len(actions), len(OBSERVABLES)
    if T == 0:
        return np.zeros((0, no))
    U = np.asarray(actions, dtype=float).reshape(T, len(CONTROLS))
    for j, ct in enumerate(CONTROLS):                     # delay stages start empty (u = 0)
        a = p.get(f'a_{ct}', 1.0)
        for _ in range(DELAY.get(ct, 0)):
            U[:, j] = lfilter([a], [1.0, a - 1.0], U[:, j])
    S = np.array([_scale(o) for o in OBSERVABLES])
    W = np.array([[p.get(f'w_{o}_{ct}', 0.0) for ct in CONTROLS] for o in OBSERVABLES])
    eff = U @ W.T                                         # (T, no) direct control effects
    pairs = [(a, b) for a in range(len(CONTROLS)) for b in range(a + 1, len(CONTROLS))]
    if pairs:
        X = np.array([[p[f'x_{o}_{CONTROLS[a]}_{CONTROLS[b]}'] for a, b in pairs] for o in OBSERVABLES])
        if X.any():
            eff = eff + np.column_stack([U[:, a] * U[:, b] for a, b in pairs]) @ X.T
    z = (1.0 - p['a_z']) ** np.arange(T)
    lam = np.array([p[f'lam_{o}'] for o in OBSERVABLES])
    c = np.array([p[f'c_{o}'] for o in OBSERVABLES])
    k0 = np.array([_logit(p[f'k_{o}']) for o in OBSERVABLES])
    KR = np.array([[p[f'kr_{o}_{ct}'] for ct in CONTROLS] for o in OBSERVABLES])
    klogit = k0 + U @ KR.T                                # (T, no) control-dependent rate logits

    mems = []   # (driver, source index, scale, a_up, a_dn, mode, [(target index, gain)])
    for m, cfg in MEMORIES.items():
        a_up = p[f'a_{m}_up'] if cfg.get('asym') else p[f'a_{m}']
        a_dn = p[f'a_{m}_dn'] if cfg.get('asym') else a_up
        src = CONTROLS.index(cfg['source']) if cfg['driver'] == 'control' else OBSERVABLES.index(cfg['source'])
        gains = [(OBSERVABLES.index(o), p[f'g_{m}_{o}']) for o in cfg['targets']]
        if any(g != 0.0 for _, g in gains):
            mems.append((cfg['driver'], src, cfg.get('scale', 1.0), a_up, a_dn, cfg.get('mode', 'target'), gains))
    gain_mem = any(m[5] == 'gain' for m in mems)
    rate_mem = any(m[5] == 'rate' for m in mems)
    base = (c + S * (eff + np.outer(z, lam))).tolist()   # target without memory terms
    effS = (eff * S).tolist()
    kmat = (1.0 / (1.0 + np.exp(-np.clip(klogit, -60, 60)))).tolist()
    klog = klogit.tolist()
    Ul = U.tolist()
    lo = [_unit_value(o, CLAMP[o][0]) if UNITS[o] == 'log' else CLAMP[o][0] for o in OBSERVABLES]
    hi = [_unit_value(o, CLAMP[o][1]) if UNITS[o] == 'log' else CLAMP[o][1] for o in OBSERVABLES]
    Sl, cl = S.tolist(), c.tolist()
    M = [0.0] * len(mems)
    y = [min(max(_unit_value(o, float(initial[o])), lo[i]), hi[i]) for i, o in enumerate(OBSERVABLES)]
    rows = []
    for t in range(T):
        target, k = base[t][:], kmat[t]
        if mems:
            gain, rate = [1.0] * no, [0.0] * no
            for (_, _, _, _, _, mode, gains), mv in zip(mems, M):
                for i, g in gains:
                    if mode == 'target':
                        target[i] += Sl[i] * g * mv
                    elif mode == 'gain':
                        gain[i] += g * mv
                    else:
                        rate[i] += g * mv
            if gain_mem:
                target = [tg + (max(gm, 0.0) - 1.0) * e for tg, gm, e in zip(target, gain, effS[t])]
            if rate_mem:
                k = [1.0 / (1.0 + math.exp(-min(max(kl + r, -60.0), 60.0))) for kl, r in zip(klog[t], rate)]
        new = [yi + ki * (ti - yi) for yi, ki, ti in zip(y, k, target)]
        if not all(l <= v <= h for v, l, h in zip(new, lo, hi)):
            new = [l if v < l else h if v > h else v for v, l, h in zip(new, lo, hi)]
        for n_m, (drv, src, scale, a_up, a_dn, _, _) in enumerate(mems):
            if drv == 'control':
                d = Ul[t][src]
            elif drv == 'level':
                d = (new[src] - cl[src]) / Sl[src]
            else:
                dy = (new[src] - y[src]) / Sl[src]
                d = dy if drv == 'rate' else abs(dy) if drv == 'absrate' else max(dy, 0.0) if drv == 'rise' else max(-dy, 0.0)
            d = min(max(d / scale, -DRIVER_CAP), DRIVER_CAP)
            M[n_m] += (a_up if d > M[n_m] else a_dn) * (d - M[n_m])
        y = new
        rows.append(y)
    out = np.array(rows)
    for i, o in enumerate(OBSERVABLES):
        if UNITS[o] == 'log':
            out[:, i] = np.exp(out[:, i])
    return out
