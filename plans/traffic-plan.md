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
| 02:19 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 02:20 | R1 | 40–79 (P1 ramp_metering 1 on) | 40 | 1920 |
| 02:20 | R1 | 80–104 (ramp on, ext) | 25 | 1895 |
| 02:20 | R1 | 105–144 (ramp off = recovery) | 40 | 1855 |
| 02:21 | R1 | 145–169 (recovery, ext) | 25 | 1830 |
| 02:21 | R1 | 170–209 (ramp 1 again = demand baseline D; also a P5-style repeat after a 65-tick gap) | 40 | 1790 |
| 02:21 | R1 | 210–259 (D + signal 0.15) | 50 | 1740 |
| 02:22 | R1 | 260–284 (D + signal 0.15, ext) | 25 | 1715 |
| 02:22 | R1 | 285–334 (D, signal back 0.5) | 50 | 1665 |
| 02:22 | R1 | 335–374 (D + lane_closure 0.65) | 40 | 1625 |
| 02:22 | R1 | 375–389 (D) + 390–429 (D + clearance 0) | 55 | 1570 |
| 02:23 | R1 | 430–469 (D + toll 0) | 40 | 1530 |
| 02:23 | R1 | 470–494 (D + toll 0, ext) | 25 | 1505 |
| 02:23 | R1 | 495–524 (D + toll 0 + freight 1) | 30 | 1475 |
| 02:24 | R1 | 525–554 (D + toll 0 + lane_closure 0.65) | 30 | 1445 |
| 02:24 | R1 | 555–584 (D + toll 0 + clearance 0) | 30 | 1415 |
| 02:24 | R1 | 585–604 (D + toll 0, clearance back 1) | 20 | 1395 |
| 02:24 | R1 | 605–654 (D: toll back 5) | 50 | 1345 |
| 02:24 | R1 | 655–699 (D, ext) | 45 | 1300 |
| 02:25 | R1 | 700–744 (full recovery, ramp 0). **R1 complete: 745 steps** | 45 | 1255 |


## 6. Run 1 observations and behaviour catalogue v1 (`data/traffic/R1.json`, 745 ticks)

Initial reading flow 37.3/34.1, speed 42.1/35.4. Plot `data/traffic/R1_r0_battery.png`, battery JSON
`data/traffic/R1_battery.json`. "D" = demand baseline: recovery action except ramp_metering = 1.

**Design change made during Run 1 (important):** at the recovery action the network is **empty** (flow 0 on both
routes): ramp_metering 0 admits no demand. Signal, lane closure, clearance and freight can only act on vehicles, so
their P1s were run on top of D (ramp 1) instead of on top of recovery. Every control still got an on/off P1; lane
closure, clearance and freight were additionally tested in the congested regime created by toll 0.

Settled / end-of-hold levels (means of the last 10–20 ticks; congested flows are means of bursty series):

| Setting (ticks) | flow_a | flow_b | speed_a | speed_b |
|---|---:|---:|---:|---:|
| recovery, P0 (20–39) | 0 | 0 | 48.9 | 48.9 |
| D (ramp 1), first (85–104) | 12.07 | 11.92 | 31.4 | 30.55 |
| recovery (145–169) | 0 | 0 | 48.85 | **47.05** |
| D second (195–209) | 12.30 | 11.68 | 31.4 | 31.5 |
| D + signal 0.15 (270–284) | 11.19 | 12.82 | 25.9 | 30.65 |
| D (signal back) (320–334) | 11.85 | 12.17 | 30.35 | 29.4 |
| D + lane 0.65 (355–374) | 12.07 | 11.93 | 30.3 | 29.45 |
| D + clearance 0 (410–429) | 12.15 | 11.86 | 30.3 | 29.48 |
| D + toll 0 (482–494) | ~21.4 | ~11.5 | 11.9 (falling) | 15.1 |
| D + toll 0 + freight 1 (510–524) | ~18 | ~12 | 8.8 (falling) | 15.1 |
| D + toll 0 + lane 0.65 (540–554) | ~25 | ~13 | 8.4 | 15.1 |
| D + toll 0 + clearance 0 (570–584) | ~15 | ~12.5 | 10.3 | 15.6 |
| D + toll 0 (595–604) | ~19 | ~14 | 8.9 | 15.2 |
| D, toll back 5 (690–699) | 12.0 | 12.0 | 30.2 | **15.0** |
| recovery (730–744) | 0 | 0 | 48.9 | **46.6** |

Noise σ (second differences in smooth holds): flows ≈ 0.025 (0.2 % of 12), speeds ≈ 0.10. Score σ
(0.1 × std after tick 20): flows ≈ 0.9–1.0, speeds ≈ 1.2.

### Behaviours (catalogue v1)

- **B1 Empty network at recovery.** ramp_metering 0 admits no vehicles: flows are 0 (tiny positive noise) from tick
  0 whatever the initial reading ("roads start empty"); speeds relax from the reading to free flow ≈ 48.9 in ~10
  ticks (k ≈ 0.2). Evidence: ticks 0–39. Explanation: base (demand = f(ramp)); reset transient only in speeds.
  Status: open (to model: demand ∝ ramp, speed relaxation from the reading).
