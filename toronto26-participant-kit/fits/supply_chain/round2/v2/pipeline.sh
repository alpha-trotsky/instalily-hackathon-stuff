#!/bin/sh
# usage: pipeline.sh MODEL TAG MODE INIT  (staged fit: s1 flow/supply, s2 retail, s3 joint)
M=$1; T=$2; MODE=$3; INIT=$4; D=fits/supply_chain/round2/v2; R=fits/supply_chain/round2/v2/run.py
MECH=a1,g1,g1r,a2,g2s,g2p,a3u,a3d,g3
RET=D0,kR,dz,az,g,aup,adn
python3 $R --model $M --tag ${T}_s1 --mode $MODE --init $INIT --restarts 2 --nfev 300 --noise 1.12,12.1,1e6 --fix $RET,$MECH ${EXTRA1} | tail -1
python3 $R --model $M --tag ${T}_s2 --mode $MODE --init $D/${T}_s1_$MODE.json --restarts 1 --nfev 300 --noise 1.12,12.1,34.7 --free $RET | tail -1
cp $D/${T}_s2_$MODE.json $D/${T}_$MODE.json
