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
| 2026-09-27 06:38 (start) | — | — | 0 | 2,000 |
| 06:39 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 06:40 | R1 | 40–79 (P1 order_quantity 80 on) | 40 | 1920 |
| 06:40 | R1 | 80–119 (orders on, ext) | 40 | 1880 |
| 06:41 | R1 | 120–159 (orders on, ext) | 40 | 1840 |
| 06:41 | R1 | 160–199 (orders off = recovery) | 40 | 1800 |
| 06:41 | R1 | 200–239 (recovery, ext) | 40 | 1760 |
| 06:42 | R1 | 240–279 (D = recovery + orders 80; 2nd order pulse after an 80-tick gap) | 40 | 1720 |
| 06:42 | R1 | 280–319 (D + production_effort 1.5) | 40 | 1680 |
| 06:42 | R1 | 320–339 (D, production back 1.0) | 20 | 1660 |
| 06:43 | R1 | 340–379 (D + receiving_effort 0.35) | 40 | 1620 |
| 06:43 | R1 | 380–409 (D, receiving back 1.5) | 30 | 1590 |
| 06:43 | R1 | 410–444 (D + rush: lead_time_buy 0.2) | 35 | 1555 |
| 06:43 | R1 | 445–469 (D + rush, ext) | 25 | 1530 |
| 06:44 | R1 | 470–499 (D, rush off) | 30 | 1500 |
| 06:44 | R1 | 500–534 (D + maintenance 0) | 35 | 1465 |
| 06:44 | R1 | 535–559 (D, maintenance back 1) | 25 | 1440 |
| 06:44 | R1 | 560–584 (D + product_mix 0.8) | 25 | 1415 |
| 06:44 | R1 | 585–599 (D + mix 0.8, ext) | 15 | 1400 |
| 06:45 | R1 | 600–624 (D, mix back 0.5) | 25 | 1375 |
| 06:45 | R1 | 625–669 (**all-controls pulse**, full reference pulse action) | 45 | 1330 |
| 06:45 | R1 | 670–749 (full recovery). **R1 complete: 750 steps** | 80 | 1250 |
| 06:58 | R2 (fresh reset) | 0–29 (P0 recovery) + 30–79 (D + production 1.5, P9c part 1) | 80 | 1170 |
| 06:58 | R2 | 80–129 (D + production 0.5, P9c part 2) | 50 | 1120 |
| 06:58 | R2 | 130–179 (P7: D + maintenance 0) | 50 | 1070 |
| 06:58 | R2 | 180–229 (P7 cont.) | 50 | 1020 |
| 06:59 | R2 | 230–279 (P7 cont.) | 50 | 970 |
| 06:59 | R2 | 280–329 (P7 cont.; 200-tick hold complete, settled) | 50 | 920 |
| 06:59 | R2 | 330–354 (P9a maintenance pause: D, maintenance 1) + 355–389 (D + maintenance 0) | 60 | 860 |
| 06:59 | R2 | 390–414 (P9a idle pause: D, maintenance 0, production 0) + 415–449 (D + maintenance 0) | 60 | 800 |
| 07:00 | R2 | 450–474 (D + maintenance 0, ext., instead of P2 q = 20 and final recovery) + 475–499 (P2: orders 40, rest recovery). **R2 complete: 500 steps** | 50 | 750 |

| 12:45 (Phase C) | R3 (fresh reset, `data/supply_chain/R3.json`) | 0–39 orders 20, rest recovery; 40–49 full recovery (reviewer G10/G3/G4 reserve probe) | 50 | 700 |

Total spent **1,300 of CAP 1,300** (R1 750, R2 500, R3 50); gateway reports 700 remaining. **No reserve left.**

## 6. Run 1 observations and behaviour catalogue v1 (`data/supply_chain/R1.json`, 750 ticks)

Initial reading: shipments 23.2, supplier 91.2, retail 109.1. Plot `data/supply_chain/R1_r0_battery.png`, battery
JSON `data/supply_chain/R1_battery.json`. "D" = demand baseline: the recovery action with order_quantity 80.

**Design change made during Run 1 (important):** at the recovery action nothing is ordered, so shipments are 0,
retail drains to 0 and the supplier sits at a hard cap (≈ 362). Production, receiving, rush, maintenance and mix
have nothing to act on there (production is blocked at the cap), so their P1s were run on top of D, as in traffic.
Every control still got an on/off P1. All-controls pulse and release was run at the end (ticks 625–749).

Settled / end-of-hold levels (means of the last ~10 ticks; the D level has a period-2 cycle 38.7/30.8):

| Setting (ticks) | shipments | supplier | retail (trend) |
|---|---:|---:|---|
| recovery P0 (26–39) | 0 | 361.6 (cap) | 0 (drained ~28/tick) |
| D first (120–159) | 34.8 (38.7/30.8 cycle) | ~329 | +3.8/tick, decelerating |
| recovery after D (225–239) | 0.46 → 0.10 (rework tail) | 361.5 | −15/tick |
| D second, S = 0 phase (250–262) | 26.3 | 0 | −3/tick |
| D + production 1.5 (305–319) | 34.8 (cycle) | ~327 | +3.5/tick |
| D (320–339) | 34.8 (cycle) | ~330 | +3/tick |
| D + receiving 0.35 (360–379) | **17.2** (no cycle) | ~346 | −3/tick |
| D (395–409) | 35.0 (damped, no cycle) | ~334 | +7/tick |
| D + rush (455–469) | **22.5** (after a burst to ~52) | ~339 | −7/tick |
| D after rush (490–499) | 29.2 (sagging) | falling 300 → 250 | −3/tick |
| D + maintenance 0 (510–534) | **43.8** | ~325 | +9/tick |
| D after maintenance (545–559) | 34.7 (cycle returns) | ~330 | ~0 (R ≈ 975) |
| D + mix 0.8 (585–599) | **27.8** (growing swing) | ~334 | −7/tick |
| D after mix (610–624) | ~33 (irregular) | ~330 | ~0 |
| all-controls pulse (650–669) | 17.2 → **19.3** | ~343 | −9/tick |
| recovery (740–749) | 0.1 → 0 | 362 | 0 (drained) |

Noise σ (second differences in smooth holds): shipments ≈ 0.1 (≈ 0.4 % of level; ≈ 0 at 0), supplier ≈ 1.35
(0 when empty), retail ≈ 2 (0 when empty). Score σ (0.1 × std after tick 20) ≈ 1.5 / 13 / 28.

