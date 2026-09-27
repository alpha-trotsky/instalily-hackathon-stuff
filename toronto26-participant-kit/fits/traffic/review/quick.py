import sys, json, time
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
m = core.load_model('fits/traffic/review/traffic_model_rv.py')
eps = core.load_episodes(['data/traffic/R1.json', 'data/traffic/R2.json'], model=m)
p = core.params_for(m, set(sys.argv[1].split(',')) if len(sys.argv) > 1 else set(), json.load(open(sys.argv[2]))['params'] if len(sys.argv) > 2 else None)
sig = core.score_sigma(eps)
for ep in eps:
    t = time.time(); pr = core.rollout(m, p, ep); dt = time.time() - t
    print(ep['source'], 'sim %.3fs' % dt, 'score', np.round(core.score(pr, ep['obs'], sig), 3))
    for a, b in [(60, 100), (200, 280), (340, 370), (480, 495), (690, 700)]:
        if b <= len(pr): print('  ', a, b, 'pred', np.round(pr[a:b].mean(0), 1), 'obs', np.round(ep['obs'][a:b].mean(0), 1))
