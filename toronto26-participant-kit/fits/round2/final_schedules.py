"""Round-2 proposed schedules (plans/round2-experiments.md). FREE: nothing here calls the simulator.

    python fits/round2/final_schedules.py            # validate bounds, screen every system, write segment JSON
    python fits/round2/final_schedules.py wildlife   # one system

Writes fits/round2/segments/<system>_<run>.json (the exact --segments payload for run_schedule.py) and prints
model predictions (mean of the last 10 ticks of each segment) per candidate fit, plus mean pairwise disagreement
in score sigma. Every run starts from a fresh reset, so controls act from tick 0.
"""
import json, os, re, sys
sys.path.insert(0, 'fits/round2'); sys.path.insert(0, '.')
from screen import run as screen

BRIEFS = open('briefs.md', encoding='utf-8').read()


def refs(system):
    txt = BRIEFS.split(f'## {system}\n')[1].split('\n## ')[0]
    rec = json.loads(re.search(r'recovery action: `(\{.*?\})`', txt).group(1))
    pul = json.loads(re.search(r'pulse action: `(\{.*?\})`', txt).group(1))
    bounds = {m.group(1): (float(m.group(2)), float(m.group(3)))
              for m in re.finditer(r'^\| (\w+) \| ([\d.]+) \| ([\d.]+) \|$', txt, re.M)}
    return rec, pul, bounds


def U(system, u, **over):
    """Action at fraction u of the recovery->pulse distance for every control, then raw overrides."""
    rec, pul, _ = refs(system)
    a = {k: round(rec[k] + u * (pul[k] - rec[k]), 6) for k in rec}
    a.update(over)
    return a


def S(steps, action, label):
    return dict(steps=steps, action=action, label=label)


