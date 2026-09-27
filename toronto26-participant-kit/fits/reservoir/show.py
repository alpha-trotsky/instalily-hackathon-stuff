import json, sys
d=json.load(open(sys.argv[1])); r=d['runs'][-1]; a=int(sys.argv[2]); b=int(sys.argv[3]) if len(sys.argv)>3 else len(r['observations'])
if a==0: print('initial', r['initial'])
for i in range(a,b):
    o=r['observations'][i]; print(i, ' '.join(f'{k[:3]}={v:.3f}' for k,v in o.items()))
