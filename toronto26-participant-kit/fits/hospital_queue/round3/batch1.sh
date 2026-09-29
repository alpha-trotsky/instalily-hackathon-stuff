#!/bin/bash
# (C) all-data fits: v2r (v2 structure) and v3 (elective pool). R4c replaces R4 (shared prefix).
Q=fits/hospital_queue/round3/q3.sh; D=fits/hospital_queue/round3; V2=fits/hospital_queue/round2/v2
( STARTS=2 bash $Q greybox/hospital_queue_model_v2.py $V2/v2_c.json v2r_c R1 R2c R3 R4c ) &
( STARTS=2 bash $Q greybox/hospital_queue_model_v3.py $D/init_v3.json v3_c R1 R2c R3 R4c ) &
wait; echo BATCH1 DONE
