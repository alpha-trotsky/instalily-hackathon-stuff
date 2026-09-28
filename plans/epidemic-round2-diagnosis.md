# Epidemic round 2: diagnosis of R3–R5 against the shipped v1 model

Diagnostician pass, 2026-09-28. **0 steps spent.** The budget read (free) shows 155 remaining. No model files were changed.

- Scripts and plots are in `toronto26-participant-kit/fits/epidemic/round2/` (KIT-relative paths below).
- σ = 0.1 × std after tick 20 of R1–R5 = **8.41 cases, 4.31 beds**, as in `heldout.py`.
- "v1" means `fits/round2/v1_models/epidemic`, which is byte-identical to `models/epidemic`: m13_all, the three-age-group SEIRS with m1 fatigue and m3 release.
- **Plots** (data, v1, the m12_all candidate, v1 err/σ and a controls panel):
  - new runs: `fits/epidemic/round2/R3_v1.png`, `R4_v1.png`, `R5_v1.png`;
  - old runs, for comparison: `R1_v1.png`, `R2_v1.png`.

## 1. Summary

1. **v1 held out on R3–R5 scores 0.532** (cases/beds: R3 0.59/0.53, R4 0.56/0.53, R5 0.42/0.56). It scores 0.742 in-sample on R1+R2. The unused candidate **m12_all scores best held out (0.600)**. base_all scores 0.556 and m23_all 0.535.
2. **Pre-registered rules:**
   - H1 is rejected: the restricted level is 61, not ≥ 80, so the structure is right and a refit is enough.
   - H2 and H4 favour the m1 candidates. m13 is best for the all-.85 first wave; m12 is best for the closure-alone first wave. base and m23 miss by 5–7σ.
   - H3 fires (cases keep falling for about 22 ticks after vaccination stops). However, elderly-priority vaccination with no M2 reproduces the same signature, so it does **not** identify M2.
3. **New behaviour 1 (B18/B19): vaccination acts mostly on hospital load, not on cases.**
   - Under vaccination the H/case ratio falls to 0.54, against about 0.67 in v1. After vaccination stops it recovers over about 60 ticks.
   - Vaccination barely changes the case level (99.7 vs about 97 without it) or the first wave (−3%, where v1 gives −10%).
   - One structural change explains all of this: **doses go preferentially to the high-severity elderly group** (weight ≈ 5–9). With v1's parameters unchanged it lifts R4 from 0.545 to 0.696 and R3 from 0.563 to 0.657.
4. **New behaviour 2 (B20): the mask effect is not eroded by long holds.**
   - The mask .85 release after 250 ticks jumps by +0.32 in log units, the full size; v1 gives +0.21.
   - Mask .7 added after 120 ticks of closure gives −0.20; v1 gives −0.13.
   - v1's closure-driven fatigue (mix 0.9, gF 0.5) wrongly scales the mask effect by about 0.55. This drives the R3 release miss (−5σ) and the R5 mask miss (+2σ).
   - Quick refits that remove mask fatigue lose R2's in-hold recovery (R2 score 0.60), so that conflict is still open.
5. **Where the score goes:** 27% of the loss is vaccination-driven hospital level, 20% is the R3 post-release wave, 13% is R5's closure+mask segment and 12% is the closure-alone first wave and floor. First-wave transients are only about 10%.

## 2. Decision-rule verdicts (`round2-experiments.md` §4.5)

- Candidates were re-simulated on the **actual** initial readings and actions (`cands.py`). The pre-run table in `final_epidemic.out` used initial 170/45.
- Each cell is the mean of the last 10 ticks of the segment unless stated otherwise, as cases, beds.

