import json, numpy as np, sys
from scipy.optimize import least_squares
f = sys.argv[1] if len(sys.argv)>1 else 'data/reservoir/R1.json'
d=json.load(open(f)); r=d['runs'][-1]
O=r['observations']; A=r['actions']
L=np.array([o['level'] for o in O]); I=np.array([o['inflow'] for o in O]); Q=np.array([o['quality'] for o in O]); Out=np.array([o['outflow'] for o in O])
T=len(O); t=np.arange(1,T+1)
def four(P,t,H=3):
    cols=[np.ones_like(t,dtype=float)]
    for h in range(1,H+1): cols+= [np.cos(2*np.pi*h*t/P), np.sin(2*np.pi*h*t/P)]
    return np.column_stack(cols)
best=None
for P in np.arange(60,80,0.05):
    X=four(P,t); c,res,_,_=np.linalg.lstsq(X[:470],I[:470],rcond=None); e=np.sum((X[:470]@c-I[:470])**2)
    if best is None or e<best[0]: best=(e,P,c)
e,P,c=best; X=four(P,t); fit=X@c; res=I-fit
print('period',round(P,3),'rms',np.sqrt(e/470), 'coef',np.round(c,3))
for a in range(0,T,10): print(a, 'inflow res mean %.3f'%res[a:a+10].mean(), 'level %.0f'%L[a:a+10].mean(), 'Q %.4f'%Q[a:a+10].mean(), 'act',A[a])
# water balance
dL=np.diff(np.concatenate([[r['initial']['level']],L]))
loss=I-Out-dL
print('loss mean by 50:',[round(loss[a:a+50].mean(),2) for a in range(0,T,50)])
