"""Review: 4000-step constant-control rollouts per fit (stability / equilibria). PYTHONPATH=. python ... fit.json ..."""
import json, sys
import numpy as np
from greybox import social_contagion_model as m
from greybox.common import core
B = {'seeding': (0, 10), 'incentive': (0, 2), 'bridge_outreach': (0, 1)}
cases = {'recovery': (0, 0, 0), 'seed9': (9, 0, 0), 'pulse': (9, 2, 0.6), 'inc2': (0, 2, 0), 'seed9_br1': (9, 0, 1), 'max': (10, 2, 1)}
for f in sys.argv[1:]:
    fj = json.load(open(f)); p = core.params_for(m, set(fj['modules']), fj['params'])
    print(f.split('/')[-1])
    for k, (s, i, b) in cases.items():
        u = [m.normalize({'seeding': s, 'incentive': i, 'bridge_outreach': b}, B)] * 4000
        y = m.simulate(p, {'adopters_a': 50, 'adopters_b': 37}, u)
        print(f"  {k:10s} t100 {y[99,0]:7.1f}/{y[99,1]:7.1f}  t500 {y[499,0]:7.1f}/{y[499,1]:7.1f}  t4000 {y[-1,0]:7.1f}/{y[-1,1]:7.1f}  max {y[:,0].max():7.1f}/{y[:,1].max():7.1f}")
