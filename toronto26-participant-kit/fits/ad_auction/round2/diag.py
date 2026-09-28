"""Round-2 diagnosis for ad_auction (free; no steps). Run from the kit: python3 fits/ad_auction/round2/diag.py"""
import json, sys, os, importlib.util
import numpy as np
sys.path.insert(0, '.')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from greybox.common import core, settle

S = 'ad_auction'; OUT = 'fits/ad_auction/round2'
NAMES = ['win_rate', 'spend', 'conversions']; CTRL = ['bid', 'budget_cap', 'targeting_breadth']
spec = importlib.util.spec_from_file_location('v1pred', 'fits/round2/v1_models/ad_auction/predict.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']

def load(r):
    run = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in NAMES] for x in run['observations']])
    a = np.array([[x[c] for c in CTRL] for x in run['actions']])
    p = np.array([[x[n] for n in NAMES] for x in mod.predict(run['initial'], run['actions'], ctx)])
    return run, o, a, p

RUNS = ['R1', 'R2c', 'R3', 'R4']
D = {r: load(r) for r in RUNS}
sig = 0.1 * np.concatenate([D[r][1][20:] for r in RUNS]).std(0)
print('score sigma', sig)

def segs(a):
    out = []; s = 0
    for t in range(1, len(a) + 1):
        if t == len(a) or np.any(a[t] != a[s]):
            out.append((s, t)); s = t
    return out

LAB = {('R3', 0): 'u.7 (3.95/76/.7075)', ('R3', 250): 'rec', ('R3', 350): 'u1 (5/100/.775)', ('R3', 400): 'rec',
       ('R3', 425): 'u.85 (4.475/88/.741)', ('R4', 0): 'bid3.25 cap100', ('R4', 50): 'bid2 cap100',
       ('R4', 100): 'bid.75 cap100', ('R4', 150): 'rec', ('R4', 200): 'bid5 cap50', ('R4', 250): 'bid5 cap30'}
rows = []; loss = []
for r in RUNS:
    run, o, a, p = D[r]
    e = (p - o) / sig
    L = 1 - 1 / (1 + np.abs(e))
    sc = 1 / (1 + np.abs(e))
    print(f'\n== {r} ({len(o)} ticks)  score per obs {sc.mean(0).round(3)}  mean {sc.mean():.3f}  lost-ticks {L.sum(0).round(1)}')
    ss = segs(a)
    if r == 'R3':  # AD1 first hold is 250 ticks: split at 50 as pre-registered
        ss = [(0, 50), (50, 250)] + ss[1:]
    for s, t in ss:
        lab = LAB.get((r, s), str(a[s].round(3).tolist()))
        n = t - s; k = min(10, n)
        dm = o[t - k:t].mean(0); pm = p[t - k:t].mean(0); full = o[s:t].mean(0); pfull = p[s:t].mean(0)
        ep = {'obs': o, 'actions': [dict(zip(CTRL, x)) for x in a], 'names': NAMES}
        st = settle.check_segment(ep, s, t) if n >= 12 else None
        print(f' [{s:3d},{t:3d}) {lab:24s} data10 {np.round(dm,3)} v1 {np.round(pm,3)} err/sig {np.round((pm-dm)/sig,1)}'
              f' | segmean data {np.round(full,3)} v1 {np.round(pfull,3)}'
              + (' | settled ' + ','.join(f"{nm[:4]}:{'Y' if st[nm]['settled'] else 'N'}({st[nm]['drift_sigma']:.1f},t{st[nm]['settling_time_text']})" for nm in NAMES) if st else ''))
        for i, nm in enumerate(NAMES):
            ee = e[s:t, i]; LL = L[s:t, i]
            first = LL[:min(20, n)].sum()
            late = ee[n // 2:]
            loss.append(dict(run=r, seg=f'[{s},{t}) {lab}', obs=nm, lost=float(LL.sum()), n=n,
                             first20=float(first), late_mean=float(late.mean()), late_std=float(late.std()),
                             mean_err=float(ee.mean())))
    # plot
    fig, ax = plt.subplots(5, 1, figsize=(13, 13), sharex=True)
    for i, nm in enumerate(NAMES):
        ax[i].plot(o[:, i], 'k.', ms=2, label='data'); ax[i].plot(p[:, i], 'r-', lw=1, label='v1')
        ax[i].set_ylabel(nm)
        for s, t in segs(a): ax[i].axvline(s, color='0.85', lw=.5)
    ax[0].legend(loc='upper right')
    for i, nm in enumerate(NAMES):
        ax[3].plot(e[:, i], lw=.8, label=nm)
    ax[3].axhline(0, color='k', lw=.5); ax[3].set_ylabel('(v1-data)/sigma'); ax[3].set_ylim(-15, 15); ax[3].legend(fontsize=7)
    ax[4].plot(a[:, 0] / 5, label='bid/5'); ax[4].plot(a[:, 1] / 100, label='cap/100'); ax[4].plot(a[:, 2], label='breadth')
    ax[4].legend(fontsize=7); ax[4].set_ylabel('controls'); ax[4].set_xlabel('tick')
    fig.suptitle(f'ad_auction {r}: data vs v1 (score {sc.mean():.3f})'); fig.tight_layout()
    fig.savefig(f'{OUT}/{r}_v1.png', dpi=90); plt.close(fig)

json.dump(dict(sigma=sig.tolist(), loss=loss), open(f'{OUT}/loss.json', 'w'), indent=1)
print('\n== score-loss ranking (all runs), tick-units lost')
for d in sorted(loss, key=lambda d: -d['lost'])[:30]:
    kind = 'transient' if d['first20'] > 0.6 * d['lost'] else ('level' if abs(d['late_mean']) > 1 and d['late_std'] < abs(d['late_mean']) else 'dynamics')
    print(f"{d['run']:4s} {d['seg']:34s} {d['obs']:12s} lost {d['lost']:6.1f}/{d['n']:3d}  first20 {d['first20']:5.1f}  late mean {d['late_mean']:+6.2f} sd {d['late_std']:5.2f}  -> {kind}")
