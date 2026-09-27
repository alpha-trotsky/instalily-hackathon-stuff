"""Chained full-rollout refit on R1+R2: repeated least_squares from the last x (fit.py's Problem).
usage: chainfit.py modules init.json out.json [perturb seed diff_step rounds nfev]"""
import sys, json, time, numpy as np
sys.path.insert(0, '.')
from scipy.optimize import least_squares
from greybox.common import core
from greybox.common.fit import Problem, evaluate
mods = [m for m in sys.argv[1].split(',') if m]
init = json.load(open(sys.argv[2]))['params']
out = sys.argv[3]
perturb = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
ds = float(sys.argv[6]) if len(sys.argv) > 6 else 1e-4
rounds = int(sys.argv[7]) if len(sys.argv) > 7 else 6
nfev = int(sys.argv[8]) if len(sys.argv) > 8 else 300
model = core.load_model('greybox/ad_auction_model.py')
eps = core.load_episodes(['data/ad_auction/R1.json', 'data/ad_auction/R2.json'], model=model)
units = ['linear'] * 3
sigma = [model.NOISE[n] for n in model.OBSERVABLES]
pr = Problem(model, eps, mods, units, sigma, (), init, 0)
x = pr.x0()
if perturb:
    x = x + np.random.default_rng(seed).normal(0, perturb, x.size) * np.maximum(np.abs(x), 0.5)
t0 = time.time(); best = None
for k in range(rounds):
    sol = least_squares(pr.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=ds, max_nfev=nfev)
    print(f'round {k}: cost {sol.cost:.1f} nfev {sol.nfev} status {sol.status} ({time.time()-t0:.0f}s)', flush=True)
    improved = best is None or sol.cost < best.cost * 0.999
    if best is None or sol.cost < best.cost: best = sol
    x = sol.x
    if not improved: break
params = pr.params(best.x)
sig = core.score_sigma(eps)
ev = [evaluate(model, params, [ep], sig) for ep in eps]
res = {'model': 'greybox/ad_auction_model.py', 'modules': sorted(mods), 'cost': float(best.cost), 'free': pr.names,
       'data': ['data/ad_auction/R1.json:0', 'data/ad_auction/R2.json:0'], 'params': params,
       'eval': {'R1': ev[0], 'R2': ev[1]}, 'time_s': time.time() - t0, 'perturb': perturb, 'seed': seed, 'diff_step': ds}
json.dump(res, open(out, 'w'), indent=1)
print('saved', out, 'cost', best.cost, 'score R1 %.3f R2 %.3f' % (np.mean(ev[0]['score']), np.mean(ev[1]['score'])))
print({k: round(v, 4) for k, v in params.items()})
