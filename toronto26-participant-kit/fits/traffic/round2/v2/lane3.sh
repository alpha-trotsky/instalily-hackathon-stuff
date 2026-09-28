export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 fits/traffic/round2/v2/trfit.py --model greybox/traffic_model_v2.py --init fits/traffic/round2/v2/B4_v2_ld3.json --data R1 R2 R3 R5 --out fits/traffic/round2/v2/B4_v2s.json --set LD=3 --scoresig --pw 3000 --lsq 60 > fits/traffic/round2/v2/B4_v2s.log 2>&1
python3 fits/traffic/round2/v2/trfit.py --model greybox/traffic_model_v2.py --init fits/traffic/round2/v2/B5_v2_ld3.json --data R1 R2 R3 R4 --out fits/traffic/round2/v2/B5_v2s.json --set LD=3 --scoresig --pw 3000 --lsq 60 > fits/traffic/round2/v2/B5_v2s.log 2>&1
