import json, os, numpy as np
D='fits/supply_chain/round2/v2'
def row(tag, mode, runs):
    p=f'{D}/{tag}_{mode}.json'
    if not os.path.exists(p): return None
    s=json.load(open(p))['scores']; v=np.array([s[r] for r in runs])
    return v.mean(0).round(3).tolist(), round(float(v.mean()),3)
v1=json.load(open('fits/round2/heldout_v1_supply_chain.json'))['runs']
print('v1 shipped A(R4,R5):', np.array([v1[r]['model'] for r in ['R4','R5']]).mean(0).round(3).tolist())
for tag in ["v1r_ls","v2","v2c"]:
    print(tag,'A', row(tag,'A',['R4','R5']), 'B4', row(tag,'B4',['R4']), 'B5', row(tag,'B5',['R5']),
          'C-all', row(tag,'C',['R1','R2','R3','R4','R5']), 'C-old', row(tag,'C',['R1','R2','R3']), 'A-old(in-sample)', row(tag,'A',['R1','R2','R3']))
