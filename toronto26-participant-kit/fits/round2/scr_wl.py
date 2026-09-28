import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(h,p,c): return {'hunting_quota':h,'habitat_protection':p,'corridor_access':c}
R=A(0,1,0)
sch={
 'WL-1 spacing':[dict(steps=80,action=A(5.95,0.235,0.85),label='joint .85 from reset'),dict(steps=30,action=R,label='release +30'),
   dict(steps=90,action=R,label='release +120'),dict(steps=60,action=A(7,0.1,1),label='joint 1.0'),dict(steps=30,action=R,label='short gap 30'),
   dict(steps=60,action=A(4.9,0.37,0.7),label='joint .7'),dict(steps=30,action=R,label='release +30'),dict(steps=120,action=R,label='release +150')],
 'WL-2 ladder':[dict(steps=80,action=A(5,1,0),label='hunt 5'),dict(steps=60,action=A(5,0.37,0),label='hunt5+hab.37'),
   dict(steps=60,action=A(0,0.37,0),label='hab .37'),dict(steps=60,action=A(0,0.37,0.7),label='hab.37+corr.7'),
   dict(steps=60,action=A(0,1,0.7),label='corr .7'),dict(steps=30,action=R,label='rec')],
 'holds 2000':[dict(steps=2000,action=R,label='rec')],
 'joint1 2000':[dict(steps=2000,action=A(7,0.1,1),label='joint 1')],
 'joint.7 2000':[dict(steps=2000,action=A(4.9,0.37,0.7),label='joint .7')]}
b='fits/wildlife/v1/'
run('wildlife','greybox/wildlife_model.py',[b+'AB_all3.json',b+'AC_all.json',b+'BC_all2.json',b+'base_all.json'],sch,['data/wildlife/R1.json','data/wildlife/R2c.json'])
