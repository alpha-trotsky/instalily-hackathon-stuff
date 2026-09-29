"""Quick sensitivity: cost per run (fit residual units) and heldout score per run when overriding params.
python probe.py MODEL PARAMS 'LD=3' 'sp_A=0.2,kg=70' ..."""
import sys, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/traffic/round3')
import trfit
from greybox.common import core
sets = [x for x in sys.argv[3].split(',') if x]
m = trfit.load(sys.argv[1], sets)
p0 = json.load(open(sys.argv[2]))['params']
eps = trfit.episodes(m, trfit.ALL); sig = trfit.heldout_sigma(m)
import os
ns = sig if os.environ.get('SCORESIG') else np.array([m.NOISE[n] for n in eps[0]['names']])
for ov in sys.argv[4:]:
    p = dict(p0)
    for kv in [x for x in ov.split(',') if x]:
        k, v = kv.split('='); p[k] = float(v)
    row = []
    for ep in eps:
        pr = core.rollout(m, p, ep); r = (pr - ep['obs']) / ns
        c = float(np.sum(2 * 4 * (np.sqrt(1 + (r / 2) ** 2) - 1)) * 0.5)
        sc = core.score(trfit.clamp(m, pr, ep['names']), ep['obs'], sig).mean()
        row.append(f"{ep['name']} {c:7.0f} {sc:.3f}")
    print(f'{ov:28s}', ' | '.join(row))
