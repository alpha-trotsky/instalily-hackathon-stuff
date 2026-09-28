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
| 06:42 | R2 (fresh reset) | 0–29 S1 P0 recovery | 30 | 1225 |
| 06:42 | R2 | 30–69 S2 ramp 0.5 | 40 | 1185 |
| 06:42 | R2 | 70–114 S3 ramp 0.5 + signal 0.9 | 45 | 1140 |
| 06:42 | R2 | 115–169 S4 P9a ramp 0.72 + toll 0 | 55 | 1085 |
| 06:43 | R2 | 170–269 S5 joint pulse (all u = 1), part 1 | 100 | 985 |
| 06:43 | R2 | 270–369 S5 joint pulse, part 2 | 100 | 885 |
| 06:43 | R2 | 370–409 S6 release to recovery | 40 | 845 |
| 06:43 | R2 | 410–469 S7 second joint pulse (gap 40) | 60 | 785 |
| 06:44 | R2 | 470–499 S8 P9b: ramp 0 + signal 0.85, rest at pulse. **R2 complete: 500 steps** | 30 | 755 |

| 07:15 (Phase C) | R3 (fresh reset) | 0–54 ramp 1 + toll 2.5, rest at recovery (reviewer gap G6) | 55 | 700 |

Total spent **1,300 of CAP 1,300** (R1 745, R2 500, R3 55). Reserve exhausted.


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