### Behaviours (catalogue v1)

- **B1 Hard bounds dominate.** Supplier stock has a hard cap ≈ 361.8 (P0 26–39, recovery 160–240, 670–749; σ 1.35
  around it) and a floor 0 (53–102, 258–286). Retail has a floor 0 (4–42, 742–749) and no cap seen up to 983.
  Shipments are exactly 0 with no orders once the pipeline is empty. Explanation: base (stocks with capacity and
  "orders withdraw only available stock"). Status: open → base; fix Smax with `--fix`.
- **B2 Reset transient.** Shipments are 0 from tick 0 whatever the reading ("conveyors start empty"). Supplier
  holds for 2 ticks then fills at +12/tick to the cap (production pipeline delay ≈ 2). Retail drains at 27.7/tick
  from the reading to 0 in 4 ticks. Status: base (empty pipelines; initial S, R from the reading).
- **B3 Production rate.** Fill rate with no orders ≈ 12/tick at effort 1 (P0). Refill under orders (dispatch
  blocked, see B5) alternates 13/6 (mean 9.5) at effort 1 (ticks 102–140) and 18/24.5 (mean 21) at effort 1.5
  (284–301): **effort 1.5 ≈ ×2 production**. Effort has no visible effect while the supplier is at its plateau
  (production back to 1.0 at 320: nothing). Status: base (production ∝ effort^~1.5–2).
- **B4 Order withdrawal and dispatch.** Orders on: the supplier drops by exactly one order (≈ 80) on the first
  tick, stays flat 3 ticks, then falls ≈ 33/tick. First pulse: −33/tick for 8 ticks, then −24, −16, −10 → 0
  (tick 53). **Second pulse (240, after 80 ticks off): −33 for only 3 ticks, then −16/tick** → 0 at 258. The
  slower drawdown on the second pulse means supply-side inflow rose by ≈ 17/tick **and remembers the first order
  period** (candidate M3 adaptive commitments; or class composition of the stock). Status: open → m3 / base.
- **B5 Supplier plateau under orders.** Under sustained D the supplier refills (at the production rate, so
  dispatch ≈ 0 then) to a plateau ≈ 329 = cap − ≈ 33 (≈ one tick of shipments), and jumps back to the cap on the
  **first** tick after orders stop (160, 670). The plateau is 346 at receiving 0.35 (shipments 17.2) and 325 at
  maintenance 0 (43.8): **plateau ≈ cap − shipments**. So under orders the supplier is refilled every tick and
  withdraws one tick of terminal throughput: production capacity under orders ≥ 44/tick, far above the 12/tick
  no-order fill rate (strong order-driven production; M3 or make-to-order in the base). Status: open.
- **B6 Shipments = terminal service rate under orders; pipeline dead time 3.** First shipments 3 ticks after
  orders on (43, 244). Level: 25.3 for ~20 ticks (while the supplier is draining / empty), then the service level.
  Service level (queue full): 34.8 at recovery staffing; **17.2 at receiving 0.35 (instant, no delay)**; 43.8
  with maintenance 0 (4 ticks delay; "maintenance shares drive service with receiving"); 27.8 at mix 0.8 (≈ 19
  ticks delay: mix acts on new batches only); 22.5 under sustained rush; 19.3 in the all-controls pulse. Status:
  base (service rate μ(receiving, maintenance, mix, rush)).
- **B7 Period-2 limit cycle.** At D with maintenance 1 shipments alternate 38.7/30.8 (sum constant 69.5) with
  σ ≈ 0.1: grows from a small perturbation within ~15 ticks (65–80, 263–270, 535–550) and persists; absent at
  receiving 0.35, with maintenance 0, and for 30 ticks after receiving was restored (380–409, damped instead).
  Supplier also alternates (±4) in phase. Explanation: drive service shared by receiving and maintenance
  alternating tick by tick. For the |error| score the best smooth forecast is the mean 34.8. Status: note for
  modeler (predict the mean).
- **B8 Large in-transit backlog; drain after orders stop.** After orders stop, shipments continue at the service
  level for ~20 ticks, then 25 (6 ticks), ~50 (6), ~43 (9), then fall in **10-tick blocks with ratio ≈ 0.21**
  (45 → 9.5 → 2.1 → 0.46 → 0.10 → 0.02; ticks 202–240 and 704–750). ≈ 1,650 goods were in transit at 160. The
  10-tick geometric tail is the **rework loop**: ≈ 21 % of goods return for rework and come back 10 ticks later
  ("Goods needing rework may return to the primary intake"). The burst to ~50 after orders stop exceeds the
  service level (35) → part of the drain bypasses the terminal limit or the terminal speeds up when not
  dispatching. Status: open → base (backlog queue + 10-tick rework loop with fraction φ ≈ 0.21) and m1 candidate
  (congestion).
- **B9 Rush: burst, then lower sustained throughput, history after release.** Rush on at 410: after 5 ticks
  shipments dip to 26 (15 ticks), then rise to ~50 (25–40 ticks after), then **fall to 22.5 and stay** (from 40
  ticks after). Rush off: 31 after 5 ticks, then a slow sag to 29.2, and the supplier starts draining
  (340 → 250 over 30 ticks) — the pre-rush D state (35, plateau 333) is **not** restored within 30 ticks. The
  sustained drop under rush fits "rush bypasses treatment" → untreated goods need rework → more rework load
  (M1 congested transport and rework) or treatment heat avoided; the lasting after-effect is a memory. Status: open
  → m1 candidate / base delay stages (commitment retained after a rush change).
- **B10 Maintenance off raises throughput immediately; no wear decline within 35 ticks.** Maintenance 0: 29 → 33
  at once, 43.8 after 4 ticks, flat for 30 ticks (no visible wear build-up). Maintenance back on: 29.3 then the
  period-2 cycle around 34.7. So maintenance costs ≈ 9/tick of terminal throughput. A slow wear effect (M2)
  would need a much longer hold. Status: open → P9a / P7 in Run 2.
- **B11 Mix 0.8 lowers throughput after a delay.** Shipments 34.8 → 25–30 after ≈ 19 ticks (new batches only),
  supplier plateau +10 after 9 ticks; back to ≈ 33 after ≈ 8 ticks when the mix returns to 0.5. Status: base (mix
  on service/dispatch with a delay).
