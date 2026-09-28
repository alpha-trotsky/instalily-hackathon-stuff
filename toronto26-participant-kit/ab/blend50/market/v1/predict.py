"""Market forecaster: gray-box M1 (funding lock) + M2 (risk capacity) model fitted to research Run A."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from market_model import simulate  # noqa: E402

NAMES = ('price', 'volume', 'depth')
CONTROLS = ('interest_rate', 'transaction_tax')
DEFAULT_BOUNDS = {'interest_rate': [0.0, 0.1], 'transaction_tax': [0.0, 0.05]}
_PARAMS = None


def _params():
    global _PARAMS
    if _PARAMS is None:
        _PARAMS = json.loads(Path(__file__).with_name('params.json').read_text())['params']
    return _PARAMS


def _normalized(action, bounds):
    values = []
    for name in CONTROLS:
        low, high = bounds[name]
        value = (float(action[name]) - low) / (high - low)
        values.append(min(max(value, 0.0), 1.0))
    return tuple(values)


def _finite(value):
    return isinstance(value, float) and math.isfinite(value)


def predict(initial, interventions, context):
    bounds = dict(DEFAULT_BOUNDS)
    bounds.update((context or {}).get('intervention_bounds') or {})
    start = {name: float(initial[name]) for name in NAMES}
    try:
        actions = [_normalized(action, bounds) for action in interventions]
        rows = simulate(_params(), start, actions)
    except Exception:
        return [dict(start) for _ in interventions]
    result, last = [], start
    for row in rows:
        current = {name: float(value) for name, value in zip(NAMES, row)}
        if not all(_finite(v) for v in current.values()):
            current = dict(last)
        result.append(current)
        last = current
    return result
