import json, sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'greybox'); import epidemic_model as M
R={}
for f in ['R1','R2']:
    r=json.load(open(f'data/epidemic/{f}.json'))['runs'][0]
    y=np.array([[o['daily_cases'],o['hospital_load']] for o in r['observations']])
    acts=[M.normalize(a, {}) for a in r['actions']]
    R[f]=(r['initial'],acts,y)
SIG=np.array([8.344,4.189])
def params(fit):
    p={k:v[0] for k,v in M.SPEC.items()}
    for m,(names,off) in M.MODULES.items():
        if m not in fit['modules']: p.update(off)
    p.update(fit['params']); return p
fits=sys.argv[1:]
def jump(l,s,k=6):
    sl=np.polyfit(np.arange(6),l[s-6:s],1)[0]; return l[s+k]-(l[s-1]+(k+1)*sl)
SW=[('R1',120),('R1',185),('R1',495),('R1',520),('R2',240),('R2',350),('R2',380)]
fig,ax=plt.subplots(4,2,figsize=(16,12))
for fn in fits:
    fit=json.load(open(f'fits/epidemic/{fn}.json')); p=params(fit)
    line=[fn, 'mods',fit['modules']]
    for j,f in enumerate(['R1','R2']):
        ini,acts,y=R[f]; pr=M.simulate(p,ini,acts)
        sc=np.mean(1/(1+np.abs(pr-y)/SIG),axis=0)
        line.append('%s score %.3f/%.3f'%(f,*sc))
        ax[0,j].plot(pr[:,0],lw=.8,label=fn); ax[1,j].plot((pr[:,0]-y[:,0])/SIG[0],lw=.8)
        ax[2,j].plot(pr[:,1],lw=.8); ax[3,j].plot((pr[:,1]-y[:,1])/SIG[1],lw=.8)
    print(' '.join(map(str,line)))
    print('   jumps model:', ' '.join('%s%d:%+.2f'%(f,s,jump(np.log(M.simulate(p,R[f][0],R[f][1])[:,0]),s)) for f,s in SW))
print('   jumps data :', ' '.join('%s%d:%+.2f'%(f,s,jump(np.log(R[f][2][:,0]),s)) for f,s in SW))
for j,f in enumerate(['R1','R2']):
    ax[0,j].plot(R[f][2][:,0],'k',lw=.6,label='data'); ax[2,j].plot(R[f][2][:,1],'k',lw=.6)
    ax[0,j].set_title(f); ax[0,j].set_ylabel('cases'); ax[1,j].set_ylabel('cases err / sigma'); ax[2,j].set_ylabel('hosp'); ax[3,j].set_ylabel('hosp err / sigma')
    for a in ax[:,j]: a.grid(alpha=.3)
    for a in (ax[1,j],ax[3,j]): a.set_ylim(-8,8)
ax[0,0].legend(fontsize=7)
plt.tight_layout(); plt.savefig('fits/epidemic/review/fit_errors.png',dpi=65)
