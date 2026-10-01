#!/bin/sh
F=fits/reservoir/round3/fit3.sh; I=fits/reservoir/round2/v2/final_v2.json; ALL="R1 R2 R3 R4 R5 R6XD R7XS"
B=m1,m3,reset,conv,lz; M3=greybox/reservoir_model_v3.py
sh $F v2r_C greybox/reservoir_model_v2.py $B $I 0 400 $ALL
sh $F q_v2 $M3 $B $I 300 0 $ALL
sh $F q_lag $M3 $B,lag $I 300 0 $ALL
sh $F q_lagdep $M3 $B,lag,dep $I 300 0 $ALL
sh $F q_laglay $M3 $B,lag,lay $I 300 0 $ALL
sh $F q_lagseq $M3 $B,lag,seq $I 300 0 $ALL
sh $F q_full $M3 $B,lag,dep,lay,seq $I 300 0 $ALL
echo BATCH1 DONE
