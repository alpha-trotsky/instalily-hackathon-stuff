"""Simulate candidate fits on draft schedules; print end-of-segment levels and pairwise disagreement in score-sigma."""
import json, sys, re, numpy as np
sys.path.insert(0, '.')
from greybox.common import core


def load_params(p):
    d = json.load(open(p))
    return d['params'] if 'params' in d else d


def ranges_for(system):
    doc = json.load(open(f'docs/{system}.json'))
    docs = doc['documents']
    docs = docs['documents'] if isinstance(docs, dict) else docs
    txt = ' '.join(d['text'] for d in docs)
    m = re.search(r'ranges: (\{[^}]*\})', txt)
    return json.loads(m.group(1))


def run(system, model_spec, fits, schedules, datafiles, init=None, last=10):
    model = core.load_model(model_spec)
    eps = core.load_episodes(datafiles, model=model)
    names = eps[0]['names']
    bounds = eps[0]['bounds']
    sig = core.score_sigma(eps)
    rng = ranges_for(system)
    ini = init or {k: (v[0] + v[1]) / 2 for k, v in rng.items()}
    keys = [f.split('/')[-1].replace('.json', '') for f in fits]
    print(f'== {system}  obs={names}  sigma(0.1std)=', [round(float(s), 4) for s in sig])
    for sname, segs in schedules.items():
        acts, ends = [], []
        for sg in segs:
            acts += [sg['action']] * sg['steps']
            ends.append((len(acts), sg.get('label', '')))
        u = [model.normalize(a, bounds) for a in acts]
        preds = {f: core.rollout(model, load_params(f), {'u': u, 'initial': ini, 'names': names}) for f in fits}
        print(f'-- {sname} ({len(acts)} steps)')
        start = 0
        for end, lab in ends:
            row = [preds[f][max(start, end - last):end].mean(0) for f in fits]
            dis = 0.0
            if len(fits) > 1:
                dis = np.mean([np.mean(np.abs(preds[fits[i]][start:end] - preds[fits[j]][start:end]) / sig)
                               for i in range(len(fits)) for j in range(i + 1, len(fits))])
            print(f'  [{start:4d}-{end - 1:4d}] {lab:30s} dis={dis:5.2f}s | ' +
                  ' | '.join(k + ':' + ','.join(f'{v:.3g}' for v in r) for k, r in zip(keys, row)))
            start = end
