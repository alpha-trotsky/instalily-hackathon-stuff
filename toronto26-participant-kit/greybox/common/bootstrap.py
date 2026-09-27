"""Parametric bootstrap for pair selection (framework section 6.3), generalizing bootstrap_market.py.

For each fitted candidate (the "truth"): simulate it on the real schedules and initial readings, add
circular-block-resampled real residuals (in the model's residual units: log or linear per observable;
block 50, the first 20 ticks of each episode excluded from the pool), refit EVERY candidate on the
synthetic data with the same procedure (modules, units, sigma, window, horizons as its fit JSON) and
record which one has the lowest cost. Output: confusion matrix, winning margins, real-data comparison.

    python -m greybox.common.bootstrap --fits fits/sys/m12.json fits/sys/m13.json fits/sys/m23.json \
        [--draws 3] [--restarts 2] [--workers 7] [--out fits/sys/bootstrap.json]

Fit JSONs written by greybox.common.fit carry model/units/noise/data; for older files pass --model,
--units, --noise and --data explicitly. Labels are the fit file stems.
"""
import argparse
import json
import os
from multiprocessing import get_context
from pathlib import Path
import numpy as np

from greybox.common import core
from greybox.common.fit import fit, parse_value_arg


def block_resample(residuals, block, rng, skip=20):
    """Circular block bootstrap of residual rows (T x n), skipping the reset transient."""
    pool = residuals[skip:] if len(residuals) > skip + block else residuals
    starts = rng.integers(0, len(pool), size=len(residuals) // block + 1)
    idx = np.concatenate([(s + np.arange(block)) % len(pool) for s in starts])[:len(residuals)]
    return pool[idx]


def load_candidate(path, defaults):
    data = json.loads(Path(path).read_text())
    return {'label': Path(path).stem, 'path': str(path), 'params': data['params'], 'modules': data['modules'],
            'cost': data.get('cost'), 'model': data.get('model') or defaults['model'],
            'units': data.get('units') or defaults['units'], 'noise': data.get('noise') or defaults['noise'],
            'train_end': data.get('train_end'), 'horizons': data.get('horizons', []), 'skip': data.get('skip', 0),
            'data': defaults['data'] or [d for d in data.get('data', [])]}


def _data_args(entries):
    """['path:0', 'path:1'] -> ['path:0,1'] so every run is loaded once, in order."""
    grouped = {}
    for entry in entries:
        path, runs = core.split_data_arg(entry)
        grouped.setdefault(path, set()).update(runs if runs is not None else {None})
    return [p if None in r else f"{p}:{','.join(map(str, sorted(r)))}" for p, r in grouped.items()]


def job(task):
    truth, draw, candidates, block, skip, restarts = task
    model = core.load_model(truth['model'])
    episodes = core.load_episodes(_data_args(truth['data']), model=model)
    names = episodes[0]['names']
    units, sigma = core.resolve_units_noise(model, names, episodes, truth['units'], truth['noise'])
    rng = np.random.default_rng(1000 * draw + sum(map(ord, truth['label'])))
    synthetic = []
    for ep in episodes:
        clean = core.to_units(core.rollout(model, truth['params'], ep), units)
        resid = core.to_units(ep['obs'], units) - clean
        resid = np.where(np.isfinite(resid), resid, 0.0)
        synthetic.append({**ep, 'obs': core.from_units(clean + block_resample(resid, block, rng, skip), units)})
    costs = {}
    for cand in candidates:
        cmodel = core.load_model(cand['model'])
        cu, cs = core.resolve_units_noise(cmodel, names, episodes, cand['units'], cand['noise'])
        eps = [{**ep, 'u': [cmodel.normalize(a, ep['bounds']) for a in ep['actions']]} for ep in synthetic]
        res = fit(cmodel, eps, set(cand['modules']), cu, cs, restarts=restarts, horizons=cand['horizons'],
                  train_end=cand['train_end'], seed=draw, workers=1, skip=cand['skip'], verbose=False,
                  init=cand['params'] if cand.get('warm') else None)
        costs[cand['label']] = res['cost']
    return {'truth': truth['label'], 'draw': draw, 'costs': costs, 'selected': min(costs, key=costs.get)}


def summarize(results, labels, real_costs):
    confusion = {t: {c: sum(r['truth'] == t and r['selected'] == c for r in results) for c in labels} for t in labels}
    margins = {t: [] for t in labels}
    for r in results:
        ordered = sorted(r['costs'].values())
        if r['selected'] == r['truth'] and len(ordered) > 1:
            margins[r['truth']].append(ordered[1] - ordered[0])
    out = {'confusion': confusion, 'margins': margins,
           'row_accuracy': {t: confusion[t][t] / max(sum(confusion[t].values()), 1) for t in labels}}
    if all(real_costs.get(l) is not None for l in labels):
        ordered = sorted(labels, key=lambda l: real_costs[l])
        winner, margin = ordered[0], real_costs[ordered[1]] - real_costs[ordered[0]] if len(labels) > 1 else None
        out.update(real_costs=real_costs, real_winner=winner, real_margin=margin,
                   min_bootstrap_margin_winner=min(margins[winner]) if margins[winner] else None)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='Parametric bootstrap confusion matrix for candidate models.')
    ap.add_argument('--fits', nargs='+', required=True, help='fit JSONs of the candidates (e.g. m12, m13, m23)')
    ap.add_argument('--data', nargs='*', help='override data files (default: those recorded in each fit)')
    ap.add_argument('--model', help='default model for fit files that do not record one')
    ap.add_argument('--units')
    ap.add_argument('--noise')
    ap.add_argument('--draws', type=int, default=3)
    ap.add_argument('--block', type=int, default=50)
    ap.add_argument('--skip', type=int, default=20)
    ap.add_argument('--restarts', type=int, default=2)
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--warm', action='store_true', help='start every refit from the real-data params of its candidate')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    defaults = {'model': args.model, 'units': parse_value_arg(args.units), 'noise': parse_value_arg(args.noise),
                'data': args.data}
    candidates = [{**load_candidate(f, defaults), 'warm': args.warm} for f in args.fits]
    labels = [c['label'] for c in candidates]
    tasks = [(t, d, candidates, args.block, args.skip, args.restarts) for d in range(args.draws) for t in candidates]
    results = []
    with get_context('spawn').Pool(min(args.workers, len(tasks))) as pool:
        for result in pool.imap_unordered(job, tasks):
            results.append(result)
            core.write_json(args.out, {'results': results})
            print(result['truth'], result['draw'], 'selected', result['selected'],
                  {k: round(v, 1) for k, v in result['costs'].items()}, flush=True)
    summary = summarize(results, labels, {c['label']: c['cost'] for c in candidates})
    core.write_json(args.out, {'results': results, 'summary': summary, 'settings': vars(args)})
    print('\nconfusion (rows: truth, columns: selected)')
    print(' ' * 24 + ' '.join(f'{c[:10]:>10s}' for c in labels))
    for t in labels:
        print(f'{t[:22]:>22s}  ' + ' '.join(f'{summary["confusion"][t][c]:10d}' for c in labels))
    print(json.dumps({k: v for k, v in summary.items() if k != 'confusion'}, default=core._json_default))


if __name__ == '__main__':
    main()