def schedules():
    X = {}
    # ---- social_contagion (1,000 left; plan 880, reserve 120)
    s = 'social_contagion'; R = U(s, 0)
    X[s] = {
        'SC1': [S(100, U(s, .7), 'P1 u.7 from reset'), S(50, R, 'rec +50 (crash)'), S(100, R, 'rec +150'),
                S(150, R, 'rec +300 (tail)'), S(60, U(s, .85), 'P2 u.85 after 300 gap'), S(20, R, 'gap 20'),
                S(60, U(s, .85), 'P3 u.85 after 20 gap'), S(20, R, 'rec 20')],
        'SC2': [S(80, R | {'seeding': 4.5}, 'seeding 4.5 alone'), S(60, R | {'seeding': 4.5, 'incentive': 2.0}, '+incentive 2'),
                S(50, R | {'seeding': 4.5, 'incentive': 1.0}, 'incentive 1 (partial cut)'),
                S(50, R | {'seeding': 4.5}, 'incentive 0'), S(80, R, 'seeding 0 (recovery)')]}
    # ---- epidemic (1,055; plan 900, reserve 155)
    s = 'epidemic'; R = U(s, 0)
    X[s] = {
        'EP1': [S(40, U(s, .85), 'all .85: first wave'), S(60, U(s, .85), 't40-99'), S(150, U(s, .85), 't100-249 (level)'),
                S(40, R, 'release'), S(110, R, 'rec +150')],
        'EP2': [S(40, R | {'vaccination_rate': 0.003}, 'vacc: first wave'), S(160, R | {'vaccination_rate': 0.003}, 'vacc t40-199'),
                S(30, R, 'off +30'), S(70, R, 'off +100')],
        'EP3': [S(40, R | {'school_closure': 1.0}, 'closure 1: first wave'), S(80, R | {'school_closure': 1.0}, 'closure t40-119'),
                S(80, R | {'school_closure': 1.0, 'mask_mandate': 0.7}, '+mask .7')]}
    # ---- wildlife (1,000; plan 850, reserve 150)
    s = 'wildlife'; R = U(s, 0)
    X[s] = {
        'WL1': [S(80, U(s, .85), 'joint .85 from reset'), S(30, R, 'release +30'), S(90, R, 'release +120'),
                S(60, U(s, 1), 'joint 1.0'), S(30, R, 'short gap 30'), S(60, U(s, .7), 'joint .7'),
                S(30, R, 'release +30'), S(120, R, 'release +150')],
        'WL2': [S(80, R | {'hunting_quota': 5.0}, 'hunt 5'), S(60, R | {'hunting_quota': 5.0, 'habitat_protection': .37}, 'hunt5+hab.37'),
                S(60, R | {'habitat_protection': .37}, 'hab .37'), S(60, R | {'habitat_protection': .37, 'corridor_access': .7}, 'hab.37+corr.7'),
                S(60, R | {'corridor_access': .7}, 'corr .7'), S(30, R, 'rec')]}
    # ---- power_grid (1,000; plan 890, reserve 110)
    s = 'power_grid'; R = U(s, 0)
    X[s] = {
        'PG1': [S(70, R | {'price_signal': 2.0}, 'price 2.0 from reset'), S(70, R | {'price_signal': .45}, 'price .45'),
                S(60, R, 'price 1.5'), S(30, R | {'reserve_dispatch': 40.0}, 'reserve 40'), S(30, R | {'reserve_dispatch': 80.0}, 'reserve 80'),
                S(30, R | {'reserve_dispatch': 120.0}, 'reserve 120'), S(30, R | {'reserve_dispatch': 80.0, 'interconnector': .5}, 'res 80 + ic .5'),
                S(30, R | {'interconnector': .5}, 'ic .5'), S(30, R, 'rec')],
        'PG2': [S(100, U(s, .7), 'joint .7 from reset'), S(60, R, 'rec 60'), S(200, U(s, 1), 'joint 1 x200 (M2 loophole)'),
                S(30, R, 'rec 30'), S(80, U(s, .85), 'joint .85'), S(40, R, 'rec')]}
    # ---- hospital_queue (700; plan 600, reserve 100)
    s = 'hospital_queue'; R = U(s, 0)
    X[s] = {
        'HQ1': [S(50, R | {'elective_scheduling': 5.0}, 'electives 5'), S(50, R | {'elective_scheduling': 10.0}, 'electives 10'),
                S(50, R | {'elective_scheduling': 10.0, 'staffing': 15.0}, 'staff 15 + el 10'),
                S(50, R | {'staffing': 15.0}, 'staff 15 alone'), S(50, R, 'rec')],
        'HQ2': [S(90, U(s, .7), 'joint .7 from reset'), S(50, R, 'rec 50'), S(60, U(s, 1), 'joint 1'),
                S(75, R, 'rec +75'), S(75, R, 'rec +150 (Lq tail)')]}
    # ---- market (1,400; plan 1,200, reserve 200) -- needs the user's go-ahead for market work
    s = 'market'; R = U(s, 0)
    X[s] = {
        'MK1': [S(150, U(s, 1), 'joint 1 from reset'), S(150, R, 'rec 150'), S(125, U(s, .7), 'joint .7'),
                S(50, R, 'short gap 50'), S(125, U(s, 1), 'joint 1 again')],
        'MK2': [S(125, R | {'interest_rate': .05}, 'rate .05'), S(125, R | {'interest_rate': .05, 'transaction_tax': .05}, '+tax .05'),
                S(125, R | {'transaction_tax': .05}, 'tax only'), S(125, R | {'transaction_tax': .025}, 'tax .025'), S(100, R, 'rec')]}
    # ---- ad_auction (1,000; plan 800, reserve 200)
    s = 'ad_auction'; R = U(s, 0)
    X[s] = {
        'AD1': [S(50, U(s, .7), 'u.7 t0-49'), S(200, U(s, .7), 'u.7 t50-249 (level)'), S(100, R, 'rec 100'),
                S(50, U(s, 1), 'u1'), S(25, R, 'rec 25'), S(75, U(s, .85), 'u.85')],
        'AD2': [S(50, R | {'bid': 3.25, 'budget_cap': 100.0}, 'bid 3.25 cap100'), S(50, R | {'bid': 2.0, 'budget_cap': 100.0}, 'bid 2 cap100'),
                S(50, R | {'bid': .75, 'budget_cap': 100.0}, 'bid .75 cap100'), S(50, R, 'rec'),
                S(50, R | {'bid': 5.0, 'budget_cap': 50.0}, 'bid5 cap50'), S(50, R | {'bid': 5.0, 'budget_cap': 30.0}, 'bid5 cap30')]}
    # ---- reservoir (1,000; plan 900, reserve 100)
    s = 'reservoir'; R = U(s, 0)
    X[s] = {
        'RS1': [S(100, U(s, .7), 'pulse .7 t0-99'), S(150, U(s, .7), 'pulse .7 t100-249'), S(50, R, 'rec +50'), S(150, R, 'rec +200')],
        'RS2': [S(150, R | {'release_rate': 10.5}, 'release 10.5'), S(80, R | {'aeration': .3}, 'aer .3'),
                S(80, R | {'aeration': .15, 'withdrawal_depth': .5}, 'aer .15 depth .5'),
                S(80, R | {'aeration': 0.0, 'withdrawal_depth': .5}, 'aer 0 depth .5'), S(60, R, 'rec')]}
    # ---- supply_chain (700; plan 600, reserve 100)
    s = 'supply_chain'; R = U(s, 0)
    X[s] = {
        'SU1': [S(50, U(s, .7), 'u.7 t0-49'), S(100, U(s, .7), 'u.7 t50-149'), S(60, R, 'rec 60'), S(60, U(s, 1), 'u1'),
                S(30, R, 'rec 30'), S(100, U(s, .85), 'u.85')],
        'SU2': [S(50, R | {'order_quantity': 80.0, 'receiving_effort': 1.0}, 'ord80 recv 1.0'),
                S(50, R | {'order_quantity': 80.0, 'receiving_effort': .7}, 'recv .7'),
                S(50, R | {'order_quantity': 80.0, 'receiving_effort': .5}, 'recv .5'),
                S(50, R | {'order_quantity': 80.0, 'receiving_effort': .5, 'maintenance': .3}, '+maint .3')]}
    # ---- traffic (700; plan 600, reserve 100). TR2 background B = recovery + ramp 1 + toll 1.5 (congests in the model).
    s = 'traffic'; R = U(s, 0); B = R | {'ramp_metering': 1.0, 'toll': 1.5}
    X[s] = {
        'TR1': [S(50, U(s, .7), 'u.7 t0-49'), S(100, U(s, .7), 'u.7 t50-149'), S(50, R, 'rec 50'), S(80, U(s, 1), 'u1'),
                S(30, R, 'rec 30'), S(90, U(s, .85), 'u.85')],
        'TR2': [S(50, B, 'B: ramp1 toll1.5'), S(40, B | {'freight_priority': 0.0}, 'B + freight 0'),
                S(40, B | {'signal_timing': .3}, 'B + signal .3'), S(40, B | {'lane_closure': .3}, 'B + lane .3'),
                S(30, B | {'clearance_effort': .5}, 'B + clearance .5')]}
    return X


