import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(p,r,c,i): return {'price_signal':p,'reserve_dispatch':r,'charging_allowance':c,'interconnector':i}
R=A(1.5,0,1,1)
sch={
 'PG-1 price ladder + reserve ladder':[dict(steps=80,action=A(2.0,0,1,1),label='price 2.0 (from reset)'),dict(steps=70,action=A(0.45,0,1,1),label='price 0.45'),
   dict(steps=70,action=A(1.5,0,1,1),label='price 1.5'),dict(steps=35,action=A(1.5,40,1,1),label='reserve 40'),dict(steps=35,action=A(1.5,80,1,1),label='reserve 80'),
   dict(steps=35,action=A(1.5,120,1,1),label='reserve 120'),dict(steps=35,action=A(1.5,80,1,0.5),label='reserve 80 + ic .5'),
   dict(steps=35,action=A(1.5,0,1,0.5),label='ic .5'),dict(steps=35,action=R,label='rec')],
 'PG-2 joint spacing':[dict(steps=100,action=A(0.45,105,0.3,0.44),label='joint .7 from reset'),dict(steps=60,action=R,label='rec 60'),
   dict(steps=60,action=A(0,150,0,0.2),label='joint 1'),dict(steps=30,action=R,label='rec 30'),
   dict(steps=100,action=A(0.225,127.5,0.15,0.32),label='joint .85'),dict(steps=50,action=R,label='rec')],
 'reserve 150 ch0 2000':[dict(steps=2000,action=A(1.5,150,0,1),label='r150 c0')],
 'price 0 2000':[dict(steps=2000,action=A(0,0,1,1),label='p0')]}
b='fits/power_grid/v1/'
run('power_grid','greybox/power_grid_model.py',[b+'m13_all.json',b+'m1_all.json',b+'m12_all.json',b+'m23_all.json'],sch,['data/power_grid/R1.json','data/power_grid/R2c.json'])
