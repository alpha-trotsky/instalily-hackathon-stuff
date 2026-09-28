#!/bin/bash
# honest validation of the clean v2 (no pool): every start comes from initA (v1's old-data-only fit), never from a fit
# that saw the scored run.
Q=fits/hospital_queue/round2/v2/queue.sh; M=greybox/hospital_queue_model_v2.py; D=fits/hospital_queue/round2/v2
( env STARTS=3 bash $Q $M $D/initA.json v2_a R1 R2c ) &
( bash $Q $M $D/initA.json v2_b_r4 R1 R2c R3; bash $Q $M $D/initA.json v2_b_r3 R1 R2c R4 ) &
wait
echo BATCH3 DONE
