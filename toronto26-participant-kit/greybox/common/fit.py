"""Generic full-rollout least-squares fitter for gray-box model modules.

MODEL-MODULE INTERFACE (see greybox/market_model.py and greybox/common/template_model.py)

Required attributes
  SPEC      dict  name -> (initial value in natural units, transform kind). The initial value is the
                    start point of every fit (restart 0) and the value used when a parameter is not fitted.
  MODULES   dict  module name -> (list of parameter names it owns, {param: value that switches it off}).
                    A fit activates a *set of module names* (e.g. {'m1', 'm2', 'withdraw'}); parameters of
                    inactive modules are not fitted and are set to their "off" values.
  to_natural(name, raw) -> natural value;  to_raw(name, value) -> raw optimizer value (inverse).
                    Use bounded transforms (sigmoid for rates in (0, 1), capped gains, ...).
  normalize(action_dict, bounds) -> tuple of normalized controls, in the order simulate expects.
                    `bounds` is {control: [lo, hi]} from the brief / forecast_context.
  simulate(p, initial, actions) -> sequence of len(actions) rows; each row has one value per
                    observable, in OBSERVABLES order, in *natural* (physical) units.
                    p: natural-unit dict for every SPEC name; initial: the noisy reading dict;
                    actions: list of normalize() outputs. Must re-init all hidden state on every call,
                    must not raise for finite params (clip states), stdlib/numpy/scipy only.
Optional attributes
  OBSERVABLES  tuple  output column order (default: the data brief's observables order).
  UNITS        {obs: 'log' | 'linear'}  residual units (default: 'log' if all data > 0 else 'linear').
  NOISE        {obs: sigma}  noise sigma in those units (log units: relative noise, e.g. 0.004).
                             Default: estimated from the data (second-difference MAD over holds).
  CLAMP        {obs: [lo, hi]}  physical output range used by predict.py and the stability gate.
  FIXED        iterable of parameter names never fitted.
  params_for(modules, fitted), free_names(modules)  override the generic versions in core.py.

RESIDUALS: r = (units(pred) - units(obs)) / sigma per observable and tick ("noise units"); all
episodes (runs from one or more data files) are concatenated into one residual vector, so they are
fitted jointly with equal weight per tick. Non-finite predictions give a penalty of 1e4 and every
residual is clipped to +-1e4, so exploding trial parameters never crash the optimizer. The reported
`cost` is scipy's least_squares cost with loss='soft_l1', f_scale=2 (0.5 * sum rho), comparable only
between fits with the same data, window, units and sigma.

    python -m greybox.common.fit --model greybox.market_model --data data/market/A.json \
        --modules m1,m2,withdraw --units log --noise 0.004 --out fits/market_common/m12.json
"""
import argparse
import json
import os
import time
from multiprocessing import get_context
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

from greybox.common import core


class Problem:
    """Residual function for one module set on a list of episodes."""

    def __init__(self, model, episodes, modules, units, sigma, fixed=(), init=None, skip=0):
        self.model, self.episodes, self.modules = model, episodes, set(modules)
        self.units, self.sigma = list(units), np.asarray(sigma, dtype=float)
        self.names = core.free_names(model, self.modules, fixed)
        self.base = core.params_for(model, self.modules, init)
        self.skip = skip
        self.targets = [core.to_units(ep['obs'], self.units) for ep in episodes]

    def x0(self):
        return np.array([self.model.to_raw(n, self.base[n]) for n in self.names], dtype=float)

    def params(self, x):
        return core.params_for(self.model, self.modules,
                               {**self.base, **{n: self.model.to_natural(n, float(v)) for n, v in zip(self.names, x)}})

    def residuals(self, x, horizon=None):
        params = self.params(x)
        out = []
        for ep, target in zip(self.episodes, self.targets):
            h = len(target) if horizon is None else min(horizon, len(target))
            pred = core.to_units(core.rollout(self.model, params, ep, h), self.units)
            out.append(((pred - target[:h]) / self.sigma)[self.skip:].ravel())
        r = np.concatenate(out)
        return np.clip(np.nan_to_num(r, nan=core.PENALTY, posinf=core.PENALTY, neginf=-core.PENALTY),
                       -core.PENALTY, core.PENALTY)


