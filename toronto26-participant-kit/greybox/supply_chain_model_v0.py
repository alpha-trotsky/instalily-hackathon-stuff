"""Supply-chain gray-box model: production pipeline -> capped supplier stock -> dispatch -> transit ->
terminal queue served at a staffing-dependent rate -> rework loop -> retail stock with sales.

Written for plans/supply_chain-plan.md (Phase A, catalogue v1). Interface: greybox/common/fit.py.
Uses only math/numpy (copied into the submission as-is).

Controls, normalized u = (value - recovery)/(pulse - recovery), CONTROLS order; simulate() converts back:
  q  = 80 u0          order_quantity            l  = 1 - 0.8 u1     lead_time_buy (low = rush)
  mx = 0.5 + 0.3 u2   product_mix               e  = 1 + 0.5 u3     production_effort
  r  = 1.5 - 1.15 u4  receiving_effort          m  = 1 - u5         maintenance

Base structure (always on), per tick:
  production  rel = e^pe * (p0 + po*Po + g3*Cm) * (1 - g2p*H)      Po <- Po + ap*(q/80 - Po)  (make-to-order)
              rel travels DP ticks (pipeline, starts empty), then S <- min(S + arrival, Smax)   (B1 cap)
  dispatch    after service: d = min(q, S, dcap, Bmax - B - in transit - in rework loop); S <- S - d
              ("orders withdraw only available stock"); d travels DT ticks (B6 dead time 3) into the queue B
  service     mu = mu0 * (r/1.5)^ar * (1 + wm*(1-m)) * (1 + wmix*(mxl-0.5)) * (1 + wl*(1-ll))
                   * (1 - g1*Cg) * (1 - g2s*H)
              mxl, ll: first-order lags of mix and lead time (mix acts on new batches only, B11; rush retained, B9)
              served = min(B, mu); a fraction phi_e of it returns after LR = 10 ticks (rework loop, B8);
              shipments = (1 - phi_e) * served
  retail      Ss <- Ss + aS*(ship - Ss);  sales = min(R + ship, max(D0 + Dg*Ss + dz*z, 0)), z = (1-az)^t
              R <- R + ship - sales   (B12; reset transient dz: sales ~28 from the initial stock, B2)
Mechanisms (theses in the plan; gain 0 = off):
  m1 congested transport and rework   Cg <- Cg + a1*(B/Bmax - Cg);  mu * (1 - g1*Cg); phi_e = phi + g1r*Cg
  m2 machine heat/wear                H <- H + a2*(e/1.5*(1 - m) - H);  mu * (1 - g2s*H), production * (1 - g2p*H)
  m3 adaptive production commitments  Cm <- Cm + (a3u if q/80 > Cm else a3d)*(q/80 - Cm);  production + g3*Cm
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
DP = 2      # production pipeline ticks (supplier fill starts 2 ticks after reset, B2)
DT = 3      # dispatch -> terminal ticks (first shipments 3 ticks after orders on, B6)
LR = 10     # rework loop ticks (10-tick geometric tail, B8)

SPEC = {
    # production / supplier
    'Smax': (361.8, 'pos'), 'p0': (12.0, 'pos'), 'pe': (1.5, 'pos'), 'po': (40.0, 'pos'), 'ap': (0.3, 'unit'),
    # dispatch / terminal
    'dcap': (45.0, 'pos'), 'Bmax': (1500.0, 'pos'),
    'mu0': (44.0, 'pos'), 'ar': (0.5, 'pos'), 'wm': (0.25, 'free'), 'wmix': (-0.8, 'free'),
    'amix': (0.1, 'unit'), 'wl': (-0.4, 'free'), 'al': (0.1, 'unit'), 'phi': (0.21, 'unit'),
    # retail
    'D0': (15.0, 'pos'), 'Dg': (0.5, 'free'), 'aS': (0.1, 'unit'), 'dz': (13.0, 'free'), 'az': (0.2, 'unit'),
    # m1 congested transport and rework
    'a1': (0.05, 'unit'), 'g1': (0.1, 'unit'), 'g1r': (0.05, 'free'),
    # m2 machine heat/wear
    'a2': (0.02, 'unit'), 'g2s': (0.1, 'unit'), 'g2p': (0.1, 'unit'),
    # m3 adaptive production commitments
    'a3u': (0.05, 'unit'), 'a3d': (0.01, 'unit'), 'g3': (10.0, 'free'),
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
    if kind == 'unit':
        return _sigmoid(raw)
    if kind == 'pos':
        return math.exp(min(raw, 50.0))
    return raw


def to_raw(name, value):
    kind = SPEC[name][1]
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


def simulate(p, initial, actions):
    T = len(actions)
    out = np.zeros((T, 3))
    if T == 0:
        return out
    g = lambda n: float(p[n])
    Smax, p0, pe, po, ap = g('Smax'), g('p0'), g('pe'), g('po'), g('ap')
    dcap, Bmax = g('dcap'), max(g('Bmax'), 1.0)
    mu0, ar, wm, wmix, amix, wl, al, phi = (g('mu0'), g('ar'), g('wm'), g('wmix'), g('amix'), g('wl'),
                                            g('al'), g('phi'))
    D0, Dg, aS, dz, az = g('D0'), g('Dg'), g('aS'), g('dz'), g('az')
    a1, g1, g1r = g('a1'), g('g1'), g('g1r')
    a2, g2s, g2p = g('a2'), g('g2s'), g('g2p')
    a3u, a3d, g3 = g('a3u'), g('a3d'), g('g3')

    S = min(max(_init(initial, 'inventory_supplier', 100.0), 0.0), Smax)
    R = max(_init(initial, 'inventory_retail', 100.0), 0.0)
    ppipe = [0.0] * DP          # production in transit (index 0 arrives next)
    tpipe = [0.0] * DT          # dispatched goods in transit to the terminal
    loop = [0.0] * LR           # rework returns
    B = 0.0                     # terminal queue ("internal buffers start empty")
    Po = Cm = H = Cg = 0.0
    mxl, ll = 0.5, 1.0          # lagged mix / lead time start at recovery
    Ss, z = 0.0, 1.0
    U = np.asarray(actions, dtype=float).reshape(T, len(CONTROLS))
    for t in range(T):
        u0, u1, u2, u3, u4, u5 = U[t]
        q = 80.0 * u0
        l = 1.0 - 0.8 * u1
        mx = 0.5 + 0.3 * u2
        e = max(1.0 + 0.5 * u3, 0.0)
        r = max(1.5 - 1.15 * u4, 0.0)
        m = 1.0 - u5
        # production
        ef = e ** pe if e > 0 else 0.0
        rel = ef * max(p0 + po * Po + g3 * Cm, 0.0) * max(1.0 - g2p * H, 0.0)
        ppipe.append(rel)
        S = min(S + ppipe.pop(0), Smax)
        B += tpipe.pop(0) + loop.pop(0)
        # terminal service
        mxl += amix * (mx - mxl)
        ll += al * (l - ll)
        mu = (mu0 * (r / 1.5) ** ar * max(1.0 + wm * (1.0 - m), 0.0) * max(1.0 + wmix * (mxl - 0.5), 0.0)
              * max(1.0 + wl * (1.0 - ll), 0.0) * max(1.0 - g1 * Cg, 0.0) * max(1.0 - g2s * H, 0.0))
        served = min(B, mu)
        B -= served
        phe = min(max(phi + g1r * Cg, 0.0), 0.9)
        loop.append(phe * served)
        ship = (1.0 - phe) * served
        # dispatch after service; space counts goods already in transit and in the rework loop (no sawtooth)
        space = Bmax - B - sum(tpipe) - sum(loop)
        d = max(min(max(q, 0.0), S, dcap, space), 0.0)
        S -= d
        tpipe.append(d)
        # retail
        Ss += aS * (ship - Ss)
        sales = min(R + ship, max(D0 + Dg * Ss + dz * z, 0.0))
        R = R + ship - sales
        z *= (1.0 - az)
        # memories
        Po += ap * (q / 80.0 - Po)
        dr = q / 80.0
        Cm += (a3u if dr > Cm else a3d) * (dr - Cm)
        H += a2 * (e / 1.5 * (1.0 - m) - H)
        Cg += a1 * (B / Bmax - Cg)
        out[t, 0] = min(max(ship, 0.0), 200.0)
        out[t, 1] = min(max(S, 0.0), 500.0)
        out[t, 2] = min(max(R, 0.0), 20000.0)
    return out
