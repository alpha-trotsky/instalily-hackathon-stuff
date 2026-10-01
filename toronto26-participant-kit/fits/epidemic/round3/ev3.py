"""Free: score fit JSONs on R1-R6 with the heldout3.py sigma (0.1 x std after tick 20 of R1-R6).
Direct simulate() call (identical to predict.py apart from clamping, which simulate already applies).
python fits/epidemic/round3/ev3.py [--model greybox/epidemic_model_v3.py] [--diag] fit1.json ..."""
import argparse, json, importlib.util, os, sys
import numpy as np
OBS = ['daily_cases', 'hospital_load']; RUNS = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']
BOUNDS = {'school_closure': (0, 1), 'mask_mandate': (0, 1), 'vaccination_rate': (0, 0.003)}


def load_model(path):
    spec = importlib.util.spec_from_file_location('m_' + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


D = {}
for r in RUNS:
    run = json.load(open(f'data/epidemic/{r}.json'))['runs'][0]
    D[r] = (run, np.array([[x[n] for n in OBS] for x in run['observations']]))
SIG = 0.1 * np.concatenate([o[20:] for _, o in D.values()]).std(0)


def sim(M, P, r):
    run, _ = D[r]; full = {k: v for k, (v, _) in M.SPEC.items()} | P
    return np.asarray(M.simulate(full, run['initial'], [M.normalize(a, BOUNDS) for a in run['actions']]))


def scores(M, P):
    return {r: (1 / (1 + np.abs(sim(M, P, r) - D[r][1]) / SIG)).mean(0) for r in RUNS}


def diag(M, P):
    p = sim(M, P, 'R6'); o = D['R6'][1]
    w = lambda a, b, x: x[a:b].mean(0).round(1).tolist()
    pk = int(np.argmax(p[:60, 0])); jd = np.log(o[125, 0] / o[119, 0]); jm = np.log(p[125, 0] / p[119, 0])
    return (f'   R6 peak {p[pk,0]:.0f}@{pk} (data 264@25) | 110-119 {w(110,120,p)} (data {w(110,120,o)}) | '
            f'jump {jm:+.3f} (data {jd:+.3f}) | 145-154 {w(145,155,p)} (data {w(145,155,o)})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--model', default='greybox/epidemic_model_v2.py')
    ap.add_argument('--diag', action='store_true'); ap.add_argument('fits', nargs='+')
    a = ap.parse_args(); M = load_model(a.model)
    for f in a.fits:
        d = json.load(open(f)); P = d.get('params', d); res = scores(M, P)
        old = np.mean([res[r].mean() for r in RUNS[:2]]); r2 = np.mean([res[r].mean() for r in RUNS[2:5]])
        print(f'{os.path.basename(f):24s} old {old:.3f} r2 {r2:.3f} R6 {res["R6"].mean():.3f} | '
              + ' '.join(f'{r} {res[r][0]:.3f}/{res[r][1]:.3f}' for r in RUNS), flush=True)
        if a.diag:
            print(diag(M, P), flush=True)
