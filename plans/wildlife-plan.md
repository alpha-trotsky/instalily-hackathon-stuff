# Wildlife plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 00:50 (overnight job, `plans/overnight-framework.md`). CAP = 1,000 steps
(Run 1 ≤ 550, Run 2 ≤ 400, reserve ≥ 50). Budget at start: 2,000 remaining (free read).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Observe prey and predator totals in northern and southern landscapes. Hunting requests prey
harvest; habitat protection changes shelter and resource renewal, especially in the north. Corridor access
controls new interregional journeys; already travelling animals can still arrive. Within each region, open
pasture, mixed cover and sheltered browse differ in feeding, hunting exposure and predation. Food renewal shares a
finite resource, young animals compete for nursery food, and arrivals compete for settlement space. Compare
habitat recovery with corridors closed and open, and harvest before versus after protection. Regional totals
alone do not identify patch occupancy, juvenile condition or animals in transit."

**Observables** and initial-reading ranges (docs):

| Observable | Initial range | Notes |
|---|---|---|
| prey_north | 70 – 100 | positive population; multiplicative dynamics → log units likely |
| predator_north | 8 – 15 | positive; predator–prey coupling → possible oscillation |
| prey_south | 70 – 100 | same ranges as north; north/south differ through habitat ("especially in the north") |
| predator_south | 8 – 15 | |

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u | Notes |
|---|---|---:|---:|---|---|
| hunting_quota | [0, 8] | 0 | 7 | value / 7 | recovery at a bound; **u can reach 8/7 = 1.14** (beyond pulse) |
| habitat_protection | [0, 1] | **1** | 0.1 | (1 − value) / 0.9 | recovery at the upper bound; u = 1 is protection 0.1, **u can reach 1.11** (protection 0) |
| corridor_access | [0, 1] | 0 | 1 | value | recovery = corridors closed |

Both recovery values are at bounds, so there is no untested side of recovery. Two controls can exceed the pulse
(hunting 8, protection 0); scoring's recovery scenarios use u ∈ [0.7, 1], so the over-pulse range matters only
for sustained/joint episodes with random actions.

**Delay / commitment phrases → pipeline stages:**
- "Corridor access controls new interregional journeys; already travelling animals can still arrive" → a transit
  compartment between regions: closing the corridor stops departures immediately, but arrivals continue for the
  travel time. Expect a lagged, smoothed exchange and a tail after closing.
- "arrivals compete for settlement space" → arrivals settle at a rate that falls with the receiving region's
  density (saturating immigration).
- "young animals compete for nursery food" → a juvenile stage: births → juveniles → adults with density-dependent
  survival; recruitment lags births.
- "Hunting requests prey harvest" → the *realized* harvest can be less than the quota (limited by exposure in
  open pasture, by availability). Quota 7 against prey ~85 is a large fraction per tick unless realized harvest is
  much smaller.
- Reset: "All unobserved quantities begin from fixed reference conditions, identical on every reset", "including
  any deterministic dependence on the initial observable state" → transit empty (probably), patch split fixed,
  juveniles fixed rule. The reset transient is deterministic given `initial`.

**Anything tied to time since reset:** no seasonality phrase. The reset transient (hidden patch/juvenile/resource
state relaxing from its reference) is the only time-since-reset effect expected.

**Cross couplings expected:** prey ↔ predator within each region (predation; predator growth from prey eaten);
north ↔ south through the corridor (only when corridor_access > 0); shared finite food resource within a region
limits prey growth (carrying capacity).

**Organizer-suggested comparisons (P9), quoted word for word:**
- P9a: "Compare habitat recovery with corridors closed and open" — habitat pulse (protection 0.1) followed by
  recovery (protection 1), once with corridor 0 and once with corridor 1 during the recovery.
- P9b: "harvest before versus after protection" — an order swap: hunting pulse then protection restored/applied,
  versus protection first then hunting. Operationally: [hunt at low protection → restore protection] vs
  [low protection → restore → hunt at full protection]; the cleanest is the P6 order swap of the hunting pulse and
  the habitat pulse (H→P vs P→H).

## 2. The three mechanisms (§3.2)

The brief does not label "mechanisms". The strongest reading pairs the three hidden quantities named in the last
sentence ("Regional totals alone do not identify patch occupancy, juvenile condition or animals in transit")
with the three competition/structure sentences. **Confidence: medium.** Alternative triple: {finite food
renewal, nursery competition, settlement competition}. The chosen modules below absorb that alternative (food
renewal is folded into base prey growth + M2; settlement competition into M3).

- **M1 patch occupancy** — "open pasture, mixed cover and sheltered browse differ in feeding, hunting exposure and
  predation". Prey redistribute among patches (towards shelter under hunting/predation pressure, towards open
  pasture for food), slowly. Occupancy is a hidden fading state.
- **M2 juvenile condition** — "young animals compete for nursery food". Recruitment depends on a juvenile stage
  whose condition reflects past food per capita; a delayed, density-dependent birth pulse.
- **M3 animals in transit / settlement** — "Corridor access controls new interregional journeys; already
  travelling animals can still arrive … arrivals compete for settlement space". A transit pipeline with
  density-limited settlement.

## 3. Theses (§3.3)

### M1 patch occupancy

| Field | Content |
|---|---|
| Quote | "open pasture, mixed cover and sheltered browse differ in feeding, hunting exposure and predation"; "habitat protection changes shelter" |
| Hidden state | P: fraction of prey in exposed (open) patches vs sheltered |
| **Driver** | hunting pressure (control) and habitat protection (control: shelter availability); possibly predator level |
| **What it changes** | the *size* of the hunting/predation effect (exposure gain on harvest and predation), and feeding (prey growth) |
| Timescales | shift over ~10–50 ticks; fades back similarly |
| P1 hunting on/off | present: prey drop fast at first, then the drop slows (animals hide → lower exposure), partial recovery during the hold; after hunting stops, a small overshoot (sheltered animals feed less → slower regrowth, or return to open pasture). Absent: monotone relaxation |
| P1 habitat on (protection 0.1) | present: exposure rises → hunting and predation effects are larger after a habitat pulse; absent: habitat only changes growth |
| P5 gap test | present: second hunting pulse after a short gap is *weaker* (still hiding); absent: equal |
| P6/P9b order | present: hunting after protection loss removes more than hunting before; absent: order matters only through levels |
| P7 long hold | present: adaptation continues (drift back up under sustained hunting) |
| P9a corridor | no specific effect |

