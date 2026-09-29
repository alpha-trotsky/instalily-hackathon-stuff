import json, sys, numpy as np
sys.argv += []
sys.path.insert(0,'fits/reservoir/round3'); import score3
m = score3.load(sys.argv[1]); p = json.load(open(sys.argv[2]))['params']
for r in sys.argv[3:]:
    d = json.load(open(f'data/reservoir/{r}.json'))['runs'][0]
    u = [m.normalize(a, score3.BOUNDS) for a in d['actions']]
    tr = []; out = m.simulate(p, d['initial'], u, trace=tr)
    o = np.array([x['quality'] for x in d['observations']])
    print(r)
    for t in range(0, len(u), int(sys.argv[-1]) if False else 5):
        Tq,z,Dm,Cm,D,V,uae = tr[t]
        print(f' t{t:4d} u={np.round(u[t],2).tolist()} q {out[t][3]:.4f} obs10 {o[t:t+5].mean():.4f} Tq {Tq:.4f} z {z:.3f} Dm {Dm:.3f} Cm {Cm:.3f} D {D:.1f} V {V:.0f}')
