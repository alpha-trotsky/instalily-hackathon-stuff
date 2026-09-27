#!/bin/sh
mods=$1; which=$2
if [ "$which" = all ]; then D="data/social_contagion/R1.json data/social_contagion/R2.json data/social_contagion/R3.json"; EV="";
else D="data/social_contagion/R1.json"; EV="--eval data/social_contagion/R2.json data/social_contagion/R3.json"; fi
M=$mods; [ "$mods" = none ] && M=""
name=$mods; [ "$mods" = none ] && name=base
[ "$mods" = m12 ] && M=m1,m2; [ "$mods" = m13 ] && M=m1,m3; [ "$mods" = m23 ] && M=m2,m3
python -m greybox.common.fit --model greybox/social_contagion_model.py --data $D --modules "$M" --restarts 3 --workers 1 --max-nfev 600 $EV --out fits/social_contagion/v1/${name}_${which}.json > fits/social_contagion/v1/${name}_${which}.log 2>&1