def _solve(problem, start, horizons, train_end, max_nfev):
    x, sol = start, None
    for h in [h for h in horizons if h < train_end] + [train_end]:
        sol = least_squares(problem.residuals, x, kwargs={'horizon': h}, loss='soft_l1', f_scale=2.0,
                            x_scale='jac', max_nfev=max_nfev)
        x = sol.x
    return sol


def _restart_job(task):
    model_spec, episodes, modules, units, sigma, fixed, init, skip, start, horizons, train_end, max_nfev = task
    model = core.load_model(model_spec)
    for ep in episodes:
        ep['u'] = [model.normalize(a, ep['bounds']) for a in ep['actions']]
    problem = Problem(model, episodes, modules, units, sigma, fixed, init, skip)
    started = time.time()
    try:
        sol = _solve(problem, start, horizons, train_end, max_nfev)
    except (OverflowError, ValueError, FloatingPointError) as err:
        return {'cost': float('inf'), 'error': str(err)}
    return {'cost': float(sol.cost), 'x': sol.x.tolist(), 'nfev': int(sol.nfev), 'time_s': time.time() - started}


def fit(model, episodes, modules, units, sigma, restarts=3, horizons=(), train_end=None, fixed=(), init=None,
        max_nfev=400, seed=0, workers=None, skip=0, verbose=True, perturb=0.1):
    """Fit one module set jointly on `episodes`. Returns a dict with params, cost, per-restart costs.

    Restart 0 starts at SPEC defaults (or `init` params); restart k>0 perturbs every raw parameter by
    N(0, perturb) * max(|x0|, 0.5); default 0.1 (fit_market.py used 0.3, which often lands in bad
    basins). `train_end` truncates every episode (ticks).
    `horizons` (e.g. (100, 300)) fits increasing prefixes first, warm-starting each stage.
    Restarts run in parallel processes when workers > 1 (Windows-safe: call under __main__ guard).
    """
    started = time.time()
    train_end = train_end or max(len(ep['obs']) for ep in episodes)
    eps = [{**ep, 'obs': ep['obs'][:train_end], 'actions': ep['actions'][:train_end]} for ep in episodes]
    for ep in eps:
        ep.pop('u', None)
    problem = Problem(model, [{**ep, 'u': [model.normalize(a, ep['bounds']) for a in ep['actions']]} for ep in eps],
                      modules, units, sigma, fixed, init, skip)
    x0 = problem.x0()
    rng = np.random.default_rng(seed)
    starts = [x0 if k == 0 else x0 + rng.normal(0, perturb, size=x0.size) * np.maximum(np.abs(x0), 0.5)
              for k in range(restarts)]
    spec = getattr(model, '__model_spec__', model.__name__)
    tasks = [(spec, eps, sorted(modules), units, list(sigma), list(fixed), init, skip, s, list(horizons), train_end,
              max_nfev) for s in starts]
    workers = workers if workers is not None else min(restarts, max(1, (os.cpu_count() or 2) - 1))
    if workers > 1 and restarts > 1:
        with get_context('spawn').Pool(min(workers, restarts)) as pool:
            results = pool.map(_restart_job, tasks)
    else:
        results = [_restart_job(t) for t in tasks]
    for k, res in enumerate(results):
        if verbose:
            print(f"  restart {k}: cost {res['cost']:.1f} nfev {res.get('nfev')} ({res.get('time_s', 0):.0f}s)", flush=True)
    best = min(results, key=lambda r: r['cost'])
    if not np.isfinite(best['cost']):
        raise RuntimeError('every restart failed')
    params = problem.params(np.array(best['x']))
    return {'model': spec, 'modules': sorted(modules), 'cost': best['cost'], 'restart_costs': [r['cost'] for r in results],
            'train_end': train_end, 'units': dict(zip(eps[0]['names'], units)), 'noise': dict(zip(eps[0]['names'], sigma)),
            'names': eps[0]['names'], 'free': problem.names, 'n_residuals': int(sum(len(ep['obs']) for ep in eps) * len(units)),
            'horizons': list(horizons), 'skip': skip, 'perturb': perturb, 'max_nfev': max_nfev, 'data': sorted({f"{ep['source']}:{ep['run']}" for ep in eps}),
            'time_s': time.time() - started, 'params': params}


