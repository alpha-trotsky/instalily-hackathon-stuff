"""Free: score a predict.py folder on data files (held-out test, framework §6.3). sigma = 0.1*std after tick 20 of ALL
data for the system (old + round 2), so scores are comparable across model versions.

    python fits/round2/heldout.py SYSTEM [--model models/SYSTEM] [--files R3 R4 ...]   # default: round-2 files
"""
import argparse, glob, importlib.util, json, os, sys
import numpy as np
OLD = {'epidemic':['R1','R2'],'wildlife':['R1','R2c'],'ad_auction':['R1','R2c'],'social_contagion':['R1','R2','R3'],
 'power_grid':['R1','R2c'],'reservoir':['R1','R2','R3'],'traffic':['R1','R2','R3'],'supply_chain':['R1','R2','R3'],
 'hospital_queue':['R1','R2c'],'market':['A']}
NEW = {'epidemic':['R3','R4','R5'],'wildlife':['R3','R4'],'ad_auction':['R3','R4'],'social_contagion':['R4','R5'],
 'power_grid':['R3','R4'],'reservoir':['R4','R5'],'traffic':['R4','R5'],'supply_chain':['R4','R5'],
 'hospital_queue':['R3','R4'],'market':['B','C']}

def episodes(s, names):
    out = []
    for r in names:
        p = f'data/{s}/{r}.json'
        if os.path.exists(p):
            for run in json.load(open(p))['runs']:
                out.append((r, run['initial'], run['actions'], run['observations']))
    return out

def sigma(s):
    eps = episodes(s, OLD[s] + NEW[s]); names = list(eps[0][1])
    allobs = np.concatenate([np.array([[o[n] for n in names] for o in ob])[20:] for _, _, _, ob in eps])
    return names, 0.1 * allobs.std(0)

def load(folder, tag):
    spec = importlib.util.spec_from_file_location(f'pred_{tag}', os.path.join(folder, 'predict.py'))
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod); return mod

def score(s, folder, files):
    names, sig = sigma(s); ctx = json.load(open(f'docs/{s}.json'))['brief']['forecast_context']
    mod = load(folder, os.path.basename(folder.rstrip('/')) + str(abs(hash(folder)))); res = {}
    for r, ini, act, ob in episodes(s, files):
        o = np.array([[x[n] for n in names] for x in ob])
        p = np.array([[x[n] for n in names] for x in mod.predict(ini, act, ctx)])
        pers = np.array([[ini[n] for n in names]] * len(o))
        res[r] = dict(model=(1 / (1 + np.abs(p - o) / sig)).mean(0).round(3).tolist(),
                      persistence=(1 / (1 + np.abs(pers - o) / sig)).mean(0).round(3).tolist())
    return names, res

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('system'); ap.add_argument('--model'); ap.add_argument('--files', nargs='*')
    a = ap.parse_args(); folder = a.model or f'models/{a.system}'; files = a.files or NEW[a.system]
    names, res = score(a.system, folder, files)
    allm = [np.mean(v['model']) for v in res.values()]
    print(json.dumps({'system': a.system, 'model': folder, 'observables': names, 'runs': res,
                      'mean_model': round(float(np.mean(allm)), 4) if allm else None}, indent=1))