- **B12 Retail sales are not constant.** Implied sales (shipments − Δretail) ≈ 28 in the reset drain, 15–17 while
  draining after the first order period (205–240), 12 during the last drain (725–740), 17 in the first 20 ticks
  of orders (45–60), 20.5 at shipments 17.2, 29–32 at shipments 35, 34–37 at shipments 44 / retail ≈ 980. Sales
  follow recent arrivals (battery: shipments → Δretail corr 0.76 at lag 0) and are higher when retail is large.
  Candidate: two goods classes with separate demand, sold only while that class is in stock ("Supplier goods
  have two classes"). Status: open → base (sales = D0 + g·smoothed shipments, clipped at stock) as a first pass.
- **B13 All-controls pulse and release.** Pulse: shipments 17.2 at once (receiving-limited), 19.3 after 25 ticks;
  supplier ~343; retail −9/tick. Release: burst 40 (5 ticks), 30/27 (15), **~53 for 12 ticks**, then 21, 13.6,
  12.0 in 5–10 tick blocks, then the rework tail 0.6 → 0.1. Supplier back to the cap at once. Status: base (drain
  of the stored backlog at the recovery service rate plus rework tail).

Mechanism evidence so far (Run 1):
- **M3 adaptive production commitments:** B4 (second order pulse drains the supplier half as fast, 80 ticks after
  the first) and B5 (production under orders ≫ fill rate without orders) → supply adapts to orders with memory.
  Supplier overshoot after orders stop cannot be seen because the supplier sits at its cap.
- **M1 congested transport/rework:** B8 (10-tick rework loop, large backlog), B9 (rush → lower sustained throughput
  and a slow after-effect). Rework is part of the base; congestion memory is the mechanism question.
- **M2 heat/wear:** no direct evidence yet (maintenance off gave a flat 35-tick hold; production 1.5 invisible at
  the plateau). Needs a long no-maintenance hold and the P9a maintenance-vs-idle comparison.

## 7. Model module v0 (`greybox/supply_chain_model.py`)

Mechanistic queue network (the template relaxation model cannot represent caps, floors and the retail
integrator). Full equations in the module docstring. Base (always on):

- **Production**: release = e^pe·(p0 + po·Po)·(…) with Po a fast lag of q/80 (make-to-order term in the base, so
  that the base can reach the high production seen under orders, B5); DP = 2-tick pipeline; supplier
  S = min(S + arrivals, Smax), **Smax fixed at 361.8** (B1).
- **Dispatch** after service: d = min(q, S, dcap, Bmax − queue − in transit − in rework loop). Counting goods in
  flight removed a model sawtooth that the first version had (dispatch switching on/off with the 10-tick loop).
- **Transit** DT = 3 ticks (B6), terminal queue B served at μ = mu0·(r/1.5)^ar·(1 + wm·(1−m))·(1 + wmix·(mix_lag −
  0.5))·(1 + wl·(1 − lt_lag)); mix and lead time act through first-order lags (B9, B11).
- **Rework loop**: fraction φ of served goods returns after LR = 10 ticks (B8); shipments = (1 − φ)·served.
- **Retail**: R ← R + ship − sales, sales = min(R + ship, D0 + Dg·Ss + dz·z), Ss a slow average of shipments,
  z a decaying reset term (B2, B12).
- Units linear for all three (hard 0 floors and caps make logs useless); fit σ = 1.5 / 10 / 25 (≈ score σ).

Mechanism modules, written from the theses before fitting (gain 0 = off):
- **m1 congested transport and rework**: Cg ← Cg + a1·(B/Bmax − Cg); service × (1 − g1·Cg); rework fraction
  φ + g1r·Cg.
- **m2 machine heat/wear**: H ← H + a2·(e/1.5·(1 − m) − H) (use without maintenance); service × (1 − g2s·H),
  production × (1 − g2p·H).
- **m3 adaptive production commitments**: Cm ← Cm + (a3u | a3d)·(q/80 − Cm) (builds / fades at different rates);
  production + e^pe·g3·Cm.

Not modeled (noted for the modeler): the period-2 cycle (B7; predict its mean), the shipment levels 25.3 vs 35 in
the first ~20 ticks of an order period, the rush burst (B9), the post-order bursts to ~50 (B8, B13), class
structure of sales (B12).

**Base fit on R1** (`fits/supply_chain/base_r1c.json`, plot `base_r1c.png`): cost 5814.6, train score 0.525
(σ = 0.1×std; persistence 0.109). Converged: four chained passes from the best give the same cost. The optimizer
stops early on this piecewise (min/clip) model and restarts with perturbation 0.1 land in bad basins
(cost 33k–57k), so fits are chained with perturbation 0.02–0.03 (`fits/supply_chain/chain.sh`).

## 8. Run-1 pair fits (for probe ranking)

Chained fits (`fits/supply_chain/chain.sh`) from the converged base, gains started at their SPEC defaults (not 0).
Cost on R1 (σ 1.5/10/25, soft_l1), train score at σ = 0.1×std:

| Fit | Cost | Train score | Mechanism parameters |
|---|---:|---:|---|
| base (no mechanism) | 5814.6 | 0.525 | — |
| **m1+m2** | **5256.1** | 0.551 | m1: g1 = 0 (service unaffected), **g1r = −0.14** (rework *falls* with queue fill), a1 0.031; m2: g2p 0.088 but **a2 → 0** (H never builds: m2 inactive) |
| m1+m3 | 5346.3 | 0.547 | m1: g1 = 0, g1r = −0.15; m3: g3 = 42.8 goods/tick, builds slowly (a3u 0.025) and fades fast (a3d 0.26) |
| m2+m3 | 5529.7 | 0.530 | m2: a2 0.97 (instant), g2p 0.10; m3: a3u → 1 (instant), **a3d → 0 (never fades: an integrator, pinned)**, g3 8.2 |

Reading (quick fits, not a verdict): m1's gain works through a *negative* rework term (less rework when the queue
is full), which is really a patch for the shipment levels 25 vs 35 (B6) rather than congestion; m2 is unused in
m1+m2 and pinned instant in m2+m3; m3 in m2+m3 is a pinned near-integrator. Parameters pinned at limits = missing
structure (framework lesson 9). The m1 − m2 − m3 evidence has to come from Run 2.

## 9. Run 2 design (§4.4)

