# Wildlife round-2 diagnosis (R3 = WL1, R4 = WL2)

Diagnostician, 2026-09-28. No steps spent, no model or plan files changed. Every number below is reproducible for free from
`toronto26-participant-kit/` with the scripts in `fits/wildlife/round2/`:

| Script | Output |
|---|---|
| `diag.py` | v1 prediction on R1/R2c/R3/R4, per-segment table, `diag.json`, plots `R3_v1.png`, `R4_v1.png`, `R1_v1.png`, `R2c_v1.png` |
| `rules.py` | decision-rule quantities for the four candidates, run from each run's **actual** initial reading (final.out used a mid-range initial); candidate held-out scores |
| `steady.py` | v1 long-run (2,000-tick) level map vs observed hold levels |
| `rank.py` | score-loss ranking and level/dynamics/transient split (`rank.json`) |
| `switches.py` | delays, t63 in linear and log units, noise, N/S predator coupling |

σ = 0.1 × std after tick 20 of all wildlife data (as `heldout.py`): prey N 4.56, pred N 0.053, prey S 4.00, pred S 0.049.
v1 = `fits/round2/v1_models/wildlife` (mA+mB, `AB_all3`). Plots: [R3](../toronto26-participant-kit/fits/wildlife/round2/R3_v1.png),
[R4](../toronto26-participant-kit/fits/wildlife/round2/R4_v1.png), old data [R1](../toronto26-participant-kit/fits/wildlife/round2/R1_v1.png),
[R2c](../toronto26-participant-kit/fits/wildlife/round2/R2c_v1.png) (black = data, red = v1 with ±1σ band, bottom = controls in u).

## 1. Summary

1. Held-out v1 score 0.419 (R3 0.467, R4 0.372); in-sample R1 0.481, R2c 0.537. **Predators are 59% of the lost score** (1,145 of 1,946 tick-obs units), exactly as on the old data (59%): the misfit is old, not new.
2. Verdicts: mA+mB (v1) is the only candidate within 2σ on all three pair-ranking quantities; mB+mC and base are dropped; mA+mC survives only by the letter (1 of 3 outside) and is refuted by the short-gap rule (−16.5σ). No H2 cohort delay (the release rule is not triggered on the pre-registered quantity). H4 not triggered (predators 2.34, inside 2.2–2.45), but v1 sits −2σ low at recovery.
3. Top losses: (a) predator reset transient under control, v1 +5 to +16σ high at t = 40–110; (b) predator recovery level 2.34 vs v1 2.23 (−2σ on every recovery tick); (c) level map at u ≈ 0.7: persistent corridor predator depression (v1 relaxes it away, +4–5σ) and habitat .37 prey (v1 +3–5σ).
4. v1 has structural faults that the new data expose: the predator block pulls Y back to a corridor-blind reserve Z (so every corridor effect is transient), the habitat level map is far too weak (hab .1 long-run 93 vs 67.5 observed, even in-sample), the fixed juvenile reset J0 = 30 (pinned at cap) makes a spurious 5-tick prey spike when hunting starts at reset, and v1 has **multiple equilibria under hunting 7** (long-run N 45, 25 or 12 depending on history).
5. Reserve (150): continue R3 with joint .7 for 120 ticks and release 30: settles the joint-box level, separates additive vs max-type predator composition, and measures pulse-length memory of the release boom.

## 2. Decision-rule verdicts (round2-experiments §4.2)

Mean of the last 10 ticks of the segment; candidates run from the run's actual initial reading and actions (`rules.py`).

