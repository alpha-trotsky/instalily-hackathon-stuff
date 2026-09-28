# Reservoir plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 02:05 (overnight job, `plans/overnight-framework.md`). CAP = 1,000 steps
(Run 1 ≤ 550, Run 2 ≤ 400, reserve ≥ 50). Budget at start: 2,000 remaining (free read). No earlier plan or data.

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Reservoir water volume, incoming and delivered outgoing water per tick, and an outlet
water-quality index from zero to one. Release and irrigation request water per tick. Withdrawal depth selects shallow
versus deep release; irrigation draws near the surface. / Aeration increases oxygen transfer and vertical mixing.
Water is stratified: temperature, dissolved material, algae and oxygen can differ by depth, although only aggregate
volume and outlet quality are observed. Seasonal river supply brings nutrients. / Light, nutrient availability,
decomposition and oxygen interact. Biomass can foul withdrawal screens, restricting actual discharge; flushing and
aeration remove some of that attached material. Groundwater, irrigated land and deposited material may return water
or contaminants after a delay. / A deep release can change later surface quality by changing stored layers, while
aeration can either dilute an outlet or remobilize deeper material. Initial instrument readings are observed; internal
layers start from the same reference profile on every reset. A tick is one operating day."

**Observables** (docs initial-reading ranges):

| Observable | Initial range | Notes |
|---|---|---|
| level | 400 – 600 | water *volume* (a stock): expected Δlevel ≈ inflow − outflow − irrigation + returns. Integrator, not a relaxation; must be bounded by something (spill, level-dependent outflow/seepage) over 4,000 ticks |
| inflow | 8 – 12 | per tick; river supply (**seasonal**, tied to time since reset) + possibly groundwater / irrigation return flows |
| outflow | 4 – 8 | *delivered* outgoing water per tick; requested release (and irrigation?) limited by screen fouling; maybe spill |
| quality | 0.78 – 0.94 | outlet index in [0, 1]; depends on withdrawal depth (layer drawn), stratification, algae/oxygen, contaminants |

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u | Range of u | Notes |
|---|---|---:|---:|---|---|---|
| release_rate | [0, 12] | 2 | 12 | (r − 2)/10 | [−0.2, 1] | **recovery not at a bound**: 0–2 (u < 0) is the untested side |
| irrigation_allocation | [0, 8] | 0 | 8 | i/8 | [0, 1] | draws near the surface |
| withdrawal_depth | [0, 1] | 0 (shallow) | 1 (deep) | d | [0, 1] | selects the layer released → outlet quality |
| aeration | [0, 1] | 1 | 0 | 1 − a | [0, 1] | recovery = full aeration; pulse = none (stratified, low oxygen at depth) |

**Structure from the brief (base model, not mechanisms):**
- Water balance: level is a stock. Outflow = delivered release (request limited by fouled screens); irrigation is
  requested water that also leaves the reservoir (it may or may not be counted in `outflow`, to be seen).
- Screen fouling (biomass attaches, restricts discharge; "flushing and aeration remove some"): a hidden state that
  grows with biomass (algae, favoured by nutrients/light, low mixing) and is removed by high release (flushing) and
  aeration. Expect: delivered outflow < requested release, more so with aeration off; a release pulse flushes.
- Stratification: aeration mixes layers; with aeration off, layers separate (surface warm/algae, bottom low oxygen).
  Withdrawal depth selects which layer leaves: outlet quality jumps when depth switches; draining one layer changes
  later surface quality ("A deep release can change later surface quality by changing stored layers").
- Seasonal river supply (nutrients + water): inflow and nutrient load follow a deterministic season tied to time
  since reset. A tick is one day, so the period may be ~365 ticks (or shorter). One run covers ≤ 1.5 cycles. For
  the 4,000-step forecast we need the period and phase: model as a sinusoid (fixed phase at reset) and check that R1
  and R2 (fresh reset) agree in phase.
- **Delay / commitment phrases → lag stages:** "may return water or contaminants after a delay" (the three
  mechanisms); "can change later surface quality" (layer memory). No order-pipeline phrase.
- **Time since reset:** seasonal supply; "internal layers start from the same reference profile on every reset"
  → a deterministic reset transient (layers relaxing from the reference profile).