Candidates simulated through m12, m13, m23 (`fits/supply_chain/rank_probes.py m12_r1 m13_r1 m23_r1`, run from the kit folder), ranked by the
smallest pairwise disagreement (mean |Δ|/score σ over the probe; a probe must separate every pair):

| Candidate | Steps | min pair | per 100 steps | m12/m13 | m12/m23 | m13/m23 |
|---|---:|---:|---:|---:|---:|---:|
| **P9c production high→low under D** (1.5 then 0.5) | 160 | **2.34** | 4.58 | 2.58 | 2.34 | 2.40 |
| **P9a idle-then-maintenance after D+m0** | 220 | 1.38 | 2.46 | 1.38 | 2.40 | 1.63 |
| P9a maintenance-then-idle | 220 | 1.09 | 2.30 | 1.09 | 1.96 | 2.02 |
| P5 short order gap (20) | 160 | 1.07 | 4.00 | 2.36 | 1.07 | 2.97 |
| P9c production low→high | 160 | 0.84 | 2.72 | 1.82 | 0.84 | 1.69 |
| all-pulse 60 + recovery 60 | 120 | 0.74 | 2.38 | 1.03 | 0.74 | 1.09 |
| all-pulse, gap 20, all-pulse | 160 | 0.54 | 3.47 | 2.37 | 0.54 | 2.63 |
| P7 all-pulse hold 200 | 200 | 0.43 | 0.98 | 0.63 | 0.43 | 0.91 |
| P2 orders 40 | 100 | 0.28 | 1.60 | 0.28 | 0.57 | 0.75 |
| P9b rush at order start / after dispatch | 80 / 100 | 0.27 / 0.25 | 2.6 / 2.5 | 0.27 / 0.25 | 0.82 / 1.06 | 0.98 / 1.20 |
| P5 long order gap (80) | 220 | 0.27 | 1.01 | 0.27 | 0.89 | 1.06 |
| P7 D + maintenance 0 hold 200 | 200 | 0.19 | 1.92 | 0.19 | 1.77 | 1.89 |
| mix 0.2 under D | 80 | 0.12 | 3.51 | 0.12 | 1.37 | 1.32 |
| P7 D hold 200 | 200 | 0.09 | 1.14 | 0.09 | 1.09 | 1.10 |
| rush 100 under D | 150 | 0.08 | 2.70 | 0.08 | 2.00 | 1.96 |
| production 0 under D | 80 | 0.06 | 0.96 | 0.06 | 0.37 | 0.34 |

**Chosen Run 2 (fresh reset, 500 steps):**

| Block | Ticks | Steps | Purpose |
|---|---|---:|---|
| P0 recovery | 0–29 | 30 | reset transient, 2nd initial reading |
| D + production 1.5 | 30–79 | 50 | **P9c** first half (high effort first) |
| D + production 0.5 | 80–129 | 50 | **P9c** second half (low; production below recovery = other side of recovery, tip 10). Opposite sequence is R1 (1.0 → 1.5) |
| **P7** D + maintenance 0 | 130–329 | 200 | long hold near the pulse: wear build-up (M2), commitments (M3), long-run retail/supplier levels |
| **P9a** maintenance pause (D, maintenance 1) | 330–354 | 25 | maintenance vs … |
| D + maintenance 0 | 355–389 | 35 | throughput after the maintenance pause |
| **P9a** idle pause (D, maintenance 0, production 0) | 390–414 | 25 | … idle pause, mix fixed at 0.5 throughout; production 0 = other side of recovery |
| D + maintenance 0 | 415–449 | 35 | throughput after the idle pause |
| **P2** orders 40, then 20 | 450–489 | 40 | mid-level orders (above / below the service rate) |
| recovery | 490–499 | 10 | release |

Pair disagreement of this exact schedule (σ units, mean over each block): P9c low-effort block m12/m13 3.72,
m13/m23 4.17; P7 m12/m23 3.2, m13/m23 3.8; P9a blocks m12/m23 3.8–5.3, m12/m13 0.3–1.2 (weakest pair). Not
included for budget: P9b (rush before/after dispatch; low ranking, R1 already has "after"), P5 long gap (R1 has
an 80-tick gap), all-pulse repeat (in R1). The idle pause keeps orders on, so it also gives a production-0
drawdown.

**Change during Run 2:** the last 50 steps were used for 25 more ticks of D + maintenance 0 (to time how long the
post-idle-pause state lasts, which is the real P9a comparison) and 25 ticks of P2 at orders 40. The planned
orders-20 block and the final 10-tick recovery were dropped (both ranked low; release was seen twice in R1).

## 10. Run 2 observations and behaviour catalogue v2 (`data/supply_chain/R2.json`, 500 ticks)

Initial reading: shipments 33.0, supplier 88.9, retail 99.0. Plots: `data/supply_chain/R2_r0_battery.png` (run),
`fits/supply_chain/r1fits_on_R2.png` (R1 fits predicting R2). Battery JSON `data/supply_chain/R2_battery.json`.

| Setting (ticks) | shipments | supplier | retail |
|---|---:|---:|---|
| recovery P0 (26–29) | 0 | 362 (cap, filled at 11.7/tick) | 0 |
| D + production 1.5 (72–79) | 34.8 (38.7/30.8 cycle) | ~324 | +5/tick |
| D + production 0.5 (110–129) | **36.1 (no cycle)** | falling (−12 then −3/tick) | +5/tick |
| D + maintenance 0, first 45 ticks (135–176) | 43.8 | refill +7/tick → 323 | +11/tick |
| D + maintenance 0, ticks 177–217 | ~41 (32/50 cycle) | ~320 | +7/tick |
| **D + maintenance 0, settled (218–329)** | **37.2** | **324.5** | **1,180 flat** (sales = shipments) |
| maintenance pause (335–354) | ~33 (irregular) | ~329 | −4/tick |
| D + m0 after maintenance pause (355–376 / 377–389) | ~41 (swing) / 37.3 | ~321 | +3 / 0 |
| idle pause, production 0 (393–414) | 37.2 (16 ticks), then 21.6 | back to cap 362 | ~+1 |
| D + m0 after idle pause (416–418 / 419–440 / 441–466 / 467–474) | 0–3 / 31.7 / ~42 (35/49 cycle) / 37.3 | falls to 99, then refills +10/tick | −5, then +7 |
| orders 40, rest recovery (475–499) | ~31.5 (25.2/38–40 cycle) | falling −6/tick | −5/tick |

