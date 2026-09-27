"""Settling check (framework section 4.3): has each observable settled at the end of a segment?

Method, per observable on ticks [start, end):
  * sigma: noise from second differences (MAD / 0.6745 / sqrt 6), from the whole run's holds unless given.
  * Fit the LAST HALF of the segment with an exponential approach y = a + b*exp(-k*t) (k profiled on a
    grid, a and b by linear least squares) and with a straight line. The exponential is used if it beats
    the line by a BIC margin, else the line (the fallback).
  * remaining drift = |fitted value at the end - asymptote a| (exponential), or
                      |slope| * half-segment length (line: drift if we held the fitted window again).
  * settled = remaining drift < 2 sigma (a line whose slope is not significant counts as settled).
  * settling time: ticks from the segment start until a 9-tick moving average stays within 2 sigma of the
    final level (asymptote if settled, else the mean of the last quarter); None -> "> segment length".
    This is non-parametric, so delays, humps and overshoots are handled.

    python -m greybox.common.settle data/market/A.json --start 175 --end 325
    python -m greybox.common.settle data/epidemic/R1.json          # default: the run's last hold (constant action)
"""
import argparse
import json
import math
import numpy as np

from greybox.common import core


def exp_fit(y, k_min=None, k_max=1.0, n_grid=80):
    """Profile least squares for y = a + b*exp(-k*t), t = 0..n-1. Returns (a, b, k, sse) or None."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n < 6:
        return None
    t = np.arange(n)
    k_min = k_min or 1.0 / n
    best = None
    for k in np.geomspace(k_min, k_max, n_grid):
        X = np.column_stack([np.ones(n), np.exp(-k * t)])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        sse = float(((X @ coef - y) ** 2).sum())
        if best is None or sse < best[3]:
            best = (float(coef[0]), float(coef[1]), float(k), sse)
    return best


def line_fit(y):
    y = np.asarray(y, dtype=float)
    t = np.arange(len(y))
    slope, intercept = np.polyfit(t, y, 1)
    resid = y - (slope * t + intercept)
    sse = float((resid ** 2).sum())
    se = math.sqrt(sse / max(len(y) - 2, 1) / max(((t - t.mean()) ** 2).sum(), 1e-12))
    return float(slope), float(intercept), sse, se


def smooth(y, window=9):
    """Centered moving average with shrinking windows at the edges."""
    y = np.asarray(y, dtype=float)
    h = window // 2
    c = np.concatenate([[0.0], np.cumsum(y)])
    idx = np.arange(len(y))
    lo, hi = np.maximum(idx - h, 0), np.minimum(idx + h + 1, len(y))
    return (c[hi] - c[lo]) / (hi - lo)


def settling_time(y, sigma, final=None, window=9):
    """Ticks from the segment start until the smoothed series stays within 2 sigma of `final`.

    `final` defaults to the mean of the last quarter. Returns None if it never stays inside
    (or only in the last quarter, i.e. undetermined).
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n < 6:
        return None
    final = float(np.mean(y[-max(3, n // 4):])) if final is None else final
    outside = np.nonzero(np.abs(smooth(y, window) - final) > 2 * sigma)[0]
    t = 0 if len(outside) == 0 else int(outside[-1]) + 1
    return float(t) if t < n - n // 4 or t == 0 else None


def check(y, sigma):
    """Settling verdict for one observable's segment (natural units). Returns a dict."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    half = y[n // 2:]
    out = {'n': n, 'sigma': float(sigma), 'end_level': float(np.mean(y[-max(3, n // 10):]))}
    if len(half) < 6 or not np.isfinite(sigma) or sigma <= 0:
        out.update(settled=None, method='too short', drift=None, settling_time=None)
        return out
    slope, _, sse_lin, se = line_fit(half)
    ef = exp_fit(half)
    m = len(half)
    bic_lin = m * math.log(max(sse_lin / m, 1e-300)) + 2 * math.log(m)
    bic_exp = m * math.log(max(ef[3] / m, 1e-300)) + 3 * math.log(m) if ef else float('inf')
    if bic_exp + 2.0 < bic_lin:
        a, b, k, _ = ef
        drift = abs(b * math.exp(-k * (m - 1)))
        out.update(method='exponential', asymptote=a, rate_k=k, drift=drift, settled=bool(drift < 2 * sigma))
    else:
        drift = abs(slope) * m
        significant = abs(slope) > 2.5 * se
        out.update(method='linear', slope=slope, slope_se=se, drift=drift,
                   settled=bool(drift < 2 * sigma or not significant))
    out['drift_sigma'] = out['drift'] / sigma
    st = settling_time(y, sigma, final=out.get('asymptote') if out['settled'] else None)
    out['settling_time'] = st
    out['settling_time_text'] = f'{st:.0f}' if st is not None else f'> {n}'
    return out


def run_sigma(obs):
    """Per-observable noise sigma from all holds of a run (natural units)."""
    return [core.robust_sigma(obs[:, i]) for i in range(obs.shape[1])]


def check_segment(ep, start, end, sigma=None):
    """Settling report for every observable of an episode over ticks [start, end)."""
    obs = ep['obs']
    if sigma is None:
        sigma = []
        for i in range(obs.shape[1]):
            per = [core.robust_sigma(obs[s + 5:e, i]) for s, e in core.holds(ep['actions'], 15)]
            per = [p for p in per if np.isfinite(p) and p > 0]
            sigma.append(float(np.median(per)) if per else core.robust_sigma(obs[:, i]))
    return {name: check(obs[start:end, i], sigma[i]) for i, name in enumerate(ep['names'])}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Settling check for a segment of a run.')
    ap.add_argument('data')
    ap.add_argument('--run', type=int, default=-1, help='run index in the file (default: last)')
    ap.add_argument('--start', type=int, help='0-based first observation index (default: start of the last hold)')
    ap.add_argument('--end', type=int, help='exclusive end index (default: end of run)')
    ap.add_argument('--sigma', help='obs=value,... natural-unit noise (default: estimated from the run)')
    ap.add_argument('--json-only', action='store_true')
    args = ap.parse_args(argv)
    eps = core.load_episodes([args.data])
    ep = eps[args.run]
    start = args.start if args.start is not None else core.holds(ep['actions'])[-1][0]
    end = args.end if args.end is not None else len(ep['obs'])
    sigma = None
    if args.sigma:
        given = dict(item.split('=') for item in args.sigma.split(','))
        sigma = [float(given[n]) for n in ep['names']]
    report = check_segment(ep, start, end, sigma)
    result = {'data': args.data, 'run': ep['run'], 'start': start, 'end': end,
              'all_settled': all(r['settled'] for r in report.values() if r['settled'] is not None),
              'observables': report}
    if not args.json_only:
        print(f"segment [{start}, {end}) of {args.data} run {ep['run']}")
        print(f"{'observable':18s} {'settled':>7s} {'drift/sig':>9s} {'method':>11s} {'settle_t':>9s} {'sigma':>10s} {'end_level':>11s}")
        for name, r in report.items():
            ds = f"{r['drift_sigma']:.2f}" if r.get('drift') is not None else '-'
            print(f"{name:18s} {str(r['settled']):>7s} {ds:>9s} {r['method']:>11s} {str(r.get('settling_time_text')):>9s} "
                  f"{r['sigma']:10.4g} {r['end_level']:11.4g}")
    print(json.dumps(result, default=core._json_default))


if __name__ == '__main__':
    main()
