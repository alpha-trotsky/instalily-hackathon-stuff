"""Free (round 3, ev3 sigma): segment-mean errors (in score sigma) of fit JSONs at the diagnosis' key windows."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ev3 import *
W = [('R1', 375, 435), ('R2', 80, 100), ('R2', 200, 240), ('R3', 30, 40), ('R3', 240, 250), ('R3', 280, 290), ('R3', 320, 330), ('R3', 390, 400),
     ('R4', 15, 30), ('R4', 40, 200), ('R4', 230, 300), ('R5', 30, 40), ('R5', 100, 120), ('R5', 190, 200), ('R1', 225, 315), ('R2', 300, 350), ('R1', 495, 545), ('R6', 20, 30), ('R6', 100, 120), ('R6', 120, 135), ('R6', 145, 155)]
ap = argparse.ArgumentParser(); ap.add_argument('--model', default='greybox/epidemic_model_v2.py'); ap.add_argument('fits', nargs='+')
a = ap.parse_args(); M = load_model(a.model)
print('window'.ljust(14) + ''.join(os.path.basename(f)[:16].rjust(18) for f in a.fits) + '   data')
preds = {f: {r: sim(M, json.load(open(f))['params'], r) for r in RUNS} for f in a.fits}
for r, s, e in W:
    o = D[r][1][s:e].mean(0)
    print(f'{r} {s}-{e}'.ljust(14) + ''.join(('%+.1f/%+.1f' % tuple((preds[f][r][s:e].mean(0) - o) / SIG)).rjust(18) for f in a.fits) + '   %.0f/%.0f' % tuple(o))
