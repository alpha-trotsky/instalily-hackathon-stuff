"""Diagnostic only (no model files changed): quality-only refits of v1 variants on ALL runs (R1-R5), water side
frozen at v1. Variants:
  v1     : v1 structure (slow reset decay z, Cm fed by aeration-on while deep, near-permanent)
  A      : v1 structure, refit quality params on R1-R5
  flush  : pool Dm also removed by deep withdrawal flow kfl*ud*D/V; Cm fed when aeration returns at ANY depth;
           reset transient free (a_z, lam_q); aeration effect saturating: ua_eff = ua**gam
Reports quality score (raw and 21-MA noise-reduced) per run."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from scipy.optimize import least_squares
sys.path.insert(0, 'greybox'); import reservoir_model as M
P0 = json.load(open('fits/reservoir/v1/final.json')); P0 = P0.get('params', P0)
bounds = {'release_rate': (0, 12), 'irrigation_allocation': (0, 8), 'withdrawal_depth': (0, 1), 'aeration': (0, 1)}
RUNS = []
for n in ['R1', 'R2', 'R3', 'R4', 'R5']:
    r, o, a, segs = run(n); acts = [M.normalize(x, bounds) for x in r['actions']]
    w = M.simulate(P0, r['initial'], acts)  # water side from v1
    RUNS.append((n, r, o, acts, w))

def qsim(p, r, acts, w, variant):
    q = float(r['initial']['quality']); z = 1.0; Dm = 0.0; Cm = 0.0; out = np.empty(len(acts))
    for i, (ur, ui, ud, ua) in enumerate(acts):
        V = w[i - 1, 0] if i else r['initial']['level']; D = min(w[i, 2], 2 + 10 * ur + 8 * ui)
        uae = ua ** p['gam'] if variant == 'flush' else ua
        Tq = p['cq'] + p['wqa'] * uae + p['wqd'] * ud + p['wqx'] * uae * ud + p['wqr'] * ur + p['wqi'] * ui + p['lam_q'] * z
        Tq -= p['g3'] * Dm * (1 + p['h3'] * ud) + p['gC'] * Cm
        q = q + p['kq'] * (Tq - q); out[i] = q
        if variant == 'flush':
            Cm += p['kr'] * Dm * (1 - uae) * (1 - Cm) - p['dC'] * Cm
            Dm += p['a3'] * uae * (1 - Dm) - p['a3d'] * (1 - uae) * Dm - p['kfl'] * ud * D / max(V, 50) * Dm
        else:
            Cm += p['kr'] * Dm * ud * (1 - ua) * (1 - Cm) - p['dC'] * Cm
            Dm += p['a3'] * ua * (1 - Dm) - p['a3d'] * (1 - ua) * Dm
        Cm = min(max(Cm, 0), 1); Dm = min(max(Dm, 0), 1); z *= 1 - p['a_z']
    return out

def ma(y, w=21):
    return np.array([y[max(0, i-w//2):i+w//2+1].mean() for i in range(len(y))])
names_v1 = ['cq', 'kq', 'wqa', 'wqd', 'wqx', 'wqr', 'wqi', 'a_z', 'lam_q', 'a3', 'a3d', 'g3', 'h3', 'kr', 'dC', 'gC']
unit = {'kq', 'a_z', 'a3', 'a3d', 'kr', 'dC'}
def pack(p, names): return np.array([M._logit(p[k]) if k in unit else p[k] for k in names])
def unpack(x, names, base):
    p = dict(base)
    for k, v in zip(names, x): p[k] = M._sigmoid(v) if k in unit else v
    return p
def resid(x, names, base, variant):
    p = unpack(x, names, base)
    return np.concatenate([(qsim(p, r, acts, w, variant) - o[:, 3]) / 0.0055 for n, r, o, acts, w in RUNS])
def report(p, variant, tag):
    s = []
    for n, r, o, acts, w in RUNS:
        qq = qsim(p, r, acts, w, variant)
        s.append(f'{n} {(1/(1+np.abs(qq-o[:,3])/SIG[3])).mean():.3f}/{(1/(1+np.abs(ma(qq-o[:,3]))/SIG[3])).mean():.3f}')
    print(f'{tag:8s} quality score raw/NR: ' + '  '.join(s)); return p
base = dict(P0); base.update(gam=1.0, kfl=0.0)
report(base, 'v1', 'v1')
xA = least_squares(resid, pack(base, names_v1), args=(names_v1, base, 'v1'), loss='soft_l1', f_scale=2, max_nfev=400).x
pA = report(unpack(xA, names_v1, base), 'v1', 'A')
names_f = names_v1 + ['gam', 'kfl']; unit |= {'kfl'}
bf = dict(base); bf.update(gam=1.0, kfl=0.5, a_z=0.05, lam_q=0.01, kr=0.05, dC=0.002, cq=0.95)
best = None
for start in (bf, dict(bf, gam=0.5, kfl=0.8, a3=0.02)):
    res = least_squares(resid, pack(start, names_f), args=(names_f, start, 'flush'), loss='soft_l1', f_scale=2, max_nfev=600)
    if best is None or res.cost < best[0]: best = (res.cost, unpack(res.x, names_f, start))
pF = report(best[1], 'flush', 'flush')
json.dump({'A': pA, 'flush': best[1]}, open('fits/reservoir/round2/qtest_params.json', 'w'), indent=1)
print('flush params:', {k: round(best[1][k], 5) for k in names_f})
print('A params:', {k: round(pA[k], 5) for k in names_v1})
