"""Score fit JSONs on social_contagion runs with the round-3 heldout3 sigma (0.1 x std after tick 20 of R1-R6).

    python fits/social_contagion/round3/ev3.py FIT.json [...] [--runs R6] [--model greybox/...py] [--levels]
"""
import argparse, json, sys, os
import numpy as np
sys.path.insert(0, os.getcwd())
from greybox.common import core
sys.path.insert(0, 'fits/round3')
import heldout3

S = 'social_contagion'
NAMES, SIG = heldout3.sigma(S)
CTX = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
BOUNDS = {k: tuple(v) for k, v in CTX['intervention_bounds'].items()}
KEY = {'R4': [(90, 100, 'u.7'), (140, 150, 'crash'), (390, 400, 'tail'), (530, 540, 'P3')],
       'R5': [(70, 80, 's4.5'), (130, 140, 'inc2'), (180, 190, 'inc1'), (230, 240, 'inc0'), (310, 320, 'rec')],
       'R6': [(50, 60, 'noinc'), (90, 100, 'pk'), (110, 120, 'inc')],
       'R1': [(180, 190, 's9'), (395, 405, 'floor')], 'R2': [(245, 255, 'pulse'), (295, 305, 'floor')], 'R3': []}


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
    ap.add_argument('--runs', nargs='+', default=['R1', 'R2', 'R3', 'R4', 'R5', 'R6'])
    ap.add_argument('--model')
    ap.add_argument('--levels', action='store_true')
    a = ap.parse_args()
    for f in a.fits:
        fj = json.load(open(f))
        model = core.load_model(a.model or fj['model'])
        res = score_fit(model, fj['params'], a.runs)
        line = ' '.join(f'{r} {v[0][0]:.3f}/{v[0][1]:.3f}' for r, v in res.items())
        print(f'{os.path.basename(f):24s} cost {fj.get("cost", 0):8.0f} | {line} | bounds {model.at_bounds(fj["params"])}')
        if a.levels:
            for r, v in res.items():
                if v[1]:
                    print('    ', r, ' '.join(f'{k}: {m[0]:.0f}/{m[1]:.0f} (d {o[0]:.0f}/{o[1]:.0f})' for k, (m, o) in v[1].items()))
