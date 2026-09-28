"""Zoom plots: reset under electives (R3 0-60), R4 recovery tail vs R1 tail aligned at release. Run from KIT."""
import json, importlib.util, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ctx = json.load(open('docs/hospital_queue.json'))['brief']['forecast_context']
spec = importlib.util.spec_from_file_location('v1p', 'fits/round2/v1_models/hospital_queue/predict.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
N = ['wait_time', 'queue', 'discharges']
def get(r):
    d = json.load(open(f'data/hospital_queue/{r}.json'))['runs'][0]
    o = np.array([[x[n] for n in N] for x in d['observations']])
    p = np.array([[x[n] for n in N] for x in mod.predict(d['initial'], d['actions'], ctx)]); return o, p
fig, ax = plt.subplots(3, 2, figsize=(13, 9))
o, p = get('R3')
for j in range(3):
    ax[j, 0].plot(o[:60, j], 'k.-', lw=.8, label='R3 data'); ax[j, 0].plot(p[:60, j], 'r', label='v1'); ax[j, 0].set_ylabel(N[j])
ax[0, 0].set_title('R3 reset under electives 5 (ticks 0-59)'); ax[0, 0].legend()
o1, p1 = get('R1'); o4, p4 = get('R4')
for j in range(3):
    ax[j, 1].plot(np.arange(170), o1[580:750, j], 'b', lw=.8, label='R1 data (release at 580)')
    ax[j, 1].plot(np.arange(150), o4[200:350, j], 'k', lw=.8, label='R4 data (release at 200)')
    ax[j, 1].plot(np.arange(150), p4[200:350, j], 'r', label='v1 on R4')
    ax[j, 1].plot(np.arange(170), p1[580:750, j], 'm--', lw=.8, label='v1 on R1')
ax[0, 1].set_title('Recovery after the all-controls pulse, aligned at release'); ax[0, 1].legend(fontsize=7)
ax[2, 1].set_xlabel('ticks since release')
plt.tight_layout(); plt.savefig('fits/hospital_queue/round2/zoom_reset_tail.png', dpi=90)