| Rule / quantity | Observed | mA+mB (v1) | mA+mC | mB+mC | base | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Pair ranking: joint .85 prey N (R3 0–79) | 10.8 | 12.5 (+0.4σ) | 30.7 (+4.4σ) | 31.0 (+4.4σ) | 40.7 (+6.5σ) | |
| Pair ranking: joint .7 prey N (R3 290–349) | 28.4 | 24.5 (−0.9σ) | 34.0 (+1.2σ) | 53.6 (+5.5σ) | 60.5 (+7.0σ) | |
| Pair ranking: hunt 5 + hab .37 prey N (R4 80–139) | 23.5 | 16.1 (−1.6σ) | 31.6 (+1.8σ) | 58.4 (+7.6σ) | 67.0 (+9.5σ) | |
| → outside ±2σ on ≥ 2 of 3 | | 0 of 3: **keep** | 1 of 3: kept by the letter | 3 of 3: **drop** | 3 of 3: **drop** | mA+mB retained; mB+mC and base dropped. Note joint .7 and hunt5+hab.37 had not settled (N drift 17σ and 6σ; asymptotes ≈ 22 and ≈ 20.5); against asymptotes mA+mC is outside on all three. |
| Release overshoot: release +30 after joint .85, prey N / S | 144.8 / 129.5 | 130.0 / 123.8 | 154.3 / 144.7 | 114.8 / 96.0 | 117.5 / 97.1 | **Not triggered** (data not ≥ 20% above every candidate; mA+mC is above). The *peak* N is 201 (t 117) vs the best candidate 167 (+20%), and after joint .7 the data are *below* v1 by 11% / 20% (129.4 vs 145.3, 104.3 vs 131.0). The overshoot is history-dependent in size, not delayed: no cohort delay (H2) from this rule; see B19. |
| Short gap: prey S at end of the 30-tick gap (R3 260–289) | 124.5 | 116.1 (−2.1σ) | 58.4 (−16.5σ) | 94.7 (−7.5σ) | 95.8 (−7.2σ) | **Food-stock gap memory of the mA+mC kind refuted.** Above the 95–116 "juvenile deficit" band; closest is mA+mB. No measurable gap memory at all (B20). |
| Predators after release +150 (R3 480–499), N / S | 2.34 / 2.33 | 2.23 / 2.22 | 2.07 / 2.02 | 2.33 / 2.32 | 2.33 / 2.32 | **H4 not triggered** by the letter (inside 2.2–2.45). But v1 is −2.0/−2.3σ low on every late recovery tick (B25), and mA+mC is −5/−6σ. |

Candidate held-out scores (mean of 4 observables): R3 v1 0.467, mA+mC 0.397, mB+mC 0.422, base 0.402; R4 v1 0.372, mA+mC 0.379, mB+mC 0.394, base 0.386. On R4 every candidate is ≈ 0.38: R4's losses are base-structure (predator block, level map), common to all candidates (§1.3 of round2-experiments). mB+mC and base score better on R4 predators (0.37 vs 0.28) only because their predators relax faster.

## 3. Behaviour catalogue (continues B1–B15 of `plans/wildlife-plan.md`)

Status is against v1. Error sizes in σ as above. Categories: S sustained, O order, R recovery spacing, C composition.

Settling (`greybox.common.settle`, per segment): settled only R3 80–199 prey (predator S drift 4σ), R3 350–499 (all four), R4 260–319 predators. **Not settled:** every joint-box hold (R3 0–79 predators drift 46–58σ; R3 200–259 prey 4σ, pred N 8σ; R3 290–349 prey N 17σ), R4 hunt 5 (14σ, 43σ), hunt5+hab.37 (pred N 20σ), hab .37 alone (post-release decline −1.7/tick), hab.37+corr.7 (prey still +0.06–0.09/tick), corridor .7 prey N (10σ), final 30-tick recovery (all rising).

