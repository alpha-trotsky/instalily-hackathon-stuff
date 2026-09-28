"""Score fits (params json) on the 4 runs with heldout sigma; per-run per-observable + mean.
usage: python3 fits/ad_auction/round2/v2/sc.py fit.json [fit2.json ...] [--model M]"""
import sys, json, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
from greybox.common.fit import evaluate
ALL = ['data/ad_auction/R1.json', 'data/ad_auction/R2c.json', 'data/ad_auction/R3.json', 'data/ad_auction/R4.json']
args = sys.argv[1:]
mp = 'greybox/ad_auction_model_v2.py'
if '--model' in args:
    i = args.index('--model'); mp = args[i + 1]; del args[i:i + 2]
model = core.load_model(mp)
ref = core.load_episodes(ALL, model=model)
sig = core.score_sigma(ref)
for f in args:
    p = json.load(open(f))['params']
    p = core.params_for(model, set(json.load(open(f))['modules']), p)
    row = []
    for ep in ref:
        s = evaluate(model, p, [ep], sig)['score']
        row.append(f"{ep['source'].split('/')[-1][:-5]} {s[0]:.3f}/{s[1]:.3f}/{s[2]:.3f}={np.mean(s):.3f}")
    print(f.split('/')[-1][:28].ljust(28), ' | '.join(row))
