# Epidemic plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 (overnight job, `plans/overnight-framework.md`). CAP = 1,000 steps
(Run 1 ≤ 550, Run 2 ≤ 400, reserve ≥ 50). Budget at start: 2,000 remaining (free read).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Daily infection onsets and occupied hospital beds in three interacting age groups. School
closure changes where contacts occur; masks reduce exposure; vaccination uses a shared clinic workforce. Age
groups differ in contacts, severity and recovery. Clinical referrals can wait for beds, and hospital pressure
reduces clinic availability. Behavior, developing immunity and postponed gatherings may retain intervention
history. Compare closure with masking at similar case counts, and vaccination before versus after a restriction
pulse; follow both cases and hospital recovery. Unobserved resident compartments start in a fixed age mix
determined by the observed initial cases; waiting lists and intervention histories start empty."

**Observables** (aggregated over the three age groups) and initial-reading ranges:

| Observable | Initial range | Notes |
|---|---|---|
| daily_cases | 100 – 240 | infection onsets per tick (day); positive, multiplicative dynamics expected → log units likely |
| hospital_load | 25 – 65 | occupied beds; lagging, smoothed version of severe cases; possibly capped by bed capacity |

**Controls** (recovery = 0, pulse = max for all three; all recovery values are at a bound, so no untested side):

| Control | Bounds | Recovery | Pulse | u |
|---|---|---:|---:|---|
| school_closure | [0, 1] | 0 | 1 | value |
| mask_mandate | [0, 1] | 0 | 1 | value |
| vaccination_rate | [0, 0.003] | 0 | 0.003 | value / 0.003 |

Recovery scenarios use u ∈ [0.7, 1] independently per control.

**Delay / commitment phrases → pipeline stages:**
- "Clinical referrals can wait for beds" → a referral waiting list between severe onsets and hospital_load
  (queue; saturating bed capacity). Hospital load should lag cases by the incubation/severity delay plus the
  wait. Expect hospital_load to lag daily_cases by several ticks and to recover more slowly.
- Infection itself (exposed → infectious) is a pipeline: control changes should act on cases after a latent delay
  of a few ticks.
