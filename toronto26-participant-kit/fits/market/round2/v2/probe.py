"""Steady states and 4000-tick behaviour of a fit.  python3 fits/market/round2/v2/probe.py FIT.json [model.py]"""
import json, sys
sys.path.insert(0, '.')
from greybox.common import core
p = json.load(open(sys.argv[1]))['params']
m = core.load_model(sys.argv[2] if len(sys.argv) > 2 else 'greybox/market_model_v2.py')
ini = {'price': 100.0, 'volume': 100.0, 'depth': 100.0}
def show(label, acts):
    y = m.simulate(p, ini, acts)
    print(f"{label:34s}", '  '.join(f"t{t}:" + '/'.join(f"{v:.2f}" for v in y[t - 1]) for t in (150, 600, 2000, 4000)))
for r, t in [(0, 0), (1, 0), (0, 1), (1, 1), (0.7, 0), (0, 0.7), (0.7, 0.7), (0.85, 0.85), (0.5, 0.5)]:
    show(f'hold r={r} tau={t} from reset', [(r, t)] * 4000)
    show(f'  after 300 recovery', [(0, 0)] * 300 + [(r, t)] * 3700)
show('pulse(1,1) 300 then recover', [(0, 0)] * 300 + [(1, 1)] * 300 + [(0, 0)] * 3400)
