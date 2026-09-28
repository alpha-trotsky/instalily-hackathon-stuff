"""Share as a static map: renewable power P = S*L. Fit P on (L, x, reserve) on old data, test on new."""
import sys; sys.path.insert(0,'fits/power_grid/round2')
from common import *
m=load_pred(); rows=[]
for r in ['R1','R2c','R3','R4']:
    d,o,a,_=run(r); p=predict(m,d)
    sw=np.r_[True,np.any(a[1:]!=a[:-1],1)]; keep=np.ones(len(o),bool)
    for i in np.where(sw)[0]: keep[i:i+3]=False
    keep[:20]=False
    for t in np.where(keep)[0]:
        rows.append((r,t,o[t,2],p[t,2],o[t,0],*a[t],o[t,1]))
runs=np.array([x[0] for x in rows]); R=np.array([x[2:] for x in rows],float)
S,Sv,L,pr,rd,ch,x,f=R.T; P=S*L; cx=1-x
on=rd>0
def X(L,cx,on,rd):
    off=~on
    return np.c_[off, off*(L-100), off*cx, off*cx**2, off*cx*(L-100), on, on*(L-100), on*cx, on*np.minimum(rd,120)/150]
nm=['off:c','off:L','off:1-x','off:(1-x)^2','off:(1-x)L','on:c','on:L','on:1-x','on:min(r,120)']
for lab,mask in [('all',np.ones(len(S),bool)),('old only',np.isin(runs,['R1','R2c']))]:
    c=np.linalg.lstsq(X(L,cx,on,rd)[mask],P[mask],rcond=None)[0]
    Sh=(X(L,cx,on,rd)@c)/L
    print(lab, dict(zip(nm,np.round(c,3))))
    for rr in ['R1','R2c','R3','R4']:
        k=runs==rr
        print(f'   {rr}: static share score {(1/(1+np.abs(Sh[k]-S[k])/SIG[2])).mean():.3f} | v1 {(1/(1+np.abs(Sv[k]-S[k])/SIG[2])).mean():.3f}')
for lab,k in [('reserve on, x=1',on&(x==1)),('reserve on, x<1',on&(x<1))]:
    print(lab,'P=S*L by reserve level:',{float(v):round(float(np.median(P[k&(rd==v)])),2) for v in np.unique(rd[k])})
