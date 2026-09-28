from common import *
m = v1()
def jump(c, s):
    sl = (np.log(c[s-1]) - np.log(c[s-7])) / 6
    return np.log(c[s+6]) - (np.log(c[s-1]) + 7*sl)
for r, s, lab in [('R1',120,'mask 1 on'),('R1',185,'mask 1 off after 65'),('R2',240,'M1+C1 off after 200'),('R2',350,'mask 1 on'),('R2',380,'mask 1 off after 30'),
                  ('R3',250,'M.85+C.85+V.85 off after 250'),('R5',120,'mask .7 on after 120 closure'),('R4',200,'vacc off after 200'),('R2',300,'closure on'),('R2',330,'closure off')]:
    run, o, a = load_run(r); p = predict(m, run)
    print(f'{r} {s:4d} {lab:32s} data {jump(o[:,0],s):+.3f}  v1 {jump(p[:,0],s):+.3f}')
# log slopes around vaccination stop in R4
run, o, a = load_run('R4'); p = predict(m, run)
for s, e in [(180,190),(190,200),(200,210),(210,220),(220,230),(230,240),(240,250)]:
    print('R4 slope', s, e, 'data %+.4f v1 %+.4f' % ((np.log(o[e-1,0])-np.log(o[s,0]))/(e-1-s), (np.log(p[e-1,0])-np.log(p[s,0]))/(e-1-s)))
