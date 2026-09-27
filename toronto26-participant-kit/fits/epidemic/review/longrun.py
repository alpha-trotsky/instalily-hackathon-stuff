import json, sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'greybox'); import epidemic_model as M
def params(fit):
    p={k:v[0] for k,v in M.SPEC.items()}
    for m,(names,off) in M.MODULES.items():
        if m not in fit['modules']: p.update(off)
    p.update(fit['params']); return p
ini={'daily_cases':170,'hospital_load':45}
scen={'recovery':[(0,0,0)]*4000,'pulse':[(1,1,1)]*4000,'mask':[(0,1,0)]*4000,'vacc':[(0,0,1)]*4000,
      'rand':[tuple(np.random.default_rng(1).uniform(0,1,3)) for _ in range(4000)]}
rng=np.random.default_rng(2); blk=[]
while len(blk)<4000: blk+= [tuple(rng.integers(0,2,3).astype(float))]*int(rng.integers(20,200))
scen['blocks']=blk[:4000]
fits=sys.argv[1:]
fig,ax=plt.subplots(len(scen),2,figsize=(16,16))
for fn in fits:
    p=params(json.load(open(f'fits/epidemic/{fn}.json')))
    row=[]
    for i,(n,a) in enumerate(scen.items()):
        y=M.simulate(p,ini,a); ax[i,0].plot(y[:,0],lw=.7,label=fn); ax[i,1].plot(y[:,1],lw=.7); ax[i,0].set_ylabel(n)
        row.append('%s c[3000:]=%.0f..%.0f h=%.0f..%.0f'%(n,y[3000:,0].min(),y[3000:,0].max(),y[3000:,1].min(),y[3000:,1].max()))
    print(fn); print('   '+'\n   '.join(row))
ax[0,0].legend(fontsize=7)
for a in ax.ravel(): a.grid(alpha=.3)
plt.tight_layout(); plt.savefig('fits/epidemic/review/longrun_4000.png',dpi=60)
