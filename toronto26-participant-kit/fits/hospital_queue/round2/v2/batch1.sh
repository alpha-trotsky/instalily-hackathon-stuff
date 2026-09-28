#!/bin/bash
# two lanes of fits (max 2 processes). np_* = elective pool switched off (Pmax ~ 0, pool params fixed)
Q=fits/hospital_queue/round2/v2/queue.sh; M=greybox/hospital_queue_model_v2.py; D=fits/hospital_queue/round2/v2
NP="env FIX=Pmax,Le,ce,the SET=Pmax=1e-9"
( bash $Q $M $D/c3.json a4 R1 R2c; $NP bash $Q $M $D/c3.json np_a R1 R2c; bash $Q $M $D/c3.json b4_r4 R1 R2c R3; $NP bash $Q $M $D/c3.json np_b_r4 R1 R2c R3 ) &
( $NP bash $Q $M $D/c3.json np_c R1 R2c R3 R4; bash $Q $M $D/c3.json b4_r3 R1 R2c R4; $NP bash $Q $M $D/c3.json np_b_r3 R1 R2c R4 ) &
wait
echo BATCH1 DONE
