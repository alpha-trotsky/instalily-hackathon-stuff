import json, sys, os, numpy as np
sys.path.insert(0, os.getcwd())
from greybox.common import core
f = json.load(open(sys.argv[1])); model = core.load_model(sys.argv[2])
C=('order_quantity','lead_time_buy','product_mix','production_effort','receiving_effort','maintenance')
S=np.array([1.12,12.1,34.7])
for r in sys.argv[3].split(','):
    ep = core.load_episodes([f'data/supply_chain/{r}.json'], model=model)[0]
    y = core.rollout(model, f['params'], ep); o=ep['obs']
    keys=[tuple(round(a[c],3) for c in C) for a in ep['actions']]
    st=0
    for t in range(1,len(keys)+1):
        if t==len(keys) or keys[t]!=keys[st]:
            e=min(t,st+999); a=max(st,e-10)
            print(f'{r} {st:4d}-{t-1:4d} {keys[st]} last10 data/model ship {o[a:e,0].mean():5.1f}/{y[a:e,0].mean():5.1f} sup {o[a:e,1].mean():5.0f}/{y[a:e,1].mean():5.0f} ret {o[a:e,2].mean():5.0f}/{y[a:e,2].mean():5.0f} | seg score {np.round((1/(1+np.abs(y[st:t]-o[st:t])/S)).mean(0),2)}')
            st=t
