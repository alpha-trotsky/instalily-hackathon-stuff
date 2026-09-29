"""Block means (data vs model) for a run, plus internal A/B queue. python ts.py MODEL PARAMS RUN [block] [t0 t1]"""
import sys, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/traffic/round3')
import trfit
m = trfit.load(sys.argv[1], [])
p = json.load(open(sys.argv[2]))['params']
p = {k: p.get(k, v[0]) for k, v in m.SPEC.items()} | p
ep = trfit.episodes(m, [sys.argv[3]])[0]
B = int(sys.argv[4]) if len(sys.argv) > 4 else 5
t0 = int(sys.argv[5]) if len(sys.argv) > 5 else 0
t1 = int(sys.argv[6]) if len(sys.argv) > 6 else len(ep['u'])
pred = np.asarray(m.simulate(p, ep['initial'], ep['u'])); o = ep['obs']
for s in range(t0, t1, B):
    e = min(s + B, t1)
    print(f'{s:4d} u={[round(x,2) for x in ep["u"][s]]} data {o[s:e].mean(0).round(1)} model {pred[s:e].mean(0).round(1)}')