- "developing immunity": vaccination → protection takes time (a delay stage on vaccination's effect).
- "waiting lists and intervention histories start empty" → reset convention: queue = 0, memories = 0.

**Anything tied to time since reset:** "Unobserved resident compartments start in a fixed age mix determined by
the observed initial cases" → the susceptible/infected split is a deterministic function of the initial cases,
so the reset transient is deterministic given `initial`. There is no seasonality phrase. Big caveat: an
epidemic with susceptible depletion is not a relaxation-to-fixed-point system; cases may grow, peak and burn out
even at constant controls (hidden susceptible pool). P0 must show which regime we are in.

**Cross couplings named in the brief:** hospital pressure reduces clinic availability → vaccination's effect is
throttled when hospital_load is high (state-dependent control gain).

**Organizer-suggested comparisons (P9), quoted word for word:**
- P9a: "Compare closure with masking at similar case counts" — closure pulse vs mask pulse started at similar
  daily_cases.
- P9b: "vaccination before versus after a restriction pulse" — schedule V→R vs R→V (an order swap, P6).
- P9c: "follow both cases and hospital recovery" — holds after each pulse must be long enough for hospital_load to
  settle, not just cases.

## 2. The three mechanisms (§3.2)

The brief names exactly three history-retaining mechanisms (confidence: high):
"Behavior, developing immunity and postponed gatherings may retain intervention history."

- **M1 behavior** — behavioural response/adaptation to interventions (fatigue during long restrictions, or
  lingering voluntary caution after they are lifted).
- **M2 developing immunity** — protection that builds with a lag from vaccination (and possibly from
  infection) and persists after vaccination stops.
- **M3 postponed gatherings** — contacts suppressed by restrictions accumulate as a deficit and are released
  after restrictions lift (a rebound in contacts/cases).

## 3. Theses (§3.3)

### M1 behavior

| Field | Content |
|---|---|
| Quote | "Behavior ... may retain intervention history." |
| Hidden state | B: behavioural adaptation to restrictions (fatigue that erodes compliance while restrictions last; after lifting, it fades). Alternative sign: lingering caution. |
| **Driver** | the restriction controls (mask, closure) held on — control-level memory; possibly the perceived risk (hospital_load level) |
| **What it changes** | the size of the restriction effect on transmission: gain on the mask/closure effect decays as B builds (mode 'gain') |
| Timescales | builds over tens of ticks (20–100), fades similarly |
| P1 step on/off | present: after a restriction step, cases fall then partially creep back up during the hold (effect erodes); after lift, the rebound is small/normal. Absent: cases settle monotonically to a lower level (or keep declining) |
| P2 mid level | present: erosion also at u=0.5, proportionally | absent: plain scaling |
| P5 gap test | present: 2nd pulse after a short gap is weaker (fatigue not yet faded) | absent: equal |
| P6 order | little order dependence beyond fatigue carry-over |
| P7 long hold | present: restriction effect keeps eroding over a long hold | absent: stable level |
| P9a closure vs mask | fatigue may differ between controls (masks are behavioural) |
| P9b vacc before/after | no direct effect |

### M2 developing immunity

| Field | Content |
|---|---|
| Quote | "developing immunity ... may retain intervention history"; "vaccination uses a shared clinic workforce" |
| Hidden state | I: immune fraction built from vaccination (and infections), with a development lag; slow/no waning |
| **Driver** | vaccination control (throttled by hospital pressure) and possibly accumulated infections |
| **What it changes** | effective susceptibility → reduces transmission (cases level) persistently; hospital follows |
| Timescales | develops over ~10–30 ticks after vaccination; fades very slowly (> 150) |
| P1 vacc step on/off | present: cases decline starts only after a lag and keeps declining after vaccination stops (effect persists, no recovery to baseline). Absent: vaccination acts promptly and its effect disappears when it stops |
| P5 gap test | present: cumulative (second vaccination pulse adds on top) | absent: independent |
| P6 / P9b vacc before vs after restriction | present: vaccinating early (before restriction) gives more total protection / the restriction rebound is smaller when immunity was built first; vaccinating during high hospital load is less effective | absent: order does not matter beyond hospital throttling |
| P7 long hold | present: continuing decline over a long vaccination hold | absent: settled level |
| P1 restriction steps | present: infection-acquired immunity means that after a big wave the post-restriction baseline is lower; absent: returns to the same baseline |

### M3 postponed gatherings

| Field | Content |
|---|---|
| Quote | "postponed gatherings may retain intervention history" |
| Hidden state | G: backlog of postponed contacts, accumulating while restrictions are on |
| **Driver** | restriction level (closure, maybe masks) integrated over time (one-sided: builds when on) |
| **What it changes** | when restrictions lift, the backlog is released as extra contacts → a transient surge in transmission (target of cases, one-sided) |
| Timescales | builds over the restriction duration; releases over ~10–40 ticks after lift |
| P1 step on/off | present: after lift, cases overshoot above the pre-restriction baseline and then fall back; during the hold no erosion. Absent: cases return monotonically to baseline |
| P5 gap test | present: backlog carries over; a short gap gives a smaller release between pulses and a bigger one after the second | absent: equal |
| P6 order | present: the release depends on which restriction ended last (closure vs mask) | |
| P7 long hold | present: longer restriction → bigger rebound (if backlog saturates, up to a cap) | absent: no rebound, whatever the duration |
| P9a closure vs mask | present: gatherings are about where contacts happen → rebound after closure larger than after masks | |
| P9b vacc before/after | immunity built before the pulse damps the release surge |

## 4. Separation table (§3.4)

| Probe | M1 behavior (fatigue) | M2 developing immunity | M3 postponed gatherings |
|---|---|---|---|
| P1 restriction on (hold) | effect erodes during hold (cases creep back up) | none specific | no erosion |
| P1 restriction off | normal return | lower baseline after a big wave (infection immunity) | **overshoot above baseline** then fall back |
| P1 vaccination on/off | none | **lagged onset, persistent after stop** | none |
| P7 long restriction vs short | long → more erosion during hold | none | long → **bigger rebound after lift** |
| P5 short vs long gap | short gap → weaker 2nd pulse | cumulative | short gap → release carries over |
| P9a closure vs mask | may differ | none | rebound after closure > after mask |
| P9b vacc before vs after restriction | none | **order matters (persistent immunity)** | immunity damps release |

Pairs:
- **M1 vs M2 (M1M3 vs M2M3 world):** vaccination pulse on/off: M2 predicts lagged, persistent effect; M1 predicts
  none. Restriction hold: M1 predicts erosion, M2 none.
- **M1 vs M3:** long restriction hold: M1 → erosion during the hold, M3 → flat during hold but rebound after lift;
  short vs long pulse rebound size (M3 grows with duration, M1 does not produce a rebound above baseline).
- **M2 vs M3:** vaccination pulse (M2 persistent, M3 nothing) and restriction lift (M3 overshoot, M2 nothing);
  P9b order swap.

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 (start) | — | — | 0 | 2,000 |
| 2026-09-27 00:35 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 2026-09-27 00:35 | R1 | 40-59 (P0 recovery) | 20 | 1940 |
| 2026-09-27 00:35 | R1 | 60-79 (P0 recovery) | 20 | 1920 |
| 2026-09-27 00:36 | R1 | 80-99 (P0 recovery) | 20 | 1900 |
| 2026-09-27 00:36 | R1 | 100-119 (P0 recovery) | 20 | 1880 |
| 2026-09-27 00:36 | R1 | 120-159 (P1 mask on) | 40 | 1840 |
| 2026-09-27 00:36 | R1 | 160-184 (P1 mask on, ext) | 25 | 1815 |
| 2026-09-27 00:36 | R1 | 185-224 (P1 mask off) | 40 | 1775 |
| 2026-09-27 00:37 | R1 | 225-269 (P1 closure on) | 45 | 1730 |
| 2026-09-27 00:37 | R1 | 270-314 (P1 closure off) | 45 | 1685 |
| 2026-09-27 00:37 | R1 | 315-374 (P1 vaccination on) | 60 | 1625 |
| 2026-09-27 00:37 | R1 | 375-434 (P1 vaccination off) | 60 | 1565 |
| 2026-09-27 00:43 | R1 | 435-469 (P2 mask 0.5) | 35 | 1530 |
| 2026-09-27 00:43 | R1 | 470-494 (recovery) | 25 | 1505 |
| 2026-09-27 00:43 | R1 | 495-519 (P3 mask+closure) | 25 | 1480 |
| 2026-09-27 00:43 | R1 | 520-544 (P9b vaccination after restriction) | 25 | 1455 |
| 2026-09-27 00:44 | R2 | 0-9 (P0 short), 10-39 (vaccination before restriction) | 40 | 1415 |
| 2026-09-27 00:44 | R2 | 40-89 (P7 mask+closure hold, part 1) | 50 | 1365 |
| 2026-09-27 00:44 | R2 | 90-139 (P7 mask+closure hold, part 2) | 50 | 1315 |
| 2026-09-27 00:44 | R2 | 140-189 (P7 mask+closure hold, part 3) | 50 | 1265 |
| 2026-09-27 00:44 | R2 | 190-239 (P7 mask+closure hold, part 4) | 50 | 1215 |
| 2026-09-27 00:45 | R2 | 240-299 (lift: recovery, rebound test) | 60 | 1155 |
| 2026-09-27 00:45 | R2 | 300-329 (P9a closure), 330-349 (recovery) | 50 | 1105 |
| 2026-09-27 00:45 | R2 | 350-379 (P9a mask), 380-399 (recovery) | 50 | 1055 |

Spend summary: R1 = 545 steps (cap 550), R2 = 400 (cap 400), total 945. Budget remaining 1,055; **55 steps of
the 1,000 CAP are left as the Phase-C reserve.** (Timestamps are the machine clock.)

## 6. Run 1 observations (`data/epidemic/R1.json`, 545 ticks, initial 113.8 / 37.7)

Schedule: recovery 0–119 | mask 120–184 | recovery 185–224 | closure 225–269 | recovery 270–314 |
vaccination 315–374 | recovery 375–434 | mask 0.5 435–469 | recovery 470–494 | mask+closure 495–519 |
vaccination 520–544. Plot: `data/epidemic/R1_r0_battery.png`; battery text `data/epidemic/R1_battery.txt`.

- **The reset transient is a full epidemic wave**, not a relaxation: cases 114 → 502 (tick 23) → trough 45.4
  (tick 91) → rising again at 1.7%/tick. Hospital first dips 37.7 → 26.9 (ticks 0–3, admission pipeline
  empty), then rises to a **hard ceiling of 155.3 ± 0.4** at tick 22 and stays there until tick 71 (about 50
  ticks after the case peak, while the referral waiting list drains). It then decays ≈ 5–6%/tick to ~39.
- **P0 never settles** (> 120): a damped epidemic oscillation (hidden susceptible pool refilling).
- **Mask (P1)**: fast, 1-tick latent, 4–8-tick transition. On: 64 → 46 (−28%), then a slow slide to 34.7 and
  a slow creep back up (34.7 → 38.3 over 25 ticks, mask still on). Off: 39 → 55 in 4 ticks (+40%), then a new
  wave. ln(0.72) = −0.33 against ln(1.40) = +0.34, so the effect is **symmetric in log units**: a
  multiplicative effect on transmission.
- **Mask 0.5 (P2)**: 103 → 89 (−14%; log −0.15 vs −0.33 at full), **≈ linear in u**.
- **Closure (P1)**: **no fast jump**, on or off. Applied at 197 cases during a growing wave, growth bent over
  within ~5 ticks, peak 207 at tick 231, then decline. Off at 99: the decline flattens, trough 88 at tick 285.
  During the closure, hospital reached the 155 cap at only ~200 cases (the first wave needed ~450), so
  **closure raises the hospital/case ratio** ("changes where contacts occur" → more household/elderly contact).
- **Mask+closure (P3)**: 112 → 83 in 6 ticks (the fast mask part), then a continued decline to 47 at tick 519.
  Hospital kept rising for 12 ticks after the switch (lag plus the closure severity shift).
- **Vaccination (P1)**: lagged ~7 ticks. Cases plateau at ~96, then decline 96 → 80 over 60 ticks. After it
  stops, the decline ends within ~8 ticks (78.3 at tick 384) and cases rise again (102 by tick 434). The
  effect is neither immediate nor visibly persistent after stopping (the epidemic refills).
- **Vaccination right after a restriction (P9b, 520–544)**: after mask+closure is lifted, cases rebound
  45 → 93 in 25 ticks despite vaccination.
- **Noise σ**: 0.23% of level (cases), 0.21% (hospital), proportional. It is tiny, so misfit dominates.

## 7. Behaviour catalogue v1 (after Run 1)

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 | Reset transient = epidemic wave (peak ~502 at tick 22–24), trough ~45 at tick 90, second rise | R1 0–120, battery png | SEIR(S) with a large initial susceptible pool (S0 fitted ≈ 1.0, pinned) | modeled by base SEIRS |
| B2 | Hard hospital ceiling 155.3, held ~50 ticks after the case peak | R1 21–71, 243–264 | bed capacity + referral waiting list (brief) | modeled by Hcap + queue Q (qab abandonment) |
| B3 | Hospital dips ~25% in the first 3 ticks | R1/R2 ticks 0–4 | admission pipeline starts empty (reset rule) | modeled (fp → 0) |
| B4 | Closure raises the hospital/case ratio | R1 225–269 reaches the cap at ~200 cases; R2 hold ratio 0.80 vs 0.67 unrestricted | age-mix shift (contacts move into households) | modeled by base term `hc` (data-driven, added after R1) |
| B5 | Mask: fast multiplicative drop/jump, log-symmetric, linear in u | R1 120/185/435; R2 350/380 | direct β reduction | modeled (wm) |
| B6 | Closure: no fast component, gradual effect | R1 225/270; R2 300/330 | age structure (children's contacts), lag stage | modeled by the closure lag a_c (fits give 0.11–0.20; one joint fit pinned it at 1) |
| B7 | Vaccination lagged ~7 ticks, weak, reverses soon after stopping | R1 315–434 | M2 developing immunity (lag) vs plain S→R depletion + refill | open (a_m2 = 0.40 in the R1 m12 fit; m23 and the joint m12 switch m2 off, a_m2 → 1) |
| B8 | Cases creep up while a restriction is held | R1 160–184 (+0.4%/tick) | M1 fatigue, or susceptible replenishment (ω) | open → see B11 |
| B9 | Damped endemic oscillation, level ~90 cases / ~64 beds | R1 270–330 | SEIRS waning ω ≈ 0.015–0.017 | modeled by base |
| B10 | First-wave peak underestimated by the base-only model (440 vs 502) | base fit plot | heterogeneity (age groups) / slow m1 term | partly: the R1 m12/m13 fits reach 500 |

## 8. Model module and Run-1 pair fits

Module: `toronto26-participant-kit/greybox/epidemic_model.py`: a single-population SEIRS with vaccination,
referral lag, waiting queue and bed cap. The mechanism modules were written from the theses before fitting:
- **m1 behaviour**: memory F of restriction (a mix of lagged closure and mask). `fat = 1 − gF·F` scales the
  restriction effect (fatigue), and `exp(−gL·F)` is a lingering-caution term.
- **m2 developing immunity**: vaccinated people go S → W (still susceptible) → R at rate a_m2; off = instant
  (a_m2 = 1).
- **m3 postponed gatherings**: a backlog B builds while restricted and is released after the lift as a contact
  boost `1 + g3·(1 − ρ)·B` (one-sided).
- Units are log/log (symmetry test, B5). The residual scale is 0.01 (true noise 0.2%; misfit-dominated). Bed
  cap and queue follow B2. Data-driven base addition: `hc` (B4).

Fits (all on R1 ticks 0–434, soft_l1). Init = base fit with the module parameters at their SPEC defaults.
**Tooling note:** `--init` from a fit whose gains sit at their off value (0) leaves those gains stuck, because
the exp/sigmoid transforms have zero gradient there (the first attempt, `*_r1a.json`, reproduced the base cost).

| Fit | Cost | Train score (σ = 0.1 std) | Notes |
|---|---:|---:|---|
| base, no hc (`base_r1`) | 6114 | 0.706 | S0, a_c, ev pinned at 1; kappa, fp pinned at 0 |
| base + hc (`base2_r1`) | 3361 | 0.778 | hc = 0.43 |
| **m1+m2** (`m12_r1`) | **1895** | 0.847 | gF_m1 = 1.0 (pinned), a_m1 = 0.0015, gL = 0.61: a very slow cumulative β reduction; a_m2 = 0.40 |
| m1+m3 (`m13_r1`) | 1975 | 0.837 | gF_m1 = 0.997 (pinned), a_m1 = 0.007; g3 = 0.20 (barely moved from its start) |
| m2+m3 (`m23_r1`) | 2705 | 0.807 | a_m2 = 1.0 (m2 unused), g3 = 28.6 with ain = 0.0007 (m3 acting as a slow integrator) |

Reading: M1 helps most on R1, but through a pinned gain and a near-integrator memory. Per lesson 9 that is
probably standing in for missing structure (heterogeneity: high-contact groups infected and immune first),
not clean evidence for behaviour.

## 9. Run 2 design (§4.4)

Screening: each candidate was simulated through the three R1 pair fits from a reset (initial 170/45). The
table gives the mean |pairwise difference| / score-σ (σ = 0.1×std of R1: 8.6 cases, 4.5 beds). All candidates
are about the same length, so the per-step ranking equals this mean.

| Candidate (from reset) | Steps | m12/m13 | m12/m23 | m13/m23 | mean |
|---|---:|---:|---:|---:|---:|
| D: rec 60, mask+closure 120, rec 80 (long restriction → rebound) | 260 | 1.55 | 3.28 | 4.64 | **3.15** |
| G: rec 10, all three 60, rec 190 (early joint in the first wave) | 260 | 1.63 | 1.72 | 3.03 | 2.13 |
| J: long mask 150 | 260 | 0.12 | 1.75 | 1.74 | 1.20 |
| E: 3 short joint pulses, gaps 20 (P5) | 240 | 0.71 | 1.04 | 1.59 | 1.11 |
| I: long vaccination 150 | 260 | 0.45 | 1.26 | 1.52 | 1.08 |
| B: P9b restriction → vaccination | 200 | 0.90 | 0.67 | 1.33 | 0.97 |
| K: long closure 150 | 260 | 0.98 | 0.78 | 1.10 | 0.95 |
| A: P9b vaccination → restriction | 200 | 0.79 | 0.64 | 1.33 | 0.92 |
| H: long recovery | 260 | 0.15 | 0.82 | 0.94 | 0.64 |
| L: mask pulses with gaps 10 / 60 | 260 | 0.14 | 0.74 | 0.84 | 0.57 |
| C: P9a mask vs closure | 260 | 0.25 | 0.55 | 0.72 | 0.51 |
| F: mask 0.5 long | 260 | 0.13 | 0.46 | 0.43 | 0.34 |

Full Run-2 schedules compared (400 steps): the **chosen** `rec 10 | vacc 30 | mask+closure 200 | rec 60 |
closure 30 | rec 20 | mask 30 | rec 20` scores m12/m13 3.60, m12/m23 5.34, m13/m23 6.87, the best on the
hardest pair (m12/m13). D-like (rec 60, joint 200, rec 140) scores 3.16/5.58/6.72; G-like 2.54/5.71/6.57.

Reasons: the long joint restriction and its lift is the best separator (M1 erosion during the hold vs the M3
rebound after it), and it doubles as P3 + P7 (200 ≥ 200). Vaccination just before it is P9b (vaccination
before a restriction pulse). The closure and mask pulses at the end are P9a. The coverage items that did not
fit into 400 went on the end of Run 1 (R1 435–544, 110 steps; R1 ≤ 550): P2 mask 0.5, P3 at u = 1 for a short
pulse, and P9b's other order (vaccination right after a restriction pulse). The R1 extension candidates scored
low (0.4–0.6 σ); they were run for coverage, not separation.

## 10. Run 2 observations and catalogue v2 (`data/epidemic/R2.json`, 400 ticks, initial 124.0 / 44.0)

Plots: `data/epidemic/R2_r0_battery.png`; the cross-run check of the R1 fits is
`data/epidemic/R2_crossrun_r1fits.png`; the quick joint fits are `data/epidemic/R2_allquick_fits.png`.

- **The initial reading barely matters**: R2's first wave peaks at 501.6 (tick 22) against R1's 502 (tick 23),
  with the same cap timing. The hidden state after a reset is effectively fixed.
- **Vaccination during the first wave (ticks 10–39) had no visible effect** on the wave. Possible reasons: the
  hospital was at the cap, so clinics were throttled as the brief says, and/or immunity was still developing.
  This is the "vaccination before" half of P9b.
- **Joint restriction held 200 ticks (40–239), started at the peak**: cases fall 245 → a **floor of 15.5 at
  tick 89**, then **rise while the restriction is still on** (~2%/tick) and plateau at **~89 by ticks
  220–239**, about the same level as the unrestricted endemic level (~90 in R1). Hospital stays at the 155 cap
  until tick 64, reaches a floor of 17.6 at ~117, then rises to 71 (ratio 0.80: the closure severity shift B4
  again).
- **Lift at 240**: a fast +40% jump in 4 ticks (the mask part), then a wave to **193 at tick 270**, hospital to
  132 at ~292, then decline. The R1 pair fits predicted a 1–5-case floor and a much later, bigger wave
  (330–400), so **all three R1 pairs fail the cross-run test badly**.
- **P9a closure vs mask** (closure at 126 falling, ticks 300–329; mask at 75 rising, 350–379): mask gives the
  fast −29% (on) / +42% (off) jumps again. Closure gives no jump and a gradual decline, and the hospital decline
  slows while schools are closed (−0.8/tick) and speeds up afterwards (−1.3/tick). The case counts were only
  approximately similar (126 vs 75).

**Cross-run test (fit on R1 ticks 0–434, predict R2; σ = 0.1×std of R1+R2):** base+hc 0.286, m23 0.262,
m12 0.254, m13 0.234; persistence 0.168. All beat persistence, but all badly miss the long-restriction segment.

**Quick joint fits on R1+R2** (one pass, 3 restarts, `--init fits/epidemic/init_r1.json`, not converged; for
orientation only, `fits/epidemic/*_all_quick.json`):

| Pair | Cost | Train score | Notes |
|---|---:|---:|---|
| m1+m3 | 27,230 | 0.594 | a_m1 = 0.070, gF = 0.62 (fatigue on a ~15-tick scale); m3 small (g3 0.14, aout 0.003) |
| m1+m2 | 29,362 | 0.580 | a_m1 = 0.094, gF = 1.0 (pinned); a_m2 → 1 (m2 unused); a_c pinned at 1 |
| m2+m3 | 42,602 | 0.523 | barely moved (nfev small); g3 → 0, a_m2 → 1: neither module used |

With faster fatigue (a_m1 ≈ 0.07–0.09) the in-restriction recovery (B11) is reproduced, but the first-wave
peak (~370 instead of 502) and the bed cap are lost: Hcap drifted to 305–329 in the two m1 fits, so the
predicted hospital reaches ~197. Both m1 pairs pin gF at or near 1. The structure is still wrong: see the open items below.

Catalogue v2 (new or updated behaviours):

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B11 | Under a long joint restriction, cases floor at 15.5 (not ~1) and recover to the unrestricted endemic level (~89) while restrictions stay on | R2 40–239 | (a) heterogeneity: an age group whose transmission the restrictions barely touch; (b) M1 behavioural fatigue on a ~15–100-tick scale; (c) faster waning/refill; (d) importation floor | **not captured** by R1 fits (they collapse to 1–5); joint fits capture it only with m1 fatigue while losing B1/B2 |
| B12 | Post-lift rebound 88 → 193 after 200 ticks of restriction, starting at once (+40% in 4 ticks = the mask part) | R2 240–299 | susceptible build-up during the restriction; M3 release | open (compare with the R1 rebound after the 65-tick mask at 185: 39 → 207 with closure applied at 225) |
| B13 | Vaccination during a hospital-capped wave has no visible effect | R2 10–39 vs R1 | clinic throttling by hospital pressure (kappa; brief); developing-immunity lag | open (kappa pinned at 0 in every fit) |
| B14 | First-wave shape independent of the initial reading (114 vs 124 → same peak and timing) | R1 vs R2 0–40 | fixed hidden initialization | modeled only if the S0/rI rule is right; a third initial reading would check it |
| B15 | Hospital decline slows during closure, speeds up after | R2 300–349 | hc (B4) | modeled by hc |
| B16 | Closure's effect on cases is gradual and weaker than masks' | R1 225; R2 300 | age structure (children) | modeled by lag a_c (an approximation) |
| B17 | Hospital/case ratio changes over time even without closure (first wave needs ~450 cases to cap; endemic ratio 0.67) | R1 | age mix of infections shifts across waves (heterogeneity) | not captured (single-group model) |

**Separating probes and P9s run:**
- D-type long restriction + lift (M1 vs M3): ✓, R2 40–299. In-hold recovery seen (M1-like or heterogeneity);
  large rebound (M3-like or plain susceptible build-up).
- Vaccination on/off for M2: ✓, R1 315–434. Lagged onset; no visible persistence.
- P9a: ✓, R2 300–379 (case counts only roughly matched, 126 vs 75).
- P9b, both orders: ✓. Vaccination before: R2 10–39 → joint at 40. After: R1 495–519 joint → 520–544
  vaccination. The "before" pulse fell in the capped first wave, so the two orders differ in more than order.
- P2 ✓ (R1 435). P3 ✓ (R1 495, R2 40). P7 ✓ (R2 joint 200). P6 order swap ✓ (via P9b). **P5 gap test not run.**

## 11. Status / hand-off to reviewer

**Files**
- Data: `toronto26-participant-kit/data/epidemic/R1.json` (545 ticks), `R2.json` (400 ticks), with battery
  JSON/TXT/PNG for each, `R2_crossrun_r1fits.png` and `R2_allquick_fits.png`.
- Model: `toronto26-participant-kit/greybox/epidemic_model.py`.
- Fits: `toronto26-participant-kit/fits/epidemic/`: `base_r1`, `base2_r1`, `init_r1` (start point),
  `m12_r1`, `m13_r1`, `m23_r1` (the Run-1 pair fits), `*_all_quick` (unconverged joint fits), plus logs.

**Budget:** 945 of the 1,000 CAP spent. 1,055 remain in the account; **55 are available to Phase C**.

**Open items for the reviewer/modeler, most important first**
1. **B11 (floor + recovery under a sustained restriction) is the main structural gap.** A single-population
   SEIRS cannot keep cases at 15 and bring them back to 89 under a 28% transmission cut without either fast
   M1 fatigue or heterogeneity. The strongest candidate is a 2–3 age-group model (the brief says "three
   interacting age groups ... differ in contacts, severity and recovery"; closure acts on children's contacts).
   That would also explain B6, B10, B16 and B17. Test m1 fatigue against it; don't accept m1 because of a
   pinned gF.
2. **Pair identification is weak.** m2 is switched off (a_m2 → 1) in three of the four fits that include it,
   and m3's gain collapses in the joint fits. The R1 winner (m12) and the joint winner (m13) differ. Nothing is
   decided yet.
3. **The optimizer stops early** (nfev 4–150) and parameters sit at sigmoid limits (S0, a_c, ev = 1; kappa,
   fp = 0), where the gradient vanishes. Consider reparametrizing, or restarting from interior values.
4. **Hospital cap**: in the m12/m13 joint quick fits, Hcap drifted to 329/305 (m23 kept 155.2), so the cap
   stopped binding, and hospital went to ~197 in the first wave. The code is fine (H ≤ Hcap by construction).
   The observed cap is 155.3 ± 0.4 in every episode, so fix Hcap = 155.3 (`--fix Hcap`) in later fits.
5. **kappa (clinic throttling) is unidentified** except by R2 10–39 (vaccination at the cap had no visible
   effect, B13).
6. **No P5 gap test** was run. If the reserve is spent, a short pair of mask pulses with a 10- vs 40-tick gap
   is the cheapest (~70–100 steps, though that exceeds the 55 reserve). A 50-step R2 continuation (mask 20,
   gap 10, mask 20) is feasible if R2 is still alive.


## 12. Review responses (Phase C modeler, 2026-09-27)

Model v2: `greybox/epidemic_model.py` (three-age-group SEIRS; v1 kept as `greybox/epidemic_model_single.py`).
Fits: `fits/epidemic/v2/`. Reserve spent in Phase C: **0 steps** (55 still available under the CAP).

| Gap | Response | Evidence |
|---|---|---|
| G1 single population can't fit both runs | **Fixed.** Three age groups (children 0.2 / adults 0.6 / elderly 0.2, proportional mixing with activities a0, a2, plus a child–child school term bs). Closure removes the school term and can move child activity into the home term (dsh); per-group severity (sev0, 1, sev2) replaces hc. Transmission scales are log-parameterised and S0 starts in the interior. Hcap FIXED = 155.2, qab floored at 0.005. | Even the no-mechanism v2 joint fit (`base_all`) reproduces both first waves (peak 522/508 vs 501/501), the cap, the R2 floor (17 vs 15.5 at tick 89) and the restricted plateau (82 vs 89 at tick 220). Joint cost 20,657 (base) / 8,839 (m13) vs 27,230 for the best v1 quick joint fit. |
| G2 long-run level under sustained controls | **Fixed / reported.** Endemic incidence ≈ ω(1 − 1/R0) is insensitive to restrictions once R0 is large; the joint fits sit in that regime. 4,000-step settled cases (ticks 3,500+, initial 170): see table below. Candidates agree within ~1σ (σ ≈ 8.3 cases) for every schedule, and all reproduce the restricted plateau ≈ 88–92 at R2 ticks 220–240. | `scratchpad chk` output, recorded below |
| G3 absorbing extinction | **Fixed.** Importation `new += eps·S` (fitted eps ≈ 3e-4). Stability gate min cases over 200 schedules incl. 8 × 40,000 steps: 17.9 (m13) / 16.4 (m12) ≥ 5. | `gates stability` |
| G4 risk-driven behaviour | **Tested, rejected by the data.** m1 has a hospital-memory term exp(−gR·Hm/Hcap); every joint fit drives gR → 0 (1e-4). Fatigue (gF 0.40–0.50, a_m1 ≈ 0.044, driven mostly by closure, mix ≈ 0.9–1.0) is what m1 uses. | m12_all, m13_all params |
| G5 vaccination unidentified | **Partly.** Throttle is now queue-driven (thr = 1/(1+kappa·Q/Hcap)). m13_all uses it (kappa ≈ 1,077: vaccination blocked while a waiting list exists = B13). m2 still collapses (a_m2 → 1 in m12_all, m23_all): M2 is **not identifiable** with the data, not rejected. | params |
| G6 all-three pulse / vacc+restriction / controls in the growth phase never observed | **Not captured with data**; relies on multiplicative composition (supported for mask+closure). Reserve not spent (see below). | — |
| G7 unconverged fits, no bootstrap | **Addressed**: v2 joint fits ran up to nfev 600 × 2 restarts; bootstrap run (2 draws, see §13). Optimizer still hits nfev limits; restart spread is large (8.8k vs 20.9k), so costs are upper bounds. | logs in `fits/epidemic/v2/` |
| G8 P9a / P9c residuals | Evaluated qualitatively: m13_all tracks R2 300–399 within ≈ 1–2σ (cases 137 vs 126 at 300, 38 vs 36 at 380; hospital 122 vs 128 at 300). | chk output |
| G9 early transient spike | **Not captured**: all fits still overshoot ticks 1–3 (+14–25%: 138 vs 114). Low weight (3 of 4,000 ticks). | chk output |
| G10 shared clinic workforce | Not tried (time); low priority. | — |

Reserve decision: G1–G3 were resolved structurally without new data, and the remaining open item (m2 identifiability,
closure parameters dsh/wc at their limits) would not be settled by 55 steps plus a refit within this phase's time.
**0 of the 55 reserve steps spent**; the reviewer's closure-from-reset probe remains the best use if a later phase
has time to refit.

Long-run settled cases / hospital (ticks 3,500–4,000, initial 170/45; `rec` = recovery, `pulse` = all three at
max, `mc` = mask+closure):

| Fit | rec | pulse | mask only | closure only | mask+closure | all at 0.5 | vacc only |
|---|---|---|---|---|---|---|---|
| base_all | 98 / 75 | 52 / 39 | 78 / 59 | 98 / 75 | 78 / 59 | 78 / 59 | 78 / 59 |
| m12_all | 106 / 80 | 45 / 34 | 64 / 46 | 102 / 79 | 78 / 59 | 71 / 53 | 76 / 55 |
| **m13_all** | 107 / 80 | 42 / 33 | 65 / 45 | 101 / 82 | 74 / 58 | 72 / 55 | 77 / 54 |
| m23_all | 100 / 78 | 47 / 35 | 71 / 53 | 104 / 81 | 74 / 57 | 75 / 57 | 75 / 56 |

All within 2σ of each other except mask-only (64–78, ~1.7σ); restricted equilibria are 40–70 % of the
unrestricted one (data only constrain mask+closure up to 200 ticks: ≈ 89 at tick 220–239, reproduced by all).

## 13. Model selection (§6.3)

**Cross-run test** (fit on R1 only, predict R2; σ = 0.1×std after tick 20 of R1+R2 = 8.34 cases, 4.19 beds):

| Model | R1 cost | R1 train score | R2 score (cross-run) |
|---|---:|---:|---:|
| base v2 (no mechanism) | 4,315 | 0.760 | **0.410** |
| m12 | 4,868 | 0.750 | 0.374 |
| m13 | 3,802 | 0.786 | 0.344 |
| m23 | 4,822 | 0.760 | 0.312 |
| persistence | — | 0.201 | 0.168 |
| (v1 best, base+hc) | | | 0.286 |

R1 alone does not identify R0 (base_r1 went to the low-R0 regime: s0 → 1, eps → 0), so the cross-run test mostly
measures optimizer luck; every v2 model beats both persistence and every v1 fit. The ordering does not favour any
pair; the no-mechanism model is best cross-run.

**Refit on all data** (R1 + R2, 945 ticks, 2 restarts, nfev ≤ 600, Hcap fixed):

| Pair | Cost | R1 score | R2 score | Pinned parameters |
|---|---:|---:|---:|---|
| base (no mechanism) | 20,657 | 0.629 | 0.607 | a_c → 0, qab → 1, ev → 1, kappa → ∞ |
| m1+m2 | 10,623 | 0.737 | 0.716 | a_m2 = 1 (m2 unused), dsh = 1, mix_m1 = 1, sev0 = 0, kappa = 0, ev = 1 |
| **m1+m3** | **8,839** | **0.750** | **0.728** | aout_m3 = 1 (instant release), dsh → 0, sev0 = 0, wc = 0, ev = 1 |
| m2+m3 | 20,389 | 0.628 | 0.669 | a_m2 = 1 (m2 unused) |

M1 (fatigue, driven mainly by the closure level) is the mechanism that matters: any pair without it is no better
than the base. m13 beats m12 by 1,784 (17 %); the m3 part is a one-tick release boost on lift (aout pinned at 1).

**Bootstrap** (`python -m greybox.common.bootstrap --draws 2 --restarts 1 --workers 3`, stopped after 3 of 6 jobs
for time; `fits/epidemic/v2/bootstrap.json`):

| Truth \ selected | m12 | m13 | m23 |
|---|---:|---:|---:|
| m12_all (2 draws) | 1 | 1 | 0 |
| m13_all (1 draw) | 1 | 0 | 0 |

Synthetic refit costs are 48k–67k against real costs of 8.8k–20k: the bootstrap refits start from the SPEC
defaults and do not converge, so the matrix measures optimizer failure, not identifiability. Bootstrap margins
m12/m13: 38, 792, 4,363 (both signs) vs a real margin of 1,784. m23 is never selected (consistent with "M1 is
needed").

**Decision (§6.3.4): m1+m3, "unresolved".** The diagonal is weak/uninformative (optimizer-dominated) and both M1
pairs have pinned parameters (m13: aout_m3 = 1; m12: a_m2 = 1, i.e. m2 unused, so m12 is effectively m1-only).
m13 has the lowest all-data cost (−17 % vs m12) and the best in-sample scores on both runs; its long-run
equilibria agree with m12 within 1σ, so the choice matters little for the 4,000-step scores. M2 is **not
identifiable** from R1+R2. The cross-run test favours the no-mechanism base (0.410), but R1 alone does not pin R0,
so that comparison is weak evidence; the base's joint cost is 2.3× m13's.

## 14. Final model and hand-off (Phase C)

- **Chosen:** v2 three-age-group SEIRS + m1 (fatigue) + m3 (release), fitted on R1 + R2 = `fits/epidemic/v2/m13_all.json`
  (copied to `fits/epidemic/final.json`). Confidence: **unresolved** (m1 accepted as needed; m3 vs m2 not separated).
- **Scores** (σ = 0.1×std after tick 20: 8.34 cases, 4.19 beds): cross-run R1 → R2 = 0.344 for m13 (base 0.410,
  m12 0.374, m23 0.312) vs persistence 0.168. All-data fit: R1 0.750, R2 0.728 (persistence 0.201 / 0.168).
- **Gates:** local score beats persistence on R2 when fitted on R1 (all four models) ✓; stability (200 schedules,
  8 × 40,000 steps) pass, 0 failures, cases ∈ [17.9, 576], hospital ≤ 155.2, alternation 0.03 ✓ (G3 floor ≥ 5 ✓);
  contract pass (40 × 4,000 steps in 4.8 s, all malformed-input cases ok) ✓; credential scan clean ✓.
- **ZIP:** `toronto26-participant-kit/submission-epidemic-v1.zip` (6 KB); folder `toronto26-participant-kit/models/epidemic/`.
- **Steps:** 945 of the 1,000 CAP spent (0 in Phase C); 55 reserve left; 1,055 left in the account.
- **Top open issues:**
  1. Optimizer convergence: restarts differ by 2× in cost and fits stop at nfev 600; a longer/warm-started refit
     (e.g. from `m13_all.json` with more nfev and restarts from interior values of the pinned parameters) would
     likely lower the cost. The bootstrap should warm-start its refits from the real fits to be informative.
  2. Closure is weakly identified (dsh, wc at limits; a_c ≈ 0.2): the reviewer's reserve probe (closure 1.0 from
     reset, 55 steps) is still the best use of the reserve, followed by a refit.
  3. Controls in the first-wave growth phase and all-three composition were never observed (G6), and the ticks 1–3
     overshoot (G9) remains; vaccination/M2 is not identifiable.


## Round 2 spend log (approved by the user 2026-09-28; schedules in `plans/round2-experiments.md`)

| Date | Run | File | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-28 14:44–14:55 UTC | EP1 (fresh reset) | `data/epidemic/R3.json` | 400 | 655 |
| 2026-09-28 14:44–14:55 UTC | EP2 (fresh reset) | `data/epidemic/R4.json` | 300 | 355 |
| 2026-09-28 14:44–14:55 UTC | EP3 (fresh reset) | `data/epidemic/R5.json` | 200 | 155 |

Segment files: `toronto26-participant-kit/fits/round2/segments/epidemic_*.json`. Server budget confirmed after the runs.
