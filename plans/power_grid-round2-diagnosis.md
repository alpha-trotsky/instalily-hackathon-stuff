# power_grid round 2: diagnosis of R3 (PG1) and R4 (PG2)

Diagnostician pass, 2026-09-28. **No simulator steps were spent.** v1 = `fits/round2/v1_models/power_grid` (m1+m3, identical to `greybox/power_grid_model.py`). Paths are under `toronto26-participant-kit/`. Scripts and plots are in `fits/power_grid/round2/`:

| File | Content |
|---|---|
| `analyze.py` → `R3_v1.png`, `R4_v1.png`, `R3_err.png`, `R4_err.png`, `segments.json` | data vs v1 per observable plus controls; error in score σ; last-10 table |
| `rank.py` → `loss_rank.json` | score loss per (segment, observable), all four runs |
| `quant.py`, `ring.py` | H3 drift, share ladder and chatter, reset transients, ringing peaks |
| `fstatic.py`, `sstatic.py` | static maps for frequency and share (fit on old data, test on new) |
| `fmap.py` | v1 steady-state level map |
| `R3_battery.json/.out`, `R4_battery.json/.out`, `R3_r0_battery.png`, `R4_r0_battery.png` | standard battery |

Score σ (0.1 × std after tick 20, all data): load 2.18, frequency 0.0747, share 0.0152. v1 held-out scores (load / f / share): R3 0.370 / 0.228 / 0.472, R4 0.387 / 0.265 / 0.670 (mean 0.399). v1 in-sample on old data is R1 0.467 / 0.421 / 0.682 and R2c 0.490 / 0.408 / 0.763.

## 1. Summary

1. **Mechanism rules:** H1 and H4 pick the m1 family over m23: load after the joint-1 release is 67.4 against 69 (m13) and 85 (m23). H3 finds no M2 fade in a 200-tick charging-0 dispatch (drift 0.04σ), so M2 stays off. H2 **rejects** the `1/(1+w·Rd)` share form. Renewable power collapses to a floor by reserve 40 and then barely moves.
2. **The largest loss is frequency level under reserve.** v1's governor and secondary loop cancel most of the steady-state surplus that reserve creates, but the data keep it: f = 51.02 / 51.15 / 51.66 at reserve 40 / 80 / 120, against v1's 50.10 / 50.37 / 50.96 (−9 to −12σ). The joint pulses give 50.83 / 50.47 / 50.11 at u = 0.7 / 0.85 / 1, against v1's flat 50.1–50.3. A **static map** f = a − 0.026·(L−100) + g(reserve) − h(interconnector) fitted on *old data only* scores 0.39 / 0.42 on R3 / R4 frequency, against v1's 0.23 / 0.27.
3. **The second loss is load ringing.** It is saturating, not linear. Every off-step trough is 63–65 whatever the step size (Δu 0.7–1.0, five cases), and every on-step peak is 162–171. The period drifts within a single ringing (at price 0 the first half-period is 33 ticks, the next 13–18), and the joint-1 hold rings irregularly for 200 ticks. v1's linear resonator under-shoots the peaks by 12–16 and damps too fast.
4. **Share is mostly right,** except for mid-reserve levels (chatter at r = 40), release spikes (+0.05–0.1 for 20–30 ticks) and a +2σ shortfall after pulses. It is the best channel (0.47 / 0.67).
5. **Loss by kind:** in the new runs, 1,327 of 1,589 tick-units classify as level (84%), 250 as dynamics and 12 as transient. Some of the "level" losses in short segments (under 100 ticks) are ringing-phase errors. The frequency level error under reserve and the load ringing already existed in the old data (R2c joint-pulse f +2.0σ, R1/R2 ringing), but the mid-reserve and joint-0.7 frequency error (−10σ) is **new-regime extrapolation**.

## 2. Decision-rule verdicts

Measured value = mean of the last 10 ticks of the segment. The m13 / m1 / m12 fits are within 0.01 of each other everywhere, so "m1 family" covers all three. Errors are in score σ.

