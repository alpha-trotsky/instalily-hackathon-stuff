"""Basin-hopping full-rollout refit on R1+R2 (fit.py's Problem, soft_l1 f_scale 2, model NOISE).
usage: hopfit.py modules init.json out.json iters perturb seed [init2.json for module params]"""
import sys, json, time, numpy as np
sys.path.insert(0, '.')
from scipy.optimize import least_squares
from greybox.common import core
from greybox.common.fit import Problem, evaluate
mods = [m for m in sys.argv[1].split(',') if m]
init = dict(json.load(open(sys.argv[2]))['params'])
if len(sys.argv) > 7:  # module params from another fit
    other = json.load(open(sys.argv[7]))['params']
    for m in mods:
        for k in __import__('importlib').import_module('greybox.common.core').load_model('greybox/ad_auction_model.py').MODULES[m][0]:
            init[k] = other[k]
out, iters, perturb, seed = sys.argv[3], int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
model = core.load_model('greybox/ad_auction_model.py')
for m in mods:  # module gains start nonzero
    for k in model.MODULES[m][0]:
        if abs(init.get(k, 0)) < 1e-6: init[k] = model.SPEC[k][0]
eps = core.load_episodes(['data/ad_auction/R1.json', 'data/ad_auction/R2.json'], model=model)
sigma = [model.NOISE[n] for n in model.OBSERVABLES]
pr = Problem(model, eps, mods, ['linear'] * 3, sigma, (), init, 0)
rng = np.random.default_rng(seed)
def solve(x):
    return least_squares(pr.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=1e-4,
                         ftol=1e-10, xtol=1e-10, max_nfev=250)
t0 = time.time()
best = solve(pr.x0()); hist = [best.cost]
print(f'start: cost {best.cost:.1f} nfev {best.nfev} ({time.time()-t0:.0f}s)', flush=True)
for k in range(iters):
    x = best.x + rng.normal(0, perturb, best.x.size) * np.maximum(np.abs(best.x), 0.5)
    sol = solve(x)
    tag = ''
    if sol.cost < best.cost:
        best, tag = sol, ' *'
    hist.append(sol.cost)
    print(f'hop {k}: cost {sol.cost:.1f} nfev {sol.nfev} best {best.cost:.1f}{tag} ({time.time()-t0:.0f}s)', flush=True)
    params = pr.params(best.x)
    sig = core.score_sigma(eps)
    ev = [evaluate(model, params, [ep], sig) for ep in eps]
    json.dump({'model': 'greybox/ad_auction_model.py', 'modules': sorted(mods), 'cost': float(best.cost), 'free': pr.names,
               'hop_costs': hist, 'params': params, 'eval': {'R1': ev[0], 'R2': ev[1]}, 'time_s': time.time() - t0},
              open(out, 'w'), indent=1)
print('done', out, best.cost, {k: round(v, 4) for k, v in pr.params(best.x).items()})
