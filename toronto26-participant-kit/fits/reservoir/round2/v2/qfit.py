"""Free: quality-only refit of the v2 module (water params frozen at the init file), for structure selection.
python3 qfit.py OUT.json --train R1 R2 R3 [--fix a,b] [--set k=v,...] [--init FILE]; prints scores on R1..R5."""
import argparse, json, sys
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, 'fits/reservoir/round2/v2'); from score import load, score, BOUNDS
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--train', nargs='+')
ap.add_argument('--fix', default=''); ap.add_argument('--set', default=''); ap.add_argument('--init', default='fits/reservoir/round2/v2/init_v2.json')
ap.add_argument('--model', default='greybox/reservoir_model_v2.py'); ap.add_argument('--nfev', type=int, default=300)
a = ap.parse_args()
M = load(a.model); base = json.load(open(a.init)); base = dict(base.get('params', base))
for kv in filter(None, a.set.split(',')):
    k, v = kv.split('='); base[k] = float(v)
Q = ['cq', 'kq', 'wqa', 'wqd', 'wqx', 'wqr', 'wqi', 'a_z', 'lam_q', 'lz', 'gam', 'a3', 'a3d', 'g3', 'h3', 'ap', 'dC', 'gC', 'kfl',
     'kr']
names = [n for n in Q if n in M.SPEC and n not in getattr(M, 'FIXED', ()) and n not in a.fix.split(',')]
eps = []
for r in a.train:
    run = json.load(open(f'data/reservoir/{r}.json'))['runs'][0]
    eps.append((run['initial'], [M.normalize(x, BOUNDS) for x in run['actions']], np.array([o['quality'] for o in run['observations']])))
def par(x):
    p = dict(base); p.update({n: M.to_natural(n, v) for n, v in zip(names, x)}); return p
def res(x):
    p = par(x)
    r = np.concatenate([(np.asarray(M.simulate(p, i, u))[:, 3] - o) / 0.0055 for i, u, o in eps])
    return np.nan_to_num(r, nan=1e4)
x0 = np.array([M.to_raw(n, base[n]) for n in names])
sol = least_squares(res, x0, loss='soft_l1', f_scale=2, x_scale='jac', max_nfev=a.nfev)
p = par(sol.x)
json.dump({'params': p, 'cost': sol.cost, 'train': a.train, 'free': names}, open(a.out, 'w'), indent=1)
sc = score(M, p, ['R1', 'R2', 'R3', 'R4', 'R5'])
print(a.out, f'cost {sol.cost:.1f} nfev {sol.nfev}', ' '.join(f'{r}:{v[3]:.3f}/{v[4]:.3f}' for r, v in sc.items()),
      '| new-q', round(np.mean([sc[r][3] for r in ('R4', 'R5')]), 3), 'old-q', round(np.mean([sc[r][3] for r in ('R1', 'R2', 'R3')]), 3))
print({n: round(p[n], 5) for n in names})