| Rule | Quantity | Data | m1 family (m13) | m23 | Verdict |
|---|---|---:|---:|---:|---|
| **H1** price 2.0 from reset (R3 0–69) | load | 92.6 (still ringing; R3 − R1 at ticks 50–69 is −4.6, so the long-run level is ≈ 90 ± 3) | 96.7 (+1.9σ) | 83.7 (−4.1σ) | **m1 family.** m23 rejected. Both miss: the settled price-2 level is ≈ 3–5 below recovery, not the linear 84 of v1's long-run map (`fmap.py`: v1 steady 84.2). |
| H1 | frequency / share | 50.32 / 0.351 | 50.0 / 0.352 | 50.3 / 0.382 | frequency favours m23 and share favours m13. The load rule governs. |
| **H4** rebound after joint 1 × 200 (R4 360–389) | load | 67.4 (trough 63.8) | 69.3 (+0.9σ) | 85.3 (+8.2σ) | **m1 family** (8σ separation, as pre-registered) |
| H4 | frequency / share | 50.87 / 0.429 | 51.0 / 0.396 | 50.6 / 0.401 | m1 family closer on frequency. Both 2σ low on share. |
| **H2** share vs reserve ladder (R3 200–289) | share at 40 / 80 / 120 | 0.186 (mean; **median 0.122**, chatter) / 0.093 / 0.074 | 0.170 / 0.119 / 0.090 | 0.183 / 0.122 / 0.092 | **Replace `1/(1+w·Rd)`.** Renewable power S·L falls from 36.8 (r = 0) to 10.7 / 9.2 / 7.4 / 7.2 at r = 40 / 80 / 120 / 150. That is a steep drop and then a floor, which is the "linear with a clip" branch of the rule. |
| **H3** M2 loophole: drift in run ticks 250–359 of the joint-1 hold (R4) | share / frequency, load-corrected linear trend | +0.0004 (0.03σ) / +0.003 Hz (0.04σ) | flat | flat | **No M2** (threshold 2σ). Caveat: share sits on its floor above r ≈ 80, so only frequency can see a fade, and frequency saturates above r ≈ 120. The bound is therefore "delivered reserve stayed ≳ 120 of 150 for 200 ticks at charging 0". |
| **Frequency gain** f at reserve 120 (R3 260–289) | frequency | **51.66** | 51.0 (−8.8σ) | 51.3 (−4.8σ) | Gain ≈ 0.0145 Hz per reserve unit at L = 100, near-linear from 0 to 120, saturating at 51.76 at 150 (R2c). v1's reserve→frequency map is convex and far too low at mid levels. |

Other pre-registered cells (`final_power_grid.out`):

| Run / segment | Data (L, f, S) | m13 | m23 |
|---|---|---|---|
| R3 p .45 | 117.6, 49.45, .338 (ringing) | 114, 49.7, .345 | 116, 49.6, .353 |
| R3 p 1.5 | 117.9, 49.34, .322 (ringing peak) | 101, 49.9, .349 | 95 |
| R3 r80 + x .5 | 95.0, 51.10, .064 | 93.9, 50.3, .093 | 93.1, 50.2, .093 |
| R3 x .5 | 93.6, 49.58, .296 | 94.6, 49.9, .287 | 94.2, 49.9, .300 |
| R3 recovery | 94.6, 50.12, .391 | 94.8, 50.2, .377 | 94.8, 50.1, .379 |
| R4 joint .7 | 120.4, **50.83**, .060 | 117, 50.1, .072 | 115, 50.1, .067 |
| R4 rec 60 | 100.8, 49.92, .388 | 105, 49.8, .347 | 94.3, 50.1, .371 |
| R4 joint 1 × 200 | 126.7, 50.11, .050 | 125, 50.3, .046 | 125, 50.2, .036 |
| R4 joint .85 | 124.2, 50.47, .055 | 123, 50.1, .058 | 119, 50.1, .050 |
| R4 rec 40 | 82.2, 50.49, .424 | 86.1, 50.4, .399 | 91.6, 50.2, .381 |

**Mechanism reading.** M1 is confirmed again. M2 is excluded a third time (H3 plus the R2c charging A/B plus the B14 nulls), which leaves m1+m3 as shipped. As before, M3 has no positive signature of its own in R3/R4. Every candidate shares the same base errors, which is where the score is lost (§4).

## 3. Behaviour catalogue (continues B1–B17 of `plans/power_grid-plan.md`)

Categories: **S** = sustained, **O** = action order, **R** = recovery history, **C** = composition.

