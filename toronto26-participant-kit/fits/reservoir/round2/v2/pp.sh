#!/bin/sh
python3 -c "
import json;p=json.load(open('$1'))['params']
print({k:round(p[k],5) for k in ['cq','kq','wqa','wqd','wqx','wqr','wqi','a_z','lam_q','lz','gam','a3','a3d','g3','h3','ap','dC','gC','kfl','gr','Hr','rho','H0','gf1','af1','g1','th1','a1'] if k in p})"
python3 fits/reservoir/round2/v2/score.py ${2:-greybox/reservoir_model_v2.py} $1 R1 R2 R3 R4 R5
