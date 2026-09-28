import json, numpy as np, importlib.util
NAMES = ['win_rate', 'spend', 'conversions']; CTRL = ['bid', 'budget_cap', 'targeting_breadth']
spec = importlib.util.spec_from_file_location('v', 'fits/round2/v1_models/ad_auction/predict.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx = json.load(open('docs/ad_auction.json'))['brief']['forecast_context']
sig = np.array(json.load(open('fits/ad_auction/round2/loss.json'))['sigma'])
for r in ['R1', 'R2c', 'R3', 'R4']:
    run = json.load(open(f'data/ad_auction/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in NAMES] for x in run['observations']]); a = np.array([[x[c] for c in CTRL] for x in run['actions']])
    p = np.array([[x[n] for n in NAMES] for x in mod.predict(run['initial'], run['actions'], ctx)])
    L = 1 - 1 / (1 + np.abs(p - o) / sig)
    since = np.zeros(len(a), int)
    for t in range(1, len(a)): since[t] = 0 if np.any(a[t] != a[t - 1]) else since[t - 1] + 1
    tr = since < 25; reset = np.arange(len(a)) < 70
    print(f'{r}: total lost {L.sum(0).round(1)} | within 25 ticks of a switch {L[tr].sum(0).round(1)} ({tr.mean():.0%} of ticks) | '
          f'>=25 ticks {L[~tr].sum(0).round(1)} | first 70 ticks {L[reset].sum(0).round(1)} | mean score if tail only {(1-L[~tr]).mean(0).round(3)}')
