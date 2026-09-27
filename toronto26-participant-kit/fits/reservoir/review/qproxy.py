# Quality score vs a noise-reduced target (9-tick MA of obs) for the R1-only and R1+R2 fits.
import json, sys, numpy as np, importlib.util
spec=importlib.util.spec_from_file_location('rm','greybox/reservoir_model.py'); rm=importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
sig=np.array([20.2,0.157,0.45,0.00102]); names=['level','inflow','outflow','quality']; k=np.ones(9)/9
for fit in sys.argv[1:]:
    p=json.load(open(fit))['params']
    for f in ['R1','R2']:
        d=json.load(open(f'data/reservoir/{f}.json')); r=d['runs'][0]
        u=[rm.normalize(a,d['brief']['interventions']) for a in r['actions']]
        obs=np.array([[o[n] for n in names] for o in r['observations']])
        pred=np.asarray(rm.simulate(p,r['initial'],u))
        sm=np.array([np.convolve(obs[:,i],k,'valid') for i in range(4)]).T; pr=pred[4:-4]
        raw=(1/(1+np.abs(pred-obs)/sig)).mean(0); prox=(1/(1+np.abs(pr-sm)/sig)).mean(0)
        print(f"{fit.split('/')[-1]:14s} {f} raw {np.round(raw,3)}  proxy(MA9) {np.round(prox,3)}  q|err|MA9 {np.abs(pr[:,3]-sm[:,3]).mean():.4f}")
