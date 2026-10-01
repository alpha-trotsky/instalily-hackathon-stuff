import sys, os, json, numpy as np
sys.path.insert(0, os.getcwd())
from greybox.common import core
import importlib.util
spec = importlib.util.spec_from_file_location('ho3', 'fits/round3/heldout3.py'); ho = importlib.util.module_from_spec(spec); spec.loader.exec_module(ho)
S = ho.sigma('supply_chain')[1]
model = core.load_model('greybox/supply_chain_model_v3.py')
base = json.load(open(sys.argv[1]))['params']
EPS = {r: core.load_episodes([f'data/supply_chain/{r}.json'], model=model)[0] for r in ['R1','R2','R3','R4','R5','R6']}
for kv in sys.argv[2:] or ['']:
    p = dict(base)
    for a in kv.split(','):
        if a: k, v = a.split('='); p[k] = float(v)
    sc = {r: round(float(np.mean(core.score(core.rollout(model, p, e), e['obs'], S))), 3) for r, e in EPS.items()}
    y = core.rollout(model, p, EPS['R6']); y1 = core.rollout(model, p, EPS['R1'])
    print(kv, sc, 'R6 end', np.round(y[45:50].mean(0), 1), np.round(y[95:100].mean(0), 1), 'R1 rush', np.round(y1[460:470, 0].mean(), 1), 'R6 t10', np.round(y[10, 0], 1))
