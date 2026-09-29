"""Score a (model, params+overrides) on A-D with heldout3 sigma; print D/B checkpoints. Free, local.
    python fits/market/round3/quick.py MODEL FIT '{"a_K":0.01}' [modules]"""
import json, sys, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
from run import MODELS, VARIANTS, FILES, NAMES, SIG
m = core.load_model(MODELS[sys.argv[1]]); fitj = json.load(open(sys.argv[2]))
ov = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
mods = VARIANTS[sys.argv[4]] if len(sys.argv) > 4 else fitj.get('modules')
P = m.params_for(mods, {**fitj['params'], **ov})
tot = []
for r in 'ABCD':
    ep = core.load_episodes([FILES[r]], names=NAMES, model=m)[0]
    pr = core.rollout(m, P, ep); sc = (1 / (1 + np.abs(pr - ep['obs']) / SIG)).mean(0); tot.append(sc.mean())
    print(r, sc.round(3), round(sc.mean(), 4))
    if r in 'BD' and '-v' in sys.argv:
        for t in range(0, 200, 10): print('   ', t, ep['obs'][t].round(2), pr[t].round(2))
print('mean', round(np.mean(tot), 4))
