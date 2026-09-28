from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from cands import cand
m = v1(); sig = sigma()
for r in ['R3', 'R4', 'R5', 'R1', 'R2']:
    run, o, a = load_run(r); p = predict(m, run); p12 = cand('m12_all', run)
    fig, ax = plt.subplots(4, 1, figsize=(12, 11), sharex=True, gridspec_kw=dict(height_ratios=[3, 3, 1.6, 1.6]))
    t = np.arange(len(o))
    for j, n in enumerate(OBS):
        ax[j].plot(t, o[:, j], 'k', lw=1.4, label='data')
        ax[j].plot(t, p[:, j], 'C3', lw=1.2, label='v1 (shipped, m13_all)')
        ax[j].plot(t, p12[:, j], 'C0--', lw=1, label='m12_all (candidate)')
        ax[j].set_ylabel(n); ax[j].grid(alpha=.3)
    ax[0].legend(loc='upper right', fontsize=8)
    for j, n in enumerate(OBS):
        ax[2].plot(t, (p[:, j] - o[:, j]) / sig[j], label=f'v1 err/σ {n}')
    ax[2].axhline(0, c='k', lw=.5); ax[2].set_ylabel('v1 err / σ'); ax[2].legend(fontsize=8); ax[2].grid(alpha=.3)
    ax[3].step(t, a[:, 0] + 0.03, where='post', label='school_closure (+0.03 offset)'); ax[3].step(t, a[:, 1], where='post', label='mask_mandate')
    ax[3].step(t, a[:, 2] / 0.003 - 0.03, where='post', label='vaccination_rate / 0.003 (-0.03 offset)'); ax[3].set_ylim(-.05, 1.1)
    ax[3].legend(fontsize=8); ax[3].set_ylabel('controls (u)'); ax[3].set_xlabel('tick')
    for s, e, _ in segs(run):
        for x in ax: x.axvline(s, c='grey', lw=.5, ls=':')
    sc = (1 / (1 + np.abs(p - o) / sig)).mean(0)
    fig.suptitle(f'epidemic {r}  initial {run["initial"]["daily_cases"]:.1f}/{run["initial"]["hospital_load"]:.1f}   v1 score cases {sc[0]:.3f} hosp {sc[1]:.3f}  (σ = {sig[0]:.2f}, {sig[1]:.2f})')
    fig.tight_layout(); fig.savefig(f'fits/epidemic/round2/{r}_v1.png', dpi=90); plt.close(fig)
print('ok')
