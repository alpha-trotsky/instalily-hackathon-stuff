# Traffic review (Phase B reviewer, 2026-09-27 ~06:45–07:15)

Scope: `data/traffic/R1.json` (745 steps), `R2.json` (500 steps), `plans/traffic-plan.md`, `greybox/traffic_model.py`, `fits/traffic/`.
Budget: 1,245 of CAP 1,300 spent → **reserve 55**. No steps were spent in this review.
Reviewer's files: `toronto26-participant-kit/fits/traffic/review/` (revised model `traffic_model_rv.py`, fit driver
`myfit.py`, plots `rvbase_vs_old_R{1,2}.png`, `rv_pairs_R{1,2}.png`, probe ranking `rank55.py`).

## 1. Independent behaviour list (written from the raw data and plots before reading the catalogue)

- **R1** Flows are exactly 0 at the recovery action (ramp 0 admits nothing); speeds relax from the reading to ≈ 48.9 in ~10–15 ticks.
- **R2** Flows appear 11–12 ticks after ramp on and vanish 11–14 ticks after ramp off (pure dead time), stepping in half quanta (6.4 → 12). Speeds start moving after 2–7 ticks, so speed reacts to vehicles in transit, not to completions.
- **R3** Total flow is proportional to ramp (12 at 0.5, 24 at 1, at toll 5), split 50/50. The speed drop is concave in load: 49 → 35.6 → 31.
- **R4** Signal is one-sided. The route losing green loses 5.5–6.5 speed at once; the route gaining green gains ~1. Flows barely move (uncongested), but the A/B split drifts slowly (~15-tick delay, τ≈30) toward the faster route.
- **R5** Lane closure 0.65 and clearance 0 have **no measurable effect** in the uncongested regime (R1 335–430). Freight priority 0 (the other side of recovery) was **never run**.
- **R6** Toll 0 is the congestion switch. Flows become bursty (0–50 per tick; these are real dynamics, since smooth-hold noise is ~0.2 %). speed_b drops to a floor of ~15 within ~20 ticks, and speed_a falls for ~100 ticks to ~8. ramp 0.72 + toll 0 (same vehicle total as ramp 1, toll 5) also congests, so the mix matters, not the volume.
- **R7** After toll goes back to 5 (R1 605), speed_a stays at 8 for ~45 ticks, then recovers in ~40. speed_b **stays at 15 for 95 ticks** under inputs where it was 29.4 before, and B keeps a standing queue (flow_b ≈ 12–13.3). Only ramp 0 clears it, after which B discharges bursts (up to 36) for ~20 ticks. This is hysteresis, with two states under identical inputs.
- **R8** The zero-demand speed_b ratchets: 48.9 → 47.05 → 46.6 across R1's demand episodes, while speed_a returns to 48.9 each time. Not seen in R2.
- **R9** Clearance 0 in congestion (R1 555–585): speed_a +2 within ~12 ticks, then **fades** 10.5 → 9.3 while the hold continues. After the switch back, a small dip (9.3 → 8.6) then partial recovery. This fits either fatigue-like fading or queue rebuilding, and is not separable from this segment alone.
- **R10** Joint pulse (R2 170–370): flow_a settles **smooth** at 6.66 (A is capacity-bound), flow_b bursty at ~12.9, speed_a 6.1 (settled only ~130 ticks after onset), speed_b 16.1.
- **R11** After the joint release (R2 370), B empties in ~23 ticks and speed_b reaches 48. A discharges bursts up to 60/tick for ~33 ticks, and speed_a recovers ~15 ticks late. With arrivals stopped, signal reversed, and the crew at the intersection (R2 470–500), B discharges ~3/tick and **speed_b keeps falling**.
- **R12** The dead time after re-pulse (R2 410, toll 0, lane 0.65) is ~15–18 ticks, versus 11–12 at toll 5. Heavy or lane-closed travel may take longer.
- **R13** Speed noise is proportional to level (σ ≈ 0.5 %). Flow noise in smooth holds is ~0.02.

## 2. Comparison with the catalogue and the models

