"""Feature measurements for the round-2 behaviour catalogue (free)."""
import json, numpy as np
NAMES = ['win_rate', 'spend', 'conversions']; CTRL = ['bid', 'budget_cap', 'targeting_breadth']
def load(r):
    run = json.load(open(f'data/ad_auction/{r}.json'))['runs'][0]
    return (np.array([[x[n] for n in NAMES] for x in run['observations']]),
            np.array([[x[c] for c in CTRL] for x in run['actions']]))
np.set_printoptions(precision=3, suppress=True, linewidth=160)
for r in ['R3', 'R4']:
    o, a = load(r)
    print(f'== {r} first 70 ticks (win, spend, conv)')
    for t in range(0, 70, 1):
        if t < 20 or t % 3 == 0: print(t, o[t])
R3, _ = load('R3'); R4, _ = load('R4')
def w(o, s, e): return o[s:e].mean(0)
print('R3 conv windows: 0-50', w(R3,0,50)[2], '50-100', w(R3,50,100)[2], '100-150', w(R3,100,150)[2], '150-200', w(R3,150,200)[2], '200-250', w(R3,200,250)[2])
print('R3 spend windows', [round(w(R3,s,s+25)[1],2) for s in range(0,250,25)])
print('R3 conv windows25', [round(w(R3,s,s+25)[2],3) for s in range(0,250,25)])
print('R3 win windows25', [round(w(R3,s,s+25)[0],3) for s in range(0,250,25)])
print('R4 bid5 cap50/30 conv windows10', [round(w(R4,s,s+10)[2],3) for s in range(200,300,10)])
print('R4 bid5 spend windows10', [round(w(R4,s,s+10)[1],2) for s in range(200,300,10)])
# slope last 30 ticks cap30
t = np.arange(30); print('R4 cap30 conv slope last30 /tick', np.polyfit(t, R4[270:300, 2], 1)[0], 'spend slope', np.polyfit(t, R4[270:300, 1], 1)[0])
t = np.arange(50); print('R3 conv slope 200-250', np.polyfit(t, R3[200:250, 2], 1)[0], 'spend', np.polyfit(t, R3[200:250, 1], 1)[0])
# switch responses around each switch
def around(o, s, pre=3, post=14):
    for t in range(s - pre, min(s + post, len(o))): print('  ', t, o[t])
for r, o, sw in [('R3', R3, [250, 350, 400, 425]), ('R4', R4, [50, 100, 150, 200, 250])]:
    for s in sw:
        print(f'-- {r} switch at {s}'); around(o, s)
# noise from second differences per segment
def rs(y):
    d = np.diff(y, 2); return np.median(np.abs(d - np.median(d))) / 0.6745 / np.sqrt(6)
for r, o, segs in [('R3', R3, [(60,250),(270,350),(440,500)]), ('R4', R4, [(60,100),(110,150),(210,250),(260,300)])]:
    for s, e in segs:
        lv = o[s:e].mean(0); ns = np.array([rs(o[s:e, i]) for i in range(3)])
        print(f'noise {r} [{s},{e}) level {lv} sd {ns} rel {ns/lv}')
