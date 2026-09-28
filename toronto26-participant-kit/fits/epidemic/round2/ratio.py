from common import *
m = v1()
def rat(x, t): return x[t,1] / x[t-25:t-5,0].mean()
W = {'R1':[(100,120),(270,315),(360,375),(420,435),(480,495)], 'R2':[(220,240),(290,300),(390,400)], 'R3':[(90,100),(140,150),(240,250),(280,290),(340,350),(390,400)],
     'R4':[(90,100),(140,150),(190,200),(220,230),(260,270),(290,300)], 'R5':[(110,120),(190,200)]}
for r, ws in W.items():
    run, o, a = load_run(r); p = predict(m, run)
    for s, e in ws:
        print(r, f'{s}-{e}', 'ctrl', a[e-1].round(4), ' H/lagged-cases data %.3f  v1 %.3f' % (np.mean([rat(o,t) for t in range(s,e)]), np.mean([rat(p,t) for t in range(s,e)])))
