"""Per-segment table: last-10 means (flows also median/mean of last 20), v1 last-10, err in score sigma;
score loss per (segment, observable) and its split into transient / level / dynamics."""
import json, sys
import numpy as np
from common import *
out = {}
runs = sys.argv[1:] or ['R4', 'R5']
print('score sigma', dict(zip(OBS, SIG.round(3))))
for name in runs:
    r, o, a = run(name); p = pred(r); segs = segments(r, a)
    # TR1: u.7 was two segments of the same action; split at 50 for the rule table too
    print(f'\n== {name}')
    rows = []
    for k, (s, e, act) in enumerate(segs):
        L = min(10, e - s); L20 = min(20, e - s)
        ob = o[e - L:e].mean(0); pr = p[e - L:e].mean(0)
        obm20 = np.median(o[e - L20:e], 0); ob20 = o[e - L20:e].mean(0); pr20 = p[e - L20:e].mean(0)
        err = p[s:e] - o[s:e]; loss = 1 - 1 / (1 + np.abs(err) / SIG)
        n = e - s; ntr = min(20, n // 3)
        tr = loss[:ntr].sum(0); late = loss[ntr:]
        bias = np.median(err[ntr:], 0)
        late_debiased = (1 - 1 / (1 + np.abs(err[ntr:] - bias) / SIG)).sum(0)
        lev = late.sum(0) - late_debiased
        rows.append(dict(run=name, seg=k, start=s, end=e, label=label(act), obs_last10=ob.round(2).tolist(), v1_last10=pr.round(2).tolist(),
                         obs_mean20=ob20.round(2).tolist(), obs_med20=obm20.round(2).tolist(), v1_mean20=pr20.round(2).tolist(),
                         err_sigma_last10=((pr - ob) / SIG).round(2).tolist(), err_sigma_mean20=((pr20 - ob20) / SIG).round(2).tolist(),
                         loss=loss.sum(0).round(1).tolist(), loss_transient=tr.round(1).tolist(), loss_level=np.maximum(lev, 0).round(1).tolist(),
                         loss_dyn=(late.sum(0) - np.maximum(lev, 0)).round(1).tolist(), late_bias_sigma=(bias / SIG).round(2).tolist(),
                         mean_score=(1 - loss.mean(0)).round(3).tolist()))
        print(f"[{s:3d}-{e:3d}) {label(act):55s}")
        print('   obs last10 ', np.round(ob, 2), ' med20', np.round(obm20, 2), ' mean20', np.round(ob20, 2))
        print('   v1  last10 ', np.round(pr, 2), ' mean20', np.round(pr20, 2), ' err/sig(mean20)', ((pr20 - ob20) / SIG).round(2))
        print('   loss', loss.sum(0).round(1), 'tr', tr.round(1), 'lvl', np.maximum(lev, 0).round(1), 'bias/sig', (bias / SIG).round(2), 'score', (1 - loss.mean(0)).round(3))
    out[name] = rows
json.dump(out, open('fits/traffic/round2/segtable_' + '_'.join(runs) + '.json', 'w'), indent=1)