"old" = `greybox/traffic_model.py` base refitted on R1+R2 (`review/old_base4_all.json`). "rv" = the reviewer's revised base (`review/traffic_model_rv.py`, `review/rv_base6_all.json`). Plots: `review/rvbase_vs_old_R1.png`, `_R2.png` (error panels in score-σ units).

| Behaviour (mine / catalogue) | old base | rv base | Evidence |
|---|---|---|---|
| R1/B1 empty network, speed reset transient | captured | captured | both plots, ticks 0–40 |
| R2/B2 dead time 11 | captured (DT = 11 shift register) | captured | |
| R12 longer dead time at toll 0 / lane | **not captured** (DT fixed) | **not captured** | R2 410–428 flows 0 for 15–18 ticks |
| R3/B14/B15 demand ∝ ramp, concave speed-load | not captured: flows 9 at ramp 0.5 (err +3σ), speeds too high | captured: `al·(n/100)^pa`, pa = 0.55 | R2 30–70 |
| R4/B16 one-sided signal | partly (linear `ws·u`, lifts speed above vf) | captured: `sg·(0.5/green − 1)` | R1 210–335, R2 70–115 |
| R4/B4 slow split drift | m1 only | m1 only (g1 ≈ 0.1–0.2); base leaves a +1.5 flow_b bias at R1 230–430 | `rv_pairs_R1.png` flow_b error |
| R5/B3 lane/clearance no effect uncongested | ok | ok (wl → 0) | |
| R6/B5/B17 toll-0 congestion, mix not volume | **not captured**: P9a speeds 30 predicted vs 15.6 | captured: heavy share and PCU queues; speeds within 1–2σ | R2 115–170 |
| R10/B18 joint pulse flow_a 6.66 smooth, speed_a 6.1 | flow_a 12 (err +6σ) | captured: flow_a ≈ 7, speed_a 6.2 | R2 170–370 |
| R7/B7 persistent speed_b = 15 after toll back | captured by accident (neutral queue on B) | **not captured**: speed_b drifts up to 23 (err up to +8σ) | R1 605–700; also in every rv pair |
| R7/B6 delayed speed_a recovery after toll back | recovers ~50 ticks early (err +10σ) | recovers ~20 ticks early (+6σ; m12/m23 +3σ) | R1 610–680 |
| R11/B19 B drains in 23 ticks after joint release | B empties at once, speed_b too high early | **not captured**: B's queue too big (one shared qmax ≈ 600 PCU), flow_b 14 until 410, speed_b 32 vs 48 | R2 370–410 |
| R11/B21 B blocked while A drains with crew at the intersection | not captured (speed_b → 50+) | partly: speed_b falls to 13–14 (exit occupancy E), flow_a ≈ 19 vs 20 | R2 470–500 |
| R8/B8/B12 speed_b zero-demand ratchet | not captured | **not captured** (J memory: kJ pinned at 1 = no memory) | R1 120–170, 720–745 |
| R9/B9 clearance effect fades during hold | not captured | not captured (m2 fatigue g2f ≈ 0.1 fits a little) | R1 555–605 |
| R11 slow A drain after release (buffers large on A, small on B) | not captured | partly (A good, B too slow: needs per-route buffer) | R2 370–410 |
| R13/B22 noise ∝ level | n/a (σ fixed) | n/a | |
| B11 burstiness: target the conditional median | both models are smooth | same | |

## 3. Base fix and the pair comparison against it

The rv base follows the researcher's list:
- two vehicle classes with the heavy share `h = σ(h0 + h1·u_toll)`, and PCU queues and capacities, so the toll-0 mix congests;
- freight priority weights heavy service;
- junction capacity as a product of `(green/0.5)^wg`, `(1 − wl·lane)` and `exp(wc·crew)`;
- an exit stage whose occupancy blocks **both** routes' admissions (`1 − (E_A+E_B)/Emax`), with exit capacity cut when the crew is at the intersection;
- speed as free speed divided by a time factor with concave load, `0.5/green` signal delay, queue, exit-occupancy, heavy-mix and completed-journey terms;
- m3 gains constrained to the physical sign.

