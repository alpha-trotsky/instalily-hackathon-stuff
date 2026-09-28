"""Supply-chain gray-box model, round 2 (v2). Interface: greybox/common/fit.py. math/numpy only.

v2 changes (plans/supply_chain-round2-diagnosis.md):
  S1  service capacity mu = smin(kr*r*(1 + kp*lift), U): a hard receiving capacity (B18) and an upstream limit
      U = U0*(1 + wm(1-m))*mix*rush*idle factors (maintenance acts on U only, B19). lift = mean pulse-side u of
      rush, mix and effort (joint-pulse ~10% receiving lift, B20; source unidentified). Replaces mu0*(r/1.5)^ar.
  S2  fast dispatch path capacity c1*e^ce (supply-limited phase depends on effort, B21).
  S4  rush acts on U only through its long-run level: factor 1 + wl*((1 - ll)/0.8)^nl with wl <= 0 and a fast lag
      (al >= 0.1). With wl free and al slow, the fit used rush as a clock for the R1 burst (rush alone -> 48 shipments).
  S3  retail sales = min(R + ship, D0 + kR*R + g*E + dz*z), E an asymmetric bounded EMA of shipments (B25).

v1 notes:

Starts from the reviewer variant (fits/supply_chain/review/sc_rv.py) and applies the review fixes:
  G1  every rate and gain is bounded (BOUNDS; sigmoid transform), so no state can act as a slow clock.
  G2  mix acts through a fixed 19-tick delay with a clipped, capped gain; rush through a bounded lag and gain.
  G3  sales = min(R + ship, D0 + kR*R + dz*z): the retail equilibrium rises steeply with shipments (no Dg*Ss).
  G4  Bmax bounded (<= 2000); the terminal serves faster (1 + wid) when no transit arrivals come in (burst ~50).
  R3  (orders 20 probe) showed no class-2 delay at low orders: dispatch fills a fast path (DT = 3) up to rate c1,
      the overflow travels the slow path (DT2 = 21). This reproduces the 25-then-35 phase at orders 80.

Per tick:
  production rel = e^pe*(p0 + po*Po + g3*Cm)*(1 - g2p*H), DP-tick pipeline, S <- min(S + arrival, Smax)
  queue      B += fast + slow arrivals + rework returns
  service    mu = mu0*(r/1.5)^ar*(1 + wm(1-m))*(1 + wmix*clip(mix[t-19] - 0.5, +-0.3))*(1 + wl*clip(1 - ll, 0, 1))
                  *(1 - g1*Cg)*(1 - g2s*H)*(1 + wid*exp(-transit arrivals/2))
             served = min(B, mu); fraction phi returns after LR = 10 ticks; shipments = (1 - phi)*served
  dispatch   d = min(q, S, dcap*min(e/ed, 1), Bmax - B - in transit - in rework); fast min(d, c1), rest slow
  retail     sales = min(R + ship, max(D0 + kR*R + dz*z, 0)), z = (1 - az)^t
Mechanisms (off by default; bounded rates 0.005..0.5, i.e. time constants <= 200 ticks):
  m1 congestion Cg <- Cg + a1*(B/Bmax - Cg); m2 heat H <- H + a2*(e/1.5*(1-m) - H); m3 commitments Cm.
"""
import math
import numpy as np

OBSERVABLES = ('shipments', 'inventory_supplier', 'inventory_retail')
CONTROLS = ('order_quantity', 'lead_time_buy', 'product_mix', 'production_effort', 'receiving_effort',
            'maintenance')
RECOVERY = {'order_quantity': 0.0, 'lead_time_buy': 1.0, 'product_mix': 0.5, 'production_effort': 1.0,
            'receiving_effort': 1.5, 'maintenance': 1.0}
PULSE = {'order_quantity': 80.0, 'lead_time_buy': 0.2, 'product_mix': 0.8, 'production_effort': 1.5,
         'receiving_effort': 0.35, 'maintenance': 0.0}
UNITS = {'shipments': 'linear', 'inventory_supplier': 'linear', 'inventory_retail': 'linear'}
NOISE = {'shipments': 1.5, 'inventory_supplier': 10.0, 'inventory_retail': 25.0}   # ~score sigma (0.1 x std)
CLAMP = {'shipments': [0.0, 200.0], 'inventory_supplier': [0.0, 500.0], 'inventory_retail': [0.0, 20000.0]}
DP = 2      # production pipeline ticks
DT = 3      # fast dispatch path
DT2 = 21    # slow (overflow / class-2) dispatch path
LR = 10     # rework loop ticks
DMX = 19    # mix delay (B11)

