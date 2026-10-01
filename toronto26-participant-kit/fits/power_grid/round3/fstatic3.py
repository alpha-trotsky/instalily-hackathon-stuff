"""Round 3: static frequency map check with observed load (settled ticks: >= 15 ticks after any control change).
Fits kLR, kx, bc (and f0, bL, br, ax1, ax2) on steady ticks by least squares; prints cell residuals."""
import json, sys
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, '.')
p2 = json.load(open('fits/power_grid/round2/v2_C_m13.json'))['params']
rows = []
for r in ['R1', 'R2c', 'R3', 'R4', 'R5']:
    run = json.load(open(f'data/power_grid/{r}.json'))['runs'][0]
    A, O = run['actions'], run['observations']
    last = 0
    for t in range(len(A)):
        if t and A[t] != A[t - 1]:
            last = t
        if t - last >= 15:
            a = A[t]; o = O[t]
            rows.append((r, t, a['price_signal'], a['reserve_dispatch'], a['charging_allowance'], a['interconnector'],
                         o['load'], np.mean([O[k]['load'] for k in range(max(0, t - 4), t + 1)]), o['frequency']))
R = np.array([x[2:] for x in rows]); tag = [x[:2] for x in rows]
pr, rd, ch, x, L, Lf, f = R.T
WR, Rsat = 8.0, p2['Rsat']
Rs = np.where(rd > 0, 0.5 * (rd + Rsat - np.sqrt((rd - Rsat) ** 2 + WR * WR)), 0.0)
cx = 1 - x
def fmap(q, form):
    f0, bL, br, ax1, ax2, kLR, kx, bc, kxL, ax3 = q
    if not form.startswith('sat'): ax3 = 0.0
    if form == 'v2': kLR = bc = 0.0
    if form == 'nob': bc = 0.0
    if form in ('v2', 'nob', 'full'): kxL = 0.0
    if form == 'xl': bc = 0.0
    if form == 'xl0': bc = kLR = 0.0
    if form == 'satxl': bc = 0.0
    X = ax1 * cx + ax2 * cx * cx + ax3 * (1 - np.exp(-cx / 0.1))
    return f0 - bL * (L - 100) * (1 - kLR * Rs / 150 * x) + br * Rs - X * np.clip(1 - kx * Rs / 150 + kxL * (L - 100) / 100, 0, 4) - bc * ch * Rs / 150 * cx
q0 = [p2['f0'], p2['bL'], p2['br'], p2['ax1'], p2['ax2'], 0.0, 0.0, 0.0, 0.0, 0.0]
for form in ['xl', 'xlfull', 'satxl', 'satxlfull']:
    sol = least_squares(lambda q: (fmap(q, form) - f) / 0.075, q0, loss='soft_l1', f_scale=2)
    res = fmap(sol.x, form) - f
    print(form, 'params', np.round(sol.x, 4).tolist(), 'score', round(float(np.mean(1 / (1 + np.abs(res) / 0.075))), 3))
    cells = {}
    for (r, t), e, a in zip(tag, res, R):
        key = (r, tuple(np.round(a[:4], 2)))
        cells.setdefault(key, []).append(e)
    for k, v in cells.items():
        if len(v) >= 5 and (k[1][1] > 0 or k[1][3] < 1):
            print('   ', k[0], k[1], f'n{len(v)} mean err {np.mean(v)/0.075:+.1f}s')
