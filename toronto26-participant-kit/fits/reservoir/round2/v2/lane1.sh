#!/bin/sh
until grep -q "saved\|Error" fits/reservoir/round2/v2/C_v1.log; do sleep 10; done
F="python3 -m greybox.common.fit --model greybox/reservoir_model.py --modules m1,m3 --restarts 1 --workers 1 --init fits/reservoir/v1/final.json"
$F --data data/reservoir/R1.json data/reservoir/R2.json data/reservoir/R3.json data/reservoir/R5.json --max-nfev 100 --out fits/reservoir/round2/v2/B4_v1.json > fits/reservoir/round2/v2/B4_v1.log 2>&1
$F --data data/reservoir/R1.json data/reservoir/R2.json data/reservoir/R3.json data/reservoir/R4.json --max-nfev 100 --out fits/reservoir/round2/v2/B5_v1.json > fits/reservoir/round2/v2/B5_v1.log 2>&1
