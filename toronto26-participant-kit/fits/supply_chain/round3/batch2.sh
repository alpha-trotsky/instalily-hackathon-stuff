#!/bin/sh
# priority order under CPU contention: v3 C, v3 B4, v2r B4, v3 H, v2r B5, v3 B5
D=fits/supply_chain/round3; P=$D/pipeline.sh
echo "== v3 C"; FIXX=E0,wlp sh $P greybox/supply_chain_model_v3.py v3 C $D/init_v3.json 2>&1 | grep -v Warn
echo "== v3 B4"; FIXX=E0,wlp sh $P greybox/supply_chain_model_v3.py v3 B4 $D/init_v3.json 2>&1 | grep -v Warn
echo "== v2r B4"; sh $P greybox/supply_chain_model_v2.py v2r B4 fits/supply_chain/round2/v2/final_v2.json 2>&1 | grep -v Warn
echo "== v3 H"; FIXX=E0,wlp sh $P greybox/supply_chain_model_v3.py v3 H $D/init_v3.json 2>&1 | grep -v Warn
echo "== v2r B5"; sh $P greybox/supply_chain_model_v2.py v2r B5 fits/supply_chain/round2/v2/final_v2.json 2>&1 | grep -v Warn
echo "== v3 B5"; FIXX=E0,wlp sh $P greybox/supply_chain_model_v3.py v3 B5 $D/init_v3.json 2>&1 | grep -v Warn
echo DONE
