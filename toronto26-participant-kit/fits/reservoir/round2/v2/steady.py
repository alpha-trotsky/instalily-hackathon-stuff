"""Free: 4,000-tick holds from a typical reset (level 515, quality 0.85) at recovery, u = 0.7 and u = 1 (all controls
at recovery + u*(pulse - recovery)); prints the level of each observable at ticks 50, 300, 1000, 4000.
python3 fits/reservoir/round2/v2/steady.py MODEL.py FIT.json"""
import json, sys
import numpy as np
sys.path.insert(0, 'fits/reservoir/round2/v2'); from score import load, BOUNDS
m = load(sys.argv[1]); fd = json.load(open(sys.argv[2])); p = fd.get('params', fd)
REC = {'release_rate': 2.0, 'irrigation_allocation': 0.0, 'withdrawal_depth': 0.0, 'aeration': 1.0}
PUL = {'release_rate': 12.0, 'irrigation_allocation': 8.0, 'withdrawal_depth': 1.0, 'aeration': 0.0}
ini = {'level': 515.0, 'inflow': 9.4, 'outflow': 5.8, 'quality': 0.85}
for u in (0.0, 0.7, 1.0):
    a = {k: REC[k] + u * (PUL[k] - REC[k]) for k in REC}
    r = np.asarray(m.simulate(p, ini, [m.normalize(a, BOUNDS)] * 4000))
    print(f'u={u}: ' + ' | '.join(f't{t}: ' + ' '.join(f'{x:.4g}' for x in r[t - 1]) for t in (50, 300, 1000, 4000)))
# pulse (u=1, 200 ticks) then recovery 3800
a1 = {k: PUL[k] for k in REC}
r = np.asarray(m.simulate(p, ini, [m.normalize(a1, BOUNDS)] * 200 + [m.normalize(REC, BOUNDS)] * 3800))
print('pulse200->recovery: ' + ' | '.join(f't{t}: ' + ' '.join(f'{x:.4g}' for x in r[t - 1]) for t in (200, 260, 500, 1500, 4000)))