Fitting: `least_squares` stalls after ~20 evaluations on this piecewise-linear model (min/queue kinks), so `review/myfit.py` runs Powell (2 × 3,000–4,000 evaluations) and then polishes with least_squares. The data are R1 + R2 jointly, with the same σ and loss as `fit.py` (flows 1.0, speeds 0.3, soft_l1, f_scale 2). All pairs started from the same base optimum, with active-module parameters reset to their SPEC defaults.

| Fit (R1+R2) | Cost | Δ vs rv base | Train score σ = 0.1·std (fa, fb, sa, sb) | Module parameters |
|---|---:|---:|---|---|
| old base (refit) | 48,221 | +66 % | 0.480 (0.43 0.40 0.51 0.58) | — |
| **rv base** | **29,096** | — | 0.569 (0.54 0.48 0.65 0.61) | — |
| rv m1 | 29,483 | +1.3 % | 0.569 | g1 0.21 (a1 not moved) |
| rv m3 | 27,209 | −6.5 % | 0.574 | **a3u → 1.0 (pinned)**, a3d 0.76: *not persistent* |
| rv m1+m2 | 28,532 | −1.9 % | 0.552 | g1 0.10; g2s 0.05 (τ 150), g2f 0.10 (τ 100) |
| rv m1+m3 | 27,698 | −4.8 % | 0.554 | g1 0.12; a3u → 1.0, a3d 0.96 |
| rv m2+m3 | 27,314 | −6.1 % | 0.573 | g2f 0.06; a3u → 1.0, a3d ≈ 1.0 |

Verdict:
1. The base fix is worth far more than any mechanism: −40 % cost against the old base.
2. m3's gain comes entirely from an **instantaneous** queue-fullness capacity penalty (a3u pinned at 1, a3d 0.76–1.0). That is a missing base nonlinearity (spillback/blocking as the approach buffer fills), not a *persistent* front (lesson 9). With the per-route buffer and a fullness term moved into the base, the m3 advantage is expected to shrink.
3. No fitted module reproduces the one real hysteresis in the data (R7/B7). Pair differences (1.9–6.5 %) are within the optimizer's run-to-run noise: m1 alone came out *worse* than the base, and m13 worse than m3 alone.
4. **No pair can be selected from these fits.** On qualitative evidence, M1 (B4 drift on both signal sides, memory across the empty gap) and M3 (B7 persistent B queue, B8 ratchet) are the best-supported mechanisms; M2 has only the ambiguous R9 fade.

## 4. Probe and coverage audit (§4.2, §6.2 step 3)

| Item | Run | Evaluated | Note |
|---|---|---|---|
| P0 each run | ✓ | ✓ | |
| P1 every control | ✓ | ✓ | signal/lane/clearance/freight uncongested (no effect) and in toll-0 congestion |
| P2 most important control | ramp ✓ | ✓ | **the control that matters most is toll, and its mid level was never run** |
| P3 top two | ✓ (joint; toll+ramp via P9a) | ✓ | |
| M1 vs M2 separating probe | signal both sides ✓ (M1 side) | partly | no probe where M2 predicts an effect and M1 none, other than R9 |
| M1 vs M3 | ✓ (signal drift vs R7 hysteresis) | not with a model: no fitted m3 reproduces B7 | |
| M2 vs M3 | ✗ | — | S6 vs S8 changes 5 controls at once; the clearance-only arm of P9b was never run |
| P9a toll vs ramp with similar totals | ✓ | ✓ (B17) | |
| P9b clearance vs signal reversal after stopping arrivals | signal arm only | ✓ | the clearance arm is missing |
| P5 / P6 | P5 ✓ (weak), P6 ✗ | ✓ | |
| P7 ≥ 200 | ✓ | ✓ | |

**Pair-fit leak (important for reading the plan).** `fits/traffic/m12_r1best.json` carries m3 gains (g3c 0.088, g3x −0.11, g3v −0.37). `m13_r1best.json` carries m2 gains (g2s 0.22, g2f 0.06). `m23_r1best.json` carries m1 (g1 0.3). These are the `--init` leak fixed in `core.py` at 06:39. They are stored in the params, and `plotfit.py` and `core.rollout` use them as stored. So the plan's §7 R1 costs, the §8 probe ranking and the §9 cross-run scores (m12 0.330, m13 0.309, m23 0.371) all compare **three-module models**. None of them is a pair result.

