"""Fit market model variants by full-rollout least squares and compare them on held-out ticks.

    python greybox/fit_market.py data/market/A.json --train-end 450 --variants base,m1,m2,m12,m13,m23,m123
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parent))
from market_model import SPEC, free_names, params_for, simulate, normalize, to_natural, to_raw

NAMES = ('price', 'volume', 'depth')
LOG_NOISE = 0.004  # measurement noise is ~0.3-0.45% of level for every observable


def load_runs(paths):
    runs = []
    for path in paths:
        data = json.loads(Path(path).read_text())
        bounds = data['brief']['interventions']
        for run in data['runs']:
            runs.append({
                'initial': run['initial'],
                'actions': [normalize(a, bounds) for a in run['actions']],
                'obs': np.array([[o[n] for n in NAMES] for o in run['observations']]),
            })
    return runs


def rollout(params, run):
    return np.array(simulate(params, run['initial'], run['actions']))


def score(pred, obs, sigma):
    """Organizer metric against our noisy observations: mean of 1/(1+|err|/sigma) per observable."""
    return (1.0 / (1.0 + np.abs(pred - obs) / sigma)).mean(axis=0)


def fit_variant(modules, runs, train_end, restarts, seed=0):
    names = free_names(modules)
    base = params_for(modules)
    x0 = np.array([to_raw(n, base[n]) for n in names])

    def residuals(x):
        params = params_for(modules, {n: to_natural(n, v) for n, v in zip(names, x)})
        res = []
        for run in runs:
            try:
                pred = rollout(params, run)[:train_end]
            except (OverflowError, ValueError, ZeroDivisionError):
                pred = np.full_like(run['obs'][:train_end], 1e-6)
            res.append(((np.log(pred) - np.log(run['obs'][:train_end])) / LOG_NOISE).ravel())
        return np.clip(np.nan_to_num(np.concatenate(res), nan=1e4), -1e4, 1e4)

    rng = np.random.default_rng(seed)
    best = None
    for attempt in range(restarts):
        start = x0 if attempt == 0 else x0 + rng.normal(0, 0.3, size=x0.size) * np.maximum(np.abs(x0), 0.5)
        try:
            sol = least_squares(residuals, start, loss='soft_l1', f_scale=2.0, x_scale='jac', max_nfev=400)
        except (OverflowError, ValueError, FloatingPointError):
            continue
        if best is None or sol.cost < best.cost:
            best = sol
    fitted = {n: to_natural(n, v) for n, v in zip(names, best.x)}
    return params_for(modules, fitted), best.cost


def evaluate(params, runs, train_end, sigma):
    rows = {}
    for label, sl in (('train', slice(0, train_end)), ('valid', slice(train_end, None))):
        preds = np.concatenate([rollout(params, r)[sl] for r in runs])
        obs = np.concatenate([r['obs'][sl] for r in runs])
        if len(obs) == 0:
            continue
        rows[label] = {'rmse': np.sqrt(((preds - obs) ** 2).mean(axis=0)), 'score': score(preds, obs, sigma)}
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data', nargs='+')
    parser.add_argument('--train-end', type=int, default=450)
    parser.add_argument('--variants', default='base,m1,m2,m3,m12,m13,m23,m123')
    parser.add_argument('--extras', default='hump', help='comma list of non-mechanism modules: hump, withdraw')
    parser.add_argument('--restarts', type=int, default=4)
    parser.add_argument('--out', type=Path, default=Path('fits/market'))
    args = parser.parse_args()
    runs = load_runs(args.data)
    obs_all = np.concatenate([r['obs'][20:] for r in runs])
    sigma = obs_all.std(axis=0)  # stand-in for the organizer's hidden sigma
    print('sigma stand-in (std after tick 20):', dict(zip(NAMES, sigma.round(3))))
    persist = np.concatenate([np.tile([r['initial'][n] for n in NAMES], (len(r['obs']), 1))[args.train_end:] for r in runs])
    obs_valid = np.concatenate([r['obs'][args.train_end:] for r in runs])
    if len(obs_valid):
        print('persistence valid score:', dict(zip(NAMES, score(persist, obs_valid, sigma).round(3))))
    args.out.mkdir(parents=True, exist_ok=True)
    for variant in args.variants.split(','):
        modules = set() if variant == 'base' else {f'm{c}' for c in variant[1:]}
        modules |= {m for m in args.extras.split(',') if m}
        started = time.time()
        params, cost = fit_variant(modules, runs, args.train_end, args.restarts)
        rows = evaluate(params, runs, args.train_end, sigma)
        line = f'{variant:5s} {args.extras:14s} cost {cost:10.1f} ({time.time() - started:5.0f}s)'
        for label, row in rows.items():
            line += f" | {label} rmse {np.round(row['rmse'], 3)} score {row['score'].mean():.4f}"
        print(line, flush=True)
        (args.out / f"{variant}_{args.extras.replace(',', '+') or 'none'}_train{args.train_end}.json").write_text(json.dumps(
            {'modules': sorted(modules), 'train_end': args.train_end, 'cost': cost, 'params': params}, indent=1))
