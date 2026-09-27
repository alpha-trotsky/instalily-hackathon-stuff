"""stab4000.py -- 4,000-step extrapolation check of the reviewer fits (run from the kit folder).
Scenarios held for 4,000 ticks after reset; prints mean shipments / supplier / retail over the last 500 ticks."""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
R = 'fits/supply_chain/review/'
M = core.load_model(R + 'sc_rv.py')
C = M.CONTROLS
def act(**kw):
    a = dict(M.RECOVERY); a['order_quantity'] = 80.0; a.update(kw); return a
SC = {'D': act(), 'D+mix0.8': act(product_mix=0.8), 'D+mix0.2': act(product_mix=0.2),
      'D+rush': act(lead_time_buy=0.2), 'D+m0+e1.5': act(maintenance=0.0, production_effort=1.5),
      'D+m0': act(maintenance=0.0), 'q20': act(order_quantity=20.0)}
init = {'shipments': 30.0, 'inventory_supplier': 90.0, 'inventory_retail': 100.0}
for f in ['rv_base_all', 'rv_m12_all', 'rv_m13_all', 'rv_m23_all']:
    fit = json.load(open(R + f + '.json'))
    p = core.params_for(M, fit['modules'], fit['params'])
    row = []
    for name, a in SC.items():
        u = [M.normalize(a, {})] * 4000
        y = M.simulate(p, init, u)
        row.append('%s %.1f/%.0f/%.0f (t300 %.1f)' % (name, *y[-500:].mean(0), y[250:350, 0].mean()))
    print(f, ' | '.join(row))