| Rule | Quantity | Data | m13 (v1) | m12 | base | m23 | Verdict |
|---|---|---|---|---|---|---|---|
| **H1** EP1 level at ticks 100–249 (R3) | ticks 240–249 | **61.0**, 39.4 | 55.7, 42.6 | 53.5, 39.2 | 60.3, 46.5 | 61.1, 45.1 | **61 < 80: H1 rejected**. The level is 1σ above the "50–60" band, so the equilibrium structure is right and a refit is enough. The cases level is effectively settled (fitted asymptote 61.7; drift over the segment 0.5 cases = 0.06σ). Beds are still rising slowly (asymptote 41.7). |
| **H2** first wave under all three at .85 (R3) | ticks 30–39 / peak | 180.5 / **281 @ 9** | 171.8 / 292 @ 10 | 189.4 / 306 @ 12 | 228.8 / 372 @ 18 | 223.7 / 372 @ 17 | Mean \|err\| over ticks 0–59: m13 **0.8σ**, m12 1.6σ, base 5.0σ, m23 5.1σ. **The m1 pairs win and base/m23 are rejected.** Controls from reset strongly blunt the first wave: 281 at c0 = 237 against v1's no-control 568. |
| **H4** closure alone during the first wave (R5) | ticks 30–39 / peak | 390.3 / **438 @ 27** | 327.3 / 412 @ 24 | 364.4 / 418 @ 26 | 364.3 / 526 @ 21 | 389.4 / 553 @ 17 | Mean \|err\| over ticks 0–59: **m12 1.6σ**, m13 3.7σ, base 5.7σ, m23 6.6σ. m23 matches ticks 30–39 only by crossing a peak that is 115 too high. **m12 wins: closure *moves* child contacts into homes (dsh = 1). m13 removes them (dsh ≈ 0) and makes the wave too narrow and too small.** |
| H4 closure × mask .7 (R5 120–199) | ticks 190–199 | 66.2, 45.1 | 82.2, 56.4 | 79.6, 51.6 | 68.6, 43.8 | 78.0, 51.0 | Data are lowest. The fatigue candidates are +1.6 to +1.9σ too high because fatigue weakens the mask (B20). base, with no fatigue, is closest. **Not settled** (rising 0.66/tick). |
| **H3** cases keep falling ≥ 10 ticks after vaccination stops (R4 200+) | min after tick 200 | minimum at **tick 221** (98.2 → 94.4) | min at 203 | — | — | — | **The rule fires: "M2 active".** Caveats: <br>(1) The decline began at tick 190, 10 ticks *before* the stop, and the log slope does not change at the stop (−0.0019 before, −0.0029 and −0.0017 after). <br>(2) v1 with elderly-priority doses and **no M2** puts the minimum at tick 218 (`variants2.py`). <br>So the rule is **confounded, and M2 stays unidentified.** The first-wave insensitivity (B19) is better evidence for a lag, but in the quick m1+m2 refit a_m2 still went to 0.96. |
| EP2 levels (R4) | 40–199 / 200–229 / 230–299 | 99.7, 52.5 / 94.6, 56.8 / 109.0, 79.6 | 88.4, 56.6 / 93.6, 62.6 / 114.1, 82.2 | 89.6, 57.7 / 92.5, 64.3 / 111.8, 81.3 | 81.7, 59.9 / 86.0, 62.4 / 102.8, 77.6 | 87.2, 61.7 / 84.1, 63.6 / 102.6, 76.1 | Every candidate is **too low on cases (−1.2 to −2σ) and too high on beds (+1 to +1.8σ)** under vaccination. This is structural (B18) and not a question of which pair. |
| EP1 release (R3 250–289) | ticks 280–289 | **188.8**, 74.1 | 147.3, 67.0 | 153.2, 69.5 | 155.9, 85.6 | 145.1, 78.4 | **All candidates are 4–5σ low.** The peak is 194 @ 290 against v1's 169 @ 300 (B20, B21). |
| EP1 recovery +150 (R3 290–399) | ticks 390–399 | 94.1, 66.1 | 92.6, 67.4 | 91.8, 67.0 | 87.9, 65.9 | 92.4, 68.3 | All within 1σ at the end, but the wave shape is wrong (B21). |
| Refit rule: choose by the new runs' score | held-out mean on R3–R5 | — | 0.532 | **0.600** | 0.556 | 0.535 | Of the shipped candidates, **m12_all** wins held out, on beds and on the closure first wave. In-sample, m13 was best (cost 8.8k vs 10.6k): lesson 6 again. |