- **Organizer-suggested comparisons (P9):** the brief has no explicit "Compare …" sentence. Implied by the last
  paragraph:
  - **P9a** deep release, then return to shallow: does *surface* (shallow-outlet) quality afterwards differ from
    before? ("A deep release can change later surface quality by changing stored layers")
  - **P9b** aeration effect on outlet quality with shallow vs deep withdrawal ("aeration can either dilute an
    outlet or remobilize deeper material"): aeration off→on while deep vs while shallow.
  - **P9c** flushing: high release after a period of aeration off (fouled screens) — does outflow deliver less than
    requested and recover?

## 2. The three mechanisms (§3.2)

The sentence that lists three parallel "may …" processes (same pattern as epidemic/wildlife):
"**Groundwater, irrigated land and deposited material may return water or contaminants after a delay.**"
Confidence high (~80%). Fouling, stratification and seasonality are described as always-on physics (base model).

- **M1 groundwater return:** reservoir water seeps to groundwater (more when level is high) and returns as extra
  inflow (maybe with dissolved contaminants) after a delay.
- **M2 irrigated-land return:** part of the irrigation water returns from the irrigated land as delayed inflow,
  carrying contaminants (fertiliser nutrients, salts) that lower quality.
- **M3 deposited material (internal loading):** material settled on the bottom (from inflow nutrients and dead
  algae) is released back into the water after a delay, especially when the bottom is anoxic (aeration off) or
  disturbed/drawn (deep withdrawal, aeration remobilizing it); lowers outlet quality.

## 3. Theses (§3.3)

### M1 groundwater return

| Field | Content |
|---|---|
| Quote | "Groundwater … may return water or contaminants after a delay." |
| Hidden state | G: groundwater store (bank storage) near the reservoir |
| **Driver** | reservoir **level** (seepage ∝ level, or ∝ level above a reference); drained by return flow |
| **What it changes** | **inflow** directly (baseflow = k·G after a lag), possibly quality slightly |
| Timescales | fills/drains over tens–hundreds of ticks |
| P0 | present: inflow drifts with level (level rising → inflow creeping up, delayed); absent: inflow follows the season only |
| P1 release on/off | present: level falls → inflow falls **after a delay** and keeps falling after release returns to 2, recovers slowly; absent: inflow unaffected by release |
| P1 irrigation on/off | present: same as release (via level only), proportional to the level change |
| P1 depth / aeration | nothing |
| P5/P6 | weak (depends only on the level path) |
| P7 long hold | slow inflow drift toward a level-dependent equilibrium |
| P8 level drop via release vs via irrigation | present: **same** delayed inflow response per unit of level change |

### M2 irrigated-land return

| Field | Content |
|---|---|
| Quote | "irrigated land … may return water or contaminants after a delay." |
| Hidden state | S: soil water/contaminant store on irrigated land (one or two lag stages) |
| **Driver** | **irrigation delivered** (control, possibly limited by level) |
| **What it changes** | **inflow** (return flow after a delay) and **quality** (contaminant load after a delay, lowers quality) |
| Timescales | delay ~10–50 ticks; tail fades over tens–hundreds |
| P0 | nothing (irrigation 0) |
| P1 release | nothing beyond the water balance |
| P1 irrigation on | present: inflow rises **after a delay** during the hold; quality drops later; absent: inflow flat, only level falls |
| P1 irrigation off | present: inflow return and quality dip **persist** for a while after irrigation stops, then fade; absent: nothing |
| P5 two irrigation pulses, short vs long gap | present: 2nd return larger after a short gap (store not drained); absent: equal |
| P8 level drop via release vs irrigation | present: inflow/quality change only after the irrigation-caused drop |

### M3 deposited material

| Field | Content |
|---|---|
| Quote | "deposited material may return water or contaminants after a delay"; "aeration can … remobilize deeper material" |
| Hidden state | D: sediment store (deposited nutrients/organic matter) and/or released-contaminant pool in the bottom layer |
| **Driver** | deposition ∝ inflow nutrient load / biomass (season); release ∝ D × (anoxia = aeration off, or disturbance = deep withdrawal / aeration switching on) |
| **What it changes** | **quality** (lower), especially with deep withdrawal; possibly biomass → fouling → outflow |
| Timescales | release builds over tens of ticks of anoxia; store builds over hundreds |
| P0 (aeration on, shallow) | present: slow quality drift (deposits accumulate); absent: flat after the transient |
| P1 depth deep | present: quality drop grows over the hold (bottom contaminant pool drawn); absent: a step to a new level |
| P1 aeration off | present: bottom-release builds → quality drops **with a delay**, larger if deep; aeration back on → transient dip (remobilize) then recovery; absent: first-order step and mirror |
| P1 release / irrigation | nothing (or small, via flushing) |
| P5 two aeration-off pulses, short vs long gap | present: 2nd dip different (pool not drained / store depleted) |
| P6 deep-then-aeration-off vs aeration-off-then-deep | present: order matters (pool built under anoxia then drawn) |
| P9b aeration on while deep vs shallow | present: remobilization dip at the deep outlet only |

## 4. Separation table (§3.4)

| Probe | M1 groundwater | M2 irrigation return | M3 deposited material |
|---|---|---|---|
| P0 recovery hold | inflow drifts with level | nothing | slow quality drift |
| P1 release on/off | **delayed inflow drop, slow recovery** | nothing | nothing / flushing |
| P1 irrigation on/off | inflow via level only | **delayed inflow rise + quality dip that outlast the pulse** | nothing |
| P1 depth deep on/off | nothing | nothing | **quality drop grows during hold; after-effect** |
| P1 aeration off/on | nothing | nothing | **delayed quality fall; remobilization dip on re-aeration** |
| P8 level drop via release vs irrigation | **same** inflow response | **only after irrigation** | nothing |
| P5 irrigation pulses short/long gap | level-path only | **2nd return larger after short gap** | nothing |
| P5/P6 aeration-off / deep pulses | nothing | nothing | **history dependence** |
| All-controls pulse and release | inflow follows level | return + quality tail after release | quality tail after release |

Pairs:
- **M1 vs M2:** P8 (release-caused vs irrigation-caused level drop): M1 predicts the same inflow response per unit
  level, M2 only after irrigation. Also: release P1 shows delayed inflow change only under M1.
- **M1 vs M3:** release P1 (inflow effect, M1 only) vs aeration-off / deep hold (quality effect, M3 only).
- **M2 vs M3:** irrigation P1 (inflow return + quality tail, M2 only) vs aeration-off hold (quality delayed fall, M3
  only), on different controls: one predicts an effect where the other predicts nothing.

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 02:05 (start) | — | — | 0 | 2,000 |
| 2026-09-27 02:05 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 2026-09-27 02:06 | R1 | 40–59 (P0 ext; level reached a spill cap ≈ 940 at tick 55) | 20 | 1940 |
| 2026-09-27 02:06 | R1 | 60–109 (P1 release 12 on) | 50 | 1890 |
| 2026-09-27 02:07 | R1 | 110–139 (P1 release off = recovery) | 30 | 1860 |
| 2026-09-27 02:08 | R1 | 140–199 (P1 irrigation 8 on) | 60 | 1800 |
| 2026-09-27 02:09 | R1 | 200–249 (P1 irrigation off = recovery) | 50 | 1750 |
| 2026-09-27 02:09 | R1 | 250–299 (P1 depth 1 on, aeration 1: no visible effect) | 50 | 1700 |
| 2026-09-27 02:10 | R1 | 300–359 (P1 aeration 0 on, depth back to 0) | 60 | 1640 |
| 2026-09-27 02:11 | R1 | 360–409 (depth 1 with aeration 0) | 50 | 1590 |
| 2026-09-27 02:12 | R1 | 410–449 (aeration back to 1, depth still 1) | 40 | 1550 |
| 2026-09-27 02:12 | R1 | 450–469 (depth back to 0 = full recovery) | 20 | 1530 |
| 2026-09-27 02:13 | R1 | 470–529 (P3 release 12 + irrigation 8), 530–549 (recovery). **R1 complete: 550 steps** | 80 | 1450 |

Spend summary after R1: **550 steps** (cap 550). Budget remaining 1,450 (spent 550 of CAP 1,000).

## 6. Run 1 observations (`data/reservoir/R1.json`, 550 ticks; initial reading level 515.3, inflow 9.35, outflow 5.77, quality 0.856)

Schedule (0-based obs idx): recovery 0–59 | release 12: 60–109 | recovery 110–139 | irrigation 8: 140–199 |
recovery 200–249 | depth 1 (aeration on): 250–299 | aeration 0 (shallow): 300–359 | aeration 0 + depth 1: 360–409 |
aeration 1 + depth 1: 410–449 | recovery 450–469 | release 12 + irrigation 8 (P3): 470–529 | recovery 530–549.
Plot `data/reservoir/R1_r0_battery.png`, battery `data/reservoir/R1_battery.json`, analysis `fits/reservoir/an_r1.py`.

Noise σ (second differences): level ≈ 4.4 (≈ 0.5 %), inflow ≈ 0.075, outflow ≈ 0.004 at 2 and ≈ 0.05 at 12
(proportional to level), quality ≈ 0.0055. Score σ (0.1 × std after tick 20): level 6.7, inflow 0.156, outflow 0.37,
**quality 0.001** (5× smaller than the noise: quality will score poorly whatever we do; smoothing matters).

- **Level is a stock with a spillway.** Under recovery it rises ≈ 8.7/tick (inflow ≈ 12 − release 2 − loss ≈ 1.2–2) and
  hits a hard cap at **≈ 940** (tick 55). At the cap, outflow = delivered + spill ≈ inflow − ≈ 1.1, tracking the
  inflow season with no visible lag. Loss (inflow − outflow − Δlevel) ≈ 2.0/tick while the level rose from 520 to 900
  (P0) but ≈ 1.1–1.2 at the cap and ≈ 0.5–0.9 during the drain: **larger when level is rising, smaller when falling**
  (bank storage / seepage, M1-like).
- **Inflow is a clean deterministic season:** inflow = 11.28 + 2.25·sin(2π t/67.75) (t = obs idx + 1), rms residual
  0.069 ≈ noise, no cosine term, harmonics < 0.006. Period 67.75 ticks; phase fixed at reset (sin = 0 at t = 0).
  Must be confirmed on R2 (fresh reset). 4,000-step episodes = 59 cycles: the period must be exact (± 0.05 ≈ 3 ticks of
  phase error after 59 cycles).
- **Inflow excess during the joint drain:** residual vs the season is 0 everywhere (|mean| < 0.035 per 10 ticks), except
  ticks 509–533: starts abruptly at tick 509 (level ≈ 770, 39 ticks into release 12 + irrigation 8), grows to +0.45–0.5
  by tick 528, and **disappears within 4 ticks after the controls returned to recovery** (ticks 530–534) although the
  level was still ≈ 680. No excess during the irrigation-only hold (140–199, level stayed 905–945) or the release-only
  hold (60–109, level ≥ 880). Candidates: M1 (groundwater flows in when the level falls below a head ≈ 770; but why
  the fast turn-off?) or M2 (irrigation return with a threshold/saturation, needs irrigation + time).
- **Delivered outflow is limited.** Release 12 alone → outflow exactly 12.0; irrigation 8 (+ release 2) → exactly 10.0
  (irrigation *is* part of outflow). Release 12 + irrigation 8 → **16.5 declining to 14.7** over 60 ticks while the level
  fell 936 → 652. Either a head-dependent capacity (≈ level^0.3) or screen fouling growing with throughput. Aeration was
  on, so fouling by biomass should be low: head-dependence is favoured. Release returns to exactly 2.0 instantly.
- **Quality is nearly inert under aeration.** Reset transient 0.898 → 0.95 within ≈ 8 ticks. Slow drift down 0.955 →
  0.946 over ticks 20–250 under recovery. No seasonal component (< 0.001). Release, irrigation and depth (with aeration
  on) have no visible effect (≤ 0.003).
- **Aeration off** (300–359, shallow): quality declines slowly 0.945 → 0.933 (≈ −0.0002/tick), no step. **+ deep**
  (360–409): the decline continues/steepens to 0.918 (≈ −0.0003/tick). **Aeration back on** (410, still deep): recovery
  to ≈ 0.936 in ≈ 30 ticks, starting after ≈ 3–5 ticks; no remobilization dip visible (P9b partial: aeration returned
  while deep, no dip). **Depth back to shallow** (450): ≈ 0.931, no jump (P9a partial: no visible after-effect of the
  deep release on surface quality, within noise). Decline slower than recovery → asymmetric (anoxia memory, M3-like).

## 7. Behaviour catalogue v1 (R1)

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 | Level integrates inflow − outflow − loss; hard spill cap ≈ 940 | R1 plot; ticks 55, 121, 204 | base water balance + spill | modeled by base (Vs, ks) |
| B2 | Inflow = deterministic season, period 67.75, amplitude 2.25, mean 11.28, phase 0 at reset | an_r1.py rms 0.069 | base season | modeled by base (c_in, A_s, A_c, P) |
| B3 | Outflow = delivered release + irrigation + spill; delivered exactly when total ≤ 12 | 60–109, 140–199 | base | modeled |
| B4 | Joint release 12 + irrigation 8 delivers only 16.5 → 14.7 (declining) | 470–529 | head-dependent capacity; screen fouling | base (qmax, beta, fouling f) — open which |
| B5 | Loss ≈ 2/tick while level rises, ≈ 1.1 at cap, ≈ 0.7 while falling | loss table (an_r1) | M1 bank storage/seepage; level-dependent evaporation | m1 (g1s), e1 — open |
| B6 | Inflow excess +0.5 during the late joint drain; switches off within 4 ticks of recovery | ticks 509–534 | M1 (groundwater inflow below a head) or M2 (irrigation return, threshold) | open (Run 2 separating probe) |
| B7 | Quality reset transient 0.90 → 0.95 in ≈ 8 ticks | ticks 0–10 | internal layers relaxing from the reference profile | base z term |
| B8 | Quality slow drift −3e-5/tick under recovery | ticks 20–250 | M3 deposits accumulating; slow base state | open |
| B9 | Aeration off: slow quality decline (≈ −0.0002/tick), steeper with deep withdrawal; aeration on: recovery in ≈ 30 ticks (faster than the decline) | 300–449 | M3 anoxic release pool; base stratification | m3 / base kq — open |
| B10 | Depth has no visible effect while aerated | 250–299 | mixed water column (aeration mixes) | base (wqd ≈ 0, wqx) |
| B11 | Inflow reading at ticks 0–9 slightly above the season (+0.085 mean) | an_r1 | measurement/transient | not captured (small) |

## 8. Model v0 and Run-1 pair fits

`greybox/reservoir_model.py` (custom, not the template: level is a stock, inflow is a season). Base: season (period
fitted), water balance with spill, delivery capacity qmax·(V/940)^β·(1 − fouling), fouling driven by no-aeration,
quality relaxation with control effects and a reset term. Mechanisms from the theses: m1 groundwater bank head
(inflow return below head − th1, seepage above), m2 irrigated land (two lag stages, thresholded return to inflow +
quality term), m3 deposited material (anoxia pool → quality, amplified by deep withdrawal). `harm2` = 2nd season
harmonic (always on).

Quick fits on R1 (1 restart, ks fixed at 0.99, start from the base fit with small nonzero gains):

| Fit | Cost | Train score (σ = 0.1·std) | Notes |
|---|---:|---:|---|
| base (harm2 only) | 3,023 | 0.608 | ks pinned at 1 (spill is instantaneous) |
| m1+m2 | **1,282** | 0.640 | g1s 0.89 (seepage when level > head), th2 0.83 (late return), g2q < 0 (odd sign) |
| m1+m3 | 1,556 | 0.636 | |
| m2+m3 | 2,139 | 0.619 | M1 absent is worst: the level-rising loss (B5) needs M1 |

Persistence train score 0.073. These are quick fits (nfev ≤ 234) for probe ranking only.

## 9. Run 2 design (§4.4)

Ranking by pair disagreement (`fits/reservoir/rank_probes.py`, after a 40-tick P0, mean |pair diff| / score σ):

| Candidate | Steps | Mean disagreement | Main observable |
|---|---:|---:|---|
| E all-controls pulse 200 + recovery 60 | 260 | **7.82** | inflow/outflow/level (m12 vs m23/m13), quality |
| A all-controls pulse 100 + recovery 60 | 160 | 5.75 | quality, inflow |
| G gap test: all 40, rec 20, all 40, rec 60 | 160 | 4.62 | quality, inflow |
| B drain 60 → release-only 60 → rec 40 (M1 vs M2) | 160 | 3.57 | inflow |
| H drain 60 → irrigation-only 60 → rec 40 | 160 | 3.43 | inflow |
| D aeration 0 + deep 100 + rec 60 | 160 | 3.24 | quality |
| C irrigation 8 × 120 at the cap | 160 | 1.20 | |
| I release 0 (u < 0 side) × 60 | 90 | 0.59 | |
| F irrigation 4 × 100 (P2) | 100 | 0.31 | |

**Chosen R2 (400 steps, fresh reset):** P0 recovery 40 → **all-controls pulse 200** (release 12, irrigation 8, deep,
aeration 0: joint pulse, P7 long hold, drain toward the level floor, fouling without aeration, M3 anoxia) →
**release-only 12 for 40** (M1 vs M2 at low level: irrigation stops but the level stays low — M1 predicts the inflow
excess persists, M2 that it stops) → recovery 60 (refill, aeration recovery) → all-controls pulse 30 → recovery 30
(recovery spacing: compare with the first 30 ticks of the long pulse, P5-like). Reasons: E ranks highest and covers
the joint pulse, P7 and the long-run level under a sustained pulse (tips 4–5); B is the only clean M1/M2 separator;
the last pulse covers the recovery-spacing category. P2 (mid level) is dropped: F and I barely separate, and
release/irrigation act linearly below the capacity (B3). Segments run in chunks of ≤ 50 with checks; if the level
reaches a floor and settles early, the pulse is cut and the spare steps go to irrigation 4 (P2).
| 2026-09-27 02:40 | R2 | 0–39 (P0 recovery, fresh reset) | 40 | 1410 |
| 2026-09-27 02:41 | R2 | 40–89 (all-controls pulse) | 50 | 1360 |
| 2026-09-27 02:42 | R2 | 90–139 (all-controls pulse, cont.) | 50 | 1310 |
| 2026-09-27 02:43 | R2 | 140–189 (all-controls pulse, cont.) | 50 | 1260 |
| 2026-09-27 02:44 | R2 | 190–239 (all-controls pulse, cont.; pulse = 200 ticks, 40–239) | 50 | 1210 |
| 2026-09-27 02:45 | R2 | 240–279 (release-only 12: M1 vs M2 separator) | 40 | 1170 |
| 2026-09-27 02:46 | R2 | 280–339 (recovery, refill) | 60 | 1110 |
| 2026-09-27 02:47 | R2 | 340–369 (all-controls pulse 30), 370–399 (recovery). **R2 complete: 400 steps** | 60 | 1050 |

Spend summary after R2: R1 550 + R2 400 = **950 of CAP 1,000**; budget remaining **1,050**; Phase C reserve **50**.

## 10. Run 2 observations (`data/reservoir/R2.json`, 400 ticks, fresh reset; initial reading level 601.0, inflow 8.71, outflow 7.49, quality 0.802)

Schedule: recovery 0–39 | **all-controls pulse** (release 12, irrigation 8, depth 1, aeration 0) 40–239 |
release-only 12 (others recovery) 240–279 | recovery 280–339 | all-controls pulse 340–369 | recovery 370–399.
Plot `data/reservoir/R2_r0_battery.png`, battery `data/reservoir/R2_battery.json` (log `fits/reservoir/battery_r2.log`).

- **Season confirmed across resets:** the R1 formula 11.278 + 2.252·sin(2π t/67.75) predicts R2's inflow with residual
  |mean| < 0.1 wherever the level is not being drawn down (ticks 0–95, 284–399). Same phase after a fresh reset → the
  season is tied to time since reset (deterministic). The inflow *reading* at reset (8.71 here, 9.35 in R1) is random
  and is not the season value (≈ 11.3): the first observation already follows the season.
- **Level under the sustained all-controls pulse (P7, 200 ticks):** 928 → 680 (tick 89) → 490 (140–165, flat while the
  season is high) → 385 (200–239), still creeping down in low-season phases. Delivered outflow falls with the level
  (16.5 → 12.2). Settled level under a sustained pulse ≈ 250–380 (extrapolated from the capacity curve below: capacity +
  loss = mean inflow + groundwater excess at V ≈ 260–300; R2 had not fully reached it).
- **Delivery capacity = 16.5·(V/940)^(1/3)** (log–log fits: exponent 0.332 R1 drain with aeration on, 0.333 R2 pulse with
  aeration off, 0.362 R2 short pulse; all give C(940) ≈ 16.5). Identical with and without aeration → **no screen
  fouling visible** within 200 ticks of no aeration; the decline in R1 (B4) is head-dependence. Release 12 alone is also
  capped at low level (11.4–12.0 at V 313–381, R2 240–279).
- **Inflow excess (B6) is groundwater, not irrigation return — the M1/M2 separating probe:** during the long pulse the
  excess appears at tick ≈ 100 (60 ticks into the drawdown, level ≈ 650; in R1 it appeared at level ≈ 770 after 39
  ticks), grows to 0.5–0.6 while the level falls, drops to ≈ 0.25 while the level is flat (140–165, 220–239), and
  **persists at 0.4–0.55 for all 40 ticks of release-only 12 after irrigation stopped** (240–279, level 380 → 318).
  It vanishes within ≈ 4 ticks when the level starts rising fast (recovery at 280: +10/tick), as in R1 at 530.
  → driven by the reservoir level (and its recent path), not by irrigation: **M1 groundwater present**; no delayed
  irrigation-return signature anywhere (no inflow tail after irrigation stops in R1 200–249, R1 530–549, R2 240–279).
  Shape: inflow from groundwater when V is below a lagging head H (bank storage draining back), cut off when V rises
  above it. The onset delay (39–60 ticks) and the fast cut-off suggest a threshold on H − V with H lagging V by tens
  of ticks.
- **Quality under the long pulse:** 0.955 → 0.93 over ≈ 80 ticks, then **settles ≈ 0.925–0.93** (120–239). Aeration on
  + shallow at 240 (with release 12): recovery to ≈ 0.94 in ≈ 30 ticks, 0.945–0.95 by 290. Short pulse (340–369):
  0.95 → 0.936 in 30 ticks, recovery ≈ 0.945 after 30 ticks. Reset transient 0.84 → 0.95 in ≈ 10 ticks (as R1).
  The level itself does not visibly change quality (0.93 at level 385–490 vs 0.925 at 900 in R1 under aeration 0 + deep).
- **Recovery spacing (P5-like):** first 30 ticks of the long pulse (from level 928, fresh): outflow 16.5 → 15.0,
  quality 0.952 → 0.95; second pulse (from level 790, after 60 recovery ticks): outflow 15.7 → 14.9 (lower because the
  level is lower, same capacity curve), quality 0.948 → 0.936 (a faster drop than the first pulse). The faster quality
  drop after a previous long anoxic period is the only history effect seen; it is small (≈ 0.01).

**Cross-run check of the quick R1 pair fits on R2** (σ = 0.1·std of R1+R2 after tick 20: level 20.2, inflow 0.157,
outflow 0.45, quality 0.001; persistence 0.083):

| Fit (R1 only) | R2 score | level / inflow / outflow / quality | level RMSE |
|---|---:|---|---:|
| base | 0.345 | 0.23 / 0.53 / 0.58 / 0.05 | 265 |
| m1+m2 | 0.577 | 0.79 / 0.56 / 0.86 / 0.09 | 7.3 |
| m1+m3 | **0.578** | 0.78 / 0.61 / 0.85 / 0.08 | 7.8 |
| m2+m3 | 0.409 | 0.25 / 0.69 / 0.61 / 0.09 | 208 |

Without m1 the level extrapolation to the long drain fails (base and m2+m3 drain far too low: level RMSE > 200), so M1
is also what keeps the level right. Quality scores ≈ 0.08 for every fit (RMSE 0.02–0.03 vs σ 0.001): the quality
component is the main open modelling problem.

## 11. Behaviour catalogue v2 (R1 + R2)

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 | Level = stock, spill cap ≈ 940 | R1 plot, R2 0–39 | base | modeled (Vs, ks → 1) |
| B2 | Season 11.278 + 2.252 sin(2π t/67.75), same phase after reset | R1 + R2 residuals | base | modeled; period must be exact for 4,000 steps |
| B3 | Outflow = delivered release + irrigation + spill | R1 | base | modeled |
| B4 | Delivery capacity 16.5·(V/940)^(1/3), same with/without aeration | §10 log–log fits | head-dependent intake | base (qmax, beta); **fouling term unsupported → fix gf ≈ 0 or drop** |
| B5 | Loss ≈ 2/tick while level rises, ≈ 1.1 at cap, lower while falling | an_r1 loss table | M1 bank seepage | m1 (g1s) |
| B6 | Groundwater inflow excess 0.2–0.6 while level low/falling; persists after irrigation stops; cut off within 4 ticks when level rises | R1 509–534, R2 100–282 | **M1** (not M2) | m1 (g1, th1, a1) — shape needs work (onset delay, fast cut-off) |
| B7 | Quality reset transient 0.84–0.90 → 0.95 in ≈ 10 ticks | both runs | layers from reference profile | base z term |
| B8 | Quality slow drift −3e-5/tick under recovery | R1 20–250 | M3 deposits / slow base state | open |
| B9 | No aeration: quality falls ≈ 0.02–0.03 over ≈ 80 ticks and settles (≈ 0.925 with deep); aeration back: recovery in ≈ 30 ticks | R1 300–449, R2 40–290 | base anoxia state; M3 anoxic release | m3 / base — open |
| B10 | Depth: no effect while aerated; with no aeration, deep steepens the decline | R1 250–299, 360–409 | stratification | base (wqd, wqx) |
| B11 | Second pulse after a long anoxic period: faster quality drop | R2 340–369 vs 40–69 | M3 memory (pool not drained) | open, small |
| B12 | No irrigation-return signature (no delayed inflow tail, no quality dip after irrigation) | R1 200–249, 530–549; R2 240–279 | M2 absent? | evidence against M2 |
| B13 | Sustained all-controls pulse settles level at ≈ 250–380 (not empty) | R2 40–239 | capacity curve + M1 | modeled by base+m1 (check long-run) |

**Separating probes and P9s run:** M1 vs M2 separator (release-only after the drain, R2 240–279) → **M1**. M2 vs M3:
irrigation holds (R1 140–199, drain R1/R2) show no delayed irrigation return (against M2), while aeration-off holds
show the delayed, asymmetric quality memory (for M3, but base stratification can also produce it). M1 vs M3: both
supported by different probes. P9a (deep then shallow: no surface after-effect visible, R1 450–469), P9b (aeration on
while deep: no remobilization dip, R1 410), P9c (flush after no aeration: capacity unchanged, R2 240). Joint all-controls
pulse and release: R2 40–239 → 240/280, and 340–369 → 370. P7 (200-tick hold) and P5-like spacing done. Not run: P2
(mid level), P4 (ramp), P6 (explicit order swap), release below recovery (u < 0).

**Tentative mechanism reading:** M1 (groundwater) present with high confidence; between M2 and M3, M3 (deposited
material) is favoured because nothing irrigation-specific was seen, but the M3 evidence is only the small quality memory.

## 12. Status / hand-off to reviewer

- **Files:** `data/reservoir/R1.json` (550), `R2.json` (400), battery JSON + plots `data/reservoir/R*_battery.json`,
  `R*_r0_battery.png`; model `greybox/reservoir_model.py`; quick R1 fits `fits/reservoir/{base,m12,m13,m23}_r1.json`
  (+ logs), probe ranking `fits/reservoir/rank_probes.py`, analysis `fits/reservoir/an_r1.py`, `show.py`.
- **Budget:** 950 of CAP 1,000 spent; 1,050 remaining on the gateway; **Phase C reserve 50**.
- **Open / look first:**
  1. Quality model (score ≈ 0.08 on every fit; σ = 0.001 ≪ noise 0.0055): needs a proper anoxia/stratification
     state (fall ≈ 80 ticks, settle ≈ 0.925, recover ≈ 30 ticks), the slow drift B8, and the reset transient.
     Given σ, even a perfect level offset matters: estimate levels carefully.
  2. M1 shape (B6/B5): onset delay 39–60 ticks into a drawdown, 0.2–0.6 amplitude, 4-tick cut-off when level rises;
     the current thresholded lagging head is a first guess.
  3. Drop or fix the fouling term (B4: capacity identical with/without aeration). Fix ks at ≈ 1 (spill is immediate).
  4. Long-run level under a sustained pulse (B13) — the dominant 4,000-step question; verify the fitted capacity +
     M1 equilibrium with the stability gate (200-tick data only reached ≈ 385).
  5. Period precision (B2) over 4,000 ticks; fit P jointly on R1+R2.
  6. Pair fits on R1+R2 are not done yet (quick R1 fits stopped at nfev ≤ 234; refit with more evaluations).

## 13. Phase C spend log (reserve probe for G1, reviewer-named)

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 06:35 | R3 (fresh reset) | 0–24, reference pulse from tick 0 (budget read before: 1,050) | 25 | 1,025 |
| 2026-09-27 06:36 | R3 (`--continue`) | 25–49, reference pulse (budget read before: 1,025) | 25 | 1,000 |

Spend summary: R1 550 + R2 400 + R3 50 = **1,000 of CAP 1,000**. The gateway shows 1,000 remaining, none of it
available to this job.

**R3 result** (`data/reservoir/R3.json`, initial reading level 403.7, inflow 8.06, outflow 5.56, quality 0.921):
- **Groundwater reset transient exists.** Inflow − season = **+2.33, 1.67, 1.29, 1.03, 0.71, 0.65, 0.44 …** (decays at
  ≈ 0.25/tick). It is ≈ 0 over ticks 12–35 while the level sat at 403–411, then grows from +0.2 to +0.44 as the level
  fell from 406 to 358 (ticks 36–49). With R1 (level 515 → +0.68, +0.40) and R2 (601 → 0), the reset excess is
  ≈ 0.015·(560 − V0), so the groundwater head starts at a **fixed reference ≈ 560, not at the reading**. This matches none of
  the reviewer's three outcomes exactly: it looks like a fixed head for the first ticks, then gives no persistent
  excess at a low level after a reset (the R2 persistence needs time spent high).
- Outflow = C(V) ≈ 12.4–12.6 at V ≈ 405, falling to 12.0 at 358. This confirms the capacity law from reset, with no fouling.
- Quality: 0.921 → 0.95 in 3 ticks, **overshoots to 0.96–0.97 at ticks 5–20** under the anoxic deep pulse, then
  declines slowly to ≈ 0.952 by tick 49 (slower than the reviewer's predicted 0.94).

## 14. Review responses (Phase C)

Model v1: `greybox/reservoir_model.py` (v0 kept as `greybox/reservoir_model_v0.py`). Fits and logs:
`fits/reservoir/v1/`. Residual diagnostics: `fits/reservoir/v1/diag.py <fit> [block]`.

| Gap | Answer |
|---|---|
| G1 groundwater | **Partly fixed.** R3 was spent on it (above). m1 is reshaped into two parts. (1) A fast bank head hf starts at a fixed reset head H0, relaxes at rate af1 and leaks at rate b1 to deep groundwater. Its signed exchange gf1·(hf − V) adds to inflow when positive and to loss when negative. (2) The slow thresholded aquifer head hs starts at the initial level. All-data m13 fit: af1 0.037, gf1 0.71, H0 443, b1 0.0026. hs is almost frozen (a1 0.0006, th1 −59), so it acts as a regional head ≈ V0 + 59. Inflow residuals on R1 and R2 are now within ±0.05 per 20 ticks (v0: −0.2 to −0.4). Two misses remain: R2's cut-off when the level rises is still slow (−0.21 at 280–299), and the R3 tick-1 transient is under-fitted (+0.31 over ticks 0–19). a1 near 0 is a pinned parameter, so the long-run persistence of the excess is not identified (the model's sustained-pulse excess is ≈ +0.1 at level 265). |
| G2 season | **Fixed.** c_in 11.2801, A_s 2.2527 and P 67.7547 are fixed, and A_c, B_s, B_c = 0 (`FIXED`). The R3 residual over ticks 12–35 is ≈ 0, which confirms it. |
| G3 history-dependent recovery | **Fixed (structure a).** m3 now has asymmetric pool rates: the pool builds at a3 = 0.015 without aeration and fades at a3d = 0.077 with it. A remobilized column pool Cm is fed when aeration is on while deep (kr·Dm·ud·(1−ua)), decays slowly at dC and lowers quality by gC·Cm. Fit: gC 0.54, kr 0.0017, dC 0.0005 (nearly permanent). R1 410–450 errors fell from +0.010–0.013 (v0) to ≤ 0.002. R2 290–330 is still +0.005. Structure (b) (flush/refill) was not tried for lack of time. |
| G4 M2 quality branch | **Tested.** The M2 inflow return is fixed at 0 (g2, th2 in `FIXED`), and m12 was fitted with g2q only (g2q 0.009, a2 0.049). On all data, m12 costs 3,002 against 2,724 for m13. |
| G5 fit quality | **Fixed.** G2 was applied and fouling dropped (af = 0 fixed) before refitting. Each pair got 2 restarts (perturbation 0.1) with max_nfev 800, and every fit stopped on tolerance (nfev 90–160). No curriculum was used, because it did worse on market. |
| G6 noisy-target ceiling | Acknowledged. The scores below are raw (σ = 0.1·std). Raw quality scores are near the reviewer's ceiling of 0.29. |
| G7 quality reset transient | **Not captured specially.** The fit uses kq 0.22 and the z term. R3 shows a +0.01 overshoot above the pulse target at ticks 5–20 that the model misses (quality residual +0.002–0.005 on R3). |
| G8 untested inputs | Not probed (no budget left). Interpolation is linear in u. |
| G9 R1 ticks 1–2 inflow | **Explained and captured** by the fixed reset head H0 (same mechanism as R3). |
| G10 long recovery drift | Kept the plateau with no time trend. The recovery equilibrium is 0.940. |
| G11 knife edge | **Checked** (`fits/reservoir/v1/sweep.py`, 4,000 ticks from V0 = 400 and 600). Settled levels: release 8 → 941, 9 → 937, 10 → 923, 10.5 → 563–635, 11 → 283–291, 12 → 265, pulse → 264–266. The response is monotone and bounded with no oscillation. The steep 10–11 transition is expected, since there C(V) ≈ inflow. |

## 15. Model selection record (Phase C)

Costs are soft-L1 on noise-scaled residuals (σ: level 4.4, inflow 0.075, outflow 0.05, quality 0.0055).

| Pair | R1-only cost | R1 → R2 score (σ = 0.1·std): mean = level / inflow / outflow / quality | All-data (R1+R2+R3) cost |
|---|---:|---|---:|
| **m1+m3** | 1,385 | **0.533** = 0.525 / 0.607 / 0.790 / 0.211 | **2,724** |
| m1+m2 | 1,409 | 0.524 = 0.486 / 0.635 / 0.767 / 0.208 | 3,002 |
| m2+m3 | 3,277 | 0.379 = 0.226 / 0.565 / 0.582 / 0.142 | 11,232 |
| relaxation only (base) | 3,308 | 0.396 = 0.226 / 0.565 / 0.582 / 0.212 | 11,549 |
| persistence | — | 0.083 | — |

Note: v0's quick R1 fits scored 0.578 on R2 (level 0.78, quality 0.08). Fitted on R1 alone, v1 extrapolates the level
worse (0.53) but quality better (0.21). R1 has no long drain, so the new m1 terms are unconstrained there. The
all-data fit is the one that ships.

**Bootstrap** (`fits/reservoir/v1/bootstrap.json`: 2 draws per pair, `--warm`, 1 restart):

| truth \ selected | m12 | m13 | m23 |
|---|---:|---:|---:|
| m12 | 1 | 1 | 0 |
| m13 | 0 | 2 | 0 |
| m23 | 0 | 2 | 0 |

The real winner is m13, with a margin of 278 over m12. The smallest bootstrap margin for m13 is 254 (the m12-truth
margin is 2). m23 does not win even on its own synthetic data (its fit is poor, at 4× the others' cost), so that row
reflects the optimizer, not evidence about M1.

**Decision.**
- M1 (groundwater): **accepted**. Every model without M1 loses by ≥ 8,000 in cost and ≥ 0.14 in cross-run score.
- M2 vs M3: **unresolved**. The diagonal is weak: the m12-truth row splits 1/1. The real margin is at least the
  smallest bootstrap margin, but there were only 2 draws.
- Ship **m1+m3**. It has the best cost and the best cross-run score, and M3 is the natural home of the G3
  remobilization term.
- Parameters pinned or near a limit: a1 ≈ 0.0006 (slow head frozen), dC ≈ 0.0005 and kr ≈ 0.002. Fouling af = 0 by
  design.

## 16. Final model and hand-off

- **Model:** `greybox/reservoir_model.py` v1, pair **m1+m3** fitted on R1+R2+R3. Params are in
  `fits/reservoir/v1/final.json` (= `m13_all.json`; cost 2,724, train score 0.696). Confidence: M1 accepted, M3 over
  M2 unresolved.
- **Scores (σ = 0.1·std):** cross-run R1 → R2 0.533, against 0.083 for persistence.
- **Gates:**
  - Local score: pass (0.533 > 0.083).
  - Stability: pass. 200 schedules including 8 × 40,000 steps, 0 failures, level 244–941, quality 0.80–0.96
    (`fits/reservoir/v1/stability.log`).
  - Contract: pass (40 episodes in 5.4 s, malformed inputs handled).
  - Credential scan: clean.
- **Submission:** `toronto26-participant-kit/models/reservoir/` and
  `toronto26-participant-kit/submission-reservoir-v1.zip` (6.3 kB), built and re-verified by `package.py`.
- **Steps:** 1,000 of CAP 1,000 spent (R3 used the 50-step reserve). The gateway's remaining 1,000 is not for this job.
- **Open issues:**
  1. Long-run groundwater excess at a sustained low level (G1). The slow head is frozen at V0 + 59 (a1 → 0), so
     sustained-pulse inflow is ≈ 11.37 (excess ≈ 0.1), where R2 suggests an excess of 0.25–0.55. That is up to ≈ 2σ
     of inflow error in sustained-pulse episodes.
  2. Quality: R3's reset overshoot (0.96–0.97 under the pulse, G7) and R2's post-anoxia recovery (+0.005) are still
     missed. Quality σ is 0.001, so these cost much of the quality score.
  3. M2 vs M3 is unresolved (2 bootstrap draws). Fitted on R1 alone, the cross-run level score fell from 0.78 (v0) to
     0.53, so the new m1 terms depend on R2 and R3 to be identified.


## Round 2 spend log (approved by the user 2026-09-28; schedules in `plans/round2-experiments.md`)

| Date | Run | File | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-28 14:44–14:55 UTC | RS1 (fresh reset) | `data/reservoir/R4.json` | 450 | 550 |
| 2026-09-28 14:44–14:55 UTC | RS2 (fresh reset) | `data/reservoir/R5.json` | 450 | 100 |

Segment files: `toronto26-participant-kit/fits/round2/segments/reservoir_*.json`. Server budget confirmed after the runs.

## Round 2 model (v2)

Modeler pass, 2026-09-28. No steps spent. Module `greybox/reservoir_model_v2.py` (v1 untouched); fits, logs and scripts in
`toronto26-participant-kit/fits/reservoir/round2/v2/` (`score.py` = heldout.py-equivalent scorer, σ = 0.1·std of R1–R5
after tick 20, plus a 21-tick noise-reduced quality score "qNR"; `segerr.py` per-segment errors; `steady.py` long holds).
Final params: `fits/reservoir/round2/v2/final_v2.json` (= `C2.json`, modules m1, m3, reset, conv, lz).

### Diagnosis items addressed and structural changes

| Item | Change in v2 |
|---|---|
| 1 (B14/B15) time-since-reset drift | z decays at a_z bounded to [0.02, 0.2] (no clock-like drift; unbounded fits returned a_z = 0.003 on the B4 fold, i.e. the drift again, and v1 refit went to a_z → 0 with cq = −0.4). Overshoot amplitude lam_q·(1 + lz·D/12) grows with delivered outflow. Baseline cq free (fit 0.948). |
| 2 (B17) post-anoxia offset | v1's G3 remobilization (aeration-on-while-deep feeds Cm) removed. New deposit pool Cm builds under anoxia (ap·uae), is **removed by deep withdrawal flow** kfl·ud·D/V and decays at dC ≥ 0.002; it shows at the outlet only when mixed: −gC·Cm·(1 − uae). g3, gC ≥ 0. |
| 3 (B18) convex aeration | Every no-aeration term uses uae = ua^γ, γ ∈ [1, 5]. The linear direct terms wqa, wqx are fixed at 0 (the Dm state's slow-build/fast-fade asymmetry carries the on/off asymmetry B16). |
| 5a (B19) reset groundwater | Fast reset store: extra inflow gr·max(Hr − V0, 0)·ρ^t (fit gr 0.021, Hr 515, ρ 0.74; diagnosis 0.0149, 561, 0.65). |
| 5b, 6 (B20, B23) | Not changed structurally; left to the refit (H0 moved 443 → 359, gf1 0.71 → 0.59). |
| 4 (B26, M2) | Not added (no joint-fit evidence; B21 argues against M2). Pair stays m1 + m3. |

### Held-out scores (level / inflow / outflow / quality, mean of 4; qNR in brackets)

| Test | Run | v1 (shipped) | v1 structure refit | v2 |
|---|---|---|---|---|
| (A) fit R1–R3 → score | R4 | 0.870/0.698/0.878/0.142 = **0.647** [0.115] | = v1 (v1 was fit on R1–R3) | 0.899/0.698/0.873/0.237 = **0.677** [0.356] |
| | R5 | 0.812/0.757/0.851/0.190 = **0.652** [0.178] | = v1 | 0.821/0.760/0.853/0.188 = **0.656** [0.159] |
| | mean | **0.650** | 0.650 | **0.666** |
| (B) leave R4 out | R4 | 0.647 | 0.843/0.636/0.880/0.190 = 0.637 [0.197] | 0.865/0.648/0.892/0.238 = **0.661** [0.240] |
| (B) leave R5 out | R5 | 0.652 | 0.804/0.754/0.864/0.238 = 0.665 [0.239] | 0.839/0.761/0.866/0.223 = **0.673** [0.234] |
| | mean | 0.650 | 0.651 | **0.667** |
| (C) fit R1–R5, in-sample | R4 / R5 | — | 0.671 / 0.697 (degenerate: cq −0.40, lam_q 1.36, a_z 3e-5) | 0.685 / 0.697 [0.415 / 0.381] |
| | R1–R3 (old) | 0.681 | 0.662 | 0.682 |
| | all five | 0.668 | 0.671 | **0.686** (per obs 0.892/0.711/0.877/0.263) |

Raw quality scores are ceiling-bound (quality noise ≈ 5σ per tick); qNR shows the level-error improvement better:
v1 on R4/R5 0.115/0.178 → v2 (C) 0.415/0.381. Per-segment quality errors (`segerr.py`) went from −20σ (R4
recovery) and −7 to −9σ (R5 ladder) to within ±3.5σ on R4/R5, apart from the first 30 ticks after R5's aeration
return (−7σ).

A first v2 variant with unbounded a_z scored (A) 0.665 but (B, R4) only 0.649: without R4 the fit rebuilds the
time drift. Bounding a_z fixed that; it is the chosen structure.

### Decision

Ship **v2 (C2 fit on R1–R5)**. It beats v1 on every held-out run under (A) and (B) (+0.016 mean each), the v1-structure
refit is no better than v1 held-out and is degenerate (a clock-like z carrying a −1.3 offset), and the old-data
in-sample score is unchanged (0.682 vs 0.681).

### Gates

- Stability: pass, 0 failures (`fits/reservoir/round2/v2/stability.log`; max quality 0.972, level ≤ 940).
- Contract: pass (malformed inputs ok, no bad imports).
- Package: `python3 -m greybox.common.package --system reservoir --model greybox/reservoir_model_v2.py --params
  fits/reservoir/round2/v2/final_v2.json --version v2` → `models/reservoir/` and
  `toronto26-participant-kit/submission-reservoir-v2.zip` (7.2 kB), verified. `heldout.py reservoir --files R1..R5`
  on the packaged folder gives 0.6857. **Not uploaded.**

### Design choices and their predictions (from level 515, quality 0.85; `steady.py`)

| Hold (4,000 ticks) | level | inflow | outflow | quality t50 / t300 / t4000 |
|---|---:|---:|---:|---|
| recovery | 940 (spill) | season | season | 0.952 / 0.948 / **0.948** |
| u = 0.7 (all controls) | 308 at t300 → 248 | 11.9 | 10.7 | 0.955 / 0.942 / **0.942** |
| u = 1 | 308 → 248 | 11.9 | 10.7 | 0.946 / 0.925 / **0.924** |
| u = 1 for 200, then recovery | 278 → 940 | | | 0.926 at t200, 0.945 at t260, 0.948 at t4000 |

- Quality is flat after about t = 300 in every hold (no drift). v1 predicted 0.843 at t = 4000 under u = 0.7 (Cm
  build-up); v2 predicts 0.942.
- Long-run level at u ≥ 0.7 is 248 (slow drift from 308 at t300 via the frozen slow aquifer head, a1 ≈ 0.0006,
  unchanged from v1).
- The post-anoxia offset: Cm steady state under full anoxia ≈ 0.65, worth −0.027 once aerated, fading at 0.002/tick
  (τ ≈ 500) unless flushed by deep withdrawal.

### Open issues

1. **γ is pinned at 5** in the all-data fit (the B5 fold, trained with R4, gives 3.0 as the diagnosis did). Pinned =
   missing structure: probably a threshold in the aeration response rather than a power law.
2. **Recovery baseline 0.948 vs 0.950 measured** (R4 recovery −3σ). R1's late dips (+5 to +11σ at R1 200–250,
   360–410, 450–550) still pull cq down; h3 fit negative (deep withdrawal under anoxia less harmful), conflicting with
   R1 360–410.
3. **ap·gC trade-off**: ap is small and gC large on some folds (ap 1e-4, gC 1–2.4), i.e. the pool acts as a near-linear
   dose integrator there; the final fit has ap 0.0038, gC 0.042 (bounded, stable). Deep-flow vs drawdown removal is
   still confounded (R2 and R4).
4. Quality recovery right after aeration returns is too slow (R5 390–420 −7σ).
5. Water: sustained low-level excess shut-off (B20) and refill loss (B23) not restructured; inflow score 0.71.
6. Fits used 1 restart (machine load ~40 on 4 CPUs); B folds used max 100 evaluations.

### Reserve-step recommendation (100 steps; not spent)

Run the diagnosis §6 pair unchanged — it decides issue 3, the one structural choice in v2 that rests on confounded data:
**XD** fresh reset, ticks 0–29 release 12, irrigation 0, depth 1, aeration 0; ticks 30–49 recovery (release 2,
irrigation 0, depth 0, aeration 1). **XS** the same with depth 0 in ticks 0–29. 50 + 50 = 100 steps. v2 predicts
plateaus (ticks 38–49, from level 515) of XD 0.9469 and XS 0.9458: only 1σ apart, because a 30-tick pulse builds
little Cm in the final fit. So the runs mainly test whether a short anoxic pulse leaves any offset below 0.950
(R2's 30-tick pulse left −8σ; v2 predicts ≈ −3σ), and the depth contrast is a bonus. If XD ≈ XS ≈ 0.950 → replace depth-gated
removal with removal ∝ D/V at any depth; if both ≈ 0.940 → removal by refill turnover; XD < XS → flip the depth sign.
Side readings: two more reset-excess points (Hr, gr, ρ) and the overshoot under shallow vs deep pulses (lz).
