"""Score a model module + fit params on runs, sigma as fits/round2/heldout.py (0.1*std after tick 20, all 4 runs).
python fits/hospital_queue/round2/v2/ev.py MODEL.py FIT.json [R1 R2c R3 R4] [--plot out.png]"""
import sys, json, time
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round2')
from greybox.common import core
import heldout

def load_runs(names):
    out = []
    for r in names:
        d = json.load(open(f'data/hospital_queue/{r}.json')); run = d['runs'][0]
        out.append((r, run['initial'], run['actions'], np.array([[o[k] for k in ('wait_time', 'queue', 'discharges')] for o in run['observations']]), d['brief']['interventions']))
    return out

_, SIG = heldout.sigma('hospital_queue')

def score(model, params, names):
    res = {}
    for r, ini, act, obs, bounds in load_runs(names):
        u = [model.normalize(a, bounds) for a in act]
        pred = np.asarray(model.simulate(params, ini, u), float)
        pred = np.clip(np.nan_to_num(pred, nan=0.0), 0, [1000, 1000, 200])
        res[r] = (1 / (1 + np.abs(pred - obs) / SIG)).mean(0)
    return res

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--plot' in argv: i = argv.index('--plot'); plot = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    args = argv
    model = core.load_model(args[0]); p = json.load(open(args[1]))['params']
    for k, (v0, _) in model.SPEC.items(): p.setdefault(k, v0)
    names = args[2:] or ['R1', 'R2c', 'R3', 'R4']
    t0 = time.time(); res = score(model, p, names)
    for r, s in res.items(): print(f'{r:4s} {s.round(3).tolist()} mean {s.mean():.3f}')
    print('all-mean', round(float(np.mean([s.mean() for s in res.values()])), 4), f'({time.time()-t0:.1f}s)')
    if '--plot' in sys.argv:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        out = plot
        runs = load_runs(names); fig, ax = plt.subplots(3, len(runs), figsize=(5 * len(runs), 9))
        ax = np.atleast_2d(ax).reshape(3, len(runs))
        for j, (r, ini, act, obs, b) in enumerate(runs):
            pred = np.asarray(model.simulate(p, ini, [model.normalize(a, b) for a in act]))
            for i in range(3):
                ax[i, j].plot(obs[:, i], 'k', lw=.7); ax[i, j].plot(pred[:, i], 'r', lw=1); ax[i, j].set_title(f'{r} {["wait","queue","dis"][i]}')
        fig.tight_layout(); fig.savefig(out, dpi=70)
