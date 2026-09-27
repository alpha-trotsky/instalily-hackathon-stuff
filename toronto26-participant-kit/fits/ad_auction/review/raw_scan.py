import json, numpy as np
obs=['win_rate','spend','conversions']
for f in ['R1','R2']:
    r=json.load(open('data/ad_auction/%s.json'%f))['runs'][0]
    A=r['actions']; O=np.array([[o[k] for k in obs] for o in r['observations']])
    segs=[];s=0
    for t in range(1,len(A)+1):
        if t==len(A) or A[t]!=A[s]: segs.append((s,t));s=t
    print('=====',f)
    for a,b in segs:
        ac=A[a]; seg=O[a:b]
        print('%4d-%4d bid%.1f cap%5.1f br%.3f'%(a,b,ac['bid'],ac['budget_cap'],ac['targeting_breadth']))
        for j,k in enumerate(obs):
            x=seg[:,j]
            print('   %-11s first3 %8.4f  t5 %8.4f t15 %8.4f  last5 %8.4f  min %8.4f max %8.4f'%(k,x[:3].mean(),x[min(5,len(x)-1)],x[min(15,len(x)-1)],x[-5:].mean(),x.min(),x.max()))
        wr,sp,cv=seg[-5:].mean(0)
        print('   spend/win %.2f  conv/spend %.3f conv/win %.2f'%(sp/max(wr,1e-3),cv/max(sp,1e-3),cv/max(wr,1e-3)))
