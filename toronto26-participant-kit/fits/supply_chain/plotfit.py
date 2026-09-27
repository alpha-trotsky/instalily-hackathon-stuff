"""plotfit.py data.json out.png fit1.json [fit2.json ...]: observations vs fitted rollouts, one panel per observable."""
import json, sys
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from greybox.common import core
import greybox.supply_chain_model as M
ep = core.load_episodes([sys.argv[1]], model=M)[0]
fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
for i, n in enumerate(M.OBSERVABLES):
    ax[i].plot(ep['obs'][:, i], color='k', lw=0.8, label='obs'); ax[i].set_ylabel(n)
for f, c in zip(sys.argv[3:], ['#eb6834', '#1baf7a', '#4a3aa7', '#e87ba4']):
    pr = core.rollout(M, json.load(open(f))['params'], ep)
    for i in range(3): ax[i].plot(pr[:, i], color=c, lw=1, label=f.split('/')[-1])
ax[0].legend(fontsize=8); plt.tight_layout(); plt.savefig(sys.argv[2], dpi=80)
