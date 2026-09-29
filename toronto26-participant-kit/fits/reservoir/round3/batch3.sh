#!/bin/sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
X="python fits/reservoir/round3/fitx.py"; D=fits/reservoir/round3
B=m1,m3,reset,conv,lz; M2=greybox/reservoir_model_v2.py; M3=greybox/reservoir_model_v3.py
OLD="R1 R2 R3"; R3="R6XD R7XS"
until grep -q "BATCH2 DONE" $D/logs/batch2.out; do sleep 5; done
echo B4_S0; $X $M2 $B $D/init_B4.json $D/B4_S0.json 100 $OLD R5 $R3
echo B4_S2; $X $M3 $B,lag,lay $D/init_B4.json $D/B4_S2.json 100 $OLD R5 $R3
echo B5_S0; $X $M2 $B $D/init_B5.json $D/B5_S0.json 100 $OLD R4 $R3
echo B5_S2; $X $M3 $B,lag,lay $D/init_B5.json $D/B5_S2.json 100 $OLD R4 $R3
echo B4_S1; $X $M3 $B,lag,dep $D/init_B4.json $D/B4_S1.json 100 $OLD R5 $R3
echo B5_S1; $X $M3 $B,lag,dep $D/init_B5.json $D/B5_S1.json 100 $OLD R4 $R3
echo BATCH3 DONE
