#!/bin/sh
# usage: pipeline.sh MODEL TAG MODE INIT  (staged fit as round 2: s1 flow/supply with retail weight 0, s2 retail only)
# RETP (env) overrides the retail parameter list; EXTRA1 extra s1 args.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M=$1; T=$2; MODE=$3; INIT=$4; D=fits/supply_chain/round3; R=fits/supply_chain/round3/run.py
MECH=a1,g1,g1r,a2,g2s,g2p,a3u,a3d,g3
RET=${RETP:-D0,kR,dz,az,g,aup,adn}
python $R --model $M --tag ${T}_s1 --mode $MODE --init $INIT --restarts 2 --nfev 300 --noise 1.10,12.5,1e6 --fix $RET,$MECH${FIXX:+,$FIXX} ${EXTRA1} | tail -1
python $R --model $M --tag ${T}_s2 --mode $MODE --init $D/${T}_s1_$MODE.json --restarts 1 --nfev 300 --noise 1.10,12.5,34.9 --free $RET | tail -8
cp $D/${T}_s2_$MODE.json $D/${T}_$MODE.json
