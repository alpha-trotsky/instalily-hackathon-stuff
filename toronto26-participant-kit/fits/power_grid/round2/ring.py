import sys; sys.path.insert(0,'fits/power_grid/round2')
from common import *
from scipy.signal import find_peaks, savgol_filter
m=load_pred()
def ext(y,t0):
    ys=savgol_filter(y,9,2)
    pk,_=find_peaks(ys,prominence=3); tr,_=find_peaks(-ys,prominence=3)
    ev=sorted([(i+t0,'P',round(y[i],1)) for i in pk]+[(i+t0,'T',round(y[i],1)) for i in tr]); return ev
for r,s0,s1,lab in [('R3',0,70,'reset->p2'),('R1',0,120,'reset->p1.5'),('R3',70,140,'p.45'),('R3',140,230,'p1.5 after .45'),('R1',120,210,'p0'),('R1',210,350,'p1.5 after 0'),('R4',160,360,'joint1'),('R4',390,470,'joint.85'),('R4',360,390,'rec30'),('R4',100,160,'rec60'),('R4',470,510,'rec40'),('R4',0,100,'joint.7 reset')]:
    d,o,a,_=run(r); p=predict(m,d)
    print(f'{r} {lab:16s} data', ext(o[s0:s1,0],s0)); print(f'{"":20s} v1  ', ext(p[s0:s1,0],s0))
# price-2 level: R3 (p2) minus R1 (p1.5), same reset
o1=run('R1')[1]; o3=run('R3')[1]
for a,b in [(0,15),(15,30),(30,50),(50,70)]:
    print('R3-R1 load ticks',a,b, (o3[a:b,0]-o1[a:b,0]).mean().round(2), ' freq', (o3[a:b,1]-o1[a:b,1]).mean().round(3),' share',(o3[a:b,2]-o1[a:b,2]).mean().round(4))
print('R1 mean load 20-120', o1[20:120,0].mean().round(1), ' R3 recovery 350-380', o3[350:380,0].mean().round(1))
