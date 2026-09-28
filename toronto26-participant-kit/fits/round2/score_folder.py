import sys, json, numpy as np
sys.path.insert(0, 'fits/round2')
from heldout import score, OLD, NEW
s, folder = sys.argv[1], sys.argv[2]
names, res = score(s, folder, OLD[s] + NEW[s])
m = {r: float(np.mean(v['model'])) for r, v in res.items()}
print(json.dumps({'system': s, 'folder': folder, 'old': round(np.mean([m[r] for r in OLD[s]]), 3), 'new': round(np.mean([m[r] for r in NEW[s]]), 3)}))
