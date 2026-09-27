#!/bin/sh
# chain.sh MODULES NAME DATA...: fit MODULES from base_r1c_init, then 2 refinement passes from the best
mods=$1; name=$2; shift 2
out=fits/supply_chain/$name.json
python -m greybox.common.fit --model greybox/supply_chain_model.py --data "$@" --modules $mods --init fits/supply_chain/base_r1c_init.json --restarts 2 --workers 2 --perturb 0.02 --max-nfev 800 --out $out
for i in 1 2; do
  python -m greybox.common.fit --model greybox/supply_chain_model.py --data "$@" --modules $mods --init $out --restarts 2 --workers 2 --perturb 0.03 --seed $i --max-nfev 800 --out ${out%.json}_t.json
  python -c "
import json,shutil
a=json.load(open('$out'));b=json.load(open('${out%.json}_t.json'))
if b['cost']<a['cost']: shutil.copy('${out%.json}_t.json','$out')
print('best', min(a['cost'],b['cost']))"
done
