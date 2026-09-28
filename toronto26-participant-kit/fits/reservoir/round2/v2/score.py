"""Held-out scorer (free): sigma = 0.1*std after tick 20 of ALL reservoir data (as fits/round2/heldout.py).
python3 fits/reservoir/round2/v2/score.py MODEL.py FIT.json R4 R5 ... -> per-run per-obs scores and mean."""
import json, sys, os, importlib.util
import numpy as np
sys.path.insert(0, 'fits/round2'); import heldout
names, SIG = heldout.sigma('reservoir')
BOUNDS = {'release_rate': (0, 12), 'irrigation_allocation': (0, 8), 'withdrawal_depth': (0, 1), 'aeration': (0, 1)}
CL = np.array([[0, 1200], [0, 40], [0, 60], [0, 1]])

def load(path):
    spec = importlib.util.spec_from_file_location('m' + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def score(model, params, runs):
    res = {}
    for r in runs:
        run = json.load(open(f'data/reservoir/{r}.json'))['runs'][0]
        o = np.array([[x[n] for n in names] for x in run['observations']])
        u = [model.normalize(a, BOUNDS) for a in run['actions']]
        p = np.clip(np.asarray(model.simulate(params, run['initial'], u)), CL[:, 0], CL[:, 1])
        e = p - o; k = 21; em = np.convolve(e[:, 3], np.ones(k) / k, mode='same')
        nr = (1 / (1 + np.abs(em) / SIG[3]))[k // 2: -(k // 2)].mean()
        res[r] = np.append((1 / (1 + np.abs(e) / SIG)).mean(0), nr)
    return res

if __name__ == '__main__':
    model = load(sys.argv[1]); fitd = json.load(open(sys.argv[2])); params = fitd.get('params', fitd)
    res = score(model, params, sys.argv[3:])
    for r, v in res.items():
        print(f'{r}: ' + ' '.join(f'{x:.3f}' for x in v[:4]) + f'  mean {v[:4].mean():.4f}   qNR {v[4]:.3f}')
    allv = np.array(list(res.values()))
    print('per-obs mean: ' + ' '.join(f'{x:.3f}' for x in allv[:, :4].mean(0)) + f'  MEAN {allv[:, :4].mean():.4f}   qNR {allv[:, 4].mean():.3f}')
