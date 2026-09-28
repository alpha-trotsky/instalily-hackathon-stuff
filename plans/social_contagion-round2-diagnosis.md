# social_contagion: round-2 diagnosis (R4 = SC1, R5 = SC2)

Diagnostician pass, 2026-09-28. No steps spent (one free `--budget` read: **120 remaining**). No model changed.
Paths below are under `toronto26-participant-kit/`. Scripts, plots and outputs are in `fits/social_contagion/round2/`:

- `analyze.py`: v1 (`fits/round2/v1_models/social_contagion/predict.py`) on R1–R5, per-segment table, plots, `analysis.json`.
- `measure.py` → `measure.out`: decision-rule quantities, delays, rates, reset troughs, noise, a/b ratios.
- `variants.py` → `variants.out`: the existing fits (m12 = v1, m23_all, m2_all) and two one-parameter ablations of v1 on R1–R5. No refits.
- `rank.py` → `rank.out`: score-loss ranking and level/dynamics/transient classification. `asym.out`: on/off timing.
- Plots: [R4.png](../toronto26-participant-kit/fits/social_contagion/round2/R4.png), [R5.png](../toronto26-participant-kit/fits/social_contagion/round2/R5.png), and the old runs for comparison: [R1.png](../toronto26-participant-kit/fits/social_contagion/round2/R1.png), [R2.png](../toronto26-participant-kit/fits/social_contagion/round2/R2.png), [R3.png](../toronto26-participant-kit/fits/social_contagion/round2/R3.png). Each has one panel per observable with v1 overlaid (red), plus a controls panel in u units.

σ = 0.1 × std of all data after tick 20 (as in `heldout.py`) = **5.58 (A) / 2.93 (B)**. "Err" = v1 − data.

## 1. Summary

1. v1 scores **0.367 / 0.355 on R4 and 0.196 / 0.210 on R5** (mean 0.282). On R5 that is barely above persistence (0.08 / 0.20). The old runs score 0.66–0.80 with the same σ, so this is the extrapolation failure the plan predicted, and it is mostly **level** error (5–12σ), not timing.
2. **The biggest miss is composition.** Incentive 2 added on top of seeding 4.5 raises the plateau to **257 / 146**. v1 predicts 194 / 110 (−11σ / −12σ). v1 has almost no steady incentive effect: gret is pinned at 0 and iota is tiny. The effect is not transient: a cut to incentive 1 settles flat at 143 / 75, which is still 6σ above v1.
3. **The crash floor is not a fixed core.** After R4's u.7 pulse the crash bottoms at **65 / 50**, against 43 / 31 in R1 and R2. v1 goes to 52–54 / 39. Regrowth then starts immediately. The partial cut 2 → 1 leaves at the **same rate (k ≈ 0.09/tick) as a full crash** but stops halfway. So the exit rate is fixed, and the size of the incentive-dependent stock sets the depth.
4. **The level map along the recovery→pulse ray is linear in A, not saturating.** A's u.7 / u.85 plateaus lie at fractions **0.68 / 0.85** of the way from recovery to u1. v1 gives 0.93, which overshoots the u.7 plateau by +5σ / +7σ. The 300-tick recovery tail heads to **≈ 93 / 77**, within 10% of v1's 96.5 / 83.7. v1's M1 (departure-driven credibility) slows every rise from a controlled reset. m2_all, which has no M1, scores higher on R4 and R5 (0.46 / 0.29 against 0.36 / 0.20).
5. **Verdicts:** H1 keep the structure and refit, pinning 93 / 77. H2 is a linear gap in magnitude but not in rate. H3 is inconclusive (A 0.75, B 1.03), and the fitted M1 hurts. H4 finds no interior saturation in A. Proposed reserve use (120): decompose the u.7 point with incentive *after* recruitment (§6).

## 2. Decision-rule verdicts

These are the pre-registered rules from `round2-experiments.md` §4.1. Each value is the mean of the last 10 ticks of the segment unless stated. Candidate predictions are from `fits/round2/final_social_contagion.out`.

