"""Score fit JSONs on runs with the heldout.py sigma (0.1 x std after tick 20 of all R1-R5 data).

    python3 fits/social_contagion/round2/v2/ev.py FIT.json [FIT2.json ...] [--runs R4 R5] [--model greybox/...py]
Prints per-run per-observable scores and key levels.
"""
import argparse, json, sys, os
import numpy as np
sys.path.insert(0, os.getcwd())
from greybox.common import core
sys.path.insert(0, 'fits/round2')
import heldout

S = 'social_contagion'
NAMES, SIG = heldout.sigma(S)
CTX = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
BOUNDS = {k: tuple(v) for k, v in CTX['interventions'].items()} if 'interventions' in CTX else {}

KEY = {'R4': [(90, 100, 'u.7'), (140, 150, 'crash'), (390, 400, 'tail'), (530, 540, 'P3')],
       'R5': [(70, 80, 's4.5'), (130, 140, 'inc2'), (180, 190, 'inc1'), (230, 240, 'inc0'), (310, 320, 'rec')],
       'R1': [(180, 190, 's9'), (395, 405, 'floor')], 'R2': [(245, 255, 'pulse'), (295, 305, 'floor')], 'R3': []}


def load_model(path):
    return core.load_model(path)


def score_fit(model, params, runs):
    out = {}
    for r in runs:
        d = json.load(open(f'data/{S}/{r}.json'))
        for run in d['runs']:
            o = np.array([[x[n] for n in NAMES] for x in run['observations']])
            u = [model.normalize(a, BOUNDS) for a in run['actions']]
            p = np.asarray(model.simulate(params, run['initial'], u))
            sc = (1 / (1 + np.abs(p - o) / SIG)).mean(0)
            lv = {lab: (p[a:b].mean(0).round(0).tolist(), o[a:b].mean(0).round(0).tolist()) for a, b, lab in KEY.get(r, [])}
            out[r] = (sc.round(3).tolist(), lv)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('fits', nargs='+')
    ap.add_argument('--runs', nargs='+', default=['R1', 'R2', 'R3', 'R4', 'R5'])
    ap.add_argument('--model')
    ap.add_argument('--levels', action='store_true')
    a = ap.parse_args()
    for f in a.fits:
        fj = json.load(open(f))
        model = load_model(a.model or fj['model'])
        res = score_fit(model, fj['params'], a.runs)
        line = ' '.join(f'{r} {v[0][0]:.3f}/{v[0][1]:.3f}' for r, v in res.items())
        print(f'{os.path.basename(f):28s} cost {fj.get("cost", 0):9.1f} | {line} | at_bounds {model.at_bounds(fj["params"]) if hasattr(model, "at_bounds") else ""}')
        if a.levels:
            for r, v in res.items():
                if v[1]:
                    print('    ', r, ' '.join(f'{k}: {m[0]:.0f}/{m[1]:.0f} (d {o[0]:.0f}/{o[1]:.0f})' for k, (m, o) in v[1].items()))
