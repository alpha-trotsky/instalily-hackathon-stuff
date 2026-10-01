# v3 = thr variant: (C), (B) R3/R4 out, (H) R5 out
D=fits/power_grid/round3; R2=fits/power_grid/round2
bash $D/pipeline.sh thr C  $R2/v2_C_m13.json "R1 R2c R3 R4 R5" "R1 R2c R3 R4 R5"
bash $D/pipeline.sh thr B4 $R2/v2_B_noR4.json "R1 R2c R3 R5" "R4"
bash $D/pipeline.sh thr B3 $R2/v2_B_noR3.json "R1 R2c R4 R5" "R3"
bash $D/pipeline.sh thr H  $R2/v2_C_m13.json "R1 R2c R3 R4" "R5"
echo QUEUE4 DONE
