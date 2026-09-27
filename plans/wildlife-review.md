# Wildlife review (Phase B)

Reviewer, 2026-09-27. No simulator steps were spent. The only gateway call was the free budget read (1,060 remaining, so 940 of the 1,000 CAP are spent and 60 are left in reserve).
Review scripts and plots are in `toronto26-participant-kit/fits/wildlife/review/`:
- `raw_plot.py` makes `R1_raw.png` and `R2_raw.png`. These plot the raw data plus the N/S ratios.
- `nums.py` and `nums2.py` produce the numbers below.
- `errs.py` makes `pair_errors_sigma.png`: the errors of the three quick joint fits, in units of score σ = 0.1×std, which is 4.4 / 0.057 / 4.0 / 0.055. It also prints per-segment scores.
- `stability.py` runs 4,000-step constant-control and random runs.
- `settle_probe.py` checks what settlement competition costs on the current data.
- `reserve_screen.py` makes `reserve_screen.png`, which screens the candidate reserve schedules.

## 1. Independent behaviour list (written before reading the plan)

| ID | Behaviour | Evidence |
|---|---|---|
| R1 | **Reset boom.** Prey rise almost linearly: N gains about 6 per tick and S about 4.5. The boom peaks at N ≈ 196 and S ≈ 158–160 at ticks 18–24, then plateaus for about 5 ticks and falls abruptly to 121/97 by about tick 60. The peak height does not depend on the initial reading: N started at 72.7 in one run and 94.7 in the other, and S at 98 and 74. | R1/R2 ticks 0–60, `R*_raw.png` |
| R2 | **The predator reset transient is affine in (Y0 − Yeq).** Take (Y − 2.2)/(Y0 − 2.2). At t = 30 it is 0.233, 0.221, 0.224 and 0.240 for R1N, R1S, R2N and R2S, although Y0 ranges from 8.2 to 13.1. At t = 60 it is 0.104, 0.102, 0.118 and 0.114. The initial fractional decline is about 5% per tick in all four series, whatever Y0 is, and the rate of decline falls with time since reset rather than with level. This looks like a linear relaxation with two timescales (about 20 and 50 ticks), not a density-dependent decay. | `nums` output, R1/R2 0–120 |
| R3 | **Slow predator tail.** Under the same recovery action, predators read 2.5 at t = 119 but about 2.28 from t ≈ 320 to 540. | R1 segment table |
| R4 | **Hunting 7.** The response is immediate, with a first-tick drop of about 7 per region. Prey fall to N 25.5 and S 11.4, settled only after about 100 ticks (R1 was still drifting at 65 ticks). | R1 120–184, R2 200–399 |
| R5 | **Hunting is strongly nonlinear.** A quota of 3.5 lowers prey by 30% (N) and 36% (S). A quota of 7 lowers them by 79% and 88%. | R1 440–489 |
| R6 | **Release after deep depletion.** Regrowth is additive, at about +5 per tick from 29 (N) and 12 (S). About 18 ticks after release, both regions stall (N 124 → 147 slowly, S 98 → 103). A second rise then reaches a sharp peak of 170/156 at 34–38 ticks after release, followed by a crash to about 125/100 within about 15 ticks. There is no overshoot after hunting 3.5 or after a habitat pulse. | R1 185–250 |
| R7 | **Habitat 0.1.** N falls 45% and S falls 35%. On and off are symmetric and there is no overshoot. The habitat level of about 66 is reached from above and below. Predators do not change. | R1 250–330, R2 30, 130 |
| R8 | **Corridor open.** All four totals fall within about 12 ticks and then plateau: prey N by 10%, prey S by 22%, predators by 26%. **When it closes**, arrivals start within 2–3 ticks and overshoot (N +15%, S +12%, predators +16%). The return takes τ ≈ 100 ticks, which is **much slower** than the roughly 15-tick crash after the hunting overshoot. | R1 330–440 |
| R9 | **Habitat restored while hunting 7 continues.** N bumps from 21 to 38 over about 20 ticks, then slides to 25.5 over about 100 ticks: a slow component under hunting. | R2 196–300 |
| R10 | **Predators fall under hunting** (2.3 → 1.9, with a 5–8 tick lag). They do **not** fall when habitat lowers prey to 66. | R1, R2 |
| R11 | **Predators N ≈ S.** The N/S ratio converges from 0.83 or 1.2 to about 1.02 within about 100 ticks, although the prey differ. | `R2_raw.png` ratio panel |
| R12 | **Noise is about 0.45% of level** for all four observables in flat windows, so it is proportional. | `nums` output (flat windows) |

## 2. Comparison with the catalogue (B1–B15) and the current best fit

