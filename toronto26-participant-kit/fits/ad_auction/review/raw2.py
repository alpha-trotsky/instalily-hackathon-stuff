import json, numpy as np
obs=['win_rate','spend','conversions']
def load(f):
    r=json.load(open('data/ad_auction/%s.json'%f))['runs'][0]
    A=np.array([[a['bid'],a['budget_cap'],a['targeting_breadth']] for a in r['actions']])
    O=np.array([[o[k] for k in obs] for o in r['observations']])
    I=np.array([r['initial'][k] for k in obs])
    return A,O,I
for f in ['R1','R2']:
    A,O,I=load(f)
    print(f,'initial',I, 'len',len(O))
    # noise: std of second difference/sqrt(6) in windows, vs level
    for j,k in enumerate(obs):
        x=O[:,j]; d2=x[2:]-2*x[1:-1]+x[:-2]
        s=np.sqrt(np.convolve(d2**2,np.ones(15)/15,'valid')/6)
        lv=x[8:8+len(s)]
        m=lv>1e-3
        print('  %s noise med %.4g  rel med %.4g  corr(log s,log lv)=%.2f'%(k,np.median(s),np.median(s[m]/lv[m]),np.corrcoef(np.log(s[m]+1e-9),np.log(lv[m]))[0,1]))
    print('  first 30 ticks:')
    for t in range(0,30,2): print('   ',t,np.round(O[t],3))
A1,O1,_=load('R1');A2,O2,_=load('R2')
print('reset transient compare t: R1 vs R2')
for t in [0,5,10,15,20,24]: print(t,np.round(O1[t],3),np.round(O2[t],3))
# conversions decay after bid=0 in R1 (405-435): fit exp
c=O1[405:435,2]; t=np.arange(len(c)); m=c>0.03
p=np.polyfit(t[m][:15],np.log(c[m][:15]),1); print('conv decay tau bid0', -1/p[0])
c=O1[480:510,2]; p=np.polyfit(np.arange(30)[3:20],np.log(c[3:20]-0.7),1); print('conv decay tau narrow (above .7)', -1/p[0])
# spend decay under pulses in R2
for a,b in [(25,65),(80,100),(160,360)]:
    s=O2[a:b,1]; base=s[-5:].mean() if b-a>100 else None
    print('spend pulse',a,b,np.round(s[:12],1), 'end',s[-3:].round(1))
# time since reset: compare recovery end levels
print('R1 recovery-end levels t~78,205,278,400,478,543:',[np.round(O1[t-3:t].mean(0),3) for t in [80,210,280,405,480,545]])
print('R2 end',np.round(O2[-3:].mean(0),3))
