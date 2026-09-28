"""Round-2 measurements for social_contagion (free). Run from KIT after analyze.py."""
import json, numpy as np
from scipy.optimize import curve_fit
HERE='fits/social_contagion/round2'; A=json.load(open(f'{HERE}/analysis.json')); sig=np.array(A['sigma'])
O={r:np.array(A['runs'][r]['obs']) for r in A['runs']}; P={r:np.array(A['runs'][r]['pred']) for r in A['runs']}
m10=lambda x,a,b: x[b-10:b].mean(0)
def expfit(y,t0):
    t=np.arange(len(y)); f=lambda t,c,d,k: c-d*np.exp(-k*t)
    try:
        p,_=curve_fit(f,t,y,p0=[y[-1],y[-1]-y[0],0.01],maxfev=20000); return p
    except Exception as e: return [np.nan]*3
print('H1 asymptote fit R4 250-399 (A,B):')
for j in range(2):
    for (a,b) in [(250,400),(150,400),(200,400)]:
        c,d,k=expfit(O['R4'][a:b,j],a); print(f'  obs{j} {a}-{b}: asym {c:.1f}  k {k:.4f}  (tau {1/k if k>0 else np.inf:.0f})  last10 {O["R4"][b-10:b,j].mean():.1f} slope_last50 {np.polyfit(np.arange(50),O["R4"][b-50:b,j],1)[0]:+.3f}/tick')
    print(f'  v1 last10 at 390-399: {P["R4"][390:400,j].mean():.1f}; v1 long-run 96.5/83.7')
print('H3 gains (R4): P2 400-459 after gap 300, P3 480-539 after gap 20')
for j in range(2):
    g2=O['R4'][450:460,j].mean()-O['R4'][395:400,j].mean(); g3=O['R4'][530:540,j].mean()-O['R4'][475:480,j].mean()
    print(f'  obs{j}: start {O["R4"][395:400,j].mean():.1f} / {O["R4"][475:480,j].mean():.1f}; end {O["R4"][450:460,j].mean():.1f} / {O["R4"][530:540,j].mean():.1f}; gain {g2:.1f} / {g3:.1f}; ratio {g3/g2:.3f}; end-level ratio {O["R4"][530:540,j].mean()/O["R4"][450:460,j].mean():.3f}')
    for lag in [10,20,30,40]:
        print(f'     +{lag}: P2 {O["R4"][400+lag,j]-O["R4"][399,j]:+.1f}  P3 {O["R4"][480+lag,j]-O["R4"][479,j]:+.1f}')
    pg2=P['R4'][450:460,j].mean()-P['R4'][395:400,j].mean(); pg3=P['R4'][530:540,j].mean()-P['R4'][475:480,j].mean(); print(f'  v1 gain ratio {pg3/pg2:.3f}')
print('H2 (R5):')
for j in range(2):
    o=O['R5'][:,j]; top=o[130:140].mean(); i1=o[180:190].mean(); i0=o[230:240].mean(); mn=o[190:240].min(); imn=190+o[190:240].argmin()
    print(f'  obs{j}: inc2 {top:.1f} inc1 {i1:.1f} inc0 last10 {i0:.1f} min {mn:.1f}@{imn}; drop ratio vs floor(43/31) {(top-i1)/(top-[43,31][j]):.2f}; vs own inc0 min {(top-i1)/(top-mn):.2f}; vs inc0 last10 {(top-i1)/(top-i0):.2f}')
print('H4 level map on the ray (last10): u.7 R4 0-99, u.85 R4 400-459, u1 R2 205-254, recovery tail R4 390-399')
for j in range(2):
    L0=O['R4'][390:400,j].mean(); L7=O['R4'][90:100,j].mean(); L85=O['R4'][450:460,j].mean(); L1=O['R2'][245:255,j].mean()
    print(f'  obs{j}: L0 {L0:.1f} L.7 {L7:.1f} L.85 {L85:.1f} L1 {L1:.1f}; frac(.7) {(L7-L0)/(L1-L0):.2f} frac(.85) {(L85-L0)/(L1-L0):.2f}; v1 frac(.7) {(P["R4"][90:100,j].mean()-P["R4"][390:400,j].mean())/(P["R2"][245:255,j].mean()-P["R4"][390:400,j].mean()):.2f}')
