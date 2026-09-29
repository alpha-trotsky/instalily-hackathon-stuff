"""Score a model module + fit params with the round-3 sigma (fits/round3/heldout3.py: 0.1*std after tick 20 of all
data incl. R4c's new ticks). R4c is scored on ticks 350+ only (as heldout3); name 'R4cfull' scores all of R4c.
python fits/hospital_queue/round3/ev3.py MODEL.py FIT.json [R1 R2c R3 R4 R4c ...] [--plot out.png] [--segs]"""
import sys, json, time
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round3'); sys.path.insert(0, 'fits/round2')
from greybox.common import core
import heldout3

NAMES = ('wait_time', 'queue', 'discharges')
_, SIG = heldout3.sigma('hospital_queue')


def load_run(r):
    f = 'R4c' if r == 'R4cfull' else r
    d = json.load(open(f'data/hospital_queue/{f}.json')); run = d['runs'][0]
    obs = np.array([[o[k] for k in NAMES] for o in run['observations']])
    return run['initial'], run['actions'], obs, d['brief']['interventions']


def predict(model, params, r):
    ini, act, obs, bounds = load_run(r)
    pred = np.asarray(model.simulate(params, ini, [model.normalize(a, bounds) for a in act]), float)
    return act, obs, np.clip(np.nan_to_num(pred, nan=0.0), 0, [1000, 1000, 200])


def score(model, params, names):
    res = {}
    for r in names:
        act, obs, pred = predict(model, params, r)
        t0 = 350 if r == 'R4c' else 0
        res[r] = (1 / (1 + np.abs(pred - obs) / SIG))[t0:].mean(0)
    return res


def load(model_path, fit_path):
    model = core.load_model(model_path); p = json.load(open(fit_path))['params']
    for k, (v0, _) in model.SPEC.items():
        p.setdefault(k, v0)
    return model, p


if __name__ == '__main__':
    argv = sys.argv[1:]; plot = None; segs = '--segs' in argv
    argv = [a for a in argv if a != '--segs']
    if '--plot' in argv:
        i = argv.index('--plot'); plot = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    model, p = load(argv[0], argv[1])
    names = argv[2:] or ['R1', 'R2c', 'R3', 'R4c']
    t0 = time.time(); res = score(model, p, names)
    for r, s in res.items():
        print(f'{r:7s} {s.round(3).tolist()} mean {s.mean():.3f}')
    print('all-mean', round(float(np.mean([s.mean() for s in res.values()])), 4), f'({time.time() - t0:.1f}s)')
    if segs:
        for r in names:
            act, obs, pred = predict(model, p, r)
            b = [0] + [i for i in range(1, len(act)) if act[i] != act[i - 1]] + [len(act)]
            for i in range(len(b) - 1):
                e = b[i + 1]
                print(f'  {r} {b[i]}-{e} data {obs[e-10:e].mean(0).round(1).tolist()} model {pred[e-10:e].mean(0).round(1).tolist()}'
                      f' err_sig {((pred - obs)[e-10:e].mean(0) / SIG).round(1).tolist()}')
    if plot:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(3, len(names), figsize=(5 * len(names), 9)); ax = np.atleast_2d(ax).reshape(3, len(names))
        for j, r in enumerate(names):
            act, obs, pred = predict(model, p, r)
            for i in range(3):
                ax[i, j].plot(obs[:, i], 'k', lw=.7); ax[i, j].plot(pred[:, i], 'r', lw=1)
                ax[i, j].set_title(f'{r} {["wait", "queue", "dis"][i]}')
        fig.tight_layout(); fig.savefig(plot, dpi=70)