## 3. Behaviour catalogue (new runs; continues B1–B17 of `epidemic-plan.md`)

- **Status** is "captured" or "not captured", with v1's error in units of σ.
- **Categories** are the scoring categories affected: S = sustained, O = order, R = recovery history, C = composition.

| ID | Behaviour | Evidence | v1 status | Cat. |
|---|---|---|---|---|
| B18 | **Vaccination lowers the hospital/case ratio** (H ÷ mean cases over ticks t−25…t−5), with a slow recovery after it stops: unvaccinated endemic ratio 0.66–0.88; R4 during vaccination 0.54; R4 after the stop 0.59 (+25 ticks), 0.70 (+65), 0.74 (+95); R3 with all three at .85: 0.65–0.67. | `ratio.py` | **Not captured.** v1's ratio is 0.67–0.80. Beds are +1.2σ over R4 40–199 (loss rank 1), +0.9σ over R3 100–249 (rank 2) and +1.1σ over R4 230–299. | S, R, C |
| B19 | **Vaccination has little effect on cases.** First wave from reset: R4 peak 489 @ 23 and 17.0k cumulative cases over ticks 0–59, against 502 and 17.6k without vaccination (R1) (−3%). Endemic level with vaccination 99.7 against about 95–100 without. | R4 vs R1; `cum.py` | **Not captured.** v1 cuts the first wave by 10% (435; −6σ at the peak) and the level to 88 (−1.35σ). | S, C |
| B20 | **The mask effect is full size after long holds**, whatever the history. 6-tick log jumps: R3 at 250 (release of .85 after 250 ticks) +0.32 (the full .85 effect is about 0.30–0.34); R5 at 120 (mask .7 after 120 ticks of closure) −0.20 (full effect about −0.24). | `jumps.py` | **Not captured.** v1 gives +0.21 and −0.13, because closure-driven fatigue scales the mask effect by about 0.55. | O, R, C |
| B21 | **The post-release wave is faster and earlier** after a long all-three hold. After a 1-tick latency cases grow +7%/tick (61 → 194 @ tick 290, 40 ticks after the release), then fall faster; beds peak at 120 @ 315. The wave is short: 94 by tick 400. | R3 250–399 | **Not captured:** −4.9σ at ticks 280–289 and +2.6σ at 320–330. v1 peaks at 169 @ 300 with a wider wave. Beds are −4σ at about 300 and +2σ at 360. Much of this follows from B20 (the release jump is 0.12 log units too small). | R, O |
| B22 | **Closure from reset delays and widens the first wave without shrinking it**: peak 438 @ 27 (unrestricted 502 @ 23); 41 ticks above half-peak (34 unrestricted); the cumulative cases over 0–59 are the same as unrestricted (17.4k vs 17.6k). | R5, `cum.py` | **Partly captured.** v1's wave is too narrow and too small (15.8k, −8σ at tick 35). m12 (dsh = 1) is close (16.7k, 1.6σ). | S, C |
| B23 | **Restricted troughs sit higher and plateau lower with controls from reset.** Floor 35.5 @ 105 → plateau 61 (R3). Closure alone: floor 43 @ 100–105, 47 @ 119 and rising. Closure + mask .7 dips to 39 @ 140 → 66 @ 199, rising (unsettled). R2 (restriction from tick 40, no vaccination): floor 15.5 → plateau 89. | R3, R5, R2 | **Partly.** R3 plateau −0.6σ; R5 closure floor +1.2σ (v1 55); R5 C+M.7 +1.9σ. | S |
| B24 | **The reset transient is unchanged under controls.** Cases stay at the initial reading for 2 ticks (R3 236.5, 237.7; R4 109.9, 109.3; R5 106.6, 106.4), then grow. Beds dip 28–32% to a minimum at tick 3–4 (R3 60.5 → 43.6), deeper than v1 (51.9). The bed cap is reached at tick 17–20, about 2 ticks earlier than v1 predicts. | `misc.py` | **Not captured**, but small. v1 jumps +9% at tick 1 (+2.4σ). Bed dip in R3 −1.9σ, then −4σ at tick 17 (early rise). About 1–2% of the loss. | S (first ticks of every episode) |
| B25 | **The initial reading matters at the top of its range.** At c0 = 237 with all three at .85 the peak comes at tick 9 (281); the no-control peak is at tick 22–24 for c0 = 107–124. v1's reset rule (E0 ∝ c0) transfers well: 292 @ 10. | R3 | **Captured** (0.8σ over ticks 0–59). | all |
| B26 | **The bed cap is the same in every run**: 155.1–155.3 (medians); it holds for 34–55 ticks (R3 17–51, R4 22–68, R5 20–75). Closure prolongs the capped period (R5 ends at 75 vs R1 71, with a lower peak). | `misc.py` | **Captured** (Hcap fixed; v1 releases the cap at 73–75). | S |
| B27 | **Stopping vaccination has no visible kink** in cases: the slope is unchanged, and the upturn comes about 20 ticks later. No bed catch-up bump either: beds rise smoothly, 53.9 → 79.6 over 100 ticks. That argues **against a shared-workforce referral throttle**, which would release a queue quickly. | R4 190–300; `jumps.py` | **Partly.** v1 turns up within about 6 ticks; the elderly-priority variant reproduces the timing. | O, R |
| B28 | **Noise** is multiplicative, 0.24% cases and 0.20–0.24% beds (second-difference MAD), the same as R1/R2. | `misc.py` | Fine. | — |
| B29 | **The damped endemic oscillation persists under vaccination**: R4 goes to a peak of 100.6 @ 190 under vaccination, a trough of 94.5 @ 221, then 109 @ 290 and still rising. Cases do not settle within 300 ticks at any setting except the R3 restricted plateau. | `settle` (all segments unsettled at noise-σ scale, drift up to 90 noise-σ) | Period and phase are captured roughly (±1.5σ). | S |

