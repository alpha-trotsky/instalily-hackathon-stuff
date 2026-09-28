import json, numpy as np, sys
sys.path.insert(0,'.')
from greybox.common.settle import exp_fit
NAMES = ['win_rate', 'spend', 'conversions']
def load(r):
    run = json.load(open(f'data/ad_auction/{r}.json'))['runs'][0]
    return np.array([[x[n] for n in NAMES] for x in run['observations']])
D = {r: load(r) for r in ['R1','R2c','R3','R4']}
def t63(y, y0, y1, log=False):
    if log: y, y0, y1 = np.log(np.maximum(y,1e-3)), np.log(y0), np.log(y1)
    f = (y - y0) / (y1 - y0)
    idx = np.nonzero(f >= 0.632)[0]
    return int(idx[0]) if len(idx) else None
cases = [('R3',250,350,'off u.7->rec'),('R3',350,400,'on rec->u1'),('R3',400,425,'off u1->rec'),('R3',425,500,'on rec->u.85'),
         ('R4',50,100,'bid 3.25->2'),('R4',100,150,'bid 2->.75'),('R4',150,200,'bid .75 cap100->rec'),('R4',200,250,'rec->bid5 cap50'),
         ('R2c',160,360,'rec->pulse'),('R2c',360,400,'pulse->rec')]
for r,s,e,lab in cases:
    o = D[r]; y0 = o[s-3:s,2].mean(); y1 = o[e-10:e,2].mean(); y = o[s:e,2]
    ext = y.max() if y1 > y0 else y.min()
    ef = exp_fit(o[s+5:e,1])
    print(f'{r} {lab:22s} conv {y0:.2f}->{y1:.2f} (extreme {ext:.2f}) t63 lin {t63(y,y0,y1)} log {t63(y,y0,y1,True)} | '
          f'spend jump {o[s-1,1]:.1f}->{o[s,1]:.1f} end {o[e-10:e,1].mean():.1f} tau {1/ef[2]:.1f} | win {o[s-3:s,0].mean():.3f}->{o[s:s+3,0].mean():.3f}->{o[e-10:e,0].mean():.3f}')