Behaviours added or updated (catalogue v2):

- **B2 (updated) Reset transient reproducible:** second reset, fill at 11.7/tick, cap reached at tick 26; retail
  drained in 4 ticks (99 → 72 → 44 → 16 → 0: 27.5/tick). Shipments 0 from tick 0 despite a reading of 33.
- **B3 (updated) Production effort under orders.** D + production 1.5 from recovery: the supplier drain is much
  slower than at effort 1 (never reaches 0; minimum 21 at tick 60) and then refills at **+36/tick** to the plateau.
  D + production 0.5: plateau held 15 ticks, then −12/tick, slowing to −3/tick after ~10 ticks (supply catching up
  while the hold continues; M3-like adaptation, or the drain of an upstream buffer). Effort 0.5 **removes the
  period-2 cycle** at once and gives a steady 36.1 (drive-service sharing: effort loads the drive shared with
  receiving).
- **B14 Idle pause stops dispatch.** With production 0 and orders on, the supplier goes **up** to its cap within 3
  ticks (dispatch stops; the primary line also carries dispatch), shipments continue from the in-transit backlog
  for 16 ticks, then 21.6. On restart shipments fall to **0 for 3 ticks**, then 31.7 for 22 ticks, and the
  supplier drains to 99 before refilling. The v0 model gets this badly wrong (predicts dispatch continuing and
  the supplier at 0). Status: **not captured** (base: dispatch must depend on production effort).
- **B15 Throughput degradation under sustained no-maintenance operation (M2 or M1 candidate).** Fresh from
  maintenance 1: 43.8 for 45 ticks, then a 32/50 cycle (mean ~41) for 40 ticks, then a sudden drop to a steady
  37.2 from tick 218 (≈ 88 ticks after maintenance stopped), stable for 110 ticks (P7, settled). After a 25-tick
  maintenance pause the elevated state (~41) returns for **22 ticks**; after a 25-tick idle pause it returns for
  **26 ticks** (after a 22-tick restart phase at 31.7). So both pauses restore throughput for a similar time. This
  fits heat that cools in any pause (M2 heat) or a congestion/rework state that drains whenever load drops (M1)
  better than wear that only maintenance repairs. A wear-only M2 would predict no restoration after the idle
  pause. Status: open → m2 (heat) vs m1: needs the modeler's pair fits on R1 + R2.
- **B16 Retail self-limits.** Under D + maintenance 0 retail stops rising at ≈ 1,180 with sales = shipments
  = 37.2 (R1: flat at ≈ 975 with shipments 34.7). So the sales rate rises with the retail level until it matches
  arrivals: retail has a **shipment-dependent equilibrium level**, not an unbounded integral. Important for
  4,000-step forecasts. Status: base (sales must increase with R; v0 uses a slow average of shipments instead).
- **B7 (updated) Period-2 cycle** appears at D with maintenance 1 and effort ≥ 1, in the post-pause elevated
  states with maintenance 0, and at orders 40 (25.2/38–40); absent at effort 0.5, receiving 0.35, and in the
  settled maintenance-0 state. Forecast target: its mean.
- **B17 P2 orders 40:** shipments cycle 25.2/38–40 (mean ≈ 31.5) with the supplier draining at 6/tick; the order
  level matters even above the service rate (dispatch ≤ q). 25 ticks only: not settled.

**Separating probes and P9s actually run (and what they showed):**

| Probe | Run / ticks | Result |
|---|---|---|
| P9a maintenance vs idle pause (mix fixed 0.5) | R2 330–474 | both pauses restore the elevated throughput for 22–26 ticks; the immediate response differs (idle: 3 ticks of 0, then 22 ticks at 31.7). Favors heat (M2) or congestion (M1) over pure wear |
| P9b rush before vs after dispatch | R1 410 ("after" only) | **not run as a comparison** (low ranking); only the "after" arm exists |
| P9c equal orders, opposite production sequences | R1 240–340 (1.0 → 1.5 → 1.0) vs R2 30–130 (1.5 → 0.5) | not exactly equal sequences; the drain with effort 1.5 first is much slower and the refill much faster; effort 0.5 second gives a slowing drain. Evaluate with the fitted pairs |
| P5 gap test | R1 order pulses 40 and 240 (80-tick gap) | second drawdown half as steep after 3 ticks (B4): supply remembers the earlier order period (M3) |
| P7 long hold ≥ 200 | R2 130–329 (D + maintenance 0) | settles after ~88 ticks at 37.2 / 324.5 / 1,180; no further drift over 110 ticks |
| P2 orders mid level | R2 475–499 (q 40) | 31.5 mean, supplier draining; short |
| P3 joint top-2 | R1 (D + receiving 0.35; D + production 1.5), R1 all-controls pulse | orders × receiving = 17.2 (receiving-limited) |
| All-controls pulse and release | R1 625–749 | B13 |
| Other side of recovery | production 0.5 and 0 (R2); mix < 0.5 **not tested** | effort 0.5 removes the cycle; effort 0 stops dispatch |

**Cross-run check (fit on R1, predict R2; score σ = 0.1×std over R1+R2):**

| Model | R2 score | shipments | supplier | retail |
|---|---:|---:|---:|---:|
| persistence | 0.137 | 0.237 | 0.084 | 0.088 |
| base v0 | 0.353 | 0.351 | 0.430 | 0.278 |
| m1+m2 | **0.388** | 0.295 | 0.434 | 0.434 |
| m1+m3 | 0.372 | 0.296 | 0.435 | 0.386 |
| m2+m3 | 0.365 | 0.434 | 0.454 | 0.207 |

The differences between pairs are small compared with the base-structure misfit (B14 idle pause, B3 supply under
orders, B16 retail level); see `fits/supply_chain/r1fits_on_R2.png`.

## Status / hand-off to reviewer

**Files**
- Plan (this file); data `toronto26-participant-kit/data/supply_chain/R1.json` (750 ticks),
  `R2.json` (500 ticks); battery plots/JSON `data/supply_chain/R{1,2}_r0_battery.png`, `R{1,2}_battery.json`.
- Model v0 `toronto26-participant-kit/greybox/supply_chain_model.py`; fits in `fits/supply_chain/`
  (`base_r1c.json` converged base; `m12_r1.json`, `m13_r1.json`, `m23_r1.json` R1-only pair fits; `chain.sh`
  chained-fit helper; plots `base_r1c.png`, `r1fits_on_R2.png`).