### M2 juvenile condition (nursery competition)

| Field | Content |
|---|---|
| Quote | "young animals compete for nursery food"; "juvenile condition"; "Food renewal shares a finite resource" |
| Hidden state | J: juvenile cohort / condition, built from births and depleted by maturation, density-dependent survival |
| **Driver** | prey level (births ∝ adults; survival falls with density / low food) — an output level, lagged |
| **What it changes** | prey growth with a lag: recruitment responds to the density of ~τ ticks ago → **overshoot/undershoot and ringing** after steps; habitat protection raises resource renewal → better condition |
| Timescales | lag 5–30 ticks; condition memory 10–50 ticks |
| P1 hunting on/off | present: after hunting stops, prey regrowth is delayed, then overshoots the old baseline (juveniles recruited from low-density good condition); absent: plain monotone regrowth |
| P1 habitat | present: habitat effect on prey growth delayed (condition improves slowly) and persists after the pulse ends |
| P5 gap test | present: recovery from the second pulse depends on the gap (a juvenile deficit carries over) |
| P7 long hold | present: damped oscillation, slow drift |
| P9a corridor | none |

### M3 animals in transit / settlement competition

| Field | Content |
|---|---|
| Quote | "already travelling animals can still arrive"; "arrivals compete for settlement space" |
| Hidden state | T_ns, T_sn: animals in transit in each direction |
| **Driver** | corridor control × regional imbalance (departures); arrivals after a delay; settlement ∝ free space |
| **What it changes** | outputs directly: north/south totals exchange with a lag; after closing, a tail of arrivals continues |
| Timescales | transit 3–20 ticks |
| P1 corridor on/off | present: totals converge between regions only after a lag; after closing, the receiving region keeps gaining for the transit time (and totals dip while animals are in transit — the sum of regions falls then recovers). Absent: instantaneous exchange, stops immediately, no dip in the sum |
| P9a habitat recovery with corridor closed vs open | present: with the corridor open, the north (habitat-sensitive) refills partly from the south with a lag and settlement saturation; closed: only local regrowth |
| P5/P6 | corridor open while one region is depleted (after hunting) → strong flow; arrivals saturate when the receiving region is crowded |
| P1 hunting | none unless corridor open |

## 4. Separation table (§3.4)

| Probe | M1 patch occupancy | M2 juvenile condition | M3 transit/settlement |
|---|---|---|---|
| P1 hunting on (hold) | fast drop then slowing/partial rebound during hold (hiding) | delayed drop in recruitment → continuing slow slide | none (corridor closed) |
| P1 hunting off | small or no overshoot; return speed set by exposure | **delayed regrowth then overshoot above baseline** | none |
| P1 habitat (protection 0.1) on/off | changes exposure → predation/hunting sizes; fast | slow persistent change of growth; outlasts the pulse | none |
| P1 corridor on/off | none | none | **lagged exchange, tail after closing, dip in the regional sum** |
| P5 two hunting pulses, short vs long gap | 2nd pulse weaker after a short gap | 2nd pulse recovery different (juvenile deficit) | none |
| P6/P9b hunting ↔ habitat order | hunting at low protection removes more (exposure) | order matters via growth memory only | none |
| P9a habitat recovery, corridor closed vs open | none | none | **open: cross-regional refill with lag and saturation** |
| P3 hunting + corridor | none specific | none specific | depleted region draws in immigrants |

Pairs:
- **M1 vs M2 (separates world M1M3 from M2M3):** hunting off-step (M2 overshoot vs none) and short-vs-long-gap
  double hunting pulse (M1 weaker 2nd pulse); hunting after a habitat pulse (M1 exposure).
- **M1 vs M3 (M1M2 vs M2M3):** corridor P1 (M3 lagged exchange + tail, M1 nothing); hunting hold (M1 hiding
  rebound, M3 nothing with corridor closed).