Relationships between outputs:

- Beds lag cases by about 20–25 ticks (R3 case peak 290, bed peak 315; as B5/R5).
- B18 is the only new relationship. It is controlled by vaccination history, is one-sided (it builds while vaccinating and fades after) and has a memory of about 50–60 ticks.

Nothing contradicts B1–B17. B11 (in-hold recovery) appears again in R3 and R5, at smaller amplitude.

## 4. Score-loss ranking (`loss.py`)

- Loss is Σ over ticks of (1 − 1/(1 + |err|/σ)), in tick-equivalents.
- The new runs have 1,800 observable-ticks and lose **828.7** (score 0.54).
- **Class:**
  - **transient**: a first-wave segment, or > 50% of the loss in the first 15 ticks;
  - **level**: sign-consistent (|mean err| / mean |err| > 0.8) and still present in the last 10 ticks;
  - **dynamics**: everything else.

| # | Run, ticks | Controls | Obs | Lost | % | Bias σ | Last-10 σ | Class | Likely cause |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | R4 40–199 | vaccination 1 | beds | 78.1 | 9.4 | +1.21 | +0.96 | level | B18 (no elderly priority) |
| 2 | R3 100–249 | all .85 | beds | 69.5 | 8.4 | +0.90 | +0.74 | level | B18 |
| 3 | R4 40–199 | vaccination 1 | cases | 66.6 | 8.0 | −0.33 | −1.35 | dynamics | B19: vaccination too strong on cases, wrong oscillation phase |
| 4 | R3 290–399 | recovery | beds | 64.3 | 7.8 | −0.33 | +0.31 | dynamics | B21 wave timing (−4σ then +2σ) |
| 5 | R3 290–399 | recovery | cases | 53.7 | 6.5 | +0.78 | −0.17 | dynamics | B21 |
| 6 | R5 120–199 | closure + mask .7 | cases | 52.9 | 6.4 | +1.97 | +1.90 | level | B20 (mask weakened by fatigue) + B23 |
| 7 | R5 120–199 | closure + mask .7 | beds | 51.7 | 6.2 | +2.09 | +2.61 | level | B20 |
| 8 | R3 100–249 | all .85 | cases | 46.5 | 5.6 | −0.40 | −0.63 | level | B23 plateau (vaccination too strong, B19) |
| 9 | R5 40–119 | closure | cases | 41.4 | 5.0 | −1.40 | +1.16 | dynamics | B22 (the wave falls too early, then the floor is too high) |
| 10 | R4 230–299 | recovery (after vaccination) | beds | 36.4 | 4.4 | +1.13 | +0.59 | level | B18 recovery |
| 11 | R3 250–289 | release | cases | 29.5 | 3.6 | −3.72 | −4.94 | level (transient in origin) | B20/B21 |
| 12 | R4 0–39 | vaccination 1 | cases | 28.8 | 3.5 | −3.32 | −3.44 | transient | B19 first wave |
| 13 | R4 230–299 | recovery | cases | 28.1 | 3.4 | +0.70 | +0.60 | level | B29 phase |
| 14 | R5 40–119 | closure | beds | 25.4 | 3.1 | −0.91 | +0.07 | dynamics | B22 |
| 15 | R5 0–39 | closure | cases | 22.2 | 2.7 | −2.19 | −7.49 | transient | B22 |
| 16 | R3 40–99 | all .85 | beds | 21.9 | 2.6 | +0.52 | +1.33 | dynamics | B18 |
| 17 | R3 0–39 | all .85 | cases | 18.0 | 2.2 | +0.33 | −1.03 | transient | B24 (tick-1 jump) |

