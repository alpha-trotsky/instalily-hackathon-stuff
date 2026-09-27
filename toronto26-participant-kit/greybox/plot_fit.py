"""Plot observations against one or more fitted market variants.

    python greybox/plot_fit.py data/market/A.json fits/market/m12_train450.json fits/market/base_train450.json --out fit.png
"""
import argparse
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_market import NAMES, load_runs, rollout

COLORS = ['#eb6834', '#1baf7a', '#4a3aa7', '#e87ba4']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('fits', nargs='+')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    run = load_runs([args.data])[0]
    t = np.arange(1, len(run['obs']) + 1)
    fig, ax = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True, facecolor='#fcfcfb')
    fits = [(Path(f).stem, json.loads(Path(f).read_text())) for f in args.fits]
    for i, name in enumerate(NAMES):
        a = ax[i]
        a.plot(t, run['obs'][:, i], color='#9a9993', lw=1.0, label='observed')
        for (label, fit), color in zip(fits, COLORS):
            a.plot(t, rollout(fit['params'], run)[:, i], color=color, lw=1.6, label=label)
        if fits:
            a.axvline(fits[0][1]['train_end'] + 0.5, color='#52514e', lw=0.8, ls='--')
        a.set_ylabel(name + (' (log)' if name == 'volume' else ''), color='#52514e')
        if name == 'volume':
            a.set_yscale('log')
        a.set_facecolor('#fcfcfb'); a.grid(axis='y', color='#e6e5e1', lw=0.8); a.tick_params(colors='#52514e')
        for s in ['top', 'right']:
            a.spines[s].set_visible(False)
    ax[0].legend(frameon=False, fontsize=8, loc='upper right')
    ax[2].set_xlabel('tick (dashed line: end of training window)', color='#52514e')
    fig.suptitle('Market: observed vs fitted rollouts', x=0.02, ha='left', color='#0b0b0b')
    fig.tight_layout(); fig.savefig(args.out, dpi=115)
