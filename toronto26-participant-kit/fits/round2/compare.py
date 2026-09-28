import sys, json, numpy as np
sys.path.insert(0, 'fits/round2')
from heldout import score, OLD, NEW
s = sys.argv[1]; out = {}
for tag, folder in (('v1', f'fits/round2/v1_models/{s}'), ('v2', f'models/{s}')):
    names, res = score(s, folder, OLD[s] + NEW[s])
    out[tag] = {r: round(float(np.mean(v['model'])), 3) for r, v in res.items()}
old = lambda t: round(np.mean([out[t][r] for r in OLD[s]]), 3); new = lambda t: round(np.mean([out[t][r] for r in NEW[s]]), 3)
print(json.dumps({'system': s, 'old_v1': old('v1'), 'old_v2': old('v2'), 'new_v1_heldout': new('v1'), 'new_v2_insample': new('v2'), 'runs': out}))
