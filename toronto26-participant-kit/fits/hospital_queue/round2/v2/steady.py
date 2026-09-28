"""Long-run levels of a fit: 4,000-tick holds from reset, and recovery after a 200-tick u=1 pulse.
python fits/hospital_queue/round2/v2/steady.py MODEL.py FIT.json"""
import sys, json
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core

def A(s, e, d, u, o, f):
    return {'staffing': s, 'elective_scheduling': e, 'diagnostic_allocation': d, 'urgent_priority': u, 'overtime': o,
            'followup_capacity': f}

R = A(20, 0, 0.4, 0.6, 0, 1); P7 = A(9.5, 14, 0.645, 0.88, 0.7, 0.3); P1 = A(5, 20, 0.75, 1, 1, 0)
m = core.load_model(sys.argv[1]); p = json.load(open(sys.argv[2]))['params']
for k, (v0, _) in m.SPEC.items(): p.setdefault(k, v0)
b = json.load(open('docs/hospital_queue.json'))['brief']['forecast_context'].get('intervention_bounds') or {}
ini = {'wait_time': 3.0, 'queue': 45.0, 'discharges': 12.0}
def run(acts):
    return np.asarray(m.simulate(p, ini, [m.normalize(a, b) for a in acts]))
for name, acts in [('recovery', [R] * 4000), ('u=0.7 hold', [P7] * 4000), ('u=1 hold', [P1] * 4000),
                   ('E (el 20) hold', [A(20, 20, 0.4, 0.6, 0, 1)] * 4000), ('staff 12 hold', [A(12, 0, 0.4, 0.6, 0, 1)] * 4000),
                   ('u=1 200 then recovery', [P1] * 200 + [R] * 3800)]:
    o = run(acts)
    cells = {t: o[t].round(1).tolist() for t in (99, 399, 999, 3999)}
    print(f'{name:24s} ' + ' | '.join(f't{t + 1}: {v}' for t, v in cells.items()),
          'finite' if np.isfinite(o).all() else 'NONFINITE')
