#!/bin/bash
# usage: queue.sh "name|runs|init|fix|modules" ...   (runs the fits sequentially in one process)
cd "$(dirname "$0")/../../../.."; F=fits/epidemic/round2/v2
for job in "$@"; do IFS='|' read -r N R I X M <<< "$job"
  python3 $F/fit2.py --name $N --runs $R --init $F/$I --fix "$X" --modules $M --units log --passes 3 > $F/$N.log 2>&1
  python3 $F/ev.py $F/$N.json >> $F/results.txt
done
