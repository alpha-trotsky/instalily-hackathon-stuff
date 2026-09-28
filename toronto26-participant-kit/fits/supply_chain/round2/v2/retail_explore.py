"""Free: retail sales laws on OBSERVED shipments (isolates the retail block). sigma 34.685."""
import json, numpy as np, sys
from scipy.optimize import least_squares
SIG = 34.685
D = {}
for r in ['R1','R2','R3','R4','R5']:
    run = json.load(open(f'data/supply_chain/{r}.json'))['runs'][0]
    D[r] = (np.array([o['shipments'] for o in run['observations']]), np.array([o['inventory_retail'] for o in run['observations']]), run['initial']['inventory_retail'])
# params: D0,kR,dz,az,g,aup,adn,Rs
def sim(p, law, ship, R0):
    D0,kR,dz,az,g,aup,adn,Rs = p
    R=R0; E=0.0; z=1.0; out=np.empty(len(ship))
    for t,s in enumerate(ship):
        E += (aup if s>E else adn)*(s-E)
        rterm = kR*R if law in 'AB' else kR*Rs*(1-np.exp(-R/Rs))
        Dm = D0 + rterm + g*E + dz*z
        sales=min(R+s,max(Dm,0)); R=max(R+s-sales,0); out[t]=R; z*=(1-az)
    return out
def res(p,law,runs):
    return np.concatenate([(sim(p,law,D[r][0],D[r][2])-D[r][1])/SIG for r in runs])
x0=[10,0.012,20,0.1,0.4,0.1,0.1,500]
LB=[-50,0,-60,0.01,0,0.005,0.005,50]; UB=[60,0.2,100,1,1.5,1,1,5000]
def fit(law,train):
    lb=list(LB);ub=list(UB);x=list(x0)
    if law=='A': lb[4],ub[4],x[4]=-1e-9,1e-9,0
    if law in 'AB' or law=='C0': pass
    if law=='B': pass
    if law in ('Bs','C'): pass
    sym = law in ('Bs',)
    best=None
    for k,(au,ad) in enumerate([(0.1,0.1),(0.5,0.05),(0.3,0.03)]):
        x[5],x[6]=au,ad
        def rr(q):
            q=np.array(q); 
            if sym: q[6]=q[5]
            return res(q,law if law!='Bs' else 'B',train)
        f=least_squares(rr,x,bounds=(lb,ub),loss='soft_l1',f_scale=2)
        if best is None or f.cost<best.cost: best=f
    q=best.x.copy()
    if sym: q[6]=q[5]
    return q
L=sys.argv[1:] or ['A','Bs','B','C']
for law in L:
    for train in (['R1','R2','R3'],['R1','R2','R3','R4','R5']):
        p=fit(law,train)
        sc={r:round(float(np.mean(1/(1+np.abs(res(p,law if law!='Bs' else 'B',[r]))))),3) for r in D}
        print(law,'+'.join(train),np.round(p,4).tolist(),sc,flush=True)
