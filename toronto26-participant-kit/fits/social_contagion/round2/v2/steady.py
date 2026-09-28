"""Steady levels over 4,000 ticks from a reset reading of 45/35: recovery, u.7, u1, seeding 4.5 + incentive 2."""
import json, sys, os
sys.path.insert(0, os.getcwd())
from greybox.common import core
B = {'seeding': (0, 10), 'incentive': (0, 2), 'bridge_outreach': (0, 1)}
cases = {'recovery': (0, 0, 0), 'u.7': (6.3, 1.4, .42), 'u1': (9, 2, .6), 's4.5+i2': (4.5, 2, 0), 's4.5': (4.5, 0, 0)}
for f in sys.argv[1:]:
    fj = json.load(open(f)); m = core.load_model(fj['model'])
    out = []
    for k, (s, i, b) in cases.items():
        u = [m.normalize({'seeding': s, 'incentive': i, 'bridge_outreach': b}, B)] * 4000
        y = m.simulate(fj['params'], {'adopters_a': 45, 'adopters_b': 35}, u)
        out.append(f"{k} @300 {y[299,0]:.0f}/{y[299,1]:.0f} @4000 {y[-1,0]:.0f}/{y[-1,1]:.0f} min {y[100:,0].min():.0f}/{y[100:,1].min():.0f} max {y[100:,0].max():.0f}/{y[100:,1].max():.0f}")
    print(os.path.basename(f)); print('   ' + '\n   '.join(out))