| ID | Behaviour | Evidence | v1 status (error in score σ) | Categories |
|---|---|---|---|---|
| B18 | **Reset transient under control is deterministic and large.** Price 2 from reset: load 86.5 → trough 58.0 (t16) → peak 98.5 (t50). Joint .7 from reset: load 120.5 → **131.2 (t13)** → 110.1 (t41) → 118–120. Frequency rises to 51.36 (R3, t20) and 51.3 (R4, t1–3). Share under joint .7: 0.084 → 0.059 (t9) → 0.061 flat (onset undershoot, as in B8/R4). | `quant.py`; `R3_v1.png`, `R4_v1.png` | Partly. R3 load trough too deep (53.9 vs 58). R4 misses the fast rise (108 → 120 vs 120 → 131: −5σ for 15 ticks). R4 frequency −5 to −10σ from tick 0. | all (every episode) |
| B19 | **Tick-0 load bias.** v1 is 8–12 load units low at tick 0 in all four runs (R1 −8.2, R2 −9.6, R3 −10.4, R4 −12.3). Data: tick-0 load ≈ L0 + wLi·Δup ± 5, keeping about 85% of the initial reading (R1 vs R2). v1's `Lref0` = 118 drags it down. | `quant.py` reset table | Not captured: −4 to −6σ at tick 0, decaying over about 20 ticks | all (≈ 0.5% of ticks) |
| B20 | **Load ringing saturates: floor ≈ 64, ceiling ≈ 170.** Off-step troughs: 64.1 (R1 p0→1.5), 63.7 (R3 .45→1.5), 64.8 / 63.8 / 63.4 (R4 releases from joint .7 / 1 / .85, Δu 0.7–1.0). On-step peaks: 168.9 (p0), 162.4 (2→.45), 171.4 (joint 1), 166.4 (joint .85). Trough depth and peak height do **not** scale with Δu. The exception is the reset to price 2 (trough 58), where the non-thermostatic base is also lower. | `ring.py` | Not captured. v1 scales linearly: troughs 71.5 / 63.3 / 74.9 (up to +5σ), peaks 146–156 (−5 to −7σ at peaks) | R, O, S |
| B21 | **Ringing period and shape are not those of a single linear mode.** At p0 the half-periods are 33 then 18 then 13 ticks (R1 133→166→184→197). At p .45 the period is ≈ 58, at 1.5 after .45 it is ≈ 64, and at 1.5 after 0 it is ≈ 85 (R1). The joint-1 hold rings **irregularly for 200 ticks** (171, 110, 127, 118, 134, 119, 130) with beats. After .45→1.5 the rebound (+29 above settle) is almost as large as the drop (−31). | `ring.py`, `R4_v1.png` 160–360 | Not captured. v1 has period ≈ 70–80 with smooth decay. R4 joint-1 load loss 122 tick-units (0.61/tick) with a −0.5σ level, so the loss is purely dynamics. | S, O, R |
| B22 | **Settled price 2.0 load ≈ 90 ± 3,** only 3–5 below recovery (94.6). The price→load map flattens above 1.5. | R3 − R1 at matched ticks | Not captured: v1's long-run map gives 84.2 at price 2 (≈ −3σ if held) | S (any episode that uses price > 1.5) |
| B23 | **Frequency keeps a steady offset proportional to reserve** (no integral restoration). At L = 100 the offset is +0.5 / +1.15 / +1.7 / +1.8 Hz at r = 40 / 80 / 120 / 150. The response is instant (k ≈ 0.9/tick) and settles in 16–17 ticks. | R3 200–289, R2c 400–449 | **Not captured**: −9 to −12σ for every reserve tick at r ≤ 120. v1 is right only at r = 150 (clip). | S, C, R |
| B24 | **Frequency is a near-static map of load and controls.** Fit on all data: f ≈ 50.01 − 0.026·(L−100) − 0.015·(L(t−2) − L) + 1.84·min(r,120)/150 + 0.31·[r > 0] − 0.20·(1−x) − 0.63·(1−x)² − 0.51·(r/150)(1−x) − 0.02·(1−ch). Fit on old data only and applied to new data with observed load, it scores 0.387 (R3) and 0.417 (R4), against v1's 0.221 / 0.268. The load coefficient in steady state is −0.026 to −0.031 Hz per unit (p0 vs recovery), against v1's effective −0.019. | `fstatic.py` | Not captured: v1's governor (kg ≈ 1) and secondary loop (kz pinned at 1) restore too much. Frequency level errors of ±2–4σ follow in every price segment. | all |
| B25 | **The interconnector's frequency effect depends on the background.** Alone, x = .5 gives −0.54 Hz and x = .2 gives about −0.8 Hz. Under reserve 80 at L ≈ 95, x = .5 gives only −0.22 Hz. In the joint pulses, the frequency deficit relative to the x = 1 reserve map (load-corrected) is ≈ 0 / −0.44 / −0.7 Hz at u = .7 / .85 / 1. This is confounded between x, the load level and charging, though charging was shown inert at r = 150, x = 1, p = 1.5 (R2c). | R3 290–349, R4 joints | Not captured: R4 joint .7 −11.3σ, joint .85 −3.8σ, joint 1 +3.3σ (all for 80–200 ticks) | **C**, S |
| B26 | **Renewable power under reserve sits on a floor.** S·L ≈ 10.7 / 9.2 / 7.4 / 7.2 at r = 40 / 80 / 120 / 150 with x = 1, and ≈ 6.1–7.1 with x ≤ .5 (r = 80–150). It is independent of load between 89 and 126, so share ≈ floor / L. Without reserve, S·L ≈ 36.4 + 0.277·(L−100) − 12·(1−x) − 9·(1−x)² (R6 confirmed). | `sstatic.py` | Partly: at r = 40 / 80 / 120 v1 is +3σ / +1.7σ / +1.0σ (v1 0.17 / 0.12 / 0.09). The joint pulses are within 1σ. | S, C |
| B27 | **Curtailment chatter at r = 40** (and 2 spikes at r = 80). Curtailment starts **5 ticks late** (share 0.24–0.25 until f passes ≈ 51.0, then 0.117). After that, share toggles 0.12 ↔ 0.28 on 7 of 25 ticks, and frequency chatters ±0.1 Hz. The pattern looks like a frequency-triggered (≈ 50.9–51.0 Hz), one-tick-lagged curtailment switch at the margin. | `quant.py` series | Not captured (v1 is smooth). Best score-wise: forecast the low state (median 0.122). | S, C (only when reserve is low, which the scorer rarely uses) |
| B28 | **Share release spike depends on the prior surplus.** After R4 joint .7 (f 50.83) share reaches 0.474 and decays to 0.39 over about 30 ticks. After R3 r80 x .5 (f 51.1) it reaches 0.36 and decays to 0.295 over about 20 ticks. After R4 joint 1 (f 50.1) there is no spike, but the level sits 0.02–0.03 above the static map for 30 ticks. | `R4_v1.png` 100–130, 360–390 | Partly: v1's spike is too small and too short (−7σ at the R4 t100 release, −2 to −4σ over R4 360–389) | R, O |
| B29 | **No M2 depletion over 200 ticks** of joint-1 dispatch at charging 0 (H3). The share floor makes share blind to a fade down to ≈ 80. | §2 | Consistent (M2 off) | S |
| B30 | **Load under mid reserve is ≈ +4–6 above recovery** (R3 r80/120: 98.5–100.5 vs 94.6), and drops by 5 when frequency falls 0.6 Hz at t290. This could be load–frequency coupling (≈ 3–8 load units per Hz), but the implied slopes are inconsistent (1–8 per Hz). Joint-pulse loads are already right in v1 (−0.5σ to −1.3σ). | R3 230–320 | Open (≤ 2.5σ over about 90 ticks) | C |
| B31 | **Noise σ:** load 0.094–0.109 (≈ 0.1%, proportional), frequency 0.018–0.019, share 0.00033–0.00035. Unchanged from B17. | battery | — | — |
| B32 | **Settling.** The load ringing is not settled in any hold shorter than about 150 ticks at a new price (settle check: R3 70–140, 140–200, 230–380 and R4 360–510 all "not settled"). Only the 200-tick joint-1 hold and the 60-tick rec after joint .7 pass. Frequency and share settle in 8–17 ticks after reserve and interconnector steps. Every response has zero delay, except the r = 40 curtailment (5 ticks, B27). | settle output | — | S |
| B33 | **Step asymmetry (price),** measured from the settled level. On, the peak overshoot is ≈ 2× the settled change (2→.45: +47 over 115, log 0.34). Off, it is ≈ 1.5× (.45→1.5: −31 from 94.6, log −0.40). The asymmetry is small in both units once the floor/ceiling saturation (B20) is accounted for. | `ring.py` | Partly (v1 is symmetric and linear) | O, R |

