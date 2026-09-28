"""For each segment's late part (after 12 ticks): score of v1 vs best constant (grid), median and mean constants.
The score 1/(1+|e|/sigma) with sigma << burst spread rewards the MODE of a quantized burst series, not the mean."""
from common import *
import json
res = {}
for nm in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a = run(nm); p = pred(r)
    for s, e, act in segments(r, a):
        s2 = s + min(12, (e - s) // 3)
        if e - s2 < 8: continue
        row = []
        for i in range(4):
            y = o[s2:e, i]; sc = lambda c: (1 / (1 + np.abs(c - y) / SIG[i])).mean()
            grid = np.linspace(0, max(y.max(), 1), 600); scs = [sc(c) for c in grid]; k = int(np.argmax(scs))
            row.append(dict(v1=round(float((1 / (1 + np.abs(p[s2:e, i] - y) / SIG[i])).mean()), 3), best=round(scs[k], 3), best_c=round(float(grid[k]), 2),
                            med=round(sc(np.median(y)), 3), mean=round(sc(y.mean()), 3), ymean=round(float(y.mean()), 2), ymed=round(float(np.median(y)), 2),
                            burst_sd=round(float(np.std(np.diff(y)) / np.sqrt(2)), 2)))
        res[f'{nm}[{s}-{e}) {label(act)}'] = row
        if nm in ('R4', 'R5') or True:
            print(f'{nm} [{s:3d}-{e:3d}) {label(act)[:48]:48s} ' + ' | '.join(
                f"{OBS[i][0]}{OBS[i][-1]} v1 {row[i]['v1']:.2f} best {row[i]['best']:.2f}@{row[i]['best_c']:.1f} med {row[i]['med']:.2f} mean {row[i]['mean']:.2f}" for i in range(2)))
json.dump(res, open('fits/traffic/round2/burst_const.json', 'w'), indent=1)
