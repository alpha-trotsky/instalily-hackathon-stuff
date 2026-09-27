# How strongly would the proposed reserve schedules separate settlement competition (cS) from none?
# For each cS, refit only the corridor params (mvX_N, mvX_S, mvY, aT) on R1+R2 (all ticks), others from m12_all_quick.
import sys, json, copy, numpy as np
from scipy.optimize import least_squares
sys.path.insert(0,'.')
from greybox.common import core
m=core.load_model('greybox/wildlife_model.py')
eps=core.load_episodes(['data/wildlife/R1.json','data/wildlife/R2.json'],model=m)
sig=core.score_sigma(eps)
fj=json.load(open('fits/wildlife/m12_all_quick.json')); base=core.params_for(m,{'m1','m2','m3'},fj['params'])
names=['mvX_N','mvX_S','mvY','aT']
def resid(th,cS):
    p=dict(base); p['cS']=cS
    for n,v in zip(names,th): p[n]=1/(1+np.exp(-v))
    r=[]
    for ep in eps:
        y=core.rollout(m,p,ep); r.append(((np.log(y)-np.log(ep['obs']))/0.01).ravel())
    return np.concatenate(r)
H7={'hunting_quota':7.0,'habitat_protection':1.0,'corridor_access':0.0}
H7C=dict(H7,corridor_access=1.0)
REC={'hunting_quota':0.0,'habitat_protection':1.0,'corridor_access':0.0}
RECC=dict(REC,corridor_access=1.0)
ext_B=[m.normalize(H7C,{})]*30+[m.normalize(H7,{})]*30
ext_R=[m.normalize(RECC,{})]*30+[m.normalize(REC,{})]*30
out={}
for cS in [0.0,0.3,1.0,3.0]:
    th0=[np.log(base[n]/(1-base[n])) for n in names]
    sol=least_squares(resid,th0,args=(cS,),loss='soft_l1',f_scale=2,max_nfev=60)
    p=dict(base); p['cS']=cS
    for n,v in zip(names,sol.x): p[n]=1/(1+np.exp(-v))
    cost=sol.cost
    ep2=eps[1]
    yB=np.asarray(m.simulate(p,ep2['initial'],ep2['u']+ext_B))[400:]
    yR=np.asarray(m.simulate(p,{'prey_north':85,'predator_north':11.5,'prey_south':85,'predator_south':11.5},ext_R))
    out[cS]=(yB,yR)
    print(f'cS={cS}: cost {cost:.0f}', {n:round(p[n],4) for n in names})
for cS in [0.3,1.0,3.0]:
    for k,lab in [(0,'B: R2 cont corr+hunt30|hunt30'),(1,'F: reset corr30|rec30')]:
        d=np.abs(out[cS][k]-out[0.0][k])/sig
        print(f'  cS {cS} vs 0, {lab}: mean |diff|/sigma per obs',np.round(d.mean(0),2),'max',np.round(d.max(0),1))
