"""Print data vs model traces for a run (5-tick means). usage: trace.py fit.json RUN [t0 t1] [--model M]"""
import sys, json, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
args = sys.argv[1:]; mp = None
if '--model' in args:
    i = args.index('--model'); mp = args[i + 1]; del args[i:i + 2]
d = json.load(open(args[0])); run = args[1]
t0, t1 = (int(args[2]), int(args[3])) if len(args) > 3 else (0, 10**6)
model = core.load_model(mp or d.get('model', 'greybox/ad_auction_model_v2.py'))
ep = core.load_episodes([f'data/ad_auction/{run}.json'], model=model)[0]
p = core.params_for(model, set(d['modules']), d['params'])
pr = np.asarray(core.rollout(model, p, ep)); ob = np.asarray(ep['obs'])
for t in range(max(t0, 0), min(t1, len(ob)), 5):
    a = ep['actions'][t] if 'actions' in ep else ''
    print(t, np.round(ob[t:t+5].mean(0), 3), np.round(pr[t:t+5].mean(0), 3), a)
