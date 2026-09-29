#!/bin/sh
# Sequential round-3 fits (1 CPU each). Run from KIT.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
D=data/ad_auction; F=fits/ad_auction/round3; V2=fits/ad_auction/round2/v2/final_v2.json
until grep -q '^done' $F/v2r_all.log 2>/dev/null; do sleep 5; done
run() { out=$1; shift; python $F/fitdrv3.py "$@" > $F/$out.log 2>&1; }
# v3 (zs on) (H): fit without R5
run v3_noR5 fz,m2,m3,zs $F/v3_noR5.json 1 $D/R1.json $D/R2c.json $D/R3.json $D/R4.json --model greybox/ad_auction_model_v3.py --init $V2 --fix qx=20,a_m3=0.005
# v3 all data
run v3_all fz,m2,m3,zs $F/v3_all.json 2 $D/R1.json $D/R2c.json $D/R3.json $D/R4.json $D/R5.json --model greybox/ad_auction_model_v3.py --init $V2 --fix qx=20,a_m3=0.005
echo queue1 done
