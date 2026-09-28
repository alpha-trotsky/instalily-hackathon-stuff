"""Groundwater excess (inflow - season), exchange E = dV - (I - O), per 10/25-tick blocks; data vs v1."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
m = load_pred()
for name in sys.argv[1:] or ['R4', 'R5']:
    r, o, a, segs = run(name); p = predict(m, r); T = len(o); t = np.arange(1, T + 1)
    ex, exm = o[:, 1] - season(t), p[:, 1] - season(t)
    V0 = r['initial']['level']
    Vprev = np.r_[V0, o[:-1, 0]]; E = o[:, 0] - Vprev - (o[:, 1] - o[:, 2])
    Vpm = np.r_[V0, p[:-1, 0]]; Em = p[:, 0] - Vpm - (p[:, 1] - p[:, 2])
    print(f'== {name} initial level {V0:.1f}; first 8 excess data', np.round(ex[:8], 2), ' v1', np.round(exm[:8], 2))
    print(' blk    level   v1lev | excess  v1exc | exch E   v1 E | outflow v1out  req')
    B = 25
    for s in range(0, T, B):
        sl = slice(s, min(T, s + B)); req = a[sl, 0].mean() + a[sl, 1].mean()
        print(f'{s:4d} {o[sl,0].mean():8.1f} {p[sl,0].mean():7.1f} | {ex[sl].mean():+6.3f} {exm[sl].mean():+6.3f} | '
              f'{E[sl].mean():+6.2f} {Em[sl].mean():+6.2f} | {o[sl,2].mean():6.2f} {p[sl,2].mean():6.2f} {req:5.1f}')
