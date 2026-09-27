# Hospital_queue plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 (overnight job, `plans/overnight-framework.md`). CAP = 1,300 steps
(6 controls: Run 1 ≤ 750, Run 2 ≤ 500, reserve ≥ 50). Budget at start: 2,000 remaining (free read).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Observe estimated wait, patients pending or receiving hospital care, and gross discharges.
Routine, urgent and elective cases need different assessment and treatment work. Diagnostic allocation divides shared
staff; urgent priority changes new service admissions. Patients already in assessment or treatment retain their work
and occupy finite chairs or beds until completion. A completed assessment may hold its chair when the treatment queue
is full. Staffing and overtime change work delivered, not completed patient counts directly. Overtime can create later
fatigue; staff changes can require orientation before staff are fully effective. Follow-up capacity diverts shared
staff to a finite outside program that can prevent delayed returns after discharge. Patients waiting can deteriorate
or leave; overflow is referred elsewhere rather than stored in an invisible queue. Fatigue, handover and returning
case mix are three possible mechanisms; exactly two apply. Compare equal staff-hours with different overtime spacing,
change diagnostic allocation at fixed staffing, or add follow-up after the same discharge burst. Initial queue
composition is a fixed function of the reported initial count; services and the follow-up program start empty."

**Observables** (initial-reading ranges from `docs/hospital_queue.json`):

| Observable | Initial range | Notes |
|---|---|---|
| wait_time | 2 – 5 | "estimated wait": probably a Little's-law style estimate, pending patients / recent service rate, or a lagged average of completed waits |
| queue | 30 – 70 | "patients pending or receiving hospital care": waiting + in assessment + awaiting treatment + in treatment. Finite (overflow referred elsewhere) |
| discharges | 8 – 15 | gross completions per tick (treatment completions); includes patients who may later return (M3) |

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u formula | u range | Notes |
|---|---|---:|---:|---|---|---|
| staffing | [1, 20] | 20 | 5 | (20 − s)/15 | [0, 1.27] | recovery at the bound; staffing 1 (u = 1.27) is beyond pulse. Work delivered ∝ staff |
| elective_scheduling | [0, 20] | 0 | 20 | e/20 | [0, 1] | added elective arrivals (demand) |
| diagnostic_allocation | [0.1, 0.8] | **0.4** | 0.75 | (d − 0.4)/0.35 | [−0.86, 1.14] | recovery **not at a bound**; 0.1 (u = −0.86) is the untested other side. Share of shared staff to assessment (diagnostics) vs treatment |
| urgent_priority | [0, 1] | **0.6** | 1 | (up − 0.6)/0.4 | [−1.5, 1] | recovery **not at a bound**; 0 (u = −1.5) is the other side. Changes which class is admitted to service first |
| overtime | [0, 1] | 0 | 1 | ot | [0, 1] | extra work delivered now; may create later fatigue (M1) |
| followup_capacity | [0, 1] | 1 | 0 | 1 − f | [0, 1] | pulse **removes** the follow-up program: frees shared staff, but lets delayed returns happen (M3) |

Recovery = full staffing, no electives, program on: an under-loaded hospital (expect the queue to fall from the
reading). Pulse = one quarter of the staff, maximum electives, maximum overtime, no follow-up: heavy overload; the queue
should hit its finite capacity (overflow is referred elsewhere, i.e. a hard cap on `queue`).

**Delay / commitment phrases → base structure (not mechanisms):**
- "Patients already in assessment or treatment retain their work and occupy finite chairs or beds until completion" →
  two service stages with finite capacity (chairs, beds) and work-in-progress that is not interrupted by control
  changes: throughput responds to staffing with a lag; discharges lag admissions by the treatment time.
- "A completed assessment may hold its chair when the treatment queue is full" → blocking: when beds/treatment queue
  are full, assessment capacity falls too (tandem-queue blocking; a saturation nonlinearity).
- "Staffing and overtime change work delivered, not completed patient counts directly" → staff act on a work rate
  (patients complete when their work is done); counts respond with a lag, not instantly.
- "Diagnostic allocation divides shared staff" → work split w_assess = d·W, w_treat = (1 − d)·W; there is an interior
  optimum (the bottleneck stage changes), i.e. a **non-monotone** effect of d.
- "urgent priority changes new service admissions" → class mix of admissions (urgent vs routine vs elective), which
  changes work per patient and who waits.
- "Patients waiting can deteriorate or leave" → abandonment ∝ waiting count; deterioration raises work per patient.
- "overflow is referred elsewhere rather than stored" → queue capped at a finite capacity (visible hard ceiling).
- "Follow-up capacity diverts shared staff to a finite outside program" → follow-up 1 costs capacity (base effect in
  every mechanism world); the prevention of returns is M3.
- Reset: "Initial queue composition is a fixed function of the reported initial count; services and the follow-up
  program start empty" → at tick 0 all initial patients are **waiting** with no one in service: expect a start-up
  transient (discharges start near 0 or at a low level until the first patients finish, then a burst).

**Anything tied to time since reset:** none named; only the start-up transient (services empty).

**Organizer-suggested comparisons (P9, quoted):**
- **P9a:** "Compare equal staff-hours with different overtime spacing" → same total overtime (e.g. 60 ticks of
  overtime 1) given as one block vs several short blocks with gaps; compare throughput/queue during and after (M1).
