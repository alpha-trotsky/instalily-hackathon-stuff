"""Rank candidate reserve schedules (<=55 steps) by disagreement among the R1+R2 refits (base, m12, m13, m23), in local sigma."""
import sys, json, itertools, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
model = core.load_model('greybox/ad_auction_model.py')
eps = core.load_episodes(['data/ad_auction/R1.json', 'data/ad_auction/R2.json'], model=model)
sig = core.score_sigma(eps)
R = 'fits/ad_auction/review/'
fits = {n: json.load(open(R + f))['params'] for n, f in [('base', 'base_hop.json'), ('m12', 'm12_c.json'), ('m13', 'm13_c.json'), ('m23', 'm23_c.json')]}
hist = eps[1]['u']  # R2 history (continue case)
REC = (1.5, 20.0, 0.55)
def seg(a, n): return [a] * n
C = {
 'A reset cap100 15 | bid3.25 cap100 20 | rec 20': seg((1.5, 100, .55), 15) + seg((3.25, 100, .55), 20) + seg(REC, 20),
 'B bid3.25 cap100 30 | rec 25': seg((3.25, 100, .55), 30) + seg(REC, 25),
 'C bid5 cap100 br1.0 30 | rec 25': seg((5, 100, 1.0), 30) + seg(REC, 25),
 'D bid3.25 cap100 br1.0 30 | rec 25': seg((3.25, 100, 1.0), 30) + seg(REC, 25),
 'E bid0.75 cap100 30 | rec 25': seg((0.75, 100, .55), 30) + seg(REC, 25),
 'F bid5 cap100 br0.1 30 | rec 25': seg((5, 100, 0.1), 30) + seg(REC, 25),
 'G bid5 cap50 30 | rec 25': seg((5, 50, .55), 30) + seg(REC, 25),
 'H br0.1 20 | br1.0 cap100 bid5 20 | rec 15 (P6 reversed)': seg((1.5, 20, .1), 20) + seg((5, 100, 1.0), 20) + seg(REC, 15),
 'I bid3.25 cap100 15 | bid3.25 cap100 br1.0 20 | rec 20': seg((3.25, 100, .55), 15) + seg((3.25, 100, 1.0), 20) + seg(REC, 20),
}
for start in ['fresh', 'continue']:
    print('==', start)
    rows = []
    for name, sch in C.items():
        pre = [] if start == 'fresh' else hist
        P = {n: np.asarray(model.simulate(p, {}, pre + sch))[len(pre):] for n, p in fits.items()}
        d = [np.mean(np.abs(P[a] - P[b]) / sig, axis=0) for a, b in itertools.combinations(P, 2)]
        rows.append((np.mean(d), name, np.round(np.mean(d, axis=0), 2), {n: np.round(P[n][len(sch)-26 if len(sch)>26 else 0], 2).tolist() for n in P}))
    for r in sorted(rows, reverse=True):
        print('%.2f  %s  per-obs %s' % (r[0], r[1], r[2]))
print('== proposed composites')
for start, b in [('continue', 5.0), ('fresh', 5.0), ('fresh', 3.25)]:
    sch = seg((b, 100, 1.0), 25) + seg((1.5, 20, 0.1), 20) + seg(REC, 10)
    pre = [] if start == 'fresh' else hist
    P = {n: np.asarray(model.simulate(p, {}, pre + sch))[len(pre):] for n, p in fits.items()}
    d = [np.mean(np.abs(P[a] - P[b2]) / sig, axis=0) for a, b2 in itertools.combinations(P, 2)]
    print(start, b, 'disagreement %.2f' % np.mean(d), np.round(np.mean(d, 0), 2))
    for n in P: print('   ', n, 'spend max %.1f' % P[n][:25, 1].max(), 'broad end', np.round(P[n][24], 2), 'narrow end', np.round(P[n][44], 2))