def evaluate(model, params, episodes, sigma_score, start=0, end=None):
    """Local score (model and persistence) and RMSE per observable on ticks [start, end) of every episode."""
    preds, obs, pers = [], [], []
    for ep in episodes:
        sl = slice(start, end)
        preds.append(core.rollout(model, params, ep)[sl])
        obs.append(ep['obs'][sl])
        pers.append(core.persistence(ep)[sl])
    preds, obs, pers = map(np.concatenate, (preds, obs, pers))
    if not len(obs):
        return None
    return {'score': core.score(preds, obs, sigma_score).tolist(), 'persistence': core.score(pers, obs, sigma_score).tolist(),
            'rmse': np.sqrt(np.nanmean((preds - obs) ** 2, axis=0)).tolist()}


def parse_value_arg(text):
    """'0.004' -> 0.004; 'log' -> 'log'; 'price=0.004,depth=0.01' -> dict; JSON dict accepted."""
    if text is None:
        return None
    text = text.strip()
    if text.startswith('{'):
        return json.loads(text)

    def conv(v):
        try:
            return float(v)
        except ValueError:
            return v
    if '=' in text:
        return {k.strip(): conv(v) for k, v in (item.split('=') for item in text.split(','))}
    return conv(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--model', required=True, help='dotted module (greybox.market_model) or path to .py')
    ap.add_argument('--data', nargs='+', required=True, help='data files, optionally path.json:runidx,...')
    ap.add_argument('--modules', default='', help='comma list of active module names')
    ap.add_argument('--units', help="'log' | 'linear' | obs=unit,...  (default: model UNITS or auto)")
    ap.add_argument('--noise', help='sigma in residual units: one value or obs=value,... (default: model NOISE or estimated)')
    ap.add_argument('--train-end', type=int, help='fit ticks [0, train_end) of every episode (default: all)')
    ap.add_argument('--horizons', default='', help='curriculum, e.g. 100,300 (then full)')
    ap.add_argument('--restarts', type=int, default=3)
    ap.add_argument('--workers', type=int, help='parallel restart processes (default: min(restarts, cpus-1))')
    ap.add_argument('--max-nfev', type=int, default=400)
    ap.add_argument('--fix', default='', help='comma list of parameter names to hold at their start value')
    ap.add_argument('--init', help='JSON fit file whose params are the start point (restart 0)')
    ap.add_argument('--skip', type=int, default=0, help='drop the first N ticks of each episode from the residuals')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--perturb', type=float, default=0.1, help='restart perturbation scale (raw units, relative)')
    ap.add_argument('--eval', nargs='*', default=[], help='extra data files to score the fit on (sigma = 0.1 x std)')
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args(argv)

    model = core.load_model(args.model)
    episodes = core.load_episodes(args.data, model=model)
    names = episodes[0]['names']
    units, sigma = core.resolve_units_noise(model, names, episodes, parse_value_arg(args.units), parse_value_arg(args.noise))
    modules = {m for m in args.modules.split(',') if m}
    init = json.loads(Path(args.init).read_text())['params'] if args.init else None
    print(f'model {args.model} modules {sorted(modules)} episodes {len(episodes)} units {units} sigma {np.round(sigma, 5).tolist()}')
    result = fit(model, episodes, modules, units, sigma, restarts=args.restarts,
                 horizons=[int(h) for h in args.horizons.split(',') if h], train_end=args.train_end,
                 fixed=[f for f in args.fix.split(',') if f], init=init, max_nfev=args.max_nfev, seed=args.seed,
                 workers=args.workers, skip=args.skip, perturb=args.perturb)
    sig_score = core.score_sigma(episodes + core.load_episodes(args.eval, names=names) if args.eval else episodes)
    result['eval'] = {'sigma_score': sig_score.tolist(),
                      'train': evaluate(model, result['params'], episodes, sig_score, 0, result['train_end'])}
    held = evaluate(model, result['params'], episodes, sig_score, result['train_end'])
    if held:
        result['eval']['heldout_ticks'] = held
    if args.eval:
        result['eval']['eval_data'] = evaluate(model, result['params'], core.load_episodes(args.eval, model=model), sig_score)
    core.write_json(args.out, result)
    line = f"cost {result['cost']:.1f} ({result['time_s']:.0f}s)"
    for key, row in result['eval'].items():
        if isinstance(row, dict):
            line += f" | {key} score {np.mean(row['score']):.4f} (persistence {np.mean(row['persistence']):.4f})"
    print(line)
    print('saved', args.out)


if __name__ == '__main__':
    main()