The fit evidence is `pair_errors_sigma.png` and the per-segment scores of `m12_all_quick`, the best pair on both runs (R1 0.581, R2 0.590).

| Behaviour | Catalogue | Model component | Verdict (fit evidence) |
|---|---|---|---|
| R1 reset boom | B1 | food stock F0 plus nursery cap | **Partly captured.** The peak comes out at 160–170 instead of 196. Reset segments score 0.375 (R1) and 0.384 (R2). |
| R2 affine predator transient | B8, which only says "decays slowly" | `dY2·Y²` density dependence | **Not captured.** In the model the decline rate is ∝ Y, so it decays too fast from 13.8 (−25σ at t ≈ 5–30 in R1 N) and too slow from 8.5 (+7σ in R2 N). The reset predator scores are 0.10 (R1 N) and 0.24 (R2 N). |
| R3 slow predator tail | — | none | **Not captured**: there are ±2–4σ drifts through both runs. |
| R4 / R5 hunting level and nonlinearity | B5 | `7u·ex·X/(X+Xh)` | **Captured.** Hunt-hold segments score 0.63–0.8. |
| R6 release overshoot and stall | B2, B3, B4 | food stock plus nursery cap | **Partly captured.** The peak comes out at about 140 instead of 172, and the stall is missing. R1 185–250 scores 0.469, the worst non-reset segment. |
| R7 habitat | B6, B11 | habitat scales food renewal | **Captured** in general. However, R1 250–290 prey N scores only 0.30 and R2 130–155 scores 0.29 (the model overshoots to 90). |
| R8 corridor dip and slow overshoot tail | B7 | transit pipeline; the overshoot comes from the food stock | **Partly captured.** The dip is fitted, but prey N scores 0.29 during the open hold, and the tail is 5σ too high at 360–400. The slow τ ≈ 100 has no dedicated state. |
| R9 slow component under hunting | B13 | none | **Not captured** (R2 200–260, prey N 0.67, predators 0.45–0.48). |
| R10 predators respond to hunting, not to habitat | B8, B15 | m1 `g1` with a_m1 → 1: hunting cuts exposure, so predators starve | **Captured, but by the wrong component.** A patch "mechanism" module is doing base predator work (see G1). |
| R11 predators N ≈ S | B9 | shared predator parameters | **Captured.** |
| R12 proportional noise | B10 | log units | **Captured.** |
| — | B12 (open corridor slows habitat recovery, more in the S) | per-region `mvX` | **Captured** (R2 155–180 scores 0.52; prey N 0.41). |
| — | B14 (predators rise in the joint pulse) | transit arrivals | **Partly captured.** R2 180–200 scores 0.39, the worst R2 segment. |

## 3. Coverage and separating probes (§4.2, §6.2 item 3)

- **Covered:** P0 in each run, P1 for all three controls, P2 for hunting, P6 order swap (R2 30–79 against 105–154), P7 of 200 steps (hunting 7), and both P9s.
- **Weak coverage:**
  - P3 lasted only 20 ticks and never settled: prey N was still falling by about 1 per tick at t = 199.
  - P9a compares pulses that don't match: 40 ticks from 123 against 25 ticks from 52.
  - P9b and P6 were evaluated only qualitatively. No pair was scored on either contrast.
- **Missing:**
  - No P5 gap test.
  - No joint pulse of hunting and corridor, habitat and corridor, or all three controls.
  - No mid levels of habitat or corridor.
  - No over-pulse values (hunting 8, protection 0).
- **Separating probes:** every pair has a probe that was run. The m1/m3 separation (m12 against m23) was ≤ 0.9σ by design and was never resolved.

## 4. Theses: missed drivers and structure

- **The mechanism triple is probably wrong (G1).** In every other brief, the sentence listing three "may…" or competition clauses is the mechanism list:
  - epidemic: "Behavior, developing immunity and postponed gatherings…";
  - market: "Inventory may tie up funding…, adverse price moves…, investors may shift…".
  For wildlife, that sentence is "Food renewal shares a finite resource, young animals compete for nursery food, and arrivals compete for settlement space." Patch occupancy is base structure, like market's producer/consumer groups. The "Regional totals alone do not identify…" line is the partial-observability sentence, like market's "Reported depth is an aggregate".
  The plan chose {patch, juvenile, transit} and put food renewal in the always-on base. That makes the pair comparison test the wrong things. It also means that dropping m1 in any pair would remove the predator response to hunting (R10).
- **Settlement driver:** m3 throttles predator arrivals by *prey* density and deletes unsettled arrivals. Two alternatives were not considered:
  - arrivals that cannot settle *wait* (a queue), which would produce R8's slow tail;
  - predator settlement depends on predator density.
