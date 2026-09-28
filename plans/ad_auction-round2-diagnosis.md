# ad_auction round-2 diagnosis (R3 = AD1, R4 = AD2)

Diagnostician pass, 2026-09-28. **No steps spent, no model changed.** Paths are relative to `toronto26-participant-kit/` unless they start with `plans/`.

Scripts, outputs and plots are in `fits/ad_auction/round2/`:

- `diag.py` → `diag.out` (per-segment levels, settle checks, v1 errors, loss ranking), `loss.json`.
- `features.py`, `asym.py`, `rel.py`, `split.py` (switch responses, on/off τ, relationships, loss split), `longrun.py` (v1 4,000-tick holds).
- Plots (data in black, v1 in red, error in σ, controls):
  - [R3_v1.png](../toronto26-participant-kit/fits/ad_auction/round2/R3_v1.png)
  - [R4_v1.png](../toronto26-participant-kit/fits/ad_auction/round2/R4_v1.png)
  - Old runs: [R1_v1.png](../toronto26-participant-kit/fits/ad_auction/round2/R1_v1.png), [R2c_v1.png](../toronto26-participant-kit/fits/ad_auction/round2/R2c_v1.png)

σ is the score σ from `heldout.py`: 0.1 × std after tick 20 of R1+R2c+R3+R4. That gives win 0.0152, spend 1.38 and conversions 0.121. Errors are v1 − data, in σ. "Last-10" is the mean of a segment's last 10 ticks.

## 1. Summary

1. **Both pre-registered rules come out in v1's favour.** Conversions at u.7 stop drifting by about tick 100, so no longer τ is needed. Spend does **not** pin at cap 30 (24.0) or cap 50 (23.8), so the bid × cap structure is right.
2. **v1 scores 0.560 (R3) and 0.487 (R4) held out; persistence scores 0.09–0.15.** 1,121 of 2,400 obs-ticks are lost. Of that, 67 % (R3) and 45 % (R4) is on ticks 25 or more after a switch, which is the regime that dominates 4,000-tick scoring. On those ticks spend scores only 0.52–0.58 and conversions 0.36–0.48.
3. **The largest loss is a level error at high bid.** Long-run spend is over-predicted by 1.1–1.8σ in *every* high-bid hold, and the same error is in-sample on R2c P7. Conversions at bid 5, breadth 0.55 keep falling while spend is flat (4.14 → 3.79), but v1 holds 4.4–4.6 (+2.7 to +5.1σ). v1 also over-predicts conversions at capped bid 5 in R1 (+2.5σ). So something depletes purchases per impression at high bid, and v1 lacks it.
4. **The next loss is a dynamics error: the conversion capacity plateau and its abrupt end** (B14 replicated). The plateau sits at 5.38 at breadth 0.775 (R3 matches R2c to ±0.04) and 5.79 at breadth 0.7075. It ends with a drop of 1.6 within about 8 ticks, and the drain is delayed after saturated holds. v1's soft capacity misses all of this, by −3 to −4σ on the plateau and +5σ after the drop.
5. **Recommended changes, in order:**
   1. Refit on R1+R2c+R3+R4 as a control.
   2. Add bounded purchase-side exposure fatigue (τ ≈ 40–60, acting on purchases only).
   3. Use a hard (FIFO) work-capacity queue.
   4. Add availability loss from committed purchases (spend undershoot, B24).

   Reserve proposal: 170 steps on the two unobserved pair compositions (cap + breadth, bid + breadth at cap 20).

## 2. Decision-rule verdicts

The rules and predictions come from `plans/round2-experiments.md` §5.1. Candidate values are from `fits/round2/final_ad_auction.out` and are last-10 means.

