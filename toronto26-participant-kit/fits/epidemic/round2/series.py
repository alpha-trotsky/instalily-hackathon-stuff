from common import *
import sys
m = v1()
for r in sys.argv[1:]:
    run, o, a = load_run(r); p = predict(m, run)
    print('==', r, run['initial'])
    print('peak data', o[:60,0].max().round(1), o[:60,0].argmax(), ' v1', p[:60,0].max().round(1), p[:60,0].argmax())
    for t in range(len(o)):
        if t < 45 or t % 5 == 0 or any(abs(t - s) <= 6 for s,_,_ in segs(run)):
            print(f'{t:4d} {a[t].round(4)} c {o[t,0]:7.1f} v1 {p[t,0]:7.1f} | H {o[t,1]:6.1f} v1 {p[t,1]:6.1f}')
