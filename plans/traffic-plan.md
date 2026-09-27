# Traffic plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 02:18 (overnight job, `plans/overnight-framework.md`). CAP = 1,300 steps
(6 controls: Run 1 ≤ 750, Run 2 ≤ 500, reserve ≥ 50). Budget at start: 2,000 remaining (free read).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Observe terminal flows and mean speeds on two routes. Light and heavy vehicles retain their
route, class and crossing commitments after entry. Toll changes the arriving mix; ramp metering changes admitted
demand. Signal timing divides new crossing admissions, freight priority changes which waiting class gets service,
and clearance effort shifts a shared crew from intersection operation toward downstream exits. Vehicles already
crossing keep occupying the shared junction until their committed work finishes and exit space opens. Thus one
route can obstruct the other even under unchanged signals. Lane closure affects different sections unequally.
Finite approach, junction and exit buffers reject excess arrivals; waiting approach drivers may divert. Route
learning, crew fatigue/switching costs and persistent spillback fronts are three possible mechanisms; exactly two
apply. Compare toll and ramp preparations with similar totals to change vehicle mix; compare clearance with a signal
reversal after stopping arrivals. Reported speed combines observed completed journey times with current stopped and
moving class mix; equal route totals can therefore report different speeds. Roads and crossings start empty."

**Observables** (initial-reading ranges from docs: all four in [30, 45]):

| Observable | Initial range | Notes |
|---|---|---|
| flow_a | 30 – 45 | terminal (exit) flow of route A, vehicles/tick; output of approach → junction → exit pipeline |
| flow_b | 30 – 45 | same for route B; shares the junction and the crew with A |
| speed_a | 30 – 45 | "combines observed completed journey times with current stopped and moving class mix" → a lagged journey-time average plus an instantaneous mix term; heavy/stopped share lowers it |
| speed_b | 30 – 45 | same for B |

"Roads and crossings start empty" → the initial reading cannot be an equilibrium of the hidden state: expect a
reset transient in flows (start low / fill up) and possibly speeds (empty road = free-flow speed).

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u formula | u range | Notes |
|---|---|---:|---:|---|---|---|
| signal_timing | [0.1, 0.9] | **0.5** | 0.15 | (0.5 − s)/0.35 | [−1.14, 1.14] | recovery **not at a bound**; 0.9 (u = −1.14) is the untested other side. Probably A's green share (pulse favours B) |
| lane_closure | [0, 0.75] | 0 | 0.65 | lc/0.65 | [0, 1.15] | capacity cut; "affects different sections unequally" |
| toll | [0, 5] | 5 | 0 | (5 − toll)/5 | [0, 1] | changes arriving **mix** (light vs heavy) → mostly speeds |
| ramp_metering | [0, 1] | 0 | 1 | rm | [0, 1] | changes **admitted demand** (direction to be measured) |
| freight_priority | [0, 1] | **0.5** | 1 | (fp − 0.5)/0.5 | [−1, 1] | recovery **not at a bound**; 0 is the other side. Which waiting class gets service |
| clearance_effort | [0, 1] | 1 | 0 | 1 − ce | [0, 1] | pulse moves the shared crew from downstream exits to intersection operation |

**Delay / commitment phrases → pipeline stages (base structure, not mechanisms):**
- "retain their route, class and crossing commitments after entry" → a vehicle entered is committed: arrival →
  approach buffer → junction crossing → exit buffer → terminal flow. Control changes reach flow_* only after the
  travel/queue delay → first-order lag stages (≥ 1) on demand-type controls (toll, ramp).
- "Vehicles already crossing keep occupying the shared junction until their committed work finishes and exit space
  opens. Thus one route can obstruct the other even under unchanged signals." → a shared junction occupancy state;
  when exit space is short, **both** routes' flows fall (cross-coupling A↔B), not only the targeted one.
