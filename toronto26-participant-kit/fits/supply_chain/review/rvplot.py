"""rvplot.py out.png model.py:fit.json [model.py:fit.json ...] -- obs vs fits and errors (score-sigma units), R1 and R2.
Run from the kit folder. Prints per-run scores (sigma = 0.1 x std over R1+R2)."""
import json, sys
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from greybox.common import core

DATA = ['data/supply_chain/R1.json', 'data/supply_chain/R2.json']
out = sys.argv[1]
fits = []
for arg in sys.argv[2:]:
    fits.append(tuple(arg.split(':', 1)))
colors = ['#eb6834', '#1baf7a', '#4a3aa7', '#e87ba4', '#888888']
fig, ax = plt.subplots(6, 2, figsize=(18, 16), sharex='col')
sig = None
for j, (mpath, fpath) in enumerate(fits):
    M = core.load_model(mpath)
    eps = core.load_episodes(DATA, model=M)
    if sig is None:
        sig = core.score_sigma(eps)
    f = json.load(open(fpath))
    p = core.params_for(M, f['modules'], f['params'])
    tot = []
    for c, ep in enumerate(eps):
        pr = core.rollout(M, p, ep)
        s = core.score(pr, ep['obs'], sig)
        tot.append(s)
        for i in range(3):
            if j == 0:
                ax[2 * i, c].plot(ep['obs'][:, i], 'k', lw=0.7)
                ax[2 * i, c].set_ylabel(M.OBSERVABLES[i])
            ax[2 * i, c].plot(pr[:, i], color=colors[j], lw=1, label=fpath.split('/')[-1])
            ax[2 * i + 1, c].plot((pr[:, i] - ep['obs'][:, i]) / sig[i], color=colors[j], lw=0.7)
            ax[2 * i + 1, c].set_ylabel('err/sigma')
            ax[2 * i + 1, c].set_ylim(-40, 40)
    print(fpath, 'cost %.0f' % f['cost'], 'R1', np.round(tot[0], 3), 'R2', np.round(tot[1], 3),
          'mean %.3f' % np.mean(tot))
ax[0, 0].legend(fontsize=7)
plt.tight_layout(); plt.savefig(out, dpi=70)
