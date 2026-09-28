"""Rank (segment, observable) by score lost vs a perfect forecast (sum over ticks of 1 - 1/(1+|err|/sigma)).
Split: transient = first min(20, n/3) ticks; late part -> level (removable by a constant shift of v1 = late median err)
and dynamics (rest). 'floor' = late loss of the best constant (burst floor, unreachable by a smooth forecast);
'reducible' = late loss - floor (can be negative when v1's shape beats a constant)."""
import sys, json
from common import *
runs = sys.argv[1:] or ['R4', 'R5']
rows = []
for nm in runs:
    r, o, a = run(nm); p = pred(r)
    for s, e, act in segments(r, a):
        n = e - s; ntr = min(20, n // 3)
        for i in range(4):
            err = p[s:e, i] - o[s:e, i]; l = 1 - 1 / (1 + np.abs(err) / SIG[i])
            late = err[ntr:]; b = np.median(late) if len(late) else 0.0
            ll = l[ntr:].sum(); lde = (1 - 1 / (1 + np.abs(late - b) / SIG[i])).sum()
            y = o[s + ntr:e, i]
            if len(y):
                grid = np.linspace(0, max(y.max(), 1), 400)
                floor = min((1 - 1 / (1 + np.abs(c - y) / SIG[i])).sum() for c in grid)
            else: floor = 0.0
            rows.append(dict(run=nm, s=s, e=e, seg=label(act), obs=OBS[i], loss=l.sum(), tr=l[:ntr].sum(), level=max(ll - lde, 0),
                             dyn=ll - max(ll - lde, 0), bias_sig=b / SIG[i], floor=floor, reducible=ll - floor, score=1 - l.mean()))
rows.sort(key=lambda x: -x['loss'])
tot = sum(x['loss'] for x in rows)
print(f'total loss {tot:.0f} tick-units over runs {runs}')
print(f"{'run':3s} {'seg':>9s} {'setting':44s} {'obs':8s} {'loss':>6s} {'tr':>5s} {'lvl':>5s} {'dyn':>5s} {'bias/s':>6s} {'floor':>5s} {'redu':>6s} {'score':>5s} type")
for x in rows[:40]:
    parts = {'transient': x['tr'], 'level': x['level'], 'dynamics': x['dyn']}
    if x['obs'].startswith('flow') and x['floor'] > 0.5 * (x['loss'] - x['tr']): parts['dynamics'] = x['reducible'] - x['level']; parts['burst floor'] = x['floor']
    typ = max(parts, key=parts.get)
    print(f"{x['run']:3s} {x['s']:4d}-{x['e']:<4d} {x['seg'][:44]:44s} {x['obs']:8s} {x['loss']:6.1f} {x['tr']:5.1f} {x['level']:5.1f} {x['dyn']:5.1f} {x['bias_sig']:6.2f} {x['floor']:5.1f} {x['reducible']:6.1f} {x['score']:5.2f} {typ}")
json.dump(rows, open('fits/traffic/round2/rank_' + '_'.join(runs) + '.json', 'w'), indent=0)
