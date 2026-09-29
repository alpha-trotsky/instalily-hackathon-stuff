#!/bin/sh
# Sequential round-3 fits (one process at a time). Run from toronto26-participant-kit/.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
F=fits/wildlife/round3; L=$F/logs; V2=greybox/wildlife_model_v2.py; V3=greybox/wildlife_model_v3.py
OV='{"qC": 4.0, "cY": 0.15}'
until [ -f $F/H_v3.json ]; do sleep 10; done
python -u $F/fit3.py --model $V3 --train R1 R2c R3 R4c --init $F/H_v3.json --restarts 1 --out $F/C_v3.json > $L/C_v3.log 2>&1
python -u $F/fit3.py --model $V2 --train R1 R2c R4c --test R3 --init fits/wildlife/round2/v2/B3_v2.json --restarts 1 --out $F/B3_v2r.json > $L/B3_v2r.log 2>&1
python -u $F/fit3.py --model $V3 --train R1 R2c R4c --test R3 --init fits/wildlife/round2/v2/B3_v2.json --override "$OV" --restarts 1 --out $F/B3_v3.json > $L/B3_v3.log 2>&1
python -u $F/fit3.py --model $V3 --train R1 R2c R3 --test R4 --init fits/wildlife/round2/v2/B4_v2.json --override "$OV" --restarts 1 --out $F/B4_v3.json > $L/B4_v3.log 2>&1
echo CHAIN DONE
