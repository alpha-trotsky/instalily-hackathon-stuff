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
| 2026-09-27 (start) | — | — | 0 | 2,000 |

## 6. Run 1 observations and behaviour catalogue v1

(filled in during Run 1)

## Status / hand-off to reviewer

(Filled in at the end of Phase A.)
