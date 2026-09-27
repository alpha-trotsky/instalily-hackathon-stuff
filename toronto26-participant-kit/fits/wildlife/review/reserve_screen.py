import sys, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'.')
from greybox.common import core
m=core.load_model('greybox/wildlife_model.py')
eps=core.load_episodes(['data/wildlife/R1.json','data/wildlife/R2.json'],model=m)
sig=core.score_sigma(eps); ep2=eps[1]
fits=['m12_all_quick','m13_all_quick','m23_all_quick']
P={f:core.params_for(m,set(json.load(open(f'fits/wildlife/{f}.json'))['modules']),json.load(open(f'fits/wildlife/{f}.json'))['params']) for f in fits}
A=lambda h,p,c:{'hunting_quota':h,'habitat_protection':p,'corridor_access':c}
N=lambda a:m.normalize(a,{})
sched={
 'B corr+hunt30|hunt30':[N(A(7,1,0 or 1))]*0+[N(A(7,1,1))]*30+[N(A(7,1,0))]*30,
 'C joint.85 x25|rec35':[N(A(5.95,0.235,0.85))]*25+[N(A(0,1,0))]*35,
 'C2 joint1.0 x20|rec40':[N(A(7,0.1,1))]*20+[N(A(0,1,0))]*40,
 'P5 rec20|h10|rec10|h10|rec10':[N(A(0,1,0))]*20+[N(A(7,1,0))]*10+[N(A(0,1,0))]*10+[N(A(7,1,0))]*10+[N(A(0,1,0))]*10,
 'R rec60':[N(A(0,1,0))]*60,
}
fig,ax=plt.subplots(4,len(sched),figsize=(20,10))
for j,(k,ext) in enumerate(sched.items()):
    Y={f:np.asarray(m.simulate(P[f],ep2['initial'],ep2['u']+ext))[400:] for f in fits}
    d=lambda a,b: (np.abs(Y[a]-Y[b])/sig).mean(0)
    print(f'{k:32s} m12/m13',np.round(d(fits[0],fits[1]),2),' m12/m23',np.round(d(fits[0],fits[2]),2),' m13/m23',np.round(d(fits[1],fits[2]),2))
    for i in range(4):
        for f in fits: ax[i,j].plot(Y[f][:,i],lw=.9,label=f)
    ax[0,j].set_title(k,fontsize=8)
ax[0,0].legend(fontsize=6); plt.tight_layout(); plt.savefig('fits/wildlife/review/reserve_screen.png',dpi=60)
