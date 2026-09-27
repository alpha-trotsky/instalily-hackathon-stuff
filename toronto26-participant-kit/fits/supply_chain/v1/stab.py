"""stab.py FIT...: 4,000-tick held-action runs across the control range (run from the kit folder)."""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
M = core.load_model('greybox/supply_chain_model.py')
def act(**kw):
    a = dict(M.RECOVERY); a['order_quantity'] = 80.0; a.update(kw); return a
SC = {'rec': act(order_quantity=0.0), 'D': act(), 'q20': act(order_quantity=20.0), 'q40': act(order_quantity=40.0),
      'mix0': act(product_mix=0.0), 'mix0.8': act(product_mix=0.8), 'mix1': act(product_mix=1.0),
      'rush0.2': act(lead_time_buy=0.2), 'lead0': act(lead_time_buy=0.0), 'm0': act(maintenance=0.0),
      'e0': act(production_effort=0.0), 'e0.5': act(production_effort=0.5), 'e1.5': act(production_effort=1.5),
      'r0.35': act(receiving_effort=0.35), 'r0': act(receiving_effort=0.0), 'allpulse': act(**M.PULSE)}
init = {'shipments': 30.0, 'inventory_supplier': 90.0, 'inventory_retail': 100.0}
bounds = {c: (0.0, 80.0 if c == 'order_quantity' else 1.5 if c in ('production_effort', 'receiving_effort') else 1.0) for c in M.CONTROLS}
for f in sys.argv[1:]:
    fit = json.load(open(f))
    p = core.params_for(M, fit['modules'], fit['params'])
    print(f)
    for name, a in SC.items():
        y = M.simulate(p, init, [M.normalize(a, bounds)] * 4000)
        drift = np.abs(y[-500:].mean(0) - y[250:350].mean(0))
        print('  %-8s last500 %6.1f/%5.0f/%6.0f  t300 %6.1f/%5.0f/%6.0f  drift %s' % (name, *y[-500:].mean(0), *y[250:350].mean(0), np.round(drift, 1)))
