from common import *
m = v1(); sig = sigma(); print('sigma', sig)
for r in ['R1','R2','R3','R4','R5']:
    run, o, a = load_run(r); p = predict(m, run)
    print(f'== {r} initial {run["initial"]} T={len(o)}')
    for (s, e, act) in segs(run) or [(0, len(o), None)]:
        lo = max(e-10, s)
        print(f'  [{s:4d}-{e-1:4d}] {act}  data last10 {o[lo:e].mean(0).round(1)}  v1 {p[lo:e].mean(0).round(1)}  err/sig {((p[lo:e]-o[lo:e]).mean(0)/sig).round(2)}  score {(1/(1+np.abs(p[s:e]-o[s:e])/sig)).mean(0).round(3)}')
    print('  overall score', (1/(1+np.abs(p-o)/sig)).mean(0).round(3))
