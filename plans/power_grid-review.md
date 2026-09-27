# power_grid review (Phase B reviewer, 2026-09-27)

I spent no simulator steps. Spent so far: 950 of CAP 1,000, so the reserve is **50**. All paths below are under
`toronto26-participant-kit/`. The review artefacts are in `fits/power_grid/review/`:

- `share_scan.py` / `share_scan.png`: the raw runs with renewable power S·L.
- `pg_model_v1s.py`: a copy of `greybox/power_grid_model.py` with the share structure fixed (details below).
- `pg_model_v2s.py`: v1s plus a bounded "conventional backoff" state that drives the share.
- `v1s_*.json` / `v2s_*.json`: my refits on R1+R2.
- `compare.py` / `v1s_pairs_err.png`: fits and error panels.
- `rank_reserve_probe.py` / `probe_rank_review.json`: the ≤50-step probe ranking.

## 1. Independent behaviour list (written before reading the plan)

| ID | Behaviour | Evidence |
|---|---|---|
| R1 | **Reset transient.** The first load reading is already 15 below the initial reading (115→100.6 in R1, 101→88.5 in R2). Load then dips to 72 at tick 14, overshoots to 105 at tick 45 and rings. After about 20 ticks R1 and R2 are identical. Frequency overshoots to 51.1 at tick 15. Share goes 0.35 → 0.40 (tick 20) → 0.33 → 0.38 in both runs and ignores its initial reading (0.35 vs 0.24). | `R1_r0_battery.png`, `R2_r0_battery.png` |
| R2 | **Price step.** Load jumps at once (+47 for 1.5→0, +24 for 0.75), overshoots to about 1.6× the settled change, then rings. The period depends on the price level: about 50 ticks at price 0, 65–85 ticks after returning to 1.5. Ringing after price-off stays large for more than 130 ticks. | R1 120–350, R2 130–170 |
| R3 | **Frequency** mirrors load (≈ −0.03 Hz per load unit) with partial restoration. There is a hard upper clip at 52.03. | both runs |
| R4 | **Reserve 150 onset.** Share falls to 0.100, then 0.059, which **undershoots**. It then creeps back +24% (to 0.073) in about 20 ticks and stays flat. Load is unaffected. | R1 280–300, R2 370–380 |
| R5 | **Reserve release.** Share **overshoots** to 0.505 and decays to 0.39 in about 15 ticks, and frequency dips to 49.15. After the joint-pulse release, where frequency had not been in surplus, the share peaks only at 0.41. R4 and R5 look like the same ~15-tick state as seen from both switches, and its size follows how deep the surplus was before the switch. | R1 350–365, R2 320–330 |
| R6 | **Renewable power.** With the interconnector open and no reserve, renewable power S·L ≈ 9 + 0.27·L (RMSE 1.9 against a std of 5.8). Equivalently, share ≈ 0.27 + 9/L. The only large outliers are the post-release spikes (+10). So the "plateau at 0.38–0.39" is mostly load dilution, not a fixed cap. | `share_scan.png`, regression in this review |
| R7 | **Interconnector.** Share is 0.155 / 0.21 / 0.375 at x = 0 / 0.2 / 1 (concave), changes instantly in both directions, and does not overshoot on reopening. Frequency drops 0.7–0.9 Hz and governors then recover about 0.4 Hz. | R1 390–470, R2 40–130 |
| R8 | **Reserve effect is multiplicative.** With reserve on, share is about 0.2× its reserve-free level at both x = 1 (0.073/0.37) and x = 0.2 (0.047/0.21). After the first ~40 ticks, the joint-pulse share creeps only +3% per 100 ticks (0.0487 → 0.0500 over 210–320). That is the same slope as R1's reserve hold with charging = 1 (+6% per 100 ticks). **Charging off made no visible difference to the share.** | segment regressions in this review |
| R9 | Setting charging to 0 on its own (reserves full) had no effect. A second dispatch 50 ticks after the joint pulse matched the first. | R1 500–525, R2 370–400 |
| R10 | **Noise σ.** Load 0.10, frequency 0.016–0.021, share 0.0003. Share is by far the most precise channel, at roughly 50 noise σ per score σ. | second differences |

## 2. Comparison with the catalogue and the model (evidence: `fits/power_grid/review/v1s_pairs_err.png`)

The catalogue (B1–B17) contains everything in my list. My additions are R6 (the dilution form), R8 (charging made no difference to the late creep) and the dependence of the ringing period on price level in R2.