| Rule | Quantity measured | Data | m12 (v1) | m23 | m2 | Verdict under the rule |
|---|---|---|---|---|---|---|
| **H1** long-run recovery | Exponential asymptote fitted to R4 250–399 (A, B). Other windows 150–399 and 200–399 give 94.9 / 72.9 and 92.4 / 75.1. Last-10 level is 89.0 / 73.2, still rising +0.04 / +0.02 per tick, with τ ≈ 110 / 180 ticks | **92.6 / 76.9** | 83 / 79 at 390–399 (asymptote 96.5 / 83.7) | 99 / 87 | 92 / 86 | **Within ±10% of 96 / 84** (A −4%, B −8%). **Keep the structure and refit, with ≈ 93 / 77 as a pinned target.** It is not "flat near 43 / 31" and not "above 105 / 90". B is the weaker side: it is 8% low, and the B asymptote varies 73–77 with the window. |
| **H2** partial incentive cut | A drop at incentive 1 (R5 140–189: 257.0 → 143.3), divided by the drop to the known floor at incentive 0 (257 − 43) | **0.53** (B: 0.62, using floor 31) | level 109 / 60 | 129 / 71 | 129 / 71 | **0.4–0.6: the linear gap is right in magnitude.** Caveats: (a) measured against R5's own incentive-0 level with seeding still on, the ratio is 0.74 (to the minimum of 104) or 0.83 (to the last-10 level of 119), which leans towards "any cut triggers". (b) **The rate is not gap-proportional.** The 2 → 1 fall has k = 0.088/tick, the same as full crashes (R1 0.091, R2 0.088), while a linear-gap hazard with E ≈ 0.82 predicts about a third of that. Magnitude is linear, rate is a step. All three candidates are 2.5–6σ too low. |
| **H3** credibility memory | Gain of P3 (after a 20-tick gap, R4 480–539) over P2 (after a 300-tick gap, 400–459), 60-tick gains | **A 0.745, B 1.026.** End-level ratio 0.887 / 0.892 | gain ratio A 0.89 / B 1.56 (end 174 / 112) | end 172 / 109 | end 172 / 110 | **Split:** A < 0.85 says keep M1 (m12). B ≥ 0.95 says switch to m23. The end-level ratio (0.89 in both) falls in the undecided 0.85–0.95 band. The comparison is confounded: P3 starts in B at 59 (still crashing) against 73 for P2, so B's gain is inflated. A's deficit is concentrated in the first 10 ticks (+6 against +15). **Inconclusive.** All candidates over-predict the P3 end by 2–4σ (A) and 1.5–2.4σ (B). Independently, the fitted M1 damages the reset-under-control rise (B30), and m2_all beats m12 on R4 and R5. |
| **H4** interior saturation | u.7 plateau (R4 90–99) placed on the recovery (R4 390–399) → u1 (R2 245–254) line | **A 0.68, B 0.48** (B not settled; with its fitted asymptote of 118 it is 0.77). u.85 (R4 450–459): **A 0.85, B 0.76** | 0.93 / 0.81 (192 / 122) | 192 / 120 | 191 / 120 | **A is linear along the ray: no interior saturation.** Data 164 / 101 against about 192 / 121 for all three candidates, +4.9σ / +7.1σ at the end of the hold. The saturation curvature must be removed from the ray. Seeding *alone* does saturate (B26), so the linearity comes from incentive and bridge, not from seeding. |

## 3. Behaviour catalogue (new runs; continues B1–B16 from `social_contagion-plan.md`)

Categories: S = sustained, O = action order, R = recovery history, C = composition of controls. Errors are in σ units (v1 − data).

