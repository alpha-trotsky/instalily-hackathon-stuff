"""History-dependence gate (diagnosis B31, item 5) + long-run level map. Free. Run from toronto26-participant-kit/:

    python3 fits/wildlife/round2/v2/history_gate.py --model greybox/wildlife_model_v2.py --params FIT.json

For each constant action A: simulate 3 different 200-tick prefixes (recovery, joint 1, habitat .1 + hunting 3)
then A until tick 4000, from a mid-range initial reading. PASS if the mean of ticks 3800-4000 agrees across
prefixes within 0.5 sigma (score sigma) on every observable. Also prints the long-run level map (ticks 3800-4000).
"""
import argparse, json, sys
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fits/round2')
import heldout
from greybox.common import core

BOUNDS = {'hunting_quota': [0.0, 8.0], 'habitat_protection': [0.0, 1.0], 'corridor_access': [0.0, 1.0]}
REC = {'hunting_quota': 0.0, 'habitat_protection': 1.0, 'corridor_access': 0.0}


def act(h=0.0, p=1.0, c=0.0):
    return {'hunting_quota': h, 'habitat_protection': p, 'corridor_access': c}


def joint(u):
    return act(7 * u, 1 - 0.9 * u, u)


ACTIONS = {'recovery': REC, 'hunt 3.5': act(3.5), 'hunt 5': act(5), 'hunt 7': act(7), 'hunt 8': act(8),
           'hab .37 (u.7)': act(p=0.37), 'hab .1': act(p=0.1), 'hab 0': act(p=0.0), 'corr .7': act(c=0.7),
           'corr 1': act(c=1), 'joint .7': joint(0.7), 'joint .85': joint(0.85), 'joint 1': joint(1.0),
           'hunt7+hab.1': act(7, 0.1), 'hunt8+hab0+corr1': act(8, 0.0, 1.0)}
PREFIXES = {'recovery': REC, 'joint 1': joint(1.0), 'hab.1+hunt3': act(3, 0.1)}
INIT = {'prey_north': 85.0, 'predator_north': 11.5, 'prey_south': 85.0, 'predator_south': 11.5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--params', required=True)
    ap.add_argument('--steps', type=int, default=4000)
    a = ap.parse_args()
    model = core.load_model(a.model)
    params = json.loads(open(a.params).read())['params']
    _, sig = heldout.sigma('wildlife')
    fails = []
    print(f"{'action':18s} {'long-run N/yN/S/yS (recovery prefix)':40s} max spread (sigma)")
    for name, A in ACTIONS.items():
        levels = []
        for pre in PREFIXES.values():
            acts = [pre] * 200 + [A] * (a.steps - 200)
            u = [model.normalize(x, BOUNDS) for x in acts]
            y = np.asarray(model.simulate(params, INIT, u))
            levels.append(y[-200:].mean(0))
            tail = y[-400:]
            if not np.all(np.isfinite(y)):
                fails.append((name, 'nonfinite'))
        L = np.array(levels)
        spread = (L.max(0) - L.min(0)) / sig
        osc = (tail.max(0) - tail.min(0)) / sig
        flag = 'FAIL' if spread.max() > 0.5 else 'ok'
        if flag == 'FAIL':
            fails.append((name, spread.round(2).tolist()))
        print(f"{name:18s} {str(np.round(L[0], 2).tolist()):40s} {spread.max():6.2f} {flag}  tail range {osc.max():.2f}sigma")
    print('HISTORY GATE', 'PASS' if not fails else f'FAIL {fails}')


if __name__ == '__main__':
    main()
