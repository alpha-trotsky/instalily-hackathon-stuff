"""Steady states over 4,000-tick holds from reset (recovery, u=.7/.85/1 on all controls), plus a pulse-recovery check.
python fits/traffic/round2/v2/longrun.py MODEL PARAMS [LD=3]"""
import sys, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/traffic/round2/v2')
import trfit as fitv2
m = fitv2.load(sys.argv[1], sys.argv[3:])
p = json.load(open(sys.argv[2]))['params']
ini = {'flow_a': 0.0, 'flow_b': 0.0, 'speed_a': 36.3, 'speed_b': 36.6}
def show(tag, u, T=4000):
    o = np.asarray(m.simulate(p, ini, [u] * T))
    cols = [o[s:e].mean(0).round(2).tolist() for s, e in ((140, 150), (990, 1000), (3990, 4000))]
    print(f'{tag:10s} t150 {cols[0]}  t1000 {cols[1]}  t4000 {cols[2]}')
show('recovery', (0.0,) * 6)
for u in (0.5, 0.7, 0.85, 1.0):
    show(f'u{u}', (u,) * 6)
# pulse u1 for 200 then recovery 3800
o = np.asarray(m.simulate(p, ini, [(1.0,) * 6] * 200 + [(0.0,) * 6] * 3800))
print('u1 200 -> rec: t250', o[245:250].mean(0).round(2).tolist(), 't4000', o[-10:].mean(0).round(2).tolist())
