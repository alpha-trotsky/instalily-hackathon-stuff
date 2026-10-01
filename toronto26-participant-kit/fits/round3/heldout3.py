"""Free: round-3 held-out scorer. sigma = 0.1*std after tick 20 of ALL data (old + round 2 + round 3), fixed for every
round-3 comparison. Continuation files (hospital R4c, wildlife R4c) are scored on their NEW ticks only (the prefix is R4).

    python fits/round3/heldout3.py SYSTEM [--model models/SYSTEM] [--files R6 ...] [--segs]
"""
import argparse, importlib.util, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'round2'))
from heldout import OLD, NEW, episodes, load
R3 = {'epidemic':['R6'],'wildlife':['R4c'],'ad_auction':['R5'],'social_contagion':['R6'],'power_grid':['R5'],
      'reservoir':['R6XD','R7XS'],'traffic':['R6'],'supply_chain':['R6'],'hospital_queue':['R4c'],'market':['D']}
START = {('hospital_queue','R4c'):350, ('wildlife','R4c'):350}
ALL = {s: OLD[s] + NEW[s] + [f for f in R3[s] if not f.endswith('c')] for s in R3}   # R4c duplicates R4's prefix

def sigma(s):
    eps = episodes(s, ALL[s] + [f for f in R3[s] if f.endswith('c')]); names = list(eps[0][1])
    arr = []
    for r, _, _, ob in eps:
        a = np.array([[o[n] for n in names] for o in ob])[20:]
        arr.append(a[START.get((s, r), 0):] if r.endswith('c') else a)
    return names, 0.1 * np.concatenate(arr).std(0)

def score(s, folder, files, segs=False):
    names, sig = sigma(s); ctx = json.load(open(f'docs/{s}.json'))['brief']['forecast_context']
    mod = load(folder, os.path.basename(folder.rstrip('/')) + str(abs(hash(folder)))); res = {}
    for r, ini, act, ob in episodes(s, files):
        o = np.array([[x[n] for n in names] for x in ob])
        p = np.array([[x[n] for n in names] for x in mod.predict(ini, act, ctx)])
        t0 = START.get((s, r), 0)
        sc = 1 / (1 + np.abs(p - o) / sig)
        res[r] = dict(model=sc[t0:].mean(0).round(3).tolist())
        if segs:
            b = [t0] + [i for i in range(t0 + 1, len(act)) if act[i] != act[i - 1]] + [len(act)]
            res[r]['segs'] = [dict(t=[b[i], b[i+1]], data=o[b[i+1]-10:b[i+1]].mean(0).round(3).tolist(),
                                   model=p[b[i+1]-10:b[i+1]].mean(0).round(3).tolist(),
                                   err_sigma=((p - o)[b[i+1]-10:b[i+1]].mean(0) / sig).round(1).tolist(),
                                   score=sc[b[i]:b[i+1]].mean(0).round(3).tolist()) for i in range(len(b) - 1)]
    return names, sig, res

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('system'); ap.add_argument('--model'); ap.add_argument('--files', nargs='*')
    ap.add_argument('--segs', action='store_true')
    a = ap.parse_args(); folder = a.model or f'models/{a.system}'; files = a.files or R3[a.system]
    names, sig, res = score(a.system, folder, files, a.segs)
    allm = [np.mean(v['model']) for v in res.values()]
    print(json.dumps({'system': a.system, 'model': folder, 'observables': names, 'sigma': sig.round(4).tolist(), 'runs': res,
                      'mean_model': round(float(np.mean(allm)), 4)}))
