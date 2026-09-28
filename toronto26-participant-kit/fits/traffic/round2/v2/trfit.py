"""Round-2 fit driver for traffic (v1 structure or v2): Powell passes then a least_squares polish (as fitv1.py),
and a score of every run R1-R5 with the heldout.py sigma (0.1 x std after tick 20 of all traffic data).
Free: no simulator steps.

python fits/traffic/round2/v2/trfit.py --model greybox/traffic_model_v2.py --init fits/traffic/final_v1.json \
    --data R1 R2 R3 --out fits/traffic/round2/v2/A_v2.json [--pw 4000] [--set LD=3 P_CAP=6] [--fix kg=75]
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.optimize import least_squares, minimize
sys.path.insert(0, '.')
from greybox.common import core, fit as F

ALL = ['R1', 'R2', 'R3', 'R4', 'R5']


def load(model_path, sets):
    m = core.load_model(model_path)
    for kv in sets or []:
        k, v = kv.split('=')
        setattr(m, k, type(getattr(m, k))(float(v)))
    return m


def episodes(m, names):
    eps = core.load_episodes([f'data/traffic/{r}.json' for r in names], model=m)
    for ep, r in zip(eps, names):
        ep['name'] = r
    return eps


def heldout_sigma(m):
    return core.score_sigma(episodes(m, ALL))


def clamp(m, pred, names):
    out = pred.copy()
    for i, n in enumerate(names):
        lo, hi = m.CLAMP[n]
        out[:, i] = np.clip(out[:, i], lo, hi)
    return np.nan_to_num(out, nan=0.0)


def score_runs(m, params, names=ALL):
    sig = heldout_sigma(m)
    res = {}
    for ep in episodes(m, names):
        pred = clamp(m, core.rollout(m, params, ep), ep['names'])
        res[ep['name']] = core.score(pred, ep['obs'], sig).round(4).tolist()
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True); ap.add_argument('--init', default='-')
    ap.add_argument('--data', nargs='+', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--pw', type=int, default=4000); ap.add_argument('--reps', type=int, default=2)
    ap.add_argument('--lsq', type=int, default=150)
    ap.add_argument('--set', nargs='*'); ap.add_argument('--fix', nargs='*')
    ap.add_argument('--scoresig', action='store_true', help='residuals in score sigma (heldout sigma) units')
    ap.add_argument('--only', nargs='*', help='fit only these parameters (others held at --init)')
    a = ap.parse_args()
    m = load(a.model, a.set)
    init = {}
    if a.init != '-':
        src = json.load(open(a.init))['params']
        init = {k: v for k, v in src.items() if k in m.SPEC}
    fixed = []
    for kv in a.fix or []:
        k, v = kv.split('='); init[k] = float(v); fixed.append(k)
    if a.only:
        fixed += [n for n in m.SPEC if n not in a.only and n not in fixed]
    eps = episodes(m, a.data)
    names = eps[0]['names']
    units = [m.UNITS[n] for n in names]; sigma = [m.NOISE[n] for n in names]
    if a.scoresig:
        sigma = heldout_sigma(m).tolist()
    P = F.Problem(m, eps, set(), units, sigma, init=init, fixed=fixed)
    x = P.x0(); t0 = time.time()

    def _cost(z):
        r = P.residuals(z)
        return float(np.sum(2 * 4 * (np.sqrt(1 + (r / 2) ** 2) - 1)) * 0.5)

    c0 = _cost(x)
    print('start cost', round(c0, 1), flush=True)
    for rep in range(a.reps):
        sol0 = minimize(_cost, x, method='Powell', options={'maxfev': a.pw // a.reps, 'xtol': 1e-3, 'ftol': 1e-6})
        x = sol0.x
        print('powell', rep, 'cost', round(sol0.fun, 1), 'nfev', sol0.nfev, '%.0fs' % (time.time() - t0), flush=True)
        json.dump({'params': P.params(x), 'cost': float(sol0.fun), 'stage': f'powell{rep}', 'set': a.set or []},
                  open(a.out + '.ckpt', 'w'), indent=1)
    if a.lsq > 0:
        sol = least_squares(P.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=0.01,
                            max_nfev=a.lsq, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        if sol.cost <= _cost(x) + 1e-9:
            x = sol.x
    params = P.params(x)
    cost = _cost(x)
    sc = score_runs(m, params)
    res = {'scoresig': a.scoresig, 'model': a.model, 'modules': [], 'set': a.set or [], 'fixed': fixed, 'cost': cost, 'start_cost': c0,
           'params': params, 'free': P.names, 'data': [f'data/traffic/{r}.json' for r in a.data],
           'train': a.data, 'scores': sc,
           'score_mean': {r: round(float(np.mean(v)), 4) for r, v in sc.items()}}
    json.dump(res, open(a.out, 'w'), indent=1)
    print('cost', round(cost, 1), 'start', round(c0, 1), res['score_mean'], '%.0fs' % (time.time() - t0), flush=True)
