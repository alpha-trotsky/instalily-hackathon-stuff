import json, sys, numpy as np, importlib.util
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
spec=importlib.util.spec_from_file_location('rm','greybox/reservoir_model.py'); rm=importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
fit=sys.argv[1]; tag=sys.argv[2]
p=json.load(open(fit))['params']
sig=np.array([20.2,0.157,0.45,0.00102])
names=['level','inflow','outflow','quality']
fig,ax=plt.subplots(4,2,figsize=(14,10),sharex='col')
for j,f in enumerate(['R1','R2']):
    d=json.load(open(f'data/reservoir/{f}.json')); r=d['runs'][0]
    bounds=d['brief']['interventions']
    u=[rm.normalize(a,bounds) for a in r['actions']]
    obs=np.array([[o[k] for k in names] for o in r['observations']])
    pred=np.asarray(rm.simulate(p,r['initial'],u))
    err=pred-obs
    sc=1/(1+np.abs(err)/sig)
    # smoothed error (noise-reduced) via 9-tick moving average
    k=np.ones(9)/9
    print(f, tag,'score/obs', np.round(sc.mean(0),3), 'rmse',np.round(np.sqrt((err**2).mean(0)),4),
          'smoothed-err mean|.|', np.round(np.abs(np.array([np.convolve(err[:,i],k,'same') for i in range(4)])).mean(1),4))
    for i in range(4):
        ax[i,j].plot(err[:,i],lw=.5,color='0.7'); ax[i,j].plot(np.convolve(err[:,i],k,'same'),lw=1.2,color='C3')
        ax[i,j].axhline(0,color='k',lw=.5); ax[i,j].axhspan(-sig[i],sig[i],color='C0',alpha=.15)
        ax[i,j].set_ylabel(names[i]+' err'); 
        for s in r['segments']:
            ax[i,j].axvline(s['start_tick'],color='0.5',ls=':',lw=.6)
    ax[0,j].set_title(f'{f}: {tag} pred - obs (grey raw, red 9-tick MA, band = score sigma)')
    if tag.endswith('q'):
        pass
plt.tight_layout(); plt.savefig(f'fits/reservoir/review/err_{tag}.png',dpi=80)
