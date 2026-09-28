#!/bin/bash
# B folds restarted from the honest old-only v2 fit (v2_a); C variant with a saturating crowding term (small Kz)
Q=fits/hospital_queue/round2/v2/queue.sh; M=greybox/hospital_queue_model_v2.py; D=fits/hospital_queue/round2/v2
( bash $Q $M $D/v2_a.json v2_b2_r4 R1 R2c R3; bash $Q $M $D/v2_a.json v2_b2_r3 R1 R2c R4 ) &
( env SET=Kz=20,wd=0.45,az=0.05 bash $Q $M $D/np_c.json kz_c R1 R2c R3 R4; env SET=Kz=20,wd=0.45,az=0.05 bash $Q $M $D/v2_a.json kz_a R1 R2c ) &
wait
echo BATCH4 DONE
