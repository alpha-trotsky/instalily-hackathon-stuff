from common import *
for r in ['R3','R4','R5']:
    run, o, a = load_run(r)
    lo = np.log(o); d2 = lo[2:] - 2*lo[1:-1] + lo[:-2]
    mad = lambda x: np.median(np.abs(x - np.median(x))) / 0.6745 / np.sqrt(6)
    capm = (o[:,1] > 150)
    print(r, 'noise (log, diff2 MAD) cases %.4f hosp %.4f' % (mad(d2[:,0]), mad(d2[:,1])),
          ' cap ticks %d-%d median %.2f sd %.2f' % (np.where(capm)[0][0], np.where(capm)[0][-1], np.median(o[capm,1]), o[capm,1].std()),
          ' first ticks', o[:4,0].round(1), ' H min %.1f @%d' % (o[:10,1].min(), o[:10,1].argmin()), 'reset_resp', run.get('reset_response'))