print('reset troughs / ratio:')
for r in ['R1','R2','R3','R4','R5']:
    o=O[r]; ini=np.array([A['runs'][r]['initial'][n] for n in A['names']]); i=o[:25].argmin(0)
    print(f'  {r}: init {ini.round(1)} trough {o[:25].min(0).round(1)} at {i} ratio {(o[:25].min(0)/ini).round(3)}; v1 trough {P[r][:25].min(0).round(1)}')
print('onset delays (first tick > start+3 sd):')
def onset(o,t0,sgn=1):
    base=o[t0-1]; 
    for t in range(t0,len(o)):
        if sgn*(o[t]-base)>1.5: return t-t0
for r,t0,s in [('R4',0,1),('R4',100,-1),('R4',400,1),('R4',460,-1),('R4',480,1),('R4',540,-1),('R5',0,1),('R5',80,1),('R5',140,-1),('R5',190,-1),('R5',240,-1)]:
    print(f'  {r} t{t0}: A {onset(O[r][:,0],max(t0,1),s)} B {onset(O[r][:,1],max(t0,1),s)}')
print('first-order rate of fall after switch-offs (log units, fit exp to first 25 ticks after 2-tick dead time):')
for r,t0,n in [('R4',100,40),('R4',460,20),('R4',540,20),('R5',140,40),('R5',190,15),('R2',255,40),('R1',355,40)]:
    for j in range(2):
        y=O[r][t0:t0+n,j]; c,d,k=expfit(y,0); print(f'  {r} t{t0} obs{j}: from {y[0]:.1f} to asym {c:.1f}, k {k:.3f}, min {y.min():.1f}@{t0+y.argmin()}')
print('rise rate k after switch-ons:')
for r,t0,n in [('R4',0,100),('R4',400,60),('R4',480,60),('R5',0,80),('R5',80,60)]:
    for j in range(2):
        y=O[r][t0+8:t0+n,j]; c,d,k=expfit(y,0); print(f'  {r} t{t0} obs{j}: asym {c:.1f} k {k:.3f} (tau {1/max(k,1e-6):.0f}), max slope {np.diff(O[r][t0:t0+n,j]).max():.2f}/tick at +{np.diff(O[r][t0:t0+n,j]).argmax()}')
print('noise: MAD of 2nd diff /0.6745/sqrt6 relative to level')
for r in ['R4','R5']:
    o=O[r]; d2=np.diff(np.log(o),2,axis=0); print(f'  {r}: rel noise {(np.median(np.abs(d2-np.median(d2,0)),0)/0.6745/np.sqrt(6)).round(4)}')
print('a/b ratio:')
for r,ts in [('R4',[99,149,249,399,459,479,539,559]),('R5',[79,139,189,239,319])]:
    print('  ',r,[f'{t}:{O[r][t,0]/O[r][t,1]:.2f}' for t in ts])
print('R5 incentive-0 undershoot/rebound and post-seeding bump:')
o=O['R5']; print('   A 190..320 every 10:', o[190:320:10,0].round(1)); print('   B', o[190:320:10,1].round(1))
print('   v1 A', P['R5'][190:320:10,0].round(1))
print('R4 recovery every 25:', O['R4'][100:400:25].round(1).tolist())
print('v1 R4 every 25:', P['R4'][100:400:25].round(1).tolist())
print('R4 0-100 every 10', O['R4'][0:100:10].round(1).tolist()); print('v1', P['R4'][0:100:10].round(1).tolist())
print('R5 0-140 every 10', O['R5'][0:140:10].round(1).tolist()); print('v1', P['R5'][0:140:10].round(1).tolist())
