"""Round-2 wildlife diagnosis (free, no steps). Run from toronto26-participant-kit/:
    python3 fits/wildlife/round2/diag.py
Writes plots + diag.json next to this file."""
import json, os, sys, importlib.util
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, 'fits/round2')
import heldout
S = 'wildlife'
names, sig = heldout.sigma(S)
ctx = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
mod = heldout.load('fits/round2/v1_models/wildlife', 'v1wl')
CTRL = ['hunting_quota', 'habitat_protection', 'corridor_access']

def segs_of(run):
    out, t = [], 0
    for blk in run.get('segments') or []:
        for s in blk['segments']:
            out.append((t, t + s['steps'], s['action'])); t += s['steps']
    return out

def label(a):
    return f"h{a['hunting_quota']:g}/p{a['habitat_protection']:g}/c{a['corridor_access']:g}"

res = {}
for r in ['R1', 'R2c', 'R3', 'R4']:
    run = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in run['observations']])
    p = np.array([[x[n] for n in names] for x in mod.predict(run['initial'], run['actions'], ctx)])
    A = np.array([[a[c] for c in CTRL] for a in run['actions']])
    segs = segs_of(run)
    if not segs:   # old runs: derive segments from action changes
        ch = [0] + [i for i in range(1, len(A)) if not np.allclose(A[i], A[i - 1])] + [len(A)]
        segs = [(ch[i], ch[i + 1], dict(zip(CTRL, A[ch[i]]))) for i in range(len(ch) - 1)]
    # merge consecutive identical actions (R3: rec 30 + rec 90 are one hold) but keep a split marker
    loss = 1 - 1 / (1 + np.abs(p - o) / sig)
    rows = []
    for (a, b, act) in segs:
        e = (p[a:b] - o[a:b]) / sig
        rows.append(dict(start=a, end=b, action=label(act),
                         obs_last10=o[max(b - 10, a):b].mean(0).round(3).tolist(),
                         pred_last10=p[max(b - 10, a):b].mean(0).round(3).tolist(),
                         err_last10_sig=((p[max(b - 10, a):b] - o[max(b - 10, a):b]).mean(0) / sig).round(2).tolist(),
                         err_mean_sig=e.mean(0).round(2).tolist(),
                         err_rms_sig=np.sqrt((e ** 2).mean(0)).round(2).tolist(),
                         lost=loss[a:b].sum(0).round(1).tolist(),
                         score=(1 - loss[a:b]).mean(0).round(3).tolist()))
    res[r] = dict(rows=rows, score=(1 - loss).mean(0).round(3).tolist(), T=len(o))
    np.save(os.path.join(HERE, f'{r}_pred.npy'), p)
    # plot
    fig, ax = plt.subplots(5, 1, figsize=(12, 13), sharex=True)
    t = np.arange(len(o))
    for i, n in enumerate(names):
        ax[i].plot(t, o[:, i], 'k.', ms=2, label='data')
        ax[i].plot(t, p[:, i], 'r-', lw=1, label='v1')
        ax[i].fill_between(t, p[:, i] - sig[i], p[:, i] + sig[i], color='r', alpha=0.12, label='v1 ±1σ')
        ax[i].set_ylabel(n); ax[i].grid(alpha=.3)
        if n.startswith('prey'): ax[i].set_yscale('log')
        for (a, b, act) in segs: ax[i].axvline(a, color='gray', lw=.5)
    ax[0].legend(loc='upper right', fontsize=8)
    ax[4].plot(t, A[:, 0] / 7, label='hunting u'); ax[4].plot(t, (1 - A[:, 1]) / 0.9, label='habitat u')
    ax[4].plot(t, A[:, 2], label='corridor u'); ax[4].legend(fontsize=8); ax[4].set_ylabel('u'); ax[4].grid(alpha=.3)
    ax[0].set_title(f'wildlife {r}: data vs v1 (score {np.round((1-loss).mean(0),3).tolist()})')
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f'{r}_v1.png'), dpi=90); plt.close(fig)

json.dump(dict(sigma=sig.round(4).tolist(), names=names, runs=res), open(os.path.join(HERE, 'diag.json'), 'w'), indent=1)
for r, v in res.items():
    print(f'== {r} T={v["T"]} score {v["score"]}')
    for w in v['rows']:
        print(f"[{w['start']:3d}-{w['end']-1:3d}] {w['action']:18s} obs {w['obs_last10']} pred {w['pred_last10']}\n"
              f"      errL10σ {w['err_last10_sig']} meanσ {w['err_mean_sig']} rmsσ {w['err_rms_sig']} lost {w['lost']} score {w['score']}")