## 4. Score-loss ranking

Loss = Σ over ticks of (1 − 1/(1 + |err|/σ)), in tick-units. The whole-segment offset is the median error over the segment's second half. "off-only" is the loss that offset alone would produce. Kind: level if off-only ≥ 60% of the loss, transient if the first 15 ticks hold ≥ 50%, otherwise dynamics. For segments shorter than about 100 ticks with ringing load, a "level" label often means ringing phase (flagged with † below). Full list: `fits/power_grid/round2/loss_rank.json`.

**New runs (R3 + R4; total 1,589 = load 552, frequency 668, share 369):**

| # | Run, segment | Observable | Loss | /tick | Offset | Kind | Cause |
|---|---|---|---:|---:|---:|---|---|
| 1 | R4 160–359 joint 1 × 200 | frequency | 143.5 | 0.72 | +3.3σ | level | B24/B25: v1 50.32 vs 50.11. Also the start dip, 48.87 vs 49.73, since load is higher (B20) and the f–L coupling is weaker (B24). |
| 2 | R4 160–359 joint 1 × 200 | load | 122.2 | 0.61 | −0.5σ | dynamics | B21 irregular 200-tick ringing, B20 peak 171 vs 156 |
| 3 | **R3 200–319 reserve ladder (4 segments together)** | frequency | 110 | 0.92 | −9 to −12σ | level | **B23** (no restoration of the reserve surplus) |
| 4 | R4 0–99 joint .7 from reset | frequency | 92.0 | 0.92 | −11.3σ | level | B23 + B25 |
| 5 | R4 390–469 joint .85 | load | 59.5 | 0.74 | −0.4σ | dynamics | B20/B21 (peak 166 vs 154, trough 97 vs 105) |
| 6 | R4 390–469 joint .85 | frequency | 56.1 | 0.70 | −3.8σ | level | B25 |
| 7 | R4 0–99 joint .7 | load | 55.6 | 0.56 | −0.8σ | level† | B18: reset rise to 131 missed |
| 8 | R3 70–139 p .45 | load | 49.5 | 0.71 | 0.0σ | dynamics | B20 peak 162 vs 146, B21 period |
| 9 | R3 140–199 p 1.5 | load, frequency | 48.8, 48.4 | 0.81 | −2.2σ, −1.6σ | level† | B21: rebound +29 missed (v1 heavily damped); f inherits it through B24 |
| 10 | R3 0–69 p 2 from reset | load, frequency | 48.1, 46.8 | 0.68 | −2.3σ, +2.0σ | level† | B18/B22/B24 |
| 11 | R4 0–99 joint .7 | share | 43.0 | 0.43 | +0.8σ | level | B26: floor 7.1/L vs v1 0.072 |
| 12 | R4 100–159 rec 60 | frequency, load, share | 43.0, 35.3, 33.3 | 0.55–0.72 | ±2–3σ | level† | B28 spike, B20 trough 64.8 vs 71.5 |
| 13 | R3 200–319 reserve ladder | share | 77 | 0.64 | ±1–3σ | level | B26/B27 |

