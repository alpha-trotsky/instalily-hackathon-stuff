"""Round-2 v2 fitting driver: fit on --train runs, score (sigma = 0.1 x std after tick 20 of ALL power_grid data,
same as fits/round2/heldout.py) on --test runs.  Runs are names like R1, R2c, R3, R4 (data/power_grid/<name>.json).

  python3 fits/power_grid/round2/v2_fit.py --model greybox/power_grid_model_v2.py --modules m1,m3 \
      --train R1 R2c --test R3 R4 --out fits/power_grid/round2/v2_A.json [--init fit.json] [--fix a,b]
  python3 fits/power_grid/round2/v2_fit.py --score-only fit.json --test R3 R4
"""
import argparse, json, sys, os
sys.path.insert(0, '.')
import numpy as np
from greybox.common import core, fit as F
from fits.round2.heldout import sigma

NAMES = ['load', 'frequency', 'renewable_share']
_, SIG = sigma('power_grid')


def eps(names, model):
    return core.load_episodes([f'data/power_grid/{r}.json' for r in names], names=NAMES, model=model)


def score(model, params, runs):
    out = {}
    for r in runs:
        ep = eps([r], model)[0]
        pred = core.rollout(model, params, ep)
        lo = np.array([model.CLAMP[n][0] for n in NAMES]); hi = np.array([model.CLAMP[n][1] for n in NAMES])
        pred = np.clip(pred, lo, hi)
        out[r] = (1 / (1 + np.abs(pred - ep['obs']) / SIG)).mean(0).round(4).tolist()
    return out


def report(model, params, runs, label=''):
    sc = score(model, params, runs)
    for r, v in sc.items():
        print(f'  {label}{r}: load {v[0]:.3f} f {v[1]:.3f} share {v[2]:.3f}  mean {np.mean(v):.4f}')
    if sc:
        print(f'  {label}mean over runs: {np.mean([np.mean(v) for v in sc.values()]):.4f}')
    return sc


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='greybox/power_grid_model_v2.py')
    ap.add_argument('--modules', default='m1,m3')
    ap.add_argument('--train', nargs='*', default=[])
    ap.add_argument('--test', nargs='*', default=[])
    ap.add_argument('--init'); ap.add_argument('--fix', default='')
    ap.add_argument('--restarts', type=int, default=2); ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--max-nfev', type=int, default=300); ap.add_argument('--perturb', type=float, default=0.1)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out'); ap.add_argument('--score-only')
    a = ap.parse_args()
    if a.score_only:
        res = json.load(open(a.score_only)); model = core.load_model(res['model'])
        report(model, res['params'], a.test or ['R1', 'R2c', 'R3', 'R4']); sys.exit()
    model = core.load_model(a.model)
    tr = eps(a.train, model)
    units = [model.UNITS[n] for n in NAMES]; sig = [model.NOISE[n] for n in NAMES]
    init = json.load(open(a.init))['params'] if a.init else None
    if init:
        init = {k: v for k, v in init.items() if k in model.SPEC}
    fixed = [x for x in a.fix.split(',') if x]
    res = F.fit(model, tr, a.modules.split(',') if a.modules else [], units, sig, restarts=a.restarts, fixed=fixed,
                init=init, max_nfev=a.max_nfev, seed=a.seed, workers=a.workers, perturb=a.perturb)
    res['train_runs'] = a.train; res['test_runs'] = a.test
    print('cost', round(res['cost'], 1), 'restarts', [round(c, 1) for c in res['restart_costs']])
    res['train_score'] = report(model, res['params'], a.train, 'train ')
    res['test_score'] = report(model, res['params'], a.test, 'TEST ')
    if a.out:
        core.write_json(a.out, res)
