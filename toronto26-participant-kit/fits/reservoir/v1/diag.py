"""10-tick mean residuals (obs - pred) per run for a fit file: python fits/reservoir/v1/diag.py FIT [block]"""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
fit = json.load(open(sys.argv[1])); blk = int(sys.argv[2]) if len(sys.argv) > 2 else 10
M = core.load_model(fit.get('model', 'greybox/reservoir_model.py'))
p = core.params_for(M, set(fit['modules']), fit['params'])
for f in ['R1', 'R2', 'R3']:
    d = json.load(open(f'data/reservoir/{f}.json')); r = d['runs'][0]
    acts = [M.normalize(a, d['brief']['interventions']) for a in r['actions']]
    pred = np.asarray(M.simulate(p, r['initial'], acts))
    obs = np.array([[o[k] for k in M.OBSERVABLES] for o in r['observations']])
    e = obs - pred
    print(f'== {f}  rows: tick, level obs, dL, dIn, dOut, dQ*1000, pred_in_excess')
    for s in range(0, len(obs), blk):
        sl = slice(s, s + blk)
        print(f'{s:4d} {obs[sl,0].mean():6.0f} {e[sl,0].mean():6.1f} {e[sl,1].mean():6.2f} {e[sl,2].mean():6.2f} {1000*e[sl,3].mean():6.1f}')