Aggregated by cause (new runs, approximate): **frequency level map (B23 + B24 + B25) ≈ 500**, load ringing shape and saturation (B20 + B21) ≈ 400, reset transient (B18 + B19) ≈ 60, share floor, chatter and release (B26–B28) ≈ 250, and the rest is noise-level misfit.

**Old runs (R1 + R2c, in-sample; total 1,391 = load 522, frequency 585, share 282).** The same errors were already there, but smaller:

- R2c 170–319, joint 1 at x .2, frequency: 94.6 (+2.0σ level). This is the same B25 error as R4 #1.
- R1 0–119 reset, frequency: 79.7 (−2.3σ; the reset overshoot is 51.06 vs 50.66, B24).
- R2c joint-1 load: 79.5 dynamics (B21). R1 p0 load: 65.3 (B20/B21, peak 169 vs 154). R1 r150 load: 51.6 dynamics.
- **Not present in old data:** the mid-reserve and joint-.7 frequency error (B23, −10σ). With only r ∈ {0, 150}, the governor loop could fit both endpoints (the r = 150 point sits near the 52 clip). This part is extrapolation, and it is now the largest single level error.
- Old-data loss was 58% level (800) and 40% dynamics (559). New-data loss is 84% level, so the round-2 regimes mostly exposed **level-map** errors.

