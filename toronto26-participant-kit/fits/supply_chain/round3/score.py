"""Free: score MODULE with a params json on runs, heldout3 sigma. python score.py MODULE PARAMS R4 [R5 ...]"""
import sys, os, json, importlib.util, numpy as np
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'fits', 'round2'))
from greybox.common import core
spec = importlib.util.spec_from_file_location('ho3', 'fits/round3/heldout3.py'); ho = importlib.util.module_from_spec(spec); spec.loader.exec_module(ho)
s = ho.sigma('supply_chain')[1]
model = core.load_model(sys.argv[1]); p = json.load(open(sys.argv[2]))['params']
for r in sys.argv[3:]:
    ep = core.load_episodes([f'data/supply_chain/{r}.json'], model=model)[0]
    sc = core.score(core.rollout(model, p, ep), ep['obs'], s)
    print(r, [round(float(x), 3) for x in sc], 'mean', round(float(np.mean(sc)), 3))