| Rule / prediction | Quantity measured | Data | final (v1) | m12_all | m13_all | base_all | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| "A conversion drift at u.7 that keeps going past tick 150 needs a longer τ" | conversions, mean of 100–150 / 150–200 / 200–250; slope over 200–250 | 4.262 / 4.301 / 4.260; slope −0.0006/tick (−0.03 over 50 ticks = 0.26σ) | 240–249: 4.37 | 4.44 | 4.47 | 4.45 | **Rule not triggered.** Settled by about tick 100 (settle.py: 3.5σ residual drift over the last half, settling time 123 ticks). Every candidate is 1.0–1.8σ **too high** at the level, which is a level error, not a τ error. v1's m3 (τ = 200) keeps falling to 4.27 by t = 1,000, which lands on the data by accident. |
| Pre-registered "conversions at u.7 fall from 5.38 (first 50) to 4.37" | last-10 at 40–49 and 240–249 | **5.80** → 4.25 | 5.38 → 4.37 | 5.44 → 4.44 | 5.46 → 4.47 | 5.46 → 4.45 | Direction right. At 40–49 the data sit on the capacity plateau (5.78–5.80 flat), −3.4σ against v1. Segment means are 5.39 (data) vs 5.55 (v1), and 4.34 vs 4.49. |
| "If spend pins at cap 30, the bid × cap interaction is misfit" | spend last-10 at bid 5, cap 30 (and cap 50) | **24.04** (cap 30), 23.84 (cap 50) | 25.8 (26.3) | 26.0 (26.7) | 26.2 (26.8) | 26.1 (26.7) | **Not pinned: the bid × cap structure is right.** Going from cap 50 to cap 30 changes nothing (win 0.594 → 0.590, spend 23.84 → 24.04), as predicted. All candidates are +1.3 to +1.8σ high on spend, which is the high-bid level error B25. |
| Pre-registered AD2 spend ladder at cap 100: 22.3 / 15.4 / 7.2 | spend last-10, bid 3.25 / 2 / 0.75 | 20.54 / 14.82 / 6.63 | 22.3 / 15.4 / 7.17 | 22.9 / 15.3 / 7.03 | 22.7 / 15.5 / 7.14 | 23.0 / 15.3 / 7.00 | Shape right; +1.3 / +0.4 / +0.4σ. The error grows with bid (B25). |
| u1 (50 ticks, R3 350–399) | last-10 win / spend / conversions | 0.560 / 37.5 / 5.37 | 0.557 / 37.2 / 4.92 | 0.554 / 37.0 / 4.95 | 0.554 / 36.8 / 4.99 | 0.556 / 37.0 / 4.95 | win and spend are fine. Conversions are −3.8σ because the data are still on the 5.38 plateau (B22). |
| u.85 (75 ticks, R3 425–499) | last-10 | 0.531 / 31.8 / 4.48 | 0.53 / 33.4 / 4.53 | 0.525 / 33.0 / 4.63 | 0.524 / 32.9 / 4.67 | 0.529 / 33.1 / 4.64 | Spend +1.1σ (B25); the rest is fine. |
| §5.1 question "slow memories over a 250-tick hold" | drift after tick 100 at u.7 | conversions flat; spend 29.1 → 28.3 (−0.004/tick, 0.6σ over 150 ticks) | — | | | | No slow memory beyond τ ≈ 50 is visible in conversions. Spend has a very slow residual decline (B24). |

The candidates agree with each other to within 0.1–0.6σ everywhere, and they all share the same errors. §1.3 predicted exactly this: the errors belong to the base model, not to the mechanism choice.

## 3. Behaviour catalogue (new runs; continues B1–B19 of `plans/ad_auction-plan.md`)

"Status" is judged against v1 (`fits/round2/v1_models/ad_auction`). Scoring categories are abbreviated: S = sustained, O = action order, R = recovery history, C = composition.

