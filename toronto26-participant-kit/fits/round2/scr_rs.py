import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(r,i,d,a): return {'release_rate':r,'irrigation_allocation':i,'withdrawal_depth':d,'aeration':a}
R=A(2,0,0,1)
sch={
 'RS-1 pulse .7 250 + rec 200':[dict(steps=100,action=A(9,5.6,0.7,0.3),label='pulse .7 t0-99'),dict(steps=150,action=A(9,5.6,0.7,0.3),label='pulse .7 t100-249'),
   dict(steps=50,action=R,label='rec +50'),dict(steps=150,action=R,label='rec +200')],
 'RS-2 release 10.5 & aeration ladder':[dict(steps=150,action=A(10.5,0,0,1),label='release 10.5'),dict(steps=80,action=A(2,0,0,0.3),label='aer .3'),
   dict(steps=80,action=A(2,0,0.5,0.15),label='aer .15 depth .5'),dict(steps=80,action=A(2,0,0.5,0),label='aer 0 depth .5'),dict(steps=60,action=R,label='rec')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')]}
run('reservoir','greybox/reservoir_model.py',['fits/reservoir/v1/final.json','fits/reservoir/v1/m13_all.json','fits/reservoir/v1/m12_all.json'],sch,['data/reservoir/R1.json','data/reservoir/R2.json','data/reservoir/R3.json'])
