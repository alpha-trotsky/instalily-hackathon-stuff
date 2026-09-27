"""Shared helpers for the gray-box tools: data loading, model loading, units, noise, scores, schedules.

Paths: every tool is meant to be run from the kit directory (`toronto26-participant-kit/`) as
`python -m greybox.common.<tool> ...`. Relative paths are resolved against the current directory.

Data files are written by `run_schedule.py`:
    {family, brief: {observables, interventions: {name: [lo, hi]}, brief: <text>, ...},
     runs: [{initial, actions: [dict], observations: [dict], segments: [{start_tick, segments}]}]}
A data argument may select runs with a suffix: `data/x/A.json:0,2` (0-based run indices).

Tick convention: observation index t (0-based) is the reading after action index t. The market plan's
"tick 1" is index 0. All CLI --start/--end values are 0-based slice indices [start, end).
"""
import importlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
import numpy as np

KIT = Path(__file__).resolve().parents[2]
DOCS = KIT / 'docs'
LOG_FLOOR = 1e-12
PENALTY = 1e4


# ----------------------------------------------------------------------------- model modules

def load_model(spec):
    """Import a model module from a dotted name (`greybox.market_model`) or a file path."""
    if spec.endswith('.py') or '/' in spec or '\\' in spec:
        path = Path(spec).resolve()
        name = '_gbmodel_' + path.stem
        if name in sys.modules:
            return sys.modules[name]
        module_spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[name] = module
        module_spec.loader.exec_module(module)
        module.__model_spec__ = spec
        return module
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
    module = importlib.import_module(spec)
    module.__model_spec__ = spec
    return module


def params_for(model, modules, fitted=None):
    """Natural-unit parameter dict: SPEC defaults, disabled modules switched off, `fitted` on top."""
    if hasattr(model, 'params_for'):
        return model.params_for(modules, fitted)
    params = {name: value for name, (value, _) in model.SPEC.items()}
    for module, (_, off) in model.MODULES.items():
        if module not in modules:
            params.update(off)
    params.update(fitted or {})
    return params


def free_names(model, modules, fixed=()):
    """Fitted parameter names: SPEC minus parameters owned by disabled modules minus `fixed`."""
    if hasattr(model, 'free_names'):
        names = model.free_names(modules)
    else:
        disabled = {n for m, (names, _) in model.MODULES.items() if m not in modules for n in names}
        names = [n for n in model.SPEC if n not in disabled]
    return [n for n in names if n not in set(fixed) | set(getattr(model, 'FIXED', ()))]


def observables(model, brief):
    return list(getattr(model, 'OBSERVABLES', None) or brief['observables'])


# ----------------------------------------------------------------------------- data

def split_data_arg(arg):
    """`path.json:0,2` -> (path, [0, 2]); plain path -> (path, None)."""
    match = re.match(r'^(.*\.json):([\d,]+)$', str(arg))
    if match:
        return match.group(1), [int(i) for i in match.group(2).split(',')]
    return str(arg), None


def load_file(path):
    return json.loads(Path(path).read_text())


def load_episodes(paths, names=None, model=None, min_len=1):
    """Flatten data files into episodes.

    Each episode: {source, run, initial, actions (raw dicts), obs (T x n array in `names` order),
    names, bounds, brief, segments, u (normalized actions if `model` given)}.
    """
    episodes = []
    for arg in paths:
        path, select = split_data_arg(arg)
        data = load_file(path)
        brief = data['brief']
        bounds = brief['interventions']
        cols = list(names) if names else (observables(model, brief) if model else list(brief['observables']))
        for index, run in enumerate(data['runs']):
            if select is not None and index not in select:
                continue
            n = min(len(run['actions']), len(run['observations']))
            if n < min_len:
                continue
            ep = {'source': path, 'run': index, 'initial': dict(run['initial']),
                  'actions': run['actions'][:n], 'names': cols, 'bounds': bounds, 'brief': brief,
                  'family': data.get('family'), 'segments': run.get('segments', []),
                  'obs': np.array([[float(o[c]) for c in cols] for o in run['observations'][:n]])}
            if model is not None:
                ep['u'] = [model.normalize(a, bounds) for a in ep['actions']]
            episodes.append(ep)
    return episodes


def rollout(model, params, ep, horizon=None):
    """Simulate one episode; returns a (T, n) float array (NaN-filled if the model raised)."""
    u = ep['u'] if horizon is None else ep['u'][:horizon]
    try:
        with np.errstate(all='ignore'):
            pred = np.asarray(model.simulate(params, ep['initial'], u), dtype=float)
        if pred.shape != (len(u), len(ep['names'])):
            raise ValueError(f'simulate returned shape {pred.shape}')
    except (OverflowError, ValueError, ZeroDivisionError, FloatingPointError, TypeError):
        pred = np.full((len(u), len(ep['names'])), np.nan)
    return pred


