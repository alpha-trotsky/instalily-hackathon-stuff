import sys, json
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
m = core.load_model(sys.argv[1]); fj = json.load(open(sys.argv[2]))
p = core.params_for(m, set(fj['modules']), fj['params'])
eps = core.load_episodes(['data/traffic/R1.json', 'data/traffic/R2.json', 'data/traffic/R3.json'], model=m)
sig = core.score_sigma(eps[:2])
for ep in eps:
    pr = core.rollout(m, p, ep)
    print(ep['source'], 'score', np.round(core.score(pr, ep['obs'], sig), 3), round(float(np.mean(core.score(pr, ep['obs'], sig))),4))
pr = core.rollout(m, p, eps[2])
for a in range(0, 55, 5): print(a, np.round(pr[a:a+5].mean(0),1), np.round(eps[2]['obs'][a:a+5].mean(0),1))
