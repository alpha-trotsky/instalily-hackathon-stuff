"""Build models/<system>/ and submission-<system>-<version>.zip, then re-test from the extracted ZIP.

    python -m greybox.common.package --system epidemic --model greybox/epidemic_model.py \
        --params fits/epidemic/final.json [--version v1] [--clamp daily_cases=0:1e5] [--dry-run]
    python -m greybox.common.package --all-zip submission-overnight-all.zip --folders models/epidemic models/market ...

Steps: copy the model module (as its own file name) + generic predict.py (predict_template.py) + params.json
into models/<system>/ (the folder is replaced), zip it with <system>/ at the ZIP root (no models/ prefix,
no __pycache__), extract to a temp dir, run the contract gate on the extracted copy, and scan every file
in the ZIP for the credential values in ../app-141-1d2abb-credentials.json (never printed). A failed check
deletes the ZIP. --dry-run writes the folder and ZIP to a temp directory instead of the kit.
Refuses to write models/market or submission-market-*.zip in the kit.

params.json fields read by predict.py: system, model_file, observables, bounds, recovery, clamp, fallback,
params. clamp: model CLAMP if defined, else [0 (or min - range if data go negative), 10 x max observed];
override with --clamp obs=lo:hi.
"""
import argparse
import importlib.util
import json
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
import numpy as np

from greybox.common import core, gates

CREDENTIALS = core.KIT.parent / 'app-141-1d2abb-credentials.json'
TEMPLATE = Path(__file__).with_name('predict_template.py')
PROTECTED_SYSTEMS = {'market'}


def _secrets():
    if not CREDENTIALS.exists():
        return None
    data = json.loads(CREDENTIALS.read_text())
    return [str(data[k]).encode() for k in ('gateway_key', 'portal_credential') if data.get(k)]


def scan_zip(zip_path):
    """True if no credential value appears in any ZIP entry; None if no credentials file exists."""
    secrets = _secrets()
    if secrets is None:
        return None
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            blob = zf.read(name)
            if any(s and s in blob for s in secrets):
                return False
    return True


def model_file(spec):
    if spec.endswith('.py') or '/' in spec or '\\' in spec:
        return Path(spec).resolve()
    found = importlib.util.find_spec(spec)
    return Path(found.origin).resolve()


def derive_clamp(model, names, episodes, init_ranges, overrides):
    clamp = {k: list(v) for k, v in (getattr(model, 'CLAMP', None) or {}).items()}
    for i, name in enumerate(names):
        if name in clamp:
            continue
        vals = np.concatenate([ep['obs'][:, i] for ep in episodes] + [np.array(init_ranges.get(name, [0.0, 1.0]), float)])
        lo, hi = float(vals.min()), float(vals.max())
        span = max(hi - lo, abs(hi), 1e-9)
        clamp[name] = [0.0 if lo >= 0 else lo - span, 10.0 * hi if hi > 0 else hi + span]
    clamp.update(overrides or {})
    return clamp


