"""v1 long holds from reset (free): does the model keep drifting where data are flat? Also internal m3 multiplier."""
import json, sys, importlib.util, numpy as np, math
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'models/ad_auction/ad_auction_model.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
P = json.load(open('models/ad_auction/params.json'))['params']
acts = {'rec': (1.5, 20, .55), 'u.7': (3.95, 76, .7075), 'u.85': (4.475, 88, .74125), 'u1': (5, 100, .775),
        'bid5cap30': (5, 30, .55), 'bid3.25cap100': (3.25, 100, .55), 'bid5cap100 b1.0': (5, 100, 1.0), 'rec b0.1': (1.5, 20, .1)}
for k, a in acts.items():
    y = M.simulate(P, None, [a] * 4000)
    print(f'{k:16s}', ' '.join(f't{t}:{y[t-10:t].mean(0).round(3).tolist()}' for t in (50, 250, 500, 1000, 4000)))
# m3 multiplier trace: re-run with g3=0 to see its effect
P0 = dict(P); P0['g3'] = 0.0
for k in ('u.7', 'u1', 'rec'):
    y = M.simulate(P, None, [acts[k]] * 1000); y0 = M.simulate(P0, None, [acts[k]] * 1000)
    print('m3 effect', k, 'conv with/without m3 at 250/1000:', y[240:250, 2].mean().round(3), y0[240:250, 2].mean().round(3), y[990:1000, 2].mean().round(3), y0[990:1000, 2].mean().round(3))
P2 = dict(P); P2['e2'] = 0.0
for k in ('u.7', 'u1', 'rec'):
    y = M.simulate(P, None, [acts[k]] * 1000); y0 = M.simulate(P2, None, [acts[k]] * 1000)
    print('m2 effect', k, 'spend/conv with vs without m2 at 1000:', y[990:1000, 1:].mean(0).round(2), y0[990:1000, 1:].mean(0).round(2))
