#!/bin/bash
# Sequential fits (one process at a time). Run from KIT.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
F=fits/traffic/round3; V2=greybox/traffic_model_v2.py; V3=greybox/traffic_model_v3.py
python $F/trfit.py --model $V3 --init fits/traffic/final_v2.json --data R1 R2 R3 R4 R5 --out $F/H_v3.json --pw 4000 --lsq 100 > $F/H_v3.log 2>&1
python $F/trfit.py --model $V3 --init fits/traffic/final_v2.json --data R1 R2 R3 R4 R5 R6 --out $F/C_v3.json --pw 4000 --lsq 100 > $F/C_v3.log 2>&1
python $F/trfit.py --model $V2 --init fits/traffic/round2/v2/B4_v2_ld3.json --data R1 R2 R3 R5 R6 --out $F/B4_v2r.json --pw 3000 --lsq 60 > $F/B4_v2r.log 2>&1
python $F/trfit.py --model $V2 --init fits/traffic/round2/v2/B5_v2_ld3.json --data R1 R2 R3 R4 R6 --out $F/B5_v2r.json --pw 3000 --lsq 60 > $F/B5_v2r.log 2>&1
python $F/trfit.py --model $V3 --init fits/traffic/round2/v2/B4_v2_ld3.json --data R1 R2 R3 R5 R6 --out $F/B4_v3.json --pw 3000 --lsq 60 > $F/B4_v3.log 2>&1
python $F/trfit.py --model $V3 --init fits/traffic/round2/v2/B5_v2_ld3.json --data R1 R2 R3 R4 R6 --out $F/B5_v3.json --pw 3000 --lsq 60 > $F/B5_v3.log 2>&1
echo QUEUE1 DONE
