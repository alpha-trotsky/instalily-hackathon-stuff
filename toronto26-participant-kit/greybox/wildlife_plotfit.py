import sys, json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from greybox.common import core
# usage: plotfit.py out.png data.json fit1.json [fit2.json ...]
out, data, fits = sys.argv[1], sys.argv[2], sys.argv[3:]
m = core.load_model('greybox/wildlife_model.py')
ep = core.load_episodes([data], model=m)[0]
obs = ep['obs']; names = ep['names']
fig, ax = plt.subplots(5, 1, figsize=(12, 13), sharex=True)
for i, n in enumerate(names):
    ax[i].plot(obs[:, i], 'k', lw=1, label='data')
    ax[i].set_ylabel(n)
for f in fits:
    fj = json.load(open(f)); p = core.params_for(m, set(fj.get('modules', [])), fj['params'])
    y = core.rollout(m, p, ep)
    for i in range(4):
        ax[i].plot(y[:, i], lw=1, label=f.split('/')[-1] + f" {fj['cost']:.0f}")
ax[0].legend(fontsize=8)
U = np.array(ep['u']) if 'u' in ep else np.array([m.normalize(a, {}) for a in json.load(open(data))['runs'][0]['actions']])
ax[4].plot(U); ax[4].legend(m.CONTROLS, fontsize=8)
plt.tight_layout(); plt.savefig(out, dpi=70)