SPEC = {
    'Smax': (361.8, 'pos'), 'p0': (12.0, 'pos'), 'pe': (0.5, 'b'), 'po': (37.0, 'pos'), 'ap': (0.13, 'b'),
    'dcap': (52.0, 'pos'), 'Bmax': (1200.0, 'b'), 'ed': (0.47, 'b'), 'c1': (32.0, 'b'),
    'kr': (73.0, 'b'), 'kp': (0.1, 'b'), 'U0': (52.0, 'b'), 'ce': (0.0, 'b'), 'nl': (1.0, 'b'), 'wm': (0.18, 'b'), 'wmix': (-0.7, 'b'),
    'wl': (-0.3, 'b'), 'al': (0.3, 'b'), 'wid': (0.3, 'b'), 'phi': (0.21, 'b'),
    'D0': (15.0, 'pos'), 'kR': (0.009, 'b'), 'dz': (4.0, 'b'), 'az': (0.2, 'b'),
    'g': (0.0, 'b'), 'aup': (0.1, 'b'), 'adn': (0.1, 'b'),
    'a1': (0.05, 'b'), 'g1': (0.1, 'b'), 'g1r': (0.05, 'b'),
    'a2': (0.02, 'b'), 'g2s': (0.1, 'b'), 'g2p': (0.1, 'b'),
    'a3u': (0.05, 'b'), 'a3d': (0.01, 'b'), 'g3': (5.0, 'b'),
}
BOUNDS = {
    'pe': (0.0, 3.0), 'ap': (0.02, 1.0), 'Bmax': (200.0, 2000.0), 'ed': (0.05, 1.5), 'c1': (5.0, 80.0),
    'kr': (20.0, 150.0), 'kp': (0.0, 0.3), 'U0': (20.0, 120.0), 'ce': (0.0, 2.0), 'nl': (1.0, 8.0),
    'g': (0.0, 1.0), 'aup': (0.005, 1.0), 'adn': (0.005, 1.0), 'wm': (-0.5, 1.0), 'wmix': (-1.5, 1.5), 'wl': (-1.0, 0.0), 'al': (0.1, 1.0),
    'wid': (0.0, 1.0), 'phi': (0.0, 0.5), 'kR': (1e-4, 0.1), 'dz': (-40.0, 60.0), 'az': (0.05, 1.0),
    'a1': (0.005, 0.5), 'g1': (0.0, 0.5), 'g1r': (0.0, 0.3),
    'a2': (0.005, 0.5), 'g2s': (0.0, 0.5), 'g2p': (0.0, 0.5),
    'a3u': (0.005, 0.5), 'a3d': (0.005, 0.5), 'g3': (-20.0, 20.0),
}
MODULES = {
    'm1': (['a1', 'g1', 'g1r'], {'g1': 0.0, 'g1r': 0.0}),
    'm2': (['a2', 'g2s', 'g2p'], {'g2s': 0.0, 'g2p': 0.0}),
    'm3': (['a3u', 'a3d', 'g3'], {'g3': 0.0}),
}
FIXED = ('Smax',)


def _sigmoid(x):
    x = min(max(x, -60.0), 60.0)
    return 1.0 / (1.0 + math.exp(-x))


def _logit(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1.0 - p))


