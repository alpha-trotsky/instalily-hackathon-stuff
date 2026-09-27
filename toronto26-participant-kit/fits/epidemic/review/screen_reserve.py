import json, sys, itertools, numpy as np
sys.path.insert(0,'greybox'); import epidemic_model as M
def params(fit):
    p={k:v[0] for k,v in M.SPEC.items()}
    for m,(names,off) in M.MODULES.items():
        if m not in fit['modules']: p.update(off)
    p.update(fit['params']); return p
r=json.load(open('data/epidemic/R2.json'))['runs'][0]; ini=r['initial']; acts=[M.normalize(a,{}) for a in r['actions']]
SIG=np.array([8.344,4.189])
P={fn:params(json.load(open(f'fits/epidemic/{fn}.json'))) for fn in ['m12_all_quick','m13_all_quick','m23_all_quick']}
R0,J,MK,CL,V,ALL=(0,0,0),(1,1,0),(0,1,0),(1,0,0),(0,0,1),(1,1,1)
C={'A all3 25|rec 30':[ALL]*25+[R0]*30,'B mask20|rec10|mask20|rec5':[MK]*20+[R0]*10+[MK]*20+[R0]*5,
   'C vacc 55':[V]*55,'D rec 55':[R0]*55,'E joint 25|rec 30':[J]*25+[R0]*30,
   'F vacc25|joint30 (P9b before, low hosp)':[V]*25+[J]*30,'G joint25|vacc30 (P9b after)':[J]*25+[V]*30,
   'H vacc+mask 25|rec30':[(0,1,1)]*25+[R0]*30,'I closure+vacc 25|rec 30':[(1,0,1)]*25+[R0]*30}
for n,c in C.items():
    out={k:M.simulate(p,ini,acts+c)[400:] for k,p in P.items()}
    d=[np.mean(np.abs(out[a]-out[b])/SIG) for a,b in itertools.combinations(P,2)]
    print('%-42s pairs(12/13,12/23,13/23) %s mean %.2f   m13 end cases %.0f hosp %.0f'%(n,' '.join('%.2f'%x for x in d),np.mean(d),out['m13_all_quick'][-1,0],out['m13_all_quick'][-1,1]))
