"""Is conversions a lagged linear filter of impressions (spend/price(bid))? What is left over?"""
import json, numpy as np
from scipy.optimize import least_squares
obs=['win_rate','spend','conversions']
def load(f):
    r=json.load(open('data/ad_auction/%s.json'%f))['runs'][0]
    A=np.array([[a['bid'],a['budget_cap'],a['targeting_breadth']] for a in r['actions']])
    return A,np.array([[o[k] for k in obs] for o in r['observations']])
D=[load('R1'),load('R2')]
def sim(th,A,O):
    k,rho,l1,l2,wb=th
    bid=np.maximum(A[:,0],1e-3); imp=O[:,1]/bid**rho*np.exp(wb*(A[:,2]-0.55))
    s1=s2=0; out=[]; buf=[0,0]
    for t in range(len(A)):
        e=buf.pop(0); buf.append(imp[t])
        s1+= l1*(e-s1); s2+= l2*(s1-s2); out.append(k*s2)
    return np.array(out)
def res(th): return np.concatenate([sim(th,A,O)-O[:,2] for A,O in D])
sol=least_squares(res,[0.25,0.3,0.3,0.3,0.0],bounds=([0,-2,0.01,0.01,-10],[5,3,1,1,10]))
print('params k,rho,l1,l2,wb',np.round(sol.x,3),'rmse',np.sqrt(np.mean(sol.fun**2)))
for (A,O),n in zip(D,['R1','R2']):
    r=sim(sol.x,A,O)-O[:,2]
    print(n,'resid (pred-obs) by 20-tick block:',np.round([r[i:i+20].mean() for i in range(0,len(r),20)],2))
