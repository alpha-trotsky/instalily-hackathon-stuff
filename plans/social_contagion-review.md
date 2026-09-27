# social_contagion: Phase B review

Reviewer: separate agent, 2026-09-27. I spent no simulator steps. Budget: CAP 1,000, 950 spent, **reserve 50**.
Paths are under `toronto26-participant-kit/`. Review artefacts are in `fits/social_contagion/review/`:
- `errplot.py`: overlays fits on R1 and R2, with log-error panels.
- `longrun.py`: 4,000-step rollouts at constant controls.
- `base_r12` / `m12_r12` / `m23_r12` / `m13_r12`: `.json` and `.log` files of refits on **R1 + R2 jointly**.
- `base_r12.png` and `pairs_r12.png`: plots of those refits.

## 1. Independent behaviour list (written from the raw data and plots before I read the plan)

Ticks are 0-based observation indices.

| ID | Behaviour | Evidence |
|---|---|---|
| R1 | **Reset drop:** both communities fall to ×0.75–0.77 of the reading within about 12 ticks. The a/b ratio is kept. The decay *accelerates*: the excess shrinks per 2 ticks by ×0.77, 0.72, 0.65, 0.60, so k rises from about 0.13 to 0.26. That shape is not first-order and points to a lag stage | R1 0–15 (61.5 → 46.3 / 38.6 → 29.1); R2 0–15 (48.6 → 37.4 / 37.8 → 28.3) |
| R2 | **Organic growth at recovery:** near-linear, +0.2/tick in A and +0.25/tick in B. It is not settled after 85 ticks. a/b drifts from 1.60 to 1.31. In R2 it is weaker (A +0.1, B ≈ 0) | R1 15–100; R2 12–25 |
| R3 | **Local seeding on:** dead time of 5–6 ticks, then a sigmoid rise. A peaks at +5.8/tick and saturates *sharply* at 230, flat from tick 170. B is ⅓ as fast and is still rising at the end (+0.2/tick) | R1 100–190 |
| R4 | **Local seeding off:** a plateau of about 6 ticks, then a slow decline with k ≈ 0.025 towards about 110 (A) and 90 (B). It is **not** back to the P0 level. On is about 4× faster than off, so they are asymmetric | R1 190–280 |
| R5 | **Incentive on (after a campaign):** A's decline (−0.47/tick) stops within about 5 ticks; B rises at +0.3 → +0.15/tick. **Incentive on (from a low base):** +0.4/tick above organic in both communities, with no fading over 30 ticks | R1 280–355; R2 25–55 |
| R6 | **Incentive off: 0-tick crash**, clean first order with k ≈ 0.09–0.10 in both communities, to an **absolute floor of A ≈ 43–44 and B ≈ 31–33**. The floor is the same in both runs even though the runs had different readings (R2's reset trough was 37.4, below its crash floor of 43.1). Members recruited by seeding at incentive 0 (R1: 128 before the incentive) leave too | R1 355–400; R2 255–300 |
| R7 | After R2's crash, B turns up by itself (+0.27/tick) while A stays flat. R1's crash (no earlier bridge work) shows almost none of this (+0.03/tick) | R2 287–305 vs R1 395–405 |
| R8 | **Post-crash campaigns are weak:** seeding 9 + bridge 0.6 after the R1 crash gains A +34 / B +13 in 20 ticks. The same seeding and bridge in pristine R2 (with incentive 2) gains **+61 / +23**, a ratio of 0.56–0.58 in *both* communities. The pristine local campaign (R1 100) gains +70 / +22 | gains computed from data |
| R9 | **Bridge 1.0 + seeding 9 (post-crash):** A is flat for 15 ticks and then accelerates; B rises steadily and then accelerates | R2 305–345 |
| R10 | **Growth continues after a bridge campaign stops.** At bridge 1.0 both communities keep growing, with the rate *peaking 15–25 ticks after the stop*; a/b is locked at 1.04, and growth is still +0.4/tick at the end. At bridge 0.6, A overshoots for 15 ticks and then declines slowly, and B grows +1.1/tick for 45 ticks and then **stops abruptly** at 118, which looks like a pipeline draining rather than a persistent tie | R2 345–400; R1 475–550 |
| R11 | **Full pulse held 200 ticks:** A rises to 199 with no overshoot and **no sag**, flat for 100+ ticks; B reaches 131. A is lower than under local seeding alone (230) and B is higher | R2 55–255 |
| R12 | Noise is proportional, 0.25% of the level (log units) | battery |
| R13 | The crash (k 0.09) is about 4× faster than the decline after seeding stops (k 0.025), which settles far higher. Leaving is governed by incentive history, not by how a member was recruited | R6 vs R4 |

## 2. Comparison with the catalogue and the current best fit

Current best fit: **`m23_r12`** (m2 + m3 refitted on R1 + R2, 2 restarts, cost 11,231). The other refits on the same data and σ:

| Fit | Cost | Stopped at | Score R1 | Score R2 |
|---|---:|---|---:|---:|
| base | 44,640 | — | 0.598 | 0.342 |
| m12 | 19,972 | nfev 64 | 0.544 | 0.624 |
| m23 | 11,231 | — | 0.650 | 0.738 |
| m13 | 37,612 | nfev 200 | 0.485 | 0.426 |

Scores use σ = 0.1 × std. Error plot: `fits/social_contagion/review/pairs_r12.png`. The Run-1 fits all failed on R2 (scores 0.23–0.40, `pairs_r1_on_R2.png`), so the structure does not transfer between runs.

| Behaviour (mine / catalogue) | Captured? | Evidence from the `m23_r12` error plot |
|---|---|---|
| R1 / B1: reset drop | **partly** | Reproduced through e0 = 0.58 (M2 disappointment at reset). The accelerating shape is not reproduced. After the drop, A's log error reaches −0.1 at ticks 30–60 in R1 |
| R2 / B2: organic growth | **partly** | A is too low in R1 0–100 (−0.1 log). R2 is fine |
| R3 / B3: seeding dead time and saturation | yes (base: lag stages + churn balance) | Spike of +0.17 log at R1 105–110 (dead time and slope slightly off) |
| R4 / B4: slow decline after seeding stops | yes | Error within ±0.05 |
| R5 / B5: incentive retains, raises B | **not captured (B)** | iota and shi → 0. R1 B is flat at 95 in the model against 91 → 107 in the data (error −0.1). A is fine only because of the retention term |
| R6 / B6 / B11: crash to an absolute floor | yes for A; B about +0.2 log too high at R2 265–290 | M2 churn for all members, balanced by reconsideration. The floor is emergent, not structural. See G2 |
| R7 / B16: B turns up after R2's crash | partly | Through m3 R, which is standing in for this |
| R8 (not in catalogue): post-crash campaign deficit of 0.57× | **captured only implicitly** | m23 fits R1 435–475 to ±0.05, through the D pool and R. Nothing has tested whether this is history (M1) or composition (incentive × seeding). See G4 |
| R9 / B15: slow start at bridge 1.0 | yes (through R) | ±0.05 |
| R10 / B9 / B14: growth continues after bridge | **A yes; B no in R1** | R1 B is −0.15 to −0.2 log at 500–550. The model is at 100, the data at 118. The abrupt stop at 118 is not reproduced |
| R11 / B12: full-pulse plateau, no sag | yes | ±0.02 |
| R12 / B10: noise | yes (log units) | — |
| R13: exit rate set by incentive history | yes (M2) | — |
| B13: incentive from a low base | partly | R2 A is +0.15 log at 40–55 |

## 3. Gaps

**G1 (high): the base is not identified.** Parameters are pinned or have run away in every refit, so the pair ranking reflects which module best masks base misfit, not which mechanisms are active (lesson 9). Examples from `m23_r12`:
- NB ≈ 1.0e5 (the code cap), NA 3.6e4, betaB 10.5 (at the code's cap of 10), kapA 8,486, om 31, qa 0.997
- psiA = 0, and tauA = tauB = iota = shi = 0

So the onboarding queue is never used, pools are effectively infinite, the incentive recruits nothing directly, and bridge introductions act only through the m3 accumulator. m12 and m13 run away as well (tauB 5e21, iota 162 or 5e21).
- *Fix:* restructure the base before running any bootstrap.
  1. Bound pools to physical sizes. A saturates at about 230 under full seeding, so N_A is roughly 250–400.
  2. Either drop the onboarding queue, or cap kap and qa to ranges where it acts.
  3. Give the introduction path its own lag (see G3).
  4. Refit with at least 3 restarts and `--horizons 150,400`.

  Do not use the bootstrap until no parameter sits at a bound.

**G2 (high): the crash floor has no structure.** The floor is absolute: A ≈ 43–44 and B ≈ 31–33 in both runs, while the reset troughs differ (46.3 and 37.4). The model instead uses M2 churn on *all* members, balanced against reconsideration. The equilibrium, and so the 4,000-step level after any incentive cut, depends on this balance, which rests on pinned parameters.
- *Fix:* add an explicit core pool that is never disappointed. It is also the equilibrium under recovery, since the floor is flat after R1's crash. Apply M2 disappointment only to non-core members (or to members who experienced the offer). Test this against R2's floor, which is 5 above its reset trough.

**G3 (high): M3 evidence is confounded with a missing long introduction lag.** After R1's bridge 0.6 campaign, B grows linearly and then *stops abruptly* 45 ticks later, which is a pipeline signature. After bridge 1.0 the growth peaks 15–25 ticks after the stop. m3 fits R with g3 at its cap (10.5), a3u 0.0012 and a3d 0.004, which makes R a near-permanent integrator of bridge work. The base's introduction path (tau) has no lag beyond the 2 local-outreach stages and is set to 0.
- *Fix:* add a separate 3–4 stage lag (deliberative audience, or introductions → relationship → onboarding) on the bridge path in the base, refit base, m23 and m12, and check whether m3's gain survives. If m3 is still needed, R7 is the real M3 signature: B rose by itself only after 200 ticks of earlier bridge work.

**G4 (high): M1 has no test, and one unexplained behaviour (R8) could be M1.** No P5 gap test was run. The M1 module can hardly act in the fitted base: its driver is queue/capacity, and with qa → 1 and a huge kap the queue never forms. So "no evidence for M1" is partly structural.

R8 is the one behaviour M1 could explain. Post-crash seeding + bridge 0.6 recruits only 0.56–0.58× what the same seeding and bridge recruited from a pristine state, with the ratio equal in A and B. There are three candidate explanations, and nothing yet tells them apart:
- (a) **M1:** credibility lost at the crash, from disappointment or broken promises.
- (b) **Base:** the disappointed pool depleting susceptibles.
- (c) **Composition:** R2's pristine campaign had incentive 2.

R11 (no sag under 200 ticks of sustained heavy seeding) is weak evidence against the backlog-driven M1 thesis. The thesis is also missing two drivers: **broken promises at an incentive cut** ("promises accompany waiting cohorts") and **departure events**.
- *Fix:* the reserve probe in §4. Also add those two alternative M1 drivers as options in the m1 module.

**G5 (medium): coverage holes from §4.2.** These were not run:
- P2 (seeding at mid level): the linearity of the main control is unknown.
- A clean P3 of seeding + incentive at bridge 0.
- P1 bridge on/off with seeding held constant.
- The P5 gap test.
- The M2 ramp-versus-step test.

P9a and P9b were run only across different histories, not from the same state. Scoring's sustained and composition episodes will use arbitrary mid-levels.
- *Fix:* the modeler should flag these as extrapolation risk. If the reserve is not used for §4, a P2 (seeding 4.5, 35 ticks after a 15-tick P0) is the next-best 50 steps.

**G6 (medium): the long-horizon equilibrium is unmeasured and differs between fits.** Recovery was never held for more than 100 undisturbed ticks from reset, and organic growth was still going. The fits disagree on where 4,000-step recovery ends up (`longrun.py`):

| Fit | Recovery level at t500 |
|---|---|
| m23 | 129 / 94 |
| m12 | 167 / 84, then 87 / 78 at t4000 (slow overshoot) |
| base | 77 / 64 |

Over 4,000-step episodes this equilibrium dominates the score.
- *Fix:* the modeler must add a prior. The crash floor (flat for about 50 ticks after a crash, R6) and R2's weak organic growth suggest a low recovery equilibrium. m23's 129 is probably too high. Check the model against R1 395–435 and R2 285–305, where it should be flat.

**G7 (medium): the incentive's direct recruitment is lost** (iota = shi = 0 in m23). R1 280–355 B is under-predicted by 0.1 log, and R2 25–55 is off by up to 0.15. M2 should also carry *attraction relative to E*, not only disappointment, and the base should have a bounded incentive-recruitment term with a cap on iota.

**G8 (low): reset shape.** The reset drop accelerates, while the model uses a first-order M2 exit from e0. A single lag stage on disappointment exits, or E rising from 0 towards e0, would fix the first 15 ticks of every scored episode. The gain is small, but it appears in all 40 episodes.

**G9 (low): stability.** The 4,000-step rollouts in `longrun.py` are bounded for every fit (no runaways). However, m12 shows a slow overshoot of 167 → 87 under recovery, and the caps in `simulate` (N ≤ 1e5, beta ≤ 10, g3 ≤ 10) are being hit. Every parameter at a cap must be interior before packaging.

## 4. Reserve spending (50 steps): recommended, for G4 (the M1 probe)

**Probe: a pristine replicate of R1's post-crash bridge campaign.** Start a fresh reset, then:

| Ticks (0-based) | Steps | seeding | incentive | bridge_outreach | Purpose |
|---|---:|---:|---:|---:|---|
| 0–14 | 15 | 0 | 0 | 0 | P0; third reset replicate (R1, R8 shape) |
| 15–49 | 35 | 9 | 0 | 0.6 | Same controls as R1 435–469, from a state with no crash history |

**Comparison.** R1 435–469 had identical controls (seeding 9, incentive 0, bridge 0.6), started at A 48 / B 37, and came 80 ticks after an incentive crash. This run starts at about 0.76 × reading (≈ 35–50) with no crash and no earlier incentive, and M3 ties are also zero in both. Only the history differs:
- **M2** is nearly silent. Incentive is 0 throughout. In R1, 80 ticks after the cut, E has decayed to about 13% of its level (m23_r12 has a2 = 0.026), so the extra churn is below 0.01/tick, which is small next to an inflow of several members per tick.
- **M3** is identical in both: ties start at zero, because bridge without seeding builds no ties (R1 405–435).
- **M1** (credibility dented by the crash or by broken promises) predicts that **the pristine gain is clearly larger than R1's**. R1's gains were A +34 / +69 and B +13 / +31 at 20 / 35 ticks. Under M1 the pristine run should approach R2's +61 / +105 (A) and +23 / +44 (B), with the *same ratio in A and B*.
- **No M1** (composition explains R8) predicts pristine ≈ R1 within about 10%, and it means incentive × seeding interacts strongly (useful for the composition scoring category either way).
- **The base disappointed-pool depletion** predicts a larger gain as well, but a community-specific one. It scales with D_c/N_c: roughly 87/N_A against 77/N_B, and N_B is smaller, so B's deficit would be bigger. The modeler separates these two explanations by refitting with and without m1, using the new run as a third episode.

It also buys a third P0/reset replicate for G8 and a second bridge-0.6 campaign for the G3 lag (introduction dead time and early acceleration).

**Alternative if the reserve must serve scoring coverage instead:** P2, which is a fresh reset, 15 ticks of recovery, then seeding 4.5 / incentive 0 / bridge 0 for 35 ticks (G5). I rank it second because M1 decides which pair gets submitted, and G1–G3 are modeling work that needs no steps.

The other gaps (G1–G3 and G6–G9) need no steps. They are model-structure fixes on the 950 ticks already collected.

## 5. Refit of m13 on R1 + R2

`m13_r12`, 1 restart: cost 37,612, scores 0.485 on R1 and 0.426 on R2. It is barely better than base (44,640) and far worse than m23 (11,231). Plot: `fits/social_contagion/review/m13_r12.png`.

Without M2 the fit cannot produce the crash (R6). It uses iota → 5e21 (a runaway) and g3 at its cap with a3u = a3d = 1 (R reduced to an instantaneous switch), with g1 0.85 and a1 0.085.

m12 (19,972) stopped early at nfev 64, so its cost is an upper bound. Its ordering against m23 is not settled, and **only m13 is clearly rejected**. That is consistent with M2 being active: both pairs that include M2 beat both fits without it. M1 against M3 is still undecided, which is G3 plus G4. Costs are still 1 to 2 restarts on a base with pinned parameters (G1), so they are not bootstrap-grade evidence.
