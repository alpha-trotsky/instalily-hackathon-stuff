import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
K=['load','frequency','renewable_share']; C=['price_signal','reserve_dispatch','charging_allowance','interconnector']
fig,ax=plt.subplots(5,2,figsize=(16,14),sharex='col')
for j,f in enumerate(['R1','R2']):
    r=json.load(open(f'data/power_grid/{f}.json'))['runs'][0]
    O=np.array([[o[k] for k in K] for o in r['observations']]); A=np.array([[a[k] for k in C] for a in r['actions']])
    L,F,S=O.T; t=np.arange(len(L))
    ax[0,j].plot(t,L); ax[0,j].set_ylabel('load')
    ax[1,j].plot(t,F); ax[1,j].set_ylabel('freq')
    ax[2,j].plot(t,S); ax[2,j].set_ylabel('share')
    ax[3,j].plot(t,S*L,label='S*L (ren MW)'); ax[3,j].plot(t,(1-S)*L,label='(1-S)*L'); ax[3,j].legend(); ax[3,j].set_ylabel('power')
    ax[4,j].plot(t,A[:,0],label='price');ax[4,j].plot(t,A[:,1]/150,label='res/150');ax[4,j].plot(t,A[:,2],label='chg');ax[4,j].plot(t,A[:,3],label='ic');ax[4,j].legend()
    for a in ax[:,j]: a.grid(alpha=.3)
    ax[0,j].set_title(f)
plt.tight_layout(); plt.savefig('fits/power_grid/review/share_scan.png',dpi=70)
