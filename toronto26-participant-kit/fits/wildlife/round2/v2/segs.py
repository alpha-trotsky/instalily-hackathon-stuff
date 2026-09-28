"""Per-segment last-10 levels and error (sigma units) for a fit. Free.
    python3 fits/wildlife/round2/v2/segs.py MODEL.py FIT.json [R3 R4 ...]"""
import json, sys
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round2'); sys.path.insert(0, 'fits/wildlife/round2/v2')
import heldout, fitv2
from greybox.common import core

CTRL = ['hunting_quota', 'habitat_protection', 'corridor_access']
model = core.load_model(sys.argv[1])
params = json.load(open(sys.argv[2]))['params']
runs = sys.argv[3:] or ['R1', 'R2c', 'R3', 'R4']
_, sig = heldout.sigma('wildlife')
for ep in fitv2.episodes(model, runs):
    p = core.rollout(model, params, ep)
    o = ep['obs']
    A = np.array([[a[c] for c in CTRL] for a in ep['actions']])
    ch = [0] + [i for i in range(1, len(A)) if not np.allclose(A[i], A[i - 1])] + [len(A)]
    sc = (1 / (1 + np.abs(p - o) / sig)).mean(0)
    print(ep['tag'], np.round(sc, 3).tolist(), round(float(sc.mean()), 4))
    for a, b in zip(ch[:-1], ch[1:]):
        lo = max(b - 10, a)
        e = (p[a:b] - o[a:b]) / sig
        lab = 'h%g/p%g/c%g' % tuple(A[a])
        print(f"  {a:4d}-{b:4d} {lab:18s} obs {np.round(o[lo:b].mean(0), 2).tolist()} mod {np.round(p[lo:b].mean(0), 2).tolist()}"
              f" meanerr {np.round(e.mean(0), 1).tolist()}")
