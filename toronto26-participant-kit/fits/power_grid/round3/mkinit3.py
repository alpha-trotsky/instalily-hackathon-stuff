"""Frequency-parameter start values for a v3 fit: static-map regression (fstatic3.py form, observed load, ticks >= 15
after a control change) on the TRAIN runs only, merged into a base fit's params.
python fits/power_grid/round3/mkinit3.py --base BASE.json --form nob|xl|xlc --train R1 R2c ... --out init.json"""
import argparse, json
import numpy as np
from scipy.optimize import least_squares
ap = argparse.ArgumentParser(); ap.add_argument('--base'); ap.add_argument('--form'); ap.add_argument('--train', nargs='+')
ap.add_argument('--out'); ap.add_argument('--report', action='store_true'); a = ap.parse_args()
p2 = json.load(open(a.base))['params']
rows = []; tags = []
for r in (['R1', 'R2c', 'R3', 'R4', 'R5'] if a.report else a.train):
    run = json.load(open(f'data/power_grid/{r}.json'))['runs'][0]
    A, O = run['actions'], run['observations']; last = 0
    for t in range(len(A)):
        if t and A[t] != A[t - 1]:
            last = t
        if t - last >= 15:
            tags.append((r, A[t]['price_signal'], A[t]['reserve_dispatch'], A[t]['charging_allowance'], A[t]['interconnector']))
            rows.append((A[t]['reserve_dispatch'], A[t]['charging_allowance'], A[t]['interconnector'], O[t]['load'], O[t]['frequency']))
rd, ch, x, L, f = np.array(rows).T
Rsat = p2['Rsat']; Rs = np.where(rd > 0, 0.5 * (rd + Rsat - np.sqrt((rd - Rsat) ** 2 + 64.0)), 0.0); cx = 1 - x
use_xl, use_c, thr = a.form in ('xl', 'xlc', 'thr'), a.form in ('xlc', 'thr'), a.form == 'thr'
tr = np.array([t[0] in a.train for t in tags]) if a.report else np.ones(len(f), bool)
def sp(z, w=0.05):
    return w * np.logaddexp(0, z / w)
def fmap(q):
    f0, bL, br, ax1, ax2, kLR, kx, bc, kxL, axr, cth = q
    kxL = kxL if use_xl else 0.0; bc = bc if use_c else 0.0
    X = ax1 * cx + ax2 * cx * cx
    if thr:
        kx = 0.0; w = np.clip(Rs / Rsat, 0, 1); X = X * (1 - w) + w * axr * sp(cx - cth)
    return f0 - bL * (L - 100) * (1 - kLR * Rs / 150 * x) + br * Rs - X * np.clip(1 - kx * Rs / 150 + kxL * (L - 100) / 100, 0, 4) - bc * ch * Rs / 150 * cx
q0 = [p2['f0'], p2['bL'], p2['br'], p2['ax1'], p2['ax2'], 0.0, 0.0, 0.0, 0.0, 2.6, 0.33]
sol = least_squares(lambda q: ((fmap(q) - f) / 0.075)[tr], q0, loss='soft_l1', f_scale=2)
q = dict(zip(['f0', 'bL', 'br', 'ax1', 'ax2', 'kLR', 'kx', 'bc', 'kxL', 'axr', 'cth'], sol.x.tolist()))
if thr:
    q['kx'] = 0.0; q['xb'] = 1.0
else:
    q.pop('axr'); q.pop('cth')
if a.report:
    res = fmap(sol.x) - f; cells = {}
    for t, e in zip(tags, res):
        cells.setdefault(t, []).append(e)
    for k, v in cells.items():
        if len(v) >= 5 and (k[2] > 0 or k[4] < 1):
            print('   ', k, f'n{len(v)} err {np.mean(v)/0.075:+.1f}s', '' if k[0] in a.train else 'HELD OUT')
q['kxL'] = min(max(q['kxL'], 0.0), 4.0) if use_xl else 0.0; q['bc'] = min(max(q['bc'], -2.0), 2.0) if use_c else 0.0
q['kLR'] = min(max(q['kLR'], -1.0), 1.5); q['kx'] = min(max(q['kx'], -2.0), 1.0)
p = dict(p2); p.update(q); p.update(hx=0.0, kxf=0.1)
print(a.form, a.train, {k: round(v, 4) for k, v in q.items()})
json.dump({'params': p, 'note': f'base {a.base} + static regression form {a.form} on {a.train}'}, open(a.out, 'w'), indent=1)