- **B12 (added on resume) Speed memory of completed journeys held while the network is empty.** B8's ratchet
  fits "reported speed combines observed completed journey times": with no completions the journey-time part
  keeps its last value (B's last completions at 115–120 and 710–722 were slow drains). Candidate base term for
  the modeler: v = w·V_inst + (1 − w)·J, J updated only in proportion to completions. Status: not captured
  (current model: speed relaxes to vf at zero demand, 1.5–2.3 too high on speed_b ≈ 1.5–2 score σ).
- **B13 Unknown: speeds at zero demand under non-recovery controls.** Every empty-network period in R1 was at the
  full recovery action, so whether toll / lane / freight / clearance / signal move free-flow speeds is untested
  (the model's vh, vc, ws terms act at zero demand). Run 2 S8 tests it.

## 7. Run-1 pair fits (`fits/traffic/`, quick fits for probe ranking)

Fitted on R1 (745 ticks), linear units, σ = 1.0 (flows) / 0.3 (speeds), soft_l1. The loss surface is rough:
restarts from SPEC-default mechanism values landed in different basins (m13 12,099 > base), so every pair was
also re-started from the other pairs' optima (`*_r1_from_*`), and the base was re-fit from the m13 optimum.

| Fit | Cost | Train score (σ = 0.1×std) | Notes |
|---|---:|---:|---|
| base (`base_r1best.json`) | 10,828 | 0.641 | first attempt 11,454 (not converged); qmax ≈ 150 binds, diversion dv → 0 |
| m1+m2 (`m12_r1best.json`) | 10,090 | 0.642 | g1 0.15, a1 0.044 (τ ≈ 23); switching g2s 0.16, a2s 0.019 (τ ≈ 53); fatigue g2f < 0 |
| m1+m3 (`m13_r1best.json`) | **10,035** | 0.655 | g1 0.12; m3 fronts a3u 0.48, a3d 0.24 (not persistent), g3x −0.29, g3v −0.39 (wrong sign: soaks misfit) |
| m2+m3 (`m23_r1best.json`) | 10,216 | 0.642 | same m2 as m12; m3 again wrong-signed speed gain |

All three pairs beat the converged base by 6–7 %; spread between pairs 1.8 % (R1 was not designed to separate).
gam (demand exponent in ramp) is unidentified (only ramp 0/1 seen) — P2 ramp 0.5 needed.
The m3 speed gain g3v < 0 and cross gain g3x < 0 are the wrong physical sign → m3 as written is standing in for
missing congested-regime structure (lesson 9), not evidence for spillback.

## 8. Run 2 design (§4.4)

Candidates simulated through the three best pair fits (`fits/traffic/rank_probes.py`), each after a 30-tick P0
from reset; disagreement = mean over ticks of |Δ|/score-σ summed over the four observables, worst pair:

| Candidate | Steps | Disagreement | Decision |
|---|---:|---:|---|
| joint pulse of all controls 200 + release 40 | 240 | **18.1** | **run** (tip 4, P3/composition, P7 ≥ 200, recovery category) |
| P9b clearance: joint 100 then ramp 0 + clearance 1 | 130 | 17.1 | covered by S6 release (ramp 0 + clearance 1 + rest) |
| P9b signal reversal: joint 100 then ramp 0 + signal 0.85 | 130 | 15.5 | **run** as S8 (after S7) |
| P5 joint 60, gap 30, joint 60 | 150 | 11.5 | **run** as S5-S6-S7 (gap 40) |
| P9a ramp 0.72 + toll 0 (total ≈ D's 24, heavier mix) | 70 | 4.8 | **run** (P9a) |
| P2 toll 2.5 at D | 60 | 4.7 | not run (budget); toll linearity stays open |
| P6 toll then lane / lane then toll | 120 each | 4.4 / 2.7 | not run (P5 covers the recovery-history category) |
| P7 D + toll 0 250 | 250 | 4.0 | superseded by the joint 200 hold |
| P5' clearance toggles at D + toll 0 | 100 | 3.9 | not run |
| P8 signal 0.3 at D | 80 | 0.5 | not run |
| P2 ramp 0.5 + signal 0.9 | 120 | 0.4 | **run** (cheap coverage: gam and the untested side of signal; M1 drift sign) |
| P2 ramp 0.5 | 60 | 0.3 | **run** (as above) |

Run 2 schedule (fresh reset, `data/traffic/R2.json`, 500 steps = the Run-2 cap; total 1,245 ≤ 1,250):

| Seg | Steps | Action (others at recovery) | Purpose |
|---|---:|---|---|
| S1 | 30 | recovery | P0 (fresh reset; initial-reading dependence) |
| S2 | 40 | ramp 0.5 | P2 ramp (gam, split at half demand) |
| S3 | 45 | ramp 0.5, signal 0.9 | other side of signal (u = −1.14); M1 drift should reverse sign vs R1 |
| S4 | 55 | ramp 0.72, toll 0 | P9a: total ≈ 24 like D but toll-driven heavy mix; congestion threshold |
| S5 | 200 | **all controls at pulse** (signal 0.15, lane 0.65, toll 0, ramp 1, freight 1, clearance 0) | joint pulse, P7 long hold, settled level |
| S6 | 40 | recovery (all released) | joint release; drain with clearance back to 1; zero-demand speed memory |
| S7 | 60 | all at pulse again | P5: 2nd pulse after a 40-tick gap vs S5's first 60 ticks (M3 fronts / M2 fatigue memory) |
| S8 | 30 | ramp 0, signal 0.85, others at pulse (clearance held 0) | P9b signal reversal after stopping arrivals, compare the drain with S6; B13 |

## 9. Run 2 observations and behaviour catalogue v2 (`data/traffic/R2.json`, 500 ticks)

Initial reading 36.0/42.0/43.6/38.8. Plots: battery `data/traffic/R2_r0_battery.png` + `R2_battery.json`;
R1 pair fits predicting R2: `fits/traffic/r1pairs_on_R2.png`; base fit on R1: `fits/traffic/base_r1.png`
(plot helper `fits/traffic/plotfit.py OUT.png DATA FIT...`).

Settled / end-of-hold levels (means; medians for bursty flows in brackets):

| Setting (ticks) | flow_a | flow_b | speed_a | speed_b |
|---|---:|---:|---:|---:|
| P0 recovery (20–29) | 0 | 0 | 48.96 | 48.86 |
| ramp 0.5 (55–69) | 5.99 | 6.01 | 34.64 | 36.50 |
| ramp 0.5 + signal 0.9 (100–114) | 6.20 (drifting) | 5.80 | 35.47 | 29.98 |
| P9a ramp 0.72 + toll 0 (140–169) | 16.8 [19.1] | 12.8 [10.6] | 15.6 (falling) | 16.2 |
| joint pulse, all u = 1 (340–369) | **6.66** (smooth) | 12.9 [13.1] | **6.09** | 16.12 |
| release, recovery (400–409) | draining → 0 at 403 | 0 from 393 | 32 (rising) | 47.7 |
| 2nd joint pulse end (455–469) | 7.3 | 13.1 | 9.3 (falling) | 16.1 |
| P9b ramp 0 + signal 0.85, rest at pulse (490–499) | 20.6 [23.7] | 5.1 [3.6] | 15.1 | **13.0** (falling) |

**Cross-run check (quick R1 fits → R2, σ = 0.1×std):** base 0.260, m12 0.330, m13 0.309, **m23 0.371**,
persistence 0.060. All pairs miss the same things (B15–B21), so the base structure is the first job, not the pair
choice.

### Behaviours added / updated (catalogue v2)

- **B1/B2 confirmed (B23).** Fresh reset from a different reading: flows 0 from tick 0 at ramp 0, speeds relax to
  48.9 in ~15 ticks; after ramp on, first flow 12 ticks later, in half-size quanta (3.2) at ramp 0.5.
- **B14 Demand ∝ ramp (gam = 1).** Total flow 12.0 at ramp 0.5 vs 24.0 at ramp 1 (toll 5). Status: fix gam = 1.
- **B15 Concave speed–load relation (not captured).** Mean route speed at total flow 0 / 12 / 24 = 49 / 35.6 /
  31: half the demand gives ~80 % of the full-demand speed drop. The model's exp(−al·n/100) is nearly linear in n
  and predicts ≈ 38 at ramp 0.5 (≈ 3 score σ error on both speeds for every mid-ramp tick). Needs a saturating
  load term (e.g. vf/(1 + a·n^p), or journey time = free time + load-dependent delay, speed = length/time).
  Also B's speed at ramp 0.5 is 1.9 above A's (A above B at ramp 1): route-specific curves.
- **B16 Signal effect is one-sided per route (not captured).** Signal 0.9 (A gets green): speed_b −6.5, speed_a
  +0.9. R1 signal 0.15 (B gets green): speed_a −5.4, speed_b +1. The route losing green loses ~6; the route gaining
  green gains ~1 → saturating in green share (e.g. delay ∝ 1/green), not the model's linear ws·u_sig (which also
  lifts free-flow speed above 49 when u_sig < 0: seen in the R2 prediction, S8).
- **B4 confirmed on the other side (M1).** Under signal 0.9 the split drifts toward A (5.94/6.05 → 6.25/5.75 over
  45 ticks, ~15-tick delay, still moving): drift toward the faster route, both signs of the speed gap. At ramp 0.5
  (speed_b > speed_a) the split drifted toward B (5.99/6.00 → 5.95/6.06). Route learning is the best-supported
  mechanism. Size: ~0.3–1 flow unit (≈ 0.3–1 score σ on flows) but persistent.
- **B17 P9a: mix, not volume, causes congestion (not captured).** ramp 0.72 + toll 0 has the same expected total
  (≈ 24) as the uncongested D (ramp 1, toll 5; speeds 30/29, smooth flows), yet it congests within ~30 ticks:
  speeds 15.6/16.2, bursty flows. Heavy vehicles (toll 0) cut capacity per vehicle; capacity must depend on the
  heavy share, not only on toll as an additive demand boost. The R1 fits predict speeds ≈ 30 here (≈ 10 score σ).
- **B18 Joint pulse settled level (not captured).** All controls at pulse for 200 ticks: flow_a settles to
  **6.66 and becomes smooth** (A's service rate is the binding capacity: green 0.3 × lane closure × clearance/
  freight), flow_b 12.9 bursty, speed_a 6.1 (settled by tick ~300, ~130 ticks after onset), speed_b 16.1. The R1
  fits put flow_a at 15–19 and speed_a 5–20 (m13 20). speed_b ≈ 15–16 in **every** congested hold (R1 toll 0,
  R2 P9a, joint): a floor for B's congested speed.
- **B19 Slow release on A (recovery category).** After the joint release, B empties in 23 ticks and speed_b is
  back to 48 in 30; A keeps discharging bursts (up to 60/tick) for 33 ticks and speed_a is only 34 after 40 ticks.
  The fits recover speed_a ~15 ticks too early. Stored queue size on A is large (buffers much larger than served
  rate × dead time).
- **B20 Second joint pulse after a 40-tick gap.** From a nearly empty network, speeds fall over ~60 ticks
  (speed_a 9.2, speed_b 16.1 at +60), similar to R1 toll-0 onset rates. No clear "worse 2nd pulse". Caveat: S5
  started from the congested P9a state, so this P5 is not a clean comparison; evidence for persistent fronts
  (M3) is weak here.
- **B21 P9b signal reversal after stopping arrivals (M2/M3 evidence, not captured).** With ramp 0, signal 0.85
  and the crew kept at the intersection (clearance 0, lane/freight/toll at pulse): A (now green) discharges its
  queue in bursts (mean 20) and speed_a recovers slowly (8.5 → 17.6 in 30 ticks); B discharges only ~3/tick and
  **speed_b keeps falling 15.6 → 12.7 with no arrivals**. Compare S6 (release incl. clearance 1): B empty in 23
  ticks, speed_b 48. So stored vehicles keep B blocked when B loses green and exits are not cleared — the brief's
  "keep occupying the shared junction until … exit space opens". Signal reversal and clearance act very
  differently on the drain (the P9b contrast the organizers point at). Clean M2-vs-M3 separation still needs a
  clearance-only switch with arrivals stopped (reserve probe below). The R1 fits empty B at once and send speed_b
  to 50+.
- **B22 Speed noise ∝ level.** Noise σ of speed_a 0.018 at 6.1 vs 0.115 at 49 (battery: proportional,
  σ_rel ≈ 0.5 %). Consider log units for speeds. Flow noise: 0.01–0.02 in smooth holds; congested flows are bursts
  (per-tick std 4–20) that the score sees; target the conditional mean.
- **B8/B12 (zero-demand speed_b ratchet).** R2 P0 speed_b 48.86; after the joint release speed_b reached 48.6 at
  +38 and was still rising — no clear ratchet this time (A was the long-draining route). Still open.

### Probes run vs coverage list (§4.2)

P0 both runs ✓; P1 all six controls ✓ (R1; signal/lane/clearance/freight on top of D, lane/clearance/freight also in
congestion); P2 ramp 0.5 ✓ (most important control), signal other side 0.9 ✓; P3 → joint pulse of all six ✓
(and R1 toll+freight, toll+lane, toll+clearance pairs); P7 ≥ 200 ✓ (joint hold 200); P5 ✓ (joint, gap 40, joint;
weak because the first pulse started congested); P9a ✓ (ramp 0.72 + toll 0 vs D; result B17); P9b ✓ signal-reversal
arm (S8; the clearance arm is only the S6 full release); separating probes: M1 via signal both sides ✓, M2/M3 via
S8 vs S6 drain (partial). Not run: toll mid level (2.5), P6 order swap, P5' clearance toggles, P8.

## Status / hand-off to reviewer

**Files:** plan (this file); data `toronto26-participant-kit/data/traffic/R1.json` (745), `R2.json` (500);
battery `data/traffic/R1_battery.json/.png`, `R2_battery.json`, `R2_r0_battery.png`; model
`greybox/traffic_model.py`; fits `fits/traffic/base_r1best.json`, `m12_r1best.json`, `m13_r1best.json`,
`m23_r1best.json` (the `*_r1b`, `*_r1_from_*`, `base_r1*` files are the restart history); probe ranking
`fits/traffic/rank_probes.py`; plot helper `fits/traffic/plotfit.py`; cross-run plot `fits/traffic/r1pairs_on_R2.png`.

**Budget:** 1,245 spent (R1 745, R2 500), 755 remaining on the server; **reserve under the CAP = 55 steps.**

**What to look at first (base structure before pairs; the cross-run scores are 0.26–0.37):**
1. B17/B18: capacity must depend on the heavy (toll-0) share and the joint controls multiplicatively; A's joint
   settled flow 6.66 and speed 6.1; B's congested speed floor ≈ 15–16.
2. B15/B16: concave speed–load curve and one-sided (1/green-type) signal effect; no speed above free flow.
3. B21/B19: stored vehicles block a route that loses green with the crew at the intersection, even with no
   arrivals; slow A release after the joint pulse. The queue/buffer sizes and the clearance-dependent exit
   service carry most of the recovery-category score.
4. Mechanisms: M1 route learning is supported on both signal sides (B4). m3 as written fits with wrong-signed
   gains (g3v, g3x < 0) — rewrite it as a one-sided front on the obstructed route (driver: queue above a threshold,
   slow recession) before comparing pairs. M2 has only the S6/S8 contrast.
5. Open: toll mid level (2.5) never tested (demand and mix effects assumed linear in u_free); order swap not run.

**Suggested reserve use (≤ 55):** a new run R3 (fresh reset; continuing R2 after a long gap may fail):
P0 15 + ramp 1 with toll 2.5 for 40. It tests the toll mid level, which matters for the sustained category. A clean M2 test (clearance-only switch after stopping arrivals) needs a congestion build of
≥ 60 ticks first and does not fit in 55.

## 10. Phase C (modeler, resumed 12:40–13:10)

Fits are in `toronto26-participant-kit/fits/traffic/v1/`. The driver is `fits/traffic/fitv1.py`: two Powell passes of 2,000 evaluations each, then a least_squares polish. Active modules start from SPEC. The cost is soft_l1 with f_scale 2, flow σ 1.0 and speed σ 0.3, as in the review. The cross-run script is `fits/traffic/crossrun.py`, and the model is `greybox/traffic_model.py` (v1).

### R3 evaluation (toll 2.5, ramp 1, 55 ticks from reset)

Toll 2.5 already congests **B**. speed_b falls to the ~15.5 floor within 50 ticks and flow_b turns bursty (8–15). A stays close to uncongested: speed_a 25, flow_a ≈ 20. The mix threshold therefore lies between toll 2.5 and toll 5, and it affects B first.

- The reviewer's rv base (fitted on R1+R2) scored 0.366 on R3. Its speed_b score was 0.24, because it predicted 19.5 instead of 15.5.
- The R1-only v1 fits score 0.20–0.27 on R3 (speeds about 0.07–0.2), so R3 carries information that R1 lacks.
- The final v1 fit (R1+R2+R3) scores 0.530 on R3.

### Review responses

| Gap | Response |
|---|---|
| G1 leaked pair fits | **Fixed.** No `*_r1best` or `rv_*` file is reused. Every v1 pair fit starts from the rv base optimum or the v1 base, with active modules reset to SPEC. Inactive modules are held at their off values by `core.params_for`. |
| G2 base structure | **Fixed.** The rv base was promoted to `greybox/traffic_model.py`, and the old model is kept as `traffic_model_v0.py`. |
| G3 B7 standing queue on B | **Largely fixed in the base, not by m3.** Per-route buffers (qmax_A 560, qmax_B 208 PCU) plus the spillback term give R1 605–705 speed_b of 14.7 → 19.4 (obs 15.1, flat), against up to 23 in rv. The remaining error is about +4 (≈ 4 score σ) at the end of the hold. The persistent m3 front builds while Q > q3 and recedes only once Q < q3. It was fitted in every pair, and every time a3u and a3d both went to 1 (m13 all-data: a3u 1.0, a3d 1.0, q3 27–89 PCU). That is an instantaneous threshold penalty, never a self-sustaining front. **The fits reject it as a persistent mechanism.** |
| G4 fullness term in base | **Fixed.** The base now has a capacity penalty `sp_r·Q_r/qmax_r` (sp_A 0.40, sp_B 0.23). m3 still fits as a static threshold on top of it (see G3), so it remains base structure in disguise. |
| G5 B drain after joint release | **Mostly fixed.** R2 370–410 speed_b is now 15.7 → 41 at +35 (obs 16 → 48). rv reached 32 at +40. |
| G6 toll mid level | **Fixed with R3** (55 steps, see above). The final fit has wt 1.80 and h1 1.47. |
| G7 optimizer | **Partly fixed.** Powell now runs before least_squares, as advised, with equal budgets per pair. However, every nested pair still ends *above* the base (see the all-data table), so optimizer noise (≈ 5–10 % of cost) is larger than any pair difference. |
| G8 M2 | **Not identifiable** (accepted). In the m2 fits the switching gain g2s goes to 0 (m12 on R1 and m12 all-data). Fatigue g2f ≈ 0.09–0.10, but no pair with m2 beats the base. |
| G9 J memory | **Tested and rejected.** kJ started at 0.5 in v1 and returned to the 1.0 bound in the base fits, which means no memory. The B8 ratchet is still not captured. |
| G10 freight 0 side | Not captured (no steps left). kf stays linear in u through exp(kf·u). |
| G11 longer dead time at toll 0 / lane | Not captured (no time). DT is fixed at 11. |
| G12 lane position | Not captured (no time). wl_A → 0 and wl_B is 0.03, so lane closure has almost no effect on junction capacity. |
| G13 bursty flows | soft_l1 is kept. The fitted model itself reproduces bursts (see Gates). The real congested flows also alternate tick to tick: on the data, the sawtooth statistic gives alternation 0.77–0.93 and relative amplitude 1.0–1.6 in congested holds. |

### Cross-run test (fit on R1 only, score on R2 and R3; σ = 0.1 × std after tick 20 of the scored run)

| Model (R1-only fit) | R1 cost | R2 score (fa, fb, sa, sb) | R3 score |
|---|---:|---|---:|
| persistence | — | 0.058 | 0.026 |
| base (no mechanism) | 11,932 | 0.266 (0.25 0.36 0.24 0.22) | 0.266 |
| m12 | 12,217 | **0.370** (0.31 0.33 0.48 0.36) | 0.250 |
| m13 | 12,292 | 0.256 (0.28 0.31 0.25 0.19) | 0.270 |
| m23 | 12,660 | 0.335 (0.25 0.35 0.27 0.47) | 0.200 |
| m13, least_squares only (smoke run) | 11,894 | 0.453 | 0.233 |

The same pair (m13) scores 0.256 or 0.453 depending on the optimizer path, so the cross-run differences between pairs are optimizer noise. R1 alone lacks the joint pulse, P9a and toll 2.5, which is why every R1-only fit scores only about 0.26–0.45 on R2.

### All-data fits (R1 + R2 + R3, 1,300 ticks)

| Fit | Cost | In-sample score (R1 / R2 / R3) | Module parameters |
|---|---:|---|---|
| base (from rv) | 27,272 | 0.593 / 0.528 / 0.489 | — |
| **base, 2nd pass (final)** | **25,679** | **0.601 / 0.534 / 0.529** | — |
| m12 cold / from base | 28,103 / 26,832 | 0.571 / 0.507 / 0.440 ; 0.576 / 0.507 / 0.491 | cold: a1 → 0, g1 −0.32; g2s → 0 |
| m13 cold / from base | 27,389 / 27,177 | 0.578 / 0.514 / 0.442 ; 0.533 / 0.518 / 0.422 | g1 0.28–0.53; **a3u = a3d = 1 (pinned)** |
| m23 cold / from base | 28,938 / 27,723 | 0.559 / 0.521 / 0.443 ; 0.532 / 0.516 / 0.432 | **a3u = a3d = 1 (pinned)**, g2f 0.10 |

### Bootstrap

**Not run.** This is a deliberate deviation made for time. Every pair model nests the base, yet every pair's real-data cost is 1,150–3,260 *above* the base's. A bootstrap would therefore measure the optimizer, not the mechanisms. No pair can reach the §6.3.4 row "real margin ≥ bootstrap margin" while its real margin against the no-mechanism model is negative.

### Decision (§6.3.4)

- m3 is pinned (a3u = a3d = 1) in every fit. That counts as missing structure, not as evidence.
- m2's switching gain goes to 0, and m1's learning rate goes to 0 in the cold m12 fit.
- No pair beats the base, so the pair is **not identifiable** with this data and this optimizer.
- **Shipped: the v1 base** (the relaxation-only fallback, with no active mechanism), `fits/traffic/final_v1.json` (a copy of `fits/traffic/v1/base_all2.json`). The qualitative evidence still favours M1 + M3 (review §3), but their fitted forms add nothing measurable.

### Gates (§7)

- **Local score:** pass. The base fitted on R1 scores 0.266 on R2 against persistence's 0.058. The final fit scores 0.534 in-sample on R2.
- **Stability** (`fits/traffic/v1/stab_final.json`, 200 schedules including 8 × 40,000 steps): **bounded, but 75 schedules are flagged "sawtooth"; accepted as a documented exception.**
  - There are no range, NaN or clamp failures. Flows stay within 0–31.7 and speeds within 5.7–49.7.
  - Speeds never exceed free flow (vf ≈ 49.7) because the time factor is now floored at 1.0. Before this change, speed_a reached 52.3.
  - The 75 sawtooth flags are tick-to-tick alternations in congested holds. The exit-occupancy feedback, cap·(1 − E/Emax) with cap > Emax, produces period-2 bursts.
  - Reason for the exception: the real congested flows show the same statistic (alternation 0.77–0.93, relative amplitude 1.0–1.6), and most model amplitudes are within or below that range. Three schedules have amplitude 3.7–14 on a near-zero mean flow.
  - Tested alternative, not shipped: a hard limiter (admissions ≤ free exit space, `fits/traffic/v1/traffic_model_exitlimit.py`) removes all but 2 sawtooth flags (amp 0.11). Its refit is much worse, though: cost 38,765 vs 25,679 and in-sample score 0.474 vs 0.572.
  - The rv base that was packaged earlier had the same kind of flags (67 schedules).
- **Contract:** pass from the extracted ZIP (40 × 4,000 steps in 4.1 s, deterministic, malformed inputs handled). The credential scan is clean.

## Final model and hand-off

- **Model:** the v1 base in `greybox/traffic_model.py`, with no mechanism modules. Parameters are in `fits/traffic/final_v1.json`. The pair is **not identifiable**: M1 + M3 are best supported qualitatively, and M2 is not identifiable.
- **Scores:** cross-run (R1 → R2) 0.266 against persistence's 0.058. The final fit scores 0.601 / 0.534 / 0.529 in-sample on R1 / R2 / R3. For comparison, the rv base scored 0.366 on R3.
- **Gates:** the local score passes and the contract passes. Stability is bounded but sawtooth-flagged (documented exception above).
- **Package:** `toronto26-participant-kit/models/traffic/` and `toronto26-participant-kit/submission-traffic-v1.zip`.
- **Steps:** 1,300 of CAP 1,300 are spent. 700 remain on the server and must not be used under this CAP.
- **Open issues:**
  1. Congested bursts: the model's period-2 exit-occupancy oscillation happens to resemble the data by accident. Its phase and amplitude on unseen schedules are unverified. A smooth congested regime that targets the median, with a limiter that still fits, would be safer.
  2. The pair fits never beat the nested base, so the optimizer is the bottleneck (about 50 parameters and piecewise-linear queues). Before any mechanism can be selected, the fits need more Powell restarts or a staged fit (freeze the base and free only the module parameters).
  3. Still not modelled: the B7 end-of-hold speed_b error (+4), the B8 speed_b ratchet (kJ pinned), the longer dead time at toll 0 (G11), the lane-closure position (G12) and the freight-0 side, which was never probed.


## Round 2 spend log (approved by the user 2026-09-28; schedules in `plans/round2-experiments.md`)

| Date | Run | File | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-28 14:44–14:55 UTC | TR1 (fresh reset) | `data/traffic/R4.json` | 400 | 300 |
| 2026-09-28 14:44–14:55 UTC | TR2 (fresh reset) | `data/traffic/R5.json` | 200 | 100 |

Segment files: `toronto26-participant-kit/fits/round2/segments/traffic_*.json`. Server budget confirmed after the runs.

## Round 2 model (v2)

Modeler pass, 2026-09-28. No simulator steps spent (100 reserve remain). Module `greybox/traffic_model_v2.py`; fits, driver and
checks in `toronto26-participant-kit/fits/traffic/round2/v2/` (`trfit.py` = Powell ×2 + least_squares polish, the v1 fit
protocol; `evalp.py`, `segs.py`, `probe.py`, `longrun.py`). Final params `fits/traffic/final_v2.json` (= `C_v2_ld3.json`).
All scores use the `heldout.py` σ (0.1 × std after tick 20 of R1–R5); the packaged folder reproduces them through `heldout.py`.

### Diagnosis items addressed and structural changes

1. **Capacity knee (diagnosis change 1; B25–B28, B7).** Junction capacity is now `smin(kg·green_r, exp(c_r))` in PCU, a
   p-norm soft minimum (p = 6, fixed) of a green-share limit with **one shared slope kg** and a fixed route cap, times the
   unchanged crew, lane, spillback and exit-occupancy factors. It replaces `exp(c_r)·(green_r/0.5)^wg_r` (−2 params, +1).
   Fitted: kg = 74.9 PCU per unit green, Cmax_A = 26.8 PCU, Cmax_B = 17.9 PCU (the diagnosis' 70–80 / 25–30 / 16–17).
   kg sits at a sharp cost minimum (probe: kg 65/70/80/90 all raise the all-data cost by 2–9 %).
2. **Speed load delay (change 2; B24, B29).** The in-transit load term counts only pipeline cells ≥ LD = 3 ticks old, so speeds
   first relax toward free flow after reset; kv refits to 0.135 (v1 0.107). A fixed constant, no new parameter.
3. B34 (drift), B35 (freight 0), B31 (B dead time), B36: **no change** (see open issues). No mechanisms (as v1).
4. Tried and rejected: residuals in score-σ units instead of the module NOISE (`--scoresig`): held-out (B) 0.431 vs 0.438.

### Held-out scores (per observable fa, fb, sa, sb; run mean)

| Test | Model | R4 | R5 | Mean |
|---|---|---|---|---:|
| (A) fit R1–R3, score R4, R5 | v1 (= v1 structure on old data) | .363 .303 .363 .414 → **0.361** | .231 .271 .643 .665 → **0.452** | **0.407** |
| | v2 knee only (LD 0) | .344 .315 .391 .509 → 0.390 | .232 .270 .619 .722 → 0.461 | 0.425 |
| | **v2 (knee + LD 3)** | .347 .311 .465 .527 → **0.413** | .229 .263 .651 .650 → **0.448** | **0.430** |
| (B) leave one new run out | v1 refit | .359 .304 .354 .427 → 0.361 | .242 .273 .566 .770 → 0.463 | 0.412 |
| | v2 knee only (LD 0) | .352 .312 .459 .518 → 0.410 | .235 .266 .623 .746 → 0.468 | 0.439 |
| | v2, score-σ residuals | .351 .321 .378 .551 → 0.400 | .231 .265 .649 .702 → 0.462 | 0.431 |
| | **v2 (knee + LD 3)** | .346 .311 .473 .544 → **0.419** | .230 .261 .639 .698 → **0.457** | **0.438** |
| (C) all data, in-sample | v1 shipped | 0.361 | 0.452 | R1–R3 0.599 / 0.531 / 0.526; 5-run mean 0.494 |
| | v1 refit | .394 .306 .491 .504 → 0.424 | .233 .275 .647 .761 → 0.479 | R1–R3 0.585 / 0.502 / 0.533; mean 0.505 |
| | **v2 (final)** | .389 .311 .495 .567 → **0.441** | .232 .262 .671 .713 → **0.469** | R1–R3 0.565 / 0.491 / 0.583; mean **0.510** |

In-sample on old data (packaged folder, `heldout.py --files R1 R2 R3`):
v2 0.547 vs v1 0.552 (−0.005, within the 0.03 rule); R1 alone drops 0.034 (flow_a at R1's toll-0 green-0.5 holds).

### Decision

**Ship v2 = knee + LD 3** (`final_v2.json`). The capacity knee earns its keep on both held-out tests (knee-only vs v1 / v1 refit:
(A) +0.018, (B) +0.027). The load delay adds +0.005 on (A) and ties on (B) (−0.001; it wins R4 speed_a and speed_b,
loses R5 speed_b), lowers the training cost in every fit (−2 to −4 %) and fixes the reset transient the diagnosis flagged
in every episode, and it adds no parameter; kept. Whole-run held-out gain: +0.023 (A) vs v1; (B) +0.031 vs v1 and +0.026 vs v1 refit.

### Gates

- **Stability** (`fits/traffic/round2/v2/stab_v2.json`, 200 schedules incl. 8 × 40,000): bounded, finite, no range or clamp
  failures (flows 0–26.2, speeds 5.6–49.5). **24 schedules flagged "sawtooth"** (v1: 75), the same congested exit-occupancy
  period-2 bursts accepted as a documented exception for v1; amplitudes mostly 0.1–1.7 (max 2.8). Accepted on the same grounds.
- **Contract** (`gates contract models/traffic`): pass. Package check from the extracted ZIP: pass (40 × 4,000 in 3.9 s,
  malformed inputs ok, credential scan clean).
- **Package:** `toronto26-participant-kit/models/traffic/` and `toronto26-participant-kit/submission-traffic-v2.zip`.

### Design choices and their predictions (4,000-tick holds from reset, all controls at u; fa, fb, sa, sb)

| Setting | t = 150 | t = 1,000 = t = 4,000 | v1 (t = 4,000) |
|---|---|---|---|
| recovery | 0, 0, 49.5, 48.8 | same | 0, 0, 49.7, 49.5 |
| u = 0.5 | 10.7, 11.8, 30.1, 30.4 | same | 11.2, 11.6, 29.7, 30.3 |
| u = 0.7 | 14.6, 12.4, **13.0**, 16.4 | 12.4, 12.4, **8.6**, 16.4 | 12.2, 15.7, 8.4, 17.6 |
| u = 0.85 | 10.1, 12.4, 8.1, 15.9 | 10.0, 12.4, 8.1, 15.9 | 9.8, 14.8, 7.8, 16.7 |
| u = 1 | 7.5, 12.3, 7.5, 15.3 | 7.4, 12.3, 7.4, 15.3 | 7.3, 13.5, 7.0, 15.7 |
| u1 200 → recovery | +50: 0, 0, 45.7, 48.0; t 4,000: 49.4, 48.6 | | |

- B's congested state is now invariant (flow_b 12.3–12.4, speed_b 15.3–16.4 at u ≥ 0.7), as B27 says.
- At u = 0.7 the model reproduces the measured 150-tick state (speed_a 13.0 vs 12.3) and then keeps drifting (the A queue fills
  its 570-PCU buffer slowly) to speed_a 8.6 by tick ~1,000. That is B34 as a plain queue dynamic, but the asymptote is an
  extrapolation: the data's k ≈ 0.04 fit gave 11.9. Nothing in 4,000 ticks is unstable or clock-like; all holds are flat after ~1,000.

### Open issues

1. **A capacity at green 0.5 with a full queue (R5, R1 toll-0 holds): flow_a −4 to −5σ in-sample** (model 16.5 vs 20.3; freight 0
   13.7 vs 18.9). The spillback penalty sp_A = 0.36 is needed by R1/R2 but caps R5; lowering it to 0.1 fixes R5 flow_a but costs
   speeds elsewhere. Also R1's lane-1 hold raises flow_a to 24.7 (model 17). Likely a missing lane/section structure.
2. u.7 long-run speed_a (8.6 vs a data-extrapolated 11.9): B34 settles the scored sustained u.7 level; unmeasured beyond 150 ticks.
3. Drain after u1 (R4 280–310): flows −4.5σ (A) / −4.9σ (B) — discharge after a long pulse is faster than modelled.
4. freight 0 effect (B35), B dead time (B31), lane/clearance (B36): not modelled. Flow bursts remain the dominant floor.
5. Sawtooth flags (24) remain a documented exception.

### Reserve steps (100) recommendation

Run the diagnosis' **TR3** unchanged: fresh reset; S1 30 ticks of B (signal 0.5, lane 0, toll 1.5, ramp 1, freight 0.5,
clearance 1); S2 35 ticks of B + signal 0.255; S3 35 ticks of B + signal 0.2025 (one `run_schedule.py` call per segment).
Predictions, last-20-tick means (fa, fb, sa, sb):

| Model | S1 (ticks 10–29) | S2 | S3 |
|---|---|---|---|
| **v2** | 18.4, 10.8, 26.1, 23.2 | **10.4**, 10.6, 9.8, 15.5 | **8.2**, 10.6, 7.8, 15.5 |
| v1 | 19.0, 10.5, 25.5, 23.3 | 9.7, 13.3, 9.6, 16.3 | 8.4, 13.9, 7.5, 16.3 |
| diagnosis H1 (green knee) / H2 (other controls) | | 14–15 / 17–19 | ≈ 11 / 17–19 |

What it decides: v2 puts the green knee at the right place on the ray (u.7, u.85 fit), but in R5's background (crew at exits,
full A queue) it predicts a much lower A capacity than H1. **flow_a ≥ 13 in S2** → open issue 1 is real (the spillback penalty
is too strong away from the ray): refit with sp_A constrained by the new points, or make the penalty act only near a full buffer.
**flow_a ≈ 10–11** → v2's capacity map holds and R5's high A flows come from the freight/lane segments. **flow_b outside
11.5–13.5** → B is not invariant and Cmax_B needs a green term. The S1 replicate vs R5 ticks 0–29 also tests burst determinism.
