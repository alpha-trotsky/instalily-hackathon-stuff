"""Free: fit retail sales laws driven by OBSERVED shipments (isolates the retail block from shipment errors).
R_t = max(R_{t-1} + ship_t - sales_t, 0), sales = min(R_{t-1}+ship_t, max(D, 0)); R_{-1} = initial reading.
law A (v1):   D = D0 + kR*R + dz*z,           z = (1-az)^t
law B (+EMA): D = D0 + kR*R + g*Ss + dz*z,    Ss <- Ss + a*(ship - Ss)
law C (+EMA, sqrt R): D = D0 + kR*sqrt(R) + g*Ss + dz*z
"""
import json, numpy as np
from scipy.optimize import least_squares
d = np.load('fits/supply_chain/round2/arrays.npz')
init = {r: json.load(open(f'data/supply_chain/{r}.json'))['runs'][0]['initial']['inventory_retail'] for r in ['R1','R2','R3','R4','R5']}
SIG = 34.685
def sim(p, law, ship, R0):
    D0, kR, dz, az, g, a = p
    R = R0; Ss = 0.0; out = np.empty(len(ship))
    for t, s in enumerate(ship):
        z = (1 - az) ** t
        Ss += a * (s - Ss)
        base = kR * (np.sqrt(max(R, 0)) if law == 'C' else R)
        D = D0 + base + dz * z + (g * Ss if law != 'A' else 0)
        sales = min(R + s, max(D, 0)); R = max(R + s - sales, 0); out[t] = R
    return out
def res(p, law, runs):
    return np.concatenate([(sim(p, law, d[r+'_o'][:, 0], init[r]) - d[r+'_o'][:, 2]) / SIG for r in runs])
X0 = {'A': [18, 0.017, 40, 0.05, 0, 0.1], 'B': [10, 0.012, 40, 0.05, 0.3, 0.07], 'C': [5, 0.5, 40, 0.05, 0.3, 0.07]}
LB = [-50, 0, -60, 0.01, 0, 0.005]; UB = [60, 5, 100, 1, 1.5, 1]
def _main():
  for law in "ABC":
    for train, test in [(['R1','R2','R3'], ['R4','R5']), (['R1','R2','R3','R4','R5'], [])]:
        x0 = list(X0[law]);
        lb = list(LB); ub = list(UB)
        if law == 'A': lb[4], ub[4] = -1e-9, 1e-9
        f = least_squares(res, x0, bounds=(lb, ub), args=(law, train), loss='soft_l1', f_scale=2)
        out = []
        for r in ['R1','R2','R3','R4','R5']:
            e = res(f.x, law, [r]); out.append(f"{r} {np.mean(1/(1+np.abs(e))):.3f}")
        print(law, 'train', '+'.join(train), 'p', np.round(f.x, 4).tolist(), '|', ' '.join(out))

if __name__ == '__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fA = least_squares(res, X0['A'], bounds=([-50,0,-60,0.01,-1e-9,0.005],[60,5,100,1,1e-9,1]), args=('A', ['R1','R2','R3','R4','R5']), loss='soft_l1', f_scale=2)
    fB = least_squares(res, X0['B'], bounds=(LB, UB), args=('B', ['R1','R2','R3','R4','R5']), loss='soft_l1', f_scale=2)
    fig, ax = plt.subplots(5, 1, figsize=(12, 14))
    for i, r in enumerate(['R1','R2','R3','R4','R5']):
        o = d[r+'_o']; ax[i].plot(o[:, 2], 'k', lw=0.8, label='data retail')
        ax[i].plot(sim(fA.x, 'A', o[:, 0], init[r]), 'b', lw=0.8, label='law A (v1 form) on observed shipments')
        ax[i].plot(sim(fB.x, 'B', o[:, 0], init[r]), 'g', lw=0.8, label='law B (+EMA shipments)')
        ax[i].plot(d[r+'_p'][:, 2], 'r', lw=0.8, label='v1 full model'); ax[i].set_ylabel(r); ax[i].legend(fontsize=7)
        a2 = ax[i].twinx(); a2.plot(o[:, 0], color='orange', lw=0.4); a2.set_ylabel('shipments', color='orange')
    fig.tight_layout(); fig.savefig('fits/supply_chain/round2/retail_law.png', dpi=85)
