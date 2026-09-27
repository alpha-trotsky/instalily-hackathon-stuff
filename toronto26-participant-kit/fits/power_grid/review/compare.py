"""Reviewer: plot fits + residuals for review fit files, and segment-wise cost differences."""
import sys, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'fits/power_grid/review'); import pg_model_v1s as m
fits = sys.argv[1:]
K = list(m.OBSERVABLES); SIG = np.array([0.5, 0.03, 0.003])
runs = {}
for f in ['R1', 'R2']:
    r = json.load(open(f'data/power_grid/{f}.json')); b = r['brief']['interventions']; run = r['runs'][0]
    runs[f] = (run, [m.normalize(a, b) for a in run['actions']], np.array([[o[k] for k in K] for o in run['observations']]))
P = {f: json.load(open(f))['params'] for f in fits}
fig, ax = plt.subplots(6, 2, figsize=(18, 16), sharex='col')
for j, (rn, (run, u, O)) in enumerate(runs.items()):
    for i, k in enumerate(K):
        ax[2*i, j].plot(O[:, i], 'k', lw=1, label='data')
        for f in fits:
            y = np.asarray(m.simulate(P[f], run['initial'], u))
            ax[2*i, j].plot(y[:, i], lw=1, label=f.split('/')[-1])
            ax[2*i+1, j].plot((y[:, i]-O[:, i]) / SIG[i], lw=.8)
        ax[2*i, j].set_ylabel(k); ax[2*i+1, j].set_ylabel(k+' err/σfit'); ax[2*i+1, j].axhline(0, c='k', lw=.5)
    ax[0, j].set_title(rn); ax[0, j].legend(fontsize=7)
    for a in ax[:, j]: a.grid(alpha=.3)
plt.tight_layout(); plt.savefig('fits/power_grid/review/v1s_pairs_err.png', dpi=65)
# segment costs (soft_l1 f_scale 2, like fit.py)
def rho(r): z = (r/2)**2; return 2*2*2*(np.sqrt(1+z)-1)/2*2/2  # 0.5*sum f^2*rho(z) ~ with f=2
for rn, (run, u, O) in runs.items():
    acts = np.array(u); ch = [0] + [t for t in range(1, len(acts)) if (acts[t] != acts[t-1]).any()] + [len(acts)]
    ys = {f: np.asarray(m.simulate(P[f], run['initial'], u)) for f in fits}
    print(rn)
    for a, b in zip(ch[:-1], ch[1:]):
        row = []
        for f in fits:
            r = (ys[f][a:b]-O[a:b])/SIG; z = r**2/4; c = 0.5*4*2*(np.sqrt(1+z)-1)
            row.append(c.sum(0).round(0).tolist())
        print(f'  {a:3d}-{b:3d}', np.round(acts[a], 2), ' | '.join(str(x) for x in row))
