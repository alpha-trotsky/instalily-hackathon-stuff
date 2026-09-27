import json, numpy as np, importlib.util
spec=importlib.util.spec_from_file_location('rm','greybox/reservoir_model.py'); rm=importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
B={'release_rate':[0,12],'irrigation_allocation':[0,8],'withdrawal_depth':[0,1],'aeration':[0,1]}
P=rm.PULSE
for tag in ['m13_all','m12_all']:
    p=json.load(open(f'fits/reservoir/review/{tag}.json'))['params']
    t=np.arange(1,51); river=p['c_in']+p['A_s']*np.sin(2*np.pi*t/p['P'])+p['A_c']*np.cos(2*np.pi*t/p['P'])
    for L0 in [400,500,600]:
        y=np.asarray(rm.simulate(p,{'level':L0,'inflow':10,'outflow':6,'quality':0.86},[rm.normalize(P,B)]*50))
        g=y[:,1]-river
        print(f"{tag} L0 {L0}: L50 {y[-1,0]:.0f}  GW excess ticks 1-10/11-25/26-50: {g[:10].mean():.2f}/{g[10:25].mean():.2f}/{g[25:].mean():.2f}  out {y[0,2]:.1f}->{y[-1,2]:.1f}  q t1,5,10,50: {y[0,3]:.3f},{y[4,3]:.3f},{y[9,3]:.3f},{y[-1,3]:.3f}")
