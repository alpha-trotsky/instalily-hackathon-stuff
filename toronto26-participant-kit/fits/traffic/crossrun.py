"""Cross-run test (framework 6.3.1): R1-only fits scored on R2 (sigma = 0.1 x std of R2 after tick 20), plus R3.
python fits/traffic/crossrun.py FIT.json [...]"""
import sys, json
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core, gates

m = core.load_model('greybox/traffic_model.py')
eps = {k: core.load_episodes([f'data/traffic/{k}.json'], model=m)[0] for k in ('R2', 'R3')}
for k, ep in eps.items():
    pers = gates.local_score(m, core.params_for(m, set(), None), [ep])['persistence_mean']
    print(k, 'persistence', round(pers, 4))
for f in sys.argv[1:]:
    fj = json.load(open(f))
    p = core.params_for(m, set(fj['modules']), fj['params'])
    row = []
    for k, ep in eps.items():
        r = gates.local_score(m, p, [ep])
        row.append(f"{k} {r['model_mean']:.4f} " + str([round(v, 3) for v in r['model'].values()]))
    print(f, fj['modules'], 'cost', round(fj['cost'], 1), ' | '.join(row))