| ID | Behaviour | Evidence | Status vs v1 | Categories |
|---|---|---|---|---|
| B20 | **Reset under control.** The first observation ignores the initial reading (R3: 0.374 / 21.9 / 0.63 → 0.294 / 76.2 / 0.002; R4: 0.341 / 27.6 / 1.27 → 0.416 / 79.5 / 0.000). **R3 at cap 76:** spend is pinned at the cap (75.4–76.6) for 15 ticks while win climbs linearly from 0.294 to 0.495 (the throttle). **R4 at cap 100:** spend is never capped; it starts at 79.5 and decays with τ ≈ 12. | `features.py`; R3 and R4 ticks 0–20 | **Not captured (transient).** In R3, v1's spend leaves the cap at t ≈ 5 (−11σ at t = 13, then +5σ at t = 30–45). In R4, v1 starts spend at 98 (+13σ at t = 0, then −9σ at t = 8). win is +3 to +4σ over t = 2–10. The rested uncapped spend is 79.5 at bid 3.25 / breadth 0.55 and more than 76 for 15 ticks at bid 3.95 / breadth 0.71. v1 over-predicts the first and under-predicts the second, so its **breadth scaling of the rested pool is off**. | all (every episode starts here), about 2 % of ticks |
| B21 | Reset conversions ramp: 2-tick dead time, then about +0.6/tick to a peak of **7.5–7.6 at t = 15–16** in both runs, although bid and breadth differ. | R3 and R4 ticks 0–20 | R3 captured (v1 7.6). R4 not captured: v1 peaks at 6.5 (−9σ over t = 15–30). | all |
| B22 | **Conversion capacity plateau with an abrupt end** (B14 replicated). The plateau is flat at **5.78–5.80 at breadth 0.7075** (R3 t = 42–61) and **5.36–5.40 at breadth 0.775** (R3 380–399 matches R2c 195–250). At breadth 0.55 there is no plateau up to 7.6. The end is a drop of 1.6 within about 8 ticks (R3 61→69: 5.79 → 4.20; R4 33→40: 6.36 → 4.8), followed by an undershoot (R3 3.95 at t ≈ 75, back up to 4.30 by t ≈ 100). | `rel.py`, `features.py`, R3_v1.png | **Not captured (dynamics).** On the plateau v1 is −3.4σ (R3 40–60) and −3.8σ (R3 u1). After the drop it is +5σ (R3 62–80). R4 is −9σ over 15–35. The capacity in conversions/tick falls with breadth: ≥ 7.6 at 0.55, 5.79 at 0.7075, 5.38 at 0.775. | S (first ~100 ticks of every high hold), R (a 50–100-tick pulse spends its whole length on the plateau), O |
| B23 | **Backlog-delayed drain.** After a saturated hold (u1 → recovery, R3 400), conversions stay at 5.37 → 5.27 for 4 ticks (2 dead-time ticks plus 2 backlog ticks) before draining. The t63 is 11–12 ticks here, against 7 after unsaturated holds (R3 250; R4 50, 100). | `asym.py`, `features.py` | Not captured: v1 drains after 2 ticks and undershoots, −4 to −5σ over R3 404–420. | R, O |
| B24 | **Spend undershoot, then partial recovery, in a long high hold from reset.** At R3 u.7, spend bottoms at **26.2 at t ≈ 48**, rises to 29.1 by t ≈ 100, then declines very slowly to 28.3 by t = 250 (−0.004/tick). Conversions mirror it with a 12–13-tick lag (a minimum of 3.95, then 4.30). The spend minimum coincides with the backlog peak (B22); the rise starts as the backlog shrinks. | R3 t = 40–250 | Not captured: v1 is monotone and settles at 30.2 (+3σ at t = 48, +1.4σ at t = 250). No undershoot appears in R4 at breadth 0.55, where the backlog is small. | S, C |
| B25 | **v1 over-predicts long-run spend at every high bid.** Last-10 errors: u.7 +1.4σ, u.85 +1.1σ, bid 3.25 +1.3σ, bid 5 cap 50 +1.8σ, bid 5 cap 30 +1.3σ, and in-sample on R2c P7 +1.2σ (late mean +1.4σ). At recovery and at bid ≤ 2 the error is ≤ 0.4σ. | `diag.out`; loss ranking | **Not captured (level).** v1 is 6–10 % too high at high bid. | S, C, R |
| B26 | **Conversions at bid 5 / breadth 0.55 keep falling while spend is flat.** 10-tick means from R4 t = 210 onwards: 5.18, 4.80, 4.40, 4.14 (cap 50), then 4.00, 3.88, 3.82, 3.81, 3.79 (cap 30; slope over the last 30 ticks −0.0011/tick). Spend is 23.8–24.0 throughout, so conversions/spend falls from 0.174 to 0.158. The same excess is in old data: capped bid 5 in R1 (80–145) is +2.5σ. | `features.py`, `rel.py` | **Not captured (level + slow dynamics).** v1 gives 4.57 and 4.42 (+3.6σ and +5.2σ at the last-10; late mean +5.1σ). | S, C |
| B27 | Pre-registered u.7 slow memory: conversions settle by about tick 100 and do not drift past 150 (§2). | §2 | Level +1.0σ (v1 4.37 against 4.25). v1's m3 carries on down to 4.27 by t = 1,000, which is unverified but harmless. | S |
| B28 | The cap does not bind at bid 5 once the pool is depleted (caps 50 and 30); a cap step from 50 to 30 has no effect on any observable. | R4 200–300 | Structure captured; level as in B25. | C |
| B29 | **Win–bid curve** (breadth 0.55, unthrottled, settled): 0.75 → 0.128, 1.5 → 0.262, 2 → 0.338, 3.25 → 0.476, 5 → 0.594. The logit slope in ln(bid) falls from 1.30 to 1.11, a mild saturation. | `rel.py` | Partly captured. v1 gives 0.142 / 0.265 / 0.333 / 0.461 / 0.574–0.583, i.e. +1.0 / +0.2 / −0.4 / −1.0 / −0.8 to −1.1σ. v1's curve is **too flat** (h = 1.14). | S, C |
| B30 | win creeps **up** during unthrottled high holds (B16 confirmed): u1 0.510 → 0.560 over 50 ticks; u.85 0.509 → 0.531; R4 bid 3.25 from reset 0.416 → 0.476 over 15 ticks. There is also a small **win dip** during R3's backlog (0.50 → 0.475 over t = 35–65, back to 0.50 by 100). | R3, R4 | u1 and u.85 captured. The R4 reset creep is not (v1 jumps to 0.46: +3σ at t = 2, then −1σ), and neither is the R3 dip (about +1σ). | S |
| B31 | win overshoots at recovery after an **uncapped** pulse (B17 confirmed): 0.280–0.286 right after the switch, falling to 0.262 within about 10 ticks (R3 250 and 400). | `asym.py` | Not captured (v1 is flat at 0.265): +1.4σ for about 5 ticks. Minor. | R |
| B32 | **Spend on/off asymmetry.** On: an instant jump above the settled level, then decay with τ = 9–14 (R3 350: 73 → 37.5; 425: 47.5 → 31.8; R4 200: 41.8 → 23.8). Off: an instant drop **below** the settled level (7.4–7.8 after high holds), then recovery with τ = 20–37 (τ = 37 after bid 0.75). The asymmetry holds in both linear and log units: depletion is faster than return. | `asym.py` | Qualitatively captured. The undershoot depth is under-predicted: v1 gives 9.0–9.5 against 7.4–7.8, about +1.2σ at the switch, closing within about 40 ticks. | R, O |
| B33 | **Conversions on/off.** t63 is 4–8 ticks on and 7–8 ticks off (12 after saturated holds, B23); the same in linear and log units. There is an overshoot on up-steps (peak/settled 1.08–1.28) and an undershoot on down-steps (2.56 vs 3.00; 1.51 vs 1.76; 2.82 vs 3.01). The rest-then-restart overshoot is visible after bid 0.75: 3.74 against a settled 3.25 (R4 150–165). | `asym.py`, `features.py` | **Not captured** for the rest-restart overshoot (−4σ, R4 155–175; the same as the old R7/R8, −5σ in R1 435–545). The high-bid overshoot is partly captured (R4 200: v1 4.9 against 5.30). | R, O |
| B34 | Recovery baselines: win 0.262–0.265 regardless of history; spend 12.6–12.8. Conversions depend on history: 3.00 after the 250-tick u.7, 3.25 after low bid. | R3 340–349, R4 190–199 | win and spend captured. Conversions −1.0σ after u.7 (v1 2.88) and −0.9σ after low bid (v1 3.14). | R |
| B35 | **Relationships.** Conversions follow spend with a lag of 12–13 (level corr 0.87–0.89) and win with a lag of 5 (0.68–0.73). Settled conversions/spend falls with bid: 0.24–0.27 at bid ≤ 1.5, 0.22 at bid 2–3.25, 0.14–0.17 at bid ≥ 3.95. Conversions per unit win are 12–14 at bid ≤ 1.5, 9.7 at bid 2–3.25 and 6.4–7.0 at bid 5 / breadth 0.55. Spend/win (a price × pool proxy) is 40–49 at breadth 0.55 and 57–67 at breadth 0.71–0.775. | `rel.py` | The drop in purchase yield at high bid is what v1 misses in B25/B26. | S, C |
| B36 | Noise: win 0.005, additive; spend 0.5–0.7 % of level; conversions 0.4–0.7 % of level (the same as B12/R15). Measured against score σ, the noise floor alone costs about 0.19/tick on win, 0.04–0.09 on spend and 0.07–0.12 on conversions. **Most of win's measured "loss" is noise, not model error.** | `features.py`; Gaussian floor check | n/a | — |
| B37 | Low bid 0.75 at cap 100: win flat at 0.128 (no creep). Spend jumps 14.9 → 4.1, then recovers slowly (τ ≈ 37) to 6.6. Conversions undershoot to 1.51, then climb slowly to 1.76–1.81. | R4 100–150 | Level not captured: win +1.0σ, conversions +2.4σ (v1 2.0 against 1.76). | S, C |
| B38 | **Surprise:** the plateau capacities reproduce to ±0.04 across runs and days (5.38 at breadth 0.775 in R2c and R3). The capacity is a fixed parameter, not a state, so a hard-queue model can identify it exactly. | B22 | — | — |

