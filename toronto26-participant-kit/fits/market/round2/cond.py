"""Free: conditional v1 tests. (a) v1 price driven by OBSERVED depth (withdraw term); (b) v1 volume driven by OBSERVED price;
(c) v1 depth driven by observed price (M2 memories). Shows which block fails on its own."""
import json, math, sys
import numpy as np
sys.path.insert(0, '.')
from fits.round2.heldout import sigma
P = json.load(open('fits/round2/v1_models/market/params.json'))['params']
_, SIG = sigma('market'); N = ['price', 'volume', 'depth']
def sim(p, ini, acts, obs):
    lp = math.log(ini['price']); d = ini['depth']; lv = math.log(ini['volume'])
    q1 = q2 = lp; z = 1.0; f = 0.0; cu = cd = 0.0; wd = 0.0; dprev = ini['depth']; lpo_prev = math.log(ini['price'])
    out = []
    for t, (r, tau) in enumerate(acts):
        f += p['k_in'] * max(r - f, 0) - p['k_out'] * max(f - r, 0)
        tgt = p['c_p'] - p['w_r'] * r - p['w_f'] * f + p['w_tau'] * tau + p['w_w'] * wd + p['lam_p'] * z
        q1 += p['a1'] * (tgt - q1); q2 += p['a2'] * (q1 - q2)
        dp = p['k_p'] * (q2 - lp); lp += dp
        # observed quantities
        do = obs[t][2]; lpo = math.log(obs[t][0]); dpo = lpo - lpo_prev; lpo_prev = lpo
        wd += p['a_w'] * (max(dprev - do, 0) / dprev - wd); dprev = do        # (a) withdraw from observed depth
        cu += p['a_c'] * (max(dpo, 0) - cu); cd += p['a_c'] * (max(-dpo, 0) - cd)  # (c) M2 from observed price
        dt = math.exp(p['c_d']) * (1 + p['w_dtau'] * tau - p['m_up'] * cu - p['m_dn'] * cd + p['lam_d'] * z)
        d += p['k_d'] * (dt - d)
        vt = math.log(math.exp(p['c_v']) * (1 + p['b_up'] * max(dpo, 0) + p['b_dn'] * max(-dpo, 0))) + p['lam_v'] * z
        lv += p['k_v'] * (vt - lv)
        z *= 1 - p['a_z']
        out.append((math.exp(lp), math.exp(lv), d))
    return np.array(out)
for r in 'ABC':
    run = json.load(open(f'data/market/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in N] for x in run['observations']])
    acts = [(x['interest_rate'] / .1, x['transaction_tax'] / .05) for x in run['actions']]
    c = sim(P, run['initial'], acts, o); v1 = np.load(f'fits/market/round2/{r}_v1pred.npy')
    sc = lambda p: (1 / (1 + np.abs(p - o) / SIG)).mean(0).round(3)
    print(r, 'v1 score', sc(v1), ' conditional score', sc(c))
    np.save(f'fits/market/round2/{r}_cond.npy', c)
    if r != 'A':
        for s, e in ([(0,150),(150,300),(300,425),(425,475),(475,600)] if r == 'B' else [(0,125),(125,250),(250,375),(375,500),(500,600)]):
            print(f'  [{s},{e}) last10 data {o[e-10:e].mean(0).round(2)}  cond {c[e-10:e].mean(0).round(2)}  v1 {v1[e-10:e].mean(0).round(2)}')
