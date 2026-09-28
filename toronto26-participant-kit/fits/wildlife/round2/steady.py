"""v1 (AB_all3) settled levels (tick 1990-2000 of a constant hold from reset, and also at the data's hold length
after the same preceding state is NOT reproduced here) vs observed end-of-hold levels. python3 fits/wildlife/round2/steady.py"""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from greybox.common import core
m = core.load_model('greybox/wildlife_model.py')
p = json.load(open('fits/wildlife/v1/AB_all3.json'))['params']
names = ['prey_north', 'predator_north', 'prey_south', 'predator_south']
b = {'hunting_quota': (0, 8), 'habitat_protection': (0, 1), 'corridor_access': (0, 1)}
ini = {'prey_north': 85, 'predator_north': 11.5, 'prey_south': 85, 'predator_south': 11.5}
S = [('recovery', 0, 1, 0, 'R3 380-499: 121.3/2.34/96.8/2.33 (settled)'),
     ('hunt 7', 7, 1, 0, 'R2c 350-399: 25.5/1.90/11.4/1.86 (settled)'),
     ('hunt 5', 5, 1, 0, 'R4 0-79 from reset: 68.7/2.55/36.9/2.34 (not settled; asympt ~62/2.1/31/1.9)'),
     ('hunt 3.5', 3.5, 1, 0, 'R1 440-489: 86.7/2.32/62.1/2.26'),
     ('hab .37', 0, .37, 0, 'R4 140-199: 89.7/2.30/81.1/2.28 (falling 1.7/tick, post-release)'),
     ('hab .1', 0, .1, 0, 'R1 250-289: 67.5/2.34/64.7/2.33'),
     ('corr .7', 0, 1, .7, 'R4 260-319: 117.7/1.95/88.8/1.92'),
     ('corr 1', 0, 1, 1, 'R1 330-369: 109.9/1.69/76.1/1.64'),
     ('hab.37+corr.7', 0, .37, .7, 'R4 200-259: 77.0/1.96/70.6/1.91'),
     ('hunt5+hab.37', 5, .37, 0, 'R4 80-139: 23.5/2.09/16.7/1.97 (falling)'),
     ('joint .7', 4.9, .37, .7, 'R3 290-349: 28.4/1.94/24.7/1.83 (falling; asympt ~22)'),
     ('joint .85', 5.95, .235, .85, 'R3 0-79: 10.8/2.03/11.1/2.06 (preds falling)'),
     ('joint 1', 7, .1, 1, 'R3 200-259: 7.6/1.79/8.1/1.73 (falling)')]
for lab, h, pr, c, ref in S:
    a = {'hunting_quota': h, 'habitat_protection': pr, 'corridor_access': c}
    u = [m.normalize(a, b)] * 2000
    y = core.rollout(m, p, {'u': u, 'initial': ini, 'names': names})
    print(f'{lab:14s} v1@2000 {"/".join(f"{v:.3g}" for v in y[-10:].mean(0))} | v1@80 {"/".join(f"{v:.3g}" for v in y[70:80].mean(0))} | data {ref}')
