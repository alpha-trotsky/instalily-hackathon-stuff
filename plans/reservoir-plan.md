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
