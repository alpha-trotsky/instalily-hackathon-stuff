"""greybox.common.bootstrap with every refit warm-started from that candidate's real-data fit (lesson from
epidemic/wildlife) and max_nfev 150. usage: python fits/ad_auction/v1/boot.py <bootstrap args>"""
import sys, json
sys.path.insert(0, '.')
from greybox.common import bootstrap, fit as fitmod
FITS = ['fits/ad_auction/v1/m12_all.json', 'fits/ad_auction/v1/m13_all.json', 'fits/ad_auction/v1/m23_all.json']
INITS = {tuple(sorted(d['modules'])): d['params'] for d in (json.load(open(f)) for f in FITS)}
_orig = fitmod.fit
def warm_fit(model, eps, modules, *a, **k):
    return _orig(model, eps, modules, *a, init=INITS[tuple(sorted(modules))], max_nfev=150, **k)
bootstrap.fit = warm_fit
if __name__ == '__main__':
    bootstrap.main(['--fits', *FITS] + sys.argv[1:])