## 5. Explanations and minimal model changes, in priority order

1. **Frequency as a (nearly) static droop map, replacing the restoring secondary loop** (B23, B24, B25; ≈ 500 tick-units, frequency is the weakest channel).
   - *Explanation:* base dynamics. The brief says "conventional governors respond to frequency with finite response times and output limits". Droop without integral restoration gives a persistent offset proportional to the imbalance. v1's secondary loop Z has kz pinned at 1 and kg ≈ 1 (lesson 9: a pinned parameter stands in for missing structure). To fit R1/R2 it restores small imbalances and only lets the near-clip r = 150 case through, so its reserve map is convex.
   - *Minimal change:* f_t = f_{t−1} + kf·(f* − f_{t−1}), with f* = 50 + β0 − βL·(L − 100) + βr·min(Rd, Rsat) + βr0·[Rd > 0] − βx(x, Rd) − βc·(1−ch), and the existing clip. Keep a small governor-dip transient only if residuals need it. βx needs a reserve interaction, for example βx·(1−x)·(1 − κ·Rd/150), or a dependence on renewable/import power (the brief ties the interconnector to remote delivery, and under reserve renewables sit on a floor, so closing x removes less power). Delete Z (or set kz = 0).
   - *Evidence it works:* the static regression fitted on R1 + R2c alone gives R3/R4 frequency scores of 0.39/0.42 with observed load, against v1's 0.23/0.27. With forecast load it will be lower, but the level errors of 10σ vanish.
   - *Conflicts:* R1's post-release dip to 49.15 and the reset overshoot need a short first-order lag (kf plus the lag-2 load term), which the regression already carries. The 52.03 clip stays. The only conflict risk is B25's confounding at the joint pulses (x vs load vs charging), and the reserve probe below resolves it.

2. **Replace the linear resonator with a saturating thermostat population** (B20, B21, B33, and B22 partly; ≈ 400 tick-units; review gap G3).
   - *Explanation:* M1 as the brief describes it. Each load warms while off and cools while on, switching at upper and lower temperature limits that price shifts. When all loads switch off, load hits a floor (≈ 64 = non-thermostatic base). When all switch on, it hits a ceiling (≈ 170). Heterogeneous thermal constants give the drifting period and the beats.
   - *Minimal change:* first try a **bounded resonator**, L = base(p) + C·φ with φ = clip(φ_eq(p) + o, 0, 1) (base ≈ 64, C ≈ 106), and a larger gain so peaks reach 162–171. That captures the floor, the ceiling and the larger peaks with three extra parameters.
   - If the period drift and the 200-tick irregular ringing still cost more than about 100 tick-units, move to K = 3–5 cohorts. Each cohort has temperature T_k, an on/off state, time constants τ_k and a deadband [lo(p), hi(p)] shifted by price, and switches deterministically. The reset population is uniformly phased at price 0.8, as the brief states.
   - *Conflicts:* none with old behaviours. B2 (the instant jump) follows naturally, because loads near the band edge switch at once. Fitting a nonsmooth cohort model needs Powell or Nelder–Mead before `least_squares` (§3.5 of `round2-experiments.md`).
   - Keep outputs bounded with the clips. Stability risk is low because the cohorts are bounded by construction.