- "Finite approach, junction and exit buffers reject excess arrivals" → saturation (flows capped at a capacity that
  lane closure and the crew change); "waiting approach drivers may divert" → a queue-dependent loss (or switch to
  the other route) of waiting demand.
- "Reported speed combines observed completed journey times with current stopped and moving class mix" → speed =
  lagged journey-time term + instantaneous class-mix/stopped term; toll (mix) and freight priority (which class is
  stopped) can move speeds without moving flows (P9a).
- Reset: "Roads and crossings start empty" → buffers and junction empty; memories at reference (0).

**Anything tied to time since reset:** none named (no seasonality). Only the fill-up transient.

**Organizer-suggested comparisons (P9, quoted):**
- **P9a:** "Compare toll and ramp preparations with similar totals to change vehicle mix" → two holds with similar
  total flow (flow_a + flow_b), one produced by toll, one by ramp metering; compare speeds (mix) and the recovery
  after each.
- **P9b:** "compare clearance with a signal reversal after stopping arrivals" → first stop arrivals (maximum metering
  / whatever setting gives the lowest admitted demand), then (i) switch clearance effort, versus (ii) reverse the
  signal split; compare how the stored vehicles drain (flows) and the speed recovery. This is aimed squarely at
  crew switching costs (M2) versus spillback fronts that persist after arrivals stop (M3).

## 2. The three mechanisms (§3.2)

Quoted from one sentence listing three parallel candidates (confidence: high):

- **M1 route learning:** "Route learning"
- **M2 crew fatigue/switching costs:** "crew fatigue/switching costs"
- **M3 persistent spillback fronts:** "persistent spillback fronts"

"… are three possible mechanisms; exactly two apply."

## 3. Theses (§3.3)

### M1 route learning

| Field | Content |
|---|---|
| Quote | "Route learning" (with "Toll changes the arriving mix"; "waiting approach drivers may divert") |
| Hidden state | L: learned preference of arriving drivers for route A over B (perceived journey-time difference) |
| **Driver** | experienced journey-time / speed difference between routes: (speed_a − speed_b) (output levels), possibly queue lengths |
| **What it changes** | the split of arriving demand between routes → flow_a vs flow_b in **opposite** directions (total roughly conserved), and through load the speeds |
| Timescales | learning over 20–200 ticks; fading similar (it is a moving average of experience) |
| P0 | small slow drift in the A/B split while speeds differ |
| P1 signal on/off | present: direct split jump, then **slow further drift** as drivers move toward the faster route (partially undoing the imbalance); after release an **opposite overshoot** that fades. Absent: a clean step each way |
| P1 lane closure | present: slower route loses flow gradually to the other route (drift during hold, rebound after) |
| P1 toll / ramp | small (affects both routes) unless the routes differ |
| P2 mid level | drift scales with the speed gap (roughly linear) |
| P5 gap | 2nd pulse starts with the preference still shifted after a short gap |
| P6 order | order effects appear as a flow split offset |
| P8 speed gap via signal vs via lane closure | **same drift** for the same speed gap (driver is the output, not the control) |
| P9b (arrivals stopped) | nothing (no arrivals to re-route) |

### M2 crew fatigue / switching costs

| Field | Content |
|---|---|
| Quote | "crew fatigue/switching costs"; "clearance effort shifts a shared crew from intersection operation toward downstream exits" |
| Hidden state | F: crew fatigue (accumulated work) and/or S: switching penalty after the crew is redeployed |
| **Driver** | fatigue: crew workload (clearance-effort level at the exits, or throughput served); switching: \|Δ clearance_effort\| (change of assignment) |
| **What it changes** | crew productivity → service capacity of exits (and junction) → **both** flows fall and speeds fall, same sign on both routes |
| Timescales | switching penalty fades 10–50 ticks; fatigue builds 50–300 ticks, recovers similar |
| P0 | fatigue: slow decline of capacity under sustained recovery (ce = 1 at the exits all the time) → slow drift of flows/speeds |
| P1 clearance on/off | switching: a **transient capacity dip after both switches** (on and off) beyond the direct step; fatigue: effect of clearance fades during a long hold, and a rested crew overshoots after release |
| P1 other controls | nothing (clearance unchanged), unless fatigue tracks throughput |
| P5 gap | two clearance switches with a short gap → fatigue/switch penalties add up (2nd weaker) |
| P7 long hold | slow drift of capacity (fatigue) |
| P9b (arrivals stopped) | clearance change still produces its switching dip in the drain rate; signal reversal does not |

