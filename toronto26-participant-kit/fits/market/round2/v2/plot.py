"""Plot a v2 fit JSON (or several) over runs A, B, C.   python3 fits/market/round2/v2/plot.py out.png fit1.json [fit2.json]"""
import json, sys
sys.path.insert(0, '.')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from greybox.common import core
out, fits = sys.argv[1], sys.argv[2:]
model = core.load_model('greybox/market_model_v2.py')
names = ['price', 'volume', 'depth']
fig, ax = plt.subplots(3, 3, figsize=(18, 10))
for j, r in enumerate('ABC'):
    ep = core.load_episodes([f'data/market/{r}.json'], names=names, model=model)[0]
    for i, n in enumerate(names):
        ax[i, j].plot(ep['obs'][:, i], 'k.', ms=2)
        for f in fits:
            fj = json.load(open(f))
            ax[i, j].plot(core.rollout(model, fj['params'], ep)[:, i], lw=1.2, label=f.split('/')[-1])
        if n == 'volume': ax[i, j].set_ylim(1.3, 3.2)
        ax[i, j].set_title(f'{r} {n}')
ax[0, 0].legend(fontsize=7)
plt.tight_layout(); plt.savefig(out, dpi=80)
