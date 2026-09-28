"""Rank (segment, observable) score loss of v1 vs a perfect forecast; classify level/dynamics/transient. Free."""
import json, numpy as np
A=json.load(open('fits/social_contagion/round2/analysis.json')); sig=np.array(A['sigma']); names=A['names']
rows=[]
for r,d in A['runs'].items():
    o=np.array(d['obs']); p=np.array(d['pred']); e=(p-o)/sig; loss=1-1/(1+np.abs(e))
    for x in d['rows']:
        a,b=x['seg']; j=names.index(x['obs']); ls=loss[a:b,j]; ee=e[a:b,j]
        n=b-a; head=min(20,n//3) if n>=30 else n
        frac_head=ls[:head].sum()/max(ls.sum(),1e-9)
        signfrac=abs(ee.mean())/max(np.abs(ee).mean(),1e-9)
        tail_err=ee[-10:].mean()
        if n>=30 and frac_head>0.5: cls='transient'
        elif signfrac>=0.8 and abs(tail_err)>=0.5: cls='level'
        else: cls='dynamics'
        rows.append((ls.sum(),r,a,b,x['obs'][-1].upper(),x['act'],ee.mean(),tail_err,signfrac,frac_head,cls))
rows.sort(key=lambda z:-z[0])
tot={r:sum(z[0] for z in rows if z[1]==r) for r in A['runs']}
print('total lost (tick-units) per run:',{k:round(v,1) for k,v in tot.items()})
print('rank | run | ticks | obs | action s/i/b | lost | mean err σ | last10 err σ | |mean|/mae | head share | class')
for i,z in enumerate(rows[:40]):
    a=z[5]; print(f"{i+1:2d} | {z[1]} | {z[2]}-{z[3]-1} | {z[4]} | {a['seeding']:.2f}/{a['incentive']:.1f}/{a['bridge_outreach']:.2f} | {z[0]:.1f} | {z[6]:+.2f} | {z[7]:+.2f} | {z[8]:.2f} | {z[9]:.2f} | {z[10]}")
