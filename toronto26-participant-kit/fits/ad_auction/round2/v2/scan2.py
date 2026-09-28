"""Grid scan of the fulfilment-capacity parameters (om, capf, kf) around a fit; prints conversion scores per run.
usage: python3 fits/ad_auction/round2/v2/scan2.py fit.json [qx]"""
import sys, json, numpy as np, itertools
sys.path.insert(0, '.')
from greybox.common import core
m = core.load_model('greybox/ad_auction_model_v2.py')
ref = core.load_episodes([f'data/ad_auction/{r}.json' for r in ('R1', 'R2c', 'R3', 'R4')], model=m)
sig = core.score_sigma(ref)
d = json.load(open(sys.argv[1])); p0 = core.params_for(m, set(d['modules']), d['params'])
if len(sys.argv) > 2:
    p0['qx'] = float(sys.argv[2])
res = []
for om, capf, kf in itertools.product((0.5, 1.5, 2.5, 3.5, 5), (1.5, 2.5, 3.5, 5, 7), (0.13, 0.25, 0.5)):
    p = dict(p0, om=om, capf=capf, kf=kf)
    s = [core.score(core.rollout(m, p, ep), ep['obs'], sig)[2] for ep in ref]
    res.append((np.mean(s), om, capf, kf, s))
res.sort(reverse=True)
for r in res[:12]:
    print(f'{r[0]:.3f} om {r[1]} capf {r[2]} kf {r[3]}', ' '.join(f'{x:.3f}' for x in r[4]))
