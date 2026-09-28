"""Delay, time-to-63% (linear and log units), overshoot for each switch in R3/R4.  python3 fits/wildlife/round2/switches.py"""
import json, numpy as np
names = ['prey_north', 'predator_north', 'prey_south', 'predator_south']
SW = {'R3': [(80, 'joint.85 off', 200), (200, 'joint1 on', 260), (260, 'joint1 off', 290), (290, 'joint.7 on', 350), (350, 'joint.7 off', 500)],
      'R4': [(80, '+hab.37 (hunt5 on)', 140), (140, '-hunt5 (hab.37 on)', 200), (200, '+corr.7', 260), (260, '-hab.37 (corr.7 on)', 320), (320, '-corr.7', 350)]}
for r, sws in SW.items():
    o = np.array([[x[n] for n in names] for x in json.load(open(f'data/wildlife/{r}.json'))['runs'][0]['observations']])
    for t0, lab, t1 in sws:
        cells = []
        for i, n in enumerate(names):
            pre = o[t0 - 5:t0].mean(0)[i]; seg = o[t0:t1, i]; end = seg[-10:].mean()
            ext = seg.max() if end > pre else seg.min()
            d1 = seg[0] - pre
            def t63(x, a, b):
                if abs(b - a) < 1e-9: return None
                f = (x - a) / (b - a); k = np.where(f >= 0.63)[0]; return int(k[0]) if len(k) else None
            tl = t63(seg, pre, end); tg = t63(np.log(seg), np.log(pre), np.log(end))
            ov = (ext - end) / (end - pre) if abs(end - pre) > 1e-9 else 0
            cells.append(f'{n[:4]}{n.split("_")[1][0].upper()} {pre:.3g}->{end:.3g} d1={d1:+.2g} t63 lin {tl} log {tg} ovs {ov:+.2f}')
        print(f'{r} t={t0} {lab}: ' + ' ; '.join(cells))
# noise: second-difference MAD in the flattest window
for r, (a, b) in [('R3', (420, 500)), ('R4', (270, 320))]:
    o = np.array([[x[n] for n in names] for x in json.load(open(f'data/wildlife/{r}.json'))['runs'][0]['observations']])[a:b]
    d2 = np.diff(o, 2, axis=0); s = np.median(np.abs(d2 - np.median(d2, 0)), 0) / 0.6745 / np.sqrt(6)
    print(r, a, b, 'noise sd', s.round(4), 'rel %', (100 * s / o.mean(0)).round(2))
# predator N/S coupling
for r in ['R3', 'R4']:
    o = np.array([[x[n] for n in names] for x in json.load(open(f'data/wildlife/{r}.json'))['runs'][0]['observations']])
    q = o[30:, 1] / o[30:, 3]
    print(r, 'predN/predS after t30: mean %.3f min %.3f max %.3f; corr(diff) %.2f; corr(level) prey N vs predN %.2f' % (
        q.mean(), q.min(), q.max(), np.corrcoef(np.diff(o[30:, 1]), np.diff(o[30:, 3]))[0, 1], np.corrcoef(o[30:, 0], o[30:, 1])[0, 1]))