| ID | Behaviour | Evidence | v1 status | Categories |
|---|---|---|---|---|
| **B17** | **Reset under control is truncated.** With controls from tick 0 the reset drop stops at ×0.86–0.87 of the reading at tick 5–9. Without controls it reaches ×0.75 at tick 13–17 (R1–R3). Recruitment starts before the expectant share has left | `measure.out` reset troughs: R4 34.6 / 25.9 at tick 5–6, R5 40.0 / 42.6 at tick 5–9 | **Captured** (v1 trough 38.0 / 26.6 and 43.3 / 41.0: +0.6σ / +0.2σ) | all (every episode) |
| **B18** | **The first rise from a controlled reset is fast.** A onset is 8–9 ticks. A reaches 94 by tick 20 in R4 and 89 in R5, with a peak slope of 5.6/tick at +14 | R4 0–30, R5 0–30 (`R4.png`) | **Not captured:** v1 has 66 / 69 at tick 20 (−5σ). m2_all has 78 / 83 and v1 with g1 = 0 has 127 / 133 (`variants.out`). v1's M1 credibility is suppressed by the reset departures | all |
| **B19** | **u.7 joint plateau from reset:** 164 / 101, with A flat after about tick 60 (asymptote 165) and B still rising (τ ≈ 49, asymptote about 118). Settle check: neither is settled (drift 5σ / 49σ noise) | R4 0–99 | **Not captured:** +4.9σ / +7.1σ at the end of the hold; v1 has 192 / 122 | S, C |
| **B20** | **The level map on the ray is linear in A:** 89 (u 0), 164 (0.7), 183 (0.85), 199 (1). Fractions 0.68 / 0.85. In B it is concave or unsettled (0.48 / 0.76) | H4 row, `measure.out` | **Not captured:** v1 fraction 0.93 | S, C |
| **B21** | **Crash from the u.7 pulse bottoms at 65 / 50** (minimum at tick 139 / 129), far above the R1/R2 floor of 43 / 31. The fall rate is k 0.062 / 0.096, and A is 2/3 as fast as in R1/R2 (0.09) | R4 100–150, `measure.out` | **Not captured:** v1 minimum 52 / 39; −1.9σ / −4.4σ at the end of the segment, −3.1σ / −3.9σ at 150–249 | R |
| **B22** | **Regrowth starts right after the crash, and B leads.** B is +0.5/tick from tick 130; A is flat until about tick 150, then +0.3/tick. After that it is a slow approach with τ ≈ 110 (A) and 180 (B). a/b is 1.15–1.22 throughout | R4 130–400 | **Not captured:** v1 is flat at 52 / 39 until about tick 200 and then climbs too slowly. It crosses B at about tick 330 and ends B +2σ high | R, S |
| **B23** | **Recovery equilibrium ≈ 93 / 77** (H1), still drifting +0.04 / +0.02 per tick at +300. Also R5 recovery, 80 ticks after seeding stopped: A 99.5 falling (−0.2/tick), B 67.8 flat or slightly rising | R4 250–399, R5 240–319 | **Partly:** A equilibrium is within 4% and B's is 8% too high. The *path* is wrong (B21/B22), and R5's recovery is −3.5σ / −5.4σ because of B28 | R, S |
| **B24** | **Incentive after recruitment is a large level effect:** adding incentive 2 to seeding 4.5 raises 197 / 99 to **257 / 146** (+60 / +47), half-change about 17 ticks, A settled (drift 0.3σ). The plateau is **above seeding 9 alone (230)** and above the full pulse (199 / 131) | R5 80–139 | **Not captured:** v1 +9 / +17, ending −11.4σ / −12.1σ. The largest error anywhere. The same deficit appeared in old data: R1 incentive after seeding raised B 91 → 107, where v1 is −4.2σ | C, O, S |
| **B25** | **Partial cut 2 → 1: fast fall at the full-crash rate (k 0.088), then flat at 143 / 75** (settled, drift 0.0σ / 0.24σ) for about 30 ticks. The new level is **below** the seeding-only level before the incentive (197 / 99), so the cut removes seeding-recruited members too | R5 140–189 | **Not captured:** v1 109 / 60 (−6.1σ / −5.2σ); m23 / m2 129 / 71 | C, O |
| **B26** | **Seeding dose saturates when seeding acts alone:** seeding 4.5 reaches 196 / 98 at tick 80, with a fitted asymptote of 219 / 148 (B far from settled, τ 83). Seeding 9 alone gives 230 / ≥ 120 (R1) | R5 0–79 | **Partly:** v1 185 / 93 (−2σ / −1.6σ). It already missed seeding 9's 230 by −3.75σ in R1 | S, C |
| **B27** | **The cut 1 → 0 with seeding on undershoots and rebounds.** A falls to 104 at tick 214 (fall k ≈ 0.03 net of inflow), then climbs to 120 by tick 240 while seeding is still 4.5. B goes 50 → 58 | R5 190–239 | **Shape captured, level not:** v1 dips to 73 and rebounds to 89 (−6.4σ / −5.1σ) | O, C |
| **B28** | **A lasting history deficit.** Seeding 4.5 at incentive 0 after the incentive episode supports only about 120 / 58 against 197 / 99 before it (×0.6), and it still stands 50 ticks after the incentive ended | R5 230–239 vs 70–79 | **Direction captured, too strong:** v1 83 / 42 (×0.45) | R, O |
| **B29** | **Pipeline overrun after seeding stops:** A keeps rising for 11 ticks (120 → 134 at tick 251), then declines at about −0.35/tick. B flattens at about 66 with no decline | R5 240–320 | **Captured in shape** (v1 peaks at 96 at about tick 250), offset by B28. **B's flat tail is not captured:** v1 B rises slowly from 47 to 53 | R |
| **B30** | **Rise and fall timing is asymmetric but consistent.** Half-change on: A 16–22 ticks, B 17–38. Off: 7–11 ticks. Symmetric in neither linear nor log units (`asym.out`). Onset delay on is 5–9 ticks (A) and 4–12 (B). Off has a 0-tick delay | `asym.out`, `measure.out` onsets | **Captured on/off** at P2/P3 (v1 errors come from levels). **The rise from a reset (B18) is too slow in v1** | O, R |
| **B31** | **Gap history (H3).** A pulse after a 20-tick gap rises more slowly in A (+6 against +15 at +10 ticks) and ends ×0.89 of the pulse after a 300-tick gap in **both** communities. P3 is still rising at the end (A drift 32σ) | R4 400–539 | **Partly:** v1 predicts end ×0.94. It over-predicts the P3 end by +2.2σ / +2.4σ and is too slow early (−2.9σ mean in B) | R, O |
| **B32** | **Crash rate depends on the pulse's incentive history.** k ≈ 0.064 after u.7/u.85 pulses of 60–100 ticks (R4 100, 460, 540) against 0.09–0.10 after 200 ticks of full incentive or incentive alone (R1, R2), and 0.088 for the partial cut (R5 140) | `measure.out` fall rates | **Partly:** v1 falls to 60 / 42 over 130–139 against about 66 / 51 | R |
| **B33** | **Output relationships:** the a/b ratio is 1.5–1.6 under ray pulses (bridge ≈ 0.5), 1.75–2.1 under seeding without bridge (R5), and 1.15–1.45 in recovery. dlogA and dlogB correlate at 0.55–0.63 for lags −2 to +5 (B lags A by about 2 ticks). Crashes start in both communities on the same tick | `measure.out`, `asym.out` | **Partly:** the ratio at the u.7 plateau is right (v1 1.57 vs 1.63), B's recovery level too high | C |
| **B34** | **Noise** is proportional, 0.25% / 0.26% of the level (log second differences), the same as R1–R3 | `measure.out` | Captured (log units) | — |
| **B35 (surprise)** | **Incentive × bridge interaction.** Incentive raises A strongly without bridge (B24: 257 at seeding 4.5), yet the pulse with bridge 0.6 and incentive 2 sits at 199 (R2), and the u.7 point with bridge 0.42 at 164. Either the bridge costs A much more than its effort share, or incentive *before or with* recruitment (R2, R4) is worth much less than incentive *after* recruitment (R5). The brief names that very comparison ("incentive before versus after recruitment"). The runs cannot separate these | R2 55–255, R4 0–99, R5 80–139 | **Not captured, and not identifiable** from current data (§6 probe) | C, O |

