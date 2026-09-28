"""Round-2 diagnosis for power_grid (no steps). Plots R3/R4 with v1 overlay, segment tables, score-loss ranking."""
import sys, json
sys.path.insert(0, 'fits/power_grid/round2')
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
OUT = 'fits/power_grid/round2/'
m = load_pred()
res = {}
for r in ['R3', 'R4']:
    d, o, a, segs = run(r); p = predict(m, d)
    fig, ax = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    t = np.arange(len(o))
    for i, n in enumerate(NAMES):
        ax[i].plot(t, o[:, i], 'k', lw=1, label='data'); ax[i].plot(t, p[:, i], 'r', lw=1, label='v1')
        ax[i].set_ylabel(n)
        for s0, s1, _ in segs: ax[i].axvline(s0, color='gray', lw=.5)
    ax[0].legend()
    for j, c in enumerate(CTRL):
        lo, hi = (0, 150) if c == 'reserve_dispatch' else (0, 2 if c == 'price_signal' else 1)
        ax[3].step(t, a[:, j] / hi, where='post', label=c)
    ax[3].legend(fontsize=7); ax[3].set_ylabel('controls (/max)')
    for s0, s1, ac in segs:
        ax[0].text(s0 + 1, ax[0].get_ylim()[1], f"p{ac['price_signal']} r{ac['reserve_dispatch']:g}\nc{ac['charging_allowance']} x{ac['interconnector']}", fontsize=6, va='top')
    fig.suptitle(f'power_grid {r}: data (black) vs v1 (red)'); fig.tight_layout(); fig.savefig(OUT + f'{r}_v1.png', dpi=90); plt.close(fig)
    # error panel in score sigma
    fig, ax = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
    for i, n in enumerate(NAMES):
        ax[i].plot(t, (p[:, i] - o[:, i]) / SIG[i], 'r', lw=.8); ax[i].axhline(0, color='k', lw=.5)
        ax[i].set_ylabel(f'{n} err / score-sigma')
        for s0, s1, _ in segs: ax[i].axvline(s0, color='gray', lw=.5)
    fig.tight_layout(); fig.savefig(OUT + f'{r}_err.png', dpi=90); plt.close(fig)
    rows = []
    for k, (s0, s1, ac) in enumerate(segs):
        dm = o[s1 - 10:s1].mean(0); pm = p[s1 - 10:s1].mean(0)
        e = p[s0:s1] - o[s0:s1]
        loss = (1 - 1 / (1 + np.abs(e) / SIG)).sum(0)
        # level vs dynamics split: loss from persistent offset (median err over last half) vs rest
        off = np.median(e[(s1 - s0) // 2:], axis=0)
        loss_lvl = (1 - 1 / (1 + np.abs(np.broadcast_to(off, e.shape)) / SIG)).sum(0)
        # transient: loss in first 15 ticks
        loss_tr = (1 - 1 / (1 + np.abs(e[:15]) / SIG)).sum(0)
        rows.append(dict(seg=k, t0=s0, t1=s1, action=ac, data_last10=dm.tolist(), v1_last10=pm.tolist(),
                         err_sig=((pm - dm) / SIG).tolist(), loss=loss.tolist(), loss_offset_equiv=loss_lvl.tolist(),
                         loss_first15=loss_tr.tolist(), mean_err_sig=(e.mean(0) / SIG).tolist(),
                         min=o[s0:s1].min(0).tolist(), max=o[s0:s1].max(0).tolist()))
    res[r] = rows
json.dump(res, open(OUT + 'segments.json', 'w'), indent=1)
for r, rows in res.items():
    print('==', r)
    for x in rows:
        ac = x['action']
        print(f"[{x['t0']:3d}-{x['t1']-1:3d}] p{ac['price_signal']:<5} r{ac['reserve_dispatch']:<5g} c{ac['charging_allowance']:<4} x{ac['interconnector']:<4} "
              f"data {x['data_last10'][0]:6.1f} {x['data_last10'][1]:6.2f} {x['data_last10'][2]:.4f} | v1 {x['v1_last10'][0]:6.1f} {x['v1_last10'][1]:6.2f} {x['v1_last10'][2]:.4f} "
              f"| errσ {x['err_sig'][0]:+5.1f} {x['err_sig'][1]:+5.1f} {x['err_sig'][2]:+5.1f} | loss {x['loss'][0]:5.1f} {x['loss'][1]:5.1f} {x['loss'][2]:5.1f}"
              f" | lvl-equiv {x['loss_offset_equiv'][0]:5.1f} {x['loss_offset_equiv'][1]:5.1f} {x['loss_offset_equiv'][2]:5.1f} | first15 {x['loss_first15'][0]:4.1f} {x['loss_first15'][1]:4.1f} {x['loss_first15'][2]:4.1f}"
              f" | range L {x['min'][0]:.0f}-{x['max'][0]:.0f} f {x['min'][1]:.2f}-{x['max'][1]:.2f} S {x['min'][2]:.3f}-{x['max'][2]:.3f}")
