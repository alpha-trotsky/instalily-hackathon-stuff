import json, numpy as np
p=np.load('fits/reservoir/review/season_params.npy')
def season(t): return p[0]+p[1]*np.sin(2*np.pi*t/p[3])+p[2]*np.cos(2*np.pi*t/p[3])
rows=[]
for f in ['R1','R2']:
    r=json.load(open(f'data/reservoir/{f}.json'))['runs'][0]
    L=np.array([o['level'] for o in r['observations']]); I=np.array([o['inflow'] for o in r['observations']]); O=np.array([o['outflow'] for o in r['observations']])
    t=np.arange(1,len(L)+1); S=season(t)
    W=10
    for a in range(10,len(L)-W,W):
        b=a+W
        dL=(L[b-1]-L[a-1])/W  # net per tick over ticks a..b-1
        net_obs=np.mean(I[a:b]-O[a:b]); gw=np.mean(I[a:b]-S[a:b])
        rows.append((f,a,L[a:b].mean(),dL,dL-net_obs,gw))
print('run  a    V      dV/dt  E=dL-(I-O)  gwexcess  E+gw(total exch vs season)')
for f,a,V,dL,E,gw in rows:
    print(f"{f} {a:4d} {V:6.0f} {dL:+6.2f} {E:+6.2f} {gw:+5.2f} {E+gw:+6.2f}")
R=np.array([(V,dL,E) for f,a,V,dL,E,gw in rows if V<925])
X=np.c_[np.ones(len(R)),R[:,0]/100,R[:,1]]
c,*_=np.linalg.lstsq(X,R[:,2],rcond=None); print('E ~ a + b*V/100 + c*dV/dt (V<925):',np.round(c,3),'resid rms',np.round(np.std(R[:,2]-X@c),3))
