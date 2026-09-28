"""Free: zoomed plots and quantitative battery for market B, C."""
import json, sys, math
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
OUT = 'fits/market/round2'
N = ['price', 'volume', 'depth']
def load(r):
    run = json.load(open(f'data/market/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in N] for x in run['observations']])
    a = np.array([[x['interest_rate'] / .1, x['transaction_tax'] / .05] for x in run['actions']])
    return run, o, a, np.load(f'{OUT}/{r}_v1pred.npy')
D = {r: load(r) for r in 'ABC'}
# zoomed overlay: volume (ylim) and log depth
fig, ax = plt.subplots(3, 3, figsize=(16, 10))
for j, r in enumerate('ABC'):
    run, o, a, p = D[r]
    ax[0, j].plot(o[:, 0], 'k.', ms=2); ax[0, j].plot(p[:, 0], 'r-'); ax[0, j].set_title(f'{r} price')
    ax[1, j].plot(o[:, 1], 'k.', ms=2); ax[1, j].plot(p[:, 1], 'r-'); ax[1, j].set_ylim(1.3, 3.2); ax[1, j].set_title(f'{r} volume (zoom)')
    ax[2, j].semilogy(o[:, 2], 'k.', ms=2); ax[2, j].semilogy(p[:, 2], 'r-'); ax[2, j].set_title(f'{r} depth (log)')
    for x in ax[:, j]:
        for i in range(1, len(a)):
            if (a[i] != a[i-1]).any(): x.axvline(i, color='g', alpha=.3)
        x.grid(alpha=.3)
fig.tight_layout(); fig.savefig(f'{OUT}/ABC_zoom.png', dpi=80)

run, o, a, p = D['B']
print('initial / first obs:')
for r in 'ABC': print(r, {k: round(v, 1) for k, v in D[r][0]['initial'].items()}, D[r][1][0].round(1), D[r][1][1:4, 2].round(1))
# B depth drain: log-depth slope in windows
ld = np.log(o[:, 2])
for s, e in [(0, 10), (10, 30), (30, 60), (60, 100), (100, 150)]:
    print(f'B depth [{s},{e}) mean {o[s:e,2].mean():.1f}  dlog/tick {np.polyfit(range(e-s), ld[s:e], 1)[0]:+.4f}  dlin/tick {np.polyfit(range(e-s), o[s:e,2], 1)[0]:+.3f}')
print('B price slope 20-150 /tick', np.polyfit(range(130), o[20:150, 0], 1)[0].round(3), ' A price slope 15-50', np.polyfit(range(35), D['A'][1][15:50, 0], 1)[0].round(3))
print('B price slope 150-230', np.polyfit(range(80), o[150:230, 0], 1)[0].round(3))
# depth recovery after 150
for k in [1, 2, 5, 10, 20, 30, 50, 80, 100, 149]:
    print(f'B depth t=150+{k}: {o[150+k,2]:.1f}   (gap to 91 closed {(o[150+k,2]-o[149,2])/(91-o[149,2]):.2f})')
# A tax-off recovery for comparison (tax off at 450, depth 41 -> 91)
for k in [1, 2, 5, 10, 20, 30]:
    oa = D['A'][1]; print(f'A depth t=450+{k}: {oa[450+k,2]:.1f} gap closed {(oa[450+k,2]-oa[449,2])/(91-oa[449,2]):.2f}')
# delays: ticks after switch until 9-tick MA moves > 3 sigma_noise from pre-switch level
sig_n = {'price': .33, 'volume': .009, 'depth': .19}
for r in 'BC':
    run, o, a, p = D[r]
    sw = [i for i in range(1, len(a)) if (a[i] != a[i-1]).any()]
    for s in sw:
        pre = o[s-5:s].mean(0)
        row = []
        for i, n in enumerate(N):
            dly = next((k for k in range(0, 60) if abs(o[s+k:s+k+3, i].mean() - pre[i]) > 4 * sig_n[n]), None)
            row.append(dly)
        print(f'{r} switch at {s} {a[s-1]}->{a[s]}  first move (ticks) price/vol/depth', row)
# volume vs |dlogp| relationship per run (after tick 30), smoothed dp
for r in 'ABC':
    run, o, a, p = D[r]
    lp = np.log(o[:, 0]); dp = np.convolve(np.diff(lp), np.ones(9) / 9, 'same')
    v = o[1:, 1]; m = np.arange(len(v)) > 30
    X = np.column_stack([np.ones(m.sum()), np.maximum(dp[m], 0), np.maximum(-dp[m], 0), a[1:][m, 0], a[1:][m, 1], a[1:][m, 0] * a[1:][m, 1]])
    c, *_ = np.linalg.lstsq(X, v[m], rcond=None)
    print(f'{r} volume ~ 1 + rise + fall + r + tau + r*tau :', c.round(3), ' resid std', (v[m] - X @ c).std().round(3))
# B volume in gap vs price speed
for s, e in [(0, 150), (150, 300), (300, 425), (425, 475), (475, 600)]:
    dp = np.diff(np.log(o[s:e, 0]))
    print(f'B [{s},{e}) volume mean {o[s+10:e,1].mean():.3f}  mean|dlogp| {np.abs(np.convolve(dp,np.ones(9)/9,"valid")).mean():.4f}')
run, o, a, p = D['C']
for s, e in [(0, 125), (125, 250), (250, 375), (375, 500), (500, 600)]:
    dp = np.diff(np.log(o[s:e, 0]))
    print(f'C [{s},{e}) volume mean {o[s+10:e,1].mean():.3f}  last10 {o[e-10:e,1].mean():.3f} mean|dlogp| {np.abs(np.convolve(dp,np.ones(9)/9,"valid")).mean():.4f}')
