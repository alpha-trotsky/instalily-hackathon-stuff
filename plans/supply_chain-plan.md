# Supply chain plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 (overnight job, `plans/overnight-framework.md`). CAP = 1,300 steps
(6 controls: Run 1 ≤ 750, Run 2 ≤ 500, reserve ≥ 50). Budget at start: 2,000 remaining (free read).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Arrivals at the retailer plus total supplier and retail stock. Supplier goods have two classes;
product mix selects new production and requested dispatch, without rewriting old batches. Orders withdraw only
available stock. Production effort releases material and operates the primary line; receiving effort staffs the
final terminal. Rush handling bypasses treatment for new primary-line departures, while the second class normally
follows its own intake. Conveyors retain their destination and travel commitment after a rush change. The two
intakes share forward transport; the second intake and treatment share cooling, while the primary intake, receiving
and maintenance share drive service. Maintenance restores treatment activity but takes utility and productive
treatment time. Goods needing rework may return to the primary intake; return-space overflow leaves as
secondary-grade goods counted in shipments. Congested transport and rework, machine heat/wear, and adaptive
production commitments are three possible memory mechanisms; exactly two apply. Hold product mix fixed when
comparing maintenance with an idle pause; compare rush changes before and after dispatch, or equal orders in
opposite production sequences. Internal buffers and conveyors start empty; the initial stocks split into fixed
class shares."

**Observables** (initial-reading ranges from `docs/supply_chain.json`):

| Observable | Initial range | Reading of the brief |
|---|---|---|
| shipments | 20 – 35 | "arrivals at the retailer" per tick: the output of dispatch → forward transport → final terminal (receiving). Also includes "secondary-grade goods" from return-space overflow |
| inventory_supplier | 80 – 120 | total supplier stock over two classes; filled by production, emptied by order-requested dispatch ("orders withdraw only available stock" → dispatch = min(order, available)) |
| inventory_retail | 80 – 120 | retail stock; filled by shipments; emptied by (unknown) retail demand/sales |

"Internal buffers and conveyors start empty" → the initial reading is **not** an equilibrium: expect a reset
transient (shipments may start from nothing in the pipeline, stocks drift). "the initial stocks split into fixed
class shares" → class composition of the stocks at reset is deterministic.

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u formula | u range | Notes |
|---|---|---:|---:|---|---|---|
| order_quantity | [0, 80] | 0 | 80 | q/80 | [0, 1] | requested dispatch from supplier to retail; at recovery nothing is ordered |
| lead_time_buy | [0, 1] | 1.0 | 0.2 | (1 − l)/0.8 | [0, 1.25] | most likely the **rush** control (short lead time = rush handling, bypasses treatment). 0 (u = 1.25) slightly beyond pulse |
| product_mix | [0, 1] | **0.5** | 0.8 | (m − 0.5)/0.3 | [−1.67, 1.67] | recovery **not at a bound**; the side 0–0.5 (u < 0) is never tested by pulses. Share of class 2 (or 1) in new production and dispatch requests |
| production_effort | [0, 1.5] | **1.0** | 1.5 | (e − 1)/0.5 | [−2, 1] | recovery **not at a bound**; 0 (u = −2, production stopped = "idle pause") is on the other side |
| receiving_effort | [0, 1.5] | 1.5 | 0.35 | (1.5 − r)/1.15 | [0, 1.30] | staffs the final terminal; pulse is **low** staffing → slower arrivals |
| maintenance | [0, 1] | 1.0 | 0 | 1 − m | [0, 1] | pulse = **no** maintenance; recovery = full maintenance (which "takes utility and productive treatment time") |

**Delay / commitment phrases → pipeline stages (base structure):**
- "Conveyors retain their destination and travel commitment after a rush change" → goods on conveyors keep their
  route: a rush change affects only **new** primary-line departures → delay (shift-register or lag stages) between
  lead_time_buy and its effect; treatment path longer than the rush path.
- "product mix selects new production and requested dispatch, without rewriting old batches" → mix acts on new
  batches only: a lagged effect through production and dispatch; old stock keeps its classes.
- "Orders withdraw only available stock" → dispatch = min(order, available stock of the requested class) —
  saturation; with the mix, a class can run out while the other has stock.
- Production pipeline: material release → primary intake → (treatment | rush bypass) → forward transport (shared
  with the second intake) → supplier stock. Dispatch pipeline: supplier stock → transport → final terminal
  (receiving effort) → shipments → retail stock. Each is at least one lag stage; all start empty.
