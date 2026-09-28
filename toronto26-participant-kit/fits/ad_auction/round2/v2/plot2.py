"""Plot data (black) vs fits on R1,R2c,R3,R4. usage: plot2.py out.png fit1.json [fit2.json] [--model M]"""
import sys, json, numpy as np
sys.path.insert(0, '.')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from greybox.common import core
args = sys.argv[1:]; mp = 'greybox/ad_auction_model_v2.py'
if '--model' in args:
    i = args.index('--model'); mp = args[i + 1]; del args[i:i + 2]
out, fits = args[0], args[1:]
model = core.load_model(mp)
ref = core.load_episodes([f'data/ad_auction/{r}.json' for r in ('R1', 'R2c', 'R3', 'R4')], model=model)
fig, ax = plt.subplots(3, 4, figsize=(24, 10))
for j, ep in enumerate(ref):
    for i in range(3):
        ax[i, j].plot(ep['obs'][:, i], 'k', lw=.8)
    for f, c in zip(fits, ['r', 'b', 'g']):
        d = json.load(open(f)); p = core.params_for(model, set(d['modules']), d['params'])
        y = core.rollout(model, p, ep)
        for i in range(3):
            ax[i, j].plot(y[:, i], c, lw=.8, label=f.split('/')[-1])
    ax[0, j].set_title(ep['source'].split('/')[-1])
ax[0, 0].legend()
fig.tight_layout(); fig.savefig(out, dpi=70)