**Grouped by cause:**

| Cause | Share of the loss |
|---|---:|
| B18 vaccination → beds (ranks 1, 2, 10, 16 and R4 200–229) | ≈ 27% |
| B20 + B21 release and mask composition (ranks 4, 5, 6, 7, 11 and R3 250–289 beds) | ≈ 33% |
| B19 vaccination → cases (3, 8, 12, 13) | ≈ 20% |
| B22 closure first wave (9, 14, 15) | ≈ 11% |
| Pure first-tick transients | ≈ 2% |

**Level vs dynamics:**

- Level errors (B18, B20, B23) are the ones that scale to 4,000-tick sustained episodes, so fix them first.
- The dynamics errors (B21, B22) matter for recovery and order episodes.

**The same errors in the old data (v1 in-sample, R1+R2, lost 485 of 1,890):**

- The top old loss is **R1 375–434 beds, +1.24σ level: recovery right after vaccination (B18 again)**. Also R1 315–374 beds and R2 10–39 cases (vaccination during the first wave, −1.6σ: B19 again).
- Closure raises beds (R1 225–269 −1.6σ, R2 300–329 −1.6σ) and is under-predicted in both runs. This is not in the new data's top list; it becomes relevant with dsh/severity.
- **B18/B19 were already present in R1/R2.** They were small there because vaccination was short.
- **B20 is new.** R1/R2 never had a mask switch after a long closure-heavy hold except R2 240, where the jump really was smaller (+0.31 at u = 1). That is the point v1's fatigue was fitted to.

## 5. Explanations and minimal model changes, in priority order

**No-refit what-if tests** (`variants.py`, `variants2.py`; v1 parameters, one structural switch, score as cases/beds):

| Variant | R1 | R2 | R3 | R4 | R5 | mean old / new |
|---|---|---|---|---|---|---|
| v1 | .791/.714 | .749/.712 | .592/.533 | .556/.533 | .418/.557 | .742 / .531 |
| elderly-priority doses ×5 | .753/.717 | .754/.689 | .669/.645 | .738/.654 | .418/.557 | .728 / **.613** |
| doses to susceptibles only | .677/.685 | .739/.704 | .412/.462 | .375/.499 | = | worse |
| no fatigue on masks | .746/.695 | **.378/.405** | .346/.369 | = | .502/.643 | conflicts until refit |

**Quick diagnostic refits:**

- Setup: R1–R5, nfev ≤ 300, one restart, Hcap fixed; files `fit_var*.json`.
- These fits include the new runs, so their "new" score is **in-sample**. They are for feasibility, not selection, and none has converged.

