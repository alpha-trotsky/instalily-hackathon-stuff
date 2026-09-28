"""v1 prediction for long holds from reset (the sustained category) at the round-2 settings."""
from common import *
r4, o4, a4 = run('R4'); r5, o5, a5 = run('R5')
sets = {'u.7': r4['actions'][0], 'u1': r4['actions'][200], 'u.85': r4['actions'][310], 'B toll1.5 ramp1': r5['actions'][0],
        'B+frt0': r5['actions'][50], 'B+sig.3': r5['actions'][90], 'B+lane.3': r5['actions'][130], 'B+clr.5': r5['actions'][170]}
ini = r4['initial']
for k, act in sets.items():
    p = np.array([[x[n] for n in OBS] for x in heldout.load('fits/round2/v1_models/traffic', 'lr').predict(ini, [act] * 2000, CTX)])
    print(f'{k:18s}', ' '.join(f't{t}: ' + ','.join(f'{v:.1f}' for v in p[t - 20:t].mean(0)) for t in (50, 150, 300, 600, 1000, 2000)))
