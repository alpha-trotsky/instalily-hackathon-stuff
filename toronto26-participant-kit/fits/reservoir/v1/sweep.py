"""G11: sustained-request sweep over 4,000 ticks (release r alone, and the reference pulse) from level 400/500/600."""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
fit = json.load(open(sys.argv[1]))
M = core.load_model('greybox/reservoir_model.py'); p = core.params_for(M, set(fit['modules']), fit['params'])
for V0 in (400, 600):
    for r in (8, 9, 10, 10.5, 11, 11.5, 12, 13, 'pulse'):
        if r == 'pulse':
            a = (1.0, 1.0, 1.0, 1.0)
        else:
            a = ((r - 2) / 10 if r <= 12 else 1.0, (max(r - 12, 0)) / 8, 0.0, 0.0)
        y = M.simulate(p, {'level': V0, 'inflow': 10, 'outflow': 6, 'quality': 0.86}, [a] * 4000)
        last = y[-680:]
        print(f'V0 {V0} req {r}: level mean {last[:,0].mean():6.1f} [{last[:,0].min():.0f},{last[:,0].max():.0f}] '
              f'inflow {last[:,1].mean():.2f} out {last[:,2].mean():.2f} q {last[:,3].mean():.4f} | level@500 {y[499,0]:.0f} @2000 {y[1999,0]:.0f}')
