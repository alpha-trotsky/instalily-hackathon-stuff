"""Gates before packaging (framework section 7): local score, stability, contract.

    # 1. local score vs persistence, sigma = 0.1 x std after tick 20 of the reference data (default: --data)
    python -m greybox.common.gates score --model greybox.market_model --params fits/market/m12.json \
        --data data/market/B.json [--ref data/market/A.json data/market/B.json]
    # 2. stability: 200 random in-bounds schedules (8 of them 40,000 steps) from random initial readings
    python -m greybox.common.gates stability --model greybox.market_model --params fits/market/m12.json \
        --system market [--data data/market/A.json] [--range price=0:5000]
    # 3. contract: fresh subprocess imports <folder>/predict.py, 40 episodes x 4,000 steps + malformed inputs
    python -m greybox.common.gates contract models/market --system market

Each command prints a JSON summary whose "pass" field is the verdict; add --out FILE to save it.
"""
import argparse
import ast
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import numpy as np

from greybox.common import core

ALLOWED_THIRD_PARTY = {'numpy', 'scipy', 'sklearn', 'joblib'}


def load_params(path):
    data = json.loads(Path(path).read_text())
    return data['params'] if 'params' in data else data


# ----------------------------------------------------------------------------- 1. local score

def local_score(model, params, episodes, ref_episodes=None, skip=20, factor=0.1, start=0):
    """Mean over observables and ticks of 1/(1+|err|/sigma), model vs persistence."""
    sigma = core.score_sigma(ref_episodes or episodes, skip, factor)
    preds = np.concatenate([core.rollout(model, params, ep)[start:] for ep in episodes])
    pers = np.concatenate([core.persistence(ep)[start:] for ep in episodes])
    obs = np.concatenate([ep['obs'][start:] for ep in episodes])
    m, p = core.score(preds, obs, sigma), core.score(pers, obs, sigma)
    names = episodes[0]['names']
    return {'sigma': dict(zip(names, sigma.tolist())), 'model': dict(zip(names, m.tolist())),
            'persistence': dict(zip(names, p.tolist())), 'model_mean': float(m.mean()),
            'persistence_mean': float(p.mean()), 'pass': bool(m.mean() > p.mean())}


# ----------------------------------------------------------------------------- 2. stability

def sawtooth(y, actions, min_hold=100, skip=20):
    """Worst sign-alternation fraction of first differences inside long holds (with its amplitude)."""
    worst = {'alternation': 0.0, 'amplitude': 0.0}
    for s, e in core.holds(actions, min_hold):
        seg = y[s + skip:e]
        d = np.diff(seg)
        scale = max(float(np.abs(seg).mean()), 1e-12)
        d = d[np.abs(d) > 1e-7 * scale]
        if len(d) < 10:
            continue
        alt = float(np.mean(np.sign(d[1:]) != np.sign(d[:-1])))
        amp = float(np.abs(d).mean() / scale)
        if alt * (amp > 1e-5) > worst['alternation']:
            worst = {'alternation': alt, 'amplitude': amp}
    return worst


def plausible_ranges(names, episodes, ranges_init, overrides=None):
    out = {}
    for i, name in enumerate(names):
        vals = [ep['obs'][:, i] for ep in episodes] + [np.array(ranges_init.get(name, [0.0, 1.0]), dtype=float)]
        vals = np.concatenate(vals)
        lo_obs, hi_obs = float(vals.min()), float(vals.max())
        lo = 0.0 if lo_obs >= 0 else lo_obs - 50 * abs(lo_obs)
        hi = 50 * hi_obs if hi_obs > 0 else hi_obs + 50 * abs(hi_obs) + 1.0
        out[name] = [lo, hi]
    out.update(overrides or {})
    return out


