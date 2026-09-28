"""Zero-refit what-if tests with v1 params: which minimal structural switch removes which loss (free)."""
from common import *
import epi_variant as V
P = json.load(open('models/epidemic/params.json'))['params']
bounds = {'school_closure': (0, 1), 'mask_mandate': (0, 1), 'vaccination_rate': (0, 0.003)}
sig = sigma()
def sim(run, **kw):
    for k, v in kw.items(): setattr(V, k, v)
    u = [V.normalize(a, bounds) for a in run['actions']]
    return V.simulate(P, run['initial'], u)
CASES = {'v1 (reproduced)': dict(MASKFAT=True, PE=1.0, ALLPOP=1.0),
         'elderly priority x5': dict(MASKFAT=True, PE=5.0, ALLPOP=1.0),
         'elderly priority x30': dict(MASKFAT=True, PE=30.0, ALLPOP=1.0),
         'doses to S only': dict(MASKFAT=True, PE=1.0, ALLPOP=0.0),
         'no fatigue on masks': dict(MASKFAT=False, PE=1.0, ALLPOP=1.0),
         'no mask fatigue + eld x5': dict(MASKFAT=False, PE=5.0, ALLPOP=1.0)}
m = v1()
for name, kw in CASES.items():
    out = []
    for r in ['R1','R2','R3','R4','R5']:
        run, o, a = load_run(r); p = sim(run, **kw)
        out.append(f'{r}:' + '/'.join('%.3f' % x for x in (1/(1+np.abs(p-o)/sig)).mean(0)))
        if name.startswith('v1'): assert np.allclose(p, predict(m, run), rtol=1e-6), r
    print(f'{name:28s}', ' '.join(out))