- **Juvenile reset:** `J0 = j0·X0` contradicts R1, whose boom does not depend on X0. Use a fixed J0.
- **Juvenile delay:** with a_m2 → 1 and NJ = 3, the delay is only 3 ticks. The stall about 18 ticks after release (and at t ≈ 12 after reset) points to a cohort delay of roughly 15–20 ticks that the pipeline, as parameterised, cannot represent.
- **Time since reset:** the predator transient (R2) and the slow tail (R3) are deterministic hidden states starting from the reset reference. They are not modelled as such.

## 5. Stability over 4,000 steps (`stability.py`)

- All pairs stay finite under 3 random 4,000-step schedules and under 90 constant settings. A run takes 0.04 s per 4,000-step episode, so timing is no concern.
- **Extinction and limit cycles:**
  - m12 and m13 drive prey to the 0.01 clamp at hunting ≥ 7 with protection ≤ 0.4.
  - Both show sustained boom–bust cycles at (hunting 7, protection 0.7, corridor 0.5 or 1). In m12 the tail range is 5× the mean.
  - Predators fall to 0.13–0.48 in random schedules.
  - None of these regimes was ever observed.
- **Pinned parameters** (`m12_all_quick`):
  - `eY` = 1 and `dY` = 0.
  - `Xp` = 1.1, so predation does not depend on prey.
  - `a_m1` ≈ 1 and `a_m2` = 1.
  - `cS` = 0.
  - `F0` = 0.99 and `kF` = 0.018. `kF` near zero means step-like intake, which drives the limit cycles.

## 6. Gaps

| # | Severity | Gap | Evidence | Fix / test |
|---|---|---|---|---|
| G1 | **high** | The mechanism triple is mislabeled, and pairs are compared across the wrong modules. | §4: brief sentence pattern. The food stock sits in the base while m1 does base predator work. | Rebuild with base = regions, patches as exposure, transit, predators, and a hunting→exposure term. The modules become **mA food renewal**, **mB nursery competition** and **mC settlement competition**. For mA off, use a fixed carrying-capacity or logistic prey term with no food stock; test whether mB+mC can reproduce R1 and R6 at all. Refit mA+mB, mA+mC and mB+mC, then run the cross-run test and the bootstrap. The current evidence already leans towards mA+mB: `settle_probe.py` shows the joint cost rising from 28.8k to 31.7k, 35.9k and 39.7k at cS = 0.3, 1 and 3 even after refitting the corridor parameters, and m13, which has no nursery cap, costs 34.5k against 28.8k. Offline, 0 steps. |
| G2 | **high** | The predator block is mis-structured. Predators are half the observables, with σ ≈ 0.057, so a 0.1 error scores 0.36 per tick. | R2 affine transient; −25σ and +7σ reset errors; predator segment scores of 0.10–0.8; pinned `eY`, `dY` and `Xp`. | Replace `dY2·Y²` with a linear two-state predator block. Y relaxes at a rate of about 0.05 towards a target set by a hidden reserve Z (τ about 50). Z starts at a fixed fraction of Y0 (the reset rule allows this) and relaxes towards Y*(prey, hunting exposure, corridor). Fit it on R1 and R2 ticks 0–120 alone before the joint fit. Add a slow state for R3. |
| G3 | **high** | Joint pulses were never observed, although the model extrapolates to extinction or limit cycles there. Recovery scenarios pulse **all three controls at once** (u 0.7–1 each), and the joint category is ¼ of the score. | §5. P3 lasted 20 ticks and never settled. No corridor joint of any kind was run. | **Spend the reserve** on the joint-pulse probe (§7). In the model, keep prey and predators above a floor: fit a small refuge term, for example harvest and predation acting only on `X − Xref` with Xref about 1–5, so extrapolation can't produce extinction. Also floor `kF` at 0.05 or more. |
| G4 | medium-high | The release overshoot is too small (140 instead of 172) and the ~18-tick stall is missing. This recurs in every recovery-spacing episode. | R6; R1 185–250 scores 0.47. | Give mB a real cohort delay: NJ of about 6, a_m2 bounded to 0.2–0.5, and a fixed J0. Alternatively, give the nursery its own food stock, separate from adult food. Check the peak height and timing on R1 185–250 and R2 80–105. |
| G5 | medium | The juvenile reset `J0 = j0·X0` contradicts the boom's independence of X0. | R1 (the peak at 196 is the same for X0 = 72.7 and 94.7). | Make J0 a fixed constant and F0 a fixed constant. |
| G6 | medium | The slow post-corridor tail (τ ≈ 100) is attributed to food, and m3's form is questionable: it deletes unsettled arrivals and uses prey density for predators. | R8; tail +5σ at 360–400. | Make settlement a waiting queue: arrivals settle at a rate ∝ free space, and the rest stay in transit. Use predator density for predators. Test within G1. |
| G7 | medium | The slow component under hunting and the slow predator tail are not modelled. | R3, R9 / B13. | One slow shared state per region, for example food with two pools or the predator reserve Z from G2. Check on R2 200–300. |
| G8 | low | The quick fits are unconverged (400 nfev), and many parameters are pinned. | §5. | Run final fits with 3 restarts and full nfev after G1 and G2. Add a gate: in 4,000-step constant-action runs, the tail range must stay below 10% of the mean. |
| G9 | low | The P9a and P9b contrasts were evaluated only qualitatively. | §3. | Report each pair's predicted-minus-observed difference on R2 155–179 against R1 290–314, and on the order A and order B segments. |
| G10 | low | There are no mid levels of habitat or corridor and no over-pulse values. The model's `u` clamp at 1.2 covers the bounds. | §3. | Accept this. The joint probe below adds non-pulse levels. |

