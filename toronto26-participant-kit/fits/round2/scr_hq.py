import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(s,e,d,u,o,f): return {'staffing':s,'elective_scheduling':e,'diagnostic_allocation':d,'urgent_priority':u,'overtime':o,'followup_capacity':f}
R=A(20,0,0.4,0.6,0,1); P7=A(9.5,14,0.645,0.88,0.7,0.3); P1=A(5,20,0.75,1,1,0)
sch={
 'HQ-1 elective/staffing ladder':[dict(steps=60,action=A(20,5,0.4,0.6,0,1),label='elective 5 from reset'),dict(steps=60,action=A(20,10,0.4,0.6,0,1),label='elective 10'),
   dict(steps=60,action=A(15,10,0.4,0.6,0,1),label='staff 15 + el 10'),dict(steps=60,action=A(15,0,0.4,0.6,0,1),label='staff 15 alone'),dict(steps=60,action=R,label='rec')],
 'HQ-2 joint spacing':[dict(steps=100,action=P7,label='joint .7 from reset'),dict(steps=60,action=R,label='rec 60'),dict(steps=60,action=P1,label='joint 1'),
   dict(steps=90,action=R,label='rec +90'),dict(steps=90,action=R,label='rec +180')],
 'elective 20 hold 1500 then rec 1500':[dict(steps=1500,action=A(20,20,0.4,0.6,0,1),label='E hold'),dict(steps=1500,action=R,label='rec after')],
 'staff 12 hold 2000':[dict(steps=2000,action=A(12,0,0.4,0.6,0,1),label='staff 12')]}
run('hospital_queue','greybox/hospital_queue_model.py',['fits/hospital_queue/final_m12.json','fits/hospital_queue/v5_base_all.json'],sch,['data/hospital_queue/R1.json','data/hospital_queue/R2c.json'])
