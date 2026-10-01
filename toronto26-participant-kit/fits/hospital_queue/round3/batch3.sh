#!/bin/bash
# extra (B) folds where the residual floor is exercised: leave R1 out / leave R2c out (starts from v2rm_c, which saw
# every run: equally leaky for v2r and v3).
Q=fits/hospital_queue/round3/q3.sh; D=fits/hospital_queue/round3
M3=greybox/hospital_queue_model_v3.py; M2=greybox/hospital_queue_model_v2.py
BASE=Ae,wo,wd,az,Kz,ca,ct,Ca,Cb,Wmax,theta,kw,gw,wu,a1u,a1d,g1,a2,g2
mk() { python -c "
import json;p=json.load(open('$1'))['params'];p.update(Rmax=75,fr=0.05,the=0.0008,ko=0.1);json.dump({'params':p},open('$2','w'),indent=1)"; }
fold() { T=$1; shift
  bash $Q $M2 $D/v2rm_c.json v2rm_b_$T "$@"; mk $D/v2rm_b_$T.json $D/init_b_$T.json
  FIX=$BASE bash $Q $M3 $D/init_b_$T.json v3_b_${T}_s1 "$@"; bash $Q $M3 $D/v3_b_${T}_s1.json v3_b_$T "$@"; }
( fold r1 R2c R3 R4c ) &
( fold r2c R1 R3 R4c ) &
wait; echo BATCH3 DONE
