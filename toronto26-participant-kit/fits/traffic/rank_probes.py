"""Run-2 probe ranking (framework §4.4): simulate candidate schedules through the Run-1 pair fits and rank by
disagreement in score-sigma units per step.  python fits/traffic/rank_probes.py FIT1 FIT2 FIT3"""
import sys, json, itertools
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core

model = core.load_model('greybox/traffic_model.py')
fits = [json.load(open(f)) for f in sys.argv[1:]]
names = [f.split('/')[-1].replace('.json', '') for f in sys.argv[1:]]
bounds = json.load(open('data/traffic/R1.json'))['brief']['interventions']
SIG = np.array([0.94, 0.61, 1.28, 1.08])     # score sigma = 0.1 x std (R1, after tick 20)
REC = dict(model.RECOVERY)
init = {'flow_a': 37.0, 'flow_b': 34.0, 'speed_a': 42.0, 'speed_b': 36.0}


def act(**kw):
    a = dict(REC); a.update(kw); return a


D = dict(ramp_metering=1.0)
JOINT = dict(signal_timing=0.15, lane_closure=0.65, toll=0.0, ramp_metering=1.0, freight_priority=1.0,
             clearance_effort=0.0)
P0 = [(30, act())]
CANDS = {
    'P2 ramp 0.5 (60)':               [(60, act(ramp_metering=0.5))],
    'P2 ramp 0.5 + signal 0.9 (60)':  [(60, act(ramp_metering=0.5)), (60, act(ramp_metering=0.5, signal_timing=0.9))],
    'P9a ramp 0.72 + toll 0 (70)':    [(70, act(ramp_metering=0.72, toll=0.0))],
    'P2 toll 2.5 at D (60)':          [(60, act(ramp_metering=1.0, toll=2.5))],
    'joint pulse 200 + release 40':   [(200, act(**JOINT)), (40, act())],
    'P5 joint 60, gap 30, joint 60':  [(60, act(**JOINT)), (30, act()), (60, act(**JOINT))],
    'P9b clearance: joint 100, ramp0+ce1 30': [(100, act(**JOINT)), (30, act(**{**JOINT, 'ramp_metering': 0.0, 'clearance_effort': 1.0}))],
    'P9b signal rev: joint 100, ramp0+sig0.85 30': [(100, act(**JOINT)), (30, act(**{**JOINT, 'ramp_metering': 0.0, 'signal_timing': 0.85}))],
    "P5' clearance toggles at D+toll0 (100)": [(40, act(ramp_metering=1.0, toll=0.0))] + [(10, act(ramp_metering=1.0, toll=0.0, clearance_effort=c)) for c in (0, 1, 0, 1, 0, 1)],
    'P6 lane then toll (60+60)':      [(60, act(ramp_metering=1.0, lane_closure=0.65)), (60, act(ramp_metering=1.0, toll=0.0))],
    'P6 toll then lane (60+60)':      [(60, act(ramp_metering=1.0, toll=0.0)), (60, act(ramp_metering=1.0, lane_closure=0.65))],
    'P7 D+toll0 long hold 250':       [(250, act(ramp_metering=1.0, toll=0.0))],
    'P8 signal 0.3 at D (80)':        [(80, act(ramp_metering=1.0, signal_timing=0.3))],
}


def expand(segs):
    out = []
    for n, a in segs:
        out += [a] * n
    return out


rows = []
for name, segs in CANDS.items():
    acts = expand(P0) + expand(segs)
    ep = {'initial': init, 'u': [model.normalize(a, bounds) for a in acts], 'names': list(model.OBSERVABLES)}
    preds = [core.rollout(model, f['params'], ep)[30:] for f in fits]
    dis = []
    for i, j in itertools.combinations(range(len(preds)), 2):
        dis.append(np.nanmean(np.abs(preds[i] - preds[j]) / SIG, axis=0))
    dis = np.array(dis)                      # pair x obs, mean per tick
    steps = len(acts) - 30
    total = dis.sum(axis=1) * steps          # summed over obs and ticks
    rows.append((name, steps, dis.mean(axis=1).max(), total.max() / steps,
                 ' '.join(f'{names[i][:3]}-{names[j][:3]}:{d.mean():.2f}' for (i, j), d in
                          zip(itertools.combinations(range(len(preds)), 2), dis))))
rows.sort(key=lambda r: -r[3])
print(f'{"probe":45s} steps  maxpair(sig/obs/tick)  per-step  pairs')
for r in rows:
    print(f'{r[0]:45s} {r[1]:5d}  {r[2]:8.3f}  {r[3]:8.3f}  {r[4]}')
