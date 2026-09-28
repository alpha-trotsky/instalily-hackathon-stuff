D=fits/power_grid/round2
python3 $D/v2_fit.py --modules m1,m3 --train R1 R2c R4 --test R3 --init $D/v2_A_m13.json --restarts 1 --workers 1 --max-nfev 250 --out $D/v2_B_noR3.json > $D/v2_B_noR3.log 2>&1 &
python3 $D/v2_fit.py --modules m1,m3 --train R1 R2c R3 --test R4 --init $D/v2_A_m13.json --restarts 1 --workers 1 --max-nfev 250 --out $D/v2_B_noR4.json > $D/v2_B_noR4.log 2>&1 &
wait
python3 $D/v2_fit.py --model greybox/power_grid_model.py --modules m1,m3 --train R1 R2c R4 --test R3 --init fits/power_grid/v1/m13_all.json --restarts 1 --workers 1 --max-nfev 250 --out $D/v1refit_B_noR3.json > $D/v1refit_B_noR3.log 2>&1 &
python3 $D/v2_fit.py --model greybox/power_grid_model.py --modules m1,m3 --train R1 R2c R3 --test R4 --init fits/power_grid/v1/m13_all.json --restarts 1 --workers 1 --max-nfev 250 --out $D/v1refit_B_noR4.json > $D/v1refit_B_noR4.log 2>&1 &
wait
echo FOLDS DONE