Settle checks (`diag.out`, settle.py): every R3/R4 segment of 50 ticks or more settles in win. Spend is unsettled at the end of u.7-0–50, u1 (50 ticks), bid 0.75 and bid 5 cap 50 (these segments are still decaying). Conversions are unsettled at the end of bid 3.25, bid 0.75, bid 5 cap 50 and recovery R4 150–200.

## 4. Score-loss ranking

Loss is Σ over ticks of 1 − 1/(1 + |err|/σ), in tick units. On the new runs, 1,121 of 2,400 obs-ticks are lost: R3 138 / 251 / 270 and R4 121 / 142 / 199 (win / spend / conversions). The type is read from the error trace. "Level" means a persistent offset over the segment's second half; "dynamics" means timing or shape; "transient" means concentrated in the first 20 ticks.

| # | Run, segment | Observable | Lost / ticks | Second-half error (mean ± sd, σ) | Type | Cause (B-ID) |
|---:|---|---|---:|---|---|---|
| 1 | R3 u.7 50–249 | conversions | 119.8 / 200 | +0.99 ± 0.18 | **level** (+ dynamics over 50–100: plateau end and undershoot) | B25/B35 purchase yield; B22 |
| 2 | R3 u.7 50–249 | spend | 111.1 / 200 | +1.30 ± 0.14 | **level** (+ undershoot missed over 40–100) | B25, B24 |
| 3 | R3 u.7 50–249 | win_rate | 51.7 / 200 | −0.19 ± 0.31 | mostly noise floor (≈ 38); the dip is B30 | B36 |
| 4 | R4 bid 5 cap 30 | conversions | 41.4 / 50 | **+5.13 ± 0.14** | **level** | B26 |
| 5 | R3 u.85 | spend | 41.1 / 75 | +1.24 ± 0.17 | level | B25 |
| 6 | R4 bid 3.25 cap 100 (from reset) | conversions | 36.1 / 50 | −4.7 ± 3.9 | transient + dynamics (peak and plateau end) | B21, B22 |
| 7 | R4 bid 0.75 | conversions | 35.8 / 50 | +2.43 ± 0.44 | level | B37 |
| 8 | R3 u1 (50) | conversions | 34.0 / 50 | −2.98 ± 0.76 | dynamics (plateau) | B22 |
| 9 | R3 u.7 0–49 | spend | 33.9 / 50 | +4.0 ± 1.6 | transient (cap pinning, then undershoot) | B20, B24 |
| 10 | R4 bid 5 cap 50 | conversions | 33.5 / 50 | +2.66 ± 0.94 | level + slow dynamics | B26 |
| 11 | R4 recovery after bid 0.75 | conversions | 32.9 / 50 | −1.75 ± 0.86 | dynamics (rest-restart overshoot) | B33 |
| 12 | R3 u.7 0–49 | conversions | 32.8 / 50 | −0.2 ± 3.4 | dynamics (plateau and drop) | B22 |
| 13 | R4 bid 3.25 | spend | 32.8 / 50 | +1.26 ± 0.30 | transient (reset spend) + level | B20, B25 |
| 14 | R3 recovery after u.7 | conversions | 32.0 / 100 | −0.75 ± 0.21 | level (history-dependent baseline) | B34 |
| 15 | R3 u.85 | conversions | 31.5 / 75 | +0.19 ± 0.36 | dynamics (overshoot size) | B33 |
| 16 | R4 bid 5 cap 50 | spend | 29.3 / 50 | +1.80 ± 0.09 | level | B25 |

