"""Parametric bootstrap: can our fitting procedure tell the mechanism pairs apart on Run A's schedule?

For each fitted pair (the "truth"), generate synthetic datasets on the exact real schedule and initial
reading. The noise added is block-resampled from that pair's real log residuals, so the synthetic data
keeps the size and autocorrelation of the real misfit, not only white measurement noise. Then refit every
candidate pair with the same procedure used on the real data and record which pair fits best.

    python greybox/bootstrap_market.py data/market/A.json --truths m12,m13,m23 --draws 5
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_market import fit_variant, load_runs, rollout

FITS = Path('fits/market')
EXTRAS = {'withdraw'}


def modules_for(variant):
    return {f'm{c}' for c in variant[1:]} | EXTRAS


def block_resample(residuals, block, rng, skip=20):
    """Circular block bootstrap of residual rows, skipping the reset transient's outsized residuals."""
    pool = residuals[skip:]
    starts = rng.integers(0, len(pool), size=len(residuals) // block + 1)
    idx = np.concatenate([(s + np.arange(block)) % len(pool) for s in starts])[:len(residuals)]
    return pool[idx]


def job(task):
    truth, draw, candidates, data_path, block, restarts = task
    run = load_runs([data_path])[0]
    params = json.loads((FITS / f'{truth}_withdraw_train600.json').read_text())['params']
    clean = rollout(params, run)
    residuals = np.log(run['obs']) - np.log(clean)
    rng = np.random.default_rng(1000 * draw + sum(map(ord, truth)))
    synthetic = dict(run, obs=clean * np.exp(block_resample(residuals, block, rng)))
    costs = {}
    for candidate in candidates:
        _, cost = fit_variant(modules_for(candidate), [synthetic], len(run['obs']), restarts, seed=draw)
        costs[candidate] = cost
    return {'truth': truth, 'draw': draw, 'costs': costs, 'selected': min(costs, key=costs.get)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('--truths', default='m12,m13,m23')
    parser.add_argument('--draws', type=int, default=5)
    parser.add_argument('--block', type=int, default=50)
    parser.add_argument('--restarts', type=int, default=2)
    parser.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument('--out', type=Path, default=FITS / 'bootstrap.json')
    args = parser.parse_args()
    truths = args.truths.split(',')
    tasks = [(t, d, truths, args.data, args.block, args.restarts) for d in range(args.draws) for t in truths]
    results = []
    with Pool(args.workers) as pool:
        for result in pool.imap_unordered(job, tasks):
            results.append(result)
            args.out.write_text(json.dumps(results, indent=1))
            print(result['truth'], result['draw'], 'selected', result['selected'],
                  {k: round(v, 1) for k, v in result['costs'].items()}, flush=True)
    print('\nconfusion (rows: truth, columns: selected)')
    print('       ' + ' '.join(f'{c:>5s}' for c in truths))
    for t in truths:
        row = [sum(r['truth'] == t and r['selected'] == c for r in results) for c in truths]
        print(f'{t:>6s} ' + ' '.join(f'{n:5d}' for n in row))
