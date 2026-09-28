"""Free: round-2 market diagnosis. Plots B, C (and A) with v1 overlay; segment table; score-loss ranking."""
import json, sys, importlib.util, os
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from fits.round2.heldout import sigma
OUT = 'fits/market/round2'
NAMES = ['price', 'volume', 'depth']
names, SIG = sigma('market')
ctx = json.load(open('docs/market.json'))['brief']['forecast_context']
spec = importlib.util.spec_from_file_location('v1p', 'fits/round2/v1_models/market/predict.py')
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

def load(r):
    run = json.load(open(f'data/market/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in NAMES] for x in run['observations']])
    a = np.array([[x['interest_rate'], x['transaction_tax']] for x in run['actions']])
    p = np.array([[x[n] for n in NAMES] for x in v1.predict(run['initial'], run['actions'], ctx)])
    return run, o, a, p

def segs(a):
    b = [0] + [i for i in range(1, len(a)) if (a[i] != a[i-1]).any()] + [len(a)]
    return list(zip(b[:-1], b[1:]))

if __name__ == '__main__':
    print('sigma', SIG.round(4))
    rows = []
    for r in ['A', 'B', 'C']:
        run, o, a, p = load(r)
        np.save(f'{OUT}/{r}_v1pred.npy', p)
        fig, ax = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
        for i, n in enumerate(NAMES):
            ax[i].plot(o[:, i], 'k.', ms=2, label='data'); ax[i].plot(p[:, i], 'r-', lw=1, label='v1')
            ax[i].set_ylabel(n); ax[i].grid(alpha=.3)
        ax[3].step(range(len(a)), a[:, 0] / 0.1, where='post', label='rate/0.1')
        ax[3].step(range(len(a)), a[:, 1] / 0.05, where='post', label='tax/0.05'); ax[3].legend(); ax[3].set_ylabel('u')
        ax[0].legend(); ax[0].set_title(f'market run {r}: data vs v1')
        for s, e in segs(a):
            for x in ax: x.axvline(s, color='g', alpha=.3)
        fig.tight_layout(); fig.savefig(f'{OUT}/{r}_v1.png', dpi=90); plt.close(fig)
        print(f'== {r}  initial', {k: round(v, 2) for k, v in run['initial'].items()})
        for s, e in segs(a):
            m = o[e-10:e].mean(0); mp = p[e-10:e].mean(0)
            sc = 1 / (1 + np.abs(p[s:e] - o[s:e]) / SIG)
            loss = (1 - sc).sum(0)
            print(f'[{s:3d}-{e:3d}) r={a[s,0]:.3f} t={a[s,1]:.3f} data={m.round(2)} v1={mp.round(2)} '
                  f'err/sig={((mp-m)/SIG).round(1)} score={sc.mean(0).round(3)} loss={loss.round(1)}')
            for i, n in enumerate(NAMES):
                err = p[s:e, i] - o[s:e, i]
                # level part: offset over last half; transient: rest
                rows.append((loss[i], r, s, e, n, float(np.median(err[(e-s)//2:]) / SIG[i]), float(err.mean() / SIG[i])))
    rows.sort(reverse=True)
    print('\n== score loss ranking (tick-weighted), median err/sig over 2nd half, mean err/sig')
    for x in rows[:30]:
        print(f'{x[0]:7.1f}  {x[1]} [{x[2]:3d},{x[3]:3d}) {x[4]:7s} late={x[5]:+6.1f}  mean={x[6]:+6.1f}')
    json.dump([list(x) for x in rows], open(f'{OUT}/loss_rank.json', 'w'), indent=0)