| ID | Behaviour | Evidence | v1 status | Cat. |
|---|---|---|---|---|
| B16 | **Reset transient under hunting: no reset boom.** Hunting 5 from reset holds N flat at 80–93 until t ≈ 45, then an abrupt drop (93 → 83 in 5 ticks) and a slide to 68.7 (asymptote ≈ 62). S falls from t = 0 (88 → 70 by t 30 → 36.9). The "food runs out" break comes at t ≈ 45 instead of 22–30 without hunting. Under joint .85 from reset, prey fall monotonically to 10.8/11.1. | R4 0–79, R3 0–79 | **Not captured.** v1 makes a spurious spike at t 5 (N 101, S 114; the J0 = 30 pipeline flush) and holds S at ≈ 105 to t 35: S +4.2σ mean over 0–79 (53 lost), up to +8σ at t 20–40. Joint .85: N −2σ too slow at t 15–40. | all (every episode starts at reset under control) |
| B17 | **The predator reset transient is faster under control.** Predators at t 78: recovery (R1) 2.90/2.77, hunt 5 (R4) 2.48/2.30, joint .85 (R3) 1.98/1.99. The slow tail's target depends on the control. After the corridor closes at R3 t 80, predators go 1.99 → 2.20 in 9 ticks, stay flat for 30 ticks, then creep to 2.36 by t 140. | R3 0–140, R4 0–80 | **Not captured.** v1 +11 to +16σ at the end of R3 0–79 (142 lost), +5 to +7σ in R4 0–79 (124 lost); v1 then jumps to 3.0 after the R3 corridor closes (+14σ over 80–109, 56 lost). | all |
| B18 | **Joint-box levels.** Prey N/S: joint .85 10.8/11.1 (80 ticks), joint 1 7.6/8.1 (still falling), joint .7 28.4/24.7 (still falling, asymptote ≈ 22/23). Predators: 2.03 falling / 1.78/1.73 / 1.94/1.84. First-tick prey drop at joint 1 is −15 per region. | R3 0–79, 200–259, 290–349 | N captured (< 1σ). **S at joint .7 not captured:** 14.6 vs 24.7, −2.5σ over the whole hold (42 lost). At joint 1 v1 stops at 10.2/9.3 while data keep falling (N −0.6σ, growing). | R, C |
| B19 | **The release boom's size depends on history, not on a delay.** Release after joint .85 from reset: N peak 201 at +37, S 167 at +35, then a 5-tick plateau and an abrupt crash (−7/tick) to 134 by +60. After joint 1 (60 ticks): N 159/S 141 at +30, still rising (gap ended). After joint .7, which started from a boom: 133/110, small. R4 release under hab .37: 126/128, then a decline to 88/79. R1 after hunting 7: 172/156. Rise rate up to +7.4/tick (N). Reading: from reset the food stock is full and hunting keeps prey from eating it; after a boom it is empty. | R3 80–140, 260–290, 350–380; R4 140–200 | **Not captured.** v1 peaks 167 (−7σ at the peak, −3.2σ last-10 of +30) after joint .85 and overshoots after joint .7 (+3.5σ N, +6.7σ S at +30). v1's crash is smooth. | R, O |
| B20 | **No gap memory.** After a 30-tick gap the regrowth after joint 1 is as fast as after joint .85 (N at +9 ticks: ≈ 44 from 7.5 vs ≈ 51 from 10.8, a similar or faster per-capita rate). S at the end of the gap is 124.5. | R3 260–289 vs 80–109 | Captured by v1 (−2.1σ on S, −2.8σ on N at gap end: slightly slow regrowth). | R |
| B21 | **Habitat map is strong already at u = 0.7.** hab .37 + corridor .7: 77.0/70.6 (settled within 0.1/tick); corridor .7 alone 117.7/88.8, so hab .37 alone ≈ 79/77 by division, i.e. ≈ 78% (N) of the hab .1 effect (67.5/64.7). The hab .37 hold after the hunting release ends at 89.7/81.1, still falling −1.7/tick. | R4 140–259; R1 250–289 | **Not captured, and never was.** v1 long-run hab .37 = 102/84, hab .1 = 93/78 (data 67.5/64.7: +5.5σ in-sample on R1 250–289). R4 200–259 N +5.0σ (47 lost), 140–199 N +2.9σ in the 2nd half. | S, R, C |
| B22 | **The corridor's predator depression is persistent.** Corridor .7 for 120 ticks (R4 200–319, with and then without hab .37): predators flat at 1.93–1.97 (settled, drift 0.02σ). Prey N under corridor .7 alone 117.7 vs recovery 121. | R4 200–319 | **Not captured.** v1 relaxes predators back towards Z (corridor-blind): +4.3/+5.0σ over 260–319 (95 lost), long-run corridor 1 predators 2.22 = recovery level. v1 long-run corridor prey N 128–129 (above recovery!) vs 117.7 (+2σ). The same error was in-sample (R1 330–369 end +3.8/+5.0σ). | S, C |
| B23 | **Predator composition is not additive (≈ the largest single depression).** Corridor .7 alone 1.95/1.92; joint .7 (adds hunt 4.9 + hab .37) 1.94/1.84; joint 1 1.78/1.73 vs corridor 1 alone 1.69/1.64 (R1, 40 ticks) and hunt 7 alone 1.90/1.86. Hunt 5 + hab .37 without corridor: 2.08/1.97, still falling. | R3, R4, R1, R2c | Partly: v1 joint .7 within 1σ, joint 1 −1.3 to −1.6σ. Its product/additive form will be wrong at other combinations. | C |
| B24 | **Predator closing overshoot only after corridor-only holds.** Closing after corridor .7 at high prey (R4 320): predators 1.95 → 2.58 in 30 ticks, still rising, above recovery (2.34); prey 118 → 135 (above 121), still rising. Closing after joint pulses (R3 260, 350, low prey): predators rise only to 2.09 and 2.25 with t63 5–9 ticks, no overshoot. R1 (corridor 1 at high prey) overshot to 2.6. | R4 320–349, R3 260, 350, R1 370 | Partly: v1's R4 end level is right (0.4σ) but it rises too fast (2.51 at +6 vs 2.17: rms 4.4σ over the segment); after joint pulses v1 is +1–3σ high. | R, O |
| B25 | **Recovery predator level ≈ 2.33–2.34, reached slowly** (R3 110–199: 2.17 → 2.37 over ≈ 60 ticks after the release; R3 380–499 flat 2.30–2.34). R1's late recovery read 2.28–2.30. | R3 110–199, 380–499 | **Not captured:** v1 2.22–2.23, −2σ on every late recovery tick (R3 380–499: 138 lost; 110–199: 114 lost). v1's yb/Yref were fitted to R1's lower tail. | all (recovery is the most-held setting) |
| B26 | **Hunting × habitat interaction is weaker than v1.** Hunt 5 + hab .37: N 67.9 → 23.5 (asymptote ≈ 20.5), S 36 → 16.6, t63 21 ticks (N). | R4 80–139 | Partly: v1 too low and too fast (N −1.5σ, 16.1 at the end; v1 long-run 13/13.7). | C, O |
| B27 | **One-tick momentum at pulse onset after a boom.** At the joint .7 onset during a boom (R3 290), prey still rise +3.3/+4.7 on the first tick and turn down at tick 2. | R3 290–295 | Not captured (v1 turns at once: −5.7σ at t 292; ≈ 10 lost). Small. | R |
| B28 | **Delays and symmetry.** Controls act on the first tick (prey d1 −2 to −15; predators −0.02 to −0.09). Prey on/off t63: on 5–21 ticks linear, 10–26 log; off 8–17 linear, 6–10 log: off is faster in log units (additive regrowth, B2), on/off symmetric in neither unit. Predators: t63 2–10 ticks after joint switches, 24–43 ticks when only habitat or hunting change (slow numerical response). | `switches.py` | Dynamics captured to ≈ 1 tick for prey; the predator time scales are partly wrong (B17, B24). | all |
| B29 | **Noise** 0.39–0.60% of level on all four, proportional (flat windows R3 420–500, R4 270–320). | `switches.py` | Captured (log units). | — |
| B30 | **Predators N ≈ S** (ratio 1.01 R3, 1.05 R4 after t 30; range 0.97–1.23); diff correlation 0.45–0.5; predator level barely tracks local prey (corr 0.31/−0.02). | `switches.py` | Captured (shared parameters) but v1's per-region prey dependence makes N/S differ under hunt 7 (R2c: v1 2.10/1.76 vs 1.90/1.86: +3.8/−2.1σ in-sample). | all |
| B31 | **Surprise (model, not data): v1 has multiple equilibria under hunting 7.** A constant hunt 7 from reset settles at N = 45.3; after 200 ticks of recovery it sits at 24–26 for ≈ 600 ticks and then collapses to 11.9; after a hab .1 pulse it collapses at ≈ 600. Data: 25.5 flat for 150 ticks (R2c). Constant-quota harvest with a near-step food intake (kF at its 0.05 floor) is bistable. | `steady.py`; ad hoc runs in this diagnosis | Model risk for every long hunting hold (sustained category): a 1.2–3σ level jump at an arbitrary time. The G8 constant-action gate only checked range/mean of the tail, not history dependence. | S |

