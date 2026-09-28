import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
def A(r,t): return {'interest_rate':r,'transaction_tax':t}
R=A(0,0)
sch={
 'MK-1 joint spacing':[dict(steps=150,action=A(0.1,0.05),label='joint 1 from reset'),dict(steps=150,action=R,label='rec 150'),
   dict(steps=125,action=A(0.07,0.035),label='joint .7'),dict(steps=50,action=R,label='short gap 50'),dict(steps=125,action=A(0.1,0.05),label='joint 1 again')],
 'MK-2 order/mid':[dict(steps=125,action=A(0.05,0),label='rate .05'),dict(steps=125,action=A(0.05,0.05),label='+tax .05'),
   dict(steps=125,action=A(0,0.05),label='tax only'),dict(steps=125,action=A(0,0.025),label='tax .025'),dict(steps=100,action=R,label='rec')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')],
 'joint 3000':[dict(steps=3000,action=A(0.1,0.05),label='joint')]}
b='fits/market/'
run('market','greybox/market_model.py',[b+'m12_withdraw_train600.json',b+'m13_withdraw_train600.json',b+'m23_withdraw_train600.json'],sch,['data/market/A.json'])
