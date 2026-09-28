"""Free: 4,000-tick holds from reset (initial 25/100/100) at recovery, u=0.7, u=0.85, u=1 joint, plus single-control pulses (u=1)."""
import json, sys, os, numpy as np
sys.path.insert(0, os.getcwd())
from greybox.common import core
f = json.load(open(sys.argv[1])); model = core.load_model(sys.argv[2])
b = json.load(open('docs/supply_chain.json'))['brief']['forecast_context']
bounds = json.load(open('data/supply_chain/R1.json'))['brief']['interventions']
REC, PUL = model.RECOVERY, model.PULSE
def act(u, only=None):
    return {c: (REC[c] + u * (PUL[c] - REC[c])) if (only is None or c in only) else REC[c] for c in model.CONTROLS}
ini = {'shipments': 25.0, 'inventory_supplier': 100.0, 'inventory_retail': 100.0}
cases = [('recovery', act(0)), ('joint u.7', act(.7)), ('joint u.85', act(.85)), ('joint u1', act(1))]
cases += [(f'orders+{c} u1', act(1, ['order_quantity', c])) for c in model.CONTROLS if c != 'order_quantity']
cases += [('orders only u1', act(1, ['order_quantity'])), ('orders only u.7', act(.7, ['order_quantity']))]
for name, a in cases:
    u = [model.normalize(a, bounds)] * 4000
    y = np.asarray(model.simulate(f['params'], ini, u))
    print(f"{name:28s} t=200 {np.round(y[199],1)}  t=1000 {np.round(y[999],1)}  t=4000 {np.round(y[-1],1)}  max {np.round(y.max(0),0)}")
