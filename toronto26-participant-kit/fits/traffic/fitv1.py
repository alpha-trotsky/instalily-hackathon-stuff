"""Phase C fit driver for greybox/traffic_model.py (v1): Powell passes then least_squares polish (review myfit.py),
with a data list. Active modules start from SPEC defaults; everything else from INIT (missing keys -> SPEC).
python fits/traffic/fitv1.py MODULES OUT INIT(or -) PW DATA1 [DATA2 ...]"""
import sys, json, time
import numpy as np
from scipy.optimize import least_squares, minimize
sys.path.insert(0, '.')
from greybox.common import core, fit as F

mods = set(x for x in sys.argv[1].split(',') if x and x != 'none')
out, initp, pw, data = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5:]
m = core.load_model('greybox/traffic_model.py')
init = None
if initp != '-':
    src = json.load(open(initp))['params']
    init = {k: v for k, v in src.items() if k in m.SPEC}
    if 'qmax' in src and 'qmax_A' not in src:
        init['qmax_A'] = src['qmax']; init['qmax_B'] = 0.5 * src['qmax']
    if init.get('kJ', 0.5) > 0.95:
        init['kJ'] = 0.5
    for mod in mods:
        for n in m.MODULES[mod][0]:
            init[n] = m.SPEC[n][0]
eps = core.load_episodes(data, model=m)
for ep in eps:
    ep['u'] = [m.normalize(a, ep['bounds']) for a in ep['actions']]
names = eps[0]['names']
units = [m.UNITS[n] for n in names]; sigma = [m.NOISE[n] for n in names]
P = F.Problem(m, eps, mods, units, sigma, init=init)
x = P.x0(); t0 = time.time()


def _cost(z):
    r = P.residuals(z)
    return float(np.sum(2 * 4 * (np.sqrt(1 + (r / 2) ** 2) - 1)) * 0.5)


c0 = _cost(x)
for rep in range(2):
    sol0 = minimize(_cost, x, method='Powell', options={'maxfev': pw // 2, 'xtol': 1e-3, 'ftol': 1e-6})
    x = sol0.x
    print('powell', rep, 'cost', round(sol0.fun, 1), 'nfev', sol0.nfev, '%.0fs' % (time.time() - t0), flush=True)
sol = least_squares(P.residuals, x, loss='soft_l1', f_scale=2.0, x_scale='jac', diff_step=0.01, max_nfev=150,
                    ftol=1e-12, xtol=1e-12, gtol=1e-12)
x = sol.x if sol.cost <= _cost(x) + 1e-9 else x
params = P.params(x)
cost = _cost(x)
sig = core.score_sigma(eps)
ev = F.evaluate(m, params, eps, sig)
per = {ep['source']: F.evaluate(m, params, [ep], sig) for ep in eps}
res = {'model': 'greybox/traffic_model.py', 'modules': sorted(mods), 'cost': cost, 'start_cost': c0,
       'params': params, 'free': P.names, 'data': data,
       'eval': {'all': ev, **per}}
json.dump(res, open(out, 'w'), indent=1)
print('cost', round(cost, 1), 'start', round(c0, 1), 'score all', round(float(np.mean(ev['score'])), 4),
      {k: round(float(np.mean(v['score'])), 4) for k, v in per.items()}, '%.0fs' % (time.time() - t0))
