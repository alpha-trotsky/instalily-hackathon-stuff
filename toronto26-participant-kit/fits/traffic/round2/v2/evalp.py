"""Score a params file on R1-R5 with the heldout sigma. python fits/traffic/round2/v2/evalp.py MODEL PARAMS [LD=3 ...]"""
import sys, json, time
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/traffic/round2/v2')
import trfit as fitv2
m = fitv2.load(sys.argv[1], sys.argv[3:])
p = json.load(open(sys.argv[2]))['params']
p = {k: p.get(k, v[0]) for k, v in m.SPEC.items()} | {k: v for k, v in p.items()}
t = time.time(); sc = fitv2.score_runs(m, p)
for r, v in sc.items(): print(r, v, round(float(np.mean(v)), 4))
print('time %.2fs' % (time.time() - t))