| Fit | Structure | Old | New | Notes |
|---|---|---:|---:|---|
| varA | v1 + elderly priority (m1, m3) | 0.731 | 0.703 | pe = 7.4 |
| varA12 | + m2 | 0.689 | 0.715 | pe = 8.8; a_m2 = 0.96, so M2 unused again |
| varB | mask not fatigued (m1, m3) | **0.631** | 0.709 | gF pinned at 1, driven by masks |
| varB_m3v1 | no m1 | **0.609** | 0.721 | pe = 21 |

pe lands at 5–21 in every fit, so elderly priority is robust. Removing mask fatigue costs R2 each time.

**Changes, in priority order:**

1. **B18 + B19 → age-prioritized vaccination.**
   - **Brief:** "vaccination uses a shared clinic workforce"; "age groups differ in ... severity".
   - **Change:** one parameter `pe`. Doses are allocated over groups with weight `(S+W+R)_g × (1, 1, pe)`, and only the S share is effective (v1 has pe = 1).
   - **What it explains:** vaccinating the high-severity, low-activity elderly lowers the H/case ratio a lot and cases little. The ratio recovers as the elderly S refills (waning, ~1/ω ≈ 90 ticks; observed ~60). It also produces the delayed post-stop minimum (B27) without M2.
   - **Conflicts:** none with old data (old 0.742 → 0.728 unrefit, 0.731 refit). It fixes old R1 375–434.
   - **Alternatives:**
     - An M2 lag (a_m2 ≈ 0.1) helps the first wave (peak 457–463 vs 435) but worsens R3 beds. A refit rejects it (a_m2 → 0.96).
     - A shared-workforce referral throttle is contradicted by B27 (no catch-up bump).
   - **What is left:** the first-wave insensitivity to vaccination (B19: data −3%, pe model −8%). Candidates are a clinic ramp-up, an H/Hcap-driven throttle (not just the queue), or the M2 lag. Try `thr = 1/(1 + kH·H/Hcap)` as one bounded term.

2. **B20 → the mask effect must not be scaled by closure-driven fatigue.**
   - **The data:** R3 (250-tick all-three hold) and R5 (120-tick closure) show full mask jumps. The only reduced jump is R2 240 (+0.31 at u = 1). The earlier review already showed that a fatigue-free fit (m23) reproduces that one from state alone.
   - **Minimal change:** apply `fat` to closure only (`me = u_m`). Lesson 4 applies: an effect seen at one switch gets a driver specific to that switch.
   - **Conflict:** the R2 in-hold recovery (15.5 → 89, B11). The quick refits without mask fatigue fall to 0.60–0.63 on the old runs, so a replacement is needed for B11. Candidates, simplest first:
     - (a) Faster susceptible refill: ω and eps free, with the R3 plateau of 61 (with vaccination) and the R2 plateau of 89 as anchors. The pre-registered base_all plateaus (60.3 R3, 82 R2) show the base can do this, but its closure was dead (a_c → 0).
     - (b) Fatigue on closure only, driven by the closure level.
     - (c) Risk-driven relaxation of contacts when cases are low: R2's 15.5 floor is the deepest ever seen. It is bounded, `exp(−g·max(0, 1 − Hm/H*))`.
   - **Decide by a converged refit on R1–R5**, warm-started from m12_all with pe added. Choose on a leave-one-run-out score, not on cost.

3. **B22 → closure displaces contacts (dsh ≈ 1, m12-style) rather than removing them.**
   - This is already in the model family: m12_all has dsh = 1 and wins H4 by 2σ. Start the refit from m12_all (the held-out winner), not m13_all.
   - It also fixes the old closure bed errors via the severity mix.
   - **Conflict:** m12's first wave under all three at .85 is a little high (306 vs 281). The refit must hold both.