- **P9b:** "change diagnostic allocation at fixed staffing" → step diagnostic_allocation (both directions) with
  staffing constant; look for a transient throughput dip beyond the new steady level (M2 handover/orientation of
  reassigned staff) vs a clean first-order step.
- **P9c:** "add follow-up after the same discharge burst" → create a discharge burst (e.g. staffing restored after a
  backlog), then follow-up 1 vs follow-up 0; with M3 the follow-up-0 branch shows delayed returns (a later queue bump).

## 2. The three mechanisms (§3.2)

Quoted from one sentence listing three parallel candidates (confidence: high):

- **M1 fatigue:** "Fatigue" ("Overtime can create later fatigue")
- **M2 handover:** "handover" ("staff changes can require orientation before staff are fully effective")
- **M3 returning case mix:** "returning case mix" ("Follow-up capacity … can prevent delayed returns after discharge")

"… are three possible mechanisms; exactly two apply."

## 3. Theses (§3.3)

### M1 fatigue

| Field | Content |
|---|---|
| Quote | "Fatigue"; "Overtime can create later fatigue" |
| Hidden state | F: accumulated staff fatigue |
| **Driver** | overtime level (possibly overtime × workload); builds while overtime is on |
| **What it changes** | effective work per staff-hour ↓ (capacity) → lower discharges, higher queue and wait, **after** overtime, fading slowly |
| Timescales | builds over 20–100 ticks of overtime; fades over 50–200 ticks |
| P0 | nothing (no overtime) |
| P1 overtime on/off | present: boost in throughput that **fades during the hold**; after release throughput **undershoots** the pre-overtime baseline (queue overshoots) and recovers slowly. Absent: clean step up, mirror step down |
| P1 other controls | nothing directly |
| P5 / P9a equal overtime hours, one block vs spaced | present: outcomes differ (block → more fatigue late if F is convex/saturating or recovers between spaced blocks); absent: nearly equal integrated effect |
| P6 order | overtime before a staffing cut → cut hurts more (tired staff) |
| P7 long overtime hold | slow downward drift of capacity |
| P9b / P9c | nothing |

### M2 handover / orientation

| Field | Content |
|---|---|
| Quote | "handover"; "staff changes can require orientation before staff are fully effective" |
| Hidden state | O: staff not yet oriented (effective staff lags nominal staff), or a handover penalty after any team change |
| **Driver** | changes in staffing (esp. increases: new staff), possibly reassignments via diagnostic_allocation changes |
| **What it changes** | effective staff / work delivered: after a staff increase capacity rises **gradually**; a reassignment gives a transient capacity dip |
| Timescales | orientation 10–50 ticks; no memory once oriented |
| P0 | nothing (staffing constant at 20) — unless reset staff count as "new" (then capacity ramps up after reset) |
| P1 staffing 20→5 (on) / 5→20 (off) | present: cut is immediate, restoration is **slow** (on/off asymmetry in capacity); absent: mirror |
| P1 overtime | nothing |
| P9b diagnostic allocation step at fixed staffing | present: **dip** in throughput after each change (both directions) before the new level; absent: clean step |
| P4 staffing ramp vs step | present: ramp keeps up (less deficit); absent: same end, same path shape (ramp slower by construction) |
| P5 two staffing cuts short vs long gap | present: second restore again slow; weak gap dependence |

### M3 returning case mix

