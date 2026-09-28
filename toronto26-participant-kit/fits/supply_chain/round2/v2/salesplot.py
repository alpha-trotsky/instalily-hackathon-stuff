import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(5,1,figsize=(13,15))
for i,r in enumerate(['R1','R2','R3','R4','R5']):
    run=json.load(open(f'data/supply_chain/{r}.json'))['runs'][0]
    O=np.array([[o['shipments'],o['inventory_supplier'],o['inventory_retail']] for o in run['observations']])
    R0=run['initial']['inventory_retail']
    Rp=np.concatenate([[R0],O[:-1,2]])
    sales=O[:,0]-(O[:,2]-Rp)
    k=5; sm=np.convolve(sales,np.ones(k)/k,'same')
    ax[i].plot(sm,'b',lw=.8,label='sales (5-avg)'); ax[i].plot(O[:,0],'orange',lw=.5,label='ship')
    a2=ax[i].twinx(); a2.plot(O[:,2],'k',lw=.8); ax[i].set_ylabel(r); ax[i].legend(fontsize=7); ax[i].grid(alpha=.3)
    mix=np.array([a['product_mix'] for a in run['actions']]); ax[i].plot(mix*20,'g',lw=.6)
fig.tight_layout(); fig.savefig('fits/supply_chain/round2/v2/sales.png',dpi=80)
