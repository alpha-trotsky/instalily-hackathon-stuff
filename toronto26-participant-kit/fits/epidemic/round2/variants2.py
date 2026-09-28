from variants import *
for pe in [1.0, 3.0, 5.0, 10.0]:
    for am2 in [1.0, 0.1, 0.03]:
        P['a_m2'] = am2; out = []; tot = []
        for r in ['R1','R2','R3','R4','R5']:
            run, o, a = load_run(r); p = sim(run, MASKFAT=True, PE=pe, ALLPOP=1.0)
            sc = (1/(1+np.abs(p-o)/sig)).mean(0); tot.append(sc.mean())
            extra = ''
            if r == 'R4': extra = ' pk %.0f lvl190-199 %.1f/%.1f min200-240@%d' % (p[:60,0].max(), *p[190:200].mean(0), 200+p[200:240,0].argmin())
            out.append(f'{r}:' + '/'.join('%.3f' % x for x in sc) + extra)
        print(f'PE={pe:4.1f} a_m2={am2:4.2f} mean_old={np.mean(tot[:2]):.3f} mean_new={np.mean(tot[2:]):.3f} |', ' '.join(out))
run, o, a = load_run('R4'); print('data R4 pk %.0f lvl190-199 %.1f/%.1f min200-240@%d' % (o[:60,0].max(), *o[190:200].mean(0), 200+o[200:240,0].argmin()))
