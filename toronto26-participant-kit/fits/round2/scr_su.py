import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
import json
def lerp(R,P,u): return {k: R[k]+u*(P[k]-R[k]) for k in R}
R={'lead_time_buy':1.0,'maintenance':1.0,'order_quantity':0.0,'product_mix':0.5,'production_effort':1.0,'receiving_effort':1.5}
P={'lead_time_buy':0.2,'maintenance':0.0,'order_quantity':80.0,'product_mix':0.8,'production_effort':1.5,'receiving_effort':0.35}
def W(**k): d=dict(R); d.update(k); return d
sch={
 'SU-1 spacing':[dict(steps=50,action=lerp(R,P,.7),label='u.7 t0-49'),dict(steps=100,action=lerp(R,P,.7),label='u.7 t50-149'),dict(steps=60,action=R,label='rec 60'),
   dict(steps=60,action=P,label='u1'),dict(steps=30,action=R,label='rec 30'),dict(steps=100,action=lerp(R,P,.85),label='u.85')],
 'SU-2 receiving/maint':[dict(steps=50,action=W(order_quantity=80,receiving_effort=1.0),label='ord80 recv1.0'),dict(steps=50,action=W(order_quantity=80,receiving_effort=0.7),label='recv .7'),
   dict(steps=50,action=W(order_quantity=80,receiving_effort=0.5),label='recv .5'),dict(steps=50,action=W(order_quantity=80,receiving_effort=0.5,maintenance=0.3),label='+maint .3')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')],
 'u.85 3000':[dict(steps=3000,action=lerp(R,P,.85),label='u.85')]}
b='fits/supply_chain/v1/'
run('supply_chain','greybox/supply_chain_model.py',[b+'base_all2.json',b+'phi_all.json',b+'base_all.json'],sch,
    ['data/supply_chain/R1.json','data/supply_chain/R2.json','data/supply_chain/R3.json'])
