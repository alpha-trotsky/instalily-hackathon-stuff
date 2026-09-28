"""Round-2 diagnosis for social_contagion (free; no steps). Run from KIT:
    python3 fits/social_contagion/round2/analyze.py
Writes plots R4.png/R5.png (+ old runs) and analysis.json next to this file."""
import json, os, sys, importlib.util
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'fits/round2'); import heldout as H
HERE = 'fits/social_contagion/round2'; S = 'social_contagion'
names, sig = H.sigma(S)
ctx = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
mod = H.load('fits/round2/v1_models/social_contagion', 'v1sc')
def segs(run, T):
    out = []; t = 0
    for block in run.get('segments') or []:
        for s in block['segments']:
            out.append((t, t + s['steps'], s['action'])); t += s['steps']
    if not out:  # old runs: split on action changes
        acts = run['actions']; st = 0
        for i in range(1, T + 1):
            if i == T or acts[i] != acts[st]:
                out.append((st, i, acts[st])); st = i
    return out
res = {}
for r in ['R1', 'R2', 'R3', 'R4', 'R5']:
    run = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in run['observations']])
    p = np.array([[x[n] for n in names] for x in mod.predict(run['initial'], run['actions'], ctx)])
    T = len(o); sg = segs(run, T)
    loss = 1 - 1 / (1 + np.abs(p - o) / sig)
    rows = []
    for (a, b, act) in sg:
        for j, n in enumerate(names):
            e = p[a:b, j] - o[a:b, j]
            rows.append(dict(seg=[a, b], act=act, obs=n, data_last10=float(o[max(a, b-10):b, j].mean()),
                             v1_last10=float(p[max(a, b-10):b, j].mean()), mean_err_sig=float(e.mean()/sig[j]),
                             mae_sig=float(np.abs(e).mean()/sig[j]), lost=float(loss[a:b, j].sum()),
                             score=float(1 - loss[a:b, j].mean())))
    res[r] = dict(initial=run['initial'], score=(1 - loss.mean(0)).round(3).tolist(), rows=rows,
                  obs=o.tolist(), pred=p.tolist())
    fig, ax = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    for j, n in enumerate(names):
        ax[j].plot(o[:, j], 'k.', ms=2, label='data'); ax[j].plot(p[:, j], 'r-', lw=1.2, label='v1 m12')
        ax[j].set_ylabel(n); ax[j].legend(loc='upper right')
        for (a, b, act) in sg: ax[j].axvline(a, color='0.8', lw=0.6)
        ax[j].set_title(f'{r} {n}: v1 score {1-loss[:, j].mean():.3f} (sigma {sig[j]:.2f})', fontsize=9)
    A = np.array([[x['seeding']/9, x['incentive']/2, x['bridge_outreach']/0.6] for x in run['actions']])
    for k, l in enumerate(['seeding/9', 'incentive/2', 'bridge/0.6']): ax[2].step(range(T), A[:, k], where='post', label=l)
    ax[2].legend(); ax[2].set_ylabel('u'); ax[2].set_xlabel('tick')
    plt.tight_layout(); plt.savefig(f'{HERE}/{r}.png', dpi=90); plt.close()
json.dump(dict(sigma=sig.tolist(), names=names, runs=res), open(f'{HERE}/analysis.json', 'w'))
print('sigma', sig)
for r in res:
    print(f'== {r} score {res[r]["score"]}  initial {res[r]["initial"]}')
    for x in res[r]['rows']:
        a = x['act']; print(f"  {x['seg'][0]:4d}-{x['seg'][1]:4d} s{a['seeding']:.2f} i{a['incentive']:.2f} b{a['bridge_outreach']:.2f} {x['obs'][-1]}"
              f" data {x['data_last10']:7.1f} v1 {x['v1_last10']:7.1f} bias {x['mean_err_sig']:+6.2f}s mae {x['mae_sig']:5.2f}s lost {x['lost']:6.1f} score {x['score']:.3f}")
