# Round 2: diagnosis and experiment plan (2026-09-28)

**Status: PROPOSED, NOT APPROVED. No steps have been spent.** Every run below needs the user's explicit "yes" per system.

**Sources:**

- The analysis continues `plans/cloud-handoff-2026-09-28.md` (local session) and `plans/overnight-report.md`.
- Everything numeric here is reproducible for free from `toronto26-participant-kit/`:
  - `python fits/round2/final_schedules.py [system]` checks bounds, screens candidate fits on each schedule and writes `fits/round2/segments/<system>_<run>.json`.
  - Outputs: `fits/round2/final_<system>.out`.
  - `python fits/round2/coverage.py` lists every held setting in our data (`fits/round2/coverage.out`).
  - `python fits/round2/insample.py` gives public vs in-sample.

**Notation:**

- **u** is the fraction of the distance from the brief's recovery action to its pulse action, applied to every control at once (u = 0 is recovery, u = 1 is pulse).
- Prediction cells are the mean of the last 10 ticks of each segment.
- σ is the local score σ (0.1 × std after tick 20).
- Predictions are from our candidate fits. **They are not data, and agreement between candidates is not evidence** (§1.3).

---

## 0. Summary

| System | Public | Left | Round 2 | Reserve | Main question the steps answer |
|---|---:|---:|---:|---:|---|
| social_contagion | 0.627 | 1,000 | 880 | 120 | Long-run recovery level, and what a *partial* incentive cut does |
| wildlife | 0.661 | 1,000 | 850 | 150 | Prey levels inside the pulse box (candidates disagree 3–4σ) and the release boom |
| hospital_queue | 0.672 | 700 | 600 | 100 | Whether 5–10 electives or staffing 15 overflow the hospital (model says queue ≈ 300) |
| market | 0.684 | 1,400 | 1,200 | 200 | Joint rate+tax, never observed but about half the scoring. **Needs your OK for market work.** |
| epidemic | 0.720 | 1,055 | 900 | 155 | Long-run level under the joint pulse box and single closure; first wave under controls |
| power_grid | 0.742 | 1,000 | 890 | 110 | Price > 1.5 and mid-price, the mid-reserve ladder, the M2 loophole (200-tick dispatch) |
| traffic | 0.834 | 700 | 600 | 100 | Whether u ≈ 0.7 congests (candidates split 4–6σ); controls acting inside a congested regime |
| supply_chain | 0.845 | 700 | 600 | 100 | Levels at pulse-box interior and receiving mid-levels (shipment bias) |
| reservoir | 0.852 | 1,000 | 900 | 100 | Pulse-box interior drain, the release knife edge 10–11, the quality long run (m12 vs m13 differ ≈ 7σ) |
| ad_auction | 0.879 | 1,000 | 800 | 200 | Interior and bid/cap ladders; slow memories over a 250-tick hold |

Round 2 uses 8,220 of the 10,555 steps left. Every run starts from a fresh reset (scoring does too), so controls act from tick 0. Runs are named R4/R5 (market: B/C) and saved via `run_schedule.py`.

**Decisions needed from you:**

1. Approve, change or cut each system's runs (§4 and §5).
2. Allow market work (MK1/MK2). The handoff rule says to ask first.
3. **Gateway key.** This session reaches the gateway but gets 401: no key is configured. Pick one:
   - add the key as the environment's API credential for `gt-gateway-wavddee32q-uc.a.run.app`, or as env var `GROUNDTRUTH_KEY` (a new session may be needed to pick it up); or
   - run the commands in §7 on your Windows machine and push the data.
4. **Do now, whatever you decide on the rest:** upload the current `submission-overnight-all.zip` to the **Final** tab. Public uploads never become final. This is a safety net and uses 1 of today's 3 slots per system (§6).

---

## 1. Diagnosis common to all systems

### 1.1 Public vs in-sample

The shipped models were run on all our own data and scored with σ = 0.1 × std. Our runs are deliberately hard (many switches), so public normally lands far **above** in-sample (+0.12 to +0.29).

| System | Public | In-sample | Gap | Reading |
|---|---:|---:|---:|---|
| ad_auction | 0.879 | 0.588 | +0.29 | fine |
| supply_chain | 0.845 | 0.557 | +0.29 | fine |
| traffic | 0.834 | 0.555 | +0.28 | fine |
| power_grid | 0.742 | 0.532 | +0.21 | in-sample misfit (load, freq 0.43–0.45) |
| reservoir | 0.852 | 0.680 | +0.17 | fine; quality 0.26 in-sample |
| wildlife | 0.661 | 0.521 | +0.14 | in-sample misfit (predators 0.41–0.46) |
| hospital_queue | 0.672 | 0.556 | +0.12 | in-sample misfit (discharges 0.38) |
| market | 0.684 | 0.660 | +0.02 | both problems |
| epidemic | 0.720 | 0.739 | **−0.02** | **extrapolation failure** |
| social_contagion | 0.627 | 0.738 | **−0.11** | **extrapolation failure** |

Two kinds of failure follow from this:

- **Misfit** (wildlife, hospital, power_grid, partly market): the model can't reproduce data we already have. Free structural fixes come first there (§3).
- **Extrapolation** (epidemic, social_contagion, partly market): the models reproduce what we measured and fail on what the scorer asks. Only new regimes fix this, so these systems get new-regime runs.

