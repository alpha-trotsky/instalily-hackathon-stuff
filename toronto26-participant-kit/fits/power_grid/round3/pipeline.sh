# One fit pipeline: pipeline.sh VARIANT TAG BASE "TRAIN RUNS" "TEST RUNS"
#   VARIANT v2r | nob | xl | xlc | thr (thr: thresholded x effect under reserve, xb = 1).  Stage 1 = frequency params only (2 restarts), stage 2 = all params (warm start).
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
D=fits/power_grid/round3; V=$1; TAG=$2; BASE=$3; TR=$4; TE=$5
NONF=$(cat $D/nonf.txt)
if [ "$V" = v2r ]; then
  M=greybox/power_grid_model_v2.py; FIX1=$NONF; FIX2=""; INIT=$BASE
else
  M=greybox/power_grid_model_v3.py
  python $D/mkinit3.py --base $BASE --form $V --train $TR --out $D/init_${V}_${TAG}.json
  INIT=$D/init_${V}_${TAG}.json
  case $V in nob) EX=hx,kxf,bc,kxL;; xl) EX=hx,kxf,bc;; xlc) EX=hx,kxf;; thr) EX=hx,kxf,kx,xb;; esac
  FIX1=$NONF,$EX; FIX2=$EX
fi
python $D/r3_fit.py --model $M --train $TR --test $TE --init $INIT --fix $FIX1 --restarts 2 --workers 2 --max-nfev 400 --out $D/${V}_${TAG}_s1.json > $D/${V}_${TAG}_s1.log 2>&1
python $D/r3_fit.py --model $M --train $TR --test $TE --init $D/${V}_${TAG}_s1.json ${FIX2:+--fix $FIX2} --restarts 1 --workers 1 --max-nfev 300 --out $D/${V}_${TAG}.json > $D/${V}_${TAG}.log 2>&1
echo "$V $TAG done: $(grep 'TEST' $D/${V}_${TAG}.log | tr '\n' ' ')"
