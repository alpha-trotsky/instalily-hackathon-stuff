"""Decision rules: candidate predictions on the ACTUAL initial readings vs data (last-10 means per segment)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import importlib
sys.path.insert(0, 'greybox'); import reservoir_model as M
bounds = {'release_rate': (0, 12), 'irrigation_allocation': (0, 8), 'withdrawal_depth': (0, 1), 'aeration': (0, 1)}
def params(path, **over):
    d = json.load(open(path)); p = d.get('params', d)
    p = {k: v for k, v in p.items()}; p.update(over); return p
cands = {'m13 (v1)': params('fits/reservoir/v1/final.json'),
         'm12_all': params('fits/reservoir/v1/m12_all.json'),
         'v1 gC=0': params('fits/reservoir/v1/final.json', gC=0.0),
         'v1 gC=0,g3=0': params('fits/reservoir/v1/final.json', gC=0.0, g3=0.0)}
for name in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a, segs = run(name)
    acts = [M.normalize(x, bounds) for x in r['actions']]
    sims = {k: M.simulate(p, r['initial'], acts) for k, p in cands.items()}
    print(f'== {name}   quality last-10 means (x1000), err in σ_q=0.00102;   level last-10')
    print('  seg        data  | ' + ' | '.join(f'{k:>16s}' for k in cands))
    for s, e, act in segs:
        lo = max(s, e - 10); d = o[lo:e, 3].mean()
        cells = [f'{1000*sims[k][lo:e,3].mean():7.2f} ({(sims[k][lo:e,3].mean()-d)/SIG[3]:+5.1f})' for k in cands]
        lv = [f'{sims[k][lo:e,0].mean():5.0f}' for k in cands]
        print(f'  [{s:3d}-{e-1:3d}] {1000*d:7.2f} | ' + ' | '.join(cells) + f' || lev {o[lo:e,0].mean():5.0f} ' + ' '.join(lv))
    for k in cands:
        sc = (1 / (1 + np.abs(sims[k] - o) / SIG)).mean(0)
        print(f'    score {k:14s} ' + ' '.join(f'{v:.3f}' for v in sc))
