import json, numpy as np
OBS=['prey_north','predator_north','prey_south','predator_south']
def load(f):
    r=json.load(open(f'data/wildlife/{f}.json'))['runs'][0]
    return np.array([[o[k] for k in OBS] for o in r['observations']]), r
for f in ['R1','R2']:
    Y,r=load(f)
    print('==',f,'init',[round(r['initial'][k],1) for k in OBS])
    # noise: second-difference based sigma in windows
    d2=(Y[2:]-2*Y[1:-1]+Y[:-2])/np.sqrt(6)
    for w0,w1 in [(60,120),(150,185),(500,540),(300,400)]:
        if w1<=len(d2): 
            s=d2[w0:w1].std(0); m=Y[w0:w1].mean(0)
            print(f'  win {w0}-{w1} mean',np.round(m,2),'sig',np.round(s,3),'rel',np.round(s/m,4))
    print('  peak prey N t',Y[:60,0].argmax(),Y[:60,0].max().round(1),' prey S t',Y[:60,2].argmax(),Y[:60,2].max().round(1))
    print('  first 30 prey N', np.round(Y[:30,0],0))
    print('  first 30 pred N', np.round(Y[:30,1],2))
