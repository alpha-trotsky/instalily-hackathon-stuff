"""Check v1 fits: params at box edges, per-episode scores (sigma = 0.1 std after tick 20), long-run levels.

    python fits/social_contagion/v1/check.py fits/social_contagion/v1/m23_all.json [...]
"""
import json
import sys
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core

DATA = ['data/social_contagion/R1.json', 'data/social_contagion/R2.json', 'data/social_contagion/R3.json']


def longrun(m, p):
    init = {'adopters_a': 50.0, 'adopters_b': 40.0}
    scen = {
        'recovery': [(0, 0, 0)] * 4000,
        'seed200_rec': [(1, 0, 0)] * 200 + [(0, 0, 0)] * 3800,
        'full200_rec': [(1, 1, 1)] * 200 + [(0, 0, 0)] * 3800,
        'full_hold': [(1, 1, 1)] * 4000,
        'bridge1_40_rec': [(0, 0, 0)] * 50 + [(1, 0, 1 / 0.6)] * 40 + [(0, 0, 0)] * 3910,
        'inc_hold': [(0, 1, 0)] * 4000,
    }
    out = {}
    for k, u in scen.items():
        y = m.simulate(p, init, u)
        out[k] = [y[i].round(1).tolist() for i in (99, 499, 1999, 3999)]
    return out


def main():
    m = core.load_model('greybox/social_contagion_model.py')
    eps = core.load_episodes(DATA, model=m)
    sig = core.score_sigma(eps[:2])
    for path in sys.argv[1:]:
        f = json.load(open(path))
        p = f['params']
        print('==', path, 'cost', round(f['cost'], 1), 'modules', f['modules'])
        print('  at bounds:', m.at_bounds({k: p[k] for k in f['free']}))
        print('  params:', {k: round(v, 4) for k, v in p.items()})
        for ep in eps:
            y = core.rollout(m, p, ep)
            print(f"  {ep['source']}: score {core.score(y, ep['obs'], sig).mean():.3f}  persistence "
                  f"{core.score(core.persistence(ep), ep['obs'], sig).mean():.3f}")
        for k, v in longrun(m, p).items():
            print(f'  {k:15s} t100/500/2000/4000', v)


if __name__ == '__main__':
    main()
