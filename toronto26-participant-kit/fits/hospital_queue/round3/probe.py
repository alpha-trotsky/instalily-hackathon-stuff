"""Quick manual probe: evaluate a fit with parameter overrides, print scores and tail cells. python probe.py MODEL FIT k=v ..."""
import sys, json
import numpy as np
sys.path.insert(0, 'fits/hospital_queue/round3')
import ev3
model, p = ev3.load(sys.argv[1], sys.argv[2])
for kv in sys.argv[3:]:
    k, v = kv.split('='); p[k] = float(v)
res = ev3.score(model, p, ['R1', 'R2c', 'R3', 'R4', 'R4c'])
print(' '.join(f'{r}:{s.mean():.3f}' for r, s in res.items()), 'mean4', round(np.mean([res[r].mean() for r in ['R1','R2c','R3','R4c']]), 4))
for r, ts in [('R1', [600, 650, 700, 749]), ('R2c', [385, 420, 500, 549]), ('R4c', [260, 300, 350, 449])]:
    act, obs, pred = ev3.predict(model, p, r)
    print(' ', r, ' '.join(f't{t}: d{obs[t].round(0).tolist()} m{pred[t].round(0).tolist()}' for t in ts))
