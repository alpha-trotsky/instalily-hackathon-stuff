"""Plot every traffic run with the v1 prediction; one panel per observable + controls + error in score sigma."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from common import *
U_PUL = {'signal_timing': 0.15, 'lane_closure': 0.65, 'toll': 0.0, 'ramp_metering': 1.0, 'freight_priority': 1.0, 'clearance_effort': 0.0}
U_REC = {'signal_timing': 0.5, 'lane_closure': 0.0, 'toll': 5.0, 'ramp_metering': 0.0, 'freight_priority': 0.5, 'clearance_effort': 1.0}
for name in ['R4', 'R5', 'R1', 'R2', 'R3']:
    r, o, a = run(name); p = pred(r); T = len(o); t = np.arange(T)
    segs = segments(r, a)
    fig, ax = plt.subplots(6, 1, figsize=(14, 16), sharex=True)
    for i, n in enumerate(OBS):
        ax[i].plot(t, o[:, i], 'k.', ms=2.5, label='data'); ax[i].plot(t, o[:, i], 'k-', lw=0.4, alpha=0.4)
        ax[i].plot(t, p[:, i], 'r-', lw=1, label='v1')
        ax[i].set_ylabel(n); ax[i].grid(alpha=.3)
        for s, e, _ in segs: ax[i].axvline(s, color='b', lw=.5, alpha=.4)
    ax[0].legend(loc='upper right')
    for i, n in enumerate(OBS):
        ax[4].plot(t, (p[:, i] - o[:, i]) / SIG[i], lw=.8, label=n)
    ax[4].axhline(0, color='k', lw=.5); ax[4].set_ylabel('err / score sigma'); ax[4].legend(ncol=4, fontsize=8); ax[4].grid(alpha=.3)
    ax[4].set_ylim(-25, 25)
    for j, c in enumerate(CTRL):
        u = (a[:, j] - U_REC[c]) / (U_PUL[c] - U_REC[c])
        ax[5].step(t, u + 0.0 * j, where='post', label=c)
    ax[5].set_ylabel('u (0 rec, 1 pulse)'); ax[5].legend(ncol=6, fontsize=7); ax[5].set_xlabel('tick'); ax[5].grid(alpha=.3)
    for s, e, act in segs:
        ax[0].text(s + 1, ax[0].get_ylim()[1] * 0.97, label(act), fontsize=6, va='top', rotation=0)
    fig.suptitle(f'traffic {name}: data (black) vs v1 (red)')
    fig.tight_layout(); fig.savefig(f'fits/traffic/round2/{name}_v1.png', dpi=90); plt.close(fig)
    print('saved', name)
