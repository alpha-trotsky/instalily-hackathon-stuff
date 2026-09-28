import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(s,i,b): return {'seeding':s,'incentive':i,'bridge_outreach':b}
R=A(0,0,0); P8=A(7.2,1.6,0.48)
sch={
 'SC-1 pulse0.8/long-rec/spacing':[dict(steps=120,action=P8,label='pulse u0.8 from reset'),dict(steps=50,action=R,label='rec: crash'),
   dict(steps=100,action=R,label='rec +150'),dict(steps=150,action=R,label='rec +300'),dict(steps=60,action=P8,label='pulse 2 (after long gap)'),
   dict(steps=20,action=R,label='short gap'),dict(steps=60,action=P8,label='pulse 3 (after 20 gap)'),dict(steps=40,action=R,label='rec')],
 'SC-2 ladder':[dict(steps=90,action=A(4.5,0,0),label='seeding 4.5'),dict(steps=70,action=A(4.5,2,0),label='+incentive 2 (bridge0)'),
   dict(steps=50,action=A(4.5,1,0),label='incentive 1 (partial drop)'),dict(steps=50,action=A(4.5,0,0),label='incentive 0'),dict(steps=70,action=R,label='seeding 0')],
 'long recovery 1500 from reset':[dict(steps=1500,action=R,label='rec')],
 'pulse u1 1500':[dict(steps=1500,action=A(9,2,0.6),label='pulse')],
 'incentive 1 hold 1000':[dict(steps=1000,action=A(0,1,0),label='inc 1')],
 'seeding 4.5 1000':[dict(steps=1000,action=A(4.5,0,0),label='seed 4.5')]}
b='fits/social_contagion/v1/'
run('social_contagion','greybox/social_contagion_model.py',[b+'m12_all.json',b+'m23_all.json',b+'m2_all.json'],sch,
    ['data/social_contagion/R1.json','data/social_contagion/R2.json','data/social_contagion/R3.json'])
