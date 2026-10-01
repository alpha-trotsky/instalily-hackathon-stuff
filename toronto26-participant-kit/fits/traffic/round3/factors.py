"""Static capacity factors per setting. python factors.py PARAMS"""
import sys, json, math
p = json.load(open(sys.argv[1]))['params']
sig = lambda x: 1/(1+math.exp(-x))
S = {'R6 B': (0,0,.7,1,0,0), 'R6 g.255': (.7,0,.7,1,0,0), 'R6 g.2025': (.85,0,.7,1,0,0),
     'ray .7': (.7,)*6, 'ray .85': (.85,)*6, 'ray 1': (1,)*6, 'R1 toll0': (0,0,1,1,0,0), 'R1 fr1': (0,0,1,1,1,0),
     'R1 lane': (0,1,1,1,0,0), 'R1 cl0': (0,0,1,1,0,1), 'R5 cl.5': (0,0,.7,1,0,.5), 'R5 fr0': (0,0,.7,1,-1,0),
     'R5 lane.3': (0,.46,.7,1,0,0), 'R5 g.3': (.57,0,.7,1,0,0)}
kgA = p['kg']; kgB = p.get('kg_B', kgA); P = 6
for k, (us, ul, uf, ur, ufr, uc) in S.items():
    gA = 0.5 - 0.35*us; gr = [gA, 1-gA]; lane = .65*ul
    h = sig(p['h0'] + p['h1']*uf); vpp = 1/(1+h*(p['pce']-1))
    row = []
    for r, R in enumerate('AB'):
        cm = math.exp(p['c_'+R]); xg = [kgA, kgB][r]*gr[r]/cm
        knee = xg/(1+xg**P)**(1/P)
        cap = cm*knee*math.exp(p['wc_'+R]*uc)*max(1-p['wl_'+R]*lane, .02)
        ecap = math.exp(p['e_'+R] - p['ke']*uc)
        row.append(f'{R}: cap {cap:5.1f}PCU (knee {knee:.2f}) ~{cap*vpp:5.1f}veh ecap {ecap:5.1f} fullpen {math.exp(-p["sp_"+R]):.2f}')
    print(f'{k:10s} h {h:.2f} wH {math.exp(p["kf"]*ufr):.2f} D {p["d0"]*ur*max(1+p["wt"]*uf,0):5.1f} | ' + ' | '.join(row))
