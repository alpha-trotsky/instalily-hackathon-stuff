import json, numpy as np
from scipy.optimize import least_squares
def load(f):
    r=json.load(open(f'data/reservoir/{f}.json'))['runs'][0]
    return np.array([o['inflow'] for o in r['observations']]), np.array([o['level'] for o in r['observations']])
I1,L1=load('R1'); I2,L2=load('R2')
t1=np.arange(1,len(I1)+1); t2=np.arange(1,len(I2)+1)
# clean masks: exclude groundwater-excess windows
m1=np.ones(len(I1),bool); m1[500:540]=False
m2=np.ones(len(I2),bool); m2[90:290]=False
def model(p,t):
    c,a,b,P=p[:4]
    return c+a*np.sin(2*np.pi*t/P)+b*np.cos(2*np.pi*t/P)
for name,ts,ys in [('R1',[t1[m1]],[I1[m1]]),('R2',[t2[m2]],[I2[m2]]),('both',[t1[m1],t2[m2]],[I1[m1],I2[m2]])]:
    t=np.concatenate(ts); y=np.concatenate(ys)
    r=least_squares(lambda p: model(p,t)-y,[11.28,2.25,0,67.75])
    J=r.jac; s2=np.sum(r.fun**2)/(len(y)-4); cov=np.linalg.inv(J.T@J)*s2
    print(name,'n',len(y),'params',np.round(r.x,4),'se',np.round(np.sqrt(np.diag(cov)),4),'rms',round(np.sqrt(np.mean(r.fun**2)),4))
    if name=='both':
        P,se=r.x[3],np.sqrt(cov[3,3])
        # phase error at t=4000 in ticks
        print('phase drift at t=4000 per 1 se of P: %.2f ticks; score impact: amplitude*2pi*dt/P = %.3f inflow'%(4000*se/P, 2.25*2*np.pi*4000*se/P/P))
        res=y-model(r.x,t)
        # residual by cycle in R1 (check amplitude/mean drift)
tt=t1[m1]; yy=I1[m1]
r=least_squares(lambda p: model(p,np.concatenate([t1[m1],t2[m2]]))-np.concatenate([I1[m1],I2[m2]]),[11.28,2.25,0,67.75]).x
res1=I1-model(r,t1); res2=I2-model(r,t2)
for k in range(0,550,68):
    s=slice(k,min(k+68,550)); print('R1 cycle',k, 'mean res %.3f'%res1[s][m1[s]].mean(), ' amp proxy max-min %.2f'%(I1[s].max()-I1[s].min()))
print('R2 first 10 res',np.round(res2[:10],3),' R1 first 10',np.round(res1[:10],3))
print('R2 excess 90-290 by 20:',[round(res2[k:k+20].mean(),2) for k in range(80,300,20)])
print('R1 excess 480-550 by 10:',[round(res1[k:k+10].mean(),2) for k in range(480,550,10)])
np.save('fits/reservoir/review/season_params.npy',r)
