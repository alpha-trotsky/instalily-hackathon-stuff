# (C), (H), (B) for v2r / nob / xl / xlc
D=fits/power_grid/round3; R2=fits/power_grid/round2
for V in v2r xlc xl nob; do
  bash $D/pipeline.sh $V C  $R2/v2_C_m13.json "R1 R2c R3 R4 R5" "R1 R2c R3 R4 R5"
  bash $D/pipeline.sh $V B3 $R2/v2_B_noR3.json "R1 R2c R4 R5" "R3"
  bash $D/pipeline.sh $V B4 $R2/v2_B_noR4.json "R1 R2c R3 R5" "R4"
  [ $V != v2r ] && bash $D/pipeline.sh $V H $R2/v2_C_m13.json "R1 R2c R3 R4" "R5"
done
echo QUEUE3 DONE
