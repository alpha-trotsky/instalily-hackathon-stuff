"""Rank candidate Run-2 probes by disagreement of the three Run-1 pair fits (score sigma = 0.1 x std of R1)."""
import json, itertools, numpy as np
import greybox.reservoir_model as m
d = json.load(open('data/reservoir/R1.json')); r = d['runs'][0]; B = d['brief']['interventions']
O = np.array([[o[k] for k in m.OBSERVABLES] for o in r['observations']])
sig = 0.1 * O[20:].std(0)
fits = {n: json.load(open(f'fits/reservoir/m{n}_r1.json'))['params'] for n in ('12', '13', '23')}
REC = dict(release_rate=2, irrigation_allocation=0, withdrawal_depth=0, aeration=1)
def A(**k): return {**REC, **k}
ALL = A(release_rate=12, irrigation_allocation=8, withdrawal_depth=1, aeration=0)
DR = A(release_rate=12, irrigation_allocation=8)
P0 = [(40, REC)]
cands = {
  'A all-pulse100+rec60': [(100, ALL), (60, REC)],
  'B drain60+release-only60+rec40': [(60, DR), (60, A(release_rate=12)), (40, REC)],
  'C irrigation8 x120 + rec40': [(120, A(irrigation_allocation=8)), (40, REC)],
  'D aer0+deep100+rec60': [(100, A(withdrawal_depth=1, aeration=0)), (60, REC)],
  'E all-pulse200+rec60': [(200, ALL), (60, REC)],
  'F irrigation4 x100': [(100, A(irrigation_allocation=4))],
  'G gap: all40,rec20,all40,rec60': [(40, ALL), (20, REC), (40, ALL), (60, REC)],
  'H drain60+irr-only60+rec40': [(60, DR), (60, A(irrigation_allocation=8)), (40, REC)],
  'I release0 x60 (u<0) + rec': [(60, A(release_rate=0)), (30, REC)],
}
init = r['initial']
for name, segs in cands.items():
    acts = [a for n, a in P0 + segs for _ in range(n)]
    U = [m.normalize(a, B) for a in acts]
    Y = {k: m.simulate(p, init, U)[40:] for k, p in fits.items()}
    steps = len(acts) - 40
    dis = [np.abs(Y[a] - Y[b]) / sig for a, b in itertools.combinations(Y, 2)]
    per = [x.mean(0) for x in dis]
    tot = np.mean([x.mean() for x in dis])
    print(f'{name:36s} steps {steps:4d} mean|diff|/sig {tot:6.2f}  per-obs(12v13,12v23,13v23) ' +
          ' | '.join(' '.join(f'{v:5.1f}' for v in q) for q in per))
print('score sigma', np.round(sig, 4))
