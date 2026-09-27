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

## Status / hand-off to reviewer

(Filled in at the end of Phase A.)
