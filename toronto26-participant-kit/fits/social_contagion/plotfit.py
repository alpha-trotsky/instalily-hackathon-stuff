"""Overlay fits on a data run: python fits/social_contagion/plotfit.py data.json out.png fit1.json [fit2.json ...]"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from greybox import social_contagion_model as m
from greybox.common import core

data, out, fits = sys.argv[1], sys.argv[2], sys.argv[3:]
d = json.load(open(data))
r = d['runs'][0]
obs = np.array([[o[k] for k in m.OBSERVABLES] for o in r['observations']])
u = [m.normalize(a, d['brief']['interventions']) for a in r['actions']]
sig = 0.1 * obs[20:].std(axis=0)
fig, ax = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
for i, o in enumerate(m.OBSERVABLES):
    ax[i].plot(obs[:, i], 'k.', ms=2, label='data')
    ax[i].set_ylabel(o)
for f in fits:
    fj = json.load(open(f))
    p = core.params_for(m, set(fj['modules']), fj['params'])
    pred = m.simulate(p, r['initial'], u)
    sc = float(np.mean(1 / (1 + np.abs(pred - obs) / sig)))
    for i in range(2):
        ax[i].plot(pred[:, i], lw=1, label=f"{f.split('/')[-1]} score {sc:.3f}")
ax[0].legend(fontsize=7)
U = np.array(u)
for j, c in enumerate(m.CONTROLS):
    ax[2].plot(U[:, j], label=c)
ax[2].legend(fontsize=7)
plt.tight_layout()
plt.savefig(out, dpi=80)
