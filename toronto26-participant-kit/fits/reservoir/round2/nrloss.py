"""Noise-reduced score loss: error series e = pred - obs smoothed by a centred MA within each segment
(w = 9 for level/inflow/outflow, 21 for quality), loss = sum(1 - 1/(1+|e_s|/sigma)). Classify each pair:
transient share = loss in the first 20 ticks of the segment / total; level offset = |mean e_s over 2nd half|."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
m = load_pred()
W = [9, 9, 9, 21]
def ma(y, w):
    out = np.empty_like(y); n = len(y); h = w // 2
    for i in range(n): out[i] = y[max(0, i-h):min(n, i+h+1)].mean()
    return out
rows = []; tot = {}
for name in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a, segs = run(name); p = predict(m, r)
    for s, e, act in segs:
        for j, n in enumerate(NAMES):
            es = ma(p[s:e, j] - o[s:e, j], W[j]) / SIG[j]
            l = 1 - 1 / (1 + np.abs(es)); L = float(l.sum()); tr = float(l[:20].sum())
            h = es[len(es)//2:]
            kind = 'transient' if tr > 0.6 * L else ('level' if abs(h.mean()) > 1.5 * h.std() else 'dynamics')
            rows.append((name, s, e, n, L, tr, float(h.mean()), float(h.std()), kind,
                         ' '.join(f'{act[c]:g}' for c in CTL)))
            tot[(name, n)] = tot.get((name, n), 0) + L
for group, names in (('NEW (R4, R5)', ('R4', 'R5')), ('OLD (R1-R3)', ('R1', 'R2', 'R3'))):
    sel = sorted([x for x in rows if x[0] in names], key=lambda x: -x[4]); T = sum(x[4] for x in sel)
    print(f'== {group}: total NR loss {T:.1f} obs-ticks; by observable: ' +
          ' '.join(f'{n}={sum(x[4] for x in sel if x[3]==n):.1f}' for n in NAMES))
    for x in sel[:15]:
        print(f'  {x[0]} [{x[1]:3d}-{x[2]-1:3d}] {x[3]:8s} lost {x[4]:6.1f} ({100*x[4]/T:4.1f}%) first20 {x[5]:5.1f} '
              f'2nd-half err {x[6]:+6.2f}σ ±{x[7]:.2f} -> {x[8]:9s} (rel irr dep aer = {x[9]})')
