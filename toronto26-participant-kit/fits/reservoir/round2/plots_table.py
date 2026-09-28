"""Plots of R4/R5 with v1 overlay; segment table (last-10 means); score-loss ranking (also old runs)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
OUT = 'fits/reservoir/round2'
m = load_pred()
loss_rows = []
for name in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a, segs = run(name); p = predict(m, r); T = len(o)
    sc = 1 / (1 + np.abs(p - o) / SIG)
    print(f'== {name}  T={T}  score by obs: ' + ' '.join(f'{n}={sc[:, j].mean():.3f}' for j, n in enumerate(NAMES)))
    for (s, e, act) in segs:
        lo = max(s, e - 10)
        om, pm = o[lo:e].mean(0), p[lo:e].mean(0)
        lab = ' '.join(f'{k[:3]}={act[k]:g}' for k in CTL)
        print(f'  [{s:3d}-{e-1:3d}] {lab:45s} obs ' + ' '.join(f'{v:8.4g}' for v in om) +
              ' | v1 ' + ' '.join(f'{v:8.4g}' for v in pm) + ' | err/sig ' + ' '.join(f'{(pm[j]-om[j])/SIG[j]:+6.1f}' for j in range(4)))
        for j, n in enumerate(NAMES):
            seg = slice(s, e); err = p[seg, j] - o[seg, j]
            lost = float((1 - sc[seg, j]).sum())
            # classify: level = mean err over second half / sd; transient = loss concentrated in first 20%
            n_t = e - s; h = slice(s + n_t // 2, e)
            first = float((1 - sc[s:s + max(1, n_t // 5), j]).sum())
            loss_rows.append(dict(run=name, s=s, e=e, obs=n, lost=lost, lost_first20=first,
                                  mean_err_2nd_half=float((p[h, j] - o[h, j]).mean() / SIG[j]),
                                  sd_err_2nd_half=float((p[h, j] - o[h, j]).std() / SIG[j]), act=lab))
    if name in ('R4', 'R5'):
        fig, ax = plt.subplots(5, 1, figsize=(12, 13), sharex=True)
        t = np.arange(T)
        for j, n in enumerate(NAMES):
            ax[j].plot(t, o[:, j], 'k.', ms=2, label='data')
            ax[j].plot(t, p[:, j], 'r-', lw=1, label='v1')
            if n == 'inflow': ax[j].plot(t, season(t + 1), 'b:', lw=0.8, label='season')
            ax[j].fill_between(t, p[:, j] - SIG[j], p[:, j] + SIG[j], color='r', alpha=0.15)
            ax[j].set_ylabel(n); ax[j].legend(fontsize=7, loc='best')
            for s, e, _ in segs: ax[j].axvline(s, color='g', lw=0.5)
        for c, lbl, k in [(0, 'release/12', 12), (1, 'irrigation/8', 8), (2, 'depth', 1), (3, 'aeration', 1)]:
            ax[4].plot(t, a[:, c] / k, label=lbl)
        ax[4].legend(fontsize=7); ax[4].set_ylabel('controls (norm)'); ax[4].set_xlabel('tick (0-based obs)')
        ax[0].set_title(f'reservoir {name}: data vs v1 (band = ±score σ)')
        fig.tight_layout(); fig.savefig(f'{OUT}/{name}_v1.png', dpi=90); plt.close(fig)
        # error plot
        fig, ax = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
        for j, n in enumerate(NAMES):
            e_ = (p[:, j] - o[:, j]) / SIG[j]
            ax[j].plot(t, e_, 'k-', lw=0.5); ax[j].plot(t, np.convolve(e_, np.ones(9) / 9, 'same'), 'r-')
            ax[j].axhline(1, ls=':'); ax[j].axhline(-1, ls=':'); ax[j].set_ylabel(f'{n} err/σ')
            for s, e, _ in segs: ax[j].axvline(s, color='g', lw=0.5)
        fig.tight_layout(); fig.savefig(f'{OUT}/{name}_err.png', dpi=90); plt.close(fig)
json.dump(loss_rows, open(f'{OUT}/loss_rows.json', 'w'), indent=0)
print('\n== score-loss ranking (new runs)')
new = sorted([x for x in loss_rows if x['run'] in ('R4', 'R5')], key=lambda x: -x['lost'])
tot = sum(x['lost'] for x in new)
for x in new[:20]:
    print(f"{x['run']} [{x['s']:3d}-{x['e']-1:3d}] {x['obs']:8s} lost={x['lost']:6.1f} ({100*x['lost']/tot:4.1f}%) first20%={x['lost_first20']:5.1f} "
          f"err2nd={x['mean_err_2nd_half']:+6.2f}σ sd={x['sd_err_2nd_half']:5.2f} {x['act']}")
print('total lost (new) =', round(tot, 1), 'of', sum(x['e'] - x['s'] for x in new), 'obs-ticks')
for n in NAMES:
    print(n, 'lost', round(sum(x['lost'] for x in new if x['obs'] == n), 1))
