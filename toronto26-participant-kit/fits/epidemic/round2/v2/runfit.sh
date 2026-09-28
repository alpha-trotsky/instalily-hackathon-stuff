#!/bin/bash
# usage: runfit.sh NAME DATA(R1,R2,...) INIT FIX UNITS [NFEV] [MODULES] [MODEL]
# UNITS: log (sigma 0.01) | lin (sigma = score sigma 8.41 cases, 4.31 beds)
cd "$(dirname "$0")/../../../.."
N=$1; DATA=$2; INIT=$3; FIX=$4; U=$5; NFEV=${6:-500}; MODS=${7:-m1,m2}; MODEL=${8:-greybox/epidemic_model_v2.py}
F=fits/epidemic/round2/v2
files=""; for r in ${DATA//,/ }; do files="$files data/epidemic/$r.json"; done
if [ "$U" = lin ]; then UN="--units linear --noise daily_cases=8.41,hospital_load=4.31"; else UN="--units log --noise 0.01"; fi
FX=""; [ -n "$FIX" ] && FX="--fix $FIX"
python3 -m greybox.common.fit --model $MODEL --data $files --modules $MODS --init $F/$INIT $FX $UN \
  --restarts 1 --workers 1 --max-nfev $NFEV --out $F/$N.json > $F/$N.log 2>&1
python3 $F/ev.py --model $MODEL $F/$N.json >> $F/results.txt
