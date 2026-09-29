# stage 1: frequency-only fits on all data from static-regression starts
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
D=fits/power_grid/round3; ALL="R1 R2c R3 R4 R5"; NONF=cL,wLp,wLi,kL,rn,qi,Lmin,Lspan,cS,wSx,wSx2,wSL,kS,wSB,kb,kR,F0,F1,Fx,rho1,kap1,g1,kk1,kr1,a3,g3,h3
python $D/r3_fit.py --model greybox/power_grid_model_v3.py --train $ALL --test $ALL --init $D/init_nob.json --fix $NONF,hx,kxf,bc,kxL --restarts 2 --workers 2 --max-nfev 400 --out $D/s1_nob_C.json > $D/s1_nob_C.log 2>&1
python $D/r3_fit.py --model greybox/power_grid_model_v3.py --train $ALL --test $ALL --init $D/init_xl.json --fix $NONF,hx,kxf,bc --restarts 2 --workers 2 --max-nfev 400 --out $D/s1_xl_C.json > $D/s1_xl_C.log 2>&1
python $D/r3_fit.py --model greybox/power_grid_model_v3.py --train $ALL --test $ALL --init $D/init_xlc.json --fix $NONF,hx,kxf --restarts 2 --workers 2 --max-nfev 400 --out $D/s1_xlc_C.json > $D/s1_xlc_C.log 2>&1
python $D/r3_fit.py --model greybox/power_grid_model_v2.py --train $ALL --test $ALL --init fits/power_grid/round3/v2r_C.json --fix $NONF --restarts 2 --workers 2 --max-nfev 400 --out $D/s1_v2r_C.json > $D/s1_v2r_C.log 2>&1
echo QUEUE2 DONE
