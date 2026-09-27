"""Standard analysis battery (framework section 6.1) for any system's data file.

    python -m greybox.common.battery data/epidemic/R1.json [--out DIR] [--system epidemic] [--skip 20]

Writes <out>/<stem>_battery.json and one plot per run, <out>/<stem>_r<i>_battery.png (one panel per
observable + a normalized-controls panel; default out = the data file's folder), and prints a summary.

Segments are derived from the actions themselves (maximal runs of an identical action, >= 5 ticks =
"hold"; anything else = "varying", e.g. ramps or fast switching), so continued runs (several
run_schedule calls) and any segment records are handled; the run_schedule call boundaries are
reported separately. Measured per run (units: natural unless stated; sigma = per-observable noise):
  noise              sigma per observable (second-difference MAD over holds), relative sigma, and whether
                     sigma scales with level across holds (log-log slope)
  reset_transient    first segment: jump, total change, settling time, t90, monotone or not
  levels             settled level (mean of the last quarter) of every hold, grouped by action
  switches           per hold->hold switch and observable: delta (and in sigma), delay (first of 3
                     ticks beyond 3 sigma of the pre level, or of the previous hold's extrapolated trend
                     if that hold had not settled), settling time (smoothed series within 2 sigma of the new
                     level), t90, exponential rate k after the delay in linear AND log units, peak
                     excursion, overshoot (fraction of |delta| and sigma), ringing crossings
  onoff_pairs        A->B followed by B->A: k_on/k_off in linear and log units, symmetry verdict per
                     unit (symmetric if 2/3 < ratio < 3/2), return-to-baseline in sigma
  returns            repeated actions: level now vs the first hold with that action (in sigma)
  correlations       (i != j) features of observable i (level, diff, |diff|, rise, fall; diffs of a 5-tick
                     moving average) vs level and diff of observable j at lags -10..+15
                     (positive lag = i leads); best lag and value, plus lag-0 value
  memory_regressions level of j regressed on controls + their fading memories, then adding fading
                     memories of rises and falls of i != j (rates 0.02..0.3): best rate, R^2 gain,
                     coefs (sigma_j per sigma_i of driver). k = None: no first-order fit (rate at grid end)
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np

from greybox.common import core, settle

LAGS = range(-10, 16)
RATES = (0.02, 0.05, 0.1, 0.2, 0.3)
COLORS = ['#eb6834', '#1baf7a', '#4a3aa7', '#e87ba4', '#2f7ed8', '#b8860b']


# ----------------------------------------------------------------------------- helpers

def segments(actions, min_hold=5):
    """[(start, end, kind)] covering the run; kind 'hold' (identical action >= min_hold) or 'varying'."""
    out = []
    for s, e in core.holds(actions, 1):
        kind = 'hold' if e - s >= min_hold else 'varying'
        if out and kind == 'varying' and out[-1][2] == 'varying':
            out[-1] = (out[-1][0], e, 'varying')
        else:
            out.append((s, e, kind))
    return out


def ema(x, a):
    out, m = np.empty(len(x)), 0.0
    for t, v in enumerate(x):
        m += a * (v - m)
        out[t] = m
    return out


def features(y):
    ys = settle.smooth(y, 5)
    d = np.concatenate([[0.0], np.diff(ys)])
    return {'level': y, 'diff': d, 'absdiff': np.abs(d), 'rise': np.maximum(d, 0), 'fall': np.maximum(-d, 0)}


def lag_corr(x, y, lag):
    if lag >= 0:
        a, b = x[:len(x) - lag], y[lag:]
    else:
        a, b = x[-lag:], y[:len(y) + lag]
    if len(a) < 10 or a.std() < 1e-12 or b.std() < 1e-12:
        return float('nan')
    return float(np.corrcoef(a, b)[0, 1])


def r2(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    return 1.0 - resid.var() / max(y.var(), 1e-300), coef


def first_sustained(mask, n=3):
    for t in range(len(mask) - n + 1):
        if mask[t:t + n].all():
            return t
    return None


def rnd(x, k=4):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return None
    return float(round(x, k)) if abs(x) >= 1e-3 or x == 0 else float(f'{x:.3g}')


# ----------------------------------------------------------------------------- analyses

def noise_report(obs, holds_, names):
    out = {}
    for i, name in enumerate(names):
        per = []
        for s, e in holds_:
            if e - s >= 15:
                sig = core.robust_sigma(obs[s + 5:e, i])
                if np.isfinite(sig) and sig > 0:
                    per.append((float(np.mean(np.abs(obs[s + 5:e, i]))), sig))
        sigma = float(np.median([p[1] for p in per])) if per else core.robust_sigma(obs[:, i])
        rep = {'sigma': sigma, 'per_hold': [(rnd(l), rnd(s)) for l, s in per]}
        levels = np.array([p[0] for p in per])
        if len(per) >= 3 and levels.min() > 0 and levels.max() / levels.min() > 1.3:
            slope = float(np.polyfit(np.log(levels), np.log([p[1] for p in per]), 1)[0])
            rep['loglog_slope'] = slope
            rep['scales_with_level'] = 'proportional' if slope > 0.6 else 'constant' if slope < 0.3 else 'partial'
        else:
            rep['scales_with_level'] = 'undetermined (level range too small)'
        if per:
            rep['sigma_rel'] = float(np.median([s / max(l, 1e-12) for l, s in per]))
        out[name] = rep
    return out


def response(seg, pre, post, sigma, positive, pre_slope=0.0):
    """Switch response measurements for one observable over the new segment.

    pre_slope: trend of the previous hold (per tick) when it had not settled; the delay is then measured
    as departure from the extrapolated trend instead of from the flat pre level.
    """
    delta = post - pre
    ys = settle.smooth(seg, 5)
    dev = ys - pre
    peak_t = int(np.argmax(np.abs(dev)))
    rep = {'pre': rnd(pre), 'post': rnd(post), 'delta': rnd(delta), 'delta_sigma': rnd(delta / sigma, 2),
           'peak_excursion': rnd(float(dev[peak_t])), 'peak_tick': peak_t}
    baseline = pre + pre_slope * np.arange(1, len(seg) + 1)
    delay = first_sustained(np.abs(seg - baseline) > 3 * sigma)
    rep['delay'] = delay
    st = settle.settling_time(seg, sigma, final=post)
    rep['settling_time'] = st if st is not None else f'> {len(seg)}'
    if abs(delta) >= 3 * sigma:
        crossed = np.nonzero(np.sign(delta) * (ys - pre) >= 0.9 * abs(delta))[0]
        rep['t90'] = int(crossed[0]) if len(crossed) else None
        over = np.sign(delta) * (ys - post)
        rep['overshoot'] = rnd(max(float(over.max()), 0.0) / abs(delta), 3)
        rep['overshoot_sigma'] = rnd(max(float(over.max()), 0.0) / sigma, 2)
        tail = seg[(delay or 0):]
        for unit, series in (('lin', tail), ('log', np.log(tail) if positive else None)):
            if series is None or len(series) < 8:
                continue
            fit = settle.exp_fit(series, k_min=0.002)
            if fit:  # a rate at either end of the grid means "not a first-order approach"
                rep[f'k_{unit}'] = rnd(fit[2], 4) if 0.0021 < fit[2] < 0.99 else None
        dev_post = ys - post
        big = np.abs(dev_post) > 2 * sigma
        signs = np.sign(dev_post[big])
        rep['ringing_crossings'] = int((signs[1:] != signs[:-1]).sum()) if len(signs) > 1 else 0
    else:
        rep['response'] = 'none (|delta| < 3 sigma)' + (', transient excursion' if abs(dev[peak_t]) > 4 * sigma else '')
    return rep


def analyze_run(ep, info, skip, min_hold):
    obs, actions, names = ep['obs'], ep['actions'], ep['names']
    T, n = obs.shape
    ctrl_names, U = core.normalized_controls(actions, info['recovery'], info['pulse'], ep['bounds'])
    segs = segments(actions, min_hold)
    hold_ranges = [(s, e) for s, e, k in segs if k == 'hold']
    noise = noise_report(obs, hold_ranges, names)
    sigma = np.array([noise[nm]['sigma'] for nm in names])
    positive = [(obs[:, i] > 0).all() for i in range(n)]

    def level(s, e):
        q = max(5, (e - s) // 4)
        return obs[max(s, e - q):e].mean(axis=0)

    seg_rows = []
    for s, e, kind in segs:
        row = {'start': s, 'end': e, 'kind': kind, 'u': [rnd(v, 3) for v in U[s]] if kind == 'hold' else None}
        if kind == 'hold':
            lv = level(s, e)
            chk = settle.check_segment(ep, s, e, list(sigma))
            row['level'] = {nm: rnd(lv[i]) for i, nm in enumerate(names)}
            row['settled'] = {nm: chk[nm]['settled'] for nm in names}
            row['settling_time'] = {nm: chk[nm]['settling_time_text'] for nm in names}
            row['drift_sigma'] = {nm: rnd(chk[nm].get('drift_sigma'), 2) for nm in names}
        seg_rows.append(row)

    # reset transient: the first segment
    s0, e0, _ = segs[0]
    first = obs[s0:e0]
    reset = {}
    for i, nm in enumerate(names):
        init = float(ep['initial'][nm])
        end = float(level(s0, e0)[i])
        ys = settle.smooth(first[:, i], 5)
        d = np.sign(np.diff(ys))
        d = d[np.abs(np.diff(ys)) > sigma[i] / 5]
        crossed = np.nonzero(np.sign(end - init) * (ys - init) >= 0.9 * abs(end - init))[0]
        st = settle.settling_time(first[:, i], sigma[i], final=end)
        reset[nm] = {'initial': rnd(init), 'first_obs': rnd(float(first[0, i])), 'jump_first3': rnd(float(first[:3, i].mean() - init)),
                     'end_level': rnd(end), 'total_change': rnd(end - init), 'change_sigma': rnd((end - init) / sigma[i], 1),
                     'settling_time': st if st is not None else f'> {e0 - s0}',
                     't90': int(crossed[0]) if len(crossed) else None,
                     'monotone': bool((d[1:] == d[:-1]).all()) if len(d) > 1 else True}

    # switches between consecutive holds
    switches = []
    for k in range(1, len(segs)):
        (ps, pe, pk), (s, e, kind) = segs[k - 1], segs[k]
        if pk != 'hold' or kind != 'hold' or e - s < 10:
            continue
        pre, post = level(ps, pe), level(s, e)
        q = max(5, (pe - ps) // 4)
        tail = obs[pe - q:pe]
        slopes = [0.0 if seg_rows[k - 1]['settled'][nm] else float(np.polyfit(np.arange(q), tail[:, i], 1)[0])
                  for i, nm in enumerate(names)]
        # pre level = end of the previous hold's trend line
        pre = np.array([pre[i] + slopes[i] * (q - 1) / 2 for i in range(n)])
        switches.append({'tick': s, 'from_u': [rnd(v, 3) for v in U[ps]], 'to_u': [rnd(v, 3) for v in U[s]],
                         'hold': e - s, 'pre_unsettled': [nm for nm in names if not seg_rows[k - 1]['settled'][nm]],
                         'obs': {nm: response(obs[s:e, i], pre[i], post[i], sigma[i], positive[i], slopes[i])
                                 for i, nm in enumerate(names)}})

    # on/off pairs: A->B then B->A
    pairs = []
    for a, b in zip(switches, switches[1:]):
        if a['to_u'] == b['from_u'] and b['to_u'] == a['from_u']:
            row = {'on_tick': a['tick'], 'off_tick': b['tick'], 'obs': {}}
            for nm in names:
                on, off = a['obs'][nm], b['obs'][nm]
                r = {'delta_on': on['delta'], 'delta_off': off['delta'], 'delay_on': on['delay'], 'delay_off': off['delay'],
                     'settle_on': on['settling_time'], 'settle_off': off['settling_time'],
                     'return_to_baseline_sigma': rnd((off['post'] - on['pre']) / noise[nm]['sigma'], 2)}
                for unit in ('lin', 'log'):
                    if on.get(f'k_{unit}') and off.get(f'k_{unit}'):
                        ratio = on[f'k_{unit}'] / off[f'k_{unit}']
                        r[f'k_ratio_{unit}'] = rnd(ratio, 3)
                        r[f'symmetric_{unit}'] = bool(2 / 3 < ratio < 1.5)
                row['obs'][nm] = r
            pairs.append(row)

    # levels grouped by action, and returns to earlier levels
    by_action, returns = {}, []
    for row in seg_rows:
        if row['kind'] != 'hold':
            continue
        key = json.dumps(row['u'])
        if key in by_action:
            firstrow = by_action[key][0]
            returns.append({'u': row['u'], 'tick': row['start'], 'vs_tick': firstrow['start'],
                            'diff_sigma': {nm: rnd((row['level'][nm] - firstrow['level'][nm]) / noise[nm]['sigma'], 2) for nm in names}})
        by_action.setdefault(key, []).append(row)
    levels = [{'u': json.loads(k), 'holds': [{'start': r['start'], 'end': r['end'], **r['level']} for r in v]}
              for k, v in by_action.items()]

    # cross-observable correlations and fading-memory regressions (after the reset transient)
    sl = slice(min(skip, T // 3), T)
    feats = [features(obs[sl, i]) for i in range(n)]
    corrs = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for fi, x in feats[i].items():
                for fj in ('level', 'diff'):
                    y = feats[j][fj]
                    vals = [lag_corr(x, y, lag) for lag in LAGS]
                    if all(not np.isfinite(v) for v in vals):
                        continue
                    best = int(np.nanargmax(np.abs(vals)))
                    corrs.append({'source': names[i], 'feature': fi, 'target': names[j], 'target_feature': fj,
                                  'best_lag': list(LAGS)[best], 'best_corr': rnd(vals[best], 3), 'corr_lag0': rnd(vals[10], 3)})
    corrs.sort(key=lambda r: -abs(r['best_corr'] or 0))
    Us = U[sl]
    base_cols = [np.ones(len(Us))] + [Us[:, c] for c in range(Us.shape[1])] + \
                [ema(Us[:, c], a) for c in range(Us.shape[1]) for a in (0.05, 0.2)]
    Xb = np.column_stack(base_cols)
    regs = []
    for j in range(n):
        yj = obs[sl, j] / sigma[j]
        r2_base, _ = r2(Xb, yj)
        for i in range(n):
            if i == j:
                continue
            best = None
            for a in RATES:
                rise, fall = ema(feats[i]['rise'] / sigma[i], a), ema(feats[i]['fall'] / sigma[i], a)
                r2_full, coef = r2(np.column_stack([Xb, rise, fall]), yj)
                if best is None or r2_full > best['r2']:
                    best = {'rate': a, 'r2': r2_full, 'coef_rise': rnd(coef[-2], 3), 'coef_fall': rnd(coef[-1], 3)}
            regs.append({'source': names[i], 'target': names[j], 'r2_controls_only': rnd(r2_base, 4),
                         'best_rate': best['rate'], 'r2_with_memories': rnd(best['r2'], 4),
                         'r2_gain': rnd(best['r2'] - r2_base, 4), 'coef_rise_sigma': best['coef_rise'],
                         'coef_fall_sigma': best['coef_fall']})
    regs.sort(key=lambda r: -(r['r2_gain'] or 0))
    calls = [{'start_tick': c.get('start_tick'), 'started_at': c.get('started_at')} for c in ep.get('segments', [])]
    return {'run': ep['run'], 'ticks': T, 'controls': ctrl_names, 'observables': names, 'schedule_calls': calls,
            'noise': noise, 'reset_transient': reset, 'segments': seg_rows, 'levels': levels, 'switches': switches,
            'onoff_pairs': pairs, 'returns': returns, 'correlations': corrs, 'memory_regressions': regs}


def plot_run(ep, report, info, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    obs, names = ep['obs'], ep['names']
    ctrl_names, U = core.normalized_controls(ep['actions'], info['recovery'], info['pulse'], ep['bounds'])
    t = np.arange(1, len(obs) + 1)
    fig, axes = plt.subplots(len(names) + 1, 1, figsize=(11, 1.9 * (len(names) + 1) + 0.6), sharex=True, facecolor='#fcfcfb')
    switch_ticks = [row['start'] for row in report['segments'][1:]]
    for i, (ax, nm) in enumerate(zip(axes, names)):
        ax.plot(t, obs[:, i], color='#52514e', lw=0.9)
        wide = obs[:, i].min() > 0 and obs[:, i].max() / obs[:, i].min() > 20
        if wide:
            ax.set_yscale('log')
        ax.set_ylabel(nm + (' (log)' if wide else ''), color='#52514e', fontsize=9)
    for c, nm in enumerate(ctrl_names):
        axes[-1].plot(t, U[:, c], color=COLORS[c % len(COLORS)], lw=1.4, label=nm)
    axes[-1].set_ylabel('u (0 rec, 1 pulse)', color='#52514e', fontsize=9)
    axes[-1].legend(frameon=False, fontsize=8, loc='upper right', ncol=min(len(ctrl_names), 3))
    for ax in axes:
        for s in switch_ticks:
            ax.axvline(s + 0.5, color='#c9c8c3', lw=0.7, ls='--', zorder=0)
        ax.set_facecolor('#fcfcfb'); ax.grid(axis='y', color='#e6e5e1', lw=0.8); ax.tick_params(colors='#52514e', labelsize=8)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
    axes[-1].set_xlabel('tick (1-based; dashed: action changes)', color='#52514e')
    fig.suptitle(f"{Path(ep['source']).name} run {ep['run']}: observations and normalized controls", x=0.02, ha='left', color='#0b0b0b')
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def print_summary(report):
    for run in report['runs']:
        print(f"\n=== run {run['run']}: {run['ticks']} ticks, controls {run['controls']}")
        print('noise sigma: ' + ', '.join(f"{nm} {r['sigma']:.4g} (rel {r.get('sigma_rel', float('nan')):.2%}, {r['scales_with_level']})"
                                          for nm, r in run['noise'].items()))
        print('reset transient: ' + ', '.join(f"{nm} {r['initial']}->{r['end_level']} settle {r['settling_time']}"
                                              for nm, r in run['reset_transient'].items()))
        for sw in run['switches']:
            print(f"switch @{sw['tick']} u {sw['from_u']}->{sw['to_u']} (hold {sw['hold']}):")
            for nm, r in sw['obs'].items():
                print(f"   {nm:16s} d {r['delta']!s:>9} ({r['delta_sigma']!s:>7} sig) delay {r['delay']!s:>4} settle {r['settling_time']!s:>6} "
                      f"k_lin {r.get('k_lin')!s:>7} k_log {r.get('k_log')!s:>7} overshoot {r.get('overshoot')!s:>5} {r.get('response', '')}")
        for p in run['onoff_pairs']:
            print(f"on/off @{p['on_tick']}/{p['off_tick']}: " + '; '.join(
                f"{nm} k_on/k_off lin {r.get('k_ratio_lin')} log {r.get('k_ratio_log')} return {r['return_to_baseline_sigma']} sig"
                for nm, r in p['obs'].items()))
        print('top correlations: ' + '; '.join(f"{c['source']}.{c['feature']}->{c['target']}.{c['target_feature']} "
                                               f"{c['best_corr']}@{c['best_lag']}" for c in run['correlations'][:6]))
        print('top memory regressions: ' + '; '.join(f"{r['source']} rise/fall -> {r['target']} gain {r['r2_gain']} a={r['best_rate']}"
                                                     for r in run['memory_regressions'][:4]))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Standard analysis battery for a data file.')
    ap.add_argument('data')
    ap.add_argument('--out', type=Path, help='output directory (default: next to the data file)')
    ap.add_argument('--system', help='system name for docs/<system>.json (default: the file family)')
    ap.add_argument('--skip', type=int, default=20, help='ticks excluded from correlations/regressions')
    ap.add_argument('--min-hold', type=int, default=5)
    ap.add_argument('--no-plots', action='store_true')
    args = ap.parse_args(argv)
    episodes = core.load_episodes([args.data])
    data_path, _ = core.split_data_arg(args.data)
    system = args.system or episodes[0]['family']
    info = core.brief_info(system, episodes[0]['brief'])
    out_dir = args.out or Path(data_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(data_path).stem
    report = {'data': args.data, 'system': system, 'recovery': info['recovery'], 'pulse': info['pulse'], 'runs': []}
    for ep in episodes:
        run = analyze_run(ep, info, args.skip, args.min_hold)
        if not args.no_plots:
            plot = out_dir / f"{stem}_r{ep['run']}_battery.png"
            plot_run(ep, run, info, plot)
            run['plot'] = str(plot)
        report['runs'].append(run)
    out = out_dir / f'{stem}_battery.json'
    core.write_json(out, report)
    print_summary(report)
    print('\nsaved', out)


if __name__ == '__main__':
    main()