**Budget:** 1,250 spent (R1 750, R2 500), 750 remaining on the gateway, **50 reserve** before the 1,300 cap.

**Open issues (reviewer, look here first)**
1. **Base structure is the main error, not the mechanisms.** The v0 base misses: dispatch depending on production
   effort (B14: idle pause stops dispatch and refills the supplier), supply under orders far above the no-order
   fill rate (B3/B5: +36/tick refill at effort 1.5), the retail equilibrium (B16: sales rise with retail stock),
   the 25-vs-35 shipment phase at the start of each order period (B6), and the rush response (B9). Pair
   comparisons on top of this base are not trustworthy yet (tip 6).
2. **Mechanism evidence:** M3 from B4 (second order pulse drains half as fast after an 80-tick gap) and B3 (drain
   slows during effort 0.5); M1 or M2-heat from B15 (throughput drops after ~88 ticks without maintenance and is
   restored equally by maintenance and idle pauses). Pure wear (repaired only by maintenance) looks unlikely.
   The R1 pair fits pin parameters (m2 rate → 0 in m1+m2; m3 fade → 0 in m2+m3; m1 acts only through a negative
   rework term), so they are not evidence yet.
3. **Not run:** P9b (rush before vs after dispatch) as a comparison; mix below 0.5 (other side of recovery);
   orders below the service rate (q ≈ 20); a long recovery after heavy load is short (≤ 80 ticks) but recovery
   levels are trivial (cap / 0 / 0).
4. **Period-2 cycle (B7)** and bursts after orders stop (B8, B13) are real but not smooth; the forecast should
   target their mean. The cycle appears and disappears with effort, maintenance and receiving.
5. **Fitting:** the piecewise model makes least_squares stop early; restarts need a small perturbation
   (0.02–0.03). Chained passes (`fits/supply_chain/chain.sh`) converge the base to cost 5814.6 on R1.
6. The 50-step reserve is best spent on P9b (rush switched on together with orders vs 20 ticks after), or on
   orders ≈ 20 (below the service rate).

## 11. Phase C: review responses (modeler, 2026-09-27 afternoon)

Model: `toronto26-participant-kit/greybox/supply_chain_model.py` (v1; the pre-review v0 is kept as
`greybox/supply_chain_model_v0.py`). Fits and scripts: `fits/supply_chain/v1/`. Reserve probe R3 spent (50 steps,
see §5): orders 20 from reset for 40 ticks, then 10 ticks of recovery.

**R3 findings.** Shipments are 0.78 × 20 = 15.6 from tick 3 (no queue, no class-2 delay at mix 0.5), step to 19.0
at tick 13 when the first rework (22%) returns 10 ticks later, then about 20. After the stop, 4 ticks at 20, then a
flat 4.4 = 0.22 × 20 rework tail. Retail stays at 0 the whole time (sales ≥ 20 at R = 0). The supplier climbs
about 1.6 per tick at q = 20 and 11–20 per tick after the stop. So φ ≈ 0.22 is directly measured, and the
reviewer's F2 (mix splits dispatch into a 21-tick class-2 path) is falsified at low orders.

| Gap | Response |
|---|---|
| G1 clock-like parameters | **Fixed.** Every rate and gain now has hard bounds via a scaled sigmoid (`BOUNDS`): memory rates in [0.005, 0.5], gains g1/g2s/g2p ≤ 0.5, g1r ≥ 0, `az` ≥ 0.05, `al` ≥ 0.02; `simulate` also clips hand-edited values. Retail `aS`/`Dg` (the slow sales memory) were removed. The 4,000-tick held-action table (`v1/stab.py`) shows no drift in shipments or supplier and ≤ 17 in retail (< 0.5σ). |
| G2 mix / rush integrators | **Fixed.** Mix acts through a fixed 19-tick delay with factor `1 + wmix·clip(mix − 0.5, ±0.3)`, `wmix` ∈ [−1.5, 1.5] (fit −0.46). Rush uses a lag with `al` ∈ [0.02, 0.5] and `wl` ∈ [−1, 1] (fit ≈ +0.09, i.e. rush is nearly neutral in the mean). Held mix 0.8 or 1.0 now gives 27.4 shipments (data ≈ 28), mix 0 gives 36.1. |
| G3 long-run retail | **Improved, not solved.** Sales = min(R + ship, D0 + kR·R + dz·z) (fit D0 = 18, kR = 0.017). At D the model settles at 781 (data ≈ 975), with maintenance 0 at 1,264 (data ≈ 1,180). The residual error is inherited from the D-level shipment bias (G5): with the true 34.8 the same law gives ≈ 954. q = 20 gives ≈ 100 (data: 0 over the 40 observed ticks). Loss weighting of settled ticks was not tried (time). |
| G4 release tail / burst | **Partly.** `Bmax` bounded to [200, 2000] (fit 1,270, from 2,470). An idle-service boost `wid` (service × (1 + wid) when no transit arrivals) was added, but the fit sets it to 0, so the burst to ≈ 50 is still missed. |
| G5 D-level bias | **Tried, not adopted.** Fitting on a [¼, ½, ¼]-smoothed shipments target with φ fixed at the R3 value 0.215 (`v1/phi_all.json`) raised D to 32.9 but lowered the raw-data score (0.509 vs 0.512) and the cross-run score (0.419 vs 0.464). D is still 31.7 vs 34.8 in the shipped fit. |
| G6 25-then-35 phase | **Fixed structurally.** Dispatch fills a fast path (DT = 3) up to rate `c1` (fit 30) and the overflow takes the 21-tick path. This gives ≈ 25 then ≈ 32 at orders 80 and the exact R3 behaviour at orders 20. |
| G7 idle-pause restart | **Not captured.** Effort 0 still stops production (`e^pe`), so the supplier holds instead of refilling to the cap. The data suggest effort gates dispatch more than production; left open. |
| G8 B15 step, G9 B4 second drawdown | **Not captured.** With bounded rates, M1+M2 and M1+M3 fitted on R1 converge to the base cost (6,219.9, identical) — the modules stay unused. The pair question is **not identifiable** with this base; M2+M3 and the bootstrap were not run (time). |
| G10 coverage | R3 covers orders < service rate. Mix < 0.5, lead 0–0.2, receiving < 0.35 remain extrapolations (bounded by construction). |
| G11 fitting | Fits now take 10–50 s (bounded parameters, `--max-nfev` 600–800). |

