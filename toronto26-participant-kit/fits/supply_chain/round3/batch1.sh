#!/bin/sh
# round-3 fits: v2r (v2 structure, all data / folds) then v3 (H, C, B4, B5); sequential
D=fits/supply_chain/round3; P=$D/pipeline.sh
for MODE in C B4 B5; do echo "== v2r $MODE"; sh $P greybox/supply_chain_model_v2.py v2r $MODE fits/supply_chain/round2/v2/final_v2.json 2>&1 | grep -v Warn; done
for MODE in H C B4 B5; do echo "== v3 $MODE"; FIXX=E0 sh $P greybox/supply_chain_model_v3.py v3 $MODE $D/init_v3.json 2>&1 | grep -v Warn; done
echo DONE
