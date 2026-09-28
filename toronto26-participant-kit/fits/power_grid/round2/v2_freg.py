"""v2 exploration: frequency as energy-balance regression (steady ticks, >=8 after a switch)."""
import sys; sys.path.insert(0,'fits/power_grid/round2')
from common import *
rows=[]
for r in ['R1','R2c','R3','R4']:
    d,o,a,_=run(r)
    sw=np.r_[True,np.any(a[1:]!=a[:-1],1)]; keep=np.ones(len(o),bool)
    for i in np.where(sw)[0]: keep[i:i+8]=False
    keep[:20]=False
    for t in np.where(keep)[0]:
        rows.append((r,o[t,1],o[t,0],o[t,2]*o[t,0],*a[t]))
runs=np.array([x[0] for x in rows]); R=np.array([x[1:] for x in rows],float)
f,L,P,pr,rd,ch,x=R.T; cx=1-x
old=np.isin(runs,['R1','R2c'])
def rep(lab,X,names):
    for m,ml in [(np.ones(len(f),bool),'all'),(old,'old')]:
        c=np.linalg.lstsq(X[m],f[m],rcond=None)[0]; res=f-X@c
        sc={rr:round(float((1/(1+np.abs(res[runs==rr])/SIG[1])).mean()),3) for rr in ['R1','R2c','R3','R4']}
        print(lab,ml,dict(zip(names,np.round(c,4))),sc)
one=np.ones_like(f)
rep('A lin r',np.c_[one,L-100,rd,cx,cx**2],['c','L','r','cx','cx2'])
rep('B lin r + P',np.c_[one,L-100,P-35,rd,cx,cx**2],['c','L','P','r','cx','cx2'])
rep('C sat r',np.c_[one,L-100,np.minimum(rd,120),cx,cx**2,cx*rd],['c','L','r120','cx','cx2','cx*r'])
rep('D sat r+P',np.c_[one,L-100,P-35,np.minimum(rd,120),cx,cx**2],['c','L','P','r120','cx','cx2'])