- **M2 vs M3 (M1M2 vs M1M3):** corridor P1/P9a (M3) and the hunting off-step overshoot (M2).

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 00:50 (start) | — | — | 0 | 2,000 |
| 2026-09-27 00:51 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 2026-09-27 00:51 | R1 | 40–59 (P0 recovery) | 20 | 1940 |
| 2026-09-27 00:51 | R1 | 60–79 (P0 recovery) | 20 | 1920 |
| 2026-09-27 00:51 | R1 | 80–99 (P0 recovery) | 20 | 1900 |
| 2026-09-27 00:52 | R1 | 100–119 (P0 recovery) | 20 | 1880 |
| 2026-09-27 00:52 | R1 | 120–159 (P1 hunting 7 on) | 40 | 1840 |
| 2026-09-27 00:52 | R1 | 160–184 (P1 hunting on, ext) | 25 | 1815 |
| 2026-09-27 00:52 | R1 | 185–224 (P1 hunting off) | 40 | 1775 |
| 2026-09-27 00:52 | R1 | 225–249 (P1 hunting off, ext) | 25 | 1750 |
| 2026-09-27 00:52 | R1 | 250–289 (P1 habitat on: protection 0.1) | 40 | 1710 |
| 2026-09-27 00:52 | R1 | 290–329 (P1 habitat off: protection 1) | 40 | 1670 |
| 2026-09-27 00:53 | R1 | 330–369 (P1 corridor on) | 40 | 1630 |
| 2026-09-27 00:53 | R1 | 370–409 (P1 corridor off) | 40 | 1590 |
| 2026-09-27 00:53 | R1 | 410–439 (P1 corridor off, ext) | 30 | 1560 |
| 2026-09-27 00:53 | R1 | 440–489 (P2 hunting 3.5) | 50 | 1510 |
| 2026-09-27 00:53 | R1 | 490–539 (recovery) | 50 | 1460 |
| 2026-09-27 01:04 | R2 | 0–29 (P0 recovery, fresh reset) | 30 | 1430 |
| 2026-09-27 01:04 | R2 | 30–54 (order A: habitat 0.1) | 25 | 1405 |
| 2026-09-27 01:04 | R2 | 55–79 (order A: hunting 7 at protection 1) | 25 | 1380 |
| 2026-09-27 01:04 | R2 | 80–104 (recovery) | 25 | 1355 |
| 2026-09-27 01:04 | R2 | 105–129 (order B: hunting 7) | 25 | 1330 |
| 2026-09-27 01:04 | R2 | 130–154 (order B: habitat 0.1) | 25 | 1305 |
| 2026-09-27 01:04 | R2 | 155–179 (P9a: habitat recovery with corridor OPEN) | 25 | 1280 |
| 2026-09-27 01:04 | R2 | 180–199 (P3: hunting 7 + habitat 0.1) | 20 | 1260 |
| 2026-09-27 01:05 | R2 | 200–249 (P7 hunting 7, part 1) | 50 | 1210 |
| 2026-09-27 01:05 | R2 | 250–299 (P7 hunting 7, part 2) | 50 | 1160 |
| 2026-09-27 01:05 | R2 | 300–349 (P7 hunting 7, part 3) | 50 | 1110 |
| 2026-09-27 01:05 | R2 | 350–399 (P7 hunting 7, part 4) | 50 | 1060 |
| 2026-09-27 01:20 | R2c (copy of R2, continued; R2.json unchanged) | 400–434 (G3 joint pulse: hunting 6, protection 0.25, corridor 0.9) | 35 | 1025 |
| 2026-09-27 01:20 | R2c | 435–459 (release to recovery) | 25 | 1000 |

Spend summary: R1 = 540 steps (cap 550), R2 = 400 (cap 400), total 940. **Phase C (modeler): +60 reserve steps on R2c (free budget check before: 1,060; after: 1,000). CAP of 1,000 now fully used.** Budget remaining 1,060; **60 steps of the
1,000 CAP are left as the Phase-C reserve.** (Timestamps are the machine clock; the Git Bash clock reads EST.)

## 6. Run 1 observations (`data/wildlife/R1.json`, 540 ticks, initial N 94.7/13.8, S 74.1/11.5)

Schedule: recovery 0–119 | hunting 7 120–184 | recovery 185–249 | habitat (protection 0.1) 250–289 | recovery
290–329 | corridor 1 330–369 | recovery 370–439 | hunting 3.5 440–489 | recovery 490–539. Plots:
`data/wildlife/R1_r0_battery.png`; battery text `data/wildlife/R1_battery.txt`.

- **Reset transient = prey boom and bust.** Prey grow at a near-constant **+5–6 per tick** (additive, not
  exponential) from 95 → 197 (N, tick 21) and 74 → 158 (S), then growth stalls and prey fall back to the recovery
  level (N 120.9, S 96.9; settled by ~55–65). The turn-downs are abrupt (N: −2/tick at 22–28, then −5/tick at
  29–34; S: plateau ~150 at 22–34, then −5/tick at 35–39). Predators fall monotonically 13.8 → 2.5 (N) and
  11.5 → 2.5 (S), fast at first (5%/tick), then slowly (0.5%/tick at 100); not fully settled at 120 (> 120).
- **Hunting 7 (P1)**: realized harvest ≈ 6.5–7 per tick **in each region** at first (the quota applies per
  region), shrinking as prey fall. N 121 → 29 (still drifting at 65 ticks), S 97 → 11.6 (settled ~47). Predators
  fall slightly (2.48 → 2.06), with a 5–8-tick delay.
- **Hunting off**: additive regrowth (+4–6/tick) and a **large overshoot**: N 29 → 172 (tick 224), S 12 → 156
  (tick 218), then an abrupt fall back to ~124/100 by 249 (overshoot 0.40 / 0.51 of the step).
- **Hunting 3.5 (P2)**: N 126 → 86.5, S 97 → 62 (settled ~35 ticks). The full quota gives −76%/−88%: **strongly
  nonlinear** in u. **Off: monotone return, no overshoot** (the overshoot needs deep depletion).
- **Habitat pulse (protection 0.1)**: N 123 → 67 (−45%), S 100 → 64.5 (−35%): stronger in the north, as the
  brief says. Settles in ~28 ticks. Predators unchanged (+0.03). **Off: monotone return, no overshoot**, ~29 ticks.
- **Corridor open**: **all four totals fall**: prey N −10 (−8%), S −20 (−21%), predators −28% in both, with
  k ≈ 0.1–0.3 (settles ~25 ticks). Animals in transit are not counted. **Closing**: arrivals continue (prey
  +1.5–3.5/tick at once) and **overshoot** above the old baseline (N 137 vs 120, S 108 vs 97, predators 2.6 vs
  2.3), returning over ~70 ticks.
- **Noise σ**: 0.44–0.48% of level for every observable, proportional → log units for all four.
- **Predators N and S move together** (level corr 0.995, diff corr 0.95) although the prey differ.
- Symmetry: habitat on/off k ratio ≈ 1 in both units (symmetric). Hunting on/off differs in both units (depletion
  is nonlinear), corridor on/off differs (transit refill + overshoot).