## 5. Missed drivers and thesis gaps (§6.2 step 4)

- **Freight priority** recovery is 0.5, not a bound. The side at 0 (u = −1) was never tested, so kf is identified only from u = +1 in congestion.
- **Toll** is the dominant congestion lever. Only u = 0 and u = 1 were run, so demand growth (`wt`) and heavy share (`h1`) are not separately identified. Across the rv fits, wt ranges from 1.36 to 1.79.
- **Lane closure** "affects different sections unequally". It showed no effect on junction capacity (wl → 0) and possibly the wrong sign in congestion (R1 525–555: flow_a ↑, speed_a decline flattens). The thesis may be on the wrong section: it could act on the approach buffer size, travel time (R12) or the exits.
- **M2** thesis drivers were only |Δclearance| and crew work. R9's fade during a 30-tick hold is the one sign of it, and the speed_a settling over ~130 ticks in the joint hold (crew at the intersection) was never checked against fatigue.
- **M3** thesis: the persistence in the data is B-specific and *self-sustaining* (a standing queue at demand ≈ capacity). A front model therefore needs a capacity loss that persists while Q > 0, with bistability. The written module (front driven by queue fullness, fading at a3d) turns into a static penalty when fitted.
- **Delay phrases:** "crossing commitments" and "keep occupying the shared junction" imply a junction/exit occupancy stage, which is missing in `traffic_model.py` (present in rv). "Waiting approach drivers may divert" is pinned in both models: old dv → 0, qd → 5e21; rv qd → 0, which makes diversion a step function.
- "Reported speed combines observed completed journey times": the old model has no completed-journey memory. In rv it exists, but kJ is pinned at 1, so B8/B12 are still unexplained.

## 6. Stability (4,000-step episodes)

- The old model with the leaked m3 gains (g3v −0.37 to −0.39, g3x < 0) multiplies speed by exp(+0.39·F), with F up to 20. Any sustained queue then drives speed to the 80 clamp. **Do not package any `*_r1best` pair file.**
- The old model's `vf·exp(−ws·u_sig)` exceeds free-flow speed for signal > 0.5.
- rv: the first rv fit showed a flow sawtooth (R1 670–700) from the exit-occupancy feedback, and rv m12 shows small flow_b jitter at R1 180–400. These need the §7 stability gate, especially with fast switching.
- Pinned parameters: rv kJ = 1, qd → 0, a3u = 1 (m3 fits); old dv = 0, qd ≈ 5e21. Each stands in for missing structure (lesson 9).

## 7. Gaps

