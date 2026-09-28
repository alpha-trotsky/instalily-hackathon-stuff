"""Free: list every held setting in our data as (run, start, length, u per control), u=(v-rec)/(pulse-rec)."""
import json, re, sys
sys.path.insert(0, '.')
from greybox.common import core
FILES = {'epidemic':['R1','R2'],'wildlife':['R1','R2c'],'ad_auction':['R1','R2c'],'social_contagion':['R1','R2','R3'],
 'power_grid':['R1','R2c'],'reservoir':['R1','R2','R3'],'traffic':['R1','R2','R3'],'supply_chain':['R1','R2','R3'],
 'hospital_queue':['R1','R2c'],'market':['A']}
def refs(system):
    txt = open('briefs.md', encoding='utf-8').read().split(f'## {system}\n')[1].split('\n## ')[0]
    rec = json.loads(re.search(r'recovery action: `(\{.*?\})`', txt).group(1))
    pul = json.loads(re.search(r'pulse action: `(\{.*?\})`', txt).group(1))
    return rec, pul
for s in sys.argv[1:] or FILES:
    rec, pul = refs(s); keys = sorted(rec)
    print(f'=== {s}  controls={keys}  (u: 0=recovery, 1=pulse; raw value in brackets when u not in [0,1] or mixed)')
    for r in FILES[s]:
        for run in json.load(open(f'data/{s}/{r}.json'))['runs']:
            acts = run['actions']; i = 0
            while i < len(acts):
                j = i
                while j < len(acts) and acts[j] == acts[i]: j += 1
                a = acts[i]
                us = []
                for k in keys:
                    d = pul[k] - rec[k]; u = (a[k] - rec[k]) / d if d else 0
                    us.append(f'{u:.2f}')
                if j - i >= 10:
                    print(f'  {r:4s} t{i:4d} len{j-i:4d}  u=[' + ' '.join(us) + ']')
                i = j
