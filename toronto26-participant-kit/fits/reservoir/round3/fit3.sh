#!/bin/sh
# usage: fit3.sh TAG MODEL MODULES INIT NFEV1 NFEV2 RUNS...   (staged: quality-only with water fixed, then all; NFEV1=0 skips stage 1)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
TAG=$1; MODEL=$2; MODS=$3; INIT=$4; N1=$5; N2=$6; shift 6
DATA=""; for r in "$@"; do DATA="$DATA data/reservoir/$r.json"; done
D=fits/reservoir/round3
WATER=Vs,e0,e1,qmax,beta,a1,g1,th1,g1s,af1,gf1,H0,b1,gr,Hr,rho
if [ "$N1" != "0" ]; then
python -m greybox.common.fit --model $MODEL --data $DATA --modules $MODS --init $INIT --fix $WATER \
  --restarts 1 --workers 1 --max-nfev $N1 --out $D/${TAG}_s1.json > $D/logs/${TAG}_s1.log 2>&1
INIT=$D/${TAG}_s1.json
fi
if [ "$N2" != "0" ]; then
python -m greybox.common.fit --model $MODEL --data $DATA --modules $MODS --init $INIT \
  --restarts 1 --workers 1 --max-nfev $N2 --out $D/${TAG}.json > $D/logs/${TAG}.log 2>&1
else cp $D/${TAG}_s1.json $D/${TAG}.json; fi
tail -2 $D/logs/${TAG}*.log