# ----------------------------------------------------------------------------- brief text

def _json_after(text, marker):
    match = re.search(re.escape(marker) + r'\s*(\{[^{}]*\})', text or '')
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def docs_for(system):
    path = DOCS / f'{system}.json'
    return load_file(path) if path.exists() else None


def brief_info(system=None, brief=None):
    """Bounds, recovery/pulse actions, initial ranges and forecast_context for a system.

    Uses docs/<system>.json when present, else the brief stored in a data file.
    """
    docs = docs_for(system) if system else None
    b = (docs or {}).get('brief') or brief or {}
    text = b.get('brief', '') if isinstance(b, dict) else ''
    doc_text = ' '.join(d.get('text', '') for d in b.get('documents', [])) if isinstance(b, dict) else ''
    bounds = {k: list(v) for k, v in b.get('interventions', {}).items()}
    recovery = _json_after(text, 'Reference recovery action:') or {k: v[0] for k, v in bounds.items()}
    pulse = _json_after(text, 'Reference pulse action:') or {k: v[1] for k, v in bounds.items()}
    context = b.get('forecast_context') or {'observables': b.get('observables'), 'intervention_bounds': bounds}
    return {'observables': list(b.get('observables', [])), 'bounds': bounds, 'recovery': recovery,
            'pulse': pulse, 'initial_ranges': _json_after(doc_text + ' ' + text, 'from these ranges:') or {},
            'context': context}


def normalized_controls(actions, recovery, pulse, bounds):
    """(T, m) array of u = (value - recovery) / (pulse - recovery); falls back to min-max if pulse == recovery."""
    names = list(bounds)
    out = np.zeros((len(actions), len(names)))
    for j, name in enumerate(names):
        lo, hi = bounds[name]
        rec, pul = recovery.get(name, lo), pulse.get(name, hi)
        if abs(pul - rec) < 1e-12:
            rec, pul = lo, hi
        out[:, j] = [(float(a[name]) - rec) / (pul - rec) for a in actions]
    return names, out


# ----------------------------------------------------------------------------- units and noise

def to_units(values, units):
    """Map (T, n) natural values into residual units, column by column ('log' or 'linear')."""
    values = np.asarray(values, dtype=float)
    out = values.copy()
    for i, unit in enumerate(units):
        if unit == 'log':
            with np.errstate(all='ignore'):
                out[..., i] = np.log(np.maximum(values[..., i], LOG_FLOOR))
    return out


def from_units(values, units):
    out = np.asarray(values, dtype=float).copy()
    for i, unit in enumerate(units):
        if unit == 'log':
            out[..., i] = np.exp(out[..., i])
    return out


def robust_sigma(y):
    """Noise sigma from second differences: MAD / 0.6745 / sqrt(6). Insensitive to smooth trends."""
    y = np.asarray(y, dtype=float)
    y = y[np.isfinite(y)]
    if len(y) < 5:
        return float('nan')
    d2 = np.diff(y, 2)
    return float(np.median(np.abs(d2 - np.median(d2))) / 0.6745 / math.sqrt(6.0))


def holds(actions, min_len=1):
    """Maximal runs of identical actions: list of (start, end) with end exclusive."""
    out, start = [], 0
    for t in range(1, len(actions) + 1):
        if t == len(actions) or actions[t] != actions[start]:
            if t - start >= min_len:
                out.append((start, t))
            start = t
    return out


def estimate_noise(episodes, units, skip=5, min_len=15):
    """Per-observable sigma in residual units: median of robust_sigma over holds (after `skip` ticks)."""
    per = [[] for _ in units]
    for ep in episodes:
        y = to_units(ep['obs'], units)
        for start, end in holds(ep['actions'], min_len=min_len):
            for i in range(len(units)):
                s = robust_sigma(y[start + skip:end, i])
                if np.isfinite(s) and s > 0:
                    per[i].append(s)
    return [float(np.median(p)) if p else 1.0 for p in per]