- **B2 Pure dead time of flows.** After ramp on, flows stay 0 for 11 ticks, then arrive in quanta (≈ 6.4, then
  12.0); after ramp off flows continue ~10–14 ticks (pipeline drains) then drop to 0 through quanta 18/5.7. Speeds
  react after ~2–3 ticks and relax with k ≈ 0.1 (31 after ~20 ticks). Evidence: ticks 40–60, 105–125, 170–190,
  700–725. Explanation: base (committed vehicles travel ≈ 10 ticks; shift register, not a first-order lag).
- **B3 Uncongested demand level.** At ramp 1, toll 5: total flow = 24.0 split ≈ 12/12, speeds ≈ 30–31.5. Lane
  closure 0.65 and clearance 0 have **no visible effect** in this regime (ticks 335–429): the demand is below every
  capacity they change. Status: open.
- **B4 Slow anti-symmetric route split drift with memory (M1 candidate).** During D holds flow_a − flow_b drifts
  with the total conserved at 24.0: 12.03/11.97 → 12.12/11.88 over 50 ticks (ticks 55–104, speed_a > speed_b); the
  second D episode, after a 65-tick zero-demand gap during which speed_b sat 1.9 below speed_a, **starts** further
  toward A (12.33/11.65) and drifts back to 12.25/11.75 as speed_b > speed_a. Signal 0.15 (A loses green): speed_a
  falls 5.4 at once (no dead time), while the flow split moves only after ~15 ticks and slowly (τ ≈ 30):
  12.2/11.8 → 11.15/12.9 over 75 ticks; after signal off it returns with the same delay and τ (11.94/12.11 at 334,
  12.14/11.87 at 429). A split that follows the **speed gap** with a delay, and remembers it across an empty
  period, is the route-learning signature (M1). Alternative: plain diversion of waiting drivers (would be fast and
  need a queue). Status: open → m1.
- **B5 Toll 0 creates congestion.** Toll 0 raises total demand to ≈ 33 (A ≈ 20, B ≈ 12.5) and makes flows
  **bursty** (0–50 per tick, quanta ≈ 6/9.5/30/40). speed_b falls to 15 within ~20 ticks and stays; speed_a falls
  steadily 30 → 8.5 over ~100 ticks (a queue on A still growing). B's flow is capped near 12–12.5 (B capacity),
  and the extra demand goes to A ("waiting approach drivers may divert"). Status: open (base: demand(toll),
  capacity-limited queues, diversion).
- **B6 Slow, asymmetric recovery from congestion.** Toll back to 5 (ticks 605–700): A keeps discharging at ≈ 20
  per tick for ~80 ticks (stored queue) before flow_a returns to 12 and speed_a to 30.3 (onset took ~100 ticks,
  recovery ~85, with a delay of ~40 ticks before speed_a starts rising). Explanation: queue storage (base) and/or
  spillback fronts (M3).
- **B7 Persistent standing queue on B (hysteresis; M3 candidate).** After the congestion episode, at D (same
  inputs as ticks 320–429 where speed_b = 29.4), speed_b stays at **15.0** for 95 ticks with flow_b = 12.0 — two
  different states under identical inputs. Only ramp 0 removes it: B then discharges a stored queue (flow_b bursts
  of 19–36 at ticks 710–722, longer than A's drain). Explanation: B's demand ≈ B's capacity so a queue that formed
  never drains (neutral queue), or a persistent spillback front (M3). Status: open → m3 / base queue.
- **B8 Zero-demand speed_b ratchet.** Free-flow speed_b is 48.9 before any traffic, 47.05 after the first demand
  episode (flat for 65 ticks), 46.6 after the congestion episode; speed_a returns to 48.9 every time. A persistent,
  B-specific state that does not fade in 50–65 ticks. Explanation: persistent spillback front on B (M3), or a
  stale journey-time memory on B ("observed completed journey times"). Status: open.
- **B9 Clearance in congestion.** Clearance 0 (crew to the intersection) at toll 0: speed_a rises 8.5 → 10.5 within
  ~10 ticks, flows fall after ~20 ticks (exits no longer cleared); switching back reverses both within ~15 ticks.
  No obvious extra switching dip. Status: open (M2 test needs a dedicated probe).
- **B10 Freight 1 and lane closure 0.65 in congestion:** no clear effect beyond the ongoing trend (speed_a decline
  flattened during lane 0.65, which is the wrong sign for a capacity cut). Status: open; low priority.
- **B11 Flow quantization and burstiness.** Uncongested flows are smooth (σ 0.025) but switch in quanta of ≈ 6;
  congested flows are bursty with a per-tick std ≈ 10–12. The score compares with noiseless values, so these bursts
  are part of the target. The best point forecast under the |error| score is the **conditional median/mean** of
  the burst process; a smooth model is the right target. Status: note for the modeler.

Speeds are strongly correlated between routes (level corr 0.93 at lag 4, battery), through shared demand.

## Status / hand-off to reviewer

(Filled in at the end of Phase A.)
