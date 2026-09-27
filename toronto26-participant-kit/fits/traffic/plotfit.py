"""Plot fit(s) against data: python fits/traffic/plotfit.py OUT.png DATA.json[:i] FIT.json [FIT2.json ...]
Also works for a schedule-only prediction when DATA is a data file."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from greybox.common import core

out, data = sys.argv[1], sys.argv[2]
fits = sys.argv[3:]
model = core.load_model('greybox/traffic_model.py')
eps = core.load_episodes([data], model=model)
ep = eps[0]
fig, ax = plt.subplots(5, 1, figsize=(14, 13), sharex=True)
t = np.arange(len(ep['obs']))
for i, n in enumerate(ep['names']):
    ax[i].plot(t, ep['obs'][:, i], 'k-', lw=0.6, label='data')
    ax[i].set_ylabel(n)
for f in fits:
    fj = json.loads(open(f).read())
    pred = core.rollout(model, fj['params'], ep)
    for i in range(4):
        ax[i].plot(t, pred[:, i], lw=1.0, label=f.split('/')[-1])
ax[0].legend(fontsize=7)
U = np.array(ep['u'])
for j, c in enumerate(model.CONTROLS):
    ax[4].plot(t, U[:, j], label=c)
ax[4].legend(fontsize=7, ncol=3)
plt.tight_layout()
plt.savefig(out, dpi=70)
