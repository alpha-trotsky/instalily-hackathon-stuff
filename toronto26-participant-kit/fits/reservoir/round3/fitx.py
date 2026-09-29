"""Direct fitter (same Problem/residuals/cost as greybox.common.fit) with tighter tolerances and verbose termination.
python fits/reservoir/round3/fitx.py MODEL MODULES INIT OUT NFEV [--fix a,b] RUNS..."""
import sys, os, json, time, numpy as np
sys.path.insert(0, os.getcwd())
from scipy.optimize import least_squares
from greybox.common import core
from greybox.common.fit import Problem
args = sys.argv[1:]; fix = []
if '--fix' in args:
    i = args.index('--fix'); fix = [f for f in args[i + 1].split(',') if f]; del args[i:i + 2]
modelp, mods, init, out, nfev = args[:5]; runs = args[5:]
model = core.load_model(modelp)
eps = core.load_episodes([f'data/reservoir/{r}.json' for r in runs], model=model)
names = eps[0]['names']; units, sigma = core.resolve_units_noise(model, names, eps, None, None)
for ep in eps: ep['u'] = [model.normalize(a, ep['bounds']) for a in ep['actions']]
modules = {m for m in mods.split(',') if m}
initp = json.load(open(init))['params']
pr = Problem(model, eps, modules, units, sigma, fix, initp, 0)
x0 = pr.x0(); t = time.time()
c0 = 0.5 * np.sum(2.0**2 * 2 * (np.sqrt(1 + (pr.residuals(x0) / 2.0) ** 2) - 1))
sol = least_squares(pr.residuals, x0, loss='soft_l1', f_scale=2.0, x_scale='jac', max_nfev=int(nfev),
                    xtol=1e-12, ftol=1e-10, gtol=1e-10, diff_step=1e-6)
print(f'start cost {c0:.1f} -> {sol.cost:.1f}  nfev {sol.nfev} njev {sol.njev} status {sol.status} {sol.message} ({time.time()-t:.0f}s)')
res = {'model': modelp, 'modules': sorted(modules), 'cost': float(sol.cost), 'free': pr.names, 'data': runs,
       'params': pr.params(sol.x)}
core.write_json(out, res)