Relationships (battery item 7): predators follow prey with a slow lag only when prey change a lot (hunting, joint pulses; R4 164–200 predators 2.04 → 2.33 as prey boom), not under habitat (B6 still holds); predator N/S coupled (B30); the regional prey sum dips with the corridor (B7 holds: R4 200 −3.3/−2.9 on the first tick).

## 4. Score-loss ranking (`rank.py`)

Lost = Σ over ticks of 1 − 1/(1 + |err|/σ). R3 + R4 lose 1,946 of 3,400 tick-observable units. By observable: prey N 439, **pred N 573**, prey S 363, **pred S 572**. By type: level 816, dynamics 907, transient 223. Type rule: *transient* if the first 15 ticks carry ≥ 50% of the loss; *level* if the second half carries ≥ 50% with a same-sign mean error ≥ 1σ; else *dynamics* (for 60–90-tick unsettled holds "dynamics" is mostly a slow-level error).

| # | Run, segment | Observable | Lost | Type | Error | Cause (B-ID) |
|---:|---|---|---:|---|---|---|
| 1 | R3 0–79 joint .85 from reset | pred S | 72.9 | level | +16σ 2nd half | B17 |
| 2 | R3 380–499 recovery | pred S | 71.0 | level | −2.2σ | B25 |
| 3 | R3 0–79 | pred N | 69.4 | level | +11σ | B17 |
| 4 | R3 380–499 | pred N | 67.1 | level | −1.9σ | B25 |
| 5 | R4 0–79 hunt 5 from reset | pred N | 65.2 | level | +6.9σ | B17 |
| 6 | R4 0–79 | pred S | 58.5 | level | +4.9σ | B17 |
| 7 | R3 110–199 recovery | pred S | 57.7 | dynamics | +1.4σ then −1.7σ | B17 tail + B25 |
| 8 | R3 110–199 | pred N | 56.5 | dynamics | same | B17 + B25 |
| 9 | R4 0–79 | prey S | 52.7 | dynamics | +4.2σ mean | B16 |
| 10 | R4 80–139 hunt5+hab.37 | pred S | 49.1 | dynamics | +4.6σ | B17/B23 |
| 11 | R4 260–319 corridor .7 | pred S | 48.6 | level | +5.0σ | B22 |
| 12 | R4 80–139 | pred N | 48.0 | dynamics | +4.1σ | B17/B23 |
| 13 | R4 200–259 hab.37+corr.7 | prey N | 47.4 | level | +5.0σ | B21 |
| 14 | R4 260–319 | pred N | 46.2 | level | +4.3σ | B22 |
| 15 | R3 380–499 | prey N | 44.7 | dynamics | +0.9σ | recovery prey N 121.3 vs v1 123 (0.4σ) + release overshoot tail (B19) |
| 16 | R3 110–199 | prey N | 42.7 | dynamics | −2.1σ | B19 (crash timing) |
| 17 | R4 140–199 hab .37 | prey N | 42.6 | level | +2.9σ 2nd half | B21 |
| 18 | R3 290–349 joint .7 | prey S | 42.1 | level | −2.5σ | B18 |
| 19 | R4 260–319 | prey N | 39.1 | dynamics | +2.0σ | B22 (corridor prey level) |
| 20 | R4 200–259 | pred S | 38.2 | level | +2.3σ 2nd half | B22 |

