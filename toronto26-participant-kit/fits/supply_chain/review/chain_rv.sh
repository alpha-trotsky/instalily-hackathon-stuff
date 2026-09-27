#!/bin/sh
# chain_rv.sh MODEL MODULES OUT INIT: 3 chained passes (2 restarts each, 1 worker), keep best
model=$1; mods=$2; out=$3; init=$4
D="data/supply_chain/R1.json data/supply_chain/R2.json"
python -m greybox.common.fit --model $model --data $D --modules $mods --init $init --restarts 2 --workers 1 --perturb 0.02 --max-nfev 800 --out $out
for i in 1 2 3; do
  python -m greybox.common.fit --model $model --data $D --modules $mods --init $out --restarts 2 --workers 1 --perturb 0.03 --seed $i --max-nfev 800 --out ${out%.json}_t.json
  python -c "
import json,shutil
a=json.load(open('$out'));b=json.load(open('${out%.json}_t.json'))
if b['cost']<a['cost']: shutil.copy('${out%.json}_t.json','$out')
print('best', min(a['cost'],b['cost']))"
done
