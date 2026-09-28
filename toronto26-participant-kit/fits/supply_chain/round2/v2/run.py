"""Free: fit + held-out protocol (A transfer, B leave-one-new-out, C all) for supply_chain v1/v2 structures.
    python fits/supply_chain/round2/v2/run.py --model greybox/supply_chain_model_v2.py --tag v2 --mode A|B4|B5|C [--init f.json]
Score sigma = 0.1*std after tick 20 of R1-R5 (= fits/round2/heldout.py)."""
import argparse, json, sys, os, time
import numpy as np
sys.path.insert(0, os.getcwd())
from greybox.common import core
from greybox.common.fit import fit, Problem
from scipy.optimize import least_squares, minimize
from multiprocessing import get_context

def _job(task):
    mspec, trainfiles, units, sigma, fixed, init, x0, nfev, powell, loops = task
    model = core.load_model(mspec)
    eps = core.load_episodes(trainfiles, model=model)
    pr = Problem(model, eps, set(), units, sigma, fixed, init)
    t = time.time()
    def cost(x):
        r = pr.residuals(x); return float(np.sum(2 * 4 * (np.sqrt(1 + (r / 2) ** 2) - 1)) * 0.5)
    x = np.array(x0)
    for it in range(loops):
        if powell:
            x = minimize(cost, x, method='Powell', options={'maxfev': powell, 'xtol': 1e-3, 'ftol': 1e-6}).x
        sol = least_squares(pr.residuals, x, loss='soft_l1', f_scale=2.0, diff_step=1e-3, max_nfev=nfev)
        x = sol.x
    return {'cost': float(sol.cost), 'x': x.tolist(), 'time_s': time.time() - t, 'names': pr.names,
            'params': pr.params(x)}
OLD = ['R1', 'R2', 'R3']; NEW = ['R4', 'R5']
P = lambda r: f'data/supply_chain/{r}.json'

def sig():
    import importlib.util
    spec = importlib.util.spec_from_file_location('ho', 'fits/round2/heldout.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.sigma('supply_chain')[1]

def score_runs(model, params, runs, s):
    out = {}
    for r in runs:
        ep = core.load_episodes([P(r)], model=model)[0]
        pred = core.rollout(model, params, ep)
        out[r] = [round(float(x), 3) for x in core.score(pred, ep['obs'], s)]
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--model'); ap.add_argument('--tag'); ap.add_argument('--mode')
    ap.add_argument('--init'); ap.add_argument('--restarts', type=int, default=2); ap.add_argument('--nfev', type=int, default=600)
    ap.add_argument('--fix', default=''); ap.add_argument('--noise', default='')
    ap.add_argument('--powell', type=int, default=0); ap.add_argument('--free', default=''); ap.add_argument('--loops', type=int, default=2); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--perturb', type=float, default=0.1)
    a = ap.parse_args()
    model = core.load_model(a.model)
    train = {'A': OLD, 'C': OLD + NEW, 'B4': OLD + ['R5'], 'B5': OLD + ['R4']}[a.mode]
    eps = core.load_episodes([P(r) for r in train], model=model)
    names = eps[0]['names']
    noise = None
    if a.noise:
        noise = dict(zip(names, [float(x) for x in a.noise.split(',')]))
    units, sigma = core.resolve_units_noise(model, names, eps, None, noise)
    init = json.load(open(a.init))['params'] if a.init else None
    if init:
        init = {k: v for k, v in init.items() if k in model.SPEC}
    fixed = [f for f in a.fix.split(',') if f]
    if a.free:
        fr = a.free.split(','); fixed = [n for n in model.SPEC if n not in fr]
    pr = Problem(model, eps, set(), units, sigma, fixed, init)
    x0 = pr.x0(); rng = np.random.default_rng(a.seed)
    starts = [x0 if k == 0 else x0 + rng.normal(0, a.perturb, x0.size) * np.maximum(np.abs(x0), 0.5) for k in range(a.restarts)]
    tasks = [(a.model, [P(r) for r in train], units, sigma, fixed, init, s0.tolist(), a.nfev, a.powell, a.loops) for s0 in starts]
    t0 = time.time()
    if a.restarts > 1:
        with get_context('spawn').Pool(2) as pool:
            rs = pool.map(_job, tasks)
    else:
        rs = [_job(tasks[0])]
    best = min(rs, key=lambda r: r['cost'])
    res = {'model': a.model, 'mode': a.mode, 'train': train, 'cost': best['cost'], 'restart_costs': [r['cost'] for r in rs],
           'time_s': time.time() - t0, 'free': best['names'], 'noise': sigma, 'params': best['params']}
    s = sig()
    res['scores'] = score_runs(model, res['params'], OLD + NEW, s)
    res['score_sigma'] = s.tolist()
    os.makedirs('fits/supply_chain/round2/v2', exist_ok=True)
    out = f'fits/supply_chain/round2/v2/{a.tag}_{a.mode}.json'
    json.dump(res, open(out, 'w'), indent=1, default=float)
    print(a.tag, a.mode, 'cost', round(res['cost'], 1), 'restarts', [round(c, 1) for c in res['restart_costs']], f"{res['time_s']:.0f}s")
    for r, v in res['scores'].items():
        print(f'  {r} {v} mean {np.mean(v):.3f}' + ('  (train)' if r in train else '  (HELD-OUT)'))
