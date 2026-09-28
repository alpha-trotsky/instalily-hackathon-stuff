"""Free: multi-pass full-rollout fitter for the epidemic round-2 work (reuses greybox.common.fit.Problem).
Alternates least_squares passes with x_scale=1 (large raw steps) and x_scale='jac' until the cost stops
improving by > 0.2 %. Output has the same layout as greybox.common.fit (params, cost, ...).
python3 fits/epidemic/round2/v2/fit2.py --name X --runs R1,R2 --init init.json [--fix a,b] [--units log|lin]
       [--modules m1,m2] [--model greybox/epidemic_model_v2.py] [--nfev 150] [--passes 6]"""
import argparse, json, sys, time, os
sys.path.insert(0, os.getcwd())
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from greybox.common import core
from greybox.common.fit import Problem

F = Path('fits/epidemic/round2/v2')
ap = argparse.ArgumentParser()
ap.add_argument('--name', required=True); ap.add_argument('--runs', required=True); ap.add_argument('--init', required=True)
ap.add_argument('--fix', default=''); ap.add_argument('--units', default='lin'); ap.add_argument('--modules', default='m1,m2')
ap.add_argument('--model', default='greybox/epidemic_model_v2.py'); ap.add_argument('--nfev', type=int, default=150)
ap.add_argument('--passes', type=int, default=6); ap.add_argument('--free', default='', help='if set, fit only these (others fixed)')
a = ap.parse_args()
model = core.load_model(a.model)
eps = core.load_episodes([f'data/epidemic/{r}.json' for r in a.runs.split(',')], model=model)
for ep in eps:
    ep['u'] = [model.normalize(x, ep['bounds']) for x in ep['actions']]
if a.units == 'lin':
    units, sigma = ['linear', 'linear'], [8.41, 4.31]
else:
    units, sigma = ['log', 'log'], [0.01, 0.01]
init = json.loads((F / a.init).read_text() if not os.path.exists(a.init) else Path(a.init).read_text())['params']
mods = {m for m in a.modules.split(',') if m}
fixed = [f for f in a.fix.split(',') if f]
if a.free:
    keep = set(a.free.split(','))
    fixed += [n for n in core.free_names(model, mods, fixed) if n not in keep]
prob = Problem(model, eps, mods, units, sigma, fixed, init)
x = prob.x0(); t0 = time.time()
def cost(x):
    r = prob.residuals(x); z = (r / 2.0) ** 2; return float(0.5 * 4.0 * np.sum(2 * (np.sqrt(1 + z) - 1)))
c = cost(x); print(f'{a.name}: start cost {c:.1f} free {len(x)}', flush=True)
for k in range(a.passes):
    c_prev = c
    for xs in (1.0, 'jac'):
        try:
            sol = least_squares(prob.residuals, x, loss='soft_l1', f_scale=2.0, x_scale=xs, max_nfev=a.nfev)
        except Exception as e:
            print('  fail', e); continue
        if sol.cost < c:
            x, c = sol.x, float(sol.cost)
        print(f'  pass {k} x_scale={xs}: cost {sol.cost:.1f} nfev {sol.nfev} ({time.time()-t0:.0f}s)', flush=True)
    if c > c_prev * 0.998:
        break
P = prob.params(x)
out = {'model': a.model, 'modules': sorted(mods), 'cost': c, 'units': units, 'noise': sigma, 'runs': a.runs,
       'free': prob.names, 'fixed': fixed, 'init': a.init, 'time_s': time.time() - t0, 'params': P}
(F / f'{a.name}.json').write_text(json.dumps(out, indent=1))
print('saved', a.name, 'cost', round(c, 1))
