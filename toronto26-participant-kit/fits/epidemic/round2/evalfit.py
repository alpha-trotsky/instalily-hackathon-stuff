from common import *
import importlib, sys
sig = sigma(); bounds = {'school_closure': (0, 1), 'mask_mandate': (0, 1), 'vaccination_rate': (0, 0.003)}
for mod, fitf in [(a.split(':')[0], a.split(':')[1]) for a in sys.argv[1:]]:
    V = importlib.import_module(mod); d = json.load(open('fits/epidemic/round2/' + fitf)); P = d.get('params', d)
    P = {k: v for k, v in P.items()}; full = {k: v for k, (v, _) in V.SPEC.items()} | P
    tot = []; out = []
    for r in ['R1','R2','R3','R4','R5']:
        run, o, a = load_run(r); p = V.simulate(full, run['initial'], [V.normalize(x, bounds) for x in run['actions']])
        sc = (1/(1+np.abs(p-o)/sig)).mean(0); tot.append(sc.mean()); out.append(f'{r}:{sc[0]:.3f}/{sc[1]:.3f}')
    print(fitf, 'old %.3f new %.3f' % (np.mean(tot[:2]), np.mean(tot[2:])), ' '.join(out), ' pe=%.2f gF=%.3f a_m1=%.3f mix=%.2f' % (full['pe'], full['gF_m1'], full['a_m1'], full['mix_m1']))
