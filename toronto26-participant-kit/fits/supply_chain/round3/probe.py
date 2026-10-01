"""Free: instrument a supply_chain model on a run (prints internal states). python probe.py MODULE PARAMS RUN t0 t1"""
import sys, json, re, importlib.util, numpy as np
mod, par, run, t0, t1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
src = open(mod).read()
# inject a trace hook just before the out[t,0] line
src = src.replace("        out[t, 0] = min(max(ship, 0.0), 200.0)", "        TRACE.append((t, ship, S, R, B, Uc, Rc, dtot, rel, sales))\n        out[t, 0] = min(max(ship, 0.0), 200.0)")
ns = {'TRACE': []}
exec(compile(src, mod, 'exec'), ns)
p = json.load(open(par))['params']
r = json.load(open(f'data/supply_chain/{run}.json'))['runs'][0]
bounds = json.load(open('models/supply_chain/params.json'))['bounds']
acts = [ns['normalize'](a, bounds) for a in r['actions']]
ns['simulate'](p, r['initial'], acts)
print('t ship S R B U Rc dtot prod sales | data ship S R')
for (t, *v) in ns['TRACE'][t0:t1]:
    o = r['observations'][t]
    print(t, ' '.join(f'{x:7.1f}' for x in v), '|', f"{o['shipments']:6.1f} {o['inventory_supplier']:6.1f} {o['inventory_retail']:6.1f}")