Grouped: predator reset transient (B17) ≈ 470 (24%); predator recovery level (B25) ≈ 250 (13%, partly overlapping B17 in 110–199); corridor/habitat level map (B21, B22) ≈ 260 (13%); reset-under-hunting prey (B16) ≈ 80; release-boom history (B19) ≈ 150.

**Old data (R1 + R2c):** v1 loses the same way: pred N 602, pred S 570, prey N 417, prey S 383; top pairs are R2c hunt 7 predator N level (+3.8σ, three 50-tick blocks ≈ 39 each: B30), R1 habitat level prey N +5.3σ (B21), R1 hunt 3.5 predators −2.2σ, R1 release predators. So B21, B22, B25 and B30 were already in-sample misfits; B16, B17 (under control), B19's history dependence and B31 are new.

## 5. Explanations and minimal model changes, in priority order

1. **Predator block (B17, B22, B23, B25, B30; ≈ 45–50% of the loss).**
   - Cause: v1's `Y → Z → Y*(local prey)` is a pure relaxation. Y is pulled back to Z whatever the corridor does, so corridor losses are only transient (B22); Z decays at a fixed kZ from a Y0-dependent start, so the reset tail cannot depend on the controls (B17); Y* uses local prey, so N ≠ S under hunting (B30); Yref/yb were fitted to R1's still-falling tail (B25).
   - Simplest explanation (plain dynamic + the brief's transit): a numerical response. Predator net growth rate r(t) = a·g(prey) − m, where g saturates at low half-saturation (≈ 3–10) on a **shared** prey signal (the mean of N and S, or predators as one pool), plus transit loss. From reset, the excess predators die at rate m − a·g(prey), faster when prey are low (B17 joint .85 vs recovery), which keeps R1/R2's affine-in-Y0 finding (the rate is independent of Y at a given prey path).
   - Corridor: make the transit stock count against predators at steady state, e.g. put the corridor into the target, Y* × (1 − cY·s(uc)) with a saturating s, and compose depressions as 1 − max-type or a saturating sum (B23: joint ≈ largest single depression; a one-sided, bounded form per lesson 4/8).
   - Conflicts: must keep the R1 corridor-closing overshoot (2.6) and the R4 one (2.58), while not producing one after joint pulses (B24). A transit stock that refills the region when the corridor closes gives the overshoot only if the region's target is high (high prey), which matches B24. Check the R2 affine transient (review R2) still holds.
2. **Habitat level map (B21; ≈ 10%, and it was +5σ in-sample).**
   - Cause: in v1 habitat acts mainly through exposure (eH ≈ 0.8–0.95) and weakly through food renewal (hF_N 0.24, hF_S 0.16), with a food stock whose intake is pinned at the kF floor. The long-run habitat effect is ~40% of the observed one at u = 1 and much less at u = 0.7.
   - Minimal change: habitat sets the prey carrying level directly and concavely in u, e.g. renewal × (1 − hF·s(uh)) with s(u) = u^γ/(u^γ + c) or 1 − exp(−u/u0), and refit hF_N/hF_S with R1 250–289, R2 30–54/130–154 and R4 140–259 as the anchors (67.5/64.7 at u = 1, ≈ 79/77 at u = 0.7).
   - Conflicts: B6/B11 (symmetric on/off, habitat attractor from above and below, predators unchanged under habitat) must still hold; with food renewal cut, the release booms after habitat pulses stay small (R1 290: no overshoot), which is consistent.
3. **Reset state of the juvenile pipeline and the food crash (B16, B19; ≈ 12%).**
   - Cause: J0 = 30 per stage (pinned at its cap) flushes ≈ 180 recruits in the first 6 ticks: a spurious spike whenever hunting holds prey low at reset. kF at its floor means intake stays smooth, so the post-peak crash is too slow, and a bistable constant-quota harvest (B31) follows.
   - Minimal change: set J0 from the observed no-control boom rate (≈ +6/tick nursery cap from t 0: J0 ≈ cap/a2, not 30), or start the pipeline empty and let F0 carry the boom; replace the kF floor with a starvation term (prey mortality rising when intake per capita < need), which gives the abrupt crash (B4, B19) without the near-step intake that makes the quota harvest bistable.
   - Test: R4 0–79 (no boom under hunt 5, break at t ≈ 45), R3 80–140 (201 peak, 5-tick plateau, crash), R3 350–380 (small overshoot after a boom), R1/R2 reset booms (196 at t 18–24, independent of X0).
   - Conflicts: G4 (the R1 18-tick stall) was the reason for the pipeline; the starvation form may explain that stall as the moment the food runs out, so the pipeline might become unnecessary. Check that mB still earns its place (it is still the only nursery evidence: the additive +5–7/tick cap).
4. **Joint-box S level (B18) and hunt × habitat (B26).** Likely follow from items 2–3 (S harvest exposure too high when habitat is low: v1 S 14.6 vs 24.7 at joint .7). Refit after 1–3, then check. If still off, give harvest exposure a saturating habitat term (eH·s(uh)).
5. **Model gate for B31.** Add a history-dependence gate: the same constant action after 3 different 200-tick prefixes must reach the same level (within 0.5σ) by tick 2,000. v1 fails it at hunting 7. A starvation term with smooth intake (item 3) should remove the bistability; if not, bound the realized harvest by a fraction of prey above the refuge.

Mechanism pair: the new data do not change the choice. mA+mB stays; mA+mC's gap memory is refuted (B20); mC settlement remains unused. The predator-closing asymmetry (B24) is the only new hint of settlement competition (predators do not re-settle into regions with depleted prey), but the transit refill against a prey-dependent target (item 1) is the simpler explanation; test it before reviving mC.

## 6. Reserve-step proposal (150 steps; not spent)

What is still unknown after R3/R4, most score-relevant first: (1) the joint-box long-run level (every joint hold was unsettled at 60–80 ticks; the scorer holds pulses much longer); (2) whether the predator composition is max-type (B23), which needs a *long* joint hold with the corridor at 0.7; (3) whether the release boom grows with pulse length (food rebuilding during a pulse, B19); (4) the settled hab .37 level (only inferred by division).

**Proposal (150 steps): continue R3 on a copy (R3 ended at t 500 settled under recovery, which matches R3's own pre-pulse state at t 200).**

```sh
cp data/wildlife/R3.json data/wildlife/R3c.json
python run_schedule.py --continue data/wildlife/R3c.json --confirm 150 --segments '[{"steps": 120, "action": {"hunting_quota": 4.9, "habitat_protection": 0.37, "corridor_access": 0.7}}, {"steps": 30, "action": {"hunting_quota": 0.0, "habitat_protection": 1.0, "corridor_access": 0.0}}]'
```

Run it as two `--continue` calls (120, then 30) with `greybox.common.settle` after the first, per §8.1.

| Measurement | Outcome → decision |
|---|---|
| Prey N/S at t 610–619 (joint .7, 120 ticks) | ≈ 22/23 (the R3 290–349 asymptotes): the joint-box level is set by controls and the model can be fitted to it; well below (≤ 16/13, v1's long run): the slow decline continues and a slow food/predator state is needed. |
| Prey trajectory t 500–560 vs R3 290–349 (the same pulse after a settled recovery instead of after a boom) | Identical after ≈ 20 ticks: no pulse-onset memory beyond the prey level; different: the food stock carries the history (sizes the mA drawdown term, B19). |
| Predators at t 610–619 | ≈ 1.93 (the corridor .7 level): max-type composition (B23), use a max/saturating form; clearly below 1.84 (still falling): the depressions add, and the prey-driven part is slow. |
| Release peak at t 620–649 vs R3 350–379 (133/110 after a 60-tick joint .7 that began in a boom) | Larger (≥ 150): food rebuilds during a long pulse (mA renewal under habitat .37 is not negligible); equal: the overshoot depends on the pre-pulse food state only. |

Fallback if R3 has expired: a fresh reset with recovery 60 (to pass the reset boom; the R1/R2/R3 booms are identical so this also re-checks the reset rule), then joint .7 for 90 → 150 steps; the release tail is then dropped. **Second choice** if the reviewer prefers the habitat map: fresh reset, hab .37 alone for 100 ticks then hab .37 + hunt 3.5 for 50 (settles hab .37 from reset, and a mid-hunting × habitat composition).
