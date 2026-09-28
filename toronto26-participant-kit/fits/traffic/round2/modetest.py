"""Score-metric test: in congested ticks the bursty flow target is quantized with many exact zeros; the metric
1/(1+|e|/sigma) (sigma ~0.7-0.9 << burst spread ~8) rewards the mode. Compare v1 flows with 'predict 0 when v1's
own speed on that route is below a threshold' and with 'predict the v1 value times f'."""
from common import *
tot = {}
for nm in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a = run(nm); p = pred(r)
    for i in (0, 1):
        y = o[:, i]; sc = lambda q: (1 / (1 + np.abs(q - y) / SIG[i]))
        cong = p[:, i + 2] < 20
        z = (np.abs(y[cong]) < 0.05).mean() if cong.any() else 0
        base = sc(p[:, i]).mean()
        for thr in (14, 17, 20):
            q = np.where(p[:, i + 2] < thr, 0.0, p[:, i]); tot.setdefault((OBS[i], thr), []).append((sc(q).mean(), base, len(y)))
        print(f'{nm} {OBS[i]}: congested ticks {cong.sum():3d}, zero fraction there {z:.2f}; v1 {base:.3f}; zero-if-speed<17 {sc(np.where(p[:, i+2] < 17, 0.0, p[:, i])).mean():.3f}')
for k, v in tot.items():
    v = np.array(v); print(k, 'weighted: mode-rule %.3f vs v1 %.3f' % ((v[:, 0] * v[:, 2]).sum() / v[:, 2].sum(), (v[:, 1] * v[:, 2]).sum() / v[:, 2].sum()))
