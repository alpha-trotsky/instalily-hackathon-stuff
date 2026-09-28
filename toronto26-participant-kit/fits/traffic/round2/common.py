"""Shared helpers for the traffic round-2 diagnosis (free; no simulator steps)."""
import importlib.util, json, os, sys
import numpy as np
KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
os.chdir(KIT); sys.path.insert(0, KIT)
sys.path.insert(0, os.path.join(KIT, 'fits', 'round2'))
import heldout
OBS = ['flow_a', 'flow_b', 'speed_a', 'speed_b']
CTRL = ['signal_timing', 'lane_closure', 'toll', 'ramp_metering', 'freight_priority', 'clearance_effort']
names, SIG = heldout.sigma('traffic')
assert list(names) == OBS
CTX = json.load(open('docs/traffic.json'))['brief']['forecast_context']
_mod = heldout.load('fits/round2/v1_models/traffic', 'v1tr')

def run(name):
    r = json.load(open(f'data/traffic/{name}.json'))['runs'][0]
    o = np.array([[x[n] for n in OBS] for x in r['observations']])
    a = np.array([[x[c] for c in CTRL] for x in r['actions']])
    return r, o, a

def pred(r):
    return np.array([[x[n] for n in OBS] for x in _mod.predict(r['initial'], r['actions'], CTX)])

def segments(r, a):
    """(start, end, action) of every constant-action stretch."""
    segs = []; s = 0
    for t in range(1, len(a) + 1):
        if t == len(a) or not np.allclose(a[t], a[s]):
            segs.append((s, t, dict(zip(CTRL, a[s])))); s = t
    return segs

def label(act):
    rec = {'signal_timing': 0.5, 'lane_closure': 0.0, 'toll': 5.0, 'ramp_metering': 0.0, 'freight_priority': 0.5, 'clearance_effort': 1.0}
    short = {'signal_timing': 'sig', 'lane_closure': 'lane', 'toll': 'toll', 'ramp_metering': 'ramp', 'freight_priority': 'frt', 'clearance_effort': 'clr'}
    d = [f"{short[c]}{act[c]:g}" for c in CTRL if abs(act[c] - rec[c]) > 1e-9]
    return ' '.join(d) if d else 'recovery'