| # | Severity | Gap | Evidence | Suggested fix / test |
|---|---|---|---|---|
| G1 | **high** | All plan-era pair fits and cross-run scores include leaked modules. There is no valid pair comparison yet. | §4 above; `m*_r1best.json` params | Discard them. Refit the pairs only on a fixed base with the fixed `core.py`, and start active modules from SPEC, not from another pair's file. |
| G2 | **high** | The base lacks mix-dependent (PCU) capacity, multiplicative capacity, concave speed-load, one-sided signal delay and junction/exit blocking. | Old refit 48.2k vs rv 29.1k; P9a and joint-pulse errors 6–10σ | Adopt `review/traffic_model_rv.py` as the new base (or port its pieces) |
| G3 | **high** | The B7 persistent standing queue on B is not captured by any model or pair. It is the only clean hysteresis and the best M3 evidence. | `rv_pairs_R1.png` speed_b 605–700, +8σ | Per-route buffer (qmax_A, qmax_B). Make B's capacity at toll 5 close to its demand, so a neutral queue is possible in the base. Rewrite m3 as a capacity loss that persists while Q_r > 0 and decays only when the queue empties (bistable), then retest m3 on B7 and R2 release. |
| G4 | **high** | m3 fits as an instantaneous queue-fullness penalty (a3u pinned 1): base structure in disguise. | §3 table | Move a fullness/spillback capacity term into the base, then refit the pairs. |
| G5 | medium | B drains too slowly after the joint release (one shared qmax ≈ 600 PCU). A's drain is long, B's short. | `rvbase_vs_old_R2.png` 370–410 | Per-route qmax (overlaps G3) |
| G6 | medium | Toll mid-level never run; wt and h1 are not identified (wt 1.36–1.79 across fits). Toll is the main lever in every scoring category. | §5 | **Reserve probe below** |
| G7 | medium | Optimizer: least_squares stalls after ~20 evaluations on queue kinks, so cost differences below ~5 % are noise. | base5 → base6 still improving; m1 worse than base | Use Powell/Nelder–Mead passes before least_squares (as `review/myfit.py`), 2–3 restarts, and equal budgets for every pair |
| G8 | medium | M2 has no clean test. The P9b clearance arm is missing (needs ≥ 60 congestion ticks + 30, which does not fit the reserve). | §4 | Accept "M2 not identifiable". If R9's fade is real, m2 fatigue would show in the rv m12 fit (g2f 0.10); check its effect on R1 555–605 in a plot. |
| G9 | medium | The completed-journey speed memory (B8/B12) is unresolved; kJ is pinned at 1. | R1 120–170 speed_b 47.05 | Update J only from completions with kJ < 1, and hold J when there are no completions. Test whether this explains B8 and R11's falling speed_b. |
| G10 | low | Freight priority 0 side never tested. | dossier | Keep kf symmetric/linear in u; no steps |
| G11 | low | Dead time is longer at toll 0 / lane closure (15–18 vs 11). | R2 410–428 | A second, slower pipeline for heavy vehicles (DT_h ≈ 15) |
| G12 | low | Lane closure effect: none, or possibly the wrong sign, in the junction position. | R1 525–555 | Try lane acting on buffer size or travel time instead of junction capacity |
| G13 | low | Bursty flows: the score target is the noiseless bursty series, so the smooth model should target the conditional median. | B11 | Keep soft_l1; check that the flow bias in congested holds is ≈ median |

## 8. Reserve spending (55 steps)

Spending the reserve is justified, for **G6 only**. No gap about the mechanisms can be closed in 55 steps. M2 needs ≥ 60 congestion ticks before a clearance-only switch, and the B7 hysteresis needs a long congestion episode followed by a long hold.

Candidates were simulated through the rv base and the three rv pairs, and through the old base (`review/rank55.py`, all from a fresh reset). The ranking uses mean |Δ|/score-σ summed over the observables:

| Candidate (fresh reset) | rv pairs max disagreement | rv base vs old base | Notes |
|---|---:|---:|---|
| ramp 1 + signal 0.15 + toll 2.5 | 8.1 | 15.1 | confounds signal and toll |
| ramp 1 + toll 3.5 | 6.1 | 15.1 | |
| **ramp 1 + toll 2.5** | 5.2 | **16.3** | clean single factor at the midpoint of the unknown range |
| ramp 1 + toll 0 + freight 0 | 5.0 | 20.3 | freight's other side, but in a regime already well characterised |
| joint u = 0.7 (recovery-scenario corner) | 4.7 | 12.7 | many factors at once |
| ramp 1 + toll 1.5 | 4.7 | 13.4 | |

**Recommended schedule (R3, new reset, 55 steps):** 55 × `{"signal_timing": 0.5, "lane_closure": 0.0, "toll": 2.5, "ramp_metering": 1.0, "freight_priority": 0.5, "clearance_effort": 1.0}`, starting at tick 0 with no P0. The reset transient is already known from R1 and R2, and starting at reset is itself scoring-realistic.

Why this probe:
- The rv base predicts congestion building by ~tick 50: flows 19.3/12.5, speeds 22/20. The old base predicts flows 11.8/8.9, speeds 17/18.
- Uncongested smooth flows would give total demand at u_toll = 0.5 directly, which identifies wt's linearity.
- Congestion would locate the mix threshold between toll 0 and 5.
- Either outcome fixes the toll interpolation used by every sustained and composition scenario.

Run it with `run_schedule.py` as one 55-step segment, saving `data/traffic/R3.json`. Budget after: 1,300 of CAP 1,300.
