#!/bin/sh
# usage: job3.sh NAME MODEL MODULES INIT SPLIT [extra args]
# splits: H = R1-R5 (no round 3), B4 = all but R4, B5 = all but R5, C = R1-R6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
name=$1; model=$2; mods=$3; init=$4; split=$5; shift 5
d=data/social_contagion
case $split in
 H) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R4.json $d/R5.json";;
 B4) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R5.json $d/R6.json";;
 B5) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R4.json $d/R6.json";;
 C) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R4.json $d/R5.json $d/R6.json";;
esac
o=fits/social_contagion/round3
python -m greybox.common.fit --model $model --data $DATA --modules "$mods" --init $init --restarts ${RESTARTS:-2} --workers 1 --max-nfev 400 "$@" --out $o/${name}_${split}.json > $o/${name}_${split}.log 2>&1
