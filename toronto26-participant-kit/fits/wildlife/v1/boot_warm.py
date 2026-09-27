"""Warm-started parametric bootstrap (epidemic lesson: cold-start refits do not converge).

Same synthetic data as greybox.common.bootstrap (block-resampled real log residuals), but every candidate
refit starts from that candidate's real-data fit (init = its params), 1 restart, capped nfev.
Run from the kit:  python fits/wildlife/v1/boot_warm.py --fits a.json b.json c.json --draws 3 --out x.json
"""
import argparse
import json
import sys
import time
from multiprocessing import get_context
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from greybox.common import core                      # noqa: E402
from greybox.common.fit import fit                   # noqa: E402
from greybox.common.bootstrap import block_resample, load_candidate, _data_args, summarize   # noqa: E402

MAX_NFEV = 120


def job(task):
    truth, draw, candidates, block, skip = task
    t0 = time.time()
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
        res = fit(cmodel, eps, set(cand['modules']), cu, cs, restarts=1, init=cand['params'],
                  train_end=cand['train_end'], seed=draw, workers=1, skip=cand['skip'], verbose=False,
                  max_nfev=MAX_NFEV)
        costs[cand['label']] = res['cost']
    return {'truth': truth['label'], 'draw': draw, 'costs': costs, 'selected': min(costs, key=costs.get),
            'time_s': time.time() - t0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fits', nargs='+', required=True)
    ap.add_argument('--draws', type=int, default=3)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    defaults = {'model': None, 'units': None, 'noise': None, 'data': None}
    candidates = [load_candidate(f, defaults) for f in args.fits]
    labels = [c['label'] for c in candidates]
    tasks = [(t, d, candidates, 50, 20) for d in range(args.draws) for t in candidates]
    results = []
    with get_context('spawn').Pool(min(args.workers, len(tasks))) as pool:
        for r in pool.imap_unordered(job, tasks):
            results.append(r)
            core.write_json(args.out, {'results': results})
            print(r['truth'], r['draw'], 'selected', r['selected'], {k: round(v, 1) for k, v in r['costs'].items()},
                  f"{r['time_s']:.0f}s", flush=True)
    summary = summarize(results, labels, {c['label']: c['cost'] for c in candidates})
    core.write_json(args.out, {'results': results, 'summary': summary, 'settings': vars(args),
                               'note': f'warm start from each candidate fit, 1 restart, max_nfev {MAX_NFEV}'})
    print('confusion (rows truth, cols selected)', labels)
    for t in labels:
        print(t, [summary['confusion'][t][c] for c in labels])
    print(json.dumps({k: v for k, v in summary.items() if k != 'confusion'}, default=core._json_default))


if __name__ == '__main__':
    main()
