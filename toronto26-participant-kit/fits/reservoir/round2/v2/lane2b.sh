#!/bin/sh
F="python3 -m greybox.common.fit --model greybox/reservoir_model_v2.py --modules m1,m3,reset,conv,lz --restarts 1 --workers 1"
$F --data data/reservoir/R1.json data/reservoir/R2.json data/reservoir/R3.json --init fits/reservoir/round2/v2/init_A2.json --max-nfev 150 --out fits/reservoir/round2/v2/A2.json > fits/reservoir/round2/v2/A2.log 2>&1
$F --data data/reservoir/R1.json data/reservoir/R2.json data/reservoir/R3.json data/reservoir/R4.json data/reservoir/R5.json --init fits/reservoir/round2/v2/init_C2.json --max-nfev 150 --out fits/reservoir/round2/v2/C2.json > fits/reservoir/round2/v2/C2.log 2>&1
$F --data data/reservoir/R1.json data/reservoir/R2.json data/reservoir/R3.json data/reservoir/R5.json --init fits/reservoir/round2/v2/A2.json --max-nfev 100 --out fits/reservoir/round2/v2/B4_2.json > fits/reservoir/round2/v2/B4_2.log 2>&1
$F --data data/reservoir/R1.json data/reservoir/R2.json data/reservoir/R3.json data/reservoir/R4.json --init fits/reservoir/round2/v2/A2.json --max-nfev 100 --out fits/reservoir/round2/v2/B5_2.json > fits/reservoir/round2/v2/B5_2.log 2>&1
