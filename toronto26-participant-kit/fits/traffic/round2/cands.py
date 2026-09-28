"""Candidates (v1 final, m12/m13/m23 all-data fits) on the actual R4/R5 schedules: per-segment last-10 levels and scores."""
from common import *
from greybox.common import core
import json
model = core.load_model('fits/round2/v1_models/traffic/traffic_model.py')
b = 'fits/traffic/'
fits = {'v1': b + 'final_v1.json', 'm12': b + 'v1/m12_allw.json', 'm13': b + 'v1/m13_allw.json', 'm23': b + 'v1/m23_allw.json'}
bounds = json.load(open('fits/round2/v1_models/traffic/params.json'))['bounds']
res = {}
for nm in ['R4', 'R5']:
    r, o, a = run(nm)
    u = [model.normalize(x, bounds) for x in r['actions']]
    P = {k: core.rollout(model, (lambda d: d['params'] if 'params' in d else d)(json.load(open(f))), {'u': u, 'initial': r['initial'], 'names': OBS}) for k, f in fits.items()}
    segs = segments(r, a)
    if nm == 'R4': segs = [(0, 50, segs[0][2]), (50, 150, segs[0][2])] + segs[1:]
    for s, e, act in segs:
        L = min(10, e - s)
        line = f'{nm} [{s:3d}-{e:3d}) {label(act)[:40]:40s} obs ' + ','.join(f'{v:.2f}' for v in o[e - L:e].mean(0))
        for k, p in P.items():
            lv = p[e - L:e].mean(0); zs = (lv - o[e - L:e].mean(0)) / SIG
            scr = (1 / (1 + np.abs(p[s:e] - o[s:e]) / SIG)).mean(0)
            line += f'\n      {k:4s} last10 ' + ','.join(f'{v:.2f}' for v in lv) + '  err/sig ' + ','.join(f'{v:+.1f}' for v in zs) + '  seg score ' + ','.join(f'{v:.2f}' for v in scr)
        print(line)
    for k, p in P.items():
        print(f'  {nm} {k} run score', (1 / (1 + np.abs(p - o) / SIG)).mean(0).round(3), round(float((1 / (1 + np.abs(p - o) / SIG)).mean()), 3))