| Field | Content |
|---|---|
| Quote | "returning case mix"; "Follow-up capacity diverts shared staff to a finite outside program that can prevent delayed returns after discharge" |
| Hidden state | R: discharged patients at risk of returning (a delay pipeline), minus those absorbed by the finite follow-up program |
| **Driver** | discharges (output level), not prevented by follow-up (1 − followup, or excess over the program's finite capacity) |
| **What it changes** | delayed extra arrivals (queue ↑ after a delay) with heavier case mix (more work per patient → wait ↑, throughput per patient ↓) |
| Timescales | return delay 20–100 ticks; returns spread over similar |
| P0 | small late queue rise only if the program's finite capacity is exceeded at recovery |
| P1 followup 1→0 | present: immediate small capacity gain (staff freed), then **after a delay** queue and wait rise (returns); absent: only the capacity gain (queue falls / stays) |
| P1 staffing restore (discharge burst) | present with follow-up 0: delayed second queue bump after the burst; with follow-up 1: none |
| P9c follow-up 1 vs 0 after the same burst | **present: delayed queue bump only with follow-up 0; absent: follow-up 0 is simply better (more staff)** |
| P5 | returns from the first pulse's discharges arrive during the second pulse |
| P7 long hold with followup 0 | queue rises over the return delay and settles higher |

## 4. Separation table (§3.4)

| Probe | M1 fatigue | M2 handover | M3 returning case mix |
|---|---|---|---|
| P0 recovery | none | ramp-up only if reset staff are "new" | none (program on) |
| P1 staffing cut & restore | none | **slow restore** (asymmetry) | restore → burst → returns only if follow-up 0 |
| P1 overtime on/off | **fading boost, undershoot after** | none | tiny (via discharges) |
| P1 follow-up 0 | none | none (unless program staff reassignment counts) | **delayed queue/wait rise** |
| P9a overtime block vs spaced (equal hours) | **differ** | same | same |
| P9b diagnostic allocation step, staffing fixed | none | **transient dip at each switch** | none |
| P9c follow-up 1 vs 0 after the same discharge burst | none | none | **delayed bump with 0 only** |
| all-controls pulse & release | undershoot after release (overtime) | slow restore of capacity | returns after release (follow-up was 0) |

Pairs:
- **M1 vs M2:** overtime on/off at fixed staffing (fading boost + undershoot → M1; nothing → M2) vs staffing
  restore / diagnostic-allocation steps (dip or slow ramp → M2).
- **M1 vs M3:** overtime spacing (P9a) vs follow-up 0 with discharges (P9c).
- **M2 vs M3:** P9b (allocation dip at fixed staffing, follow-up unchanged → M2 only) vs P9c (follow-up switch after a
  burst with staffing unchanged → M3 only).

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 ~06:25 (start) | — | — | 0 | 2,000 |
| ~06:26 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| ~06:27 | R1 | 40–59 (P0 ext; wait still decaying) | 20 | 1940 |
| ~06:28 | R1 | 60–99 (P1 staffing 5 on) | 40 | 1900 |
| ~06:29 | R1 | 100–124 (staffing 5, ext) | 25 | 1875 |
| ~06:30 | R1 | 125–149 (staffing 5, ext) | 25 | 1850 |
| ~06:31 | R1 | 150–174 (staffing 5, ext; not settled, τ > 115) | 25 | 1825 |
| ~06:32 | R1 | 175–214 (staffing back 20 = recovery) | 40 | 1785 |
| ~06:33 | R1 | 215–239 (recovery ext; backlog draining 1.7/tick) | 25 | 1760 |
| ~06:34 | R1 | 240–279 (P1 overtime 1 on, during the backlog) | 40 | 1720 |
| ~06:35 | R1 | 280–309 (overtime off = recovery) | 30 | 1690 |
| ~06:36 | R1 | 310–349 (P1 elective 20 on → loaded base "E") | 40 | 1650 |
| ~06:37 | R1 | 350–379 (E + diagnostic 0.75; P9b-lite at fixed staffing) | 30 | 1620 |
| ~06:38 | R1 | 380–409 (E, diagnostic back 0.4) | 30 | 1590 |
| ~06:39 | R1 | 410–439 (E + overtime 1) | 30 | 1560 |
| ~06:40 | R1 | 440–469 (E, overtime off) | 30 | 1530 |
| ~06:41 | R1 | 470–499 (E + urgent 1) | 30 | 1500 |
| ~06:42 | R1 | 500–529 (E, urgent back 0.6, follow-up 0) | 30 | 1470 |
| ~06:43 | R1 | 530–579 (**all-controls pulse**: staffing 5, elective 20, diag 0.75, urgent 1, overtime 1, follow-up 0) | 50 | 1420 |
| ~06:44 | R1 | 580–639 (release to full recovery) | 60 | 1360 |
| ~06:45 | R1 | 640–684 (recovery ext) | 45 | 1315 |
| ~06:46 | R1 | 685–729 (recovery ext) | 45 | 1270 |
| ~06:46 | R1 | 730–749 (recovery ext; 170-tick recovery hold). **R1 complete: 750 steps** | 20 | 1250 |
| ~06:50 | R2 | 0–29 (P0 recovery, fresh reset) | 30 | 1220 |
| ~06:50 | R2 | 30–89 (recovery + follow-up 0: direct M3 test) | 60 | 1160 |
| ~06:51 | R2 | 90–109 (follow-up 0 ext, replaces the planned 20-tick follow-up-back segment: nothing had changed) | 20 | 1140 |
| ~06:51 | R2 | 110–139 (L = staffing 12.5 + elective 20) | 30 | 1110 |
| ~06:52 | R2 | 140–219 (L + overtime spaced 4 × (10 on/10 off), P9a) | 80 | 1030 |
| ~06:53 | R2 | 220–259 L + overtime block 40, 260–289 L overtime off (P9a) | 70 | 960 |
| ~06:54 | R2 | 290–319 L + diagnostic 0.1, 320–349 L diagnostic back 0.4 (P9b) | 60 | 900 |
| ~06:55 | R2 | 350–364 (recovery + overtime 1: drain, staffing 12.5 → 20) | 15 | 885 |
| ~06:55 | R2 | 365–379 (recovery + overtime 1 ext: the burst only reached 20+/tick after ~20 ticks) | 15 | 870 |
| ~06:56 | R2 | 380–454 (recovery + follow-up 0 after the burst, P9c; shortened 90 → 75 for the extra overtime) | 75 | 795 |
| ~06:57 | R2 | 455–499 (recovery, follow-up 1). **R2 complete: 500 steps** | 45 | 750 |

**Total spent 1,250 of CAP 1,300; 750 remain on the gateway; reserve for Phase C = 50.**

## 6. Run 1 observations and behaviour catalogue v1 (`data/hospital_queue/R1.json`, 750 ticks)

Initial reading wait 3.92, queue 39.2, discharges 13.4. Plot `data/hospital_queue/R1_r0_battery.png`, battery JSON
`data/hospital_queue/R1_battery.json`. "E" = loaded base: recovery action except elective_scheduling = 20.

**Design change made during Run 1:** at the recovery action the hospital is **under-loaded** (queue 23 = patients in
service, nobody waiting, discharges = arrivals 11.5), so overtime, diagnostic allocation, urgent priority and
follow-up cannot show a capacity effect there. Overtime was first tested during the backlog left by the staffing cut;
diagnostic allocation, a second overtime pulse, urgent priority and follow-up were tested on the loaded base E, where
discharges equal capacity. Every control got an on-step P1; the off-steps of urgent and follow-up are inside the
all-controls release.

Settled / end-of-hold levels (means over the window):

| Setting (ticks) | wait_time | queue | discharges | settled? |
|---|---:|---:|---:|---|
| recovery P0 (20–59) | → 0 (0.01) | 23.0 | 11.49 | yes |
| staffing 5 (150–174) | 94.5 (rising 0.4/tick) | 274 (rising 0.3/tick) | 2.63 | **no** (τ > 115) |
| recovery with backlog (215–239) | 30 (falling) | 200 (draining 1.7/tick) | 11.4 | no |
| recovery + overtime 1, backlog (240–251) | falling | drains 165 → 23 in 12 ticks | **22–31** | — |
| recovery after overtime (254–309) | → 0, k ≈ 0.12 | 23.0 | 11.50 | yes |
| E (330–349) | 25.9 (rising) | 271 → 278 | 9.7 | queue ~yes |
| E + diagnostic 0.75 (360–379) | 46.9 (rising) | **321** | **4.9** | queue yes |
| E, diagnostic back 0.4 (395–409) | 50.7 → 48.6 | 314 (not back to ~280) | 8.8 | yes |
| E + overtime 1 (415–439) | 36 → 31.7 | 303.5 | **13.8** | yes |
| E, overtime off (450–469) | 39.7 → 42 | 313.8 | 8.9 | yes |
| E + urgent 1 (480–499) | 44.2 (flat; trend stopped) | 313.1 | 8.9 | yes |
| E + follow-up 0 (505–529) | 45.0 | 313.5 | 8.8 | yes |
| all-controls pulse (560–579) | 105 (rising 0.6/tick) | 327 | **2.0** | queue yes |
| recovery after pulse, end (735–749) | 5.6 (falling 0.02/tick) | **99** (draining 0.1–0.2/tick) | 11.08 | **no** |

Noise: in smooth under-loaded holds σ(queue) ≈ 0.17, σ(discharges) ≈ 0.06, σ(wait) ≈ 0.005 (level-dependent);
in overloaded holds discharges are **bursty** (quanta 0–18 per tick, σ ≈ 2) and queue σ ≈ 2. Score σ (0.1 × std after
tick 20): wait ≈ 3.4, queue ≈ 11, discharges ≈ 0.45.

### Behaviours (catalogue v1)

- **B1 Reset start-up transient.** Discharges are 0 for 2 ticks, then burst (19, 8, 15, 27) while the initial queue
  (39 + arrivals) flows through; queue peaks at 61 (tick 1), then settles at 23.0 by tick 9. Wait decays
  geometrically (factor ≈ 0.885/tick) from the reading toward 0. Evidence: ticks 0–20. Explanation: base ("services
  start empty"; the initial count is all waiting). Status: modeled by base (W0 = reading, empty stages).
- **B2 Under-loaded recovery equilibrium.** queue 23.0 = in-service count, discharges 11.49 = arrival rate, wait → 0.
  Identical after the overtime-drained backlog (ticks 254–309). Little's law: in-service time ≈ 2 ticks. Status:
  modeled by base (A0, nsv).
- **B3 wait_time is a lagged estimate.** With nobody waiting it decays with k ≈ 0.115–0.12/tick (ticks 0–60 and
  252–310); under load it tracks ≈ (queue − 23)/discharges with a lag (staffing 5: (274−23)/2.6 ≈ 96 vs 94.5; all
  pulse (327−23)/2.0 ≈ 150 vs 105 still rising). Status: modeled by base (v EMA of W/Dm).
- **B4 Staffing sets capacity ∝ staff.** Staffing 5: discharges fall to 2.6 at once (0 on the switch tick, no lag) ≈
  5/20 of 11.5; queue climbs 10/tick, then slows (abandonment / overflow) and is still rising at 0.3/tick after 115
  ticks (274–280). Status: modeled by base (kmu·s); the slow creep is open (not settled).
- **B5 Slow capacity restoration after staffing returns (M2 candidate).** Staffing 5 → 20 (tick 175): discharges
  ~8 for 10 ticks, 9–10 up to tick 195, ≈ 11.4 from ~tick 205 (≈ 25–30 ticks to full); the same after the
  all-controls release (tick 580): 4.8, 6.2, 8.5, 8.0, 9.7, … reaching ≈ 11 after ~50 ticks. The cut (20 → 5) was
  immediate. On/off asymmetry in capacity = the M2 orientation signature. Alternatives: deteriorated (heavier) backlog
  patients (case mix), or refilling of the bed stage. Status: open → m2 (vs base mix).
- **B6 Recovery capacity only just exceeds demand.** With a backlog at staffing 20, discharges ≈ 11.4 ≈ the arrival
  rate, so the backlog drains mainly through patients leaving (≈ 1.7/tick at ~180 waiting, ≈ 1 %/tick) — a 270-patient
  backlog needs > 150 ticks. Status: modeled by base (kmu, theta) — to verify.
- **B7 Overtime nearly doubles capacity at recovery, +50 % under electives.** Recovery + backlog: 11.4 → 22–31
  (immediate, no lag), draining 142 patients in 12 ticks. On E: 8.8 → 13.8. No visible fade over 30–40 ticks and no
  undershoot after release (E: 8.9 after vs 8.8 before). **No fatigue signature yet** (70 overtime ticks total).
  Status: modeled by base (wo); M1 unresolved (needs a long overtime hold on a loaded base, P9a).
- **B8 Electives flood the hospital.** Elective 20: queue 23 → 270 within 11 ticks (≈ +20–25/tick), then a
  plateau that creeps up (271 → 278 in 20 ticks); discharges fall 11.5 → 9.7 (heavier/different elective work).
  Status: base (Ae, Wmax overflow, we mix).
- **B9 Diagnostic allocation 0.75 starves treatment.** On E: discharges 9.7 → 4.9 within ~3 ticks, queue +44
  (271 → 321: assessed patients holding chairs, B-blocking). Back to 0.4: discharges recover only to 8.8 (not 9.7)
  and queue stays 314 (no return to ~280). Possible handover dip (M2, P9b) or blocking/mix memory. Status: open.
- **B10 Urgent priority 1 has a small effect:** wait trend flattens (44.2, +2 vs the prior trend), queue and
  discharges unchanged. Status: base (wu) — low priority.
- **B11 Follow-up 0 has no immediate effect** on E (discharges 8.8 → 8.8): the staff it frees are negligible, or
  capacity is not the binding limit in the saturated state. Status: open (M3 needs P9c).
- **B12 Queue ceiling depends on the configuration:** 270–280 (staffing 5 or E), 314–327 (after diagnostic 0.75 /
  all-pulse). Overflow referral caps the waiting room; the extra ~45 are patients holding chairs/beds. Status: base
  (Wmax + Ca/Cb).
- **B13 Persistent residual backlog after the all-controls release (hysteresis, possibly M3).** 150 ticks after
  release the queue sits at **≈ 99** (not 23), draining only 0.1–0.2/tick; discharges 11.08 (below the P0 11.49) with
  an exact period-2 alternation (10.65/11.5, later 10.95/11.2); wait ≈ 5.5 slowly falling. Around tick 722–729 two
  bursts (14.5, 18.4, 14.5) dropped the queue 120 → 100. Candidate explanations: returning patients after the
  80-tick follow-up-0 period (M3; but then inflow should exceed 11.5, and discharges are lower); a lower-priority class
  (electives) stuck behind routine arrivals with very slow abandonment; fatigue after overtime (M1) keeping capacity
  just at demand. **This matters most for 4,000-step scoring** (the recovery level). Status: open — top priority for
  Run 2.
- **B14 Discharge quantization.** Overloaded discharges come in bursts (0, 3.4, 8, 18 …); the score compares with
  the noiseless process, so a smooth model is the right target. Status: note for the modeler.

Correlations (battery): wait lags queue by ~8 ticks (0.78); discharges anti-correlated with wait at lag 10–15.

Important cross-check for B5/B6: at the **reset** (ticks 2–9) the hospital at staffing 20 discharged 16.3/tick on
average (bursts to 27) while clearing the initial queue, but after the staffing cut it managed only ≈ 11.4/tick with a
backlog for 60+ ticks (ticks 205–239). Same controls, both with patients waiting → a slow hidden state lowers capacity
after the overload (orientation M2, heavier deteriorated case mix, or returns M3).

## 7. Model v0 and Run-1 pair fits

`greybox/hospital_queue_model.py` (written from the theses before fitting): tandem fluid queue — arrivals A0 +
Ae·elective (+ returns) → waiting W (overflow cap Wmax, leaving rate θ) → assessment chairs (cap Ca, rate ∝ staff ×
diag) → assessed patients hold their chair until a bed is free (Bk) → treatment beds (cap Cb, rate ∝ staff × (1 −
diag)) → discharges. Capacity = kmu·s_eff·(1 + wo·ot)(1 − g1·F)(1 − wf·fu)/(1 + we·φ), φ = elective share (slow mix
state). queue = W + Xa + Bk + Xt + nsv·D; wait = EMA of W / EMA(D) × exp(wu(up − 0.6)). Soft minimum (width 0.5) at
every capacity limit. Reset: W = queue reading, services empty. Mechanisms: m1 fatigue F (EMA of overtime, asym
rates) × capacity; m2 handover H (staff increases + k2d × reassigned staff on diag changes, fading a2) subtracts from
effective staff; m3 returns (g3 × discharges above the follow-up program's capacity fu·Pc, 2-stage lag a3) add arrivals
and heavier mix (wr). Fixed: kmu = 0.65 (redundant with ca, ct), A0 = 11.5, nsv = 2 (visible P0 constants, tip 2).

Quick R1 fits (3 restarts, init = base fit + SPEC mechanism defaults, so gains don't start at 0), linear units,
residual σ wait 1 / queue 3 / discharges 1, `fits/hospital_queue/*_r1.json`:

| Modules | Cost | Train score (0.1×std) | Notes |
|---|---:|---:|---|
| base (urg) | 9,399 | 0.495 | persistence 0.152 |
| m1 | 10,177 | 0.475 | worse than base → optimizer failure (g1 0.13) |
| m2 | 8,115 | 0.525 | g2 0.55, a2 0.034 (τ ≈ 30 ticks): the slow capacity restoration B5 |
| m3 | 9,382 | 0.497 | Pc 107 (program capacity ≫ discharges) → nearly off |
| **m1+m2** | 8,115 | 0.525 | g1 0.004 (fatigue off) — same as m2 alone |
| m1+m3 | 9,446 | 0.493 | g3 0.40, wr −3.1 (returns *lighten* mix: unphysical) |
| m2+m3 | **6,758** | **0.551** | wr −1,869 (absurd, pinned) — m3 used as a mix hack; not evidence for M3 |

Reading: M2 (handover) is the only module that captures a clear behaviour (B5). Fatigue is not seen in R1 (overtime
only on short holds). M3's improvement comes from an absurd parameter (lesson 9) → structure missing (probably the
case-mix / deterioration of waiting patients, B13). The optimizer is fragile (restart costs differ by 5×), so these
are for probe ranking only.

## 8. Run 2 design (§4.4)

Candidate probes simulated through the three R1 pair fits after a 30-tick P0 (`rank.py` in scratch; mean |pair
difference| / score σ, per observable then averaged):

| Candidate | Steps | m12–m13 | m12–m23 | m13–m23 | min |
|---|---:|---:|---:|---:|---:|
| C7 E30 + OT 30, then recovery with follow-up 0 80 (P9c) | 140 | 3.38 | 2.56 | 3.52 | **2.56** |
| C5 E40 + recovery 120 (B13 residual) | 160 | 2.47 | 2.92 | 2.26 | **2.26** |
| C7b same as C7 with follow-up 1 | 140 | 1.98 | 2.70 | 2.25 | 1.98 |
| C8 staffing 5 60 + recovery 80 | 140 | 1.46 | 0.23 | 1.66 | 0.23 |
| C6 E30 + staffing 10 30 + back 40 | 100 | 0.97 | 0.92 | 0.99 | 0.92 |
| C3b E30 + OT spaced 4×(10/10) (P9a) | 110 | 0.79 | 1.05 | 1.05 | 0.79 |
| C3a E30 + OT block 40/off 40 (P9a) | 110 | 0.76 | 0.91 | 1.23 | 0.76 |
| C4 E30 + diag 0.1 30 + back 30 (P9b) | 90 | 0.74 | 1.16 | 0.74 | 0.74 |
| C1 follow-up 0 at recovery 60 + back 20 | 80 | 2.61 | 0.45 | 2.82 | 0.45 |
| C9 E30 + diag 0.55 30 + back 30 | 90 | 0.50 | 1.01 | 0.63 | 0.50 |
| C3c staffing 12.5 60 + OT block | 140 | 2.04 | 0.31 | 1.87 | 0.31 |
| C2 staffing 12.5 60 (P2) | 60 | 0.88 | 0.10 | 0.98 | 0.10 |

**Chosen Run 2 (500 steps, fresh reset):**

| # | Segment | Steps | Purpose |
|---|---|---:|---|
| 1 | P0 recovery | 30 | reset transient at a new initial reading |
| 2 | recovery + follow-up 0 | 60 | **direct M3 A/B** (tip 13): at under-load discharges = arrivals, so returns show as discharges > 11.49 and queue > 23 (σ 0.06 / 0.17); no M3 → nothing changes (C1) |
| 3 | recovery | 20 | follow-up back on |
| 4 | L = staffing 12.5 + elective 20 | 30 | loaded base; P2 for staffing (u = 0.5) and P3 (staffing + elective jointly) |
| 5 | L + overtime spaced 4 × (10 on / 10 off) | 80 | **P9a** spaced half (40 overtime ticks) |
| 6 | L + overtime block 40 on, then 30 off | 70 | **P9a** block half (40 overtime ticks), fatigue undershoot after release |
| 7 | L + diagnostic 0.1 30, back 0.4 30 | 60 | **P9b** at fixed staffing, the untested side of a non-bound recovery value |
| 8 | recovery + overtime 1 | 15 | drains the backlog → **discharge burst**; also staffing 12.5 → 20 restore (M2) |
| 9 | recovery + follow-up 0 | 90 | **P9c** (compare R1 ticks 252–309: the same burst followed by follow-up 1 → flat 11.50) and B13 (residual backlog?) |
| 10 | recovery (follow-up 1) | 45 | returns stop? final recovery level |

Coverage after Run 2: P0 ×2, P1 all six, P2 staffing (0.5), P3 staffing+elective and the all-controls pulse, P9a/b/c,
P5 via spaced overtime, long recovery 170 (R1). Not covered: step vs ramp (P4), order swap (P6), a ≥ 200-tick P7 at a
single constant setting (R1 staffing 5 115 ticks, E-base 220 ticks with sub-settings).

## 9. Run 2 observations and behaviour catalogue v2 (`data/hospital_queue/R2.json`, 500 ticks)

Initial reading wait 2.61, queue 36.6, discharges 12.2. Plot `data/hospital_queue/R2_r0_battery.png`, battery
`data/hospital_queue/R2_battery.json` (run with `--min-hold 15`, because the battery crashes with
`KeyError: settling_time_text` on the 10-tick holds; tool bug, see hand-off). Cross-run plot of the R1 fits:
`data/hospital_queue/R2_crossrun_r1fits.png`; R1 fits on R1: `data/hospital_queue/R1_pairfits.png`.
"L" = staffing 12.5 + elective 20, other controls at recovery.

| Setting (ticks) | wait_time | queue | discharges |
|---|---:|---:|---:|
| P0 recovery (10–29) | → 0 | 22.94 | 11.49 |
| recovery + follow-up 0 (30–109, 80 ticks) | → 0 | 22.97 | **11.49 ± 0.015** (unchanged) |
| L (125–139) | 24 (rising) | 263 → 279 | 6.3 → 7.2 |
| L + overtime, spaced 10/10 ×4 (140–219) | 34 → 50 | 276 → 308 | on 10.3, 9.8, 9.6, 9.6 / off 6.1, 6.2, 5.6, 5.1 |
| L + overtime block 40 (220–259) | 49 → 43 | 306 → 311 | 9.5, 9.3, 9.7, 9.7 (per 10 ticks) |
| L overtime off (260–289) | 47 → 58 | 313 | 5.3, 5.5, 5.8 |
| L + diagnostic 0.1 (290–319) | 61 → 76 → 49 | **310 → 170** | 5.2 → **9.9** |
| L diagnostic back 0.4 (320–349) | 49 → 33 → 47 | 170 → 279 | **5.0, 2.4, 2.4, 3.6, 5.5, 5.7** (5-tick means) |
| recovery + overtime (350–379) | 47 → 13 | 282 → 56 | 12.4, 13.7, 15.2, 16.7, 21.1, 23.6 (5-tick means) |
| recovery + follow-up 0 after the burst (380–454) | → 0 | **49.5 flat**, drops to 37.9 at 425 and 34.1 at 451 | 11.5 (single bursts of 15 and 19 at the drops) |
| recovery, follow-up 1 (455–499) | 0 | **34.5 flat** | 11.51 |

### New / updated behaviours (catalogue v2)

- **B15 No returns: M3 null twice.** (a) Follow-up 0 at the under-loaded recovery for 80 ticks: discharges 11.49 ±
  0.015 and queue 22.97, identical to P0 (a return flow of even 0.1/tick would show). (b) P9c: after a discharge burst
  (≈ 20–28/tick for ~15 ticks, ~150 extra discharges), follow-up 0 for 75 ticks: discharges stay 11.5 and the queue
  *falls*. R1 comparison (the same kind of burst followed by follow-up 1, ticks 252–309): also flat 11.50. Unless
  returns are delayed by > 80 ticks, **M3 (returning case mix) is absent → the active pair is M1 + M2**
  (moderate–high confidence). Follow-up also has no visible capacity cost (B11). Status: evidence against m3.
- **B16 Fatigue signature: weak.** Spaced overtime: on-phase capacity 10.3 → 9.8 → 9.6 → 9.6 and off-phase 6.1 → 6.2 →
  5.6 → 5.1 (declining); block: steady 9.5–9.7 for 40 ticks, and the off level after the block (5.3 → 5.8) recovers
  slowly upward. Same total overtime (40 ticks): off level after spaced ≈ 5.1, after block ≈ 5.3. A downward drift
  also exists without overtime on the elective base (R1 E: 9.7 → 8.8 over 200 ticks), so it is confounded with the
  elective case mix accumulating (queue 263 → 313). The on/off ratio stays ≈ 1.8. A fatigue that builds over ~100
  overtime ticks and costs ≈ 5–10 % capacity is compatible; a large, fast fatigue is not. Status: open (m1 small).
- **B17 Handover / orientation (M2) supported again.** Staffing 12.5 → 20 with overtime (350–379): discharges ramp 12.4
  → 23.6 over ~25–30 ticks (5-tick means), whereas in R1 (tick 240, staffing restored 65 ticks earlier) the same
  overtime gave 22–31 **at once**. Together with B5 (two ramps of ≈ 25–50 ticks after staffing 5 → 20) this is the
  clearest mechanism signature in the data. Alternative: the elective case mix being flushed. Status: m2.
- **B18 Diagnostic allocation is non-monotone and has a large pipeline transient (P9b).** At fixed staffing 12.5 on L,
  d = 0.1 raises discharges 5.2 → 9.9 and drains the queue 310 → 170. Patients who had finished assessment were
  holding chairs while waiting for treatment, and more treatment staff clears them. So at d = 0.4 with electives,
  **treatment is the bottleneck** and ~140 of the ~310 in "queue" sit in service stages. Back to 0.4: discharges
  **crash to 2.4 for ~15 ticks**, then recover to 5.7 over ~20 ticks while the queue refills to 279. The dip is
  expected from the tandem pipeline (the treatment stage ran dry because assessment was starved), but it could also
  contain a handover dip (M2 via reassignment). In R1, d = 0.75 lowered discharges (9.7 → 4.9), and going back to 0.4
  recovered only to 8.8. Status: base (tandem structure). The v0 model gets the d = 0.1 direction **wrong** (it
  predicts a discharge collapse); the blocked-chair state has to dominate. M2's k2d (reassignment) is not tested
  separately from the pipeline.
- **B19 Persistent residual occupancy after overload (hysteresis), confirmed and quantised.** After the drain the queue
  does not return to 23. R2 sits at 49.5 (wait → 0 and discharges exactly 11.5, so nobody is waiting and nothing extra
  is discharged), then drops in single quanta (49.5 → 37.9 at tick 425 with a 15-discharge burst, → 34.1 at 451), and
  stays at 34.5 for the last 50 ticks. R1 ended at 99 with the same quantised drops. These are patients who occupy
  chairs or beds for a long time without being counted as waiting, probably electives with long treatment work or
  completed assessments holding chairs, and they leave in batches. **This sets the recovery level for thousands of
  scored ticks** (the recovery-spacing category). The model needs a slow "long-stay occupancy" state that fills during
  elective load and empties in quanta over ~50–150 ticks. Status: not captured (v0 drains to 23).
- **B20 Reset transient reproduced** at a different reading: queue 36.6 → 47.6, 58.8, then 23 by tick 8; discharges 0,
  0, then bursts 18, 7.5, 23.6, 18, 15, 19.6, 15. Status: base.

### Probes run and what they showed

| Probe | Run / ticks | Result |
|---|---|---|
| P0 ×2 | R1 0–59, R2 0–29 | identical equilibrium 23.0 / 11.49 / 0; start-up burst from empty services |
| P1 staffing | R1 60–239 | capacity ∝ staff, immediate cut, slow restore (M2) |
| P1 overtime | R1 240–309, 410–469 | ×2 at the recovery backlog, ×1.5 on E, immediate, no undershoot after 30–40 ticks |
| P1 elective | R1 310–349 | flood to the overflow ceiling in 11 ticks, heavier mix |
| P1 diagnostic 0.75 / P9b 0.1 | R1 350–409, R2 290–349 | non-monotone; pipeline crash on switching back |
| P1 urgent 1 | R1 470–499 | small (the wait trend flattens) |
| P1 follow-up 0 | R1 500–529, R2 30–109 | nothing at all |
| P2 staffing 12.5, P3 staffing + elective | R2 110–139 | capacity 6.3–7.2, roughly proportional to staff under the elective mix |
| all-controls pulse & release (tip 4) | R1 530–749 | discharges 2.0 under the pulse; release: slow capacity ramp, 170-tick drain, residual 99 |
| P9a overtime spacing (P5) | R2 140–289 | small differences; weak fatigue at most |
| P9c follow-up after a burst | R2 350–454 vs R1 240–309 | no returns with follow-up 0 |
| M3 direct A/B (tip 13) | R2 30–109 | null |
| Long recovery (tip 5) | R1 580–749 (170), R2 380–499 (120) | residual long-stay occupancy |

Not run: step vs ramp (P4), order swap (P6), a ≥ 200-tick hold at one constant setting (the longest were staffing 5
for 115 ticks and the elective base for 220 ticks with sub-settings), staffing 1 (u = 1.27), elective mid-level and
diagnostic mid-levels.

### Cross-run check (R1 fits → R2, σ = 0.1×std over R1+R2)

| Fit | R2 score |
|---|---:|
| persistence | 0.284 |
| base (urg) | 0.475 |
| **m1+m2** | **0.482** |
| m1+m3 | 0.331 |
| m2+m3 | 0.374 |

m2+m3's best R1 cost (with an absurd wr) does not transfer. m1+m2 (≈ m2 alone) transfers best, consistent with B15.

## Status / hand-off to reviewer

**Spent:** R1 750 + R2 500 = 1,250 of CAP 1,300; 750 remain on the gateway; **reserve 50** for Phase C.

**Files:** `plans/hospital_queue-plan.md` (this file); `data/hospital_queue/R1.json`, `R2.json`,
`R1_battery.json/png`, `R2_battery.json/png/txt`, `R1_pairfits.png`, `R2_crossrun_r1fits.png`; model
`greybox/hospital_queue_model.py` (v0 tandem fluid queue); fits
`fits/hospital_queue/{base_r1,base_r1b,base_r1c,m12_r1,m13_r1,m23_r1,m1_r1,m2_r1,m3_r1}.json` (plus `.log` files,
`base_init*.json` and `pair_init.json`).

**Mechanism reading:** M2 handover is present (B5, B17). M3 returning case mix is absent (B15, two clean nulls). By
"exactly two", M1 fatigue should then be present even though its signature is weak (B16); look for it as a slow
(≥ 100-tick), small (≤ 10 %) capacity loss after cumulative overtime. Pair to favour: **m1+m2**.

**Open, in priority order:**
1. **B19 residual long-stay occupancy** after elective load (queue 34.5 and 99 instead of 23 at recovery, leaving in
   quanta). This has the largest effect on 4,000-step recovery scoring and is not captured by v0.
2. **B18 tandem structure:** the v0 model predicts the wrong sign for diagnostic 0.1 (it starves treatment instead of
   clearing blocked chairs). Under electives, treatment must be the bottleneck, with ~140 patients in service stages.
3. The elective case mix (work per patient) is confounded with fatigue in B16; the queue ceiling of 270–330 depends on
   the configuration (B12).
4. The v0 fits are rough: the optimizer stops early (restart costs differ 5×), and m1 alone fitted worse than base.
   The modeler should improve the base first (tip 6), then compare pairs.
5. Tool bug: `greybox/common/battery.py` line 188 raises `KeyError: 'settling_time_text'` for holds shorter than the
   settle tool's minimum; the workaround is `--min-hold 15`.
6. Candidates for the 50-step reserve: extend a recovery after elective load to see whether the residual 34.5 ever
   drains (B19); or run a 40-tick overtime block at staffing 20 with a backlog and compare it with R1 ticks 240–251 to
   size fatigue.
