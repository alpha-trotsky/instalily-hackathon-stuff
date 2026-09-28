"""Score-loss ranking of (run, segment, observable) for v1: lost = sum over ticks of 1 - 1/(1+|err|/sigma).
Type: 'level' if the 2nd half of the segment carries >= 50% of the loss with |mean err| >= 1 sigma and a consistent sign,
'transient' if the first 15 ticks carry >= 50%, else 'dynamics'.  python3 fits/wildlife/round2/rank.py"""
import json, sys
import numpy as np
d = json.load(open('fits/wildlife/round2/diag.json'))
sig = np.array(d['sigma']); names = d['names']
rows = []
for r in ['R3', 'R4', 'R1', 'R2c']:
    run = json.load(open(f'data/wildlife/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in run['observations']])
    p = np.load(f'fits/wildlife/round2/{r}_pred.npy')
    e = (p - o) / sig
    loss = 1 - 1 / (1 + np.abs(e))
    for w in d['runs'][r]['rows']:
        a, b = w['start'], w['end']
        for i, n in enumerate(names):
            L = loss[a:b, i]; tot = L.sum(); h = a + (b - a) // 2
            second = loss[h:b, i].sum(); first15 = loss[a:min(a + 15, b), i].sum()
            me2 = e[h:b, i].mean(); signfrac = abs(np.sign(e[h:b, i]).mean())
            if first15 >= 0.5 * tot: typ = 'transient'
            elif second >= 0.5 * tot and abs(me2) >= 1 and signfrac > 0.8: typ = 'level'
            else: typ = 'dynamics'
            rows.append((r, a, b, w['action'], n, round(float(tot), 1), typ, round(float(me2), 2), round(float(e[a:b, i].mean()), 2)))
new = [x for x in rows if x[0] in ('R3', 'R4')]
tot_new = sum(x[5] for x in new)
print(f'total lost R3+R4 (tick-obs units): {tot_new:.0f} of {sum((w["end"]-w["start"])*4 for r in ["R3","R4"] for w in d["runs"][r]["rows"])}')
for x in sorted(new, key=lambda x: -x[5])[:25]:
    print(f'{x[0]} [{x[1]:3d}-{x[2]-1:3d}] {x[3]:18s} {x[4]:15s} lost {x[5]:5.1f} ({100*x[5]/tot_new:4.1f}%) {x[6]:9s} mean err 2nd half {x[7]:+.2f}σ, whole {x[8]:+.2f}σ')
print('\nby observable (R3+R4):', {n: round(sum(x[5] for x in new if x[4] == n), 1) for n in names})
print('by type (R3+R4):', {t: round(sum(x[5] for x in new if x[6] == t), 1) for t in ['level', 'dynamics', 'transient']})
old = [x for x in rows if x[0] in ('R1', 'R2c')]
print('by observable (old R1+R2c):', {n: round(sum(x[5] for x in old if x[4] == n), 1) for n in names})
print('by type (old):', {t: round(sum(x[5] for x in old if x[6] == t), 1) for t in ['level', 'dynamics', 'transient']})
print('\nold-data top 12:')
for x in sorted(old, key=lambda x: -x[5])[:12]:
    print(f'{x[0]} [{x[1]:3d}-{x[2]-1:3d}] {x[3]:18s} {x[4]:15s} lost {x[5]:5.1f} {x[6]:9s} 2nd-half {x[7]:+.2f}σ')
json.dump(rows, open('fits/wildlife/round2/rank.json', 'w'))
