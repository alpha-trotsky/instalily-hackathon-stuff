import sys; sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run
import json
def lerp(R,P,u): return {k: R[k]+u*(P[k]-R[k]) for k in R}
R={'clearance_effort':1.0,'freight_priority':0.5,'lane_closure':0.0,'ramp_metering':0.0,'signal_timing':0.5,'toll':5.0}
P={'clearance_effort':0.0,'freight_priority':1.0,'lane_closure':0.65,'ramp_metering':1.0,'signal_timing':0.15,'toll':0.0}
def W(**k): d=dict(R); d.update(k); return d
D=W(ramp_metering=1.0)
sch={
 'TR-1 spacing':[dict(steps=50,action=lerp(R,P,.7),label='u.7 t0-49'),dict(steps=100,action=lerp(R,P,.7),label='u.7 t50-149'),dict(steps=50,action=R,label='rec 50'),
   dict(steps=80,action=P,label='u1'),dict(steps=30,action=R,label='rec 30'),dict(steps=90,action=lerp(R,P,.85),label='u.85')],
 'TR-2 mid singles on D':[dict(steps=50,action=D,label='D ramp1 toll5'),dict(steps=50,action=W(ramp_metering=1.0,freight_priority=0.0),label='freight 0'),
   dict(steps=50,action=W(ramp_metering=1.0,signal_timing=0.3),label='signal .3'),dict(steps=50,action=W(ramp_metering=1.0,lane_closure=0.5,clearance_effort=0.5),label='lane .5 clear .5'),
   dict(steps=50,action=W(ramp_metering=1.0,toll=1.5),label='toll 1.5')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')],
 'u.85 3000':[dict(steps=3000,action=lerp(R,P,.85),label='u.85')]}
b='fits/traffic/'
run('traffic','greybox/traffic_model.py',[b+'final_v1.json',b+'v1/m12_allw.json',b+'v1/m13_allw.json',b+'v1/m23_allw.json'],sch,
    ['data/traffic/R1.json','data/traffic/R2.json','data/traffic/R3.json'])
