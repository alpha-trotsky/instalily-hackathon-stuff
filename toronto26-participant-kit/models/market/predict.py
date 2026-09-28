"""Gray-box forecaster (generic predict.py written by greybox/common/package.py).

Loads params.json and the model module next to this file (relative to __file__), caches them in a module
global, and re-initializes every simulated state on each call (the model's simulate() starts from the
initial reading). Any failure falls back to persistence; outputs are clamped to params.json "clamp".
Standard library + numpy/scipy only.
"""
import importlib.util
import json
import math
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CACHE = {}


def _load():
    if not _CACHE:
        cfg = json.loads((_HERE / 'params.json').read_text())
        spec = importlib.util.spec_from_file_location('_gb_model_' + cfg.get('system', 'x'), _HERE / cfg['model_file'])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _CACHE.update(cfg=cfg, model=module)
    return _CACHE['cfg'], _CACHE['model']


def _num(value, default):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    return value if math.isfinite(value) else default


def _bounds(cfg, context):
    bounds = {k: list(v) for k, v in cfg['bounds'].items()}
    try:
        for name, pair in ((context or {}).get('intervention_bounds') or {}).items():
            if name in bounds:
                lo, hi = float(pair[0]), float(pair[1])
                if math.isfinite(lo) and math.isfinite(hi) and lo <= hi:
                    bounds[name] = [lo, hi]
    except Exception:
        pass
    return bounds


def _clean_actions(interventions, bounds, recovery):
    """Every action as a full in-bounds dict; missing / bad values repeat the previous action."""
    last = {k: min(max(float(recovery.get(k, lo)), lo), hi) for k, (lo, hi) in bounds.items()}
    out = []
    for action in interventions:
        current = {}
        for name, (lo, hi) in bounds.items():
            value = _num(action.get(name) if isinstance(action, dict) else None, last[name])
            current[name] = min(max(value, lo), hi)
        out.append(current)
        last = current
    return out


def predict(initial, interventions, context):
    try:
        n = len(interventions)
    except TypeError:
        return []
    try:
        cfg, model = _load()
        names = cfg['observables']
        fallback = cfg.get('fallback', {})
    except Exception:
        names, fallback, cfg, model = list(initial) if isinstance(initial, dict) else [], {}, None, None
    start = {}
    for name in names:
        value = initial.get(name) if isinstance(initial, dict) else None
        start[name] = _num(value, _num(fallback.get(name), 0.0))
    if cfg is None:
        return [dict(start) for _ in range(n)]
    try:
        bounds = _bounds(cfg, context)
        actions = _clean_actions(interventions, bounds, cfg.get('recovery', {}))
        rows = model.simulate(cfg['params'], start, [model.normalize(a, bounds) for a in actions])
        clamp = cfg.get('clamp', {})
        result, last = [], start
        for t in range(n):
            current = {}
            row = rows[t] if t < len(rows) else None
            for i, name in enumerate(names):
                value = _num(row[i], None) if row is not None else None
                if value is None:
                    value = last[name]
                lo, hi = clamp.get(name, (-math.inf, math.inf))
                current[name] = float(min(max(value, lo), hi))
            result.append(current)
            last = current
        return result
    except Exception:
        return [dict(start) for _ in range(n)]
