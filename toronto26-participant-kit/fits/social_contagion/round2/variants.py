"""Score v1 and simple variants (existing fits, one-parameter ablations; no refits) on R1-R5. Free."""
import json, sys, numpy as np
sys.path.insert(0,'greybox'); import social_contagion_model as M
A=json.load(open('fits/social_contagion/round2/analysis.json')); sig=np.array(A['sigma']); names=A['names']
bounds={'seeding':(0,10),'incentive':(0,2),'bridge_outreach':(0,1)}
def run(p,r):
    d=json.load(open(f'data/social_contagion/{r}.json'))['runs'][0]
    acts=[M.normalize(a,bounds) for a in d['actions']]
    return M.simulate(p,d['initial'],acts), np.array([[o[n] for n in names] for o in d['observations']])
P={}
for k,f in [('v1_m12','fits/social_contagion/v1/final.json'),('m23_all','fits/social_contagion/v1/m23_all.json'),('m2_all','fits/social_contagion/v1/m2_all.json')]:
    P[k]=json.load(open(f))['params']
P['v1_g1=0']=dict(P['v1_m12'],g1=0.0)
P['v1_gret=0.5']=dict(P['v1_m12'],gret=0.5)
res={}
for k,p in P.items():
    row=[]
    for r in ['R1','R2','R3','R4','R5']:
        pr,o=run(p,r); s=(1/(1+np.abs(pr-o)/sig)).mean(0); row.append(s.mean())
        if r=='R4': e4=[pr[20,0],pr[90:100].mean(0).round(1).tolist(),pr[130:140].mean(0).round(1).tolist(),pr[390:400].mean(0).round(1).tolist()]
        if r=='R5': e5=[pr[20,0],pr[130:140].mean(0).round(1).tolist(),pr[180:190].mean(0).round(1).tolist(),pr[310:320].mean(0).round(1).tolist()]
    print(f'{k:12s} R1..R5 {np.round(row,3)} | R4 A@20 {e4[0]:.0f} u.7 {e4[1]} crash {e4[2]} tail {e4[3]} | R5 A@20 {e5[0]:.0f} inc2 {e5[1]} inc1 {e5[2]} tail {e5[3]}')
print('data: R4 A@20 94 u.7 [164.1,100.9] crash[~66,51] tail [89,73.2] | R5 A@20 89 inc2 [257,146] inc1 [143,75] tail [99.5,67.8]')