def to_natural(name, raw):
    kind = SPEC[name][1]
    if kind == 'b':
        lo, hi = BOUNDS[name]
        return lo + (hi - lo) * _sigmoid(raw)
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(raw, 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
    if kind == 'b':
        lo, hi = BOUNDS[name]
        return _logit((value - lo) / (hi - lo))
    if kind == 'unit':
        return _logit(value)
    if kind == 'pos':
        return math.log(max(value, 1e-300))
    return value


def normalize(action, bounds):
    out = []
    for c in CONTROLS:
        lo, hi = bounds.get(c, (min(RECOVERY[c], PULSE[c]), max(RECOVERY[c], PULSE[c])))
        v = min(max(float(action[c]), lo), hi)
        out.append((v - RECOVERY[c]) / (PULSE[c] - RECOVERY[c]))
    return tuple(out)


def _init(initial, name, default):
    try:
        v = float(initial[name])
        return v if math.isfinite(v) else default
    except (KeyError, TypeError, ValueError):
        return default


def _b(p, n):
    """Parameter value clipped to its bound (guards hand-edited or --init values)."""
    v = float(p[n])
    if not math.isfinite(v):
        v = SPEC[n][0]
    if n in BOUNDS:
        lo, hi = BOUNDS[n]
        v = min(max(v, lo), hi)
    return v


def simulate(p, initial, actions):
    T = len(actions)
    out = np.zeros((T, 3))
    if T == 0:
        return out
    g = lambda n: _b(p, n)
    Smax, p0, pe, po, ap = g('Smax'), g('p0'), g('pe'), g('po'), g('ap')
    dcap, Bmax, ed, c1 = g('dcap'), g('Bmax'), max(g('ed'), 1e-3), g('c1')
    kr, kp, U0, ce, nl = g('kr'), g('kp'), g('U0'), g('ce'), g('nl')
    wm, wmix, wl, al, wid, phi = g('wm'), g('wmix'), g('wl'), g('al'), g('wid'), g('phi')
    D0, kR, dz, az = g('D0'), g('kR'), g('dz'), g('az')
    gE, aup, adn = g('g'), g('aup'), g('adn')
    E = 0.0
    a1, g1, g1r = g('a1'), g('g1'), g('g1r')
    a2, g2s, g2p = g('a2'), g('g2s'), g('g2p')
    a3u, a3d, g3 = g('a3u'), g('a3d'), g('g3')

    S = min(max(_init(initial, 'inventory_supplier', 100.0), 0.0), Smax)
    R = min(max(_init(initial, 'inventory_retail', 100.0), 0.0), 20000.0)
    ppipe = [0.0] * DP
    tp1 = [0.0] * DT
    tp2 = [0.0] * DT2
    loop = [0.0] * LR
    mixbuf = [0.5] * DMX
    B = 0.0
    Po = Cm = H = Cg = 0.0
    ll, z = 1.0, 1.0
    U = np.asarray(actions, dtype=float).reshape(T, len(CONTROLS))
    for t in range(T):
        u0, u1, u2, u3, u4, u5 = U[t]
        q = min(max(80.0 * u0, 0.0), 80.0)
        l = min(max(1.0 - 0.8 * u1, 0.0), 1.0)
        mx = min(max(0.5 + 0.3 * u2, 0.0), 1.0)
        e = min(max(1.0 + 0.5 * u3, 0.0), 1.5)
        r = min(max(1.5 - 1.15 * u4, 0.0), 1.5)
        m = min(max(1.0 - u5, 0.0), 1.0)
        ef = e ** pe if e > 0 else 0.0
        ef_c = e ** ce if e > 0 else 0.0
        rel = ef * max(p0 + po * Po + g3 * Cm, 0.0) * max(1.0 - g2p * H, 0.0)
        ppipe.append(rel)
        S = min(S + ppipe.pop(0), Smax)
        arr = tp1.pop(0) + tp2.pop(0)
        B += arr + loop.pop(0)
        mixbuf.append(mx)
        mxd = mixbuf.pop(0)
        ll += al * (l - ll)
        Uc = (U0 * max(1.0 + wm * (1.0 - m), 0.05)
              * (1.0 + wmix * min(max(mxd - 0.5, -0.3), 0.3))
              * max(1.0 + wl * min(max((1.0 - ll) / 0.8, 0.0), 1.0) ** nl, 0.05)
              * max(1.0 - g1 * Cg, 0.0) * max(1.0 - g2s * H, 0.0)
              * (1.0 + wid * math.exp(-arr / 2.0)))
        lift = (min(max(u1, 0.0), 1.0) + min(max(u2, 0.0), 1.0) + min(max(u3, 0.0), 1.0)) / 3.0
        Rc = kr * r * (1.0 + kp * lift)
        mu = 0.5 * (Rc + Uc - math.sqrt((Rc - Uc) ** 2 + 1.0))
        mu = max(mu, 0.0)
        served = min(B, mu)
        B -= served
        phe = min(max(phi + g1r * Cg, 0.0), 0.9)
        loop.append(phe * served)
        ship = (1.0 - phe) * served
        dtot = max(min(q, S, dcap * min(e / ed, 1.0)), 0.0)
        space = max(Bmax - B - sum(tp1) - sum(tp2) - sum(loop), 0.0)
        dtot = min(dtot, space)
        d1 = min(dtot, c1 * ef_c)
        S -= dtot
        tp1.append(d1)
        tp2.append(dtot - d1)
        E += (aup if ship > E else adn) * (ship - E)
        sales = min(R + ship, max(D0 + kR * R + gE * E + dz * z, 0.0))
        R = min(R + ship - sales, 20000.0)
        z *= (1.0 - az)
        Po += ap * (q / 80.0 - Po)
        dr = q / 80.0
        Cm += (a3u if dr > Cm else a3d) * (dr - Cm)
        H += a2 * (e / 1.5 * (1.0 - m) - H)
        Cg += a1 * (B / Bmax - Cg)
        out[t, 0] = min(max(ship, 0.0), 200.0)
        out[t, 1] = min(max(S, 0.0), 500.0)
        out[t, 2] = min(max(R, 0.0), 20000.0)
    return out
