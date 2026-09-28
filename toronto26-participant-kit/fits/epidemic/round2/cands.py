"""Candidates (v2 joint fits) and v1 on the actual round-2 initial readings and actions; decision-rule quantities."""
from common import *
sys.path.insert(0, KIT)
from greybox.common import core
from greybox.common.gates import load_params
model = core.load_model('greybox/epidemic_model.py')
bounds = {'school_closure': (0, 1), 'mask_mandate': (0, 1), 'vaccination_rate': (0, 0.003)}
FITS = {k: load_params(f'fits/epidemic/v2/{k}.json') for k in ['m13_all', 'm12_all', 'base_all', 'm23_all']}
def cand(k, run):
    u = [model.normalize(a, bounds) for a in run['actions']]
    return model.simulate(core.params_for(model, [], None) | FITS[k], run['initial'], u)
if __name__ == '__main__':
    m = v1(); sig = sigma()
    for r in ['R3', 'R4', 'R5']:
        run, o, a = load_run(r); P = {k: cand(k, run) for k in FITS}; P['v1'] = predict(m, run)
        print('==', r)
        wins = [(s, e) for s, e, _ in segs(run)]
        for s, e in wins:
            lo = max(e - 10, s)
            print(f'  [{s}-{e-1}] data {o[lo:e].mean(0).round(1)} ' + ' '.join(f'{k}:{P[k][lo:e].mean(0).round(1)}' for k in P))
        print('  peak0-60 data', o[:60, 0].max().round(1), o[:60, 0].argmax(), ' '.join(f'{k}:{P[k][:60,0].max():.0f}@{P[k][:60,0].argmax()}' for k in P))
        print('  score', ' '.join(f'{k}:{(1/(1+np.abs(P[k]-o)/sig)).mean(0).round(3)}' for k in P))
