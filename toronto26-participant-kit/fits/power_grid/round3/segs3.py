"""Per-segment table (last-10 means, err in score sigma, segment score) for fit JSONs on runs.
python fits/power_grid/round3/segs3.py RUN FIT [FIT ...]"""
import sys, json
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round3'); sys.path.insert(0, 'fits/round2')
import numpy as np
from greybox.common import core
from heldout3 import sigma
NAMES = ['load', 'frequency', 'renewable_share']; _, SIG = sigma('power_grid')
run = sys.argv[1]
for fp in sys.argv[2:]:
    res = json.load(open(fp)); m = core.load_model(res['model'])
    ep = core.load_episodes([f'data/power_grid/{run}.json'], names=NAMES, model=m)[0]
    pr = core.rollout(m, res['params'], ep); o = ep['obs']; A = ep['actions']
    b = [0] + [i for i in range(1, len(A)) if A[i] != A[i - 1]] + [len(A)]
    sc = 1 / (1 + np.abs(pr - o) / SIG)
    print(fp.split('/')[-1], run, 'score', sc.mean(0).round(3).tolist())
    for i in range(len(b) - 1):
        s, e = b[i], b[i + 1]
        print(f'  {s:4d}-{e:4d} data {np.round(o[e-10:e].mean(0),3).tolist()} model {np.round(pr[e-10:e].mean(0),3).tolist()}'
              f' err {np.round((pr-o)[e-10:e].mean(0)/SIG,1).tolist()} score {sc[s:e].mean(0).round(3).tolist()}')
