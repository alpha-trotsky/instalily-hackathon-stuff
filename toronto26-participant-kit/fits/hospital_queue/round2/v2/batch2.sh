#!/bin/bash
# v1 structure refit baseline (no structure change): C all data, B folds. A for v1 = shipped v1 (fit on old only).
Q=fits/hospital_queue/round2/v2/queue.sh; M=greybox/hospital_queue_model.py; I=fits/hospital_queue/final_m12.json
( bash $Q $M $I v1r_c R1 R2c R3 R4 ) &
( bash $Q $M $I v1r_b_r4 R1 R2c R3; bash $Q $M $I v1r_b_r3 R1 R2c R4 ) &
wait
echo BATCH2 DONE
