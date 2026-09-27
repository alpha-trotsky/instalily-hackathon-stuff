import json, sys, itertools, numpy as np
sys.path.insert(0,'greybox'); import epidemic_model as M
def params(fit):
    p={k:v[0] for k,v in M.SPEC.items()}
    for m,(names,off) in M.MODULES.items():
        if m not in fit['modules']: p.update(off)
    p.update(fit['params']); return p
ini={'daily_cases':200,'hospital_load':55}
SIG=np.array([8.344,4.189])
names=['m12_r1','m13_r1','m23_r1','m12_all_quick','m13_all_quick','m23_all_quick']
P={fn:params(json.load(open(f'fits/epidemic/{fn}.json'))) for fn in names}
R0,J,MK,CL,V,ALL=(0,0,0),(1,1,0),(0,1,0),(1,0,0),(0,0,1),(1,1,1)
C={'rec 55 (control)':[R0]*55,'all3 55':[ALL]*55,'all3 0.85 55':[(.85,.85,.85)]*55,'mask 55':[MK]*55,'vacc 55':[V]*55,
   'all3 30|rec 25':[ALL]*30+[R0]*25,'closure 55':[CL]*55}
for n,c in C.items():
    out={k:M.simulate(p,ini,c) for k,p in P.items()}
    d=[np.mean(np.abs(out[a]-out[b])/SIG) for a,b in itertools.combinations(P,2)]
    print('%-18s mean pairwise %.2f | peak cases by fit: %s | end hosp: %s'%(n,np.mean(d),' '.join('%.0f'%out[k][:,0].max() for k in names),' '.join('%.0f'%out[k][-1,1] for k in names)))
