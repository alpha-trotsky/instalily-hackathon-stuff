from common import *
from cands import cand, FITS
m = v1(); sig = sigma()
for r in ['R3','R4','R5']:
    run, o, a = load_run(r)
    print(r, ' '.join(f'{k}: {np.mean(np.abs(cand(k,run)[:60,0]-o[:60,0]))/sig[0]:.2f}σ' for k in FITS), '(mean |err| cases ticks 0-59)')