CANDIDATES = {
    'social_contagion': ('greybox/social_contagion_model.py', ['fits/social_contagion/v1/' + f for f in ['m12_all.json', 'm23_all.json', 'm2_all.json']],
                         ['data/social_contagion/R1.json', 'data/social_contagion/R2.json', 'data/social_contagion/R3.json']),
    'epidemic': ('greybox/epidemic_model.py', ['fits/epidemic/v2/' + f for f in ['m13_all.json', 'm12_all.json', 'base_all.json', 'm23_all.json']],
                 ['data/epidemic/R1.json', 'data/epidemic/R2.json']),
    'wildlife': ('greybox/wildlife_model.py', ['fits/wildlife/v1/' + f for f in ['AB_all3.json', 'AC_all.json', 'BC_all2.json', 'base_all.json']],
                 ['data/wildlife/R1.json', 'data/wildlife/R2c.json']),
    'power_grid': ('greybox/power_grid_model.py', ['fits/power_grid/v1/' + f for f in ['m13_all.json', 'm1_all.json', 'm12_all.json', 'm23_all.json']],
                   ['data/power_grid/R1.json', 'data/power_grid/R2c.json']),
    'hospital_queue': ('greybox/hospital_queue_model.py', ['fits/hospital_queue/final_m12.json', 'fits/hospital_queue/v5_base_all.json'],
                       ['data/hospital_queue/R1.json', 'data/hospital_queue/R2c.json']),
    'market': ('greybox/market_model.py', ['fits/market/' + f for f in ['m12_withdraw_train600.json', 'm13_withdraw_train600.json', 'm23_withdraw_train600.json']],
               ['data/market/A.json']),
    'ad_auction': ('greybox/ad_auction_model.py', ['fits/ad_auction/final.json'] + ['fits/ad_auction/v1/' + f for f in ['m12_all.json', 'm13_all.json', 'base_all.json']],
                   ['data/ad_auction/R1.json', 'data/ad_auction/R2c.json']),
    'reservoir': ('greybox/reservoir_model.py', ['fits/reservoir/v1/' + f for f in ['final.json', 'm12_all.json']],
                  ['data/reservoir/R1.json', 'data/reservoir/R2.json', 'data/reservoir/R3.json']),
    'supply_chain': ('greybox/supply_chain_model.py', ['fits/supply_chain/v1/' + f for f in ['base_all2.json', 'phi_all.json', 'base_all.json']],
                     ['data/supply_chain/R1.json', 'data/supply_chain/R2.json', 'data/supply_chain/R3.json']),
    'traffic': ('greybox/traffic_model.py', ['fits/traffic/final_v1.json'] + ['fits/traffic/v1/' + f for f in ['m12_allw.json', 'm13_allw.json', 'm23_allw.json']],
                ['data/traffic/R1.json', 'data/traffic/R2.json', 'data/traffic/R3.json']),
}

if __name__ == '__main__':
    X = schedules()
    os.makedirs('fits/round2/segments', exist_ok=True)
    total = {}
    for system in sys.argv[1:] or list(X):
        _, _, bounds = refs(system)
        for name, segs in X[system].items():
            for sg in segs:
                assert set(sg['action']) == set(bounds), (system, name, sg)
                for k, v in sg['action'].items():
                    assert bounds[k][0] <= v <= bounds[k][1], (system, name, k, v)
            payload = [dict(steps=sg['steps'], action=sg['action']) for sg in segs]
            json.dump(payload, open(f'fits/round2/segments/{system}_{name}.json', 'w'), indent=1)
            total[system] = total.get(system, 0) + sum(sg['steps'] for sg in segs)
        model, fits, data = CANDIDATES[system]
        screen(system, model, fits, X[system], data)
        print(f'   {system} total steps: {total[system]}', flush=True)
