#!/bin/sh
# Round-3 screening fits on all data (1 CPU, sequential). Run from KIT.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
D=data/ad_auction; F=fits/ad_auction/round3; V2=fits/ad_auction/round2/v2/final_v2.json; M3=greybox/ad_auction_model_v3.py
AD="$D/R1.json $D/R2c.json $D/R3.json $D/R4.json $D/R5.json"
until grep -q '^done' $F/v2r_all.log 2>/dev/null; do sleep 5; done
python $F/fitdrv3.py fz,m1,m2,m3 $F/v3m1_all.json 1 $AD --model $M3 --init $V2,$F/init_m1.json --fix qx=20,a_m3=0.005 > $F/v3m1_all.log 2>&1
python $F/fitdrv3.py fz,m2,m3,zs $F/v3zs_all.json 1 $AD --model $M3 --init $V2,$F/init_zs.json --fix qx=20,a_m3=0.005 > $F/v3zs_all.log 2>&1
echo queue2 done
