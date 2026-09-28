"""Round-2 diagnosis for hospital_queue (free: no steps). Run from KIT: python3 fits/hospital_queue/round2/diag.py
Plots every run with the v1 prediction overlaid, prints per-segment levels (last 10 ticks) and per-segment score loss."""
import importlib.util, json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = 'hospital_queue'
OUT = 'fits/hospital_queue/round2'
sys.path.insert(0, 'fits/round2')
import heldout  # noqa
names, sig = heldout.sigma(S)
ctx = json.load(open(f'docs/{S}.json'))['brief']['forecast_context']
spec = importlib.util.spec_from_file_location('v1pred', f'fits/round2/v1_models/{S}/predict.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
CTRL = ['staffing', 'elective_scheduling', 'diagnostic_allocation', 'urgent_priority', 'overtime', 'followup_capacity']
REC = dict(staffing=20, elective_scheduling=0, diagnostic_allocation=0.4, urgent_priority=0.6, overtime=0, followup_capacity=1)


def segs_of(acts):
    out, st = [], 0
    for t in range(1, len(acts) + 1):
        if t == len(acts) or acts[t] != acts[st]:
            out.append((st, t)); st = t
    return out


def label(a):
    diff = {k: a[k] for k in CTRL if abs(a[k] - REC[k]) > 1e-9}
    return 'recovery' if not diff else ' '.join(f'{k[:5]}={v:g}' for k, v in diff.items())


def run(r):
    d = json.load(open(f'data/{S}/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in names] for x in d['observations']])
    p = np.array([[x[n] for n in names] for x in mod.predict(d['initial'], d['actions'], ctx)])
    return d, o, p


res = {'sigma': dict(zip(names, sig.round(4).tolist())), 'runs': {}}
losses = []
for r in ['R1', 'R2c', 'R3', 'R4']:
    d, o, p = run(r)
    acts = d['actions']; T = len(o)
    loss = 1 - 1 / (1 + np.abs(p - o) / sig)
    rr = {'initial': d['initial'], 'score': (1 - loss).mean(0).round(3).tolist(), 'segments': []}
    for a, b in segs_of(acts):
        w = slice(max(a, b - 10), b)
        seg = dict(ticks=[a, b], action=label(acts[a]),
                   obs_last10=o[w].mean(0).round(2).tolist(), pred_last10=p[w].mean(0).round(2).tolist(),
                   err_sigma_last10=((p[w].mean(0) - o[w].mean(0)) / sig).round(2).tolist(),
                   mean_abs_err_sigma=(np.abs(p[a:b] - o[a:b]) / sig).mean(0).round(2).tolist(),
                   mean_signed_err_sigma=((p[a:b] - o[a:b]) / sig).mean(0).round(2).tolist(),
                   loss_ticks=loss[a:b].sum(0).round(1).tolist())
        rr['segments'].append(seg)
        for j, n in enumerate(names):
            losses.append((float(loss[a:b, j].sum()), r, a, b, n, seg['action'], seg['mean_signed_err_sigma'][j],
                           seg['mean_abs_err_sigma'][j]))
    res['runs'][r] = rr
    # plot
    fig, ax = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
    for j, n in enumerate(names):
        ax[j].plot(o[:, j], 'k', lw=0.8, label='data')
        ax[j].plot(p[:, j], 'r', lw=1.2, label='v1 (final_m12)')
        ax[j].set_ylabel(n); ax[j].grid(alpha=.3)
        for a, b in segs_of(acts):
            ax[j].axvline(a, color='gray', lw=0.5, ls=':')
    ax[0].legend(); ax[0].set_title(f'{S} {r}: data vs v1  (score {np.mean(rr["score"]):.3f}; per obs {rr["score"]})')
    lo = {k: v[0] for k, v in ctx.get('intervention_bounds', {}).items()} if ctx.get('intervention_bounds') else None
    B = {'staffing': (1, 20), 'elective_scheduling': (0, 20), 'diagnostic_allocation': (0.1, 0.8), 'urgent_priority': (0, 1),
         'overtime': (0, 1), 'followup_capacity': (0, 1)}
    for k in CTRL:
        v = np.array([x[k] for x in acts]); l, h = B[k]
        ax[3].plot((v - l) / (h - l), label=k, lw=1.2)
    ax[3].set_ylabel('controls (min-max)'); ax[3].legend(fontsize=7, ncol=3); ax[3].set_xlabel('tick')
    plt.tight_layout(); plt.savefig(f'{OUT}/{r}_v1.png', dpi=90); plt.close()

losses.sort(reverse=True)
res['loss_ranking'] = [dict(loss=round(l, 1), run=r, ticks=[a, b], obs=n, action=lab, signed_sigma=s, abs_sigma=m)
                       for l, r, a, b, n, lab, s, m in losses[:40]]
json.dump(res, open(f'{OUT}/diag.json', 'w'), indent=1)
print('sigma', dict(zip(names, sig.round(3))))
for r, rr in res['runs'].items():
    print(f'\n== {r} init {({k: round(v, 2) for k, v in rr["initial"].items()})} score {rr["score"]}')
    for s in rr['segments']:
        print(f'  {s["ticks"][0]:4d}-{s["ticks"][1]:4d} {s["action"][:60]:60s} obs {s["obs_last10"]} pred {s["pred_last10"]} '
              f'err {s["err_sigma_last10"]} |e| {s["mean_abs_err_sigma"]} loss {s["loss_ticks"]}')
print('\nTop losses')
for x in res['loss_ranking'][:25]:
    print(x)
