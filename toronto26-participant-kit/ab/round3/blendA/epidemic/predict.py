"""Blend forecaster: weighted average of the forecasters in ./v1 and ./v2 (weights in blend.json).
Each sub-forecaster loads its own files relative to its own __file__. If one fails, the other is used alone."""
import importlib.util
import json
import math
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CACHE = {}


def _load():
    if not _CACHE:
        cfg = json.loads((_HERE / 'blend.json').read_text())
        mods = {}
        for name in cfg['weights']:
            spec = importlib.util.spec_from_file_location(f'_blend_{name}_{cfg["system"]}', _HERE / name / 'predict.py')
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mods[name] = mod
        _CACHE.update(cfg=cfg, mods=mods)
    return _CACHE['cfg'], _CACHE['mods']


def predict(initial, interventions, context):
    cfg, mods = _load()
    outs = {}
    for name, mod in mods.items():
        try:
            outs[name] = mod.predict(initial, interventions, context)
        except Exception:
            pass
    if not outs:
        return [dict(initial) for _ in interventions]
    names = list(initial)
    res = []
    for t in range(len(interventions)):
        row = {}
        for k in names:
            num = den = 0.0
            for name, out in outs.items():
                try:
                    v = float(out[t][k])
                except Exception:
                    continue
                if math.isfinite(v):
                    w = cfg['weights'][name]
                    num += w * v
                    den += w
            row[k] = num / den if den > 0 else float(initial[k])
        res.append(row)
    return res
