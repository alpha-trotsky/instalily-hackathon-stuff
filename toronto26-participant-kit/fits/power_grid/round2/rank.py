"""Score loss vs perfect forecast per (segment, observable), with level/dynamics/transient split. All runs."""
import sys, json; sys.path.insert(0,'fits/power_grid/round2')
from common import *
m=load_pred(); out=[]
def lab(ac):
    pr,rd,ch,x=ac; return f'p{pr:g} r{rd:g} c{ch:g} x{x:g}'
for r in ['R1','R2c','R3','R4']:
    d,o,a,_=run(r); p=predict(m,d); e=p-o
    ch=np.where(np.r_[True,np.any(a[1:]!=a[:-1],1)])[0].tolist()+[len(o)]
    tot=(1-1/(1+np.abs(e)/SIG)).sum(0)
    print(f'{r}: total loss (tick-units) load {tot[0]:.0f} freq {tot[1]:.0f} share {tot[2]:.0f} of {len(o)} ticks each; score {(1-tot/len(o)).round(3)}')
    for s0,s1 in zip(ch[:-1],ch[1:]):
        for i,n in enumerate(NAMES):
            ee=e[s0:s1,i]; loss=(1-1/(1+np.abs(ee)/SIG[i])).sum()
            tail=ee[min(15,(s1-s0)//2):]; off=np.median(tail)
            lvl=(1-1/(1+abs(off)/SIG[i]))*(s1-s0)          # loss a pure constant offset would give
            tr=(1-1/(1+np.abs(ee[:15])/SIG[i])).sum()
            resid=ee-off; dyn=(1-1/(1+np.abs(resid[min(15,(s1-s0)//2):])/SIG[i])).sum()
            kind='level' if lvl>=0.6*loss else ('transient' if tr>=0.5*loss else 'dynamics')
            out.append(dict(run=r,t0=int(s0),t1=int(s1),seg=lab(a[s0]),obs=n,loss=round(float(loss),1),per_tick=round(float(loss/(s1-s0)),2),
                            offset_sig=round(float(off/SIG[i]),1),loss_if_offset_only=round(float(lvl),1),loss_first15=round(float(tr),1),kind=kind))
json.dump(out,open('fits/power_grid/round2/loss_rank.json','w'),indent=0)
new=[x for x in out if x['run'] in ('R3','R4')]; old=[x for x in out if x['run'] in ('R1','R2c')]
for title,L in [('NEW (R3,R4)',new),('OLD (R1,R2c)',old)]:
    print('==',title,'top 20')
    for x in sorted(L,key=lambda z:-z['loss'])[:20]:
        print(f"{x['run']:3s} [{x['t0']:3d}-{x['t1']-1:3d}] {x['seg']:28s} {x['obs']:15s} loss {x['loss']:6.1f} ({x['per_tick']:.2f}/tick) offset {x['offset_sig']:+5.1f}σ off-only {x['loss_if_offset_only']:5.1f} first15 {x['loss_first15']:4.1f} -> {x['kind']}")
    for k in ['level','dynamics','transient']:
        print('  ',k, round(sum(x['loss'] for x in L if x['kind']==k),0))
    for n in NAMES: print('  ',n, round(sum(x['loss'] for x in L if x['obs']==n),0))
