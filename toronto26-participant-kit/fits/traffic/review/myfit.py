"""Reviewer fit driver: fit.Problem + least_squares with a coarse diff_step (the queue model is piecewise linear).
python fits/traffic/review/myfit.py MODEL MODULES OUT [INIT.json] [nfev]"""
import sys, json, time
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, '.')
from greybox.common import core, fit as F

model_path, mods, out = sys.argv[1], set(m for m in sys.argv[2].split(',') if m and m != 'none'), sys.argv[3]
init = json.load(open(sys.argv[4]))['params'] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
nfev = int(sys.argv[5]) if len(sys.argv) > 5 else 300
m = core.load_model(model_path)
if init is not None:  # active modules start from SPEC defaults, not from the init file's off values
    for mod in mods:
        for n in m.MODULES[mod][0]:
            init[n] = m.SPEC[n][0]
eps = core.load_episodes(['data/traffic/R1.json', 'data/traffic/R2.json'], model=m)
for ep in eps:
    ep['u'] = [m.normalize(a, ep['bounds']) for a in ep['actions']]
names = eps[0]['names']
units = [m.UNITS[n] for n in names]; sigma = [m.NOISE[n] for n in names]
P = F.Problem(m, eps, mods, units, sigma, init=init)
x = P.x0(); t0 = time.time()
c0 = 0.5 * np.sum(2 * 4 * (np.sqrt(1 + (P.residuals(x) / 2) ** 2) - 1))
stages = [(0.05, 300, 40), (0.02, None, nfev), (0.01, None, nfev // 2)]
if init is not None:
    stages = stages[1:]
from scipy.optimize import minimize
def _cost(z):
    r = P.residuals(z)
    return float(np.sum(2 * 4 * (np.sqrt(1 + (r / 2) ** 2) - 1)) * 0.5)
pw = int(sys.argv[6]) if len(sys.argv) > 6 else 3000
for rep in range(2):
    sol0 = minimize(_cost, x, method='Powell', options={'maxfev': pw // 2, 'xtol': 1e-3, 'ftol': 1e-6})
    x = sol0.x
    print('powell', rep, 'cost', round(sol0.fun, 1), 'nfev', sol0.nfev, '%.0fs' % (time.time() - t0), flush=True)
stages = stages[-1:]
for ds, h, nf in stages:
    sol = least_squares(P.residuals, x, kwargs={'horizon': h}, loss='soft_l1', f_scale=2.0, x_scale='jac',
                        diff_step=ds, max_nfev=nf, ftol=1e-12, xtol=1e-12, gtol=1e-12)
    x = sol.x
    print('diff_step', ds, 'horizon', h, 'cost', round(sol.cost, 1), 'nfev', sol.nfev, '%.0fs' % (time.time() - t0), flush=True)
params = P.params(x)
sig = core.score_sigma(eps)
ev = F.evaluate(m, params, eps, sig)
per = [F.evaluate(m, params, [ep], sig) for ep in eps]
res = {'model': model_path, 'modules': sorted(mods), 'cost': float(sol.cost), 'start_cost': float(c0), 'params': params,
       'free': P.names, 'eval': {'all': ev, 'R1': per[0], 'R2': per[1]}}
json.dump(res, open(out, 'w'), indent=1)
print('cost', round(sol.cost, 1), 'score all', round(np.mean(ev['score']), 4), 'R1', round(np.mean(per[0]['score']), 4),
      'R2', round(np.mean(per[1]['score']), 4), np.round(ev['score'], 3).tolist())
