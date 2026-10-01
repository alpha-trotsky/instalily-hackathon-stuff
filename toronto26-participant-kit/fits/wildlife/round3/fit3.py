"""Round-3 wildlife fitter + held-out scorer (free, no steps). Copy of fits/wildlife/round2/v2/fitv2.py with:
  * R4c (R4 continued, ticks 350-499) available as a run; never train on R4 and R4c together (shared prefix);
  * scores use fits/round3/heldout3.py sigma (0.1 x std after tick 20 of ALL data incl. round 3);
  * R4c as a TEST run is scored on ticks 350+ only (as heldout3.py); as a train run it is scored in full.
Run from toronto26-participant-kit/:
    python fits/wildlife/round3/fit3.py --model greybox/wildlife_model_v2.py --train R1 R2c R3 R4c \
        --init fits/wildlife/round2/v2/C_v2.json --out fits/wildlife/round3/C_v2r.json
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round3')
import heldout3
from greybox.common import core, fit as gfit

RUNS = {'R1': 'data/wildlife/R1.json', 'R2c': 'data/wildlife/R2c.json', 'R3': 'data/wildlife/R3.json',
        'R4': 'data/wildlife/R4.json', 'R4c': 'data/wildlife/R4c.json'}
NAMES = ['prey_north', 'predator_north', 'prey_south', 'predator_south']
RAWCLIP = 6.0


def sig3():
    names, s = heldout3.sigma('wildlife')
    return np.array([s[list(names).index(n)] for n in NAMES])


def episodes(model, runs):
    assert not ('R4' in runs and 'R4c' in runs), 'R4 and R4c share ticks 0-349'
    eps = core.load_episodes([RUNS[r] for r in runs], names=NAMES, model=model)
    for ep, r in zip(eps, runs):
        ep['tag'] = r
    return eps


def score_runs(model, params, runs, test=False):
    sig = sig3()
    out = {}
    for ep in episodes(model, runs):
        p = core.rollout(model, params, ep)
        t0 = 350 if (test and ep['tag'] == 'R4c') else 0
        s = (1 / (1 + np.abs(p - ep['obs']) / sig))[t0:].mean(0)
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
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--nfev', type=int, default=300)
    ap.add_argument('--perturb', type=float, default=0.1)
    ap.add_argument('--no-clip', action='store_true')
    ap.add_argument('--score-only', action='store_true', help='no fit: score --init params on --train/--test')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    model = core.load_model(a.model)
    modules = {m for m in a.modules.split(',') if m}
    init = {n: v for n, (v, _) in model.SPEC.items()}
    if a.init:
        init.update({k: v for k, v in json.loads(Path(a.init).read_text())['params'].items() if k in model.SPEC})
    init.update(json.loads(a.override))
    t0 = time.time()
    if a.score_only:
        res = {'params': init, 'cost': float('nan'), 'model': a.model, 'init': a.init}
    else:
        if not a.no_clip:
            init = clip_init(model, init)
        eps = episodes(model, a.train)
        units = ['log'] * 4
        sigma = [0.01] * 4
        fixed = [f for f in a.fix.split(',') if f]
        if a.stage1:
            keep = set(a.stage1.split(','))
            allfree = core.free_names(model, modules, fixed)
            r1 = gfit.fit(model, eps, modules, units, sigma, restarts=1,
                          fixed=fixed + [n for n in allfree if n not in keep],
                          init=init, max_nfev=a.nfev, workers=1, perturb=a.perturb)
            print(f"stage1 cost {r1['cost']:.1f}", flush=True)
            init = r1['params']
        res = gfit.fit(model, eps, modules, units, sigma, restarts=a.restarts, fixed=fixed, init=init,
                       max_nfev=a.nfev, workers=a.workers, perturb=a.perturb)
    res['train_runs'], res['test_runs'] = a.train, a.test
    res['score_train'] = score_runs(model, res['params'], a.train)
    res['score_test'] = score_runs(model, res['params'], a.test, test=True) if a.test else {}
    res['wall_s'] = time.time() - t0
    core.write_json(Path(a.out), res)
    mt = lambda d: round(float(np.mean([np.mean(v) for v in d.values()])), 4) if d else None
    print(f"cost {res['cost']:.1f} train {res['score_train']} ({mt(res['score_train'])}) test {res['score_test']} "
          f"({mt(res['score_test'])}) {res['wall_s']:.0f}s -> {a.out}", flush=True)


if __name__ == '__main__':
    main()
