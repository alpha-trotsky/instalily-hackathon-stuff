#!/bin/bash
# v3 (residual floor) staged fits: s1 = floor params only on a fixed v2 base, s2 = all free from s1.
# C all data; H = fit old+R4 (no R4c); B folds leave R3 / R4 out. v2rm_b_r3 = v2 structure masked fold (R3 left out).
Q=fits/hospital_queue/round3/q3.sh; D=fits/hospital_queue/round3; V2=fits/hospital_queue/round2/v2
M3=greybox/hospital_queue_model_v3.py; M2=greybox/hospital_queue_model_v2.py
BASE=Ae,wo,wd,az,Kz,ca,ct,Ca,Cb,Wmax,theta,kw,gw,wu,a1u,a1d,g1,a2,g2
mk() { python -c "
import json;p=json.load(open('$1'))['params'];p.update(Rmax=75,fr=0.05,the=0.0008,ko=0.1);json.dump({'params':p},open('$2','w'),indent=1)"; }
(
  FIX=$BASE bash $Q $M3 $D/init_v3f.json v3_c_s1 R1 R2c R3 R4c; bash $Q $M3 $D/v3_c_s1.json v3_c R1 R2c R3 R4c
  bash $Q $M2 $V2/v2_b2_r3.json v2rm_b_r3 R1 R2c R4c; mk $D/v2rm_b_r3.json $D/init_b_r3.json
  FIX=$BASE bash $Q $M3 $D/init_b_r3.json v3_b_r3_s1 R1 R2c R4c; bash $Q $M3 $D/v3_b_r3_s1.json v3_b_r3 R1 R2c R4c
) &
(
  mk $V2/v2_c.json $D/init_h.json
  FIX=$BASE bash $Q $M3 $D/init_h.json v3_h_s1 R1 R2c R3 R4; bash $Q $M3 $D/v3_h_s1.json v3_h R1 R2c R3 R4
  mk $V2/v2_b2_r4.json $D/init_b_r4.json
  FIX=$BASE bash $Q $M3 $D/init_b_r4.json v3_b_r4_s1 R1 R2c R3; bash $Q $M3 $D/v3_b_r4_s1.json v3_b_r4 R1 R2c R3
) &
wait; echo BATCH2 DONE
