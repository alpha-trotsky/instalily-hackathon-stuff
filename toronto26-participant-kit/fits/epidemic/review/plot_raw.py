import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
for f in ['R1','R2']:
    r=json.load(open(f'data/epidemic/{f}.json'))['runs'][0]
    y=np.array([[o['daily_cases'],o['hospital_load']] for o in r['observations']])
    a=np.array([[x['school_closure'],x['mask_mandate'],x['vaccination_rate']/0.003] for x in r['actions']])
    t=np.arange(1,len(y)+1)
    fig,ax=plt.subplots(4,1,figsize=(14,11),sharex=True)
    ax[0].plot([0],[r['initial']['daily_cases']],'ro'); ax[0].plot(t,y[:,0],lw=.8); ax[0].set_ylabel('cases')
    ax[1].semilogy(t,y[:,0],lw=.8); ax[1].semilogy([0],[r['initial']['daily_cases']],'ro'); ax[1].set_ylabel('log cases')
    ax[2].plot(t,y[:,1],lw=.8,c='C1'); ax[2].plot([0],[r['initial']['hospital_load']],'ro'); ax[2].set_ylabel('hosp')
    for i,n in enumerate(['school','mask','vacc/0.003']): ax[3].step(t,a[:,i]+i*0.02,where='post',label=n)
    ax[3].legend()
    for x in ax:
        for c in np.where(np.any(np.diff(a,axis=0)!=0,axis=1))[0]: x.axvline(c+1.5,c='k',lw=.3)
        x.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(f'fits/epidemic/review/raw_{f}.png',dpi=70)
