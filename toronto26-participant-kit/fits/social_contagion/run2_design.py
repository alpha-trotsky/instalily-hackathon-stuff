"""Rank Run-2 candidate probes by disagreement between the three R1 pair fits (framework §4.4). Zero steps.

python fits/social_contagion/run2_design.py fits/social_contagion/m12_r1.json fits/social_contagion/m13_r1.json fits/social_contagion/m23_r1.json
"""
import json
import sys
import numpy as np
from greybox import social_contagion_model as m
from greybox.common import core

R1 = json.load(open('data/social_contagion/R1.json'))
BOUNDS = R1['brief']['interventions']
OBS = np.array([[o[k] for k in m.OBSERVABLES] for o in R1['runs'][0]['observations']])
SIG = 0.1 * OBS[20:].std(axis=0)
INIT = R1['runs'][0]['initial']


def act(s=0.0, i=0.0, b=0.0):
    return {'seeding': s, 'incentive': i, 'bridge_outreach': b}


def seg(n, **kw):
    return [act(**kw)] * n


def ramp(n, a, b):
    return [act(**{k: a.get(k, 0) + (j + 1) / n * (b.get(k, 0) - a.get(k, 0)) for k in ('s', 'i', 'b')}) for j in range(n)]


P0 = seg(30)
CANDS = {
    'A P7 full pulse (9,2,0.6) 200 + rec 60': seg(200, s=9, i=2, b=0.6) + seg(60),
    'A2 P7 full pulse 150 + rec 60': seg(150, s=9, i=2, b=0.6) + seg(60),
    'B P9b incentive before: inc 40, seed+inc 40, rec 40': seg(40, i=2) + seg(40, s=9, i=2) + seg(40),
    'C P9b incentive after: seed 40, inc 40, rec 40': seg(40, s=9) + seg(40, i=2) + seg(40),
    'D P5 seeding 30 on / 20 gap / 30 on + rec 40': seg(30, s=9) + seg(20) + seg(30, s=9) + seg(40),
    'E P2 seeding 4.5 80 + rec 40': seg(80, s=4.5) + seg(40),
    'F M2 inc 60, ramp down 30, rec 30': seg(60, i=2) + ramp(30, {'i': 2}, {}) + seg(30),
    'F2 M2 inc 60, step down, rec 60': seg(60, i=2) + seg(60),
    'G bridge 1.0 campaign 40 + rec 60': seg(40, s=9, b=1.0) + seg(60),
    'H local campaign 40 + rec 60': seg(40, s=9) + seg(60),
    'I P3 seed+inc 60 + rec 40': seg(60, s=9, i=2) + seg(40),
    'J short inc 15 + rec 45': seg(15, i=2) + seg(45),
    'K P7 recovery 200': seg(200),
}


def run(fit, sched):
    p = core.params_for(m, set(fit['modules']), fit['params'])
    return m.simulate(p, INIT, [m.normalize(a, BOUNDS) for a in P0 + sched])[len(P0):]


def main(paths):
    fits = [json.load(open(p)) for p in paths]
    names = [p.split('/')[-1].replace('.json', '') for p in paths]
    rows = []
    for label, sched in CANDS.items():
        preds = [run(f, sched) for f in fits]
        diffs = []
        for a in range(len(preds)):
            for b in range(a + 1, len(preds)):
                diffs.append(float(np.mean(np.abs(preds[a] - preds[b]) / SIG)))
        rows.append((np.mean(diffs) * 100 / len(sched), label, len(sched), diffs))
    print('pairs:', names)
    for score, label, n, diffs in sorted(rows, reverse=True):
        print(f'{score:7.2f}  {n:4d}  {" / ".join(f"{d:6.1f}" for d in diffs)}  {label}')


if __name__ == '__main__':
    main(sys.argv[1:])
