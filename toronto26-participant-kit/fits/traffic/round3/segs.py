"""Per-segment last-10-tick means (data vs model) and segment scores. python segs.py MODEL PARAMS RUN [LD=3]"""
import sys, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/traffic/round3')
import trfit
m = trfit.load(sys.argv[1], sys.argv[4:])
p = json.load(open(sys.argv[2]))['params']
sig = trfit.heldout_sigma(m)
ep = trfit.episodes(m, [sys.argv[3]])[0]
pred = trfit.clamp(m, np.asarray(m.simulate(p, ep['initial'], ep['u'])), ep['names'])
o = ep['obs']; u = ep['u']
s = 0
for t in range(1, len(u) + 1):
    if t == len(u) or u[t] != u[s]:
        e = t; a = max(s, e - 10)
        sc = (1 / (1 + np.abs(pred[s:e] - o[s:e]) / sig)).mean(0)
        print(f'{s:4d}-{e:4d} u={[round(x,2) for x in u[s]]}\n   data {o[a:e].mean(0).round(1)} model {pred[a:e].mean(0).round(1)} err/sig {((pred[a:e]-o[a:e]).mean(0)/sig).round(1)} score {sc.round(2)}')
        s = t
