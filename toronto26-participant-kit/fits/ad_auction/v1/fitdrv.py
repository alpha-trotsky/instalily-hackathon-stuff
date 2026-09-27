"""Phase-C fit driver for ad_auction v1 (review G5/G6): fit.py's Problem in local-score sigma units
(0.1 x std after tick 20 of R1+R2c), soft_l1 f_scale 2, start + basin hops (sequential, 1 CPU).
usage: python fits/ad_auction/v1/fitdrv.py MODULES OUT.json HOPS DATA... [--init a.json[,b.json]] [--seed S]"""
import sys, json, time, argparse, numpy as np
sys.path.insert(0, '.')
from scipy.optimize import least_squares
from greybox.common import core
from greybox.common.fit import Problem, evaluate

MODEL = 'greybox/ad_auction_model.py'
SIGMA = [0.0151, 1.52, 0.124]          # score sigma of R1+R2c (win, spend, conv)
ap = argparse.ArgumentParser()
ap.add_argument('modules'); ap.add_argument('out'); ap.add_argument('hops', type=int); ap.add_argument('data', nargs='+')
ap.add_argument('--init', default=''); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--nfev', type=int, default=300)
ap.add_argument('--perturb', type=float, default=0.15)
ap.add_argument('--fix', default='', help='name=value,... held fixed')
a = ap.parse_args()
mods = [m for m in a.modules.split(',') if m]
model = core.load_model(MODEL)
init = {}
for f in [f for f in a.init.split(',') if f]:        # later files override earlier ones
    init.update(json.load(open(f))['params'])
init = {k: v for k, v in init.items() if k in model.SPEC}
for m in mods:                                        # module gains start nonzero
    for k in model.MODULES[m][0]:
        if k not in init or abs(init[k]) < 1e-6 or k in model.MODULES[m][1] and init[k] == model.MODULES[m][1][k]:
            init[k] = model.SPEC[k][0]
fix = {k: float(v) for k, v in (i.split('=') for i in a.fix.split(',') if i)}
init.update(fix)
eps = core.load_episodes(a.data, model=model)
pr = Problem(model, eps, mods, ['linear'] * 3, SIGMA, tuple(fix), init, 0)
rng = np.random.default_rng(a.seed)
solve = lambda x: least_squares(pr.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=1e-4,
                                ftol=1e-9, xtol=1e-9, max_nfev=a.nfev)
t0 = time.time()
best = solve(pr.x0()); hist = [best.cost]
print(f'start: cost {best.cost:.1f} nfev {best.nfev} ({time.time()-t0:.0f}s)', flush=True)
def dump():
    params = pr.params(best.x)
    ref = core.load_episodes(['data/ad_auction/R1.json', 'data/ad_auction/R2c.json'], model=model)
    sig = core.score_sigma(ref)
    ev = {f"{ep['source']}:{ep['run']}": evaluate(model, params, [ep], sig) for ep in ref}
    json.dump({'model': MODEL, 'modules': sorted(mods), 'cost': float(best.cost), 'free': pr.names, 'hop_costs': hist,
               'units': dict(zip(eps[0]['names'], ['linear'] * 3)), 'noise': dict(zip(eps[0]['names'], SIGMA)),
               'names': eps[0]['names'], 'train_end': None, 'horizons': [], 'skip': 0, 'data': a.data,
               'params': params, 'eval': ev, 'time_s': time.time() - t0}, open(a.out, 'w'), indent=1)
dump()
for k in range(a.hops):
    x = best.x + rng.normal(0, a.perturb, best.x.size) * np.maximum(np.abs(best.x), 0.5)
    sol = solve(x); tag = ''
    if sol.cost < best.cost:
        best, tag = sol, ' *'
    hist.append(sol.cost)
    print(f'hop {k}: cost {sol.cost:.1f} nfev {sol.nfev} best {best.cost:.1f}{tag} ({time.time()-t0:.0f}s)', flush=True)
    dump()
print('done', a.out, round(best.cost, 1), json.dumps({k: round(v, 4) for k, v in pr.params(best.x).items()}))
