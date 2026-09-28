import sys; sys.path.insert(0,'fits/power_grid/round2')
from common import *
m=load_pred()
D={r:run(r) for r in ['R1','R2c','R3','R4']}
o3=D['R3'][1]; o4=D['R4'][1]
# H3: joint-1 hold ticks 160-359, drift over hold ticks 250-359 -> abs ticks 250..359 (hold-relative 90..199) and 410..519? hold is 200 ticks, so 'ticks 250-359' in run coords
for lab,(a,b) in {'run 250-359':(250,360),'run 200-359':(200,360)}.items():
    t=np.arange(a,b); L=o4[a:b,0]
    for i,n in enumerate(NAMES):
        y=o4[a:b,i]; X=np.c_[np.ones_like(t),t-a,L-125]
        c=np.linalg.lstsq(X,y,rcond=None)[0]
        print(f'H3 {lab} {n}: slope/tick {c[1]:.3g}, drift over window {c[1]*(b-a):.4g} = {c[1]*(b-a)/SIG[i]:.2f} score-sigma; load coef {c[2]:.3g}; first10 {y[:10].mean():.4f} last10 {y[-10:].mean():.4f}')
# share ladder: low state, chatter
a3=D['R3'][2]
for s0,s1,lab in [(200,230,'r40'),(230,260,'r80'),(260,290,'r120'),(290,320,'r80 x.5')]:
    S=o3[s0+5:s1,2]; L=o3[s0+5:s1,0]
    lo=np.percentile(S,25); hi=S>lo+0.03
    print(f'{lab}: share median {np.median(S):.4f} p25 {lo:.4f} mean {S.mean():.4f}; spikes(>p25+.03) {hi.sum()} of {len(S)} at ticks {list(np.where(hi)[0]+s0+5)}; S*L median {np.median(S*L):.2f}; f median {np.median(o3[s0+5:s1,1]):.3f} L median {np.median(L):.1f}')
# renewable power at other settings
for r,(s0,s1,lab) in [('R3',(350,380,'rec x1')),('R3',(320,350,'x.5 r0')),('R1',(300,350,'r150 x1')),('R4',(200,360,'joint1')),('R4',(40,100,'joint.7')),('R4',(420,470,'joint.85')),('R3',(40,70,'p2'))]:
    o=D[r][1]; S=o[s0:s1,2]; L=o[s0:s1,0]
    print(f'{r} {lab}: S {np.median(S):.4f} L {np.median(L):.1f} S*L {np.median(S*L):.2f} f {np.median(o[s0:s1,1]):.3f}')
# chatter periodicity at r40
S=o3[200:230,2]; print('r40 share series', np.round(S,3).tolist())
print('r40 freq series', np.round(o3[200:230,1],2).tolist())
print('r80 share series', np.round(o3[230:260,2],3).tolist())
# reset transients: first 25 ticks of R1 (p1.5), R3 (p2), R4 (joint .7), plus v1
for r in ['R1','R2c','R3','R4']:
    d,o,a,_=D[r]; p=predict(m,d)
    print(r,'init',{k:round(v,3) for k,v in d['initial'].items()})
    print('  load',np.round(o[:30:3,0],1).tolist(),' v1',np.round(p[:30:3,0],1).tolist())
    print('  freq',np.round(o[:30:3,1],2).tolist(),' v1',np.round(p[:30:3,1],2).tolist())
    print('  shr ',np.round(o[:30:3,2],3).tolist(),' v1',np.round(p[:30:3,2],3).tolist())
    i=np.argmin(o[:40,0]); print('  load min',o[i,0].round(1),'at',i,' v1 min',p[:40,0].min().round(1),'at',np.argmin(p[:40,0]))
