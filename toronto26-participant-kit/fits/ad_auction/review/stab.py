"""4000-step stability / extremes check of fitted params. usage: stab.py fit.json [...]"""
import sys, json, time, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
model = core.load_model('greybox/ad_auction_model.py')
B = model.BOUNDS
rng = np.random.default_rng(0)
def sched(kind):
    T = 4000; acts = []; t = 0
    while t < T:
        L = int(rng.integers(20, 400))
        if kind == 'uniform':
            a = tuple(rng.uniform(*B[c]) for c in model.CONTROLS)
        elif kind == 'extreme':
            a = tuple(B[c][rng.integers(0, 2)] for c in model.CONTROLS)
        else:  # recovery/pulse style
            a = (1.5 + rng.uniform(0.7, 1) * 3.5 * rng.integers(0, 2), 20 + rng.uniform(0.7, 1) * 80 * rng.integers(0, 2), 0.55 + rng.uniform(0.7, 1) * 0.225 * rng.integers(0, 2))
        acts += [a] * L; t += L
    return acts[:T]
fixed = {'pulse4000': [(5.0, 100.0, 0.775)] * 4000, 'narrow_bid5': [(5.0, 100.0, 0.1)] * 4000, 'broad_bid5': [(5.0, 100.0, 1.0)] * 4000,
         'rec4000': [(1.5, 20.0, 0.55)] * 4000, 'bid5cap20': [(5.0, 20.0, 0.55)] * 4000, 'lowbid': [(0.3, 100.0, 0.55)] * 4000}
for f in sys.argv[1:]:
    p = json.load(open(f))['params']
    print('==', f)
    for name, acts in fixed.items():
        t0 = time.time(); Y = np.asarray(model.simulate(p, {}, acts)); dt = time.time() - t0
        print('  %-12s finite %s  end %s  min %s max %s  (%.2fs)' % (name, np.isfinite(Y).all(), np.round(Y[-1], 3), np.round(Y.min(0), 3), np.round(Y.max(0), 3), dt))
    for kind in ['uniform', 'extreme', 'scen']:
        for k in range(3):
            acts = sched(kind); Y = np.asarray(model.simulate(p, {}, acts))
            print('  %-8s %d finite %s min %s max %s' % (kind, k, np.isfinite(Y).all(), np.round(Y.min(0), 3), np.round(Y.max(0), 3)))
