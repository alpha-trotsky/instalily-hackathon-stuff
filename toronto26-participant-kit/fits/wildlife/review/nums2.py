import json, numpy as np
OBS=['prey_north','predator_north','prey_south','predator_south']
def load(f):
    r=json.load(open(f'data/wildlife/{f}.json'))['runs'][0]
    return np.array([[o[k] for k in OBS] for o in r['observations']]), r
Y1,_=load('R1'); Y2,_=load('R2')
def sm(Y,a,b): return np.round(Y[a:b].mean(0),2)
print('R1 segment means (last 10 of each seg)')
for a,b in [(110,120),(175,185),(240,250),(280,290),(320,330),(360,370),(430,440),(480,490),(530,540)]: print(' ',a,b,sm(Y1,a,b))
print('R2 segment ends')
for a,b in [(20,30),(45,55),(70,80),(95,105),(120,130),(145,155),(170,180),(190,200),(250,260),(300,310),(350,360),(390,400)]: print(' ',a,b,sm(Y2,a,b))
print('R1 hunt on 118-140 prey N', np.round(Y1[118:140,0],0))
print('R1 hunt off 183-262 prey N', np.round(Y1[183:262:2,0],0))
print('R1 hunt off 183-262 prey S', np.round(Y1[183:262:2,2],0))
print('R1 corr 326-440 N', np.round(Y1[326:440:3,0],0))
print('R1 corr 326-440 S', np.round(Y1[326:440:3,2],0))
print('R1 corr 326-440 pN', np.round(Y1[326:440:3,1],2))
print('R1 hab 246-330 N', np.round(Y1[246:330:2,0],0))
print('R1 hab 246-330 S', np.round(Y1[246:330:2,2],0))
print('R2 196-240 N',np.round(Y2[196:240,0],1))
