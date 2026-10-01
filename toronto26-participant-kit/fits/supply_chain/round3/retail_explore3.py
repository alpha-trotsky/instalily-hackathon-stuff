"""Free: retail sales laws on OBSERVED shipments incl. R6 (isolates the retail block). sigma = heldout3 retail sigma."""
import json, numpy as np, sys
from scipy.optimize import least_squares
SIG = 34.945
RUNS = ['R1','R2','R3','R4','R5','R6']
D = {}
for r in RUNS:
    run = json.load(open(f'data/supply_chain/{r}.json'))['runs'][0]
    D[r] = (np.array([o['shipments'] for o in run['observations']]), np.array([o['inventory_retail'] for o in run['observations']]),
            run['initial']['inventory_retail'], np.array([a['order_quantity'] for a in run['actions']]), np.array([a['product_mix'] for a in run['actions']]))
# common: D0, dz, az, aup, adn ; law-specific extras
LAWS = {
 'v2':  (['D0','kR','dz','az','g','aup','adn'], [14,0.013,11,0.05,0.23,0.07,0.98], [0,1e-4,-40,0.05,0,0.005,0.005],[60,0.1,60,1,1,1,1]),
 'v2e0':(['D0','kR','dz','az','g','aup','adn','E0'], [12,0.007,5,0.05,0.45,0.05,0.05,28], [0,1e-4,-40,0.05,0,0.005,0.005,0],[60,0.1,60,1,1.5,1,1,60]),
 'syme0':(['D0','kR','dz','az','g','aup','E0'], [12,0.007,5,0.05,0.45,0.05,28], [0,1e-4,-40,0.05,0,0.005,0],[60,0.1,60,1,1.5,1,60]),
 'tanh':(['D0','kR','dz','az','Dg','Ek','aup','adn'], [12,0.01,11,0.05,16,10,0.07,0.9], [0,0,-40,0.05,0,1,0.005,0.005],[60,0.1,60,1,40,60,1,1]),
 'tanhsp':(['D0','kR','dz','az','Dg','Ek','aup','adn','R0'], [12,0.03,11,0.05,16,10,0.07,0.9,700], [0,0,-40,0.05,0,1,0.005,0.005,0],[60,0.2,60,1,40,60,1,1,2000]),
 'tanhq':(['D0','kR','dz','az','Dg','Ek','aup','adn','kq'], [12,0.003,11,0.05,16,10,0.07,0.9,0.005], [0,0,-40,0.05,0,1,0.005,0.005,0],[60,0.1,60,1,40,60,1,1,0.1]),
}
def sim(p, law, ship, R0, q, mix):
    P = dict(zip(LAWS[law][0], p))
    R=R0; E=P.get('E0',0.0); z=1.0; out=np.empty(len(ship))
    if 'adn' not in P: P['adn']=P['aup']
    for t,s in enumerate(ship):
        E += (P['aup'] if s>E else P['adn'])*(s-E)
        if law in ('v2','v2e0','syme0'): Dm = P['D0'] + P['kR']*R + P['g']*E
        else:
            Dm = P['D0'] + P['Dg']*np.tanh(E/P['Ek'])
            if law == 'tanh': Dm += P['kR']*R
            if law == 'tanhsp': Dm += P['kR']*50*np.logaddexp(0,(R-P['R0'])/50)
            if law == 'tanhq': Dm += P['kR']*R + P['kq']*R*R/1000
        Dm += P['dz']*z
        sales=min(R+s,max(Dm,0)); R=max(R+s-sales,0); out[t]=R; z*=(1-P['az'])
    return out
def res(p,law,runs):
    return np.concatenate([(sim(p,law,D[r][0],D[r][2],D[r][3],D[r][4])-D[r][1])/SIG for r in runs])
def fit(law,train):
    names,x0,lb,ub = LAWS[law]; best=None
    for k in range(3):
        x=np.clip(np.array(x0,float)*(1+0.3*k*np.random.default_rng(k).normal(size=len(x0))), np.array(lb)+1e-6, np.array(ub)-1e-6)
        f=least_squares(lambda q: res(q,law,train),x,bounds=(lb,ub),loss='soft_l1',f_scale=2)
        if best is None or f.cost<best.cost: best=f
    return best.x
sc = lambda p,law,r: round(float(np.mean(1/(1+np.abs(res(p,law,[r]))))),3)
for law in (sys.argv[1:] or LAWS):
    p=fit(law,RUNS)
    print(law,'ALL',dict(zip(LAWS[law][0],np.round(p,4).tolist())),{r:sc(p,law,r) for r in RUNS},flush=True)
    loo={}
    for h in ['R4','R5','R6','R1']:
        p=fit(law,[r for r in RUNS if r!=h]); loo[h]=sc(p,law,h)
    print(law,'LOO',loo,'mean',round(np.mean(list(loo.values())),3),flush=True)