def build_folder(system, model_spec, params_path, folder, data_paths=(), clamp_overrides=None):
    model = core.load_model(model_spec)
    fit = json.loads(Path(params_path).read_text())
    params = fit['params'] if 'params' in fit else fit
    info = core.brief_info(system)
    names = core.observables(model, {'observables': info['observables']})
    episodes = core.load_episodes(data_paths, names=names) if data_paths else []
    init_ranges = core.initial_ranges(system, episodes, names)
    fallback = {n: (float(np.median(np.concatenate([ep['obs'][:, i] for ep in episodes]))) if episodes
                    else float(np.mean(init_ranges[n]))) for i, n in enumerate(names)}
    src = model_file(model_spec)
    cfg = {'system': system, 'model_file': src.name, 'observables': names, 'bounds': info['bounds'],
           'recovery': info['recovery'], 'clamp': derive_clamp(model, names, episodes, init_ranges, clamp_overrides),
           'fallback': fallback, 'modules': fit.get('modules'), 'source_fit': str(params_path),
           'built_at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'params': params}
    folder = Path(folder)
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    shutil.copyfile(src, folder / src.name)
    shutil.copyfile(TEMPLATE, folder / 'predict.py')
    (folder / 'params.json').write_text(json.dumps(cfg, indent=1, default=core._json_default))
    return cfg


def write_zip(folders, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder in folders:
            folder = Path(folder)
            for path in sorted(folder.rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                    zf.write(path, f'{folder.name}/{path.relative_to(folder).as_posix()}')


def verify_zip(zip_path, systems):
    """Extract, run the contract gate on every system folder, scan for credentials."""
    result = {'zip': str(zip_path), 'size_bytes': Path(zip_path).stat().st_size}
    with zipfile.ZipFile(zip_path) as zf:
        result['expanded_bytes'] = sum(i.file_size for i in zf.infolist())
        roots = {n.split('/')[0] for n in zf.namelist()}
    result['roots_ok'] = roots == set(systems)
    result['credential_scan'] = {True: 'clean', False: 'FOUND CREDENTIAL', None: 'skipped (no credentials file)'}[scan_zip(zip_path)]
    with tempfile.TemporaryDirectory() as tmp:
        zipfile.ZipFile(zip_path).extractall(tmp)
        result['contract'] = {}
        for system in systems:
            c = gates.contract(Path(tmp) / system, system)
            result['contract'][system] = {k: c.get(k) for k in ('pass', 'wall_s', 'n_errors', 'malformed', 'bad_imports', 'child_error')}
    result['pass'] = bool(result['roots_ok'] and result['credential_scan'] != 'FOUND CREDENTIAL'
                          and result['size_bytes'] < 30 * 2 ** 20 and result['expanded_bytes'] < 300 * 2 ** 20
                          and all(c['pass'] for c in result['contract'].values()))
    return result


def _guard(path, kit_models, kit_root):
    path = Path(path).resolve()
    for system in PROTECTED_SYSTEMS:
        if path == (kit_models / system).resolve() or (path.parent == kit_root.resolve() and path.name.startswith(f'submission-{system}-')):
            raise SystemExit(f'refusing to write {path}: {system} is protected')


def package(system, model_spec, params_path, version='v1', data_paths=None, clamp=None, dry_run=False, force=False):
    root = Path(tempfile.mkdtemp(prefix=f'package_{system}_')) if dry_run else core.KIT
    folder = root / 'models' / system
    zip_path = root / f'submission-{system}-{version}.zip'
    _guard(folder, core.KIT / 'models', core.KIT)
    _guard(zip_path, core.KIT / 'models', core.KIT)
    if zip_path.exists() and not force:
        raise SystemExit(f'{zip_path} exists; choose a new --version or pass --force')
    if data_paths is None:
        data_paths = sorted(str(p) for p in (core.KIT / 'data' / system).glob('*.json') if not p.stem.endswith('_battery'))
    cfg = build_folder(system, model_spec, params_path, folder, data_paths, clamp)
    write_zip([folder], zip_path)
    result = {'system': system, 'folder': str(folder), 'dry_run': dry_run, 'clamp': cfg['clamp'], **verify_zip(zip_path, [system])}
    if not result['pass']:
        zip_path.unlink()
        result['zip'] = None
        result['note'] = 'verification failed: ZIP deleted, folder kept for debugging'
    return result


def build_all_zip(folders, out, force=False):
    """Combined ZIP (e.g. submission-overnight-all.zip) of several system folders, verified like package()."""
    out = Path(out)
    if out.exists() and not force:
        raise SystemExit(f'{out} exists; pass --force to replace it')
    for folder in folders:
        if not (Path(folder) / 'predict.py').exists():
            raise SystemExit(f'{folder} has no predict.py')
    write_zip(folders, out)
    result = verify_zip(out, [Path(f).name for f in folders])
    if not result['pass']:
        out.unlink()
        result['zip'] = None
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description='Build and verify a submission folder and ZIP.')
    ap.add_argument('--system')
    ap.add_argument('--model', help='model module file or dotted name')
    ap.add_argument('--params', help='fit JSON with a "params" dict')
    ap.add_argument('--version', default='v1')
    ap.add_argument('--data', nargs='*', help='data files for clamp/fallback (default: data/<system>/*.json)')
    ap.add_argument('--clamp', default='', help='obs=lo:hi,... output clamp overrides')
    ap.add_argument('--dry-run', action='store_true', help='build in a temp directory instead of the kit')
    ap.add_argument('--force', action='store_true', help='replace an existing ZIP')
    ap.add_argument('--all-zip', help='build a combined ZIP from --folders instead')
    ap.add_argument('--folders', nargs='*', default=[])
    args = ap.parse_args(argv)
    if args.all_zip:
        result = build_all_zip(args.folders, args.all_zip, args.force)
    else:
        if not (args.system and args.model and args.params):
            ap.error('--system, --model and --params are required')
        clamp = {k: [float(v) for v in r.split(':')] for k, r in (i.split('=') for i in args.clamp.split(',') if i)}
        result = package(args.system, args.model, args.params, args.version, args.data, clamp, args.dry_run, args.force)
    print(json.dumps(result, indent=1, default=core._json_default))
    if not result['pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
