# Ad auction review (Phase B reviewer, §6.2)

Reviewer: separate agent, 2026-09-27. No steps were spent (budget: 945 of the 1,000 cap spent, **reserve 55**).
Paths are under `toronto26-participant-kit/`. Review artefacts are in `fits/ad_auction/review/`:

| File | What it is |
|---|---|
| `raw_scan.py`, `raw2.py` | per-segment levels, noise, reset replicate, drain τ (raw data only) |
| `base_hop.json` | **base refitted on R1+R2** (cost 63,888; perturbed start + 14 basin hops; start from the R1 base gave 86,530 and stalled after 23 nfev) |
| `m12_c.json`, `m13_c.json`, `m23_c.json` | pairs refitted on R1+R2 from `base_hop` + R1 module params, 4 hops each |
| `pairs_r12.png` | all four refits on R1 and R2, errors in local σ (0.1 × std: win 0.0152, spend 1.35, conv 0.125) |
| `base_r12c.png` | base refit alone |
| `stab.py`, `stab.txt` | 4000-step stability and extremes |
| `rank_reserve.py` | reserve candidates ranked by disagreement between the four refits |
| `hopfit.py`, `chainfit.py`, `plotfit.py` | fit/plot drivers (fit.py's `Problem`, soft_l1, f_scale 2, model NOISE) |

## 1. Independent behaviour list (written from the raw data before reading the plan)

| ID | Behaviour | Evidence |
|---|---|---|
| R1 | Reset is deterministic and ignores the initial reading: R1 and R2 first 25 ticks agree to noise (win 0.147→0.235, spend 20.0, conv 0.005→4.2) although initial readings differ (0.376/15.8/0.88 vs 0.325/21.8/1.03) | `raw2.py` |
| R2 | Reset transient: spend pinned at the cap for ~20–28 ticks, then falls to ~13.3 (τ ≈ 10–15); win_rate rises almost linearly 0.147→0.25 over 25 ticks; conversions ramp +0.21/tick and overshoot to 4.48 (t≈35) before settling at 3.1 by t≈80 | R1 0–80 |
| R3 | Conversions pipeline: 2-tick dead time on every switch, geometric drain τ ≈ 7 ticks (bid 0), τ ≈ 8 (breadth 0.1) | R1 405–435, 480–510 |
| R4 | Budget cap binds only on a rested pool or at high bid; cap 100 at bid 1.5 has no effect | R1 210–280 |
| R5 | While capped, win_rate is throttled (cap 20: R1 reset, bid 5 at 0.30–0.34, breadth 1.0 at 0.14) | R1, R2 125–140 |
| R6 | Unthrottled bid 5: win 0.55–0.60 (creeps **up** during holds); spend spikes 73 / 88 then decays (τ ≈ 12 / 25) to 25.7 / 34.4 | R2 25–65, 160–360 |
| R7 | Every "rest then restart" gives a conversions overshoot whose size recovers fast, while the spend (opportunity) pool recovers slowly: after 30 ticks of bid 0 the conv peak is 4.26 (95 % of the reset peak 4.48) but spend stays capped only 12 ticks (vs 28 at reset) | R1 435–480 vs 0–80 |
| R8 | Conversions overshoot on every up-step and undershoot on every down-step, with a common τ ≈ 15–20 ticks: bid-5 on (cap 20) bump 3.13→3.85 then sag to 3.2 at constant spend; bid off dip to 2.26 then recovery by ~190 | R1 80–210 |
| R9 | After the **capped** bid pulse (R1) win and spend undershoot (0.222, 10.2) and recover in ~30 ticks; after **uncapped** pulses (R2) win is at/above baseline (0.27–0.28) while spend undershoots far deeper (7.4–7.7) and recovers slowly (τ ≈ 25–30) | R1 145–175 vs R2 65–80, 360–400 |
| R10 | Breadth steps act like a high-pass on win_rate (0.775: 0.27→0.20 then creeps up; 0.1: 0.355 then creeps down; reversed on return) | R1 280–545 |
| R11 | Broad→narrower conversions transient: breadth off (0.775→0.55) gives a conv bump 3.5→3.77 before falling below the old baseline; breadth on gives a dip first | R1 280–405 |
| R12 | P5: a second pulse after a 15-tick gap is much weaker (spend 33 vs 73, conv peak 4.6 vs 7.0) | R2 80–100 vs 25–45 |
| R13 | P7: conv peak 6.15, plateau 5.35–5.44 for ~60 ticks, abrupt drop at ~255, settles at 4.47; spend settles 34.4 by ~270; win 0.56 | R2 160–360 |
| R14 | Slow drift of the settled recovery baseline: spend 13.3→13.0→12.5→12.2 (R1 78→400), conv varies 2.95–3.9 with history; win baseline is history-independent (0.264–0.269) | R1 recovery ends |
| R15 | Noise: win σ ≈ 0.005 additive; spend σ ≈ 0.5–0.6 % **of level** (0.08 in R1, 0.22 in R2); conv σ ≈ 0.5 % of level; values clip at 0 | `raw2.py` |

## 2. Comparison with the catalogue (plan §7, §12) against the R1+R2 refits

Base refitted on both runs (`base_hop`): local score R1 0.596 / R2 0.573 (persistence 0.175 / 0.100).
Errors below are read from `pairs_r12.png` (σ = local score σ).

| Behaviour (mine / plan) | Component | Captured? (R1+R2 base refit) |
|---|---|---|
| R1 / B1 reset ignores initial | reset convention | **yes** |
| R2 / B1,B2 reset win throttle | pacing `th` + pool | **no**: model win starts at 0.05–0.06 vs 0.147 (−6σ for 25 ticks) in all four fits: the fitted rested pool is too large (S_u(0) ≈ 90 needed for the model's throttle vs ≈ 36 implied by win 0.147/0.265 × cap 20). Only ~1 % of scored ticks, but a symptom of G2 |
| R2 conv overshoot at reset | pipeline + X pool | yes (±1σ after an early +7σ spike) |
| R3 / B6,B19 dead time, drain | DEAD=2, prepare, queue | mostly; drain after bid 0 lags (+4σ at 405–415) |
| R4 / B5 cap no effect at bid 1.5 | smooth min | yes |
| R5 / B2 throttle while capped | pacing | yes (bid 5 cap 20, breadth 1.0 cap 20) |
| R6 / B2,B3,B16 unthrottled bid 5 | auction curve, pool | level yes; the win creep-up is not (flat, −1.5σ); P7 spend decay too fast in the model (−12σ at t≈170) |
| R7 conv recovers fast, spend pool slow | one pool (X, ret τ ≈ 220) | **no**: post-rest conv peaks 3.45 vs 4.26 (R1 450) and 3.3 vs 3.97 (R1 525), −6σ, in **all four** fits |
| R8 / B10 conv overshoot/undershoot τ ≈ 15–20 | pool (too slow) + capacity | **no**: bid-on bump −6σ, bid-off dip +5σ, 180–280 −3σ in **all four** fits; no mechanism module changes it |
| R9 / B9,B17 post-pulse win: undershoot after capped, none after uncapped | m1 (spend density) | **no**, and m1 makes it worse (§3 G3) |
| R10 / B8 breadth high-pass on win | ring composition (+m1) | partly: breadth 0.775 creep yes; narrow creep-down no (−2σ→+1σ at 480–510; −3σ at R2 140–160) |
| R11 / B7 breadth-off conv bump | ring work `om` + queue | **no** (−5σ at 355–370) |
| R12 / B13 weak second pulse | X pool | yes (spend and conv within ±2σ) |
| R13 / B14,B15 P7 plateau, settled 4.47 | capacity `capf` | **no**: no plateau/abrupt drop (−8σ at 175, −4σ at 240), and the settled level is **over**-predicted (4.76–4.8 vs 4.47, +2.5σ for 90+ ticks; 4000-step pulse hold ends at 4.76) |
| R14 / B11 slow baseline drift | X pool ret | partly (spend yes, conv no) |
| R15 / B12 noise | NOISE constants | constant σ for spend, but spend noise is proportional (G6) |

Catalogue items not in my list: B4 (partial pool recovery; the same as R7, but the plan reads it as "one slow pool"; the
conversions data say two timescales), B15 (breadth-dependent capacity; plausible, not checked separately). Everything in my
list is in the catalogue except R7's two-timescale reading and R8's common τ ≈ 15–20.

### Pairs refitted on R1+R2 (the mechanisms judged against this base)

| Fit | Cost | Score R1 / R2 | Pinned / extreme parameters |
|---|---:|---|---|
| base | 63,888 | 0.596 / 0.573 | om 8.1 (ring work ratio ≈ e^7 ≈ 1,400×), qm −4.1 (purchase ratio ≈ 40×) |
| m1+m2 | 58,529 | 0.568 / 0.541 | **a_m2 = 1.00** (fatigue with no memory: a static cut) |
| m1+m3 | **54,208** | 0.590 / 0.545 | **a_m3 = 1.00, g3 = −4.0** (static broad-exposure penalty; `1 + g3·P` is clipped at 0, so purchases shut off) |
| m2+m3 | 58,592 | **0.615** / 0.573 | **a_m2 = 0.001** (other end: permanent), **a_m3 = 1.00, g3 = −6.6**, om 19, **capf 92** (capacity switched off) |

Every pair has a pinned module parameter, so by §2.9 none is evidence for its mechanisms. The cost ranking
(m13 < m12 ≈ m23 < base) and the score ranking (m23 > base > m13 > m12) disagree, because relative to the score the cost
weights spend ~6× more than win and ~2× more than conversions (G5). The four fits share the same conversions error trace in R1 (`pairs_r12.png`, panel 5):
no module as written touches R7/R8/R11/R13.

## 3. Coverage and separation check (§4.2, §3.4)

| Item | Run? | Evaluated? |
|---|---|---|
| P0 in each run | yes (R1 80, R2 25) | yes (R2 replicate identical) |
| P1 every control | yes | yes |
| P2 most important control (bid mid-level) | **no** | — |
| P3 top two controls (bid + cap) | yes (R2 25–65) | yes |
| M1/M2 separator (P1 bid hold; P8 same spend via bid vs budget) | P1 yes; **P8 no** | M1 prediction (win drifts down) contradicted; not evaluated in a refit before this review |
| M1/M3 separator (P1 breadth off; P6) | P1 yes; P6 half only (broad→narrow, 15 + 20 ticks) | partly |
| M2/M3 separator (P5 short vs long gap) | short gap only; the "long gap" reference is the first pulse, which ran during the reset transient | yes, qualitatively (against positive M3) |
| P9 "equal spending can leave different future opportunities" | not designed; incidental matches only | open |
| P5 or P6 | yes | yes |
| P7 ≥ 200 | yes (200 at pulse action) | yes |

The M3 probe was weak: the "broad introduction" (R2 125–140, breadth 1.0 at cap 20) was **throttled** (win 0.14,
spend capped) for only 15 ticks, so few broad impressions were delivered before the narrow follow-up.

## 4. Theses: missed drivers

- **M1 driver.** The thesis uses our spend density. R2 contradicts it: with 3–4× more spend than R1's capped pulse, R2
  shows no win undershoot after the pulse and a win creep **up** during it. Fitted m1 (g1 > 0) predicts a win overshoot
  at every unthrottled bid-on followed by a drift down (+8 to +11σ at R2 25 and 160). Untested drivers: our **bid level**
  or **win share** (rivals escalate against high bids), audience profitability (conversions), and a **negative** gain
  (rivals leave audiences we dominate), which matches R2 but not R1's capped undershoot. R1 vs R2 is a natural P8 (same
  bid, spend 20 vs 25–73). It should be evaluated in the fit before anything else.
- **M2 driver.** The driver (impressions per member) is plausible, but in this model M2 and the base X pool act on the
  **same** availability `1 − X − F`, so they are degenerate (a_m2 pins at 1 or 0.001). R7 says the conversion-limiting
  pool and the opportunity/spend-limiting pool recover on different timescales. The thesis should say which output each
  pool acts on.
- **M3 driver and delay.** "Broad introduction" may need time to become preparedness (a delay stage), and it may be
  keyed to breadth **above the follow-up breadth**, not above 0.55. It was probed only while throttled. The R1
  breadth-off conversions bump (R11) is also the M3 "present" signature from the thesis and was not evaluated as such.
- **Controls whose recovery value is not at a bound:** bid in (0, 1.5) (only bid 0 was tested), cap in (20, 100) at high
  bid, cap < 20, breadth extremes at high bid, and breadth 0.1 / 1.0 were held only 15–30 ticks. Sustained and joint
  scoring episodes can use any of these.
- **Time since reset:** none beyond the reset transient. That is correct.

## 5. Model code: stability over 4,000 steps (`stab.txt`)

- All fits give finite, in-bounds output for 4,000-step constant, uniform-random, extreme-corner and
  recovery/pulse-style schedules, at about 0.07 s per episode. There is no numerical risk.
- **Extrapolation risk:** at bid 5, cap 100 and breadth 1.0 (untested), the settled conversions are base 2.94,
  m23 1.80 and **m13 0.00** (spend 99.8 at the cap). The `J = I·q·(1 + g3·P)` clip at 0, with g3 = −4, turns
  purchases off. Any M3 multiplier must be bounded, for example `exp(g3·P)` or `1 + g3·P/(1 + |g3|·P)`.
- `om` and `qm` go to extremes (8 and −4 in the base; om 19 in m23), and `capf` goes to 92 in m23. These are ring
  gradients standing in for missing structure (G2).
- The fitting landscape is rough. From the R1 base, the refit stopped on ftol after 23 nfev at 86,530. A perturbed
  start reached 63,891, and 14 basin hops did not improve it. The non-smooth pieces are `max(0, ·)` availability, the
  `dx+df > free` rescale, the J clip and the SMOOTH=12 pacing min. Converged costs need several restarts.

## 6. Gaps (the modeler must answer each)

**G1 (high): conversions have a fast readiness memory (τ ≈ 15–20) that no component captures.** Evidence: R7 and R8.
In all four refits, conversions miss by −6σ on the bid-on bump, +5σ on the bid-off dip, −6σ on post-rest overshoots and
−3σ during R1 180–280. This is the classic depletion signature (overshoot on up-steps, undershoot on down-steps, one
τ), but it is faster than the X pool (ret τ ≈ 220) and it does not show in spend. Fix: add a separate **purchase-readiness
pool** Y_r (base, from "converted customers take time to become available again" and "stages of attention and
purchase"). Purchases are `J_r = I_r q_r (1 − Y_r)`, `Y_r += eps_y J_r/size − ret_y Y_r`, with ret_y ≈ 0.05. Y acts
**only** on purchases. Keep a slower pool (X or M2's F) acting on opportunities/spend. Test: Run-1-fit → Run-2 score,
and whether om/qm come back from their extremes.

**G2 (high): opportunity-pool size and timescales are mis-set.** Evidence: reset win −6σ (the implied rested uncapped
spend is ≈ 36 at bid 1.5, but the model needs ≈ 90); P7 spend decays too fast (−12σ at t ≈ 170) while P3's decay fits;
recovery spend has two timescales (τ ≈ 25–30 after P7, plus a > 200-tick drift, R14). Fix: two opportunity timescales
(fast exposure fatigue ≈ 25, slow ≈ 200+). This is where M2 can live **on opportunities only**, which also removes its
degeneracy with X. Check that the reset win transient then comes out right without a special term.

**G3 (high): M1 as coded is contradicted, and R9 is unexplained.** Evidence: m1 fits overshoot win at unthrottled bid-on
by +8 to +11σ and drift the wrong way (data creep up). They also lower the score (m12 0.568/0.541 and m13 0.590/0.545,
against the base's 0.596/0.573). Fix, with no steps: refit m1 variants whose driver is (a) our bid, (b) our win share,
(c) our spend density with a free-sign gain. Also rule out (d) ring composition alone by checking the base's predicted
ring mix after R1 145 and after R2 65. Keep M1 only if some variant fits **both** R1 145–175 (undershoot) and R2 65–80
and 360–400 (no undershoot).

**G4 (high): P7 settled conversions are overpredicted, and the plateau/abrupt drop is missed.** Evidence: all fits end
at 4.76–4.8 against 4.47 (+2.5σ over the last 100 ticks). A 4,000-step pulse hold would carry that bias for the whole
episode, which matters for sustained and recovery scoring. Fix: G1 is likely to fix much of this, because readiness
depletion lowers the long-run purchase rate. Otherwise make fulfillment capacity a hard queue (conversions =
min(capacity, queue)) so the plateau ends when the backlog clears.

**G5 (medium): the fit objective does not match the score.** Cost uses the model NOISE (spend 0.066, win 0.0047,
conv 0.0123), but the score's σ is 1.35 / 0.015 / 0.125. Relative to the score, the cost weights spend ~6× more than
win and ~2× more than conversions. Cost and score rankings of the pairs disagree (m13 best by cost, m23 best by score).
Fix: fit in local-score σ units, or at least rescale per observable so that each carries equal weight in the score.
Report pair selection on the Run-1 → Run-2 **score**.

**G6 (medium): all pair comparisons so far are uninformative.** Every refit pair has a module rate pinned at a bound
(a_m2 = 1 or 0.001, a_m3 = 1), and the m3 gain is used as a static penalty. Fix: after G1–G2, refit pairs with ≥ 3
restarts and ≥ 5 basin hops (these fits stall on ftol after 20–100 nfev). Bound g3 (§5). Only then run §6.3.

**G7 (medium): M3 was never probed with an unthrottled broad introduction, and P6 was only half run.** Evidence: §3.
The four refits disagree most at breadth 1.0 × high bid. Conversions after broad→narrow come out as 2.17 / 3.28 / 0.68 /
0.87 (base / m12 / m13 / m23), which is 6–10 local σ of disagreement (`rank_reserve.py`). → reserve run below.

**G8 (low): spend noise is proportional to the level** (0.08 in R1, 0.22 in R2, ≈ 0.55 %). With a constant σ = 0.066,
R2's high-spend segments are over-weighted. Fix: σ_spend = 0.0055 × level (or log residuals for spend > 1).

**G9 (low): untested control ranges** are bid in (0, 1.5), cap in (20, 100) at high bid, and cap < 20. All fits share
the auction and pacing forms, so they agree there (< 1.2σ), but those forms are unverified. Tolerate this; cover it with
the reserve only if G7 is already answered.

**G10 (low): the reset transient is about 1 % of scored ticks.** Do not add ad hoc terms for the reset win_rate. It
should come out of G2.

## 7. Reserve recommendation (55 steps)

**Yes: spend the reserve on G7.** It is the largest model disagreement (6–10σ, mostly in conversions). It is a
required separation probe (M3 with a strong broad introduction, and the missing P6 half). Its settings (breadth 1.0 at
high bid) can appear in joint and sustained scoring episodes.

Schedule, **continuing R2** (`run_schedule.py --continue`; the pool is then partly depleted, so the spend stays below
the cap: model maxima 71–90):

| Ticks (R2 idx) | Steps | Action | Purpose |
|---|---:|---|---|
| 400–424 | 25 | bid 5.0, cap 100, breadth 1.0 | unthrottled broad introduction (auction curve and capacity at breadth 1.0) |
| 425–444 | 20 | bid 1.5, cap 20, breadth 0.1 | narrow follow-up. Compare with R1 480–509 (after recovery) and R2 140–159 (after a throttled broad intro): an M3 dose response |
| 445–454 | 10 | recovery (1.5, 20, 0.55) | off-step / return |

Total: **55 steps** (945 → 1,000). If the continue call fails, start a fresh reset with the same 55 steps and no P0,
because the reset is deterministic and has been replicated twice. On a rested pool the broad segment will hit the
100 cap at first (all models predict it). That is still informative, because the throttle regime is identified.
Run G1–G3 and G5 (no steps) before or in parallel with this. None of them needs data.
