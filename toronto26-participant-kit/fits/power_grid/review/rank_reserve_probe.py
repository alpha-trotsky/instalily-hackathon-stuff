"""Reviewer: rank <=50-step M2-vs-M3 probes (fresh reset) through the review refits (share structure fixed)."""
import sys, json, numpy as np
sys.path.insert(0, 'fits/power_grid/review')
import pg_model_v1s as m1s, pg_model_v2s as m2s
B = json.load(open('data/power_grid/R1.json'))['brief']['interventions']
init = {'load': 105.0, 'frequency': 50.0, 'renewable_share': 0.3}
REC = dict(price_signal=1.5, reserve_dispatch=0, charging_allowance=1, interconnector=1)
def seq(*segs):
    out = []
    for n, kw in segs: out += [dict(REC, **kw)] * n
    return out
C = {
 'A res150 ch0 x1 p1.5 x50': seq((50, dict(reserve_dispatch=150, charging_allowance=0))),
 'A1 twin: res150 ch1 x1 x50': seq((50, dict(reserve_dispatch=150))),
 'B res150 ch0 x40 + rec10': seq((40, dict(reserve_dispatch=150, charging_allowance=0)), (10, {})),
 'C joint pulse x50': seq((50, dict(price_signal=0, reserve_dispatch=150, charging_allowance=0, interconnector=0.2))),
 'D res150 ch0 x1 p0 x50': seq((50, dict(price_signal=0, reserve_dispatch=150, charging_allowance=0))),
 'E ic0 x30 + reopen20': seq((30, dict(interconnector=0)), (20, {})),
 'G price2.0 x50': seq((50, dict(price_signal=2.0))),
 'H res150 ch0 ic0.2 p1.5 x50': seq((50, dict(reserve_dispatch=150, charging_allowance=0, interconnector=0.2))),
}
NS = np.array([0.1, 0.02, 0.0003])       # measurement noise
SS = np.array([1.95, 0.075, 0.014])      # score sigma (0.1 x std)
fits = {}
for tag, mod in [('v1s', m1s), ('v2s', m2s)]:
    for pr in ['m1', 'm12', 'm13']:
        fits[f'{tag}_{pr}'] = (mod, json.load(open(f'fits/power_grid/review/{tag}_{pr}.json'))['params'])
res = {}
print(f"{'probe':32s} {'pair':6s} {'mean|m12-m13|/noise (L,f,S)':30s} {'/score-sigma':22s} {'m12 share end-start':>20s} {'m13':>8s}")
for name, acts in C.items():
    for tag in ['v1s', 'v2s']:
        ys = {}
        for pr in ['m12', 'm13', 'm1']:
            mod, p = fits[f'{tag}_{pr}']
            ys[pr] = np.asarray(mod.simulate(p, init, [mod.normalize(a, B) for a in acts]))
        d = np.abs(ys['m12'] - ys['m13']).mean(0)
        res[f'{name}|{tag}'] = {'noise_units': (d / NS).round(2).tolist(), 'score_units': (d / SS).round(3).tolist(),
                                'm12_share_15_end': [round(ys['m12'][15, 2], 4), round(ys['m12'][-1, 2], 4)],
                                'm13_share_15_end': [round(ys['m13'][15, 2], 4), round(ys['m13'][-1, 2], 4)],
                                'm12_f_end': round(ys['m12'][-1, 1], 3), 'm13_f_end': round(ys['m13'][-1, 1], 3),
                                'm12_L_end': round(ys['m12'][-1, 0], 2), 'm13_L_end': round(ys['m13'][-1, 0], 2)}
        r = res[f'{name}|{tag}']
        print(f"{name:32s} {tag:6s} {str(r['noise_units']):30s} {str(r['score_units']):22s} {str(r['m12_share_15_end']):>20s} {str(r['m13_share_15_end'])}  f_end {r['m12_f_end']}/{r['m13_f_end']} L_end {r['m12_L_end']}/{r['m13_L_end']}")
json.dump(res, open('fits/power_grid/review/probe_rank_review.json', 'w'), indent=1)
