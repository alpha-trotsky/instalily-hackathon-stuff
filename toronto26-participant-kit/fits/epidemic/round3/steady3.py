"""Free (round 3, ev3 data): long-run levels (4,000 ticks from reset at initial 150/45) at fixed settings, for fit JSONs."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ev3 import *
ap = argparse.ArgumentParser(); ap.add_argument('--model', default='greybox/epidemic_model_v2.py'); ap.add_argument('fits', nargs='+')
a = ap.parse_args(); M = load_model(a.model)
SET = [('recovery', 0, 0, 0), ('mask .7', 0, .7, 0), ('closure .7', .7, 0, 0), ('vacc .7', 0, 0, .0021), ('all .7', .7, .7, .0021),
       ('mask 1', 0, 1, 0), ('closure 1', 1, 0, 0), ('vacc 1', 0, 0, .003), ('all 1', 1, 1, .003)]
for f in a.fits:
    P = {k: v for k, (v, _) in M.SPEC.items()} | json.load(open(f))['params']; print(os.path.basename(f), '(mean t3000-3999 cases/beds; min-max cases t2000-3999)')
    for name, c, m, v in SET:
        act = [M.normalize({'school_closure': c, 'mask_mandate': m, 'vaccination_rate': v}, BOUNDS)] * 4000
        p = np.asarray(M.simulate(P, {'daily_cases': 150.0, 'hospital_load': 45.0}, act))
        print(f'  {name:11s} {p[3000:,0].mean():7.1f} / {p[3000:,1].mean():6.1f}   range {p[2000:,0].min():6.1f}-{p[2000:,0].max():6.1f}  finite={np.isfinite(p).all()}')
