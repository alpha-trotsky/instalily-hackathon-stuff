import json, sys, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
pass
for f in sys.argv[1:]:
    d = json.load(open(f))
    mm = core.load_model('greybox/wildlife_model.py' if '/v1/' in f else 'greybox/wildlife_model_v0.py')
    eps = core.load_episodes(['data/wildlife/R1.json', 'data/wildlife/R2c.json'], model=mm)
    print('==', f, 'cost', round(d['cost']), {k: round(v, 4) for k, v in d['params'].items() if k in d['free']})
    for ep, nm in zip(eps, ['R1', 'R2c']):
        pr = core.rollout(mm, d['params'], ep)
        r = np.log(pr) - np.log(ep['obs'])
        segs = [(0, 30), (30, 120), (120, 250), (250, 400), (400, 460), (460, 540)]
        print(nm, 'rms log err per obs', np.sqrt((r ** 2).mean(0)).round(3),
              'seg rms', [(a, np.sqrt((r[a:b] ** 2).mean()).round(3)) for a, b in segs if a < len(r)])