| Behaviour | Component in the best refit (v1s) | Status |
|---|---|---|
| B1/R2 load ringing | single damped m1 resonator driven by Δprice | **partial**: errors of ±30 σ_fit (±15 load units, about 7 score σ) over R1 250–350 and R2 130–200. The period is fixed, but the data's period depends on price. |
| B2 instant jump, B5 linear price | `wLi`, `wLp` | captured |
| B3/R1 reset dip depth | reference price 0.8 | partial (78 vs 72) |
| B4 initial load reading fades at ~17%/tick | none (`init` module off) | not captured (low) |
| B6 frequency droop / governor | governor loop | captured roughly; ±10–30 σ_fit at events |
| B7 frequency clip | fixed clip | captured |
| B8/R8 reserve collapses the share | v1s multiplicative 1/(1+wSr·Rd), wSr ≈ 4.3 | **captured** (the joint-pulse share error is now ≤ 2 σ_fit; before the fix the model predicted 0) |
| R4 onset undershoot, B9/R5 release spike | v1s: exp(−wSG·G); v2s: bounded backoff state | **not captured** in either variant (−40 σ_fit ≈ −0.12 share for ~15 ticks after R1 350). v2s did not help (kgs → 0.015). |
| B10/R6 plateau | v1s has no cap and relies on load dilution. **m13 uses M3 as a static cap** (h3 = 0.339). | see G1 |
| B11 slow share oscillation at recovery | load dilution | partial (±10 σ_fit) |
| B12/R7 interconnector nonlinearity | quadratic in (1−x) (`wSx2`) | captured |
| B13/B14 M3 and M2 nulls | — | evidence (see G1) |
| B16 joint-pulse load +4 | m12 `g2L` (recharge draw) | partial; only m12 has it |

**Refit with the share structure fixed** (R1+R2, one restart each, same σ_fit as the plan; costs are comparable within a variant):

| Variant | m1 only | m1+m2 | m1+m3 |
|---|---:|---:|---:|
| v1s (multiplicative share, no cap) | 28,552 | **26,828** | 28,118 |
| v2s (+ backoff state) | 28,563 | **26,490** | 27,658 |
| researcher v0 (additive share, cap 0.39) | — | 30,289 | 31,511 |

Fixing the share structure lowers every cost by 3–4k, but **m12 still leads by about 1.2k**. The segment breakdown (`compare.py`) shows where that lead comes from:

- **M2's contribution** is +3.9k on R2 joint-pulse frequency, plus 0.4k on share there. In the fit, the reserve fades to 61% over the 150-tick charging-off pulse (d2 = 0.0033, with **e2 = 0.9998 pinned at its bound**). The same fit then predicts a joint-pulse share rise of 0.0433 → 0.0563 (+30%) over ticks 210–319. The data rise only 0.0486 → 0.0499 (+3%), and R1 shows the same creep with charging on. **M2 is being used as a frequency drift term, and its own prediction in the most precise channel contradicts the data.** By lesson 9 (a parameter pinned at its limit), this lead is not evidence for M2.
- **M3's contribution** (0.4–0.9k) comes from a static share cap at h3 ≈ 0.34, not from thermal memory. The thesis signature (overshoot after reopening a cooled line) was null in R2 at tick 90.
- Neither pair shows its mechanism's own signature, so the pair question is **still open** after the share fix.

## 3. Coverage (§4.2) and separating probes

- P0 in each run: done. P1 for every control: done, though charging was only tested while reserves were full, where it is inert unless M2 is active. P2 for price: done (0.75).
- **P3 (two top controls together): not run.** The joint pulse moves all four controls at once, so it does not show whether price + reserve add on frequency and share.
- **P4/P9a (price ramp vs step): not run.** P6 (order swap): not run. **P7 (≥ 200 ticks): not run** (the longest hold was 150).
- M1 vs M2 and M1 vs M3 are separated (every pair without m1 is more than 11k worse). **M2 vs M3:**
  - P9c (reopen after full closure) was run and evaluated: null.
  - P9b (second dispatch after a 50-tick gap) was run, but **it cannot detect M2 with fast recharge**. The fitted M2 refills at c2 ≈ 0.12/tick, and E is 0.996 at tick 370.
  - The long charging-off dispatch was run, but its share channel was not used to bound the fade. It gives a bound of **≤ 3–5% fade per 100 ticks, provided share is sensitive to Rd near Rd = 1**. That proviso is unverified, because no reserve level between 0 and 150 was tried.

## 4. Missed drivers, stability

- **Reserve level.** Only Rd = 0 and 150 were observed. The model assumes the share and frequency response is smooth between them, but it could saturate once reserve exceeds headroom, where renewables would sit at a must-run floor. If it does saturate, a reserve fade at 150 would be invisible in the share, and that is the loophole left in the M2 null.
- **M3 driver.** Only low-flow → reopen was tested. Sustained **high** flow (x = 1 under high demand for a long time) was never checked for slow share decline beyond load dilution.
- **Price 1.5–2.0** (u < 0) is untested. Scoring's sustained, order and joint episodes can use it.
- **M1 period depends on price level** (thermostat band shift). A fixed-frequency resonator cannot capture it.
- **Stability over 4,000 steps.**
  - The resonator is stable (|eig| = √ρ1 ≈ 0.98), and all states are clipped.
  - **Risk:** m12's fade extrapolates to total reserve loss after roughly 700–1,000 ticks of charging-off dispatch. Frequency would then collapse toward the clip. This is a 4,000-step extrapolation of a 150-tick drift that the share data contradict.
  - Pinned parameters: kL = 1.0 (v1s m12), e2 = 0.9998, kS ≈ 1. Only e2 matters, because kL and kS just mean "instant".

## 5. Gaps

