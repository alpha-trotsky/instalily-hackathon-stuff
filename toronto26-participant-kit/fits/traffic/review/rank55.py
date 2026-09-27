"""Rank <=55-step reserve probes (fresh reset) by disagreement between fitted models (mean |diff|/score-sigma, 4 obs summed).
python fits/traffic/review/rank55.py MODEL:FIT ..."""
import sys, json, itertools
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
eps = core.load_episodes(['data/traffic/R1.json', 'data/traffic/R2.json'])
sig = core.score_sigma(eps); bounds = eps[0]['bounds']
REC = {'signal_timing': 0.5, 'lane_closure': 0.0, 'toll': 5.0, 'ramp_metering': 0.0, 'freight_priority': 0.5, 'clearance_effort': 1.0}
PUL = {'signal_timing': 0.15, 'lane_closure': 0.65, 'toll': 0.0, 'ramp_metering': 1.0, 'freight_priority': 1.0, 'clearance_effort': 0.0}
def act(**kw):
    a = dict(REC); a.update(kw); return a
def frac(u):
    return {k: REC[k] + u * (PUL[k] - REC[k]) for k in REC}
C = {
 'toll2.5_ramp1_x55': [act(ramp_metering=1.0, toll=2.5)] * 55,
 'toll1.5_ramp1_x55': [act(ramp_metering=1.0, toll=1.5)] * 55,
 'toll3.5_ramp1_x55': [act(ramp_metering=1.0, toll=3.5)] * 55,
 'joint_u0.7_x55': [frac(0.7)] * 55,
 'joint_u0.85_x55': [frac(0.85)] * 55,
 'toll0_fr0_ramp1_x55': [act(ramp_metering=1.0, toll=0.0, freight_priority=0.0)] * 55,
 'toll0_ramp1_x35_then_ce0_x20': [act(ramp_metering=1.0, toll=0.0)] * 35 + [act(ramp_metering=1.0, toll=0.0, clearance_effort=0.0)] * 20,
 'toll0_ramp1_x35_then_rec_x20': [act(ramp_metering=1.0, toll=0.0)] * 35 + [act()] * 20,
 'toll0_lane.65_ramp1_x55': [act(ramp_metering=1.0, toll=0.0, lane_closure=0.65)] * 55,
 'ramp1_sig0.15_toll2.5_x55': [act(ramp_metering=1.0, toll=2.5, signal_timing=0.15)] * 55,
}
models = []
for spec in sys.argv[1:]:
    mp, fp = spec.split(':')
    models.append((fp.split('/')[-1], core.load_model(mp), json.load(open(fp))['params']))
init = {'flow_a': 37.5, 'flow_b': 37.5, 'speed_a': 37.5, 'speed_b': 37.5}
rows = []
for name, acts in C.items():
    preds = []
    for tag, m, p in models:
        u = [m.normalize(a, bounds) for a in acts]
        preds.append(np.asarray(m.simulate(p, init, u)))
    dis = max(float(np.mean(np.abs(a - b) / sig, axis=0).sum()) for a, b in itertools.combinations(preds, 2))
    ends = ' | '.join('%s %s' % (t[:10], np.round(pr[-10:].mean(0), 1).tolist()) for (t, _, _), pr in zip(models, preds))
    rows.append((dis, name, ends))
for d, n, e in sorted(rows, reverse=True):
    print('%-32s dis %.2f  end: %s' % (n, d, e))
