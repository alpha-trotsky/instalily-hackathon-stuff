"""Shared loaders for the round-2 reservoir diagnosis (free; no steps)."""
import importlib.util, json, math, os, sys
import numpy as np
KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
os.chdir(KIT); sys.path.insert(0, KIT)
NAMES = ['level', 'inflow', 'outflow', 'quality']
CTL = ['release_rate', 'irrigation_allocation', 'withdrawal_depth', 'aeration']
sys.path.insert(0, os.path.join(KIT, 'fits', 'round2'))
import heldout
_, SIG = heldout.sigma('reservoir')
CTX = json.load(open('docs/reservoir.json'))['brief']['forecast_context']

def load_pred(folder='fits/round2/v1_models/reservoir'):
    return heldout.load(folder, 'v1res')

def run(name):
    r = json.load(open(f'data/reservoir/{name}.json'))['runs'][0]
    o = np.array([[x[n] for n in NAMES] for x in r['observations']])
    a = np.array([[x[c] for c in CTL] for x in r['actions']])
    segs = []
    t = 0
    for block in r.get('segments') or []:
        for s in block['segments']:
            segs.append((t, t + s['steps'], s['action'])); t += s['steps']
    if not segs:  # derive from action changes
        st = 0
        for i in range(1, len(a) + 1):
            if i == len(a) or (a[i] != a[i - 1]).any():
                segs.append((st, i, dict(zip(CTL, a[st])))); st = i
    return r, o, a, segs

def predict(mod, r):
    p = mod.predict(r['initial'], r['actions'], CTX)
    return np.array([[x[n] for n in NAMES] for x in p])

def season(t):
    return 11.2801 + 2.2527 * np.sin(2 * np.pi * t / 67.7547)