**Split by time since the last switch** (`split.py`):

| Run | Ticks within 25 of a switch: share, loss (win / spend / conv) | Ticks 25 or more after a switch: loss | Score on those later ticks (win / spend / conv) |
|---|---|---|---|
| R3 | 25 %: 44 / 70 / 73 | 95 / 181 / 197 | 0.75 / 0.52 / 0.48 |
| R4 | 50 %: 62 / 79 / 104 | 59 / 63 / 96 | 0.61 / 0.58 / 0.36 |

Scored episodes are 4,000 ticks with few switches, so the later ticks, and therefore **level errors, dominate**. This matches `round2-experiments.md` §1.2.

**v1 on the old data** (R1, R2c; in-sample for v1): scores 0.619 and 0.543. The same errors were already there:

- High-bid long-run level: R2c P7 spend +1.4σ and conversions +1.5σ (late means). R1 capped bid 5 conversions +2.5σ.
- Plateau missed: R2c 185–250 at −4σ.
- Rest-restart conversions overshoot missed: R1 435–480 and 510–545, −5σ.
- Reset spend transient: R2c −11σ at t = 165.

The fit had these errors in-sample, and the round-2 held-out errors have the same sign and size. So they are **structural** and were not caused by missing domain. The exception is B26: its size at bid 5 / breadth 0.55 (+5σ) is new, because no earlier run held bid 5 at breadth 0.55 for more than 40 ticks.

