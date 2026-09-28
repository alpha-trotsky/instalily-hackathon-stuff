#!/bin/sh
# usage: job.sh NAME MODEL MODULES INIT SPLIT [extra args]
name=$1; model=$2; mods=$3; init=$4; split=$5; shift 5
d=data/social_contagion
case $split in
 A) DATA="$d/R1.json $d/R2.json $d/R3.json";;
 B4) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R5.json";;
 B5) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R4.json";;
 C) DATA="$d/R1.json $d/R2.json $d/R3.json $d/R4.json $d/R5.json";;
esac
python3 -m greybox.common.fit --model $model --data $DATA --modules "$mods" --init $init --restarts 2 --workers 1 --max-nfev 400 "$@" --out fits/social_contagion/round2/v2/${name}_${split}.json > fits/social_contagion/round2/v2/${name}_${split}.log 2>&1