## 7. Behaviour catalogue v1 (after Run 1)

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 | Reset boom-and-bust: prey +5–6/tick to ~197/158 at tick ~21, abrupt fall to 121/97 by ~55 | R1 0–60, `R1_r0_battery.png` | finite food stock that starts full (fixed reference) and is eaten down; M2 recruitment limits | partly modeled (food F, F0; peak too low/early in fits) |
| B2 | Prey regrowth is additive (~+5/tick), independent of prey level (29 or 12) | R1 185–205 diffs | nursery-limited recruitment (M2 "young compete for nursery food"); food-renewal-limited births | modeled by m2 `iRm` (nursery cap), the main gain in the R1 fits |
| B3 | Overshoot after deep depletion (hunting 7 off) but none after mild depletion (hunting 3.5) or a habitat pulse | R1 185–249 vs 290, 490 | food stock accumulates while prey are scarce and renewal is full (habitat pulse → low renewal → no stock) | partly modeled (overshoot too small: peak 135 vs 172) |
| B4 | Abrupt turn-downs / plateaus in the booms (step-like changes of growth rate) | R1 ticks 12, 22, 29, 35, 207, 225 | Holling-II intake with a small half-saturation (food runs out abruptly); patch structure (three patches exhausting at different times, M1) | partly modeled (kF → ~0.02 in the joint fit) |
| B5 | Hunting harvest ≈ quota per region at high prey, shrinking at low prey; strongly nonlinear in u | R1 120–184, 440–489 | harvest = 7 u X/(X + Xh), Xh ≈ 35–50 | modeled (base) |
| B6 | Habitat pulse lowers prey (N −45%, S −35%), symmetric on/off, no overshoot, predators unaffected | R1 250–329 | habitat scales food renewal per region (hF_N > hF_S) | modeled (base) |
| B7 | Corridor open lowers all four totals (prey −8%/−21%, predators −28%); closing gives lagged arrivals and an overshoot | R1 330–439 | transit pipeline (animals in transit not counted, aT ≈ 0.045); food accumulates while fewer animals graze | modeled (base transit); overshoot size only partly |
| B8 | Predators decay slowly from the reset reading to ~2.5 and barely respond to prey | R1 0–120, whole run | density-dependent predator mortality (dY2) with weak prey coupling (small Xp) | modeled (base; eY pinned at 1, dY pinned at 0) |
| B9 | Predators N ≈ S at all times | battery correlations | same predator parameters in both regions; weak prey coupling | modeled (shared predator params) |
| B10 | Noise 0.45% of level, proportional | battery | measurement noise | log units |

## 8. Model module and Run-1 pair fits

