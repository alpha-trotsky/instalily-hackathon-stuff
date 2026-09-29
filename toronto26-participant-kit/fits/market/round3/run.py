"""Round-3 market: fit a module set on a fold of A,B,C,D and score held-out runs.
sigma = heldout3 sigma (0.1 x std after tick 20 of A+B+C+D) = 0.8376 / 0.0376 / 2.4185.

    python fits/market/round3/run.py MODEL VARIANT FOLD [--init FIT] [--restarts 1] [--nfev 300] [--tag x]
MODEL: v2 | v3. FOLD: letters of the training runs, e.g. ABC (H: -> D), ABD (B: -> C), ACD (B: -> B), ABCD (final).
Held-out runs are every run of A-D not in the fold.
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core, fit as gfit

OUT = Path('fits/market/round3')
MODELS = {'v2': 'greybox/market_model_v2.py', 'v3': 'greybox/market_model_v3.py'}
V2 = ['m1', 'm2', 'withdraw', 'conv', 'gate', 'dmap', 'm2mult', 'inv', 'jx', 'vjx', 'vfl']
VARIANTS = {'full': V2, 'v3': V2 + ['rz', 'zdm', 'klin', 'wx', 'tz', 'kfl', 'kmin']}
for _m in ['rz', 'zdm', 'klin', 'wx', 'tz', 'kfl', 'kmin']:
    VARIANTS['v3-' + _m] = [x for x in VARIANTS['v3'] if x != _m]
FILES = {r: f'data/market/{r}.json' for r in 'ABCD'}
NAMES = ['price', 'volume', 'depth']
SIG = np.array([0.8376, 0.0376, 2.4185])


def score_runs(model, params, runs):
    res = {}
    for r in runs:
        ep = core.load_episodes([FILES[r]], names=NAMES, model=model)[0]
        pred = core.rollout(model, params, ep)
        res[r] = (1 / (1 + np.abs(pred - ep['obs']) / SIG)).mean(0).round(4).tolist()
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('model'); ap.add_argument('variant'); ap.add_argument('fold')
    ap.add_argument('--restarts', type=int, default=1); ap.add_argument('--nfev', type=int, default=300)
    ap.add_argument('--init', default='fits/market/round2/v2/full_ABC_s3.json')
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    model = core.load_model(MODELS[a.model])
    mods = VARIANTS.get(a.variant) or a.variant.split(',')
    train = list(a.fold); test = [r for r in 'ABCD' if r not in train]
    eps = core.load_episodes([FILES[r] for r in train], names=NAMES, model=model)
    init = json.load(open(a.init))['params']
    t = time.time()
    res = gfit.fit(model, eps, mods, ['log'] * 3, [0.004] * 3, restarts=a.restarts, init=init,
                   max_nfev=a.nfev, workers=a.workers, verbose=False)
    out = {'model': MODELS[a.model], 'variant': a.variant, 'fold': a.fold, 'modules': mods, 'cost': res['cost'],
           'restart_costs': res['restart_costs'], 'time_s': time.time() - t, 'init': a.init,
           'train_scores': score_runs(model, res['params'], train),
           'heldout_scores': score_runs(model, res['params'], test), 'params': res['params']}
    name = f"{a.model}_{a.variant.replace(',', '+')}_{a.fold}{a.tag}.json"
    (OUT / name).write_text(json.dumps(out, indent=1))
    ho = out['heldout_scores']
    hm = np.mean([np.mean(v) for v in ho.values()]) if ho else float('nan')
    print(f"{a.model} {a.variant:10s} {a.fold:4s} cost {res['cost']:9.1f} {out['time_s']:5.0f}s "
          f"train {out['train_scores']} heldout {ho} mean {hm:.4f}", flush=True)