def stability(model, params, system=None, episodes=(), n=200, n_long=8, steps=4000, long_steps=40000,
              seed=0, ranges=None, max_alternation=0.5):
    info = core.brief_info(system, episodes[0]['brief'] if episodes else None)
    bounds, names = info['bounds'], core.observables(model, {'observables': info['observables']})
    init_ranges = core.initial_ranges(system, episodes, names)
    ranges = plausible_ranges(names, episodes, init_ranges, ranges)
    rng = np.random.default_rng(seed)
    kinds = ('holds', 'switch', 'extremes', 'uniform', 'mixed')
    failures, lo_seen, hi_seen, worst_saw = [], np.full(len(names), np.inf), np.full(len(names), -np.inf), 0.0
    started = time.time()
    for k in range(n):
        length = long_steps if k < n_long else steps
        kind = 'mixed' if k < n_long else kinds[k % len(kinds)]
        actions = core.random_schedule(bounds, length, kind, rng, info['recovery'], info['pulse'])
        ep = {'initial': core.random_initial(init_ranges, rng), 'u': [model.normalize(a, bounds) for a in actions],
              'names': names}
        pred = core.rollout(model, params, ep)
        problems = []
        if not np.isfinite(pred).all():
            problems.append('non-finite')
        else:
            lo_seen, hi_seen = np.minimum(lo_seen, pred.min(0)), np.maximum(hi_seen, pred.max(0))
            for i, name in enumerate(names):
                lo, hi = ranges[name]
                if pred[:, i].min() < lo or pred[:, i].max() > hi:
                    problems.append(f'{name} out of [{lo:.4g}, {hi:.4g}]: {pred[:, i].min():.4g}..{pred[:, i].max():.4g}')
                saw = sawtooth(pred[:, i], actions)
                worst_saw = max(worst_saw, saw['alternation'])
                if saw['alternation'] > max_alternation:
                    problems.append(f"{name} sawtooth alternation {saw['alternation']:.2f} amp {saw['amplitude']:.2g}")
        if problems:
            failures.append({'schedule': k, 'kind': kind, 'steps': length, 'problems': problems})
    return {'schedules': n, 'long': n_long, 'time_s': time.time() - started, 'ranges': ranges,
            'min_seen': dict(zip(names, lo_seen.tolist())), 'max_seen': dict(zip(names, hi_seen.tolist())),
            'worst_alternation': worst_saw, 'failures': failures[:20], 'n_failures': len(failures),
            'pass': not failures}


# ----------------------------------------------------------------------------- 3. contract

CHILD = r'''
import json, math, sys, time
folder, payload_path = sys.argv[1], sys.argv[2]
sys.path.insert(0, folder)
t0 = time.time()
import predict as P
t_import = time.time() - t0
payload = json.load(open(payload_path))
ctx, names, errors = payload['context'], payload['observables'], []
lo = {n: math.inf for n in names}; hi = {n: -math.inf for n in names}
first = None
t1 = time.time()
for k, ep in enumerate(payload['episodes']):
    try:
        out = P.predict(ep['initial'], ep['actions'], ctx)
    except Exception as e:
        errors.append(f'episode {k} raised {e!r}'); continue
    if k == 0:
        first = out
    if not isinstance(out, list) or len(out) != len(ep['actions']):
        errors.append(f'episode {k}: expected list of {len(ep["actions"])}, got {type(out).__name__} len {len(out) if hasattr(out, "__len__") else None}'); continue
    for t, row in enumerate(out):
        if not isinstance(row, dict) or any(n not in row for n in names):
            errors.append(f'episode {k} tick {t}: missing observables'); break
        vals = [row[n] for n in names]
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in vals):
            errors.append(f'episode {k} tick {t}: non-finite {vals}'); break
        for n in names:
            lo[n] = min(lo[n], row[n]); hi[n] = max(hi[n], row[n])
t_run = time.time() - t1
ep = payload['episodes'][0]
repeat = P.predict(ep['initial'], ep['actions'], ctx)
deterministic = repeat == first
malformed = {}
bad_initial = dict(ep['initial']); bad_initial[names[0]] = float('nan')
cases = {
    'nan_initial': (bad_initial, ep['actions'][:50], ctx),
    'missing_control': (ep['initial'], [{}] + ep['actions'][1:50], ctx),
    'string_value': (ep['initial'], [{k: 'x' for k in ep['actions'][0]}] + ep['actions'][1:50], ctx),
    'out_of_bounds': (ep['initial'], [{k: 1e9 for k in ep['actions'][0]}] * 50, ctx),
    'none_context': (ep['initial'], ep['actions'][:50], None),
    'empty_schedule': (ep['initial'], [], ctx),
}
for label, (i0, acts, c) in cases.items():
    try:
        out = P.predict(i0, acts, c)
        shape_ok = isinstance(out, list) and len(out) == len(acts) and all(
            isinstance(r, dict) and all(n in r for n in names) for r in out)
        finite = shape_ok and all(math.isfinite(float(r[n])) for r in out for n in names)
        malformed[label] = 'ok' if finite else 'non-finite values (warning)' if shape_ok else 'bad output'
    except Exception as e:
        malformed[label] = f'raised {e!r}'
print(json.dumps({'import_s': t_import, 'run_s': t_run, 'errors': errors[:20], 'n_errors': len(errors),
                  'deterministic': deterministic, 'malformed': malformed, 'min': lo, 'max': hi}))
'''