**Settle status** (`python3 -m greybox.common.settle`, strict 2σ-noise criterion, σ_noise ≈ 0.2–0.4). Settled: only R5 80–139 A, R5 140–189 A and B. Everything else is still drifting at the segment end. The practical cases (drift per tick at the end):

- R4 0–99: A about 0.1, B about 0.3.
- R4 250–399: +0.04 / +0.02.
- R5 0–79: +0.5 / +0.45. Seeding 4.5 is far from its level.
- R5 240–319: −0.2 / +0.05.

Levels in §2 are therefore lower bounds for rises. That is why B19, B23 and B26 are also quoted as fitted asymptotes.

## 4. Score-loss ranking

Loss = Σ over ticks of 1 − 1/(1 + |err|/σ), in tick units (`rank.out`). Totals: **R4 716, R5 510**; old R1 374, R2 244, R3 20.

Classes:
- **level:** the mean error keeps its sign (|mean| / MAE ≥ 0.8), and the last-10 error is ≥ 0.5σ;
- **transient:** more than 50% of the loss falls in the first 20 ticks;
- **dynamics:** everything else.

| # | Run, ticks | Obs | Action (s / i / b) | Lost | Mean err | Last-10 err | Class | Cause (behaviour) |
|---|---|---|---|---:|---:|---:|---|---|
| 1 | R4 250–399 | A | 0 / 0 / 0 | 98.3 | −2.0σ | −1.1σ | level | Slow post-crash regrowth (B22). The equilibrium itself is fine (B23) |
| 2 | R4 150–249 | B | 0 / 0 / 0 | 84.2 | −5.4σ | −3.9σ | level | Crash floor too deep and regrowth too late (B21, B22) |
| 3 | R4 250–399 | B | 0 / 0 / 0 | 79.7 | −0.1σ | +2.0σ | dynamics | v1 crosses the data: too low early, too high late. B equilibrium +8% (B23) |
| 4 | R4 150–249 | A | 0 / 0 / 0 | 73.9 | −2.9σ | −3.1σ | level | B21, B22 |
| 5 | R5 240–319 | B | 0 / 0 / 0 | 68.8 | −6.2σ | −5.4σ | level | Inherited from B28, plus B's flat tail (B29) |
| 6 | R4 0–99 | A | 6.3 / 1.4 / 0.42 | 67.9 | +0.3σ | +4.9σ | dynamics + level | Too slow rise (B18), then plateau +27 (B19/B20) |
| 7 | R5 240–319 | A | 0 / 0 / 0 | 66.2 | −5.0σ | −3.5σ | level | B28 carried into recovery |
| 8 | R4 0–99 | B | 6.3 / 1.4 / 0.42 | 66.0 | +1.5σ | +7.1σ | dynamics + level | B18, B19 |
| 9–12 | R5 0–79 and 80–139 | A, B | 4.5 / 0 or 2 / 0 | 51–53 each | −2 to −8σ | up to −12σ | level | B26 (seeding dose) and **B24 (incentive level effect)** |
| 13–17 | R5 140–239 | A, B | 4.5 / 1 or 0 / 0 | 40–44 each | −4 to −7σ | −5 to −6σ | level | B25, B27, B28 |
| 14, 18 | R4 480–539 | B, A | 7.65 / 1.7 / 0.51 | 43, 39 | −2.9σ, −1.5σ | +2.4σ, +2.2σ | dynamics | Rise too slow early, plateau too high (B31, B20) |
| 19 | R2 105–154 (old) | B | 9 / 2 / 0.6 | 38.7 | +3.5σ | +2.8σ | level | B overshoot under the full pulse (old) |
| 20–21 | R4 400–459 | A, B | 7.65 / 1.7 / 0.51 | 35, 34 | −2.0σ, −0.8σ | +0.1σ, −0.9σ | dynamics | Rise timing only |

