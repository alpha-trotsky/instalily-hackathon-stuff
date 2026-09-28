import json, sys, os, importlib.util
import numpy as np
sys.path.insert(0, '.')
from fits.round2.heldout import sigma
S = 'power_grid'
NAMES = ['load', 'frequency', 'renewable_share']
CTRL = ['price_signal', 'reserve_dispatch', 'charging_allowance', 'interconnector']
_names, SIG = sigma(S)
assert list(_names) == NAMES, _names
CTX = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']

def load_pred(folder='fits/round2/v1_models/power_grid', tag='v1'):
    spec = importlib.util.spec_from_file_location('pgpred_' + tag, os.path.join(folder, 'predict.py'))
    m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m); return m

def run(r):
    d = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in NAMES] for x in d['observations']])
    a = np.array([[x[c] for c in CTRL] for x in d['actions']])
    segs = []; t = 0
    for sg in d.get('segments', [{'segments': []}])[0]['segments'] if d.get('segments') else []:
        segs.append((t, t + sg['steps'], sg['action'])); t += sg['steps']
    return d, o, a, segs

def predict(mod, d):
    p = mod.predict(d['initial'], d['actions'], CTX)
    return np.array([[x[n] for n in NAMES] for x in p])