## 7. Reserve recommendation (60 steps)

**Spend the reserve, but on neither pure P5 nor a pure settlement probe.** Use a **sustained joint reference-type pulse followed by release** (G3). The reasons:

1. The joint pulse is the regime that the recovery and joint scoring categories are built from, half the score in all, and it has never been observed. The fitted models predict prey extinction or limit cycles there.
2. It includes the corridor at low density, which is a settlement-competition condition not seen before: prey were at 120 in R1 and at 66–100 in R2.
3. The release shows how prey regrow from very low numbers, after food has been drawn down by the habitat cut:
   - exponential regrowth from adults means food limits it (mA);
   - additive regrowth of about 5 per tick means the nursery cap limits it (mB).
   This is the spacing memory that P5 would probe.

Screening against the three quick fits (`reserve_screen.py`) gives the mean |pair difference| in units of σ:

| Schedule | Mean pair difference (σ) |
|---|---|
| Joint probe (recommended) | 1.4–2.7 on prey, 0.75 on predators |
| Pure settlement continuation (corridor + hunting 30, then hunting 30) | 0.04–0.7 on prey |
| Researcher's P5 continuation | 2.1–3.1 on prey |

P5 screens slightly higher than the joint probe. However, P5 targets the patch-sheltering thesis, which G1 argues is not a candidate mechanism, and it covers only hunting. **If the orchestrator wants one of the two named probes, choose P5 over the settlement probe.** The settlement probe separates weakly, and the existing data already penalise cS.

**Exact schedule.** Continue R2, which ended settled under hunting 7. Work on a copy so that R2.json stays unchanged for the existing fits. Run from `toronto26-participant-kit/`:

```sh
cp data/wildlife/R2.json data/wildlife/R2c.json
python run_schedule.py --continue data/wildlife/R2c.json --confirm 60 --segments '[{"steps": 35, "action": {"hunting_quota": 6.0, "habitat_protection": 0.25, "corridor_access": 0.9}}, {"steps": 25, "action": {"hunting_quota": 0.0, "habitat_protection": 1.0, "corridor_access": 0.0}}]'
```

The joint pulse sets hunting at u = 0.86, habitat at u = 0.83 and corridor at 0.9, which is inside the scoring's recovery range. The release is to the reference recovery action.

**Fallback.** If the first continued step fails because the run expired, a failed step should not be charged, but check `--budget` to confirm. Then delete `R2c.json` and start a new run with the same segments. The R1/R2 reset booms serve as the control: their hidden reset state is deterministic and the peak does not depend on the initial prey. This measures the joint pulse at high density.

```sh
python run_schedule.py --system wildlife --output data/wildlife/R3.json --confirm 60 --segments '<same JSON as above>'
```

**P5 alternative**, if chosen instead. This is the researcher's schedule: a continuation of R2 on the copy, 60 steps:

```json
[{"steps":20,"action":{"hunting_quota":0.0,"habitat_protection":1.0,"corridor_access":0.0}},{"steps":10,"action":{"hunting_quota":7.0,"habitat_protection":1.0,"corridor_access":0.0}},{"steps":10,"action":{"hunting_quota":0.0,"habitat_protection":1.0,"corridor_access":0.0}},{"steps":10,"action":{"hunting_quota":7.0,"habitat_protection":1.0,"corridor_access":0.0}},{"steps":10,"action":{"hunting_quota":0.0,"habitat_protection":1.0,"corridor_access":0.0}}]
```

G1, G2 and G4 to G9 need no steps. They are the bigger score levers: predators are half the metric.
