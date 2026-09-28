#!/bin/bash
# usage: [FIX=a,b SET=k=v MODS=m1,m2,urg] queue.sh MODEL INIT TAG FILES...   (one refit2 fit; FILES are run names)
M=$1; I=$2; T=$3; shift 3; D=fits/hospital_queue/round2/v2
DATA=""; for r in "$@"; do DATA="$DATA data/hospital_queue/$r.json"; done
python3 fits/hospital_queue/refit2.py --model $M --modules ${MODS:-m1,m2,urg} --init $I --data $DATA --rounds ${ROUNDS:-2} --nfev ${NFEV:-60} --starts ${STARTS:-1} --fix "${FIX:-}" --set "${SET:-}" --out $D/$T.json > $D/$T.log 2>&1