## 12. Phase C: final model and hand-off

**Model-selection record.**

| Candidate | Data | Cost | Score (raw R1–R3, σ = 0.1×std R1+R2) | Cross-run R1 → R2 |
|---|---|---:|---:|---:|
| v1 base, no mechanisms (`v1/base_all2.json`) | R1+R2+R3 | 10,812.7 | **0.512** | **0.464** (`v1/base_r1.json`) |
| v1 base, φ fixed 0.215, smoothed target (`v1/phi_all.json`) | smoothed R1–R3 | n/c | 0.509 | 0.419 |
| v1 + M1+M2 / M1+M3 | R1 | 6,219.9 (= base) | — | — (modules unused) |
| persistence | | | 0.128 | 0.137 |

**Decision: not identifiable → ship the v1 base without mechanism modules** (as the reviewer advised). Confidence in
the pair: none; confidence the base is safe: good.

**Gates.** Local score beats persistence cross-run (0.464 vs 0.137): pass. Contract (40 × 4,000 steps from the
extracted ZIP, all malformed-input cases): pass, 50.8 s. Stability (`v1/stab_gate.json`): no range failures (max
shipments 49.7, supplier ≤ 361.8, retail ≤ 1,817 over 200 schedules + 8 × 40,000 steps), but **61 sawtooth flags**.
Checked by hand: every flag is the 10-tick rework loop echoing an earlier fast "switch" schedule and decaying
geometrically inside the next hold (mean |Δ| ≤ 3.2 in the first 40 ticks, ≤ 0.008 in the last 40; the level tends
to 0, which inflates the relative amplitude). The real system shows the same 10-tick rework echo (R1 680–750, R3
40–49). **Accepted as a false positive.**

**Package.** `toronto26-participant-kit/models/supply_chain/` (predict.py, model copy, params.json) and
`toronto26-participant-kit/submission-supply_chain-v1.zip` (5.8 kB); package check passed (roots, credential scan,
contract).

**Budget.** 1,300 of CAP 1,300 spent; gateway 700 remaining (not to be used under this CAP).

**Top open issues.**
1. D-level shipments 31.7 vs 34.8 (−2.5σ on every sustained-operation tick) and the resulting retail level (781 vs
   975). A service-rate structure that reproduces both the φ = 0.22 rework and the 35 level is still missing.
2. Release burst to ≈ 50 (G4) and idle-pause restart / effort-0 supplier refill (G7) not captured.
3. Mechanism pair unresolved: no module reproduces B15 or B4; a threshold heat state (G8) and a withdrawal-rate
   commitment (G9) are the next candidates.


## Round 2 spend log (approved by the user 2026-09-28; schedules in `plans/round2-experiments.md`)

| Date | Run | File | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-28 14:44–14:55 UTC | SU1 (fresh reset) | `data/supply_chain/R4.json` | 400 | 300 |
| 2026-09-28 14:44–14:55 UTC | SU2 (fresh reset) | `data/supply_chain/R5.json` | 200 | 100 |

Segment files: `toronto26-participant-kit/fits/round2/segments/supply_chain_*.json`. Server budget confirmed after the runs.

## Round 2 model (v2)

Modeler pass, 2026-09-28. No steps spent (reserve 100 untouched). Module `toronto26-participant-kit/greybox/supply_chain_model_v2.py`;
fits, scripts and logs in `toronto26-participant-kit/fits/supply_chain/round2/v2/` (`run.py` fitter/protocol, `pipeline.sh`
staged fit, `table.py`, `longrun.py`, `segtab.py`, `plot.py`, `retail_explore.py`). Final params `v2/final_v2.json` (= `v2c_C.json`).

**Diagnosis items addressed and structural changes** (every other v1 part unchanged; no mechanism modules, as v1):

| Item | Change |
|---|---|
| §5.1 / B18, B19, B20 service structure | `mu0·(r/1.5)^ar·(1+wm(1−m))·…` replaced by `mu = smin(kr·r·(1 + kp·lift), U)` (soft-min, width 1). `U = U0·(1+wm(1−m))·mix·rush·idle` — maintenance acts on U only. `lift` = mean of the clipped pulse-side u of rush, mix and effort (source of the joint-pulse +10% unidentified, so the risk is spread over the three). Fit (C): kr·(1−φ) = 49.5·r (data 49.2), kp = 0.083. |
| B21 supply-limited phase | fast path capacity `c1·e^ce` — **did not earn its keep** (ce fits to 0 in every fold); harmless, left at 0. |
| §5.2 / B25 retail | sales = min(R+ship, D0 + kR·R + g·E + dz·z), E an asymmetric bounded EMA of shipments (aup/adn ∈ [0.005, 1]). Fit: g 0.23, aup 0.07, adn ≈ 1. On observed shipments the best law found still only reaches 0.45–0.52 on R4/R5 (`retail_explore.py`); the retail law remains structurally wrong. |
| rush (not in diagnosis; found here) | rush factor `1 + wl·((1−ll)/0.8)^nl`, wl ∈ [−1, 0], lag al ≥ 0.1, nl ∈ [1, 8]. R1 (l 0.2 alone) gives −35%; R4 u.7 (l 0.44) shows ~no penalty, hence the power. **With v1's bounds (wl ∈ [−1, 1], al ≥ 0.02) the all-data fit pinned al at 0.02 and used rush as a slow clock for the R1 burst: rush alone → 48 shipments, supplier 0, retail 1,739 at 4,000 ticks.** That variant (`v2_*`) was rejected; the bounded one is `v2c_*`. |
| §5.3 supplier (make-to-order, 27-tick path), §5.4 release burst (`wid`) | **Not done** (time; see open issues). `wid` still fits to 0. |

**Fitting.** `greybox.common.fit`'s least_squares stopped after 6–19 evaluations (finite-difference step too small for the
min/clip structure). `run.py` uses `diff_step = 1e-3`, 2 restarts, and a **staged** fit: s1 flow + supplier params with retail
weight 0; s2 retail params only, flow frozen. A joint s3 pass (all params, 12 min) lowered cost but made held-out worse
(A 0.512 vs 0.547), so it is not used. Residual σ = score σ (1.12 / 12.1 / 34.7).

