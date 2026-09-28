import json, importlib.util, sys, numpy as np
runs = {'epidemic':['R1','R2'],'wildlife':['R1','R2c'],'ad_auction':['R1','R2c'],'social_contagion':['R1','R2','R3'],
 'power_grid':['R1','R2c'],'reservoir':['R1','R2','R3'],'traffic':['R1','R2','R3'],'supply_chain':['R1','R2','R3'],
 'hospital_queue':['R1','R2c'],'market':['A']}
for s, rl in runs.items():
    spec = importlib.util.spec_from_file_location(f'pred_{s}', f'models/{s}/predict.py')
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
    ctx = json.load(open(f'docs/{s}.json'))['brief']
    eps=[]
    for r in rl:
        for run in json.load(open(f'data/{s}/{r}.json'))['runs']:
            eps.append((run['initial'], run['actions'], run['observations']))
    names=list(eps[0][0].keys())
    allobs=np.concatenate([np.array([[o[n] for n in names] for o in ob])[20:] for _,_,ob in eps])
    sig=0.1*allobs.std(0); tot=[]
    for ini,act,ob in eps:
        pred=np.array([[p[n] for n in names] for p in mod.predict(ini,act,ctx)])
        o=np.array([[x[n] for n in names] for x in ob])
        tot.append((1/(1+np.abs(pred-o)/sig)).mean(0))
    m=np.mean(tot,0); print(s, round(m.mean(),3), dict(zip(names, np.round(m,2))))
