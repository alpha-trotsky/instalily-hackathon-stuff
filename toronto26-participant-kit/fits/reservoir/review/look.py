import json, numpy as np
def load(f):
    r=json.load(open(f'data/reservoir/{f}.json'))['runs'][0]
    O={k:np.array([o[k] for o in r['observations']]) for k in ['level','inflow','outflow','quality']}
    A={k:np.array([a[k] for a in r['actions']]) for k in ['release_rate','irrigation_allocation','withdrawal_depth','aeration']}
    return r['initial'],O,A
for f in ['R1','R2']:
    ini,O,A=load(f)
    print(f,ini)
    L,I,Q,Out=O['level'],O['inflow'],O['quality'],O['outflow']
    # mass balance: dL vs I - Out
    dL=np.diff(np.r_[ini['level'],L])
    res=dL-(I-Out)
    for a,b in [(0,40),(40,60),(60,110),(110,140),(140,200),(200,250),(250,300),(300,360),(360,410),(410,450),(450,470),(470,530),(530,550),(40,90),(90,140),(140,190),(190,240),(240,280),(280,340),(340,370),(370,400)]:
        if b>len(L): continue
        s=slice(a,b)
        print(f"{a:4d}-{b:4d} L {L[a]:6.1f}->{L[b-1]:6.1f} I {I[s].mean():6.2f} Out {Out[s].mean():6.2f} dL-(I-O) {res[s].mean():+6.2f} Q {Q[s].mean():.4f}±{Q[s].std():.4f} req {A['release_rate'][a]+A['irrigation_allocation'][a]:.0f}")
