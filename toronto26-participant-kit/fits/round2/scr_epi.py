import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(c,m,v): return {'school_closure':c,'mask_mandate':m,'vaccination_rate':v}
R=A(0,0,0); P85=A(0.85,0.85,0.00255)
sch={
 'EP-1 all 0.85 from reset 300, rec 150':[dict(steps=40,action=P85,label='all .85: first wave'),dict(steps=60,action=P85,label='t40-99'),
   dict(steps=100,action=P85,label='t100-199'),dict(steps=100,action=P85,label='t200-299'),dict(steps=40,action=R,label='release'),dict(steps=110,action=R,label='rec +150')],
 'EP-2 vacc from reset 250, off 150':[dict(steps=40,action=A(0,0,0.003),label='vacc: first wave'),dict(steps=110,action=A(0,0,0.003),label='t40-149'),
   dict(steps=100,action=A(0,0,0.003),label='t150-249'),dict(steps=30,action=R,label='off +30'),dict(steps=120,action=R,label='off +150')],
 'EP-3 mask .7 from reset 250':[dict(steps=40,action=A(0,0.7,0),label='first wave'),dict(steps=110,action=A(0,0.7,0),label='t40-149'),dict(steps=100,action=A(0,0.7,0),label='t150-249')],
 'EP-3b closure 1 from reset 250':[dict(steps=40,action=A(1,0,0),label='first wave'),dict(steps=110,action=A(1,0,0),label='t40-149'),dict(steps=100,action=A(1,0,0),label='t150-249')],
 'long rec 3000':[dict(steps=600,action=R,label='rec to 600'),dict(steps=2400,action=R,label='rec to 3000')]}
b='fits/epidemic/v2/'
run('epidemic','greybox/epidemic_model.py',[b+'m13_all.json',b+'m12_all.json',b+'base_all.json',b+'m23_all.json'],sch,['data/epidemic/R1.json','data/epidemic/R2.json'])