def resolve_units_noise(model, names, episodes, units=None, noise=None):
    """Residual units and sigma per observable. Precedence: explicit args > model UNITS/NOISE > auto.

    Auto units: 'log' if every observation is positive, else 'linear'. Auto noise: estimate_noise().
    `units`/`noise` may be a single value (applied to all) or a dict.
    """
    def pick(arg, attr):
        if isinstance(arg, dict):
            return arg
        if arg is not None:
            return {n: arg for n in names}
        return dict(getattr(model, attr, None) or {})
    u, s = pick(units, 'UNITS'), pick(noise, 'NOISE')
    for i, name in enumerate(names):
        if name not in u:
            positive = all((ep['obs'][:, i] > 0).all() for ep in episodes) if episodes else True
            u[name] = 'log' if positive else 'linear'
    unit_list = [u[n] for n in names]
    if any(n not in s for n in names):
        est = estimate_noise(episodes, unit_list)
        for i, name in enumerate(names):
            s.setdefault(name, est[i])
    return unit_list, [float(s[n]) for n in names]


# ----------------------------------------------------------------------------- scores

def score_sigma(episodes, skip=20, factor=0.1):
    """Local stand-in for the organizer sigma: factor x std of each observable after tick `skip`."""
    obs = np.concatenate([ep['obs'][skip:] for ep in episodes])
    return factor * obs.std(axis=0)


def score(pred, obs, sigma):
    """Organizer metric per observable: mean over ticks of 1 / (1 + |err| / sigma)."""
    err = np.abs(np.asarray(pred) - np.asarray(obs))
    err = np.where(np.isfinite(err), err, 1e12)
    return (1.0 / (1.0 + err / sigma)).mean(axis=0)


def persistence(ep):
    return np.tile([float(ep['initial'][n]) for n in ep['names']], (len(ep['obs']), 1))


# ----------------------------------------------------------------------------- random schedules

KINDS = ('holds', 'switch', 'extremes', 'uniform', 'mixed')


def _level(rng, lo, hi, rec, pul):
    r = rng.random()
    if r < 0.25:
        return rec
    if r < 0.5:
        return pul
    if r < 0.7:
        return lo if rng.random() < 0.5 else hi
    if r < 0.8:  # recovery-scenario range u in [0.7, 1]
        return rec + rng.uniform(0.7, 1.0) * (pul - rec)
    return rng.uniform(lo, hi)


def random_schedule(bounds, steps, kind, rng, recovery=None, pulse=None):
    """In-bounds action list of a given kind: holds, switch (fast), extremes, uniform, mixed."""
    names = list(bounds)
    recovery = recovery or {n: bounds[n][0] for n in names}
    pulse = pulse or {n: bounds[n][1] for n in names}

    def clip(action):
        return {n: float(min(max(action[n], bounds[n][0]), bounds[n][1])) for n in names}

    def level():
        return clip({n: _level(rng, *bounds[n], recovery.get(n, bounds[n][0]), pulse.get(n, bounds[n][1]))
                     for n in names})

    out = []
    while len(out) < steps:
        k = kind if kind != 'mixed' else KINDS[rng.integers(0, 4)]
        if k == 'holds':
            out += [level()] * int(rng.integers(30, 600))
        elif k == 'switch':
            a, b = level(), clip({n: bounds[n][int(rng.integers(0, 2))] for n in names})
            period = int(rng.integers(1, 6))
            out += [(a if (t // period) % 2 == 0 else b) for t in range(int(rng.integers(50, 400)))]
        elif k == 'extremes':
            out += [clip({n: bounds[n][int(rng.integers(0, 2))] for n in names})] * int(rng.integers(100, 400))
        else:
            out += [clip({n: rng.uniform(*bounds[n]) for n in names}) for _ in range(int(rng.integers(50, 400)))]
    return out[:steps]


def random_initial(ranges, rng, widen=0.15):
    """Initial reading sampled uniformly from each observable's range, widened by `widen` on both sides."""
    out = {}
    for name, (lo, hi) in ranges.items():
        pad = widen * (hi - lo)
        value = rng.uniform(lo - pad, hi + pad)
        out[name] = float(max(value, 0.0) if lo >= 0 else value)
    return out


def initial_ranges(system=None, episodes=(), names=None):
    """Docs initial ranges if available, else the range of initial readings in the data (+-20%)."""
    ranges = dict(brief_info(system)['initial_ranges']) if system else {}
    for name in names or []:
        if name not in ranges:
            vals = [ep['initial'][name] for ep in episodes if name in ep['initial']]
            if vals:
                lo, hi = min(vals), max(vals)
                ranges[name] = [lo - 0.2 * abs(lo), hi + 0.2 * abs(hi)]
            else:
                ranges[name] = [0.0, 1.0]
    return ranges


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, default=_json_default))


def _json_default(obj):
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (set, tuple)):
        return list(obj)
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(type(obj))
