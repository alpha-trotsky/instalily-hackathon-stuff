"""Plot fits (obs vs pred, errors in local-sigma units) on R1 and R2. usage: plotfit.py out.png fit1.json [fit2.json ...]"""
import sys, json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from greybox.common import core
model = core.load_model('greybox/ad_auction_model.py')
eps = core.load_episodes(['data/ad_auction/R1.json', 'data/ad_auction/R2.json'], model=model)
sig = core.score_sigma(eps)
out, fits = sys.argv[1], sys.argv[2:]
fig, axes = plt.subplots(7, 2, figsize=(18, 20), sharex='col')
for c, ep in enumerate(eps):
    O = ep['obs']; t = np.arange(len(O))
    for j in range(3):
        axes[2*j, c].plot(t, O[:, j], 'k', lw=0.8, label='obs')
        axes[2*j, c].set_ylabel(ep['names'][j])
    for f in fits:
        d = json.load(open(f)); P = core.rollout(model, d['params'], ep)
        lab = f.split('/')[-1].replace('.json', '')
        sc = core.score(P, O, sig)
        for j in range(3):
            axes[2*j, c].plot(t, P[:, j], lw=0.9, label='%s %.3f' % (lab, sc[j]))
            axes[2*j+1, c].plot(t, (P[:, j]-O[:, j])/sig[j], lw=0.8)
            axes[2*j+1, c].axhline(0, color='k', lw=0.5); axes[2*j+1, c].set_ylabel('err/sig')
        print(lab, ep['source'][-7:], 'score', np.round(sc, 3), 'mean %.3f' % sc.mean(), 'rmse', np.round(np.sqrt(np.mean((P-O)**2, 0)), 3))
    for j in range(3): axes[2*j, c].legend(fontsize=7)
    U = np.array([[a['bid']/5, a['budget_cap']/100, a['targeting_breadth']] for a in ep['actions']])
    axes[6, c].plot(t, U); axes[6, c].legend(['bid/5', 'cap/100', 'breadth'], fontsize=7)
    axes[0, c].set_title(ep['source'])
plt.tight_layout(); plt.savefig(out, dpi=70)
print('sigma', sig)