**Grouped by cause:** the recovery path after a crash (#1–5, 7; about 470) > incentive composition and history in R5 (#9–17; about 420) > the u.7/u.85 ray level and the rise from reset (#6, 8, 14, 18, 20–21; about 290). Nearly all of it is **level** error. Pure transients (the first 20 ticks after a switch) are negligible.

**The same errors in old data (v1 in-sample, same σ):**
- The seeding plateau was already too low: R1 140–189 A, −2.0σ to −3.75σ (B26).
- The incentive level effect in B was already missing: R1 280–354 B, −1.9σ and −4.2σ (B24).
- B after a bridge campaign was already too low: R1 475–549 B, −1.4σ and −3.3σ.
- B was already too high under the full pulse: R2 105–204 B, +3.5σ and +1.1σ.

Crash floors were fitted well in old data (R1 355–404 −0.2σ / −0.7σ), because both old crashes had the same history. That is why B21 is new.

## 5. Explanations and minimal model changes, in priority order

1. **Incentive level effect and the depth of the partial cut (B24, B25, B32; old R1 B −4.2σ).**
   - *Candidates:*
     - (a) Brief: "promises accompany waiting cohorts". Members recruited or retained while an offer is on carry that promise, and leave when the offer falls below it. This is an M2 variant, the payment-based form.
     - (b) The incentive lowers churn (`gret`), a plain dynamic. It is pinned at 0 in v1 because R2 (incentive 2 with bridge) sits low.
     - (c) A separate incentive-led pool that joins only under incentive.
   - *Simplest form consistent with all cuts:* an **incentive-held stock H**, the non-core members recruited or retained while ui > 0, with promise level E_H. When ui < E_H, a fraction (E_H − ui)/E_H of H becomes at-risk and leaves at a **fixed** rate k2 ≈ 0.09/tick, bounded through a sigmoid.
     - It gives the magnitude ratio 0.53 at 2 → 1 (H2), the gap-independent rate (B25 against R1 and R2), and the shallower floor when E_H is lower or H is smaller (B21, B32).
     - Add a bounded steady incentive term (gret or iota with a cap) so that incentive raises the plateau (B24).
   - *Conflict:* the R2 full pulse is only 199 / 131 with incentive 2 (B35). Without item 3, a strong incentive term will over-predict R2. Fit items 1 and 3 together.
   - Lesson 4 applies: a cut-only effect gets a one-sided driver, and there is no mirror effect when the incentive rises.
2. **Post-crash floor and regrowth path (B21–B23, B28).**
   - *Candidates:*
     - (a) The floor is not a core but "at-risk members exhausted" (item 1), so it rises when the incentive history is shorter or lower.
     - (b) Disappointed members reconsider faster, or not everyone who leaves enters D (brief: "need time before reconsidering"). v1 has ρ 0.063, but the D pool is too large, which delays regrowth and deepens B28.
     - (c) v1's M1 credibility dip during departures suppresses regrowth right after a crash, while the data regrow at once (B22).
   - *Minimal change:* item 1 plus dropping or reshaping M1 (item 4). Then pin the recovery asymptote to ≈ 93 / 77 (H1), for example with a heavier weight on R4 250–399.
   - *Conflict:* the R1/R2 floors of 43 / 31 must still come out after 200-tick full-incentive histories. Under (a) they do, because E_H ≈ 1 and H is large there.
3. **The level map along the ray, and the bridge cost to A (B19, B20, B26, B35).**
   - *Candidates:*
     - (a) The bridge diverts more than outreach effort. For example it diverts the onboarding workforce ("workforce also needed by existing members"), so A's onboarding capacity falls with b. This is base structure.
     - (b) Incentive *before or with* recruitment is weak while incentive *after* recruitment is strong. This is an order/history effect, M2 expectation at recruitment time.
     - (c) Seeding saturates in dose (B26: 4.5 gives about 95% of 9 alone), so along the ray the incentive and bridge terms carry the u-dependence, and they are roughly linear.
   - *Minimal change:* local effort `us·(1 − b)` → `h(κ·us)·(1 − b)^m`, with a saturating dose and m ≥ 1 fitted. Keep the incentive term linear and bounded.
   - Whether (a) or (b) holds is **not identifiable** from R1–R5. It is what the reserve probe decides (§6).
   - *Conflict:* none known. R1 seeding 9 alone at 230 needs the dose saturation, not a change of pool size.
4. **Remove or re-drive M1 (B18, B31, H3).**
   - v1's M1 is driven by departures / members. The reset under control has large departures (the expectant share leaving) at the moment seeding starts, so credibility collapses and the rise lags by about 5σ at tick 20.
   - m2_all, which has no M1, already scores 0.456 / 0.293 on R4 / R5 against 0.361 / 0.203 for v1, and the same on old data (0.66 / 0.66 / 0.80).
   - v1 with g1 simply set to 0 collapses (0.13–0.30): the other parameters compensate for M1, which fits lesson 9 (a missing-structure stand-in). Refit rather than ablate.
   - *Candidates for the B31 deficit:* the depleted susceptible pool (D not yet reconsidered, which is base) or credibility loss (M1). Either way it is ×0.89 in both communities, and a *slow* credibility (a1 ≈ 0.02) driven only by disappointment exits would not touch the reset.
   - *Minimal change:* refit m2 (and m23) on R1–R5 with items 1–3. Keep M1 only as a slow, disappointment-driven form, and only if it improves the hold-out on R4 480–539.
   - *Conflict:* R3 (a pristine campaign) showed no slow crash-credibility effect 80 ticks after a crash. A slow M1 must have recovered within about 80 ticks, which the 20-tick gap still allows.
5. **B's recovery tail (B23, B29).** B is flat at 67–73 in both recovery tails, while v1 creeps to 84. Probably the B pool (NB 185) or βB is too large, which is a plain dynamic. Refitting on R4 250–399 and R5 240–319 fixes it. There is no conflict: R1 520–549 B at 117 is a post-bridge pipeline, not an equilibrium.
6. **Reset under control (B17, B18).** Already captured once item 4 is done. No change.

**Suggested refit protocol:** all five runs, log units, 3 restarts. Hold out R4 480–559 and R5 190–319 for the first pass, as a check on order and history. Stability gate at 4,000+ ticks. Check that no parameter sits at a bound, especially gret and the new k2.

## 6. Reserve-step proposal (120 steps; budget read 120 remaining; not spent)

**What is still unknown and matters for scoring:** B35. Is the low u.7 / u1 plateau (164, 199) caused by the bridge costing A, or by incentive given *with or before* recruitment being worth less than incentive given *after* it (R5 257)? Composition and order episodes toggle exactly these. The long-run recovery (H1) and the partial cut (H2) are now measured, so they do not need steps.

**Probe RC1 (fresh reset, 120 steps, one `run_schedule.py` call per segment with `--continue`, `--confirm` equal to the steps):**

| Ticks | Steps | seeding | incentive | bridge_outreach | Compares with |
|---|---:|---:|---:|---:|---|
| 0–59 | 60 | 6.3 | 0 | 0.42 | R4 0–99 (same seeding and bridge, incentive 1.4 from tick 0); R5 0–79 (seeding 4.5, bridge 0) |
| 60–119 | 60 | 6.3 | 1.4 | 0.42 | R4 90–99 (164 / 101): the same u.7 action, but the incentive arrives **after** recruitment |

**What each outcome decides:**

- **Segment 1 level (tick 50–59), the bridge cost.**
  - If A ≈ 150–165: the bridge costs A far more than its 42% effort share (seeding 4.5 alone gives about 200). **Adopt 3(a):** the bridge diverts capacity, with m > 1.
  - If A ≈ 190–210: the bridge costs little, so R4's low plateau is due to the incentive being present from the start. **Adopt 3(b).**
  - B tells us whether the bridge adds to B at incentive 0 over 60 ticks.
- **Segment 2 end vs R4 u.7 (164 / 101), the order effect.**
  - Within ±1.5σ (A ±8): the plateau is history-free and the incentive increment is additive. Item 1's steady term is calibrated as (segment 2 − segment 1) in a bridge background.
  - Well above, as in R5's +60: **incentive after recruitment ≫ incentive with recruitment.** This is an order effect worth modelling (an expectation set at recruitment), and it hits the order and composition categories directly.
  - Below: the incentive interacts negatively with bridge.
- The run also gives a third controlled-reset rise (B18) and a second u.7-seeding rise for timing.

**Alternative if the refit already separates 3(a) from 3(b)** (unlikely, since the current data confound them): `--continue` is not possible on R4 or R5 (runs are finished). A fresh 120-step long recovery tail would add little, because H1 is within 10%. So RC1 is the only recommended use. Keep the whole 120 for it. Its segments are already at the ~60-tick settle scale of A. Do not extend it: B would need ≥ 150 ticks to settle, which the reserve cannot buy.
