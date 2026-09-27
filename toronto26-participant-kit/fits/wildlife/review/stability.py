import sys, json, time, itertools, numpy as np
sys.path.insert(0,'.')
from greybox.common import core
m=core.load_model('greybox/wildlife_model.py')
init={'prey_north':85,'predator_north':11.5,'prey_south':85,'predator_south':11.5}
for f in ['m12_all_quick','m13_all_quick','m23_all_quick']:
    fj=json.load(open(f'fits/wildlife/{f}.json')); p=core.params_for(m,set(fj['modules']),fj['params'])
    worst=[]; t0=time.time()
    for h,pr,c in itertools.product([0,2,3.5,5,7,8],[0,0.1,0.4,0.7,1],[0,0.5,1]):
        u=[m.normalize({'hunting_quota':h,'habitat_protection':pr,'corridor_access':c},{})]*4000
        y=np.asarray(m.simulate(p,init,u)); tail=y[3000:]
        rel=(tail.max(0)-tail.min(0))/np.maximum(tail.mean(0),1e-6)
        worst.append((rel.max(),h,pr,c,np.round(tail.mean(0),2), np.round(y[300],2)))
    dt=(time.time()-t0)/90
    worst.sort(key=lambda w:-w[0])
    print(f, f'{dt:.2f}s per 4000-step episode')
    for w in worst[:4]: print('   osc(rel range last 1000)',round(w[0],4),'h,p,c',w[1:4],'mean',w[4])
    # steady-state extremes
    lo=min(worst,key=lambda w:w[4].min()); print('   lowest level',lo[1:5])
    # random schedule
    rng=np.random.default_rng(0)
    for k in range(3):
        sch=core.random_schedule(fj.get('bounds',{'hunting_quota':[0,8],'habitat_protection':[0,1],'corridor_access':[0,1]}),4000,'mixed',rng) if hasattr(core,'random_schedule') else None
        u=[m.normalize(a,{'hunting_quota':[0,8],'habitat_protection':[0,1],'corridor_access':[0,1]}) for a in sch]
        y=np.asarray(m.simulate(p,init,u)); print('   random mixed: finite',np.isfinite(y).all(),'min',np.round(y.min(0),3),'max',np.round(y.max(0),1))