3. **Price→load level above 1.5 flattens** (B22).
   - *Explanation:* plain saturation (demand floor).
   - *Change:* use up⁺ = max(up, 0) for most of the level term, plus a small separate slope for up < 0 (settled ≈ 90 at price 2, so ≈ −13 per unit of negative up instead of v1's −31).
   - *Conflicts:* none, since price > 1.5 was only seen in R3.

4. **Share under reserve: a floor form instead of `1/(1+w·Rd)`** (B26, and the level part of B28).
   - *Explanation:* base dispatch. The brief says "dispatch allocates supply according to operating cost and system conditions". Reserve displaces renewables down to a must-run floor.
   - *Change:* renewable power P = max(P_floor(x), P_free(L, x) − k·Rd) with k ≈ 0.7, P_floor ≈ 11 − 0.03·Rd at x = 1 and ≈ 6–7 at x ≤ .5. Then share = P / L, smoothed by a soft-min for the fitter.
   - Keep v1's lagged-surplus term B (spike after release) but refit it. The R4 t100 spike (0.474) is larger than v1 allows.
   - Chatter (B27): do not model it; the soft-min at the kink predicts about the low state.
   - *Conflicts:* M3's static cap (h3 ≈ 0.35) was partly standing in for "share ≈ 0.27 + 9/L". With P modelled explicitly, check whether g3 → 0. If it does, **m1-only** becomes the natural choice (M3 has still shown no signature of its own). That is a model-selection question for the modeler, and must go through a bootstrap, not this note.

5. **Reset and initial-reading handling** (B18, B19; ≈ 60 tick-units, but in every scored episode).
   - *Change:* L(0) = L0_reading + instant response, with the reading's deviation from the model's reference fading at qi ≈ 0.85. Fix `Lref0` to the model's own 0.8-price equilibrium instead of fitting it: at 118 it is a pinned-style misfit sink.
   - The R4 reset rise to 131 comes from items 1–2: the ringing gain and the joint start.
   - *Conflicts:* none.

6. **Load–frequency coupling** (B30). This is optional and open. Add L += D·(f − 50) with D fitted, and keep it only if the refit gives D > 0 with a margin. The evidence is inconsistent (1–8 load units per Hz), and the scoring stake is at most 2.5σ over short windows.

Every change above is base structure. None needs M2 or M3. Following lesson 5, pair comparisons should be redone only after items 1–4.

## 6. Reserve-step proposal (110 steps left for power_grid per `round2-experiments.md` §0; not spent here)

**What is still unknown and matters for the score:**

- The composition cell **price 0 + reserve 150 at x = 1**, which was never observed. Is the joint-pulse frequency deficit (B25) caused by the interconnector or by high load / governor limits?
- The interconnector effect under reserve at high load.
- Charging at high load (the last M2 loophole: charging draw or fade with the load at 125).

The joint pulses dominate scoring (composition plus recovery-spacing, about half the score), and B25 decides the frequency map there.

**PG3 (fresh reset, 110 steps):**

```sh
python run_schedule.py --system power_grid --output data/power_grid/R5.json --confirm 110 --segments '[
 {"steps": 60, "action": {"price_signal": 0.0, "reserve_dispatch": 150, "charging_allowance": 1.0, "interconnector": 1.0}},
 {"steps": 30, "action": {"price_signal": 0.0, "reserve_dispatch": 150, "charging_allowance": 1.0, "interconnector": 0.2}},
 {"steps": 20, "action": {"price_signal": 1.5, "reserve_dispatch": 0,   "charging_allowance": 1.0, "interconnector": 1.0}}]'
```

| Segment | What it measures | Predictions (last 10) | Decision |
|---|---|---|---|
| A: p0 + r150, ch 1, x 1 (60) | P3 price × reserve at x = 1, from reset | v1: f 50.66, S 0.077. Static map B24 (additive): **f ≈ 51.15**, S ≈ 7.2/L ≈ 0.058 at L ≈ 125 | If f ≈ 51.1 ± 0.15, the model is additive and the joint deficit is an **interconnector** effect: use βx(1−x) with a reserve interaction. If f ≈ 50.2–50.5, frequency saturates at high load (governor output limit), so add a load-dependent droop / limit and make x weak under reserve. The two outcomes are about 7–12σ apart. S tests whether the floor is load-independent at x = 1. |
| B: same, x .2 (30) | x effect under reserve at high load. Compared with R4 joint 1 (identical except charging 0), it also gives the **charging effect at high load**. | Static map: f ≈ 50.27. v1: 50.25. R4 joint 1 last 10: 50.11 | A − B gives βx directly. B vs R4 joint 1: a difference > 0.15 Hz (2σ) at matched load means charging acts (the M2 loophole reopens). Otherwise M2 is closed for good. |
| C: recovery (20) | The trough floor after a price-0 step with reserve and no interconnector history (B20), and the share release spike after a deep-surplus pulse (B28) | trough ≈ 64 (B20) vs v1 63.4 | Trough 63–65 again confirms the saturation floor (the thermostat model). Spike size vs the pre-release f from A/B calibrates B28. |

**Alternative if B25 is resolved for free** (for example, if a refit with item 1 explains the joint deficits by load alone within 1σ): spend the 110 steps on **price 0 alone for 110 ticks from reset**, to measure the long-run ringing amplitude at price 0 without reserve. This is the residual risk named in `round2-experiments.md`, and it bears on the sustained category, where load ringing (B21) is the #2 loss.
