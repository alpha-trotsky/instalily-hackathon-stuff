"""Round-2 decision rules + battery numbers for hospital_queue (free). Run from KIT."""
import json, sys
import numpy as np
from scipy.optimize import curve_fit
sys.path.insert(0, '.')
from greybox.common import core
sys.path.insert(0, 'fits/round2')
import heldout

S = 'hospital_queue'
names, sig = heldout.sigma(S)
model = core.load_model('fits/round2/v1_models/hospital_queue/hospital_queue_model.py')
FITS = {'final_m12 (v1)': 'fits/hospital_queue/final_m12.json', 'v5_base': 'fits/hospital_queue/v5_base_all.json'}
eps = core.load_episodes(['data/hospital_queue/R3.json', 'data/hospital_queue/R4.json'], model=model)


def P(f):
    d = json.load(open(f)); return d['params'] if 'params' in d else d


preds = {}
for ep, r in zip(eps, ['R3', 'R4']):
    preds[r] = {k: core.rollout(model, P(f), ep) for k, f in FITS.items()}
    preds[r]['obs'] = np.array(ep['y']) if 'y' in ep else None

raw = {}
for r in ['R3', 'R4']:
    d = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    raw[r] = np.array([[x[n] for n in names] for x in d['observations']])

SEG = {'R3': [(0, 50, 'electives 5'), (50, 100, 'electives 10'), (100, 150, 'staffing 15 + el 10'),
              (150, 200, 'staffing 15 alone'), (200, 250, 'recovery')],
       'R4': [(0, 90, 'joint .7'), (90, 140, 'recovery 50'), (140, 200, 'joint 1'), (200, 275, 'recovery +75'),
              (275, 350, 'recovery +150')]}
print('sigma', sig.round(3))
for r, segs in SEG.items():
    print('==', r)
    for a, b, lab in segs:
        o = raw[r][b - 10:b].mean(0)
        row = f'{a:3d}-{b:3d} {lab:22s} data {np.round(o, 2)}'
        for k in FITS:
            p = preds[r][k][b - 10:b].mean(0)
            row += f' | {k} {np.round(p, 2)} ({np.round((p - o) / sig, 1)}s)'
        print(row)
        # slopes over segment (per tick) last 20 ticks
        t = np.arange(b - 20, b)
        sl = [np.polyfit(t, raw[r][b - 20:b, j], 1)[0] for j in range(3)]
        print('      slope last 20 (per tick):', np.round(sl, 3), ' mean over seg:', raw[r][a:b].mean(0).round(2))

# H1 extra: R3 electives 5 phases
o = raw['R3']
print('\nH1 R3 electives-5 phases: 3-30 mean', o[3:30].mean(0).round(2), '30-50', o[30:50].mean(0).round(2))
# H2: drain rate at staffing 15 alone
q = o[150:200, 1]; print('H2 queue slope 150-200', np.polyfit(np.arange(50), q, 1)[0].round(3), 'disch', o[150:200, 2].mean().round(2))
# H3: exponential fit to R4 recovery queue 200-349
q = raw['R4'][200:350, 1]; t = np.arange(150.)
f = lambda t, qi, q0, tau: qi + (q0 - qi) * np.exp(-t / tau)
for lo in (0, 50, 100):
    try:
        pp, _ = curve_fit(f, t[lo:], q[lo:], p0=[50, q[lo], 80], maxfev=20000)
        print(f'H3 exp fit from +{lo}: asymptote {pp[0]:.1f}, q0 {pp[1]:.1f}, tau {pp[2]:.1f}')
    except Exception as e:
        print('fit fail', e)
for k in FITS:
    p = preds['R4'][k][200:350, 1]
    pp, _ = curve_fit(f, t, p, p0=[50, p[0], 80], maxfev=20000)
    print(f'H3 {k} model exp fit: asymptote {pp[0]:.1f}, tau {pp[2]:.1f}; model queue at 349 {p[-1]:.1f}')
# linear drain rates in the tail
for a, b in [(200, 250), (250, 305), (310, 340), (340, 350)]:
    print(f'R4 queue slope {a}-{b}:', np.polyfit(np.arange(b - a), raw['R4'][a:b, 1], 1)[0].round(3),
          'disch mean', raw['R4'][a:b, 2].mean().round(3), 'wait mean', raw['R4'][a:b, 0].mean().round(2))
# R3 recovery drain
print('R3 queue slope 200-250', np.polyfit(np.arange(50), raw['R3'][200:250, 1], 1)[0].round(3))
# model hidden states: Lq at end of R4
json.dump({r: {k: v[-1].round(2).tolist() for k, v in preds[r].items() if v is not None} for r in preds},
          open('fits/hospital_queue/round2/rules_end.json', 'w'))
