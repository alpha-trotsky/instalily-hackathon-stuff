from common import *
from cands import cand
m=v1()
for r in ['R1','R2','R4','R5','R3']:
    run,o,a=load_run(r); p=predict(m,run); q=cand('m12_all',run)
    print(r, 'cum cases 0-59 data %.0f v1 %.0f m12 %.0f'%(o[:60,0].sum(),p[:60,0].sum(),q[:60,0].sum()), ' ticks>50%%pk data %d v1 %d m12 %d'%((o[:60,0]>o[:60,0].max()/2).sum(),(p[:60,0]>p[:60,0].max()/2).sum(),(q[:60,0]>q[:60,0].max()/2).sum()))