Caveat: the organizer's σ is unknown, and ours is inflated in some systems (epidemic's 500-case first wave). Treat the gap as a strong signal, not proof.

### 1.2 What is wrong is mostly the base structure and the level map, not the mechanism pair

Your read that "modelling choices are off" is right. The evidence says the choice that is off is mostly **base structure and the steady-state level map**, not *which two of three mechanisms*:

- Traffic and supply_chain shipped **with no mechanisms** and scored 0.83–0.84.
- Overnight, mechanism swaps moved local scores by 0.01–0.05. Base-structure fixes moved them by 0.1–0.3.
- Episodes are 4,000 ticks, so transients are a few percent of scored ticks. A persistent 1σ offset caps an observable at 0.5 **for the whole hold**. Long-run levels at the settings the scorer holds dominate the score.

### 1.3 The overnight experiments had a blind spot, and the data shows where

`coverage.py` lists every setting we have ever held for ≥ 10 ticks. Across all ten systems:

- **The pulse-box interior (u 0.7–0.85) has never been held.** The only exceptions are a 35-tick wildlife segment and a few u = 0.5 single-control holds.
  - Every recovery-spacing episode (¼ of the score) pulses **each control independently at 70–100%**, so these interior points are what the scorer asks most.
  - We have only interpolated between u = 0 and u = 1. For nonlinear systems (congestion onset, saturation, thresholds) that is exactly where interpolation fails.
- **Long holds are rare.** The longest single hold per system is 120–200 ticks against 4,000-tick episodes. The longest recovery hold is 100 ticks (social) to 170 ticks (hospital).
- **Controls from reset were rarely used**, yet every scored episode starts from reset.
- Overnight probes were chosen by *disagreement between candidate pair fits*. The candidates share one base, so they agree even where all of them are wrong.
  - Screening confirms it: ad_auction and supply_chain candidates agree to < 1σ **everywhere**, including 3,000-tick holds, and so do most of social's and power_grid's.
  - Disagreement can't find the base model's blind spots. **Round 2 is designed by coverage of the scoring distribution instead**, and uses disagreement only as a bonus to rank mechanisms.

### 1.4 Design rules used in every system

1. **Fresh reset, controls from tick 0.** This matches scoring and doubles as the reset-transient test (relationship g).
2. **Pulse-box interior at u = 0.7, 0.85 and 1**, one intensity per pulse, so recovery-spacing runs also map intensity.
3. **At least one long hold (≥ 150–250 ticks) at an interior level, and one long recovery tail (≥ 150–300).**
4. **Recovery-spacing:** the same pulse after a long gap and after a short gap. The gain ratio measures slow memory.
5. **Gray-code ladders:** each step changes one control, so single-control effects are measured in different backgrounds (composition) and on/off pairs give order effects.
6. **No replicates.** The simulator is deterministic from reset, with noise of about 0.2–0.5%. One observation per new state is enough, so every step buys a new state.
7. **Mid-levels and the other side of recovery** where recovery is not at a bound: price 2.0, bid 0.75, freight 0, electives 5–10.

### 1.5 Coverage relationships (the matrix in each section)

Each system's matrix marks each relationship ✓ (existing data), ● (round 2) or ✗ (extrapolated; the justification is given).

- **(a)** Steady-state gain of each control at u ≈ 0.7 and 1 (nonlinearity).
- **(b)** The other side of recovery, or mid-levels.
- **(c)** Pairwise and all-joint composition.
- **(d)** On/off dynamics, dead times, asymmetry.
- **(e)** History: gap and order effects.
- **(f)** Long-run levels (≥ 150-tick holds).
- **(g)** The reset transient with controls from tick 0.

---

## 2. What "all relationships" can and cannot mean with 600–1,200 steps

A full factorial is impossible: 3–6 controls × 3 levels × history is thousands of states, each needing 30–100 ticks to settle. The argument for completeness is therefore structural:

1. **The scoring generator is structured, not arbitrary.** The docs name four categories built from the recovery action, the pulse action at 70–100% per control, and single versus joint compositions. Round 2 samples exactly that family:
   - the recovery→pulse ray at 0.7, 0.85 and 1;
   - single controls at their pulse-interior values;
   - one-at-a-time changes inside the box.
2. **Multiplicative, mechanistic base models interpolate well inside a sampled hull and badly outside it.** Round 2 moves the hull boundary to include the interior and the long run, where today we extrapolate.
3. **The remaining gaps are named** in each section's residual-risk list, so we know which forecasts are still extrapolations.

What is not guaranteed:

- 3-way interactions away from the recovery→pulse ray;
- histories longer than about 600 ticks;
- behaviour after 1,000+ ticks at settings we held for only 150–250.

For those, the model's structural form carries the forecast. We keep it bounded (lesson 8 of the overnight report).

---

## 3. Free work to do before and alongside spending (no steps)

In order of expected gain:

1. **hospital_queue:** per-class elective capacity. Elective discharges are 8–13σ too low in the data we already have.
2. **wildlife:** the predator block. Predators are half the observables, with σ ≈ 0.055, and score 0.41–0.46 in-sample.
3. **power_grid:**
   - a thermostat-population load model, because the ringing period depends on price;
   - the secondary frequency loop (kz pinned at its bound);
   - the share spike after release.
