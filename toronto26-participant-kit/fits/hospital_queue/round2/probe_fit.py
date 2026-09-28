"""DIAGNOSTIC ONLY (not a candidate model): how much of the v1 loss is parameter compensation (we, theta, Ae) vs
missing structure. Refits a few v1 parameters on R1+R2c+R3+R4, scores each run. Run from KIT."""
import json, sys, time
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round2')
from greybox.common import core
import heldout
names, sig = heldout.sigma('hospital_queue')
M = core.load_model('fits/round2/v1_models/hospital_queue/hospital_queue_model.py')
p0 = json.load(open('models/hospital_queue/params.json'))['params']
eps = core.load_episodes([f'data/hospital_queue/{r}.json' for r in ['R1', 'R2c', 'R3', 'R4']], model=M)
for kv in sys.argv[2:]:
    k, v = kv.split('='); p0[k] = float(v)
FREE = sys.argv[1].split(',') if len(sys.argv) > 1 else ['Ae', 'we', 'theta', 'wd', 'kw', 'Wmax', 'Cb', 'a2', 'g2']

def pars(x):
    p = dict(p0); p.update({k: M.to_natural(k, v) for k, v in zip(FREE, x)}); return p

def score(p):
    out = []
    for ep in eps:
        pr = core.rollout(M, p, ep); o = np.asarray(ep['y'] if 'y' in ep else ep['obs'])
        out.append((1 / (1 + np.abs(pr - o) / sig)).mean(0).round(3).tolist())
    return out

def res(x):
    p = pars(x); r = []
    for ep in eps:
        pr = core.rollout(M, p, ep); o = np.asarray(ep['y'] if 'y' in ep else ep['obs'])
        r.append(((pr - o) / sig).ravel())
    r = np.concatenate(r); r[~np.isfinite(r)] = 1e3; return np.clip(r, -1e3, 1e3)

x0 = np.array([M.to_raw(k, p0[k]) for k in FREE])
print('v1 scores R1,R2c,R3,R4:', score(p0))
t = time.time()
sol = least_squares(res, x0, loss='soft_l1', f_scale=2, diff_step=1e-2, max_nfev=300)
for _ in range(3):
    sol = least_squares(res, sol.x, loss='soft_l1', f_scale=2, diff_step=1e-3, max_nfev=300)
p = pars(sol.x)
print('free', FREE, 'nfev', sol.nfev, f'{time.time()-t:.0f}s')
print('refit params:', {k: round(p[k], 4) for k in FREE})
print('refit scores R1,R2c,R3,R4:', score(p))
