"""Phase C refit driver (from review/refit.py): larger diff_step + repeated rounds, several perturbed starts.
python fits/hospital_queue/refit2.py --modules m1,m2,urg --init X.json --data data/hospital_queue/R1.json [more] --out Y.json
"""
import argparse, json, sys, time
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, '.')
from greybox.common import core
from greybox.common.fit import Problem

ap = argparse.ArgumentParser()
ap.add_argument('--model', default='greybox/hospital_queue_model.py')
ap.add_argument('--modules', default='urg')
ap.add_argument('--init', required=True)
ap.add_argument('--data', nargs='+', default=['data/hospital_queue/R1.json', 'data/hospital_queue/R2c.json'])
ap.add_argument('--out', required=True)
ap.add_argument('--fix', default='')
ap.add_argument('--rounds', type=int, default=3)
ap.add_argument('--nfev', type=int, default=150)
ap.add_argument('--starts', type=int, default=3)
ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--set', default='')
a = ap.parse_args()

model = core.load_model(a.model)
init = dict(json.load(open(a.init))['params'])
for kv in [s for s in a.set.split(',') if s]:
    k, v = kv.split('='); init[k] = float(v)
for k, (v0, _) in model.SPEC.items():
    init.setdefault(k, v0)
eps = []
for f in a.data:
    d = json.load(open(f)); run = d['runs'][0]; names = list(model.OBSERVABLES)
    ep = {'obs': np.array([[o[k] for k in names] for o in run['observations']]), 'actions': run['actions'],
          'initial': run['initial'], 'bounds': d['brief']['interventions'], 'names': names, 'source': f, 'run': 0}
    ep['u'] = [model.normalize(x, ep['bounds']) for x in ep['actions']]
    eps.append(ep)
mods = set(m for m in a.modules.split(',') if m)
fixed = [s for s in a.fix.split(',') if s]
pb = Problem(model, eps, mods, ['linear'] * 3, [1.0, 3.0, 1.0], fixed, init, 0)
rng = np.random.default_rng(a.seed)
best = None; t0 = time.time()
for st in range(a.starts):
    x = pb.x0().copy()
    if st > 0:
        x = x + rng.normal(0, 0.15, size=x.shape) * np.maximum(np.abs(x), 0.5)
    for r in range(a.rounds):
        for ds in (1e-2, 1e-3):
            sol = least_squares(pb.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=ds,
                                max_nfev=a.nfev, xtol=1e-10, ftol=1e-10)
            x = sol.x
    print(f'start {st}: cost {sol.cost:.1f} ({time.time() - t0:.0f}s)', flush=True)
    if best is None or sol.cost < best[0]:
        best = (sol.cost, x.copy())
p = pb.params(best[1])
json.dump({'model': a.model, 'modules': sorted(mods), 'cost': float(best[0]), 'free': pb.names, 'params': p,
           'data': a.data, 'noise': {'wait_time': 1, 'queue': 3, 'discharges': 1}}, open(a.out, 'w'), indent=1)
print('saved', a.out, round(best[0], 1), {k: round(v, 4) for k, v in p.items() if k in pb.names})
