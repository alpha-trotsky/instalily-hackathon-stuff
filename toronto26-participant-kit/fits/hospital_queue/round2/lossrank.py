"""Score-loss ranking with level/dynamics/transient classification (free). Run from KIT after diag.py."""
import json, sys, importlib.util
import numpy as np
sys.path.insert(0, 'fits/round2'); import heldout
S = 'hospital_queue'; names, sig = heldout.sigma(S)
ctx = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
spec = importlib.util.spec_from_file_location('v1p', f'fits/round2/v1_models/{S}/predict.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
SEG = {'R3': [(0, 50, 'el 5'), (50, 100, 'el 10'), (100, 150, 'st15+el10'), (150, 200, 'st15'), (200, 250, 'rec')],
       'R4': [(0, 90, 'joint .7'), (90, 140, 'rec 50'), (140, 200, 'joint 1'), (200, 275, 'rec +75'), (275, 350, 'rec +150')]}
rows = []; tot = {}
for r, segs in SEG.items():
    d = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in d['observations']])
    p = np.array([[x[n] for n in names] for x in mod.predict(d['initial'], d['actions'], ctx)])
    e = (p - o) / sig; L = 1 - 1 / (1 + np.abs(e))
    tot[r] = L.sum(0).round(1).tolist()
    for a, b, lab in segs:
        for j, n in enumerate(names):
            l = L[a:b, j]; ee = e[a:b, j]
            first = l[:20].sum() / max(l.sum(), 1e-9)
            lev = abs(ee.mean()) / max(np.abs(ee).mean(), 1e-9)
            # classify: level if sign-consistent (|mean|/mean|.| > .7) and loss spread (first-20 share < 20/len+0.15)
            share20 = 20 / (b - a)
            if lev > 0.7 and first < share20 + 0.2: kind = 'level'
            elif first > share20 + 0.2: kind = 'transient'
            else: kind = 'dynamics'
            rows.append(dict(run=r, seg=f'{a}-{b} {lab}', obs=n, loss=round(float(l.sum()), 1), signed=round(float(ee.mean()), 2),
                             absm=round(float(np.abs(ee).mean()), 2), end10=round(float(ee[-10:].mean()), 2),
                             first20_share=round(float(first), 2), kind=kind))
rows.sort(key=lambda x: -x['loss'])
print('total loss (tick-units) per run/obs', tot)
for x in rows: print(x)
json.dump(rows, open('fits/hospital_queue/round2/lossrank.json', 'w'), indent=1)
