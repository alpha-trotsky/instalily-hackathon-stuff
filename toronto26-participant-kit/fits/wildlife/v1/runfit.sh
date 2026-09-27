#!/bin/bash
mods=$1; data=${2//#/ }; out=$3; init=$4
cd "C:/Users/Belia/OneDrive/Documents/GitHub/instalily-hackathon-stuff/toronto26-participant-kit"
extra=""; [ "$init" != "init_none" ] && extra="--init fits/wildlife/v1/$init.json"
ev=""; [[ "$out" == *_r1 ]] && ev="--eval data/wildlife/R2c.json"
python -m greybox.common.fit --model greybox/wildlife_model.py --data $data --modules ${mods/none/} --restarts 1 --workers 1 --max-nfev ${NFEV:-300} $extra $ev --out fits/wildlife/v1/$out.json > fits/wildlife/v1/$out.log 2>&1
echo done $out