## 5. Explanations and minimal model changes, in priority order

Framework lessons apply: v1 already has **pinned parameters**, which point to missing structure:

- `ret_y` = 1.0: the readiness pool is static.
- `eps_x` ≈ 1e-7 and `ret` ≈ 1: the slow pool X is switched off.
- `a_m3` held by hand at 0.005.
- g3 = −15.5: the tanh priming multiplier is effectively a switch between 1 and 0.2.
- om = 8.1: the ring work ratio is extreme.

`longrun.py` shows that v1's M2 (F, τ ≈ 150) carries **all** the depletion. Without it, u.7 spend would be 76 at the cap. M3 cuts broad-breadth conversions by 7–9 %.

**0. Control step (free, do first): refit v1's structure on R1+R2c+R3+R4.** Include round-2 data before judging structure. If B25 and B26 survive a joint refit (expected, since they were already present in-sample), the structure is missing. Report held-out per run (fit on 3 runs, predict the 4th).

**1. B25 + B26 + B35 + R1 capped bid 5: purchase yield falls at high bid and keeps falling at constant spend.** Top priority: about 350 lost ticks in round 2, all on sustained ticks.

Candidates:

- (a) **M2 exposure fatigue acting on purchase propensity.** Repeated exposure makes people unresponsive, so they are still auctioned (spend and win unchanged) but stop converting. The driver is impressions per member, which is highest at high bid and narrow breadth. This explains why conversions/spend falls at *constant* spend (B26), and why it hits bid 5 at breadth 0.55 hardest.
- (b) A static per-impression yield that falls with bid, because marginal impressions won at high bid convert less. It fixes the level but cannot produce B26's drift at constant spend.
- (c) Domain only (refit). This is unlikely: the error is in-sample on R2c.

