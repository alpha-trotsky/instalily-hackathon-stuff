"""Free: round-2 diagnosis for supply_chain. Plots R4/R5 vs v1, segment stats, score-loss ranking."""
import json, sys, os
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'fits/round2')
import heldout as H
OUT = 'fits/supply_chain/round2'
S = 'supply_chain'
names, sig = H.sigma(S)
ctx = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
mod = H.load('fits/round2/v1_models/supply_chain', 'v1sc')
CTRL = ['order_quantity','lead_time_buy','product_mix','production_effort','receiving_effort','maintenance']
LABELS = {'R4': ['u.7 a (0-49)','u.7 b (50-149)','rec 60','u1 60','rec 30','u.85 100'],
          'R5': ['ord80 recv1.0','recv .7','recv .5','recv .5 + maint .3']}
res = {}
for r in ['R1','R2','R3','R4','R5']:
    run = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in run['observations']])
    p = np.array([[x[n] for n in names] for x in mod.predict(run['initial'], run['actions'], ctx)])
    a = np.array([[x[c] for c in CTRL] for x in run['actions']])
    res[r] = (o, p, a, run)
print('sigma', sig.round(3).tolist())
rows = []; seginfo = {}
for r in ['R4','R5']:
    o, p, a, run = res[r]
    segs = run['segments'][0]['segments']; t0 = 0; seginfo[r] = []
    for i, sg in enumerate(segs):
        t1 = t0 + sg['steps']; lab = LABELS[r][i]
        seginfo[r].append((t0, t1, lab))
        print(f'{r} [{t0:3d}-{t1-1:3d}] {lab:22s}', end='')
        for j, n in enumerate(names):
            d10 = o[t1-10:t1, j].mean(); m10 = p[t1-10:t1, j].mean()
            f10 = o[t0:t0+10, j].mean()
            err = p[t0:t1, j] - o[t0:t1, j]
            loss = (1 - 1/(1 + np.abs(err)/sig[j])).sum()
            # split: level = |mean err| over last half, dyn = rest
            half = err[(t1-t0)//2:]
            rows.append(dict(run=r, seg=lab, t0=t0, t1=t1, obs=n, data_last10=d10, v1_last10=m10,
                             data_first10=f10, bias=float(err.mean()), bias_last_half=float(half.mean()),
                             mae=float(np.abs(err).mean()), loss=float(loss),
                             loss_first20=float((1 - 1/(1 + np.abs(err[:20])/sig[j])).sum())))
            print(f' | {n[:4]} d{d10:7.1f} m{m10:7.1f} e{(m10-d10)/sig[j]:+6.1f}s', end='')
        print()
        t0 = t1
rows.sort(key=lambda x: -x['loss'])
tot = sum(x['loss'] for x in rows)
print('\nTotal loss ticks-equivalent', round(tot,1), 'of', sum(len(res[r][0]) for r in ['R4','R5'])*3)
for x in rows:
    print(f"{x['run']} {x['seg']:22s} {x['obs'][:10]:10s} loss {x['loss']:6.1f} ({100*x['loss']/tot:4.1f}%) "
          f"first20 {x['loss_first20']:5.1f} bias {x['bias']/sig[names.index(x['obs'])]:+6.1f}s "
          f"lastHalfBias {x['bias_last_half']/sig[names.index(x['obs'])]:+6.1f}s mae {x['mae']/sig[names.index(x['obs'])]:5.1f}s")
json.dump(rows, open(f'{OUT}/segment_loss.json','w'), indent=1)
# old-data scores
for r in ['R1','R2','R3','R4','R5']:
    o, p, a, run = res[r]
    sc = (1/(1+np.abs(p-o)/sig)).mean(0)
    print(r, 'v1 score per obs', sc.round(3).tolist(), 'mean', sc.mean().round(3))
# plots
for r in ['R1','R2','R3','R4','R5']:
    o, p, a, run = res[r]
    fig, ax = plt.subplots(5, 1, figsize=(13, 13), sharex=True)
    t = np.arange(len(o))
    for j, n in enumerate(names):
        ax[j].plot(t, o[:, j], 'k-', lw=0.8, label='data'); ax[j].plot(t, p[:, j], 'r-', lw=1, label='v1')
        ax[j].set_ylabel(n); ax[j].legend(loc='upper right', fontsize=7)
    e = (p - o) / sig
    for j, n in enumerate(names): ax[3].plot(t, e[:, j], lw=0.8, label=n)
    ax[3].axhline(0, color='k', lw=0.5); ax[3].set_ylabel('err / score sigma'); ax[3].set_ylim(-40, 40); ax[3].legend(fontsize=7)
    lo = np.array([0,0,0,0,0,0.]); hi = np.array([80,1,1,1.5,1.5,1.])
    for k, c in enumerate(CTRL): ax[4].step(t, a[:, k]/hi[k], where='post', label=c)
    ax[4].set_ylabel('controls / max'); ax[4].legend(fontsize=7, ncol=3)
    for r2 in seginfo.get(r, []):
        for axx in ax: axx.axvline(r2[0], color='gray', lw=0.4, ls=':')
    ax[0].set_title(f'supply_chain {r}: data vs v1 (score sigma {sig.round(2).tolist()})')
    fig.tight_layout(); fig.savefig(f'{OUT}/{r}_v1.png', dpi=90); plt.close(fig)
np.savez(f'{OUT}/arrays.npz', **{f'{r}_{k}': v for r in res for k, v in zip('opa', res[r][:3])})
