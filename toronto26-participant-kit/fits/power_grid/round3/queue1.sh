# round-3 (C) fits, sequential. Run from the kit root.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
D=fits/power_grid/round3; I=fits/power_grid/round2/v2_C_m13.json
ALL="R1 R2c R3 R4 R5"
python $D/r3_fit.py --model greybox/power_grid_model_v2.py --train $ALL --test $ALL --init $I --restarts 1 --workers 1 --max-nfev 250 --out $D/v2r_C.json > $D/v2r_C.log 2>&1
python $D/r3_fit.py --model greybox/power_grid_model_v3.py --train $ALL --test $ALL --init $I --fix hx,kxf,bc --restarts 1 --workers 1 --max-nfev 250 --out $D/v3a_C.json > $D/v3a_C.log 2>&1
python $D/r3_fit.py --model greybox/power_grid_model_v3.py --train $ALL --test $ALL --init $D/v3a_C.json --fix bc --restarts 1 --workers 1 --max-nfev 250 --out $D/v3b_C.json > $D/v3b_C.log 2>&1
python $D/r3_fit.py --model greybox/power_grid_model_v3.py --train $ALL --test $ALL --init $D/v3b_C.json --restarts 1 --workers 1 --max-nfev 250 --out $D/v3c_C.json > $D/v3c_C.log 2>&1
echo QUEUE1 DONE
