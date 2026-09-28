"""Settle checks, release ramps, noise, wait/queue relation for hospital_queue round 2 (free). Run from KIT."""
import json, subprocess, sys
import numpy as np

S = 'hospital_queue'
SEG = {'R3': [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250)],
       'R4': [(0, 90), (90, 140), (140, 200), (200, 275), (275, 350)]}
raw = {}
for r in ['R1', 'R2c', 'R3', 'R4']:
    d = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    raw[r] = np.array([[x['wait_time'], x['queue'], x['discharges']] for x in d['observations']])

print('== settle (greybox.common.settle, per segment)')
for r, segs in SEG.items():
    for a, b in segs:
        out = subprocess.run([sys.executable, '-m', 'greybox.common.settle', f'data/{S}/{r}.json', '--start', str(a),
                              '--end', str(b), '--json-only'], capture_output=True, text=True).stdout
        j = json.loads(out[out.index('{'):])
        print(r, a, b, {k: (v['settled'], v['settling_time_text'], v.get('method'), round(v.get('drift_sigma', float('nan')), 1))
                        for k, v in j['observables'].items()})

print('\n== release ramps: 5-tick means of discharges after staffing increases')
for r, t0, lab in [('R1', 175, 'R1 5->20 (dS 15), after staffing-5 only'), ('R1', 580, 'R1 all-pulse release (dS 15)'),
                   ('R3', 200, 'R3 15->20 (dS 5), backlog'), ('R4', 90, 'R4 joint .7 release (dS 10.5)'),
                   ('R4', 200, 'R4 joint 1 release (dS 15)')]:
    m = [raw[r][t0 + 5 * i:t0 + 5 * i + 5, 2].mean() for i in range(12)]
    print(f'{lab:45s}', np.round(m, 1))

print('\n== queue ramp from reset (first 15 ticks)')
for r in ['R3', 'R4']:
    print(r, raw[r][:15, 1].round(0))

print('\n== noise: MAD of 2nd differences /0.6745/sqrt(6), per segment (last 30 ticks)')
for r, segs in SEG.items():
    for a, b in segs:
        x = raw[r][max(a, b - 30):b]
        d2 = np.diff(x, 2, axis=0)
        print(r, a, b, (np.median(np.abs(d2 - np.median(d2, 0)), 0) / 0.6745 / np.sqrt(6)).round(3),
              'std disch', x[:, 2].std().round(2))

print('\n== wait vs (queue-23)/discharges (10-tick means at segment ends)')
for r in ['R1', 'R2c', 'R3', 'R4']:
    o = raw[r]
    for b in range(20, len(o) + 1, 20):
        w, q, dd = o[b - 10:b].mean(0)
        if q > 40:
            print(r, b, f'wait {w:6.1f}  (q-23)/D {(q - 23) / max(dd, .1):6.1f}  ratio {w / ((q - 23) / max(dd, .1)):5.2f}')

print('\n== cross-correlation wait vs queue (lags) R3, R4')
for r in ['R3', 'R4']:
    o = raw[r]; dw = np.diff(o[:, 0]); dq = np.diff(o[:, 1])
    best = max(range(-5, 16), key=lambda L: np.corrcoef(dq[max(0, -L):len(dq) - max(0, L)], dw[max(0, L):len(dw) - max(0, -L)])[0, 1])
    lv = max(range(0, 30), key=lambda L: np.corrcoef(o[:len(o) - L, 1], o[L:, 0])[0, 1])
    print(r, 'level corr queue->wait best lag', lv, round(np.corrcoef(o[:len(o) - lv, 1], o[lv:, 0])[0, 1], 3))
