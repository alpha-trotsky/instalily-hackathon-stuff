"""Round-2 market v2: fit variants on folds and score held-out runs (sigma = 0.1 x std after tick 20 of A+B+C).

    python3 fits/market/round2/v2/run.py VARIANT FOLD [--restarts 2] [--nfev 300]
FOLD: A (fit A -> score B,C), AB (-> C), AC (-> B), ABC (final, in-sample)
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core, fit as gfit

OUT = Path('fits/market/round2/v2')
MODEL = 'greybox/market_model_v2.py'
BASE = ['m1', 'm2', 'withdraw']
VARIANTS = {
    'v1s': BASE,
    'full': BASE + ['conv', 'gate', 'dmap', 'm2mult', 'inv', 'jx', 'vjx', 'vfl'],
}
for m in ['conv', 'gate', 'dmap', 'm2mult', 'inv', 'jx', 'vjx', 'vfl']:
    VARIANTS['full-' + m] = [x for x in VARIANTS['full'] if x != m]
    VARIANTS['v1s+' + m] = BASE + [m]
FILES = {r: f'data/market/{r}.json' for r in 'ABC'}
NAMES = ['price', 'volume', 'depth']


def sigma():
    eps = core.load_episodes(FILES.values(), names=NAMES)
    return 0.1 * np.concatenate([e['obs'][20:] for e in eps]).std(0)


def score_runs(model, params, runs):
    sig = sigma(); res = {}
    for r in runs:
        ep = core.load_episodes([FILES[r]], names=NAMES, model=model)[0]
        pred = core.rollout(model, params, ep)
        res[r] = (1 / (1 + np.abs(pred - ep['obs']) / sig)).mean(0).round(4).tolist()
    return res


def variant_modules(name):
    if name in VARIANTS:
        return VARIANTS[name]
    return name.split(',')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('variant'); ap.add_argument('fold')
    ap.add_argument('--restarts', type=int, default=2); ap.add_argument('--nfev', type=int, default=300)
    ap.add_argument('--init', default='fits/market/m12_withdraw_train600.json')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    model = core.load_model(MODEL)
    mods = variant_modules(a.variant)
    train = list(a.fold); test = [r for r in 'BC' if r not in train]
    eps = core.load_episodes([FILES[r] for r in train], names=NAMES, model=model)
    init = json.load(open(a.init))['params']
    t = time.time()
    res = gfit.fit(model, eps, mods, ['log'] * 3, [0.004] * 3, restarts=a.restarts, init=init,
                   max_nfev=a.nfev, workers=a.workers, verbose=False)
    out = {'variant': a.variant, 'fold': a.fold, 'modules': mods, 'cost': res['cost'],
           'restart_costs': res['restart_costs'], 'time_s': time.time() - t,
           'train_scores': score_runs(model, res['params'], train),
           'heldout_scores': score_runs(model, res['params'], test), 'params': res['params']}
    name = f"{a.variant.replace(',', '+')}_{a.fold}{a.tag}.json"
    (OUT / name).write_text(json.dumps(out, indent=1))
    ho = out['heldout_scores']
    hm = np.mean([np.mean(v) for v in ho.values()]) if ho else float('nan')
    print(f"{a.variant:14s} {a.fold:4s} cost {res['cost']:9.1f} {out['time_s']:5.0f}s train {out['train_scores']} "
          f"heldout {ho} mean {hm:.4f}", flush=True)