**Held-out scores** (σ = 0.1 × std after tick 20 of R1–R5, as `fits/round2/heldout.py`; per observable shipments / supplier / retail; mean):

| Variant | (A) fit R1–R3 → R4+R5 | (B) → R4 (fit R1–3+R5) | (B) → R5 (fit R1–3+R4) | (C) all data, R1–R5 in-sample | Old runs in-sample (fit A / fit C) |
|---|---|---|---|---|---|
| v1 shipped (= v1 fit on old) | 0.218 / 0.681 / 0.159 = **0.353** | — | — | — | 0.420 / 0.564 / 0.680 = 0.555 |
| v1 structure refit (`v1r_ls_*`) | = v1 (0.353) | 0.250 / 0.624 / 0.160 = 0.345 | 0.345 / 0.733 / 0.222 = 0.433 | 0.431 | — / 0.409 |
| v2 unbounded rush (`v2_*`, rejected) | 0.571 / 0.694 / 0.376 = 0.547 | 0.418 / 0.637 / 0.294 = 0.450 | 0.605 / 0.780 / 0.443 = 0.609 | 0.583 | 0.523 / 0.578 |
| **v2 (`v2c_*`, shipped)** | 0.562 / 0.706 / 0.372 = **0.547** | 0.255 / 0.623 / 0.159 = **0.346** | 0.619 / 0.781 / 0.418 = **0.606** | 0.503 / 0.647 / 0.603 = **0.584** | 0.545 / 0.588 |

Final (C) per run: R1 0.509, R2 0.504, R3 0.751, R4 0.528, R5 0.629 (confirmed with `heldout.py` on the packaged folder).

**Decision: ship v2 (`v2c`).** It beats v1 on (A) by +0.19 and on the R5 fold by +0.17, and ties v1 on the R4 fold. The R4 fold
failure is understood: without R4 the rush power `nl` has only one data point (l 0.2) and fits to 1 (linear), so the u.7 hold
(rush 0.44) is predicted 20% too low. The unbounded variant scores better there only because its rush term sat at a bound — not
evidence. Old-data in-sample: 0.545 (fit A) vs 0.555 for v1 (−0.010, within the 0.03 rule); 0.588 with the final fit.
The v1-structure refit does not help (0.431 on all data, worse than v1 on old runs), so the gains are structural.

**Gates.** Stability (`v2/stab_gate.json`, 200 schedules + 8 × 40,000 steps): no range failures (max shipments 44.6,
supplier 361.8, retail 1,514); 50 sawtooth flags, all shipments, all relative-amplitude artefacts at near-zero levels (the
64 extreme corners held 400 ticks give an absolute alternation ≤ 0.064, 0.06σ) — the same false positive accepted for v1
(61 flags). Contract: pass (40 × 4,000 steps in 8.7 s, all malformed cases ok). Package: pass (roots, credential scan clean,
contract from the extracted copy). ZIP `toronto26-participant-kit/submission-supply_chain-v2.zip` (6.5 kB);
`models/supply_chain/` now holds v2.

**Design choices and their predictions** (from reset, initial 25/100/100, `v2/longrun.py`; shipments / supplier / retail; all
settled by t ≈ 1,000 and unchanged to t = 4,000):

| Hold | t = 200 | t = 4,000 |
|---|---|---|
| recovery | 0 / 361.8 / 0 | 0 / 361.8 / 0 |
| joint u = 0.7 | 34.4 / 327 / 841 | 34.4 / 327 / 929 (data at t 150: 36.6 / 331 / 722, still rising) |
| joint u = 0.85 | 27.7 / 334 / 484 | 27.7 / 334 / 536 |
| joint u = 1 | 18.8 / 343 / 13 | 18.8 / 343 / 18 |
| orders 80 only (u 0.7 or 1) | 32.1 / 330 / 719 | 32.1 / 330 / 795 |
| orders + rush u 1 | 25.5 / 336 / 369 | 25.5 / 336 / 410 |
| orders + mix u 1 | 28.8 / 333 / 545 | 28.8 / 333 / 603 |
| orders + receiving u 1 | 17.3 / 345 / 0 | 17.3 / 345 / 0 |
| orders + maintenance u 1 | 40.4 / 321 / 1,144 | 40.4 / 321 / 1,275 |

Long-run behaviour: every state is a fixed point by t ≈ 1,000 (retail linear with kR = 0.013, τ ≈ 75 ticks); no drift, no clocks.
Retail goes to ~0 whenever shipments ≤ ~19 (D0 + g·E ≥ ship) — an untested prediction for the 4,000-tick joint-u1 holds.

**Open issues** (largest first):
1. Retail law: 0.37–0.60 even with the right shipments; never-settling retail (B26) and the long-run level at every hold are
   extrapolations. A two-class retail stock (diagnosis §5.2b) is the next thing to try.
2. D level (orders only) 32.1 vs 34.8 (−2.4σ): the fit compromises between maintenance 0 short-term (43.8) and long-term (37.3)
   with one `wm`. A heat state on U (M2, threshold) would free U0; not tried.
3. Rush dose-response rests on one composite point (`nl` 6.6); B4 fold shows it is not identified without R4. Rush transient
   (26 → 50 burst → 22.5, R1 410–469) not modeled.
4. Supplier make-to-order plateau at cap − q and 27-tick supply step (B21–B23), release bursts (B24): not captured.
5. Joint-pulse receiving lift source unidentified (spread over rush/mix/effort).

**Reserve recommendation (100 steps, not spent).** Issue 3 costs more than the lift question: single-rush pulses at 70–100%
(l 0.44–0.2) are held for thousands of ticks at r 1.5, where the model predicts −2% (l 0.44) and a linear rush predicts −20%
(≈ 6σ). The diagnosis's R6 runs at r 0.5 (receiving-limited), where rush on U is invisible, so it cannot decide this.
**R6' (fresh reset, `--confirm 100`):** ticks 0–34 orders 80, lead 1.0, mix 0.5, effort 1.0, receiving 1.5, maintenance 1.0
(reset transient replicate, reaches U by t ≈ 33); ticks 35–99 the same with **lead_time_buy 0.44** (65 ticks; R1 needed ~35
to settle). Decision: settled shipments ≥ 33 → threshold rush confirmed, keep `nl`; ≈ 26–29 → rush roughly linear, refit `nl`
with it (and R1 alone gives the level at 0.2). Second choice if rush is deprioritised: the diagnosis's R6 (lift attribution).
