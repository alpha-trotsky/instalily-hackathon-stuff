#!/bin/bash
# (B) folds: leave out R4 / R5 (round-2 runs), fit on everything else incl. R6. Two at a time.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
F=fits/traffic/round3; V2=greybox/traffic_model_v2.py; V3=greybox/traffic_model_v3.py
ONLY="kg_B c_A c_B wl_A wl_B wle_A wle_B wc_A wc_B e_A e_B ke Emax kf sp_A sp_B qmax_A pce h1 sg_A be_A"
python $F/trfit.py --model $V3 --init fits/traffic/round2/v2/B4_v2_ld3.json --data R1 R2 R3 R5 R6 --out $F/B4_v3s1.json --pw 2000 --lsq 30 --fix kg=200 --only $ONLY > $F/B4_v3s1.log 2>&1 &
python $F/trfit.py --model $V3 --init fits/traffic/round2/v2/B5_v2_ld3.json --data R1 R2 R3 R4 R6 --out $F/B5_v3s1.json --pw 2000 --lsq 30 --fix kg=200 --only $ONLY > $F/B5_v3s1.log 2>&1
wait
python $F/trfit.py --model $V2 --init fits/traffic/round2/v2/B4_v2_ld3.json --data R1 R2 R3 R5 R6 --out $F/B4_v2r.json --pw 2000 --lsq 30 > $F/B4_v2r.log 2>&1 &
python $F/trfit.py --model $V2 --init fits/traffic/round2/v2/B5_v2_ld3.json --data R1 R2 R3 R4 R6 --out $F/B5_v2r.json --pw 2000 --lsq 30 > $F/B5_v2r.log 2>&1
wait
echo QUEUE_B DONE
