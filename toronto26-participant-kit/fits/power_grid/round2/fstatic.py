"""Is frequency a static map of (observed load, controls)? Regression on all data, skipping 3 ticks after each switch."""
import sys; sys.path.insert(0,'fits/power_grid/round2')
from common import *
m=load_pred()
rows=[]
for r in ['R1','R2c','R3','R4']:
    d,o,a,_=run(r); p=predict(m,d)
    sw=np.r_[True,np.any(a[1:]!=a[:-1],1)]; keep=np.ones(len(o),bool)
    for i in np.where(sw)[0]: keep[i:i+3]=False
    keep[:20]=False
    for t in np.where(keep)[0]:
        pr,rd,ch,x=a[t]; L=o[t,0]; Ll=o[max(t-2,0),0]
        rows.append((r,t,o[t,1],p[t,1],L,Ll,pr,rd,ch,x,o[t,2]))
R=np.array([x[2:] for x in rows],float); runs=np.array([x[0] for x in rows])
f,fv,L,Ll,pr,rd,ch,x,S=R.T
rs=np.minimum(rd,120)/150; cx=1-x
def feats(L,Ll,rs,rd,cx,ch,S):
    return np.c_[np.ones_like(L),L-100,Ll-L,rs,(rd>0)*1.0,cx,cx**2,rs*cx,1-ch]
X=feats(L,Ll,rs,rd,cx,ch,S)
names=['c','L-100','Llag2-L','min(r,120)/150','r>0','1-x','(1-x)^2','r*(1-x)','1-ch']
for lab,mask in [('all',np.ones(len(f),bool)),('fit R1+R2c -> test R3+R4',np.isin(runs,['R1','R2c']))]:
    c=np.linalg.lstsq(X[mask],f[mask],rcond=None)[0]
    res=f-X@c
    print(lab, dict(zip(names,np.round(c,4))))
    for rr in ['R1','R2c','R3','R4']:
        k=runs==rr
        sc=(1/(1+np.abs(res[k])/SIG[1])).mean(); scv=(1/(1+np.abs(fv[k]-f[k])/SIG[1])).mean()
        print(f'   {rr}: static-map(obs load) rmse {np.sqrt((res[k]**2).mean()):.3f} Hz score {sc:.3f} | v1 rmse {np.sqrt(((fv[k]-f[k])**2).mean()):.3f} score {scv:.3f}')
