"""Re-evaluate the cost of saved fits with the current model file (consistency check); print key params."""
import json, sys
from pathlib import Path
import numpy as np
from greybox.common import core
from greybox.common.fit import Problem

model = core.load_model('greybox/power_grid_model.py')
for f in sys.argv[1:]:
    d = json.loads(Path(f).read_text())
    eps = core.load_episodes(d['data'], model=model)
    for ep in eps:
        ep['u'] = [model.normalize(a, ep['bounds']) for a in ep['actions']]
    pr = Problem(model, eps, d['modules'], [d['units'][n] for n in d['names']], [d['noise'][n] for n in d['names']], init=d['params'])
    r = pr.residuals(pr.x0())
    cost = 0.5 * np.sum(2 * 4.0 * (np.sqrt(1 + (r / 2.0) ** 2) - 1))
    p = d['params']
    ev = d.get('eval', {}).get('eval_data')
    print(f"{f}: saved {d['cost']:.1f} now {cost:.1f} | d2 {p['d2']:.2e} e2 {p['e2']:.3f} c2 {p['c2']:.3f} g2L {p['g2L']:.3f} | g3 {p['g3']:.3f} h3 {p['h3']:.3f} a3 {p['a3']:.4f}"
          + (f" | eval {np.mean(ev['score']):.4f} pers {np.mean(ev['persistence']):.4f}" if ev else ''))
