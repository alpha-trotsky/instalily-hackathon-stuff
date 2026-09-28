#!/bin/sh
# usage: fit2.sh TAG "DATA FILES" MODULES [MODEL] [INIT]  -> staged fit (quality-only, then all), 2 workers
TAG=$1; DATA=$2; MODS=$3; MODEL=${4:-greybox/reservoir_model_v2.py}; INIT=${5:-fits/reservoir/round2/v2/init_v2.json}
D=fits/reservoir/round2/v2
WATER=Vs,e0,e1,qmax,beta,a1,g1,th1,g1s,af1,gf1,H0,b1,gr,Hr,rho
python3 -m greybox.common.fit --model $MODEL --data $DATA --modules $MODS --init $INIT --fix $WATER \
  --restarts 1 --workers 1 --max-nfev 400 --out $D/${TAG}_s1.json > $D/${TAG}_s1.log 2>&1
python3 -m greybox.common.fit --model $MODEL --data $DATA --modules $MODS --init $D/${TAG}_s1.json \
  --restarts 1 --workers 1 --max-nfev 600 --out $D/${TAG}.json > $D/${TAG}.log 2>&1
tail -2 $D/${TAG}.log
