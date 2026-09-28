"""Free: per-segment quality mean error (pred-obs, in score sigma) for a fit; segments from action changes."""
import json, sys
import numpy as np
sys.path.insert(0, 'fits/reservoir/round2/v2'); from score import load, BOUNDS, SIG, names
M = load(sys.argv[1]); fd = json.load(open(sys.argv[2])); p = fd.get('params', fd)
col = names.index(sys.argv[3]) if len(sys.argv) > 3 else 3
for r in ['R1', 'R2', 'R3', 'R4', 'R5']:
    run = json.load(open(f'data/reservoir/{r}.json'))['runs'][0]
    o = np.array([x[names[col]] for x in run['observations']]); acts = run['actions']
    pr = np.asarray(M.simulate(p, run['initial'], [M.normalize(x, BOUNDS) for x in acts]))[:, col]
    e = (pr - o) / SIG[col]; st = 0; out = []
    for i in range(1, len(acts) + 1):
        if i == len(acts) or acts[i] != acts[i - 1]:
            a = acts[st]; h = (st + i) // 2
            out.append(f"{st}-{i}[{a['release_rate']:.3g},{a['irrigation_allocation']:.2g},{a['withdrawal_depth']:.2g},{a['aeration']:.2g}] "
                       f"{e[st:h].mean():+.1f}/{e[h:i].mean():+.1f}")
            st = i
    print(r, ' | '.join(out))
