#!/bin/bash
# usage: [FIX=a,b SET=k=v MODS=m1,m2,urg STARTS=n NFEV=n ROUNDS=n] q3.sh MODEL INIT TAG FILES...  (one refit2 fit, round-3 dir)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M=$1; I=$2; T=$3; shift 3; D=fits/hospital_queue/round3
DATA=""; for r in "$@"; do DATA="$DATA data/hospital_queue/$r.json"; done
python fits/hospital_queue/round3/refit3.py --model $M --modules ${MODS:-m1,m2,urg} --init $I --data $DATA --rounds ${ROUNDS:-2} --nfev ${NFEV:-60} --starts ${STARTS:-1} --fix "${FIX:-}" --set "${SET:-}" --out $D/$T.json > $D/$T.log 2>&1
