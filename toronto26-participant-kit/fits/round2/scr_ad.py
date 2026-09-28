import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
import json
def lerp(R,P,u): return {k: R[k]+u*(P[k]-R[k]) for k in R}
R={'bid':1.5,'budget_cap':20.0,'targeting_breadth':0.55}; P={'bid':5.0,'budget_cap':100.0,'targeting_breadth':0.775}
def A(b,c,t): return {'bid':b,'budget_cap':c,'targeting_breadth':t}
sch={
 'AD-1 spacing':[dict(steps=50,action=lerp(R,P,.7),label='u.7 t0-49'),dict(steps=200,action=lerp(R,P,.7),label='u.7 t50-249'),
   dict(steps=100,action=R,label='rec 100'),dict(steps=50,action=P,label='u1'),dict(steps=25,action=R,label='rec 25'),dict(steps=75,action=lerp(R,P,.85),label='u.85')],
 'AD-2 ladders':[dict(steps=50,action=A(3.25,100,.55),label='bid 3.25 cap100'),dict(steps=50,action=A(2.0,100,.55),label='bid 2 cap100'),
   dict(steps=50,action=A(0.75,100,.55),label='bid .75 cap100'),dict(steps=50,action=R,label='rec'),dict(steps=50,action=A(5,50,.55),label='bid5 cap50'),dict(steps=50,action=A(5,30,.55),label='bid5 cap30')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')],
 'u.85 3000':[dict(steps=3000,action=lerp(R,P,.85),label='u.85')]}
b='fits/ad_auction/'
run('ad_auction','greybox/ad_auction_model.py',[b+'final.json',b+'v1/m12_all.json',b+'v1/m13_all.json',b+'v1/base_all.json'],sch,
    ['data/ad_auction/R1.json','data/ad_auction/R2c.json'])
