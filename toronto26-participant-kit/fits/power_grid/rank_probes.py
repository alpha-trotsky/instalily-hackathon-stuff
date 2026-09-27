"""Rank Run-2 candidate probes by disagreement between the Run-1 pair fits (and module on/off variants),
in units of score sigma (0.1 x std of R1 observables after tick 20) per step of cost. Zero steps spent."""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from greybox import power_grid_model as m
from greybox.common import core

R = {'price_signal': 1.5, 'reserve_dispatch': 0.0, 'charging_allowance': 1.0, 'interconnector': 1.0}
PULSE = {'price_signal': 0.0, 'reserve_dispatch': 150.0, 'charging_allowance': 0.0, 'interconnector': 0.2}
def a(**kw): return {**R, **kw}
def hold(n, act): return [act] * n
def ramp(n, a0, a1): return [{k: a0[k] + (i + 1) / n * (a1[k] - a0[k]) for k in a0} for i in range(n)]

P0 = hold(40, R)
CANDS = {
 'C1 all-pulse 150 + release 60': hold(150, PULSE) + hold(60, R),
 'C1s all-pulse 60 + release 60': hold(60, PULSE) + hold(60, R),
 'C2 res150+ch0 100, off ch0 30, ch1 30, res150 30': hold(100, a(reserve_dispatch=150, charging_allowance=0)) + hold(30, a(charging_allowance=0)) + hold(30, R) + hold(30, a(reserve_dispatch=150)),
 'C3 ic 0 for 60, reopen 50': hold(60, a(interconnector=0.0)) + hold(50, R),
 'C4 price ramp 1.5->0 40, hold 30, ramp back 40': ramp(40, R, a(price_signal=0.0)) + hold(30, a(price_signal=0.0)) + ramp(40, a(price_signal=0.0), R),
 'C5 price 0.75 60, back 50': hold(60, a(price_signal=0.75)) + hold(50, R),
 'C6 reserve 60 for 100, off 40': hold(100, a(reserve_dispatch=60)) + hold(40, R),
 'C7 ic0.2, res150 40, res off 30, reopen 30': hold(10, a(interconnector=0.2)) + hold(40, a(reserve_dispatch=150, interconnector=0.2)) + hold(30, a(interconnector=0.2)) + hold(30, R),
 'C8 res150 ch1 40, gap 10, res150 40': hold(40, a(reserve_dispatch=150)) + hold(10, R) + hold(40, a(reserve_dispatch=150)),
}
data = json.load(open('data/power_grid/R1.json'))
bounds = data['brief']['interventions']
obs = np.array([[o[k] for k in m.OBSERVABLES] for o in data['runs'][0]['observations']])
sig = 0.1 * obs[20:].std(axis=0)
init = {'load': 105.0, 'frequency': 50.0, 'renewable_share': 0.3}

def load(name, **over):
    d = json.load(open(f'fits/power_grid/{name}_r1.json'))
    p = core.params_for(m, set(d['modules']), d['params']); p.update(over); return p
fits = {'m12': load('m12'), 'm13': load('m13'), 'm23': load('m23')}
# hypothetical "module on" variants for modules that the R1 fits left at ~0
fits['m12+M2hyp'] = load('m12', d2=1 / 150, c2=0.01, e2=0.3, g2L=0.3)
fits['m13-noM3'] = load('m13', g3=0.0)
fits['m13+M3hyp'] = load('m13', g3=1.5, a3=0.05)
comps = [('m12', 'm13'), ('m12', 'm23'), ('m13', 'm23'), ('m12', 'm12+M2hyp'), ('m13-noM3', 'm13+M3hyp'), ('m13-noM3', 'm13')]
rows = []
for name, sched in CANDS.items():
    acts = P0 + sched
    u = [m.normalize(x, bounds) for x in acts]
    Y = {k: m.simulate(p, init, u)[40:] for k, p in fits.items()}
    cost = len(sched)
    res = {f'{a_}|{b_}': float(np.mean(np.abs(Y[a_] - Y[b_]) / sig)) for a_, b_ in comps}
    rows.append((name, cost, res))
print('mean |diff| / score-sigma over the probe (P0 excluded); cost = probe steps')
hdr = ' '.join(f'{a_}|{b_}'[:16].rjust(17) for a_, b_ in comps)
print('probe'.ljust(50), 'cost', hdr)
for name, cost, res in rows:
    print(name[:50].ljust(50), str(cost).rjust(4), ' '.join(f'{v:17.2f}' for v in res.values()))
json.dump([{'probe': n, 'cost': c, 'disagreement': r} for n, c, r in rows], open('fits/power_grid/probe_ranking.json', 'w'), indent=1)