Simplest adequate change: **(a)**. Add a per-ring purchase-fatigue state Z_r, updated as Z_r += e_z·I_r/size·(1 − Z_r) − a_z·Z_r, with J_r ×= (1 − Z_r). Keep a_z bounded to [0.01, 0.1] (τ 10–100) and e_z > 0 (a one-sided driver; saturating by construction).

- This is a second, purchase-only role for M2's quote. It could also **replace** the pinned static Y (ret_y = 1).
- **Conflict check:** it must keep R1's recovery conversions (3.0–3.3) and the R2 P5 weak second pulse (B13). It may also absorb part of the rest-restart overshoot (B33, the old R7/R8), which has the same sign: a rested audience converts more. It conflicts with nothing observed.
- If a_z pins at a bound, try (b) as a static ring × bid factor.

**2. B22 + B23 + B38: hard fulfillment capacity (FIFO) instead of the soft minimum.**

- Replace `done = (want^-4 + capf^-4)^-1/4` with `done = min(C_work, Qw)`, with kf → 1 or kf free. Conversions per tick = work done / mean work per purchase in the queue. The plateau is then C_work / w(breadth mix), and the abrupt end comes when the queue empties.
- The data give the plateau directly: ≥ 7.6 at 0.55, 5.79 at 0.7075, 5.38 at 0.775. That fixes the work ratio between rings 3 and 4 at about 1.08 per 0.07 of breadth. It should let `om` come off its extreme of 8.1 (review G2).
- Keep the prepare stage (a_p), because the geometric drain with τ ≈ 7 after unsaturated holds (B6) comes from it. Under a hard queue the delayed drain (B23) follows automatically.
- **Conflict check:** R1's drain after bid 0 (τ 7), and the R2 P3 conversions peak of 6.95 at breadth 0.55, which is below 7.6, so consistent. A FIFO queue with per-ring work needs the queue's mix; the current pooled Qn/Qw average is enough.
- Keep a small smoothing (exponent ≥ 20) so the fitter's gradients survive.

**3. B24 (spend undershoot and recovery at R3 u.7; spend over-prediction during the backlog).**

- (a) The brief's "started purchases remain committed": people with pending purchases (in the prepare stage or the queue) are unavailable. Availability becomes 1 − X − F − κ·committed_r/size. The spend minimum then coincides with the backlog peak (seen: t ≈ 48, backlog clears at 62), and there is no undershoot where the backlog is small (breadth 0.55: seen in R4).
- (b) Delayed (multi-stage) return of converted customers.

Prefer (a). It reuses change 2's queue and one gain κ. Test it by fitting R3 0–100 and checking that R4 shows no undershoot.

**4. B20/B21 reset transient under control** (about 2 % of ticks, but in every episode).

- The rested uncapped spend is 79.5 at bid 3.25 / breadth 0.55 and more than 76 for 15 ticks at bid 3.95 / breadth 0.71. v1 swaps the ordering, so its breadth scaling of pool size × price (nu = −3.5, kp = 4.1) is wrong.
- Expect the joint refit (step 0) with the R3/R4 resets to fix most of it. No new structure is needed until that refit shows otherwise.
- Do not add a special reset term (review G10).