- Shared resources (coupling): forward transport (both intakes), cooling (second intake + treatment), drive service
  (primary intake + receiving + maintenance) → **maintenance can slow receiving/primary intake** (drive service
  shared) and class-2 production can slow treatment (cooling shared).
- Rework loop: "Goods needing rework may return to the primary intake; return-space overflow leaves as
  secondary-grade goods counted in shipments" → a recirculating buffer; when it overflows, shipments get an
  extra component unrelated to orders.

**Anything tied to time since reset:** nothing seasonal. Only the empty-pipeline transient and the fixed class
split of the initial stocks.

**Organizer-suggested comparisons (P9, quoted):**
- **P9a:** "Hold product mix fixed when comparing maintenance with an idle pause" → with mix constant, compare (i) a
  maintenance period with (ii) an idle pause (production_effort 0 or low, maintenance off) of the same length,
  after the same loading history; compare the throughput afterwards. Aimed at heat (cools in both) vs wear
  (restored only by maintenance).
- **P9b:** "compare rush changes before and after dispatch" → switch rush (lead_time_buy) on/off at a time when
  goods are already dispatched on conveyors vs before dispatch; conveyors keep their commitment, so the effect
  timing differs. Aimed at congested transport (M1).
- **P9c:** "equal orders in opposite production sequences" → the same order schedule with production effort high
  then low vs low then high. Aimed at adaptive production commitments (M3) (and heat/wear history).

## 2. The three mechanisms (§3.2)

Quoted from one sentence listing three parallel candidates (confidence: high): "Congested transport and rework,
machine heat/wear, and adaptive production commitments are three possible memory mechanisms; exactly two apply."

- **M1 congested transport and rework**
- **M2 machine heat/wear**
- **M3 adaptive production commitments**

## 3. Theses (§3.3)

### M1 congested transport and rework

| Field | Content |
|---|---|
| Quote | "Congested transport and rework"; "The two intakes share forward transport"; "Goods needing rework may return to the primary intake; return-space overflow leaves as secondary-grade goods counted in shipments" |
| Hidden state | C: congestion / backlog on the shared forward transport plus the rework recirculation volume; persists (drains slowly) |
| **Driver** | load on transport = flow through both intakes (production effort, rush, mix) plus dispatch (orders); accumulated exposure above a capacity (one-sided) |
| **What it changes** | transit speed / capacity → throughput to supplier stock and to shipments falls under sustained high load and **recovers slowly** after load falls; rework feedback adds load; overflow adds secondary-grade shipments |
| Timescales | builds 10–50 ticks under overload; drains 30–200 ticks |
| P0 | none unless recovery itself congests |
| P1 production on/off | present: supplier stock growth sags during a long hold; slow hangover after release (on/off asymmetric). Absent: mirror steps |
| P1 orders on/off | present: shipments lag/sag at high dispatch, backlog drains after off (shipments continue longer). Absent: symmetric pipeline response |
| P1 rush on/off | present: rush sends more goods onto transport at once → congestion transient; retained commitments delay the off effect |
| P1 maintenance / receiving | only via load changes |
| P3 joint / all-controls pulse | congestion strongest (production 1.5 + rush + orders 80); slow recovery after release |
| P5 gap (two high-load pulses) | 2nd pulse starts congested after a short gap → lower throughput |
| P9a maintenance vs idle | idle pause drains congestion (less load); maintenance does too if it lowers throughput → **no maintenance-specific difference** |
| P9b rush before/after dispatch | **differs** (goods already on the transport keep congesting it) |
| P9c opposite production sequences | final state differs only through the congestion still present (high-late sequence ends congested) |

### M2 machine heat/wear