4. **supply_chain:** the D-level shipments bias (31.7 vs 34.8 = −2.5σ on every sustained tick). The retail level (781 vs 975) follows from it.
5. **All systems:** staged refits (base frozen, then modules), more restarts, and Powell before `least_squares` where it stalls. Check every model at 4,000+ ticks.

These are worth doing *before* round-2 data arrive only where the fix changes what we'd learn. Otherwise do them with round-2 data in the same refit.

---

## 4. Weak systems

### 4.1 social_contagion (0.627; 1,000 left; 880 planned, 120 reserve)

**Diagnosis.** The public score is 0.11 **below** in-sample, so this is an extrapolation failure. The model is fitted on transitions but never saw:

- a recovery longer than 100 ticks (the model's equilibrium of 96.5/83.7 is untested);
- any pulse-box interior point;
- any partial incentive change.

Its M2 expectation term is a linear gap form, which implies a large crash for *any* cut.

**Hypotheses, ranked by scoring impact:**

| # | Hypothesis | Why it matters |
|---|---|---|
| H1 | The long-run recovery level is wrong: the true tail stays near the crash floor (43/31) or rises past 96/84 | Recovery ticks are about half of every recovery-spacing episode |
| H2 | The incentive response is not linear-gap: a partial cut 2 → 1 crashes much less, or fully | Scored schedules at 70–100% hold incentive at 1.4–2.0, and composition episodes toggle it |
| H3 | Credibility memory (M1) is real: a pulse after a short gap gains less than after a long gap | m12 vs m23 |
| H4 | Interior saturation: u = 0.7 is nearly the u = 1 level (model: 192/121 vs 199/131) | Level map inside the box |

**SC1 (fresh reset, 560 steps):** intensity, long recovery tail, and spacing.

| Ticks | Action | m12 (A, B) | m23 | m2 | Tests |
|---|---|---|---|---|---|
| 0–99 | P1 u.7 (seed 6.3, inc 1.4, bridge 0.42) | 192, 122 | 192, 120 | 191, 120 | H4, (g) |
| 100–149 | recovery | 54, 39 | 59, 45 | 60, 46 | crash floor |
| 150–249 | recovery | 62, 57 | 71, 65 | 69, 63 | |
| 250–399 | recovery (tail to +300) | **83, 79** | **99, 87** | 92, 86 | **H1** (2.5σ on A, m12 vs m23) |
| 400–459 | P2 u.85 after a 300 gap | 184, 115 | 186, 116 | 184, 116 | |
| 460–479 | recovery gap 20 | 94, 61 | 96, 63 | 97, 64 | |
| 480–539 | P3 u.85 after a 20 gap | 174, 112 | 172, 109 | 172, 110 | **H3** |
| 540–559 | recovery | 89, 59 | 89, 59 | 89, 60 | |

**SC2 (fresh reset, 320 steps):** a partial incentive cut, and incentive before versus after recruitment.

| Ticks | Action | m12 | m23 | m2 | Tests |
|---|---|---|---|---|---|
| 0–79 | seeding 4.5 alone | 185, 91 | 187, 89 | 185, 89 | mid seeding, (b) |
| 80–139 | + incentive 2 | 194, 110 | 196, 111 | 194, 110 | incentive *after* recruitment (the brief's comparison) |
| 140–189 | incentive 1 | **109, 60** | **129, 71** | 129, 71 | **H2** (3.3σ on A) |
| 190–239 | incentive 0 | 83, 42 | 105, 53 | 103, 52 | |
| 240–319 | seeding 0 (recovery) | 80, 52 | 92, 65 | 89, 64 | floor after a seeding-only history |

**Decision rules:**

- **H1.** Fit an exponential asymptote to ticks 250–399.
  - Within ±10% of 96/84: keep the structure and refit.
  - Flat near 43/31: remove organic regrowth (core-only equilibrium).
  - Above 105/90: enlarge the organic pool.
  - Either way the new asymptote becomes a pinned fit target.
- **H2.** Compare the A drop at incentive 1 (from 194) with the drop at incentive 0 (known: to about 43).
  - Ratio 0.4–0.6: the linear gap is right.
  - Above 0.8: any cut triggers disappointment (a step-function trigger).
  - Below 0.2: payment-based (disappointment only near 0).
- **H3.** Take the ratio of the 60-tick gain of P3 over P2.
  - Below 0.85: M1 confirmed, keep m12.
  - 0.95 or more: switch to m23 (the fallback is ready).
- **H4.** Place the u.7 plateau on the recovery → u1 line to set the saturation curvature.

**Coverage:**

| | seeding | incentive | bridge |
|---|---|---|---|
| (a) u≈0.7 / 1 | ● SC1 (joint) / ✓ | ● SC2 (1.0 ≈ u.5) / ✓ | ● SC1 (joint only) / ✓ |
| (b) mid | ● 4.5 | ● 1.0 | ✗ bridge alone at 0.3 (bridge acts only with seeding, as R1 showed) |
| (c) composition | ✓ seed+bridge, ● seed+inc (bridge 0), ● all at .7/.85 | | |
| (d) on/off | ✓ seeding, incentive; ● incentive partial off | | |
| (e) history | ● gap 300 vs 20; ● incentive after recruitment; ✓ incentive before (R1) | | |
| (f) long run | ● recovery +300; ✗ pulse level past 200 (model saturates, R2 200-tick hold flat) | | |
| (g) reset | ● P1 from tick 0; ● seeding from tick 0 | | |

**Critique and cuts:**

- Cut: a 1,000-tick incentive-1 hold, and seeding 4.5 for 1,000.
  - The screen says incentive 1 stays level after 50 ticks in all models.
  - If SC2 shows ongoing drift at incentive 1, spend the 120-step reserve continuing SC2 at incentive 1 (`--continue`).
- **Residual risk:**
  - B's bridge lag of about 50 ticks is only measured at full bridge.
  - Bridge 0.3 with seeding > 0 is interpolated.
  - Recovery beyond +300 is extrapolated from the fitted asymptote.
  - **Public A/B:** upload the recovery-asymptote variants (current vs round-2 fit) as paired public tests; §6 shows the slot use.

### 4.2 wildlife (0.661; 1,000 left; 850 planned, 150 reserve)

**Diagnosis.** In-sample misfit, mostly predators (σ 0.055, scoring 0.41–0.46). In addition:

- The release boom is missed: peak 140 in the model vs 172 in the data, and the stall is missed too.
- The pulse box is where candidates diverge most. Over 2,000-tick holds at joint 0.7, prey N ranges 16–61 (6.3σ).

**Hypotheses:**

| # | Hypothesis | Why it matters |
|---|---|---|
| H1 | Prey inside the box (hunting 5–6, habitat 0.2–0.37, corridor 0.7–0.85) are far from any candidate | Every pulse; candidates disagree 3–4σ |
| H2 | The release overshoot needs a cohort delay or nursery food stock (mB), not just food renewal | Every recovery episode starts with a release |
| H3 | Gap memory: food stock (mA) vs juvenile deficit (mB) | The pair |
| H4 | The predator long run depends on prey (currently a fixed decay to 2.4) | Half the observables |

**WL1 (fresh reset, 500):**

| Ticks | Action | AB | AC | BC | base | Tests |
|---|---|---|---|---|---|---|
| 0–79 | joint .85 (hunt 5.95, hab 0.235, corr 0.85) | prey N **12.7** | 30.7 | 31.0 | 40.7 | H1, (g) |
| 80–109 | release +30 | N/S 131/124 | **154/144** | 115/96 | 117/97 | H2 |
| 110–199 | release +120 | 123/97 | 123/97 | 122/97 | 124/97 | |
| 200–259 | joint 1 | 10.2 | 23.0 | 14.2 | 17.2 | |
| 260–289 | short gap 30 | S 116 | **S 58** | S 95 | S 96 | H3 (gap memory) |
| 290–349 | joint .7 | **24.5** | 34.0 | 53.6 | 60.5 | H1 |
| 350–499 | release +150 | 123/98 | 124/97 | 122/97 | 124/97 | H4 tail |

**WL2 (fresh reset, 350):** a gray-code ladder.

| Ticks | Action | AB (N) | AC | BC | base |
|---|---|---|---|---|---|
| 0–79 | hunt 5 | 66.5 | 55.0 | 70.8 | 72.0 |
| 80–139 | + habitat .37 | **16.6** | 31.6 | 58.4 | 67.0 |
| 140–199 | habitat .37 alone | 103 | 86 | 117 | 119 |
| 200–259 | + corridor .7 | 101 | 88 | 110 | 110 |
| 260–319 | corridor .7 alone | 125 | 128 | 120 | 120 |
| 320–349 | recovery | 142 | 129 | 135 | 136 |

This also covers the brief's "harvest before vs after protection".

**Decision rules:**

- **Pair ranking.** Rank pairs by joint .85 and .7 prey N and by hunt5+hab.37 (candidates 1.3–9σ apart). A candidate outside ±2σ on two of the three is dropped.
- **Release overshoot.** If the release +30 overshoot is again ≥ 20% above every candidate, add a cohort delay or a nursery food stock (H2).
- **Short gap.** Prey S near 58 after the short gap confirms the food-stock memory (AC). Near 95–116 favours the juvenile deficit.
- **Predators.** If the predator level at release +150 differs from 2.2–2.45 by more than 2σ, the predator equilibrium must depend on prey (H4).

**Coverage:**

| | hunting | habitat | corridor |
|---|---|---|---|
| (a) | ● 5 alone, ● 5.95/4.9 joint / ✓ 7 | ● .37 alone, ● .235 joint / ✓ .1 | ● .7 alone, ● .85 joint / ✓ 1 |
| (b) mid | ✓ 4 (R1) | ● .37 | ● .7 |
| (c) | ● H+Hab, ● Hab+C, ● all at .7/.85/1; ✓ Hab+H (R2c), ✗ H+C alone (corridor lowers totals additively in data; interpolated) | | |
| (d) | ✓ each on/off; ● ladder on/off in new backgrounds | | |
| (e) | ● gap 120 vs 30; ● harvest before vs after protection | | |
| (f) | ✓ hunting 200 (R2c); ● release +150 twice; ✗ the joint-box level past 80 ticks | | |
| (g) | ● joint .85 and hunt 5 from reset | | |

**Critique:** joint-box holds are 60–80 ticks. Settling within that window is *assumed* from the model and from R2c's 200-tick hunting hold; it is checked with `greybox.common.settle` right after the run. If a segment has not settled, the reserve continues it. A 2,000-tick hold was considered and rejected: the long-run spread comes mostly from where prey settle, which 80 ticks shows. **Residual risk:** the predator slow tail beyond 150 ticks, and H+C without habitat.

### 4.3 hospital_queue (0.672; 700 left; 600 planned, 100 reserve)

**Diagnosis.**

- In-sample misfit: elective discharges are 8–13σ too low.
- A knife edge: at recovery, capacity (about 11.4–16.7) barely exceeds arrivals (11.49). The shipped model therefore predicts that **5 electives, or staffing 15 with no electives, flood the queue to about 290–305**. We have never tested it. Sustained-operation episodes will visit these regimes for thousands of ticks.
- The long-stay pool: after long elective holds, the model leaves a permanent residual queue of 69–108. Only 11.5–34.5 were ever observed.

**Hypotheses:**

| # | Hypothesis | Why it matters |
|---|---|---|
| H1 | Electives have their own capacity (per-class), so small elective loads do *not* flood the shared queue | Discharges are 1/3 of the observables; any elective level |
| H2 | Capacity per staff is concave: staffing 15 still clears arrivals | Every staffing level between 5 and 20 is untested |
| H3 | The long-stay pool drains (not permanent), or is much smaller | Every recovery tail after a pulse |

**HQ1 (fresh reset, 250):**

| Ticks | Action | final_m12 (wait, queue, disch) | v5 base | Tests |
|---|---|---|---|---|
| 0–49 | electives 5 | 19, **305**, 5.9 | 17, 276, 9.1 | H1, (g) |
| 50–99 | electives 10 | 32, 309, 5.1 | 33, 292, 8.8 | H1 level map |
| 100–149 | staffing 15 + electives 10 | 44, 311, 3.8 | 49, 301, 6.6 | H2 × electives |
| 150–199 | staffing 15 alone | 36, 289, 6.3 | 45, 290, 6.8 | H2 (drain) |
| 200–249 | recovery | 18, 197, 10.2 | 26, 221, 10.1 | drain rate |

**HQ2 (fresh reset, 350):**

| Ticks | Action | final_m12 | v5 base | Tests |
|---|---|---|---|---|
| 0–89 | joint .7 (staffing 9.5, electives 14, diag .645, urgent .88, overtime .7, follow-up .3) | disch **2.6** | disch **6.9** | interior, 4.6σ |
| 90–139 | recovery | 32, 259, 8.4 | 32, 244, 9.7 | |
| 140–199 | joint 1 | 111, 312, 1.0 | 94, 300, 3.3 | fatigue after a pulse |
| 200–349 | recovery +150 | queue **108** at +150 | 95 | **H3** (the observed residual was 34.5) |

**Decision rules:**

- **H1.** If queue at electives 5 stays below 80 and discharges rise by about the elective rate, H1 holds: implement separate elective service (the free fix, §3). A flood to 250+ means the shared queue is right; refit only the rates.
- **H2.** If staffing 15 alone drains the queue at ≥ 1/tick, capacity at 15 exceeds arrivals: make capacity ∝ staffing^α with α < 1, or add a saturation.
- **H3.** Fit an exponential to the recovery +150 queue.
  - Asymptote ≤ 40: the Lq pool is small or draining; replace the permanent pool.
  - Asymptote ≈ 100: keep it.

**Coverage:**

| | staffing | electives | diag | urgent | overtime | follow-up |
|---|---|---|---|---|---|---|
| (a) | ● 9.5 joint, ● 15 / ✓ 5 | ● 5, 10, 14 / ✓ 20 | ● .645 joint / ✓ .75 | ● .88 joint / ✓ 1 | ● .7 joint / ✓ 1 | ● .3 joint / ✓ 0 |
| (b) | ✓ 12.5 (with electives only) | ● 5, 10 | ✓ 0.1 (R2c) | ✗ < 0.6 (assumed to only reorder admissions; untested) | ✓ spacing (R2c) | ✗ mid (M3 absent: follow-up has no effect) |
| (c) | ● staffing × electives; ● all at .7 and 1; ✓ singles on electives background (R1) | | | | | |
| (d) | ✓ all six on/off; ● electives step up and down | | | | | |
| (e) | ● gap 50 between .7 and 1; ✓ overtime spacing | | | | | |
| (f) | ● recovery +150 after pulses; ✗ elective holds > 100 ticks (the model saturates the queue within 50; untested) | | | | | |
| (g) | ● electives 5 and joint .7 from reset | | | | | |

**Critique:** 700 is tight. Cut: a staffing-12 1,000-tick hold (the screen says the queue saturates within 50). **Residual risk:** urgent priority below 0.6, and long elective holds with overtime (fatigue build over hundreds of ticks).

### 4.4 market (0.684; 1,400 left; 1,200 planned, 200 reserve). **Needs your OK for market work.**

**Diagnosis.** There is one 600-tick run with single controls only. **Joint rate+tax has never been observed**, yet all recovery pulses and the joint category use it (about half the score). The models assume additivity. The market plan's own hypothesis, "price impact ∝ 1/depth", predicts an interaction.

**Hypotheses:**

| # | Hypothesis |
|---|---|
| H1 | Joint effect ≠ sum of singles (price moves more when depth is low) |
| H2 | Mid-levels are nonlinear (rate 0.05: m12 82.7 vs m23 76.2, **7σ** on price) |
| H3 | Order and hysteresis: rate→tax differs from tax→rate |
| H4 | Slow memory over 125-tick holds and 50-tick gaps (M3 vs M2) |

**MK1 (fresh reset, 600):**

| Ticks | Action | m12 (price, vol, depth) | m13 | m23 |
|---|---|---|---|---|
| 0–149 | joint 1 (0.1, 0.05) | 73.9, 1.84, 41.1 | 74.5, 1.80, 41.4 | 70.4, 1.89, 42.1 |
| 150–299 | recovery | 92.4, 1.81, 91.0 | 92.8 | 91.6 |
| 300–424 | joint .7 | 79.3, 1.83, 56.1 | 79.6 | 81.1 |
| 425–474 | gap 50 | 82.4, 2.10, 90.4 | 82.2 | 84.9 |
| 475–599 | joint 1 again | 74.3, 1.85, 41.1 | 74.6 | 76.2 |

**MK2 (fresh reset, 600):**

| Ticks | Action | m12 | m13 | m23 |
|---|---|---|---|---|
| 0–124 | rate .05 | **82.7** | 82.6 | **76.2** |
| 125–249 | + tax .05 | 83.8, 41.3 | 84.1 | 81.4 |
| 250–374 | tax only (rate off: order effect vs MK1) | 92.1 | 93.2 | 91.5 |
| 375–499 | tax .025 | depth 66.7 | 65.9 | 66.7 |
| 500–599 | recovery | 92.7 | 92.9 | 93.9 |

**Decision rules:**

- **H1.** If the joint-1 price is outside the additive prediction by > 2σ (> 1.8), add a depth-dependent price impact.
- **H2.** Rate .05 picks between m12/m13 and m23 directly (a 7σ gap).
- **H3.** Compare "tax only after rate+tax" with tax-only in run A.
- **H4.** "Joint 1 again" after a 50 gap vs after reset: a gain ratio below 0.9 means a slow memory.

**Coverage:** (a) ● .7 and 1 joint, ● rate .05; (b) ● tax .025; (c) ● both orders; (d) ✓ each on/off; (e) ● gap 150 vs 50; (f) ✓/● 125–150 holds, ✗ past 150; (g) ● joint and rate from reset. **Residual risk:** rate .07 alone (interpolated), and holds past 150.

### 4.5 epidemic (0.720; 1,055 left; 900 planned, 155 reserve)

**Diagnosis.** The public score is 0.02 below in-sample, so the model fails on regimes we never tested:

- Long-run levels under sustained controls: model equilibria are about 42–107, but data reach only tick 240.
- The mask+closure plateau of 89 in R2 was *not* declining, while the model says it keeps falling.
- All three controls together, and controls during the first wave, were never observed.

**Hypotheses:**

| # | Hypothesis |
|---|---|
| H1 | The equilibrium under restrictions is much higher than modelled (fatigue/behaviour pulls it back up): the R2 plateau of 89 already hints at this |
| H2 | Controls from reset change the first wave strongly (182 vs 243 across candidates, 2.7σ) |
| H3 | Vaccination's sustained effect and the M2 developing-immunity tail |
| H4 | Closure alone during the first wave (274 vs 319, 2.8σ) and closure × mask composition |

**EP1 (fresh reset, 400):** all three at .85 (mask .85, closure .85, vacc .00255) for 250, then recovery 150.

| Ticks | m13 (cases, beds) | m12 | base | m23 |
|---|---|---|---|---|
| 0–39 first wave | 182, 154 | 190, 149 | 243, 155 | 241, 155 |
| 100–249 level | 56, 43 | 53, 39 | 61, 47 | 61, 45 |
| release (250–289) | 148, 67 | 153, 69 | 156, 86 | 146, 79 |
| recovery +150 | 93, 67 | 92, 67 | 88, 66 | 92, 68 |

**EP2 (fresh reset, 300):** vaccination 0.003 for 200, then off for 100.

| Ticks | m13 | m12 | base | m23 |
|---|---|---|---|---|
| 40–199 | 90, 59 | 91, 60 | 82, 61 | 87, 63 |
| off +100 | 114, 82 | 112, 81 | 103, 78 | 103, 76 |

**EP3 (fresh reset, 200):** closure 1 for 120, then add mask .7 for 80.

| Ticks | m13 | m12 | base | m23 |
|---|---|---|---|---|
| 0–39 first wave | **274** | 319 | 309 | 318 |
| 40–119 | 57, 41 | 51, 39 | 60, 39 | 58, 37 |
| + mask .7 | 85, 59 | 83, 55 | 69, 45 | 79, 53 |

**Decision rules:**

- **H1.** The EP1 level at ticks 100–249:
  - ≥ 80: the equilibrium structure is wrong. Strengthen fatigue or risk compensation and pin that level.
  - 50–60: the structure is right; refit.
- **H2 and H4.** The first-wave peaks rank candidates directly (> 2.7σ spread).
- **H3.** If cases keep falling for ≥ 10 ticks after vaccination stops, M2 (developing immunity) is active.
- **Refit rule.** Refit with all four runs (R1, R2, R4–R6). Choose by the new runs' score, not by cost.

**Coverage:** (a) ● all at .85; ● closure 1 alone; ● vacc 0.003 alone; ✓ mask 1, mask .5 (b), closure 1. (c) ● all three; ● C+M.7; ✓ M+C. (d) ✓ each on/off. (e) ✓/● release after long holds. (f) ● 250-tick all-three hold, ● 200-tick vaccination hold. (g) ● three new from-reset starts. ✗ M+V and C+V, interpolated through the multiplicative transmission form. **Residual risk:** the endemic oscillation period beyond 300 ticks.

### 4.6 power_grid (0.742; 1,000 left; 890 planned, 110 reserve)

**Diagnosis.**

- In-sample misfit on load (ringing period) and frequency (secondary control pinned).
- Untested inputs: price > 1.5 and 0–0.45, reserve between 0 and 150, interconnector mid-levels.
- The M2 test was a 50-tick hold, so depletion may only appear on longer dispatch holds.

**Hypotheses:**

| # | Hypothesis |
|---|---|
| H1 | Load vs price is nonlinear: price 2.0 load 96.7 (m1-family) vs 83.7 (m23), **6.8σ** |
| H2 | Share vs reserve is not 1/(1+w·Rd): the ladder predicts 0.17 / 0.12 / 0.09 at 40 / 80 / 120 |
| H3 | M2 (reserve depletion) shows up only past 150 ticks of dispatch at charging 0 |
| H4 | The rebound after a long joint pulse: load 69 (m1-family) vs 85 (m23), **8σ** |

**PG1 (fresh reset, 380):**

| Segment | m13 (load, freq, share) | m23 |
|---|---|---|
| price 2.0 (70) | 96.7, 50.0, .352 | **83.7**, 50.3, .382 |
| price .45 (70) | 114, 49.7, .345 | 116 |
| price 1.5 (60) | 101 | 95 |
| reserve 40 / 80 / 120 (30 each) | share .170 / .119 / .090; freq 50.1 / 50.4 / 51.0 | .183 / .122 / .092 |
| res 80 + ic .5 (30) | .093 | .093 |
| ic .5 (30) | .287 | .300 |
| recovery (30) | 94.8, .377 | 94.8, .379 |

**PG2 (fresh reset, 510):**

| Segment | m13 | m23 |
|---|---|---|
| joint .7 (price .45, res 105, ch .3, ic .44) (100) | 117, 50.1, .072 | 115, .067 |
| recovery (60) | 105 | 94 |
| **joint 1 × 200** (M2 loophole) | 125, 50.3, .046 | 125, .036 |
| recovery 30 | **69**, 51.0 | **85**, 50.6 |
| joint .85 (80) | 123, .058 | 119, .050 |
| recovery (40) | 86 | 92 |

**Decision rules:**

- **H1 and H4.** Price 2.0 and the post-pulse rebound separate the m1-family from m23 (7–8σ).
- **H2.** Fit share vs reserve on the ladder. If it's linear with a clip, replace the 1/(1+w·Rd) form.
- **H3.** If share or frequency drifts during ticks 250–359 of the long joint-1 hold (beyond 2σ), M2 is active: move to m12 or m23.
- **Frequency.** Frequency at reserve 120 (51.0 predicted) calibrates the frequency gain.

**Coverage:** (a) ● price .45, reserve ladder, ic .5, all at .7/.85; ✓ singles at 1. (b) ● price 2.0, reserve 40/80/120, ic .5. (c) ● reserve × ic, all joint; ✓ reserve × charging. (d) ✓. (e) ● recovery 60 vs 30 around pulses. (f) ● 200-tick dispatch. (g) ● price 2.0 and joint .7 from reset. ✗ charging mid-level alone (it acts only through the reserve refill). **Residual risk:** the ringing at price 0 over long holds.

---

## 5. Strong systems (more domain for a better fit)

The public scores are 0.83–0.88 with healthy gaps above in-sample, so the structure is right and the fit needs **domain**:

- In screening, candidates agree to < 1σ almost everywhere (ad_auction and supply_chain *everywhere*), so these runs won't choose mechanisms.
- They are level-mapping runs: interior points, ladders, one long hold.
- The gain comes from refitting on wider data. The expected lift is modest (+0.02–0.05 each), and it is safer than the weak systems' structural bets.

### 5.1 ad_auction (0.879; 1,000; 800 planned, 200 reserve)

- **AD1 (500):**
  - u.7 (bid 3.95, cap 76, breadth .71) from reset for 250;
  - recovery 100;
  - u1 50;
  - recovery 25;
  - u.85 75.
- **AD2 (300):**
  - bid ladder 3.25 / 2 / 0.75 at cap 100 (50 each);
  - recovery 50;
  - bid 5 at cap 50 then cap 30 (50 each).
- **Predictions (final fit):**
  - conversions at u.7 fall from 5.38 (first 50 ticks) to 4.37 (ticks 50–249), which tests the slow M2/M3 memories over 250 ticks (open issue 2);
  - AD2 spend 22.3 / 15.4 / 7.2 along the bid ladder;
  - spend is *not* pinned at caps 50 or 30 (26.3 / 25.8).
- **Rules:**
  - A conversion drift at u.7 that keeps going past tick 150 needs a longer τ.
  - If spend pins at cap 30, the bid × cap interaction is misfit.
- **Residual risk:**
  - breadth changes at fixed bid;
  - bid 0–0.75.

### 5.2 reservoir (0.852; 1,000; 900 planned, 100 reserve)

- **RS1 (450):**
  - u.7 (release 9, irrigation 5.6, depth .7, aeration .3) from reset for 250 (level 379 → 304);
  - recovery 200.
  - Quality: m13 0.930 vs m12 0.937–0.939 in recovery, about **7σ** apart.
- **RS2 (450):**
  - release 10.5 for 150 (knife edge: 515 predicted);
  - then an aeration/depth ladder: aeration .3; aeration .15 + depth .5; aeration 0 + depth .5 (80 each);
  - recovery 60.
- **Rules:**
  - The recovery quality level settles M3 vs M2 (the weak channel, in-sample 0.26).
  - Release 10.5 pins the outflow cap's level exponent.
  - The aeration ladder gives quality's dose-response, never measured below 1.
- **Residual risk:**
  - the seasonal phase × pulse timing;
  - irrigation alone at mid-levels.

### 5.3 supply_chain (0.845; 700; 600 planned, 100 reserve)

- **SU1 (400):**
  - u.7 from reset for 150 (shipments 24.1, retail 257);
  - recovery 60;
  - u1 60;
  - recovery 30;
  - u.85 100 (shipments 21.3, retail 175–220).
- **SU2 (200):** orders 80 with receiving 1.0 / 0.7 / 0.5, then + maintenance .3 (50 each; shipments 25.9 / 21.5 / 18.1 / 21.4).
- **Rules:**
  - If shipments on every orders-80 segment sit about 10% above the model, as in the known D-level bias, fix the service-rate structure. The receiving ladder then pins the curve.
  - Maintenance .3 vs 0 vs 1 gives the maintenance dose-response.
- **Residual risk:**
  - product-mix changes;
  - lead_time_buy mid-levels.

### 5.4 traffic (0.834; 700; 600 planned, 100 reserve)

- **TR1 (400):**
  - u.7 from reset for 150;
  - recovery 50;
  - u1 80;
  - recovery 30;
  - u.85 90.
  - **At u.7 the candidates split 4σ.** speed_a is predicted at 8.4 (shipped) vs 15 (m12), 10.5 (m23) and 26 (m13). The question is whether the congestion onset lies below or above u.7. The recovery drain after u.7 splits 6σ.
- **TR2 (200):**
  - background B = recovery + ramp 1 + toll 1.5, a congested background (speeds 14–16);
  - then freight 0 (speed_a to 8.7), signal .3, lane .3, and clearance .5, each 30–40 ticks.
  - This design replaces the draft's toll-5 background, where the screen showed these controls do nothing (the regime is uncongested).
- **Rules:**
  - Locate the congestion onset in heavy share between u.7 and u.85.
  - The freight 0 and lane .3 responses fix open issues G12 and freight 0 (both never probed).
- **Residual risk:**
  - the period-2 oscillation under per-tick switching.

---

## 6. Upload-slot and timeline plan

- **Slots:** 3 accepted uploads per system per Toronto day, shared by the public and final tabs. A crash after acceptance still costs the slot.
- **Deadline:** final uploads close **2026-09-30 12:00 Toronto**. **Public uploads never become final.**

| When (Toronto) | Action | Slots used per system |
|---|---|---|
| 09-28 now | **Final tab: upload `submission-overnight-all.zip` as it is (safety net)** | 1 |
| 09-28 | Approve round 2 → run per system (a few minutes each) → refit | 0 |
| 09-28 evening | Public A/B of the round-2 refits for the systems ready | ≤ 2 |
| 09-29 | More public A/B (paired: same 40 public episodes, so differences are reliable); then final upload of the winners | ≤ 2 public + 1 final |
| 09-30 before 12:00 | Last corrections to Final only; keep 1 slot for a rollback | ≤ 3 |

Only the **latest** accepted final upload counts. Keep every submitted ZIP. Never make the final upload the untested variant.

## 7. Execution (after approval; from `toronto26-participant-kit/`)

Steps per system:

1. Free budget check.
2. Run each schedule from its segment file.
3. Log the spend in `plans/<system>-plan.md`.
4. Commit a snapshot.

```sh
python run_schedule.py --budget social_contagion                                   # free
python run_schedule.py --system social_contagion --output data/social_contagion/R4.json \
    --segments fits/round2/segments/social_contagion_SC1.json --confirm 560
python run_schedule.py --system social_contagion --output data/social_contagion/R5.json \
    --segments fits/round2/segments/social_contagion_SC2.json --confirm 320
```

| System | Run → file | Steps |
|---|---|---:|
| social_contagion | SC1 → R4, SC2 → R5 | 560 + 320 |
| epidemic | EP1 → R3, EP2 → R4, EP3 → R5 | 400 + 300 + 200 |
| wildlife | WL1 → R3, WL2 → R4 | 500 + 350 |
| power_grid | PG1 → R3, PG2 → R4 | 380 + 510 |
| hospital_queue | HQ1 → R3, HQ2 → R4 | 250 + 350 |
| market | MK1 → B, MK2 → C | 600 + 600 |
| ad_auction | AD1 → R3, AD2 → R4 | 500 + 300 |
| reservoir | RS1 → R4, RS2 → R5 | 450 + 450 |
| supply_chain | SU1 → R4, SU2 → R5 | 400 + 200 |
| traffic | TR1 → R4, TR2 → R5 | 400 + 200 |

The reserves (100–200 per system) are held for a confirmation run after refits (round 3), each proposed separately.
