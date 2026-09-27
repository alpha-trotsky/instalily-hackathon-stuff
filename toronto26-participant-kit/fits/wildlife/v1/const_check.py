"""Extra wildlife gate (review G3/G8): 4,000-step constant-action runs over a grid incl. over-pulse values,
plus the joint recovery-range pulse. Reports min tail prey/predators and tail range / mean (limit-cycle check)."""
import json, sys, itertools, numpy as np
sys.path.insert(0, '.')
from greybox.common import core
m = core.load_model(sys.argv[2] if len(sys.argv) > 2 else 'greybox/wildlife_model.py')
p = json.load(open(sys.argv[1]))['params']
bounds = {'hunting_quota': [0, 8], 'habitat_protection': [0, 1], 'corridor_access': [0, 1]}
worst_rng, worst_min, worst_minY, bad = 0, 1e9, 1e9, []
for q, h, c in itertools.product([0, 3.5, 6, 7, 8], [1, 0.55, 0.25, 0.1, 0], [0, 0.5, 0.9, 1]):
    a = {'hunting_quota': q, 'habitat_protection': h, 'corridor_access': c}
    u = [m.normalize(a, bounds)] * 4000
    y = np.asarray(m.simulate(p, {'prey_north': 85, 'predator_north': 11, 'prey_south': 85, 'predator_south': 11}, u))
    tail = y[-1000:]
    rng = ((tail.max(0) - tail.min(0)) / tail.mean(0)).max()
    worst_rng = max(worst_rng, rng); worst_min = min(worst_min, tail[:, [0, 2]].min()); worst_minY = min(worst_minY, tail[:, [1, 3]].min())
    if rng > 0.1 or tail[:, [0, 2]].min() < 1.0 or not np.isfinite(y).all():
        bad.append((q, h, c, round(float(rng), 3), round(float(tail[:, [0, 2]].min()), 2)))
print(json.dumps({'worst_tail_range_over_mean': round(float(worst_rng), 4), 'min_tail_prey': round(float(worst_min), 3),
                  'min_tail_pred': round(float(worst_minY), 3), 'n_bad': len(bad), 'bad': bad[:12],
                  'pass': not bad}))
