"""Round-2 wildlife fitter + honest held-out scorer (free, no steps). Run from toronto26-participant-kit/:

    python3 fits/wildlife/round2/v2/fitv2.py --model greybox/wildlife_model_v2.py --train R1 R2c --test R3 R4 \
        --init fits/wildlife/final.json --out fits/wildlife/round2/v2/A_v2.json

Residuals: log units, noise 0.01 (as v1's final fit), soft_l1. Score: sigma = 0.1 x std after tick 20 of ALL wildlife
data (fits/round2/heldout.py), per run and observable. Pinned raw init values are clipped to +-RAWCLIP so they can move.
--stage1 NAMES fits only those names first (others frozen at init), then everything.
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round2')
import heldout
from greybox.common import core, fit as gfit

RUNS = {'R1': 'data/wildlife/R1.json', 'R2c': 'data/wildlife/R2c.json', 'R3': 'data/wildlife/R3.json',
        'R4': 'data/wildlife/R4.json'}
NAMES = ['prey_north', 'predator_north', 'prey_south', 'predator_south']
RAWCLIP = 6.0   # applied only to clearly pinned raw values (|raw| > 8)


def episodes(model, runs):
    eps = core.load_episodes([RUNS[r] for r in runs], names=NAMES, model=model)
    for ep, r in zip(eps, runs):
        ep['tag'] = r
    return eps


def score_runs(model, params, runs):
    _, sig = heldout.sigma('wildlife')
    out = {}
    for ep in episodes(model, runs):
        p = core.rollout(model, params, ep)
        s = (1 / (1 + np.abs(p - ep['obs']) / sig)).mean(0)
        out[ep['tag']] = [round(float(v), 4) for v in s]
    return out


def clip_init(model, params):
    out = dict(params)
    for n in model.SPEC:
        if n in out:
            raw = model.to_raw(n, out[n])
            if abs(raw) > 8.0 and model.SPEC[n][1] != 'pos':
                out[n] = model.to_natural(n, float(np.clip(raw, -RAWCLIP, RAWCLIP)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--train', nargs='+', required=True)
    ap.add_argument('--test', nargs='*', default=[])
    ap.add_argument('--init')
    ap.add_argument('--override', default='{}', help='JSON dict of natural values applied on top of init')
    ap.add_argument('--modules', default='mA,mB')
    ap.add_argument('--fix', default='')
    ap.add_argument('--stage1', default='')
    ap.add_argument('--restarts', type=int, default=2)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--nfev', type=int, default=300)
    ap.add_argument('--perturb', type=float, default=0.1)
    ap.add_argument('--no-clip', action='store_true')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    model = core.load_model(a.model)
    modules = {m for m in a.modules.split(',') if m}
    init = {n: v for n, (v, _) in model.SPEC.items()}
    if a.init:
        init.update({k: v for k, v in json.loads(Path(a.init).read_text())['params'].items() if k in model.SPEC})
    init.update(json.loads(a.override))
    if not a.no_clip:
        init = clip_init(model, init)
    eps = episodes(model, a.train)
    units = ['log'] * 4
    sigma = [0.01] * 4
    fixed = [f for f in a.fix.split(',') if f]
    t0 = time.time()
    if a.stage1:
        keep = set(a.stage1.split(','))
        allfree = core.free_names(model, modules, fixed)
        r1 = gfit.fit(model, eps, modules, units, sigma, restarts=1, fixed=fixed + [n for n in allfree if n not in keep],
                      init=init, max_nfev=a.nfev, workers=1, perturb=a.perturb)
        print(f"stage1 cost {r1['cost']:.1f}", flush=True)
        init = r1['params']
    res = gfit.fit(model, eps, modules, units, sigma, restarts=a.restarts, fixed=fixed, init=init, max_nfev=a.nfev,
                   workers=a.workers, perturb=a.perturb)
    res['train_runs'], res['test_runs'] = a.train, a.test
    res['score_train'] = score_runs(model, res['params'], a.train)
    res['score_test'] = score_runs(model, res['params'], a.test) if a.test else {}
    res['wall_s'] = time.time() - t0
    core.write_json(Path(a.out), res)
    mt = lambda d: round(float(np.mean([np.mean(v) for v in d.values()])), 4) if d else None
    print(f"cost {res['cost']:.1f} train {res['score_train']} ({mt(res['score_train'])}) test {res['score_test']} "
          f"({mt(res['score_test'])}) {res['wall_s']:.0f}s -> {a.out}", flush=True)


if __name__ == '__main__':
    main()
