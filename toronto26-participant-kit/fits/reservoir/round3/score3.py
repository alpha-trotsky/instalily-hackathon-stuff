"""Round-3 scorer (free): sigma = heldout3 sigma (0.1*std after tick 20 of R1-R7).
python fits/reservoir/round3/score3.py MODEL.py FIT.json R1 R2 ... [--segs] -> per-run per-obs scores, qNR, mean."""
import json, sys, os, importlib.util
import numpy as np
sys.path.insert(0, 'fits/round3'); sys.path.insert(0, 'fits/round2')
import heldout3
names, SIG = heldout3.sigma('reservoir')
BOUNDS = {'release_rate': (0, 12), 'irrigation_allocation': (0, 8), 'withdrawal_depth': (0, 1), 'aeration': (0, 1)}
CL = np.array([[0, 1200], [0, 40], [0, 60], [0, 1]])

def load(path):
    spec = importlib.util.spec_from_file_location('m' + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def run(model, params, r):
    d = json.load(open(f'data/reservoir/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in d['observations']])
    u = [model.normalize(a, BOUNDS) for a in d['actions']]
    p = np.clip(np.asarray(model.simulate(params, d['initial'], u)), CL[:, 0], CL[:, 1])
    return d, o, p

def score(model, params, runs, segs=False):
    res = {}
    for r in runs:
        d, o, p = run(model, params, r)
        e = p - o; k = 21; em = np.convolve(e[:, 3], np.ones(k) / k, mode='same')
        nr = (1 / (1 + np.abs(em) / SIG[3]))[k // 2: -(k // 2)].mean()
        res[r] = np.append((1 / (1 + np.abs(e) / SIG)).mean(0), nr)
        if segs:
            a = d['actions']; b = [0] + [i for i in range(1, len(a)) if a[i] != a[i - 1]] + [len(a)]
            for i in range(len(b) - 1):
                s0, s1 = b[i], b[i + 1]; w = slice(max(s1 - 10, s0), s1)
                print(f'  {r} [{s0},{s1}) end10 data {o[w].mean(0).round(4).tolist()} model {p[w].mean(0).round(4).tolist()}'
                      f' err/sig {((p - o)[w].mean(0) / SIG).round(1).tolist()}')
    return res

if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    model = load(args[0]); fitd = json.load(open(args[1])); params = fitd.get('params', fitd)
    res = score(model, params, args[2:], '--segs' in sys.argv)
    for r, v in res.items():
        print(f'{r}: ' + ' '.join(f'{x:.3f}' for x in v[:4]) + f'  mean {v[:4].mean():.4f}   qNR {v[4]:.3f}')
    allv = np.array(list(res.values()))
    print('per-obs mean: ' + ' '.join(f'{x:.3f}' for x in allv[:, :4].mean(0)) + f'  MEAN {allv[:, :4].mean():.4f}   qNR {allv[:, 4].mean():.3f}')
