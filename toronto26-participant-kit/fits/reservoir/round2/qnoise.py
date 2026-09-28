"""Quality: seasonal component?, noise level, and noise-reduced score loss of v1 (reference = 21-tick centred MA
within each segment, first 3 ticks of each segment kept raw)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
m = load_pred()
def ma(y, w=21):
    out = y.copy(); n = len(y); h = w // 2
    for i in range(n):
        lo, hi = max(0, i - h), min(n, i + h + 1); out[i] = y[lo:hi].mean()
    return out
rows = []
for name in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a, segs = run(name); p = predict(m, r); T = len(o); t = np.arange(1, T + 1)
    q = o[:, 3]; ref = q.copy()
    for s, e, _ in segs:
        ref[s:e] = ma(q[s:e]); ref[s:min(e, s + 3)] = q[s:min(e, s + 3)]
    res = q - ref
    X = np.column_stack([np.sin(2*np.pi*t/67.7547), np.cos(2*np.pi*t/67.7547), np.ones(T)])[20:]
    c, *_ = np.linalg.lstsq(X, res[20:], rcond=None)
    # seasonal in the smooth part too: regress ref on season + block means
    print(f'{name}: resid sd {res[20:].std():.4f} ({res[20:].std()/SIG[3]:.1f}σ), seasonal amp in resid {np.hypot(*c[:2]):.5f}')
    sc_raw = 1 / (1 + np.abs(p[:, 3] - q) / SIG[3]); sc_nr = 1 / (1 + np.abs(p[:, 3] - ref) / SIG[3])
    print(f'   v1 quality score raw {sc_raw.mean():.3f}  noise-reduced {sc_nr.mean():.3f}')
    for s, e, act in segs:
        rows.append((name, s, e, float((1 - sc_nr[s:e]).sum()), float(np.mean(p[s:e, 3] - ref[s:e]) / SIG[3])))
    if name in ('R4', 'R5'): np.save(f'fits/reservoir/round2/{name}_qref.npy', ref)
print('\nnoise-reduced quality loss by segment (new runs), ticks lost, mean err σ:')
for x in sorted([x for x in rows if x[0] in ('R4', 'R5')], key=lambda x: -x[3]):
    print(f'  {x[0]} [{x[1]:3d}-{x[2]-1:3d}] lost {x[3]:6.1f} of {x[2]-x[1]}  mean err {x[4]:+6.1f}σ')
print('old runs:')
for x in sorted([x for x in rows if x[0] not in ('R4', 'R5')], key=lambda x: -x[3])[:8]:
    print(f'  {x[0]} [{x[1]:3d}-{x[2]-1:3d}] lost {x[3]:6.1f} of {x[2]-x[1]}  mean err {x[4]:+6.1f}σ')
