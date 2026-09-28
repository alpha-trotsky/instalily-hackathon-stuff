"""Steady levels over 4,000 ticks from reset for recovery, joint u=0.7, u=1 (and single controls at u=1).
python3 fits/power_grid/round2/v2_levels.py FIT"""
import sys,json; sys.path.insert(0,'.')
import numpy as np
from greybox.common import core
r=json.load(open(sys.argv[1])); m=core.load_model(r['model']); p=r['params']
B={'price_signal':[0,2],'reserve_dispatch':[0,150],'charging_allowance':[0,1],'interconnector':[0,1]}
def act(u, which=('p','r','c','x')):
    return {'price_signal':1.5*(1-u) if 'p' in which else 1.5,'reserve_dispatch':150*u if 'r' in which else 0,
            'charging_allowance':1-u if 'c' in which else 1,'interconnector':1-0.8*u if 'x' in which else 1}
ini={'load':105,'frequency':50.0,'renewable_share':0.3}
for lab,a in [('recovery',act(0)),('joint .7',act(.7)),('joint 1',act(1)),('price 0',act(1,'p')),('reserve 150',act(1,'r')),('ic .2',act(1,'x')),('price 2',dict(act(0),price_signal=2.0))]:
    y=np.asarray(m.simulate(p,ini,[m.normalize(a,B)]*4000))
    print(f'{lab:12s} t100 {np.round(y[90:100].mean(0),3)}  t400 {np.round(y[390:400].mean(0),3)}  t3990 {np.round(y[3990:].mean(0),3)}  range last 1000 L {y[3000:,0].min():.1f}-{y[3000:,0].max():.1f} finite {np.isfinite(y).all()}')
