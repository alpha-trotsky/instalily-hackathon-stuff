"""Free: implied retail sales = shipments - dRetail over windows; relation to R and shipments."""
import numpy as np
d = np.load('fits/supply_chain/round2/arrays.npz')
W = {'R1': [(45,62),(66,100),(100,160),(205,240),(300,320),(360,380),(420,440),(510,534),(545,559),(585,599),(650,669),(700,740)],
     'R2': [(5,25),(40,79),(110,129),(140,176),(218,329),(420,440),(475,499)],
     'R4': [(8,30),(30,60),(60,86),(100,150),(155,165),(175,200),(215,269),(305,330),(330,360),(360,400)],
     'R5': [(13,31),(35,50),(55,100),(118,150),(155,200)]}
rows = []
for r, ws in W.items():
    o = d[r+'_o']
    for a, b in ws:
        sh = o[a:b, 0].mean(); R = o[a:b, 2].mean(); dR = (o[b-1, 2] - o[a-1, 2]) / (b - a)
        s = sh - dR
        rows.append((r, a, b, sh, R, dR, s)); print(f'{r} {a:3d}-{b:3d} ship {sh:5.1f} R {R:7.1f} dR {dR:+6.2f} sales {s:5.1f}')
X = np.array([(1, x[3], x[4]) for x in rows if x[4] > 40]); y = np.array([x[6] for x in rows if x[4] > 40])
c, *_ = np.linalg.lstsq(X, y, rcond=None); print('sales ~ c0 + c1*ship + c2*R:', c.round(4), 'rms', np.sqrt(((X@c-y)**2).mean()).round(2))
X2 = np.array([(1, x[4]) for x in rows if x[4] > 40]); c2, *_ = np.linalg.lstsq(X2, y, rcond=None)
print('sales ~ c0 + c2*R:', c2.round(4), 'rms', np.sqrt(((X2@c2-y)**2).mean()).round(2))
X3 = np.array([(1, x[3], np.sqrt(x[4])) for x in rows if x[4] > 40]); c3, *_ = np.linalg.lstsq(X3, y, rcond=None)
print('sales ~ c0 + c1*ship + c2*sqrtR:', c3.round(4), 'rms', np.sqrt(((X3@c3-y)**2).mean()).round(2))
