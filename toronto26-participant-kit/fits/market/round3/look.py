import json,sys,numpy as np
sys.path.insert(0,'.')
from greybox.common import core
m=core.load_model('greybox/market_model_v2.py')
pj=json.load(open('models/market/params.json'))
P=m.params_for(pj['modules'],pj['params'])
for r in sys.argv[1:]:
    ep=core.load_episodes([f'data/market/{r}.json'],names=['price','volume','depth'],model=m)[0]
    print(r,'initial',ep['initial'],len(ep['obs']))
    pred=core.rollout(m,P,ep); o=ep['obs']; u=ep['u']
    for t in list(range(0,20,2))+list(range(20,len(o),10)):
        print(t, np.round(u[t],2), o[t].round(2), pred[t].round(2))
