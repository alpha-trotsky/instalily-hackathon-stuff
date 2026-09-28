import sys; sys.path.insert(0,'fits/power_grid/round2')
from common import *
m=load_pred(); ini={'load':105.,'frequency':50.,'renewable_share':.35}
def const(p,r,c,x,T=400):
    A=[dict(price_signal=p,reserve_dispatch=r,charging_allowance=c,interconnector=x)]*T
    q=np.array([[z[n] for n in NAMES] for z in m.predict(ini,A,CTX)]); return q[-50:].mean(0)
print('v1 steady state (last 50 of 400):  load  f  share')
for lab,a in [('rec',(1.5,0,1,1)),('p2',(2,0,1,1)),('p.45',(.45,0,1,1)),('p0',(0,0,1,1)),('r40',(1.5,40,1,1)),('r80',(1.5,80,1,1)),('r120',(1.5,120,1,1)),('r150',(1.5,150,1,1)),('r80x.5',(1.5,80,1,.5)),('x.5',(1.5,0,1,.5)),('x.2',(1.5,0,1,.2)),('x0',(1.5,0,1,0)),('j.7',(.45,105,.3,.44)),('j.85',(.225,127.5,.15,.32)),('j1',(0,150,0,.2))]:
    print(f'{lab:8s}', np.round(const(*a),3))
# data load/freq in quiet windows
for r,s0,s1,lab in [('R2c',420,450,'r150 p1.5 ch0'),('R2c',380,400,'r150 p1.5 ch1'),('R1',300,350,'r150'),('R1',470,500,'rec'),('R3',235,290,'r80/120'),('R3',300,320,'r80 x.5'),('R3',330,350,'x.5'),('R3',360,380,'rec'),('R4',260,360,'joint1'),('R1',180,210,'p0 alone'),('R4',130,160,'rec')]:
    o=D=run(r)[1]; print(r,lab,'L',o[s0:s1,0].mean().round(1),'f',o[s0:s1,1].mean().round(3),'S',o[s0:s1,2].mean().round(4))