def check_imports(folder):
    """Top-level imports of every .py file must be stdlib, numpy/scipy/sklearn/joblib, or local files."""
    local = {p.stem for p in Path(folder).glob('*.py')}
    bad = []
    for path in Path(folder).rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.module and node.level == 0 else []
            for mod in mods:
                top = mod.split('.')[0]
                if top not in sys.stdlib_module_names and top not in ALLOWED_THIRD_PARTY and top not in local:
                    bad.append(f'{path.name}: {mod}')
    return bad


def contract(folder, system, episodes=40, steps=4000, seed=1, time_limit=300.0, data_eps=()):
    folder = Path(folder).resolve()
    info = core.brief_info(system)
    names, bounds = info['observables'], info['bounds']
    rng = np.random.default_rng(seed)
    init_ranges = core.initial_ranges(system, data_eps, names)
    kinds = ('holds', 'switch', 'extremes', 'uniform', 'mixed')
    payload = {'context': info['context'], 'observables': names,
               'episodes': [{'initial': core.random_initial(init_ranges, rng, widen=0.0),
                             'actions': core.random_schedule(bounds, steps, kinds[k % 5], rng, info['recovery'], info['pulse'])}
                            for k in range(episodes)]}
    result = {'folder': str(folder), 'system': system, 'bad_imports': check_imports(folder),
              'files': sorted(p.name for p in folder.iterdir())}
    required = {'predict.py'}
    result['missing_files'] = sorted(required - set(result['files']))
    with tempfile.TemporaryDirectory() as tmp:
        payload_path = Path(tmp) / 'payload.json'
        payload_path.write_text(json.dumps(payload))
        started = time.time()
        proc = subprocess.run([sys.executable, '-I', '-B', '-c', CHILD, str(folder), str(payload_path)], cwd=tmp,
                              capture_output=True, text=True, timeout=max(1200, time_limit * 2))
        result['wall_s'] = time.time() - started
    if proc.returncode != 0:
        result.update(child_error=proc.stderr[-3000:], **{'pass': False})
        return result
    child = json.loads(proc.stdout.strip().splitlines()[-1])
    result.update(child)
    result['pass'] = bool(not child['n_errors'] and child['deterministic'] and not result['bad_imports']
                          and not result['missing_files'] and all(v == 'ok' or v.endswith('(warning)') for v in child['malformed'].values())
                          and result['wall_s'] < time_limit)
    return result


# ----------------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description='Gates before packaging.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('score')
    s.add_argument('--model', required=True)
    s.add_argument('--params', required=True)
    s.add_argument('--data', nargs='+', required=True)
    s.add_argument('--ref', nargs='*', help='data defining sigma = 0.1 x std after tick 20 (default: --data)')
    s.add_argument('--start', type=int, default=0, help='score ticks >= start only')
    st = sub.add_parser('stability')
    st.add_argument('--model', required=True)
    st.add_argument('--params', required=True)
    st.add_argument('--system')
    st.add_argument('--data', nargs='*', default=[])
    st.add_argument('--n', type=int, default=200)
    st.add_argument('--n-long', type=int, default=8)
    st.add_argument('--steps', type=int, default=4000)
    st.add_argument('--long-steps', type=int, default=40000)
    st.add_argument('--range', default='', help='obs=lo:hi,... plausible-range overrides')
    st.add_argument('--seed', type=int, default=0)
    c = sub.add_parser('contract')
    c.add_argument('folder')
    c.add_argument('--system', required=True)
    c.add_argument('--episodes', type=int, default=40)
    c.add_argument('--steps', type=int, default=4000)
    c.add_argument('--data', nargs='*', default=[], help='data files to widen initial ranges (default: docs ranges)')
    for p in (s, st, c):
        p.add_argument('--out', type=Path)
    args = ap.parse_args(argv)

    if args.cmd == 'score':
        model = core.load_model(args.model)
        eps = core.load_episodes(args.data, model=model)
        ref = core.load_episodes(args.ref, names=eps[0]['names']) if args.ref else None
        result = local_score(model, load_params(args.params), eps, ref, start=args.start)
    elif args.cmd == 'stability':
        model = core.load_model(args.model)
        eps = core.load_episodes(args.data, model=model) if args.data else []
        overrides = {k: [float(v) for v in r.split(':')] for k, r in (i.split('=') for i in args.range.split(',') if i)}
        result = stability(model, load_params(args.params), args.system, eps, args.n, args.n_long, args.steps,
                           args.long_steps, args.seed, overrides)
    else:
        eps = core.load_episodes(args.data) if args.data else []
        result = contract(args.folder, args.system, args.episodes, args.steps, data_eps=eps)
    text = json.dumps(result, indent=1, default=core._json_default)
    print(text)
    if args.out:
        core.write_json(args.out, result)
    return result


if __name__ == '__main__':
    main()