| Field | Content |
|---|---|
| Quote | "machine heat/wear"; "the second intake and treatment share cooling, while the primary intake, receiving and maintenance share drive service. Maintenance restores treatment activity but takes utility and productive treatment time" |
| Hidden state | H: heat of treatment/second intake (cools when idle, cooling shared); W: wear of treatment/drives (restored **only** by maintenance) |
| **Driver** | utilization: production effort (and mix toward class 2 for heat), receiving effort (drive service), accumulated; maintenance = 0 lets wear build |
| **What it changes** | treatment/production capacity (and possibly receiving capacity) → supplier-stock growth and shipments decline slowly during sustained high effort or without maintenance |
| Timescales | heat builds/cools 20–100 ticks; wear builds 100–500 ticks, restored by maintenance over 20–100 |
| P0 | at recovery (effort 1, maintenance 1) wear held low, heat at a moderate level: little drift |
| P1 production 1.5 on/off | present: jump then **slow decline** of production during the hold (heat), rested machines overshoot after off; absent: flat hold |
| P1 maintenance off (u = 1) | present: immediate gain (maintenance no longer takes treatment time) then **slow decline** as wear builds; after maintenance back on: immediate loss then slow recovery of capacity; absent: two mirror steps |
| P1 orders | none directly (only via utilization of receiving) |
| P5 gap (two production pulses) | 2nd weaker after a short gap (heat not dissipated) |
| P7 long hold at high effort, no maintenance | continuing slow decline |
| P9a maintenance vs idle | **differs**: idle cools heat but leaves wear; maintenance restores wear → different throughput afterwards |
| P9b rush before/after dispatch | rush bypasses treatment → less treatment heat; timing irrelevant |
| P9c opposite production sequences | differs (heat depends on recent effort) |

### M3 adaptive production commitments

| Field | Content |
|---|---|
| Quote | "adaptive production commitments"; "Production effort releases material and operates the primary line" |
| Hidden state | P: production commitment that adapts to recent demand (orders / dispatch / low supplier stock) — a moving average of withdrawals |
| **Driver** | order history (order_quantity, or actual dispatch), possibly the supplier-stock shortfall |
| **What it changes** | production rate → supplier stock inflow (and later shipments); commitments persist after demand falls |
| Timescales | adapts over 30–200 ticks; commitments fade similarly |
| P0 | none (no orders) — or slow decay of an initial commitment |
| P1 orders on/off | present: supplier stock falls fast then **partially recovers during the hold** (production ramps up); after orders stop, supplier stock **overshoots** above its baseline then decays (bullwhip). Absent: stock goes down and comes back monotonically |
| P1 production effort | present: effect of effort modulated by commitment; absent: plain step |
| P1 maintenance / receiving | none |
| P5 gap (two order pulses) | 2nd pulse depletes stock less after a short gap (commitment still high) |
| P9a maintenance vs idle | none |
| P9b rush before/after dispatch | none |
| P9c equal orders, opposite production sequences | **differs** strongly: commitments follow orders and interact with the effort path |

## 4. Separation table (§3.4)

| Probe | M1 congested transport/rework | M2 heat/wear | M3 adaptive commitments |
|---|---|---|---|
| P0 recovery | none | little | slow decay of initial commitment at most |
| P1 orders on/off (production at recovery) | shipments lag / backlog drain after off | none | **supplier stock partial recovery during hold, overshoot after off** |
| P1 production 1.5 on/off | sag only if transport saturates; slow hangover | **slow decline during hold, rebound after** | effect modulated by commitment |
| P1 maintenance off/on (P9a style) | none | **gain then slow decline; loss then slow recovery** | none |
| P1 rush on/off | **congestion transient, delayed off (retained commitments)** | less treatment heat | none |
| P5 two high-load pulses, short vs long gap | 2nd worse after short gap | 2nd worse after short gap | 2nd order pulse depletes less |
| P9a maintenance vs idle pause (mix fixed) | same | **differs** | same |
| P9b rush before vs after dispatch | **differs** | same | same |
| P9c equal orders, opposite production sequences | small | differs (heat) | **differs strongly** |
| all-controls pulse & release | slow drain of congestion after release | slow capacity recovery | stock overshoot after release |

Pairs:
- **M1 vs M2:** maintenance off/on at constant load (P1 maintenance, P9a) → M2 only; rush timing (P9b) and
  order-driven transport load with effort at recovery → M1 only.
- **M1 vs M3:** orders on/off with production at recovery: M3 predicts supplier-stock overshoot after off, M1 predicts
  a slow backlog drain in shipments but no stock overshoot. P9b (rush timing) → M1 only.
- **M2 vs M3:** maintenance off/on with orders constant → M2 only; orders pulse with production and maintenance at
  recovery → M3 only; P9c separates by which history matters (effort vs orders).

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 (start) | — | — | 0 | 2,000 |

## 6. Run 1 observations and behaviour catalogue v1

(filled in below as segments arrive)

## Status / hand-off to reviewer

(Filled in at the end of Phase A.)
