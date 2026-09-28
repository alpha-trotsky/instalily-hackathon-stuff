"""Decision rules of round2-experiments.md §4.2 measured on R3/R4 and compared with the four candidates, each run
from the run's actual initial reading and actions. Also scores each candidate on R3/R4 (held-out) and on old data.
    python3 fits/wildlife/round2/rules.py"""
import json, sys
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round2')
from greybox.common import core
import heldout

names, sig = heldout.sigma('wildlife')
model = core.load_model('greybox/wildlife_model.py')
B = 'fits/wildlife/v1/'
FITS = {'AB_all3(v1)': B + 'AB_all3.json', 'AC_all': B + 'AC_all.json', 'BC_all2': B + 'BC_all2.json', 'base_all': B + 'base_all.json'}
bounds = {'hunting_quota': (0, 8), 'habitat_protection': (0, 1), 'corridor_access': (0, 1)}

def pred(f, run):
    p = json.load(open(f)); p = p.get('params', p)
    u = [model.normalize(a, bounds) for a in run['actions']]
    return core.rollout(model, p, {'u': u, 'initial': run['initial'], 'names': names})

runs = {r: json.load(open(f'data/wildlife/{r}.json'))['runs'][0] for r in ['R1', 'R2c', 'R3', 'R4']}
obs = {r: np.array([[x[n] for n in names] for x in runs[r]['observations']]) for r in runs}
P = {k: {r: pred(f, runs[r]) for r in runs} for k, f in FITS.items()}

def L10(a, s, e): return a[e - 10:e].mean(0)
print('sigma', sig.round(4))
print('\n== held-out/in-sample scores (mean over 4 obs; per obs)')
for k in FITS:
    row = []
    for r in runs:
        sc = (1 / (1 + np.abs(P[k][r] - obs[r]) / sig)).mean(0)
        row.append(f'{r} {sc.mean():.3f} {sc.round(2).tolist()}')
    print(k, ' | '.join(row))

rules = [('joint .85 prey N', 'R3', 0, 80, 0), ('joint .7 prey N', 'R3', 290, 350, 0), ('hunt5+hab.37 prey N', 'R4', 80, 140, 0),
         ('release +30 (joint .85) prey N', 'R3', 80, 110, 0), ('release +30 (joint .85) prey S', 'R3', 80, 110, 2),
         ('release +30 (joint .7) prey N', 'R3', 350, 380, 0), ('release +30 (joint .7) prey S', 'R3', 350, 380, 2),
         ('short gap 30 prey S', 'R3', 260, 290, 2), ('short gap 30 prey N', 'R3', 260, 290, 0),
         ('release +150 pred N', 'R3', 350, 500, 1), ('release +150 pred S', 'R3', 350, 500, 3),
         ('release +120 pred N', 'R3', 80, 200, 1), ('release +120 pred S', 'R3', 80, 200, 3)]
print('\n== decision-rule quantities (mean of last 10 ticks); candidate value and (cand-obs)/sigma')
for lab, r, s, e, i in rules:
    o = L10(obs[r], s, e)[i]
    cells = ' | '.join(f'{k.split("(")[0]} {L10(P[k][r], s, e)[i]:.2f} ({(L10(P[k][r], s, e)[i]-o)/sig[i]:+.1f}σ)' for k in FITS)
    print(f'{lab:32s} obs {o:7.2f} | {cells}')
# release overshoot: peak within the release segment vs candidates
print('\n== release peaks (max over the release window)')
for lab, r, s, e in [('R3 release after joint .85', 'R3', 80, 200), ('R3 release after joint 1 (short gap)', 'R3', 260, 290),
                     ('R3 release after joint .7', 'R3', 350, 500), ('R4 release after hunt5+hab.37 (hab .37 kept)', 'R4', 140, 200),
                     ('R1 release after hunting 7', 'R1', 185, 250), ('R2c release after joint', 'R2c', 435, 460)]:
    for i in (0, 2):
        o = obs[r][s:e, i]
        cells = ' | '.join(f'{k.split("(")[0]} {P[k][r][s:e, i].max():.0f}@{s+int(P[k][r][s:e, i].argmax())}' for k in FITS)
        print(f'{lab:45s} {names[i]:10s} obs {o.max():.0f}@{s+int(o.argmax())} | {cells}')
json.dump({k: {r: v.tolist() for r, v in d.items()} for k, d in P.items()}, open('fits/wildlife/round2/cand_preds.json', 'w'))