### M3 persistent spillback fronts

| Field | Content |
|---|---|
| Quote | "persistent spillback fronts"; "Finite approach, junction and exit buffers reject excess arrivals"; "one route can obstruct the other" |
| Hidden state | Q: extent of the spillback front (queue reaching upstream sections), with hysteresis: grows when a buffer is full, recedes slowly once demand falls |
| **Driver** | congestion: demand exceeding capacity (buffer overflow) → shows as low speed / flow below demand; one-sided (only when saturated) |
| **What it changes** | upstream capacity and speeds on the obstructed route **and the other route** (shared junction); recovery slower than onset |
| Timescales | builds fast (10–30 ticks) under overload, recedes slowly (50–300 ticks) |
| P0 | only if the recovery setting is itself congested |
| P1 lane closure / ramp demand up | present: flows/speeds fall **fast** at onset, **recover slowly** after release (on/off asymmetry), both routes affected; absent: mirror-image responses |
| P2 mid level | threshold: little effect below saturation, large above → nonlinear in u |
| P5 gap | 2nd congestion pulse after a short gap is **worse** / starts lower (front still present) |
| P6 order | congestion first then another control: the other control's effect is modified while the front persists |
| P9b (arrivals stopped) | the stored front keeps speeds low until it drains; signal reversal and clearance change drain it differently (front on one route vs exits) |
| P7 long hold | under sustained overload the front keeps growing slowly (drift) |

## 4. Separation table (§3.4)

| Probe | M1 route learning | M2 crew fatigue/switching | M3 spillback fronts |
|---|---|---|---|
| P0 recovery | slow split drift if speeds differ | slow capacity drift (fatigue at ce = 1) | none unless congested |
| P1 signal on/off | **anti-symmetric A/B drift** during hold, opposite overshoot after | none | only if one side saturates |
| P1 lane closure | slower route loses flow gradually | none | fast fall / **slow recovery**, both routes |
| P1 clearance on/off | none | **dip at each switch**; fading effect in holds | changes exit capacity → front if saturating |
| P2 mid signal | drift ∝ speed gap | none | ~none (below saturation) |
| P5 two congestion pulses, short vs long gap | small | only if clearance is switched | **2nd pulse worse after short gap** |
| P5' two clearance switches, short vs long gap | none | **2nd switch weaker/penalized after short gap** | none |
| P8 same speed gap via signal vs lane closure | **same drift** | none | different (lane closure saturates) |
| P9b clearance vs signal reversal, arrivals stopped | nothing (no arrivals) | clearance switch dip in drain | stored front drains slowly; reversal releases it |
| all-controls pulse & release | split drift after release | switching dip at release | slow recovery after release |

Pairs:
- **M1 vs M2:** A/B **opposite-sign** redistribution driven by speed gap (signal step, P8) vs same-sign capacity
  dip tied to clearance switches (P1 clearance, P5').
- **M1 vs M3:** redistribution without congestion (moderate signal step, P2) vs congestion hysteresis (lane
  closure on/off asymmetry, P5 congestion gap).
- **M2 vs M3:** clearance switching with **no congestion** (P9b with arrivals stopped, or P1 clearance at recovery
  demand) → M2 only; congestion pulses with clearance unchanged (lane closure P5) → M3 only.

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 02:18 (start) | — | — | 0 | 2,000 |

## Status / hand-off to reviewer

(Filled in at the end of Phase A.)
