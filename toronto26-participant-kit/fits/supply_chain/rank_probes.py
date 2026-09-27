"""Rank candidate supply_chain Run-2 probes by disagreement between the fitted pair models.
Disagreement = mean |pred_a - pred_b| / score sigma over the probe ticks (after a 30-tick P0), summed over pairs;
reported per 100 steps and as the smallest pairwise value (a probe must separate every pair)."""
import json, sys, itertools
import numpy as np
sys.path.insert(0, '.')
import greybox.supply_chain_model as M
REC = dict(M.RECOVERY); PUL = dict(M.PULSE)
BOUNDS = {'order_quantity': [0, 80], 'lead_time_buy': [0, 1], 'product_mix': [0, 1], 'production_effort': [0, 1.5],
          'receiving_effort': [0, 1.5], 'maintenance': [0, 1]}
def A(**kw):
    a = dict(REC); a.update(kw); return a
D = dict(order_quantity=80)
CANDS = {
  'P7 D+maint0 hold 200': [(200, A(**D, maintenance=0))],
  'P7 D hold 200': [(200, A(**D))],
  'P7 all-pulse hold 200': [(200, dict(PUL))],
  'P9a maint-then-idle after D+m0 80': [(80, A(**D, maintenance=0)), (30, A(**D)), (40, A(**D, maintenance=0)),
                                         (30, A(maintenance=0, production_effort=0)), (40, A(**D, maintenance=0))],
  'P9a idle-then-maint after D+m0 80': [(80, A(**D, maintenance=0)), (30, A(maintenance=0, production_effort=0)),
                                   (40, A(**D, maintenance=0)), (30, A(**D)), (40, A(**D, maintenance=0))],
  'P9c prod high->low under D': [(60, A(**D, production_effort=1.5)), (60, A(**D, production_effort=0.5)), (40, A())],
  'P9c prod low->high under D': [(60, A(**D, production_effort=0.5)), (60, A(**D, production_effort=1.5)), (40, A())],
  'P5 short gap orders (20)': [(50, A(**D)), (20, A()), (50, A(**D)), (40, A())],
  'P5 long gap orders (80)': [(50, A(**D)), (80, A()), (50, A(**D)), (40, A())],
  'P9b rush at order start': [(40, A(**D, lead_time_buy=0.2)), (40, A())],
  'P9b rush after dispatch': [(20, A(**D)), (40, A(**D, lead_time_buy=0.2)), (40, A())],
  'P2 orders 40': [(60, A(order_quantity=40)), (40, A())],
  'P2 orders 20': [(60, A(order_quantity=20)), (40, A())],
  'mix low 0.2 under D': [(50, A(**D, product_mix=0.2)), (30, A(**D))],
  'production 0 under D': [(50, A(**D, production_effort=0)), (30, A(**D))],
  'rush long under D 100': [(100, A(**D, lead_time_buy=0.2)), (50, A(**D))],
  'all-pulse 60 + recovery 60': [(60, dict(PUL)), (60, A())],
  'all-pulse 60 + gap 20 + all-pulse 40': [(60, dict(PUL)), (20, A()), (40, dict(PUL)), (40, A())],
}
fits = {k: json.load(open(f'fits/supply_chain/{k}.json'))['params'] for k in sys.argv[1:]}
sig = np.array([1.5, 13.0, 28.0])
init = {'shipments': 25.0, 'inventory_supplier': 100.0, 'inventory_retail': 100.0}
rows = []
for name, blocks in CANDS.items():
    acts = [A()] * 30
    for n, a in blocks: acts += [a] * n
    u = [M.normalize(a, BOUNDS) for a in acts]
    preds = {k: M.simulate(p, init, u) for k, p in fits.items()}
    dis = {f'{a}/{b}': float(np.mean(np.abs(preds[a] - preds[b])[30:] / sig)) for a, b in itertools.combinations(preds, 2)}
    rows.append((sum(dis.values()) / (len(acts) - 30) * 100, min(dis.values()), name, len(acts) - 30, dis))
for per, mn, name, n, dis in sorted(rows, key=lambda r: -r[1]):
    print(f'min {mn:5.2f}  per100 {per:5.2f}  {name:38s} {n:4d}st  ' + '  '.join(f'{k} {v:.2f}' for k, v in dis.items()))
