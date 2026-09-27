import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
OBS=['prey_north','predator_north','prey_south','predator_south']
for f in ['R1','R2']:
    r=json.load(open(f'data/wildlife/{f}.json'))['runs'][0]
    Y=np.array([[o[k] for k in OBS] for o in r['observations']])
    A=r['actions']
    fig,ax=plt.subplots(6,1,figsize=(13,15),sharex=True)
    for i,k in enumerate(OBS): ax[i].plot(Y[:,i],'k',lw=.8); ax[i].set_ylabel(k); ax[i].grid(alpha=.3)
    ax[4].plot(Y[:,0]/Y[:,2],label='prey N/S'); ax[4].plot(Y[:,1]/Y[:,3],label='pred N/S'); ax[4].legend(); ax[4].grid(alpha=.3)
    ax[5].plot([a['hunting_quota']/8 for a in A],label='hunt/8'); ax[5].plot([a['habitat_protection'] for a in A],label='habitat'); ax[5].plot([a['corridor_access'] for a in A],label='corridor'); ax[5].legend()
    for a in ax: 
        for s in range(0,len(A),20): pass
    plt.tight_layout(); plt.savefig(f'fits/wildlife/review/{f}_raw.png',dpi=70)
