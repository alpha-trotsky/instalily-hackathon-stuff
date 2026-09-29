"""Round-3 scorer for ad_auction fit JSONs: heldout3 sigma (0.1 x std after tick 20 of R1,R2c,R3,R4,R5).
usage: python fits/ad_auction/round3/sc3.py fit.json [fit2.json ...] [--model M] [--runs R3,R5]"""
import sys, json, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
from greybox.common.fit import evaluate
ALL = ['data/ad_auction/R1.json', 'data/ad_auction/R2c.json', 'data/ad_auction/R3.json', 'data/ad_auction/R4.json',
       'data/ad_auction/R5.json']
args = sys.argv[1:]
mp = None; runs = None
if '--model' in args:
    i = args.index('--model'); mp = args[i + 1]; del args[i:i + 2]
if '--runs' in args:
    i = args.index('--runs'); runs = args[i + 1].split(','); del args[i:i + 2]
for f in args:
    d = json.load(open(f))
    model = core.load_model(mp or d.get('model', 'greybox/ad_auction_model_v2.py'))
    ref = core.load_episodes(ALL, model=model)
    sig = core.score_sigma(ref)
    p = core.params_for(model, set(d['modules']), d['params'])
    row = []; ms = []
    for ep in ref:
        r = ep['source'].split('/')[-1][:-5]
        if runs and r not in runs:
            continue
        s = evaluate(model, p, [ep], sig)['score']; ms.append(np.mean(s))
        row.append(f"{r} {s[0]:.3f}/{s[1]:.3f}/{s[2]:.3f}={np.mean(s):.4f}")
    print(f.split('/')[-1][:30].ljust(30), ' | '.join(row), f'| mean {np.mean(ms):.4f}')
