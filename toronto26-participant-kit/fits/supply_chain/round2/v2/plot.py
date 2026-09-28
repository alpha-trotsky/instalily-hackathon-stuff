import json, sys, os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.getcwd())
from greybox.common import core
f = json.load(open(sys.argv[1])); model = core.load_model(sys.argv[2]); runs = sys.argv[3].split(',')
fig, ax = plt.subplots(3 * len(runs), 1, figsize=(13, 4.2 * len(runs)))
for i, r in enumerate(runs):
    ep = core.load_episodes([f'data/supply_chain/{r}.json'], model=model)[0]
    y = core.rollout(model, f['params'], ep)
    for k in range(3):
        a = ax[3 * i + k]; a.plot(ep['obs'][:, k], 'k', lw=.7); a.plot(y[:, k], 'r', lw=.8); a.set_ylabel(f'{r} {ep["names"][k][:12]}'); a.grid(alpha=.3)
fig.tight_layout(); fig.savefig(sys.argv[4], dpi=70)
