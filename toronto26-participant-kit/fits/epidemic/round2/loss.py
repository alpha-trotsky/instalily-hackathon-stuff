"""Score lost vs a perfect forecast per (run, segment, observable) for v1; classify level/dynamics/transient."""
from common import *
m = v1(); sig = sigma(); rows = []
for r in ['R1','R2','R3','R4','R5']:
    run, o, a = load_run(r); p = predict(m, run)
    for s, e, act in segs(run):
        for j, n in enumerate(OBS):
            err = (p[s:e, j] - o[s:e, j]) / sig[j]
            loss = 1 - 1/(1+np.abs(err))
            k = min(15, e - s)
            rows.append(dict(run=r, s=s, e=e, act=act, obs=n, lost=loss.sum(), per_tick=loss.mean(),
                             first15=loss[:k].sum()/max(loss.sum(),1e-9), bias=err.mean(), mabs=np.abs(err).mean(),
                             signr=abs(err.mean())/max(np.abs(err).mean(),1e-9), last10=err[-10:].mean(), maxe=err[np.abs(err).argmax()]))
def cls(x):
    if x['s'] == 0 or x['first15'] > 0.5: return 'transient'
    if x['signr'] > 0.8 and abs(x['last10']) > 0.5*x['mabs']: return 'level'
    return 'dynamics'
def short(act): return 'C%.2g M%.2g V%.2g' % (act['school_closure'], act['mask_mandate'], act['vaccination_rate']/0.003)
for new in (True, False):
    sel = [x for x in rows if (x['run'] in ('R3','R4','R5')) == new]
    tot = sum(x['lost'] for x in sel)
    print('\n== ', 'NEW runs' if new else 'OLD runs (in-sample)', f'total lost {tot:.1f} ticks-equivalent')
    print('rank run  seg        controls           obs    lost  %tot  /tick  bias  mean|e| last10  first15%  class')
    for i, x in enumerate(sorted(sel, key=lambda x: -x['lost'])[:22 if new else 14]):
        print(f"{i+1:3d} {x['run']} {x['s']:4d}-{x['e']-1:<4d} {short(x['act']):18s} {x['obs'][:6]:6s} {x['lost']:6.1f} {100*x['lost']/tot:5.1f} {x['per_tick']:.3f} {x['bias']:+6.2f} {x['mabs']:5.2f} {x['last10']:+6.2f} {100*x['first15']:6.0f}   {cls(x)}")
