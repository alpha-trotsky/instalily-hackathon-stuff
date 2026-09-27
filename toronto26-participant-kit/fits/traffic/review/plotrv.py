"""python fits/traffic/review/plotrv.py OUT_PREFIX MODEL.py FIT.json [MODEL2.py FIT2.json]  -> OUT_PREFIX_R1.png, _R2.png
Top 4 panels: data (black) and fits; panels 5-8: error / score sigma (clipped to +-10)."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from greybox.common import core
out = sys.argv[1]; pairs = list(zip(sys.argv[2::2], sys.argv[3::2]))
eps0 = core.load_episodes(['data/traffic/R1.json', 'data/traffic/R2.json'])
sig = core.score_sigma(eps0)
for k, tag in enumerate(['R1', 'R2']):
    fig, ax = plt.subplots(8, 1, figsize=(14, 18), sharex=True)
    for j, (mp, fp) in enumerate(pairs):
        m = core.load_model(mp)
        ep = core.load_episodes(['data/traffic/%s.json' % tag], model=m)[0]
        pr = core.rollout(m, json.load(open(fp))['params'], ep)
        t = np.arange(len(ep['obs']))
        for i, n in enumerate(ep['names']):
            if j == 0:
                ax[i].plot(t, ep['obs'][:, i], 'k-', lw=0.5); ax[i].set_ylabel(n)
            ax[i].plot(t, pr[:, i], lw=1.1, label=fp.split('/')[-1])
            ax[4 + i].plot(t, np.clip((pr[:, i] - ep['obs'][:, i]) / sig[i], -10, 10), lw=0.6)
            ax[4 + i].set_ylabel('err/σ ' + n); ax[4 + i].axhline(0, color='grey', lw=0.5)
    ax[0].legend(fontsize=7)
    plt.tight_layout(); plt.savefig('%s_%s.png' % (out, tag), dpi=60); plt.close()
print('ok')
