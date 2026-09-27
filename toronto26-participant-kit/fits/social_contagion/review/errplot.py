"""Review: overlay fits on R1 and R2 with log-error panels.
python fits/social_contagion/review/errplot.py out.png fit1.json [fit2.json ...]  (PYTHONPATH=.)"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from greybox import social_contagion_model as m
from greybox.common import core

out, fits = sys.argv[1], sys.argv[2:]
runs = ['data/social_contagion/R1.json', 'data/social_contagion/R2.json']
fig, ax = plt.subplots(4, 2, figsize=(16, 11), sharex='col')
for j, path in enumerate(runs):
    d = json.load(open(path)); r = d['runs'][0]
    obs = np.array([[o[k] for k in m.OBSERVABLES] for o in r['observations']])
    u = [m.normalize(a, d['brief']['interventions']) for a in r['actions']]
    sig = 0.1 * obs[20:].std(axis=0)
    for i in range(2):
        ax[i, j].plot(obs[:, i], 'k.', ms=2)
        ax[i, j].set_ylabel(m.OBSERVABLES[i]); ax[i + 2, j].set_ylabel('log err ' + m.OBSERVABLES[i])
        ax[i + 2, j].axhline(0, color='k', lw=0.5)
    for f in fits:
        fj = json.load(open(f))
        p = core.params_for(m, set(fj['modules']), fj['params'])
        pred = m.simulate(p, r['initial'], u)
        sc = float(np.mean(1 / (1 + np.abs(pred - obs) / sig)))
        lab = f"{f.split('/')[-1]} {path[-7:-5]} score {sc:.3f}"
        print(lab)
        for i in range(2):
            ax[i, j].plot(pred[:, i], lw=1, label=lab if i == 0 else None)
            ax[i + 2, j].plot(np.log(pred[:, i] / obs[:, i]), lw=1)
    ax[0, j].legend(fontsize=7); ax[0, j].set_title(path)
    U = np.array(u)
    for t in np.nonzero(np.any(np.diff(U, axis=0) != 0, axis=1))[0]:
        for i in range(4):
            ax[i, j].axvline(t + 1, color='grey', lw=0.4, ls='--')
plt.tight_layout(); plt.savefig(out, dpi=75)
