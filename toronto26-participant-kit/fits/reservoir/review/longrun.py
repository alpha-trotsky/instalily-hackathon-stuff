import json, numpy as np, importlib.util
spec=importlib.util.spec_from_file_location('rm','greybox/reservoir_model.py'); rm=importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
B={'release_rate':[0,12],'irrigation_allocation':[0,8],'withdrawal_depth':[0,1],'aeration':[0,1]}
init={'level':500,'inflow':10,'outflow':6,'quality':0.86}
REC=rm.RECOVERY; PUL=rm.PULSE
def mix(u): return {c: REC[c]+u*(PUL[c]-REC[c]) for c in rm.CONTROLS}
scen={'recovery':[REC]*4000,'pulse':[PUL]*4000,'pulse0.7':[mix(0.7)]*4000,'rel12only':[dict(REC,release_rate=12)]*4000,
      'rel10only':[dict(REC,release_rate=10)]*4000,'alt200':([PUL]*200+[REC]*200)*10}
for tag in ['m13_all','m12_all']:
    p=json.load(open(f'fits/reservoir/review/{tag}.json'))['params']
    for s,acts in scen.items():
        y=np.asarray(rm.simulate(p,init,[rm.normalize(a,B) for a in acts]))
        late=y[3000:]
        print(f"{tag} {s:10s} late mean L {late[:,0].mean():6.1f} [{late[:,0].min():5.0f},{late[:,0].max():5.0f}] in {late[:,1].mean():6.2f} out {late[:,2].mean():6.2f} q {late[:,3].mean():.4f}  finite {np.isfinite(y).all()}")
