"""Free: score fit JSONs on R1-R5 with the heldout.py sigma (0.1 x std after tick 20 of R1-R5).
python3 fits/epidemic/round2/v2/ev.py [--model greybox/epidemic_model_v2.py] fit1.json fit2.json ..."""
import argparse, json, importlib.util, sys, os
import numpy as np
OBS = ['daily_cases', 'hospital_load']; RUNS = ['R1', 'R2', 'R3', 'R4', 'R5']
BOUNDS = {'school_closure': (0, 1), 'mask_mandate': (0, 1), 'vaccination_rate': (0, 0.003)}
def load_model(path):
    spec = importlib.util.spec_from_file_location('m_' + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def data():
    out = {}
    for r in RUNS:
        run = json.load(open(f'data/epidemic/{r}.json'))['runs'][0]
        out[r] = (run, np.array([[x[n] for n in OBS] for x in run['observations']]))
    return out
D = data(); SIG = 0.1 * np.concatenate([o[20:] for _, o in D.values()]).std(0)
def sim(M, P, r):
    run, o = D[r]; full = {k: v for k, (v, _) in M.SPEC.items()} | P
    for k, (_, off) in M.MODULES.items():
        pass
    return np.asarray(M.simulate(full, run['initial'], [M.normalize(a, BOUNDS) for a in run['actions']]))
def scores(M, P):
    res = {}
    for r in RUNS:
        p = sim(M, P, r); o = D[r][1]
        res[r] = (1 / (1 + np.abs(p - o) / SIG)).mean(0)
    return res
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--model', default='greybox/epidemic_model_v2.py'); ap.add_argument('fits', nargs='+')
    a = ap.parse_args(); M = load_model(a.model)
    for f in a.fits:
        d = json.load(open(f)); P = d.get('params', d); res = scores(M, P)
        old = np.mean([res[r].mean() for r in RUNS[:2]]); new = np.mean([res[r].mean() for r in RUNS[2:]])
        print(f'{os.path.basename(f):28s} old {old:.3f} new {new:.3f} | ' + ' '.join(f'{r} {res[r][0]:.3f}/{res[r][1]:.3f}' for r in RUNS), flush=True)
