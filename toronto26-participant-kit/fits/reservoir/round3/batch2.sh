#!/bin/sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
X="python fits/reservoir/round3/fitx.py"; D=fits/reservoir/round3; L=$D/logs
B=m1,m3,reset,conv,lz; M2=greybox/reservoir_model_v2.py; M3=greybox/reservoir_model_v3.py
OLD="R1 R2 R3"; R3="R6XD R7XS"
echo H_S1; $X $M3 $B,lag,dep $D/init_H.json $D/H_S1.json 100 $OLD R4 R5
echo H_S2; $X $M3 $B,lag,lay $D/init_H.json $D/H_S2.json 100 $OLD R4 R5
echo C_S1; $X $M3 $B,lag,dep $D/q_lagdep_s1.json $D/C_S1.json 100 $OLD R4 R5 $R3
echo C_S2; $X $M3 $B,lag,lay $D/q_laglay_s1.json $D/C_S2.json 100 $OLD R4 R5 $R3
echo BATCH2 DONE
