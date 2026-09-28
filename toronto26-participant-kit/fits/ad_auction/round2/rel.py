import json, numpy as np
NAMES = ['win_rate', 'spend', 'conversions']
def load(r):
    run = json.load(open(f'data/ad_auction/{r}.json'))['runs'][0]
    return np.array([[x[n] for n in NAMES] for x in run['observations']])
R3, R4, R2 = load('R3'), load('R4'), load('R2c')
print('R3 u1 conv 360-400:', R3[360:400:3, 2].round(2))
print('R2c P7 conv 175-270:', R2[175:270:5, 2].round(2))
for nm, o in (('R3', R3), ('R4', R4)):
    ds, dc = np.diff(o[:, 1]), np.diff(o[:, 2])
    cc = [(lag, np.corrcoef(ds[:len(ds) - lag], dc[lag:])[0, 1]) for lag in range(0, 16)]
    best = max(cc, key=lambda x: x[1]); print(nm, 'diff corr spend->conv best lag', best[0], round(best[1], 2))
    lv = [(lag, np.corrcoef(o[:len(o) - lag, 1], o[lag:, 2])[0, 1]) for lag in range(0, 30)]
    b = max(lv, key=lambda x: x[1]); print(nm, 'level corr spend->conv best lag', b[0], round(b[1], 2))
    wv = [(lag, np.corrcoef(o[:len(o) - lag, 0], o[lag:, 2])[0, 1]) for lag in range(0, 30)]
    b = max(wv, key=lambda x: x[1]); print(nm, 'level corr win->conv best lag', b[0], round(b[1], 2))
# settled ratios
for nm, o, s, e in (('R3 u.7', R3, 240, 250), ('R3 rec', R3, 340, 350), ('R3 u1(50)', R3, 390, 400), ('R3 u.85', R3, 490, 500),
                    ('R4 b3.25', R4, 40, 50), ('R4 b2', R4, 90, 100), ('R4 b.75', R4, 140, 150), ('R4 rec', R4, 190, 200),
                    ('R4 b5c50', R4, 240, 250), ('R4 b5c30', R4, 290, 300), ('R2c P7', R2, 350, 360)):
    m = o[s:e].mean(0); print(f'{nm:10s} win {m[0]:.3f} spend {m[1]:6.2f} conv {m[2]:.3f} conv/spend {m[2]/m[1]:.3f} spend/win {m[1]/m[0]:.1f} conv/win {m[2]/m[0]:.2f}')
