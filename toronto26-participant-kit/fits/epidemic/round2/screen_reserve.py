"""Free screen of reserve schedules through the diagnostic variant fits (no steps)."""
from common import *
import importlib, itertools, sys
sig = sigma(); bounds = {'school_closure': (0, 1), 'mask_mandate': (0, 1), 'vaccination_rate': (0, 0.003)}
M = [('epi_varA', 'init_v1pe.json', 'v1'), ('epi_varA', 'fit_varA.json', 'A:eld+fatigue'), ('epi_varA', 'fit_varA12.json', 'A12:eld+m2'),
     ('epi_varB', 'fit_varB.json', 'B:nomaskfat')] + [tuple(x.split(':')) for x in sys.argv[1:]]
def A(c, m, v): return {'school_closure': c, 'mask_mandate': m, 'vaccination_rate': v}
S = {'S1 mask .85 x120, off x35': [(120, A(0, .85, 0)), (35, A(0, 0, 0))],
     'S2 mask .85 x80, +vacc .7 x40, all off x35': [(80, A(0, .85, 0)), (40, A(0, .85, .0021)), (35, A(0, 0, 0))],
     'S3 closure .7+mask .7 x120, off x35': [(120, A(.7, .7, 0)), (35, A(0, 0, 0))],
     'S4 vacc .7 x20 then +mask .85 x100, off x35': [(20, A(0, 0, .0021)), (100, A(0, .85, .0021)), (35, A(0, 0, 0))],
     'S5 rec x60, mask1 x30, gap10, mask1 x30, gap 25': [(60, A(0, 0, 0)), (30, A(0, 1, 0)), (10, A(0, 0, 0)), (30, A(0, 1, 0)), (25, A(0, 0, 0))]}
ini = {'daily_cases': 170.0, 'hospital_load': 45.0}
for name, sch in S.items():
    acts = sum([[a] * n for n, a in sch], []); preds = {}
    for mod, f, lab in M:
        V = importlib.import_module(mod); d = json.load(open('fits/epidemic/round2/' + f)); P = {k: v for k, (v, _) in V.SPEC.items()} | d.get('params', d)
        preds[lab] = V.simulate(P, ini, [V.normalize(x, bounds) for x in acts])
    dis = np.mean([np.mean(np.abs(preds[a] - preds[b]) / sig) for a, b in itertools.combinations(preds, 2)])
    ends = np.cumsum([n for n, _ in sch])
    print(f'{name:48s} steps {len(acts)}  mean pairwise dis {dis:.2f}σ')
    for e in ends:
        print('    end %3d: ' % e + ' | '.join(f'{k}:{preds[k][e-10:e,0].mean():.0f},{preds[k][e-10:e,1].mean():.0f}' for k in preds))
