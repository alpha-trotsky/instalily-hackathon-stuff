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

Total spent 1,245 of CAP 1,300 → **reserve 55 steps** for Phase C.


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
