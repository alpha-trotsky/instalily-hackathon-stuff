"""Counterfactual holds and R4/R6 traces for a fit: python fits/social_contagion/round3/cf.py FIT.json"""
import json,sys,os,numpy as np
sys.path.insert(0,os.getcwd())
from greybox.common import core
fj=json.load(open(sys.argv[1])); m=core.load_model(fj['model']); p=fj['params']
B={'seeding':(0,10),'incentive':(0,2),'bridge_outreach':(0,1)}
ini={'adopters_a':45,'adopters_b':40}
def run(sched,ini=ini):
    u=[]
    for n,(s,i,b) in sched: u+= [m.normalize({'seeding':s,'incentive':i,'bridge_outreach':b},B)]*n
    return m.simulate(p,ini,u)
for lab,sch in [('u7',[(300,(6.3,1.4,.42))]),('noinc',[(300,(6.3,0,.42))]),('R6',[(60,(6.3,0,.42)),(240,(6.3,1.4,.42))]),('s45',[(80,(4.5,0,0)),(220,(4.5,2,0))])]:
    y=run(sch); print(lab,' '.join(f'{t}:{y[t,0]:.0f}/{y[t,1]:.0f}' for t in [30,60,90,120,200,299]))
for lab,sch in [('rec',[(4000,(0,0,0))]),('u7',[(4000,(6.3,1.4,.42))]),('R6',[(60,(6.3,0,.42)),(3940,(6.3,1.4,.42))]),('u1',[(4000,(9,2,.6))]),('s45i2',[(4000,(4.5,2,0))])]:
    y=run(sch); print(lab,' '.join(f'{t}:{y[t,0]:.0f}/{y[t,1]:.0f}' for t in [300,1000,2000,3999]), f'min {y[100:].min(0).round(0)} max {y[100:].max(0).round(0)}')
for f in ['R4','R6']:
    r=json.load(open(f'data/social_contagion/{f}.json'))['runs'][0]
    o=np.array([[x['adopters_a'],x['adopters_b']] for x in r['observations']])
    y=m.simulate(p,r['initial'],[m.normalize(a,B) for a in r['actions']])
    print(f,' '.join(f'{t}:{y[t,0]:.0f}/{y[t,1]:.0f}({o[t,0]:.0f}/{o[t,1]:.0f})' for t in range(0,120,10)))