4. **B21 follows mostly from 2.** A full mask release jump gives about 12% more growth at once (v1's peak 169 → about 190, data 194). Check it after the refit. If the wave is still too broad, the post-release growth rate (0.035/tick vs 0.029) points to more susceptibles accumulated under the hold, the same ω/eps question as 2a. There is no need for the m3 one-tick release (aout pinned at 1, lesson 9).

5. **B24 reset transient (≤ 2% of the loss).**
   - Add one extra latent stage (E → E2 → I), or start E0 on stage 1 only. This reproduces the 2 flat ticks.
   - A two-stage bed pipeline (P1 → P2) gives the deeper bed dip and the steeper rise to the cap.
   - Low priority; do it only if it is cheap in the refit.

6. **M2 stays unidentified.** Do not choose pairs by M2 until change 1 is in: elderly priority takes over every signature attributed to M2 so far.

## 6. Reserve-step proposal (155 remaining; not spent)

**Still unknown, ranked by scoring impact:**

1. Whether masks fatigue on their own driver. A mask-heavy hold is common in all four categories, and no data have a long mask-only hold from reset. The longest is R1's 65 ticks, with a slow creep of +0.4%/tick.
2. The mask-alone first wave and level from reset: never observed.
3. The first-wave vaccination throttle (B19 remainder).

Pair-fit disagreement is about 1σ for every probe (`screen_reserve.py`). Per §1.3 the choice below is by coverage, not by disagreement.

**Proposed run R6: one fresh reset, 155 steps, all spent.**

| Ticks | Action | Steps |
|---|---|---:|
| 0–119 | mask_mandate 0.85, school_closure 0, vaccination_rate 0 | 120 |
| 120–154 | recovery (all 0) | 35 |

```sh
python run_schedule.py --budget epidemic      # free; expect 155
# segments: [{"steps":40,"action":M85},{"steps":80,"action":M85},{"steps":35,"action":REC}]
python run_schedule.py --system epidemic --output data/epidemic/R6.json \
    --segments fits/round2/segments/epidemic_EP4.json --confirm 155
```

The segment file `epidemic_EP4.json` still has to be written. Split the 120-tick hold 40 + 80 so that `settle` can be checked after tick 40.

**Screened predictions at initial 170/45** (cases, beds; last 10 ticks):

| Tick | v1 | varA | varA12 | varB |
|---|---|---|---|---|
| 120 | 42, 36 | 39, 34 | 47, 42 | 42, 38 |
| 155 | 145, 60 | 142, 58 | 142, 65 | 135, 62 |

**What each outcome decides:**

- **Release jump at 120** (6-tick log jump, as in `jumps.py`):
  - **≥ +0.29** (the full .85 effect): no mask fatigue. Take change 2 (`me = u_m`) and solve B11 with 2a/2b/2c.
  - **≤ +0.22**: mask-driven fatigue is real. Keep fatigue on masks with a mask driver (mix → 0), and explain R3's full jump by the vaccination/closure state.
- **Slope over ticks 60–119 under the mask:**
  - creeping up ≥ 1%/tick while cases are low: susceptible refill or relaxation (2a/2c);
  - flat: the level is set by the restriction.
- **First-wave peak and timing under mask .85 from reset:** a direct check of the mask first-wave gain (m13 vs m12 predict a peak about 5–8% apart). It covers the most common single-control first wave.
- **Level at ticks 110–119:** the first mask-alone restricted level (the candidates give 39–47, 1σ apart).

**Fallback if the modeler wants to keep a settle reserve:** use 90 + 30 = 120 steps and hold 35 back. The fatigue test needs at least about 90 ticks of mask exposure (a_m1 ≈ 0.045 means about 98% of F is built by tick 90).

Do not spend steps on the vaccination questions. The pe change is well identified from R1, R3 and R4 already, and a vaccination probe would need the endemic phase (≥ 90 ticks from reset) before it could separate anything.

---

**Files** (all under `toronto26-participant-kit/fits/epidemic/round2/`):

- Analysis scripts:
  - `common.py`
  - `overview.py`
  - `series.py`
  - `cands.py`
  - `loss.py`
  - `ratio.py`
  - `jumps.py`
  - `misc.py`
  - `cum.py`
  - `fw.py`
  - `plots.py`
- What-if tests:
  - `epi_variant.py`, `epi_varA.py`, `epi_varB.py` (scratch copies of the model with switches)
  - `variants.py`, `variants2.py`
- Diagnostic fits: `fit_var*.json` and `fit_var*.log`.
- Reserve screen: `screen_reserve.py`.
- Plots: `R1_v1.png` to `R5_v1.png`.
