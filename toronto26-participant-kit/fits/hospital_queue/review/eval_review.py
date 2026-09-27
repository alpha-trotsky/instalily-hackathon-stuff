"""Reviewer helper: simulate fitted params on R1/R2, plot fit + errors, print per-window errors in score-sigma units.
Usage (from KIT): python fits/hospital_queue/review/eval_review.py tag1=fit1.json tag2=fit2.json ...
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location('hq', 'greybox/hospital_queue_model.py')
hq = importlib.util.module_from_spec(spec); spec.loader.exec_module(hq)

OBS = hq.OBSERVABLES
runs = {}
for r in ('R1', 'R2'):
    d = json.load(open(f'data/hospital_queue/{r}.json'))['runs'][0]
    y = np.array([[o[k] for k in OBS] for o in d['observations']])
    u = [hq.normalize(a, {}) for a in d['actions']]
    runs[r] = (d['initial'], u, y, d['actions'])
allY = np.vstack([v[2][20:] for v in runs.values()])
SIG = 0.1 * allY.std(axis=0)
print('score sigma', dict(zip(OBS, np.round(SIG, 3))))

fits = [a.split('=', 1) for a in sys.argv[1:]]
WIN = {'R1': [(0, 60), (60, 175), (175, 240), (240, 310), (310, 350), (350, 410), (410, 470), (470, 530), (530, 580),
              (580, 650), (650, 750)],
       'R2': [(0, 30), (30, 110), (110, 140), (140, 220), (220, 290), (290, 320), (320, 350), (350, 380), (380, 455),
              (455, 500)]}
preds = {}
for tag, path in fits:
    p = json.load(open(path))['params']
    for r, (ini, u, y, _) in runs.items():
        preds[(tag, r)] = hq.simulate(p, ini, u)
for r, (ini, u, y, _) in runs.items():
    print(f'\n== {r}: mean |err|/sigma per window (wait, queue, discharges) and score')
    for tag, _ in fits:
        P = preds[(tag, r)]
        e = np.abs(P - y) / SIG
        sc = (1 / (1 + e)).mean()
        row = ' '.join(f'{a}-{b}:' + '/'.join(f'{x:.1f}' for x in e[a:b].mean(0)) for a, b in WIN[r])
        print(f'{tag:>8} score {sc:.3f} | {row}')
    fig, ax = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
    for i, k in enumerate(OBS):
        ax[i].plot(y[:, i], 'k-', lw=0.8, label='data')
        for tag, _ in fits:
            ax[i].plot(preds[(tag, r)][:, i], lw=1.0, label=tag)
        ax[i].set_ylabel(k)
    for tag, _ in fits:
        e = (preds[(tag, r)] - y) / SIG
        ax[3].plot(np.abs(e).mean(1), lw=0.8, label=tag)
    ax[3].set_ylabel('mean |err|/score-sigma'); ax[3].set_yscale('log')
    ax[0].legend(fontsize=7)
    for a, b in WIN[r]:
        for aa in ax: aa.axvline(a, color='0.8', lw=0.5, ls='--')
    fig.suptitle(f'{r}: review fits ' + ', '.join(t for t, _ in fits))
    fig.tight_layout()
    out = f'fits/hospital_queue/review/{r}_' + '_'.join(t for t, _ in fits) + '.png'
    fig.savefig(out, dpi=80); print('saved', out)