Module: `toronto26-participant-kit/greybox/wildlife_model.py`: a two-region food → prey → predator
consumer-resource model with Holling-II intake, per-region habitat effects on food renewal and on exposure,
per-region harvest `7 u X/(X + Xh)`, and a transit pipeline (4 stocks: prey/predators leaving N/S). The transit
pipeline is **in the base**, because the brief states it as fact ("already travelling animals can still
arrive") and R1 shows it clearly (B7). Mechanism modules, written from the theses before fitting:
- **m1 patch occupancy**: sheltering memory P → uq (hunting pressure) at rate a_m1; it scales exposure to harvest
  and predation by (1 − g1 P) and feeding by (1 − g1f P).
- **m2 juvenile / nursery**: births pass through a 3-stage juvenile pipeline (rate a_m2) with nursery-limited
  entry `B/(1 + iRm B)`; reset J = j0 X0 per stage. Off: a_m2 = 1, iRm = 0.
- **m3 settlement competition**: arrivals settle with probability 1/(1 + cS X_dest/100); the rest are lost.
  (Deviation from the pre-registration: the transit lag itself moved to the base; M3 is settlement only.)

Why not the relaxation template: B1/B3 (boom-and-bust overshoot after deep depletion, absent after mild
depletion) and B7 (a dip in the regional *sum* when the corridor opens) need hidden stocks, not first-order
relaxation.

Development: the first version (linear food intake, a single juvenile stage with density-dependent survival) gave
base 14,455, m12 13,377, m13 14,124, m23 13,730, with a_m2 pinned at 1. The Holling-II intake and the nursery cap
(B2) replaced it. Fits (R1 ticks 0–539, log units, residual scale 0.01, soft_l1, 3 restarts; init =
`init_r1.json` = base2 params *without* module params, so module gains start at their nonzero SPEC defaults):

| Fit | Cost | Train score (σ = 0.1 std) | R2 score of the R1 fit | Notes |
|---|---:|---:|---:|---|
| base2 (`base2_r1`) | 14,417 | 0.555 | 0.351 | eY → 1, dY → 0 pinned; kF 0.32 |
| **m1+m2** (`m12_r1`) | **12,456** | 0.574 | 0.293 | a_m1 → 0 and g1 → 0.99 (pinned: a static exposure cut, not a memory); iRm 0.053 (nursery cap ≈ 19/tick); a_m2 → 1 (no juvenile delay); kF, F0 → 0 |
| m1+m3 (`m13_r1`) | 13,793 | 0.582 | **0.386** | a_m1 → 1 (instant), g1 0.09, g1f 0.20; cS → 0 |
| m2+m3 (`m23_r1`) | 12,561 | 0.569 | 0.296 | iRm 0.053; cS → 0 (m3 unused) |

Persistence on R2: 0.067. Reading: m2's nursery cap is the only module that clearly lowers the R1 cost
(about −1,900). m3 (settlement) is switched off by every fit. m1 is used only as a static or instantaneous effect
with pinned rates (lesson 9: missing structure, not evidence). The m2 fits generalise *worse* to R2 because they
predict a spurious regrowth wave during the 200-tick hunting hold (`data/wildlife/R2_crossrun_r1fits.png`).

## 9. Run 2 design (§4.4)

Screening (the three `fits/wildlife/m*_r1.json` pairs, from reset, initial 85/11.5/85/11.5, mean |pairwise
difference| / score-σ over ticks ≥ 40; σ = 0.1×std of R1):

| Candidate (from reset, rec 40 first) | Steps | m12/m13 | m12/m23 | m13/m23 | mean |
|---|---:|---:|---:|---:|---:|
| J: hunting 7 long 200, rec 60 (P7) | 300 | 8.41 | 0.49 | 8.60 | **5.83** |
| M: hunting 8 + protection 0 (over-pulse) 50, rec 80 | 170 | 7.24 | 0.43 | 6.91 | 4.86 |
| E: P3 hunting 7 + habitat 0.1, 50, rec 80 | 170 | 7.23 | 0.87 | 6.42 | 4.84 |
| H: hunting 7 + corridor 1, 60, rec 60 | 160 | 1.72 | 0.20 | 1.67 | 1.20 |
| F: P9b/P6 habitat 40 → hunting 40, rec 60 | 180 | 1.65 | 0.33 | 1.61 | 1.19 |
| A: P5 hunting 30, gap 20, hunting 30 | 200 | 0.98 | 0.20 | 0.93 | 0.70 |
| G: P9b/P6 hunting 40 → habitat 40, rec 60 | 180 | 0.90 | 0.25 | 0.90 | 0.69 |
| B: P5 hunting 30, gap 80, hunting 30 | 200 | 0.94 | 0.15 | 0.90 | 0.66 |
| C: P9a habitat 60 → rec (corridor closed) 60 | 160 | 0.84 | 0.24 | 0.88 | 0.65 |
| K: habitat + corridor 60 | 160 | 0.85 | 0.16 | 0.91 | 0.64 |
| I: long joint mid 3.5 / 0.55 / 0.5, 200 | 300 | 0.84 | 0.21 | 0.85 | 0.63 |
| D: P9a habitat 60 → rec (corridor open) 60 | 200 | 0.61 | 0.23 | 0.66 | 0.50 |
| L: corridor long 150 | 250 | 0.35 | 0.13 | 0.33 | 0.27 |

Full 400-step schedules: the **chosen** `rec 30 | habitat 25 → hunting 25 | rec 25 | hunting 25 → habitat 25 |
rec with corridor open 25 | hunting + habitat 20 | hunting 200` scores m12/m13 4.34, m12/m23 0.50, m13/m23 4.12.
Alternatives: `rec 40 | P3 60 | rec 60 | hunting 200 | rec 40` 7.64/0.79/7.33 (higher, but no P6/P9a/P9b); the
chosen schedule with a mid-level joint P7 (3.5/0.55/0.5) 1.25/0.27/1.28; P5 gaps 10/60 + P9a + hunting 200
3.08/0.29/3.12.

Reasons: the long hunting hold is the best separator (m2's nursery/juvenile dynamics predict a regrowth wave
under sustained hunting, m13 a slow slide), and it doubles as P7 (200) and as the check for effects that
re-emerge during long holds. The two back-to-back order blocks cover P6 and P9b ("harvest before versus after
protection": habitat pulse → harvest, versus harvest → habitat pulse). The corridor-open recovery after the
order-B habitat pulse is the open half of P9a; its closed half is R1 290–329 (habitat pulse, then recovery with
the corridor closed). P3 (top two controls at u = 1 together) is a 20-tick joint pulse leading into the long hold.
The m1/m3 pair (m12 vs m23) is poorly separated by every candidate (≤ 0.9 σ), because the R1 fits leave both
modules nearly inactive; no affordable probe fixes that. P5 (gap test) was dropped in favour of P6 for budget.

## 10. Run 2 observations and catalogue v2 (`data/wildlife/R2.json`, 400 ticks, initial N 72.7/8.5, S 98.1/10.6)

Plots: `data/wildlife/R2_r0_battery.png`; the R1 fits on R2 are `data/wildlife/R2_crossrun_r1fits.png`; the quick
joint fits are `data/wildlife/R2_allquick_fits.png` and `R1_allquick_fits.png`. Battery: `R2_battery.txt`.

- **The reset boom does not depend on the initial reading**: N starts at 72.7 (R1: 94.7) and still peaks at ~196
  (tick 24; R1: 197 at tick 21). S starts at 98.1 (R1: 74.1) and peaks at ~160 (tick 18; R1: 158). The boom is set
  by a fixed hidden stock (food), not by the starting prey. Predators start at 8.5/10.6 and join the same slow
  decay (3.7/4.2 at tick 29).
- **Order A (habitat 30–54 → hunting 55–79)**: the habitat pulse during the bust takes N 178 → 71 and S 145 → 67
  (towards the ~66 habitat level). Hunting after protection is restored, starting from 70/64: N → 38.6, S → 18.0
  in 25 ticks.
- **Order B (hunting 105–129 → habitat 130–154)**: hunting from the post-hunt boom (138/113): N → 52, S → 26 in 25
  ticks. The habitat pulse then makes prey **rise** to 66.5/64.5, the same habitat-pulse level as in R1 (67/64.5)
  and order A. The habitat level is an attractor from above and below.
- **P9a, habitat recovery with the corridor open (155–179)**: N 66 → 103, S 64 → 75.5 in 25 ticks, predators
  2.15 → 1.62 (−25%). With the corridor closed (R1 290–314): N 67 → 118, S 64.5 → 95. **The open corridor slows
  the recovery, much more in the south**, and costs predators ~25% (animals in transit).
- **P3 joint hunting + habitat (180–199)**: N 103 → 21, S 76 → 18 in 20 ticks; the first-tick drop in N is −12
  (harvest plus habitat). Predators **rise** 1.68 → 2.29 (transit arrivals after the corridor closed, plus
  exposure).
- **P7 hunting 7 for 200 (200–399), protection restored**: N regrows 21 → 38 (tick 219) *under hunting* (food
  renewal restored), then slides to 25.5 by ~300 and stays flat. S 18.7 → 21.6 → 11.4 (flat from ~260).
  Predators 2.3 → 1.9/1.86. **Nothing re-emerges during the second half of the hold** (the last 100 ticks are flat
  to within noise). Settled levels under hunting 7: N 25.5, S 11.4 (R1 after 65 ticks: 29 and still drifting, 11.6).

Cross-run test (R1 fits → R2, σ = 0.1×std of R1+R2): **m13 0.386**, base2 0.351, m23 0.296, m12 0.293;
persistence 0.067. All beat persistence; the m2 fits fail on the long hold (spurious regrowth wave, B13).

**Quick joint fits on R1+R2** (3 restarts, 400 nfev, `--init fits/wildlife/init_r1.json`; for orientation only,
`fits/wildlife/*_all_quick.json`):

| Pair | Cost | Train score | Notes |
|---|---:|---:|---|
| **m1+m2** | **28,822** | 0.585 | a_m1 → 1 (instant: P = uq), g1 0.19, **g1f 0.56** (hunting cuts births by 56%·u); iRm 0.041; a_m2 → 1; F0 → 0.99, kF 0.018 |
| m1+m3 | 34,530 | 0.555 | a_m1 → 1, g1 0.18, g1f 0.33; cS → 0 |
| m2+m3 | 36,622 | 0.532 | iRm 0.085; cS → 0 |

All three still miss the reset-boom peak (160–170 vs 196) and the N regrowth bump under hunting (R2 200–260).

Catalogue v2 (new or updated behaviours):

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 (upd.) | The reset boom's height and timing are the same for initial prey 72.7 and 94.7 | R1 vs R2 ticks 0–30 | fixed reference food stock F0 ≈ full; boom length set by food, not prey | partly modeled (peak 160–170 vs 196 in joint fits) |
| B11 | The habitat-pulse level (~66/64.5) is reached from above and from below, in either order | R1 250, R2 30, R2 130 | habitat sets food renewal → a renewal-limited prey level | modeled (base) |
| B12 | An open corridor slows habitat recovery, much more in the south; predators −25% | R2 155–179 vs R1 290–314 | transit loss per region (mvX_S > mvX_N) | modeled (base transit); m3 settlement not needed so far (cS → 0) |
| B13 | Under sustained hunting 7 the level is flat after ~100 ticks (N 25.5, S 11.4); N regrows 21 → 38 early in the hold after the joint pulse | R2 200–399 | food renewal restored after the habitat pulse; no slow hidden drift | **not captured**: the R1 m2 fits predict a spurious regrowth wave; the joint fits get the flat level but miss the bump |
| B14 | Joint hunting + habitat: predators rise | R2 180–199 | transit arrivals after closing + habitat exposure | partly (eH small) |
| B15 | Hunting reduces births ("disturbance"), or m1 exposure acts instantly | joint m12: g1f 0.56 with a_m1 → 1 | a direct hunting → feeding term; a fast patch shift | open (pinned a_m1: treat as missing structure) |

**Separating probes and P9s run:**
- Long hunting hold (the best-screened m2 separator): ✓ R2 200–399. Flat; no regrowth wave. This is evidence
  against the R1 m2 fits' juvenile/nursery dynamics as fitted, not necessarily against M2 itself.
- P6 order swap / P9b "harvest before versus after protection": ✓ R2 30–79 (habitat → hunting) and 105–154
  (hunting → habitat).
- P9a "habitat recovery with corridors closed and open": ✓ closed R1 290–329, open R2 155–179 (both after a
  habitat pulse; the preceding pulses were 40 vs 25 ticks and started from 123 vs 52 prey, so they match only
  roughly).
- P2 hunting 3.5 ✓ (R1 440). P3 ✓ (R2 180, only 20 ticks). P7 ✓ (R2 200, 200 ticks).
- **Not run:** P5 gap test (two equal hunting pulses, short vs long gap), the main M1 (patch/sheltering) thesis
  probe; a corridor probe with one region depleted (M3 settlement competition needs a crowded vs an empty
  destination); P2 for habitat/corridor (mid levels); over-pulse levels (hunting 8, protection 0).

## 11. Status / hand-off to reviewer

**Files**
- Data: `toronto26-participant-kit/data/wildlife/R1.json` (540 ticks), `R2.json` (400 ticks), with battery
  JSON/TXT/PNG for each, plus `R1_base.png`, `R1_pairfits.png`, `R2_crossrun_r1fits.png`, `R1_allquick_fits.png`
  and `R2_allquick_fits.png`.
- Model: `toronto26-participant-kit/greybox/wildlife_model.py`. Plot helper:
  `toronto26-participant-kit/greybox/wildlife_plotfit.py` (run from the kit:
  `python greybox/wildlife_plotfit.py out.png data.json fit1.json [fit2.json ...]`).
- Fits: `toronto26-participant-kit/fits/wildlife/`: `base_r1` (first model version, superseded), `base2_r1`,
  `init_r1` (start point: base2 without module params), `m12_r1`, `m13_r1`, `m23_r1` (the Run-1 pair fits), and
  `*_all_quick` (unconverged joint fits), plus logs. The `m*_r1.log` files of the superseded first version were
  overwritten.

**Budget:** 940 of the 1,000 CAP spent (R1 540, R2 400). 1,060 remain in the account; **60 are available to
Phase C**.

**Open items for the reviewer/modeler, most important first**
1. **The boom-and-bust shape (B1, B3, B4)** is the largest misfit: additive growth at ~+5/tick, an abrupt stall,
   then a fall. Candidates: nursery-capped recruitment (m2 iRm) plus a food stock with near-step intake
   (kF → 0.02). The joint m12 fit goes this way, but its peak is still 160–170 vs 196 and too early. Consider a
   food stock with its own capacity per region (not normalized to 1), starvation mortality when intake falls
   below need, or three patches (M1) exhausting in sequence (the stalls at R1 ticks 12, 22, 29, 207 and 225 look
   step-like).
2. **Pair identification is weak.** m3 (settlement) is switched off by every fit (cS → 0). m1 is used only with
   pinned rates (a_m1 → 0 or 1), that is, as a static or instantaneous hunting effect. m2 (nursery cap) is the
   only clearly useful module, but its R1 fit fails the cross-run test (B13). Nothing is decided.
3. **Parameters pinned at limits:** eY = 1 and dY = 0 (predator equations); a_m1 and a_m2 at 1; kF and F0 → 0 in
   m12_r1. The predator block is probably mis-structured (predators hardly depend on prey, and N ≈ S). Try
   predators relaxing to a level set by lagged prey with density dependence, or a shared predator pool.
4. **No P5 gap test and no M3 probe.** R2 ended settled under hunting 7 and may still be alive. A 60-step R2
   continuation that fits the reserve: `rec 20 | hunting 7 for 10 | rec 10 | hunting 7 for 10 | rec 10` (a short
   gap; compare with the R1/R2 single pulses) for M1, or `corridor 1 + hunting 7 for 30 | corridor 1 for 30`
   (one depleted region receiving arrivals: both regions are depleted under hunting, so this tests settlement
   only weakly) for M3. The P5 continuation is the better use.
5. The corridor removes a *larger* share of prey in the south (B7, B12). The model uses per-region departure
   rates (mvX_S ≈ 2–3 × mvX_N). A settlement-space explanation (M3) was expected, but the fits don't use it.

## 12. Reserve run R2c (Phase C, 60 steps, review G3)

`data/wildlife/R2c.json` is a copy of R2 (R2.json unchanged), continued at tick 400 with the reviewer's exact
schedule. The run had not expired. Free budget check before: 1,060; after: 1,000 (the CAP of 1,000 is fully used).

- **Joint pulse (400–434: hunting 6, protection 0.25, corridor 0.9)**, starting from the hunting-7 settled state
  (25.4 / 1.90 / 11.4 / 1.86): prey N fall 25.4 → 10.8 and settle by about tick 420. Prey S dip 11.4 → 8.9
  (tick 409) and then *rise* to 10.0 (arrivals from the north). Predators fall 1.90 → 1.62 (N) and
  1.86 → 1.49 → 1.55 (S). **No extinction and no cycle.**
- **Release (435–459, recovery action):** prey regrow at about 25% per tick at first (N +2.7, +3.1, +3.4, …), that
  is, in proportion to the adult stock. The increments then saturate at +6–7 per tick (N 10.8 → 139.7 and
  S 10.0 → 135.7 in 25 ticks, still rising). An exponential start followed by an additive cap means births are
  food-limited (mA) *and* nursery-capped (mB). Predators recover 1.64 → 2.03 over the 25 ticks.

## 13. Review responses (Phase C modeler, 2026-09-27)

Model v1 is `toronto26-participant-kit/greybox/wildlife_model.py`. The old model is kept as
`greybox/wildlife_model_v0.py`, and the fits in `fits/wildlife/*_r1.json` and `*_all_quick.json` refer to v0. The new
fits are in `fits/wildlife/v1/`.

| Gap | Response |
|---|---|
| G1 mechanism triple | **Fixed.** The modules are now mA food renewal (a finite renewing food stock; off = logistic births with a habitat-dependent K and no hidden stock), mB nursery (a 6-stage juvenile pipeline with nursery-capped entry and a fixed J0; off = instant recruitment) and mC settlement (arrivals settle ∝ 1/(1+cS X/100), predators ∝ 1/(1+cSY Y); unsettled arrivals wait in transit). Patch exposure, an instant hunting and habitat effect on exposure and births, is now base. All three pairs were refitted (§14). mB+mC reproduces the reset boom only roughly, although its R1 fit scores 0.406 cross-run. On all data it cannot match the long hunting hold or the habitat effects (cost 53.1k against 37.8k). |
| G2 predator block | **Fixed.** A linear two-state block: Y relaxes at kY ≈ 0.107 towards a reserve Z, and Z relaxes at kZ ≈ 0.027 towards Y* = yb·Xe/(Xe+Xp). The reset uses Z0 = Yref + zf (Y0 − Yref), which is affine in Y0. The dY2·Y² term is removed. Predator cross-run scores are 0.41 (N) and 0.45 (S) over all of R2c (mA+mB fitted on R1). v0 scored 0.10–0.24 on the reset segments alone. R3 slow tail: covered only through kZ (τ ≈ 37). No extra state was added, for lack of time. |
| G3 joint pulses / extinction | **Fixed, with new data.** The 60 reserve steps went on the reviewer's joint pulse (§12). The model now has a refuge Xr ≈ 6.8 (harvest and predation act on X − Xr) and a floor of 0.05 on kF. Harvest and predation use **exponential (monotone) removal**, which removed a period-2 sawtooth that the stability gate found. Constant-action grid (100 settings, including hunting 8 and protection 0, 4,000 steps each): the lowest tail prey level is 9.2, the lowest predator level 1.47, and the largest tail range/mean 0.000. So no setting drives prey extinct or cycles. v0 m12, refitted on the same data, drives prey to 0.01 in 37 of the 100 settings. |
| G4 release overshoot / cohort delay | **Tested, not captured.** a_m2 was allowed in [0.15, 1] with NJ = 6 (a delay of up to 40 ticks). Every fit pins a_m2 → 1 (a 6-tick delay), and the fixed J0 pins at its cap of 30. The ~18-tick stall is still missing. This is missing structure and is flagged. |
| G5 juvenile reset | **Fixed.** J0 is a fixed constant. F0 is fixed too (it fits to 1.0). |
| G6 settlement form | **Fixed (form) and tested.** The queue form is implemented in mC. In the mA+mC and mB+mC fits, cS → 0.00 and cSY ≈ 0.09–0.16, so prey settlement competition goes unused. The bootstrap still ranks the mC pairs last. |
| G7 slow component under hunting | **Partly fixed**, through the food stock and the predator reserve Z. The R2 250–400 rms log error is 0.057, against 0.74 for v0 m12 cross-run. The bump at R2 200–260 is still under-fitted: R2 120–250 has an rms of 0.16, the worst segment. |
| G8 unconverged fits / pinned parameters | The fits were warm-started through 2–3 stages (nfev 300–400). **Pinned in the final fit:** a_m2 = 1, J0 = 30 (cap), F0 = 1, kF → 0 (the 0.05 floor is active), g1 = 0 and eHY = 0. The G8 limit-cycle gate was added as `fits/wildlife/v1/const_check.py` and passes. |
| G9 P9a/P9b contrasts | Not reported separately, for lack of time. They are included in the R2c cross-run score. In the final fit, R2 30–120 has an rms of 0.066 and 120–250 an rms of 0.16. |
| G10 mid levels / over-pulse | Accepted. The joint probe adds hunting 6, protection 0.25 and corridor 0.9, and the constant-action gate covers hunting 8 and protection 0. |

## 14. Model selection (§6.3)

Costs use log units, a residual scale of 0.01 for every observable and soft_l1 (f_scale 2). The score σ is 0.1×std after
tick 20 of R1+R2c (4.53 / 0.057 / 4.10 / 0.055). Every fit is a warm-started chain with 1 restart per stage, because
of the 4-CPU limit.

**Cross-run (fit on R1, score on R2c including the joint pulse):**

| Pair | R1 cost | R2c score | Per observable (pN / yN / pS / yS) |
|---|---:|---:|---|
| **mA+mB** (`AB_r1b`, final removal form) | 7,647 | **0.417** | 0.400 / 0.415 / 0.401 / 0.451 |
| mA+mB (`AB_r1`, old removal form) | 7,608 | 0.392 | 0.391 / 0.401 / 0.371 / 0.406 |
| mB+mC (`BC_r1`) | 18,529 | 0.406 | 0.372 / 0.357 / 0.573 / 0.322 |
| mA+mC (`AC_r1`) | 18,303 | 0.302 | 0.435 / 0.215 / 0.334 / 0.224 |
| persistence | — | 0.066 | 0.160 / 0.010 / 0.088 / 0.007 |

For comparison, the best v0 fit (m13_r1) scored 0.386 on R2.

**All data (R1 + R2c):**

| Fit | Cost | Train score |
|---|---:|---:|
| **mA+mB** `AB_all3` (final; exponential removal) | **37,815** | 0.519 |
| mA+mB `AB_all2` (old removal form; the bootstrap candidate) | 43,282 | 0.520 |
| mA+mC `AC_all` | 51,870 | 0.496 |
| mB+mC `BC_all2` | 53,129 | 0.525 |
| No mechanism (logistic, no pipeline, no settlement) `base_all` | 54,303 | 0.517 |
| v0 m12 refitted on R1+R2c (`v0m12_all`, reference) | 38,788 | 0.558 (fails the extinction gate) |

**Bootstrap** (`fits/wildlife/v1/boot_warm.py` → `bootstrap.json`): 2 draws per truth, because the job was running
behind. Each refit was warm-started from that candidate's real-data fit, with 1 restart and at most 120 nfev. The
candidates were AB_all2, AC_all and BC_all2. Draw 1 ran after the change of removal form. Its truth simulation and its
refits both used the new form, so the draw is internally consistent.

| Truth \ selected | mA+mB | mA+mC | mB+mC |
|---|---:|---:|---:|
| mA+mB | 2 | 0 | 0 |
| mA+mC | 0 | 2 | 0 |
| mB+mC | 0 | 0 | 2 |

Winning margins: mA+mB 17.8k and 19.2k, mA+mC 18.3k and 31.3k, mB+mC 8.7k and 15.9k. The real winner is mA+mB with a
real margin of 8.6k, below the smallest mA+mB bootstrap margin of 17.8k.

**Decision: "unresolved"** (a near tie, pointing to missing structure). The diagonal is strong, but the real margin is
about half the bootstrap margins. mA+mB is chosen because:
- it has the best all-data cost and the best cross-run score (0.417);
- it is the only pair that passes the constant-action extinction and limit-cycle gate (mB+mC cycles at protection 0,
  with a tail range/mean of 1.2);
- it matches the R2c release (an exponential start followed by an additive cap).

The pinned parameters (a_m2, J0, kF) mark the missing cohort delay (G4). Confidence is medium that {food renewal,
nursery} is the active pair. Every fit leaves settlement competition unused.

## 15. Final model and hand-off (Phase C)

- **Model:** mA food renewal + mB nursery in `greybox/wildlife_model.py`. The params are in `fits/wildlife/final.json`
  (the same as `v1/AB_all3.json`), fitted on R1 + R2c.
- **Scores:** cross-run (R1 fit → R2c) 0.417, against 0.066 for persistence.
- **Gates:**
  - local score: pass;
  - stability: pass (200 schedules, 8 of them 40,000 steps; 0 failures; worst alternation 0.42);
  - extra constant-action gate: pass (no extinction, no cycles);
  - contract: pass (40 × 4,000 steps in 7.2 s; every malformed case ok).
- **Submission:** `toronto26-participant-kit/models/wildlife/` (predict.py, wildlife_model.py, params.json) and
  `toronto26-participant-kit/submission-wildlife-v1.zip` (6.1 kB; roots ok; credential scan clean). Not uploaded.
- **Steps:** all 1,000 steps of the CAP are spent (R1 540, R2 400, R2c 60). The account still has 1,000, outside the CAP.
- **Open issues:**
  1. The ~18-tick stall and the full height of the post-release overshoot (G4) are still missing, with a_m2 and J0
     pinned at their limits. The next structure to try is a nursery food stock or a longer cohort delay.
  2. R2 120–250 (order B → P9a with the corridor open → P3 → the start of the hunting hold) is the worst segment
     (rms 0.16 in log units). The regrowth bump under hunting is under-fitted.
  3. The pair choice is "unresolved": the real margin is half the bootstrap margins, and every fit is a warm chain
     with a single restart. More restarts could change the costs.
