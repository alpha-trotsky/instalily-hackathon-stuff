"""Shared loaders for the epidemic round-2 diagnosis (free; no steps)."""
import json, importlib.util, sys, os
import numpy as np
KIT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(KIT)
OBS = ['daily_cases', 'hospital_load']
CTRL = ['school_closure', 'mask_mandate', 'vaccination_rate']
CTX = json.load(open('docs/epidemic.json'))['brief']['forecast_context']

def load_run(r):
    run = json.load(open(f'data/epidemic/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in OBS] for x in run['observations']])
    a = np.array([[x[c] for c in CTRL] for x in run['actions']])
    return run, o, a

def segs(run):
    out, t = [], 0
    for blk in run.get('segments', []):
        for s in blk['segments']:
            out.append((t, t + s['steps'], s['action'])); t += s['steps']
    return out

def v1():
    spec = importlib.util.spec_from_file_location('v1pred', 'fits/round2/v1_models/epidemic/predict.py')
    m = importlib.util.module_from_spec(spec); sys.modules['v1pred'] = m; spec.loader.exec_module(m); return m

def predict(mod, run):
    p = mod.predict(run['initial'], run['actions'], CTX)
    return np.array([[x[n] for n in OBS] for x in p])

def sigma():
    allo = []
    for r in ['R1', 'R2', 'R3', 'R4', 'R5']:
        _, o, _ = load_run(r); allo.append(o[20:])
    return 0.1 * np.concatenate(allo).std(0)
