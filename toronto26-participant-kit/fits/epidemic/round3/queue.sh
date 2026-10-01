#!/bin/bash
# usage: queue.sh "name|runs|init|fix|model" ...   (sequential fits, log units, then ev3 scoring)
cd "$(dirname "$0")/../../.."; F=fits/epidemic/round3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for job in "$@"; do IFS='|' read -r N R I X M <<< "$job"; M=${M:-greybox/epidemic_model_v2.py}
  python $F/fit3.py --name $N --runs $R --init $F/$I --fix "$X" --modules m1,m2 --model $M --units log --passes 3 > $F/$N.log 2>&1
  python $F/ev3.py --diag --model $M $F/$N.json >> $F/results.txt
done
