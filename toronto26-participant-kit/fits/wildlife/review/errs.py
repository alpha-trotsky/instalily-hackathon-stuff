import sys, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'.')
from greybox.common import core
m=core.load_model('greybox/wildlife_model.py')
eps=core.load_episodes(['data/wildlife/R1.json','data/wildlife/R2.json'],model=m)
sig=core.score_sigma(eps)
print('sigma',np.round(sig,3))
fits=['m12_all_quick','m13_all_quick','m23_all_quick']
res={}
for f in fits:
    fj=json.load(open(f'fits/wildlife/{f}.json')); p=core.params_for(m,set(fj['modules']),fj['params'])
    res[f]=[core.rollout(m,p,ep) for ep in eps]
segs={'R1':[(0,60,'reset boom'),(60,120,'settled rec'),(120,185,'hunt7'),(185,250,'hunt off'),(250,290,'hab'),(290,330,'hab off'),(330,370,'corr'),(370,440,'corr off'),(440,490,'hunt3.5'),(490,540,'rec')],
      'R2':[(0,30,'reset boom'),(30,55,'hab'),(55,80,'hunt'),(80,105,'rec'),(105,130,'hunt'),(130,155,'hab'),(155,180,'hab rec+corr'),(180,200,'hunt+hab'),(200,300,'hunt7 hold a'),(300,400,'hunt7 hold b')]}
for f in fits:
    print('==',f)
    for ei,(ep,name) in enumerate(zip(eps,['R1','R2'])):
        pr=res[f][ei]; s=core.score(pr,ep['obs'],sig)
        print(' ',name,'score',np.round(s,3),round(s.mean(),3))
        if f=='m12_all_quick':
            for a,b,l in segs[name]:
                s=core.score(pr[a:b],ep['obs'][a:b],sig); print(f'    {a:3d}-{b:3d} {l:14s}',np.round(s,2),round(s.mean(),3))
# error plot for m12
fig,ax=plt.subplots(4,2,figsize=(15,11),sharex='col')
for ei,ep in enumerate(eps):
    for i,n in enumerate(ep['names']):
        for f,c in zip(fits,['C0','C1','C2']):
            ax[i,ei].plot((res[f][ei][:,i]-ep['obs'][:,i])/sig[i],c,lw=.8,label=f)
        ax[i,ei].axhline(0,color='k',lw=.5); ax[i,ei].set_ylabel(n+' err/σ'); ax[i,ei].set_ylim(-40,40); ax[i,ei].grid(alpha=.3)
ax[0,0].legend(fontsize=7); ax[0,0].set_title('R1'); ax[0,1].set_title('R2')
plt.tight_layout(); plt.savefig('fits/wildlife/review/pair_errors_sigma.png',dpi=65)
