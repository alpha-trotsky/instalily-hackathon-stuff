"""Per-segment last-10 levels and scores for a fit JSON: python3 fits/power_grid/round2/v2_seg.py FIT [RUN ...]"""
import sys,json; sys.path.insert(0,'.')
exec(open('fits/power_grid/round2/v2_fit.py').read().split("if __name__")[0])
r=json.load(open(sys.argv[1])); m=core.load_model(r['model']); p=r['params']
print({k:round(v,4) for k,v in p.items()})
for run in sys.argv[2:] or ['R3','R4']:
    ep=eps([run],m)[0]; pr=core.rollout(m,p,ep); o=ep['obs']; a=np.array([[x[c] for c in ['price_signal','reserve_dispatch','charging_allowance','interconnector']] for x in ep['actions']])
    sw=[0]+[i for i in range(1,len(a)) if (a[i]!=a[i-1]).any()]+[len(a)]
    for s,e in zip(sw[:-1],sw[1:]):
        sl=slice(s,e); sc=(1/(1+np.abs(pr[sl]-o[sl])/SIG)).mean(0)
        print(run,s,e,a[s],'obs',np.round(o[e-10:e].mean(0),3),'pred',np.round(pr[e-10:e].mean(0),3),'score',np.round(sc,2))