**5. B29 win–bid curve is too flat** (±1σ at bid 0.75 and 5). Refit with the R4 ladder. If the logit slope still shows saturation, let K vary by ring or use `p = pmax·b^h/(b^h + K^h)` with pmax < 1. This is harmless for older behaviours.

**6. B33 rest-restart conversions overshoot** (the old G1, −4 to −5σ). Re-evaluate after change 1. A purchase fatigue with τ ≈ 20–50 is the same sign and may capture it. If it does not, this is unknown; do not add a separate fast pool, which was rejected in v1.

**7. B31 / B30 small win transients** (≤ 1.4σ for ≤ 10 ticks). Leave them.

**Mechanism reading.** Round 2 gives no new evidence for M3 (broad priming). v1 uses it as a τ = 200 breadth penalty on conversions, and change 1 could absorb that role. M1 is still unsupported: win creeps *up* under pressure, and no undershoot follows uncapped pulses.

If change 1 is accepted, the natural next pair to try is **M2 (on purchases and opportunities) + M3 against M2 alone**. Bound every rate (framework lesson 8).

## 6. Reserve-step proposal (200 left; not spent here)

What remains unknown and affects the score: the scorer's **composition** episodes combine controls, and two of the three pairs have **never** been observed:

- **cap + breadth at recovery bid:** the cap stops binding at breadth 0.775 once the pool is depleted, but on a rested pool it binds. Unknown: whether cap 100 lets broad targeting spend far more.
- **bid + breadth at cap 20 (throttled):** the joint high-bid, broad setting while the budget is throttled. Unknown: the throttled win level, conversions under throttle at breadth 0.775 (does the throttle cut purchases proportionally?), and the win undershoot after a *capped* pulse (B9), which so far has been seen only at breadth 0.55.

Proposed run **R5 (fresh reset, 170 steps, plus 30 held for settle extension in chunks of 10–20):**

| Ticks | Steps | Action (bid, cap, breadth) | u | v1 prediction (last-10 win / spend / conv) | What each outcome decides |
|---|---:|---|---|---|---|
| 0–49 | 50 | 1.5, 100, 0.775 | (0, 1, 1) | t = 10–19: 0.247 / 32.3 / 5.70; t = 40–49: 0.246 / 20.1 / 4.16 | Spend above 20 for more than 10 ticks, and a settled level 1.5σ or more above R1's cap-20 breadth run (17.7): cap × breadth interaction; the pool at broad breadth is bigger than modeled (ties in with B20). A conversions plateau near 5.4 would confirm B22's capacity at 0.775 from a rested start. |
| 50–84 | 35 | recovery | — | 0.264 / 13.2 / 3.08 | Post-broad recovery (R category); breadth off-step under cap 100 history. |
| 85–134 | 50 | 5, 20, 0.775 | (1, 0, 1) | 0.187 / 20.0 (capped) / 2.89 | If conversions are ≥ 3.5 (as with breadth 0.775 alone in R1): the throttle does not scale purchases proportionally, so the pacing/ring structure is wrong. If they are ≤ 2.9, v1's composition holds. Throttled win decides the pacing form at broad breadth. |
| 135–169 | 35 | recovery | — | 0.266 → 0.265 / 14.0 → 13.2 / 3.0 (no win undershoot; min 0.265) | A win undershoot below 0.25 (as in R1 after the capped bid pulse): B9 is tied to *capped* pulses at any breadth, which keeps an M1-like or throttle-memory term alive. No undershoot: B9 is specific to breadth 0.55 or the R1 history, and can be dropped. |

Total: 170 steps, plus up to 30 for extensions (only if settle.py reports that the throttled segment or the cap-100 breadth segment has not settled). This spends the reserve fully.

Alternative if only 100 steps are allowed: keep rows 3–4 only (bid + breadth at cap 20, then recovery: 85 steps). This is the setting that recovery-spacing episodes produce whenever the bid and breadth pulses overlap while the cap sits at recovery.

**Not proposed:** another long high-bid hold. B25 and B26 are structural (present in-sample on old data), and R3/R4 already give 250 + 100 ticks to fit them; a refit, not more data, is the next step.
