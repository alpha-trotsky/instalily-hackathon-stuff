"""Reviewer refit driver: same Problem/residuals as greybox.common.fit, but a larger finite-difference step
(diff_step) so least_squares does not stop at kinks after ~10-30 evaluations, plus repeated polishing rounds.
Usage (from KIT): python fits/hospital_queue/review/refit.py --modules urg --init X.json --out Y.json [--fix wf] [--rounds 4]
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, '.')
from greybox.common import core
from greybox.common.fit import Problem

ap = argparse.ArgumentParser()
ap.add_argument('--modules', default='urg')
ap.add_argument('--init', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--fix', default='')
ap.add_argument('--rounds', type=int, default=4)
ap.add_argument('--nfev', type=int, default=150)
ap.add_argument('--set', default='', help='name=value,... overrides of init params (natural units)')
a = ap.parse_args()

model = core.load_model('greybox/hospital_queue_model.py')
init = json.load(open(a.init))['params']
for kv in [s for s in a.set.split(',') if s]:
    k, v = kv.split('='); init[k] = float(v)
eps = []
for f in ('data/hospital_queue/R1.json', 'data/hospital_queue/R2.json'):
    d = json.load(open(f))
    run = d['runs'][0]
    names = list(model.OBSERVABLES)
    ep = {'obs': np.array([[o[k] for k in names] for o in run['observations']]), 'actions': run['actions'],
          'initial': run['initial'], 'bounds': d['brief']['interventions'], 'names': names, 'source': f, 'run': 0}
    ep['u'] = [model.normalize(x, ep['bounds']) for x in ep['actions']]
    eps.append(ep)
mods = set(m for m in a.modules.split(',') if m)
fixed = [s for s in a.fix.split(',') if s]
pb = Problem(model, eps, mods, ['linear'] * 3, [1.0, 3.0, 1.0], fixed, init, 0)
x = pb.x0()
t0 = time.time()
cost0 = 0.5 * np.sum(2.0 ** 2 * 2 * (np.sqrt(1 + (pb.residuals(x) / 2.0) ** 2) - 1))
print('start cost', round(cost0, 1), flush=True)
for r in range(a.rounds):
    for ds in (1e-2, 1e-3):
        sol = least_squares(pb.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=ds,
                            max_nfev=a.nfev, xtol=1e-10, ftol=1e-10)
        x = sol.x
        print(f'round {r} ds {ds}: cost {sol.cost:.1f} nfev {sol.nfev} status {sol.status} ({time.time() - t0:.0f}s)', flush=True)
p = pb.params(x)
json.dump({'model': 'greybox/hospital_queue_model.py', 'modules': sorted(mods), 'cost': float(sol.cost),
           'free': pb.names, 'params': p, 'data': ['R1:0', 'R2:0'], 'noise': {'wait_time': 1, 'queue': 3, 'discharges': 1}},
          open(a.out, 'w'), indent=1)
print('saved', a.out, {k: round(v, 4) for k, v in p.items()})
