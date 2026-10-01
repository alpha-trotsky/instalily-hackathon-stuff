"""Long-run holds from reset (4,000 ticks): levels at t=100, 250, 1000, 4000 for recovery, u.7, u1, bid5/cap30/b.55.
round-3 copy (adds the R5 holds); usage: python fits/ad_auction/round3/longrun3.py fit.json [--model M]"""
import sys, json, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
args = sys.argv[1:]; mp = 'greybox/ad_auction_model_v3.py'
if '--model' in args:
    i = args.index('--model'); mp = args[i + 1]; del args[i:i + 2]
model = core.load_model(mp)
for f in args:
    d = json.load(open(f)); p = core.params_for(model, set(d['modules']), d['params'])
    print(f)
    for name, a in [('recovery', (1.5, 20, .55)), ('u.7', (3.95, 76, .7075)), ('u1', (5, 100, .775)),
                    ('bid5 cap30 .55', (5, 30, .55)), ('bid5 cap100 b1', (5, 100, 1.0)), ('bid0.75 cap100', (.75, 100, .55)), ('bid5 cap20 .775', (5, 20, .775)), ('bid1.5 cap100 .775', (1.5, 100, .775))]:
        y = np.asarray(model.simulate(p, {}, [a] * 4000))
        print(f'  {name:16s}', ' '.join(f't{t}:' + '/'.join(f'{v:.3f}' for v in y[t - 10:t].mean(0)) for t in (50, 100, 250, 1000, 4000)))
