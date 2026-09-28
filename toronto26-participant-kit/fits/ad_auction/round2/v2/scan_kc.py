"""Scan the committed-availability gain kc around a fit (mean score per run)."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
m = core.load_model('greybox/ad_auction_model_v2.py')
ref = core.load_episodes([f'data/ad_auction/{r}.json' for r in ('R1', 'R2c', 'R3', 'R4')], model=m)
sig = core.score_sigma(ref)
d = json.load(open(sys.argv[1]))
for kc in (0, 0.01, 0.03, 0.1, 0.3, 1.0):
    p = core.params_for(m, set(d['modules']) | {'cm'}, {**d['params'], 'kc': kc})
    print(kc, [round(float(np.mean(core.score(core.rollout(m, p, ep), ep['obs'], sig))), 3) for ep in ref])