| # | Severity | Gap | Evidence | Fix / test |
|---|---|---|---|---|
| G1 | **high** | M2 vs M3 unresolved. m12's 1.2k lead after the share fix is a frequency fit in the joint pulse whose share prediction is 10× the data. m13's gain is a static cap. | §2 table and bullets; `v1s_pairs_err.png` | Spend the reserve on the probe below. Until then, do not credit the margin to either module. |
| G2 | **high** | If m12 is chosen as fitted, the reserve vanishes after about 1,000 ticks of charging-off dispatch. | d2, e2 in `v1s_m12.json` | Cap the fade with the share evidence: at most 5% per 150 ticks at charging 0 (d2 ≲ 3e-4), unless the probe shows a fade. |
| G3 | **high** | Load ringing is under-predicted (±15 load units). The period depends on the price level. | R1 250–350, R2 130–200 error panels | Replace the resonator with a small thermostat-population model taken from the brief: N bins with heterogeneous time constants, a deadband shifted by price, and on/off state. Alternatively use 2 modes with price-dependent frequency. No steps needed. |
| G4 | **high** (for score) | Reserve response at mid levels is unknown (only 0 and 150 observed). | §3 | No data within CAP. Keep a smooth 1/(1+wSr·Rd) and flag it. It competes with G1 for the 50 steps, but the orchestrator's priority is G1. |
| G5 | medium | The release spike (0.505) and the onset undershoot are not captured. Their size follows the surplus depth before the switch. | R4, R5; −40 σ_fit | Model renewable *power*: Rp = min(avail(x), needed), with share = Rp/(Rp + C + Res) and conventional C = C0 + governor backoff (a large, slow limit). Try this before crediting either module. |
| G6 | medium | Frequency residuals in the joint pulse and after release are what M2 absorbs. | segment costs | Try a governor with an output limit plus a slow secondary (integral) loop before crediting M2. |
| G7 | medium | Coverage: no P3 pair (price+reserve), no P4/P9a ramp, no P6 order swap, no P7 ≥ 200, no price above 1.5. | §3 | Model-side priors only; out of budget. |
| G8 | low | The initial load reading's decay (~17%/tick) is ignored. | R1 vs R2 ticks 0–20 | Add (L0 − L̂0)·0.83^t to the load. |
| G9 | low | P9b cannot detect fast-recharge M2. | E(370) = 0.996 | Note it in the plan; the probe below covers it. |
| G10 | low | Costs come from single restarts. A warm start of m1 from m12's base gives 29.0k against 28.55k from its own start, so optimizer noise is about ±0.5k. | `v1s_m1_w.json` | Use 3 restarts and cross warm-starts before quoting margins. |

## 6. Reserve spend: recommended (50 steps, G1)

This is a **charging A/B during full dispatch at x = 1**. charging_allowance is a lever only M2 can use. With the other controls equal, M3 and the base model predict *no* difference from the charging = 1 twins already on file.

- **Preferred:** continue R2, whose last 30 ticks were the same action with charging = 1, so the twin is in the same run at the same load phase:
  `python run_schedule.py --continue data/power_grid/R2.json --segments '[{"steps": 50, "action": {"price_signal": 1.5, "reserve_dispatch": 150, "charging_allowance": 0, "interconnector": 1}}]' --confirm 50`
  - Check the first reading. It must continue from tick 399 (share ≈ 0.074, frequency ≈ 51.8). If it does not, or the call fails, use the fallback.
- **Fallback:** a fresh reset with the same 50-tick action from tick 0:
  `--system power_grid --output data/power_grid/R3.json --segments '[{"steps": 50, "action": {"price_signal": 1.5, "reserve_dispatch": 150, "charging_allowance": 0, "interconnector": 1}}]' --confirm 50`
  - Load should follow the P0 transient already measured twice. The charging = 1 twins are R1 280–349 and R2 370–399.
- **Predictions** (`rank_reserve_probe.py`):

  | Model | Share, start → end (continuation) | Frequency at tick 49 vs the charging = 1 twin | Share, fresh reset (ticks 15 → 49) |
  |---|---|---|---|
  | m12 (v1s / v2s) | 0.074 → 0.084 / 0.088 (+30 noise σ) | about 0.5 Hz lower | 0.077 → 0.082–0.084 |
  | m13 and m1 | flat 0.075 ± 0.001 | identical to the twin | flat 0.075 ± 0.001 |

- **Decision rule:**
  - Fit share ~ a + b·t + c·(L−100) over the hold, skipping the first 15 ticks on the fallback.
  - If the rise is ≥ +0.004 over the hold, with frequency more than 0.2 Hz below the twin at matched load, then M2 is active. Refit m12 with that fade, and drop m13.
  - If the slope is ≤ R1's (+0.0004 per 10 ticks), there is no charging-dependent fade on this scale. Then M2 is inactive by elimination (or irrelevant within 150 ticks). Choose m1+m3, or the base model with d2 capped (G2), and fix G5/G6 instead of letting a module absorb the frequency misfit.
- **Caveat (G4):** if share saturates at Rd = 150, a fade could hide in the share. The frequency channel still separates the models at the end of the hold, once load returns to about 100 and frequency comes off the 52 clip.
