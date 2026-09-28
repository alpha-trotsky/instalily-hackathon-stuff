# Market round 2: diagnosis of runs B and C (2026-09-28)

Diagnostician pass for `market`, following `plans/agent-prompts/round2-diagnostician.md`. **No simulator steps were spent and no model files were changed.**

- **Data.**
  - Old: `data/market/A.json` (600 ticks, single controls only).
  - New: `data/market/B.json` (schedule MK1) and `data/market/C.json` (MK2). Both are 600 ticks from a fresh reset, with controls from tick 0.
- **Model.** v1 is `fits/round2/v1_models/market/`, which is identical to `greybox/market_model.py` with the m12 + withdraw fit.
- **σ.** 0.1 × std of all market data after tick 20, as in `heldout.py`: price 0.865, volume 0.0354, depth 2.37. The pre-registered tables in `round2-experiments.md` §4.4 used σ = 0.92 / 0.021 / 1.93, and the verdicts below hold with either set.
- **Scripts.** All are under `toronto26-participant-kit/fits/market/round2/`:
  - `diag.py`: plots, segment table and loss ranking;
  - `diag2.py`: zoom plots, the depth drain, delays and volume regressions;
  - `cond.py`: v1 blocks driven by observed data.
- **Plots.**
  - [B_v1.png](../toronto26-participant-kit/fits/market/round2/B_v1.png) and [C_v1.png](../toronto26-participant-kit/fits/market/round2/C_v1.png): full panels plus controls, with the v1 overlay.
  - [ABC_zoom.png](../toronto26-participant-kit/fits/market/round2/ABC_zoom.png): zoomed volume and log depth for A, B and C.
  - [A_v1.png](../toronto26-participant-kit/fits/market/round2/A_v1.png): the old data.

## 1. Summary

1. **v1 fails badly out of sample.** It scores 0.23 / 0.20 / 0.34 (price / volume / depth) on B and 0.36 / 0.25 / 0.58 on C, against 0.64 / 0.57 / 0.89 in-sample on A. The errors are new-regime failures: on A, no segment has a late error above 1σ, except volume in the tax segment at 2.5σ.
2. **Joint rate + tax from reset is a regime v1 has never seen.** Depth drains at a steady 1% per tick to 12, without settling. The rate's price fall is almost completely blocked (95.6 against 74 predicted). Volume sits on a plateau of 2.75. This one segment costs 16% of all B + C score loss.
3. **The same joint pulse after a recovery behaves differently.** Price settles at 66.6, below rate-alone's 73 (−8σ against additive), and depth settles at the normal tax level (41.7). The joint effect is non-additive **and** depends on history (H1 holds, H4 fires).
4. **Order effect (H3).** After rate + tax, turning the rate off does **not** let price recover while any tax is on (86.9 against 94.1 for tax alone in A). Price jumps back to 94 about 25 ticks after the tax goes to 0. Rate 0.5 alone gives 84.35: m12 and m13 fit it (1.8σ off), m23 does not (9σ), so **M1 is confirmed again** (H2).
5. **Static nonlinearities and volume levels.** Depth against tax is concave (tax 0.5 gives 55.4 against 66.7 for the linear v1). Rate against price is convex (40% of the full log effect at half rate). Volume has held levels that v1 lacks entirely: it declines to 1.56 under joint, holds 2.08 under tax 0.5 after the rate, and holds 2.75 under joint from reset. Volume is the largest loss by observable.

## 2. Decision-rule verdicts

Values are means of the last 10 ticks of each segment. The err columns are data − candidate, in the heldout σ.

| Rule | Measured | m12 | m13 | m23 | Verdict |
|---|---|---|---|---|---|
| **H1: is joint 1 additive?** Trigger: price > 2σ from additive. | **From reset** (B 0–150): price 95.56 (not settled, still −0.09/tick), volume 2.74, depth 12.07 (not settled, −1%/tick). **After a 50-tick gap** (B 475–600): 66.63, 1.56, 41.70 (price settled). | 73.9 / 74.3 (err +25σ / −9σ) | 74.5 / 74.6 | 70.4 / 76.2 | **Non-additive: TRUE.** The miss is in opposite directions depending on history, so the rule's prescribed fix (depth-dependent price impact) explains at most the post-gap case, where lower depth gives a larger fall. It cannot explain the blocked fall from reset. Joint 0.7 after 150 ticks of recovery is close to additive for price (78.15 against 79.3, −1.3σ), but depth is 48.1 against 56.1 (−3.4σ, the tax curve). |
| **H2: rate 0.05 level** (C 0–125) | price 84.35, volume 1.79, depth 90.77 | 82.7 (+1.9σ) | 82.6 (+2.0σ) | 76.2 (+9.4σ) | **m23 rejected. M1 is present** (consistent with the Run A bootstrap). The response is convex in rate: ln(84.35/93) = −0.098 against −0.242 at full rate, a ratio of 0.40. Linear models overshoot by about 1.7 price units. |
| **H3: order and hysteresis.** Tax only after rate + tax (C 250–375) against tax only in A (325–450). | price 86.91, volume 1.75, depth 42.34 against A's 94.13, 1.82, 41.32 | 92.1 (−6σ) | 93.2 | 91.5 | **TRUE, and large.** Price stays about 7 below (8σ) for the whole 125 ticks, creeping up +0.016/tick. It stays depressed under tax 0.025 (88.4) and recovers only when the tax reaches 0 (+5.5 in about 30 ticks, after a 21-tick dead time). Depth shows no order effect (within 0.4σ). |
| **H4: slow memory?** Joint 1 after a 50-tick gap (B 475) against joint 1 from reset (B 0). Gain = drop from baseline (price 92.7, depth 91). | Price drop: 26.1 after the gap, and **−2.9 from reset** (above baseline; not settled). Depth drop: 49.3 after the gap, 78.9 from reset. | predicted equal gains | | | **The rule fires** (depth gain ratio 0.62 < 0.9, and the price ratio is far from 1), **but the cause is the reset state, not a gap memory.** Gap 150 (joint 0.7) and gap 50 (joint 1) both land on the static tax-depth curve (48.1 and 41.7), and the gap-50 recovery released depth to 88.4 in about 30 ticks. The history effect is "joint applied during the reset transient". B keeps a lasting depth deficit: 88.2–88.8 at ticks 300 and 470, against 91 in A and C. |

**Mechanism reading.**

- m23 is out a second time.
- M1 funding is strongly implicated by H3, because a rate-induced price depression persists until trading costs vanish. That matches the brief: "inventory ties up funding until settlement", with settlement needing trading that the tax suppresses.
- M2 versus M3 is not separated by these runs.
  - M3 evidence is still weak. There is about 1σ of overshoot after tax-off in C (95 → 94), and the rise continues about 15 ticks past the B 475 switch, which the pipeline explains.
  - M2 evidence is modest. Depth dips to 37 during the B 475–600 price crash (v1: 41) and recovers after it.

## 3. Behaviour catalogue

Market had no B-IDs yet, so B1–B10 restate the Run A relationships from `plans/market-plan.md` ("Model v1"), for reference. **New behaviours start at B11.**

- **Categories:** S = sustained, O = order, R = recovery, C = composition.
- **Errors:** "err" is v1 − data in σ, from the last-10 mean unless stated.

**Run A behaviours (all modeled by v1 in-sample):**

| ID | Behaviour | Status on new data |
|---|---|---|
| B1 | Reset transient: volume 90 → 2 in 15 ticks, depth rises to about 99 then drifts, price flat for about 12 ticks then drifts down | Volume captured. Depth is not captured under rate from reset (B12, B19). |
| B2 | rate 1 → price −21%, 5–15 tick dead time, asymmetric on (60 ticks) / off (110 ticks) through the M1 lock | Not captured under tax (B13, B15) |
| B3 | tax → depth −54%, immediate, symmetric in linear units | Captured at 0 and 1 only. Mid-levels are wrong (B17). |
| B4 | tax-on price hump +6, no mirror on tax-off (withdraw term) | Captured in C 125–250 (hump 89 at tick 175; v1 87.9) |
| B5 | volume ≈ base·(1 + c·\|price speed\|) | Base level is wrong in several regimes (B16) |
| B6 | Price falls dent depth (M2, falls about 2× rises) | Partly captured (B20) |
| B7 | Levels return to about 93 / 1.78 / 91 after pulses | Varies with history: 91.8 (B), 94.0 (C) and depth 88.5 (B) (B21) |
| B8–B10 | Noise about 0.35–0.45% of level; rate has no direct effect on depth or volume; tax has no direct effect on volume | Noise confirmed (B22). The volume claims fail under joint controls (B16). |

**New behaviours (B11–B24):**

| ID | Behaviour | Evidence | v1 status (err in σ) | Categories |
|---|---|---|---|---|
| **B11** | **Joint rate + tax from reset blocks the rate's price fall.** Price drifts down linearly at −0.09/tick, against −0.275/tick for A's no-control reset drift, and still falls after release at −0.068/tick until about tick 230, reaching 91. | B_v1.png. Tick 150: 95.6 against v1 74.1. | **Not captured.** Late err −26σ, mean −21σ (B 0–150 price loss 137.5). The B 150–300 carry-over costs another 104. | S, C |
| **B12** | **Depth drain under joint from reset.** Depth 108 → 40 by tick 30, then a *constant fractional* loss of about 1%/tick (dlog/tick −0.0098, −0.0089, −0.0120 in successive windows) to 12.1 at tick 150, with no floor in sight. | ABC_zoom.png (log depth is straight) | **Not captured.** v1 settles at 41 (late err +9.4σ). The 4,000-tick extrapolation is unknown and could run toward 0. | S, C |
| **B13** | **Slow two-phase depth recovery after the drain.** 62% of the gap closes in 20 ticks (A tax-off: 93%), then about 2%/tick. Depth is 88–89 at tick 300, not 91. | `diag2.py` output | **Not captured.** v1 is back to 91 in about 20 ticks (mean err +5.5σ, loss 118.5). | R |
| **B14** | **Lasting depth deficit after B's drain.** Recovery level 88.2–88.8 at ticks 250–300 and 440–470 in B, against 90.8–91.1 in A and C. Could also be reset-state dependent (B's first observed depth was 108, against 87 in A and 102 in C). | segment table | Not captured, about +1σ | R, O |
| **B15** | **Price hysteresis under tax.** After the rate goes off, price stays depressed while tax > 0: 86.9 under tax 1 and 88.4 under tax 0.5, creeping up +0.016/tick. It recovers to 94 about 21 + 30 ticks after tax reaches 0. The rate-off dead time under tax is 41 ticks (26 without tax). | C_v1.png | **Not captured.** Err +6σ (C 250–375) and +4.8σ (C 375–500). Loss 90 + 106. | O, R |
| **B16** | **Volume has held levels that depend on regime**, not only on price speed. Last-10 levels: joint 1 after recovery 1.56 and still falling (drift 117σ); joint 0.7: 1.69 (falling); rate 0.5 + tax 1: 1.70 (falling); tax 1 after rate: 1.75; tax 0.5 after rate: **2.08 plateau** for 125 ticks; joint from reset: **2.74 plateau** (2.9 → 2.73); recovery 1.78–1.82. Under joint controls volume decays slowly below base in all three joint segments. | ABC_zoom.png middle row. Regression on rise/fall/r/τ/rτ has residual std 0.35 (B) and 0.16 (C), against 0.087 (A). | **Not captured.** Err −25σ (B 0–150), +8.3σ (B 475–600), −8.5σ (C 375–500), +4σ (C 125–250, C 250–375). Volume is the largest loss: 479 (B) and 453 (C). | S, C, O |
| **B17** | **Depth against tax is concave.** tax 0.5 → 55.4 and tax 0.7 → 48.1, against linear 66.7 / 56.1. `91/(1 + 1.19τ)` gives 57.0 / 49.6 (within 0.7σ), and `91·exp(−0.785·τ^0.66)` gives 55.4 / 49.0. Rate has no effect on depth (rate 0.5 + tax 1: 41.9, against tax 1 alone: 41.3–42.3). | segment table | **Not captured.** +4.8σ (C 375–500), +3.4σ (B 300–425). Loss 100 + 95. | S, C, R (every 70–85% pulse) |
| **B18** | **Rate against price is convex.** Half rate gives 40% of the full log effect (84.35 against the linear 82.4). Joint 0.7: 78.15. | C 0–125, B 300–425 | Partly captured: err −1.8σ (C 0–125), +1.3σ (B 300–425) | S, R |
| **B19** | **Rate from reset dents depth** (C: 102 → 81 at about tick 50, recovering to 90.7 by 125; v1 87). This is a milder version of B12 without tax, and it unwinds. | C_v1.png | Not captured, about −2.5σ at the trough (C 0–125 depth loss 58.7) | S |
| **B20** | **Depth dip during a fast price crash under tax** (B 475–600: 41.5 → 37 at about tick 550 → 41.7), the M2 signature at a low depth level | B_v1.png | Not captured (v1 flat at 41), about 1.7σ over about 60 ticks | C, R |
| **B21** | **Joint 1 after recovery is deeper than rate alone:** 66.6 against 73 (A). A pre-fall rise continues about 15 ticks past the switch (92.5 at tick 490), then the price falls at −0.45/tick. There is no interaction at rate 0.5 + tax 1 (84.9 against 84.35 for rate 0.5 alone, plus A's roughly +1 for tax). | B_v1.png | **Not captured.** Err +8.9σ, late +11σ (loss 109) | C, R |
| **B22** | **Noise is about 0.35–0.5% of level** for all three observables, including depth 15 (0.065, 0.42%). Proportional noise is confirmed down to low levels. | `diag2`/noise table | n/a. Consider scoring and fitting in log units for depth. | — |
| **B23** | **Gap-50 recovery** after joint 0.7: price rises fast (78 → 87, about 0.25%/tick, after a 15-tick dead time), much faster than A's rate-off recovery. Volume is 2.65 against the predicted 2.1. Depth recovers to 88.4 in about 30 ticks. | B_v1.png | Price err −5.5σ, volume −15.5σ (loss 33 + 47) | R |
| **B24** | **Reset initial state varies between resets.** First depth reading: 87 (A), 108 (B), 102 (C). Initial volume 90–101, price 107–110. The scale is far above 0.4% noise. | `diag2` output | v1 starts from `initial`, so this is fine. It affects B14's interpretation and the value of a replicate. | all |

**Delays** (ticks after a switch until the 3-tick mean moves more than 4 noise-σ; `diag2.py`):

- Price: 14–26 ticks after rate or joint switches, 20 after tax-on, 41 for rate-off under tax, 21 after tax-off.
- Depth: 0 ticks for every tax switch.
- Volume: 0–9 ticks.

**On/off symmetry.**

- Depth on/off in the B 425/475 gap is symmetric in linear units, settling in 20–30 ticks each way, as in A.
- The exception is after the drain: off is slower than on (B13). In log units, the drain-off rise (12 → 60 in 20 ticks) is faster than the on-fall.

**Relationships between outputs.**

- Volume excess no longer follows |price speed| alone. `cond.py` feeds v1's volume block with the (smoothed) observed price and still gets 1.89 against 2.74 in B 0–150, and 1.83 against 2.08 in C 375–500.
- Depth-withdraw → price: driving v1's price with the observed (smoothed) depth drain raises B 0–150 price only to 78.8 (data 95.6). The blocked fall is **not** a side effect of the depth drain through the existing withdraw term.
- Each block therefore fails on its own.

**Settling** (`python3 -m greybox.common.settle`, per segment).

- Not settled at the segment end:
  - B 0–150 (all three observables);
  - B 150–300 depth (drift 47σ_noise);
  - B 475–600 volume (drift 117) and depth;
  - C 125–250 volume;
  - C 375–500 volume and price (a slow creep).
- Settled: price in C 0–125 (66 ticks), C 125–250, B 475–600 (82 ticks), and depth for every tax step except the drain.

## 4. Score-loss ranking

Loss = Σ over ticks of 1 − 1/(1 + |err|/σ), for v1. The totals are A 546, B 1,338 and C 1,089, out of 1,800 each. The top 5 pairs are 26% of all B + C loss.

| # | Run, segment | Observable | Loss | Late err | Mean err | Type | Cause (B-ID) |
|---:|---|---|---:|---:|---:|---|---|
| 1 | B 0–150 joint 1 from reset | volume | 140.7 | −23.9σ | −16.6σ | **level** | B16 plateau 2.75 |
| 2 | B 0–150 | price | 137.5 | −26.1σ | −20.6σ | **dynamics → level** (blocked response) | B11 |
| 3 | B 150–300 recovery | depth | 118.5 | +2.6σ | +5.5σ | **transient** (slow recovery) | B13, B14 |
| 4 | B 0–150 | depth | 112.5 | +9.4σ | +5.6σ | **level / drift** | B12 |
| 5 | B 475–600 joint 1 again | price | 109.0 | +11.1σ | +4.2σ | **level**, plus timing of the pre-fall rise | B21 |
| 6 | C 375–500 tax 0.5 | volume | 108.4 | −9.3σ | −8.3σ | **level** | B16 plateau 2.08 |
| 7 | B 150–300 | volume | 106.6 | +2.9σ | +2.8σ | transient | B16, B13 |
| 8 | C 375–500 | price | 105.6 | +5.0σ | +5.5σ | **level** (hysteresis) | B15 |
| 9 | B 150–300 | price | 104.3 | +0.2σ | −8.9σ | transient (carry-over from B11) | B11 |
| 10 | B 475–600 | volume | 103.7 | −1.9σ | −6.0σ | dynamics (bump, then decay to 1.56) | B16 |
| 11 | C 250–375 tax only | volume | 101.8 | +4.1σ | +5.0σ | level | B16 |
| 12 | C 375–500 | depth | 100.3 | +4.7σ | +4.3σ | **level** (static curve) | B17 |
| 13 | B 300–425 joint 0.7 | depth | 95.2 | +3.3σ | +3.2σ | **level** (static curve) | B17 |
| 14 | C 250–375 | price | 89.9 | +5.4σ | +2.0σ | level (hysteresis) | B15 |
| 15 | C 125–250 | volume | 89.1 | +3.8σ | −1.2σ | level / slow decay | B16 |

**By type.**

- About 60% of the top-15 loss is **level** error: persistent offsets over a whole hold, which cap the score at about 0.1–0.3 while they last.
- Transient and carry-over errors (#3, #7, #9) come next.
- Pure timing errors are minor.

**Old data.**

- v1 on A has no level error above 1.1σ, except volume in the tax segment at 2.5σ late. Its A losses (40–67 per segment-observable) are the noise and transient floor at this σ.
- None of the top errors existed in A. **All of them are new-regime failures:** joint controls, mid-levels, tax after rate, and controls from reset.

## 5. Explanations and minimal model changes, in priority order

The simplest explanation comes first in each item. Framework lessons applied:

- one-sided drivers for single-switch effects;
- bounded or multiplicative forms;
- no additive state that can cross a bound over 4,000 ticks.

1. **B15 (and part of B11): tax-gated settlement of the M1 funding lock.**
   - **Explanation:** the brief's M1. Locked funding is released only by trading, and the tax suppresses trading.
   - **Change:** `k_out_eff = k_out · g(τ)`, with `g` bounded in (0, 1), for example `g = (1 − τ)^n` or `sigmoid(κ·(τ0 − τ))`. It needs to be about 0.05 at τ = 0.5 and τ = 1, and 1 at τ = 0.
   - **Captures:** the C 250–500 hold and the jump at 500. It adds 2 parameters.
   - **Conflicts:** none with A, where F had already released before the tax, so F ≈ 0.
   - **Do not** gate `k_in` the same way: B 300 and B 475 show that the rate lowers price quickly under tax after a recovery.
2. **B16 volume levels: a volume level state separate from the price-speed term.**
   - **Simplest:** a multiplicative, slowly relaxing factor `V_level ∈ [0.5, 2]` driven by r·τ, which decays below base under joint control (three joint segments all decline).
   - **Candidate unifying explanation:** volume excess = the flow of inventory unwinding through trading (M1 inventory stock). This fits:
     - C 375–500, where tax 0.5 lets locked inventory trade out slowly: plateau 2.08;
     - tax 1: nothing trades (1.75);
     - tax 0: a burst (2.25), then base.
   - **It does not explain** the B 0–150 plateau of 2.75 under tax 1. That needs the reset inventory being forced out (see 3).
   - **Captures:** the largest loss block (volume is the biggest observable loss in both B and C). There is some risk to A's volume bumps if the new state is driven by |dp|. Keep the existing rise/fall term.
3. **B11 + B12 + B13 + B19: a reset-inventory stock under funding pressure.**
   - **Hypothesis:** the reset leaves an inventory I0 (the tick-0 volume burst of 100). The rate charges funding on it, which drains market-maker capital, so depth falls and price support holds. Trading unwinds it at a rate ∝ (1 − τ).
     - Without tax (C, rate 0.5), it unwinds within about 50–100 ticks, which gives the B19 dent that recovers.
     - With tax 1 (B), it cannot unwind, which gives the 1%/tick capital drain (B12), a slow capital refill (B13, time constant about 50 ticks) and a lasting deficit (B14).
   - **Change:** a capital state `K ∈ [K_min, 1]` (multiplicative on depth), with `dK = −a·r·I − ... + b·(1 − K)` and `I ← I − u(τ)·I` from `I = I0` at reset. This is an M1 extension; the brief's M2 "risk capacity" is the alternative reading of K.
   - **Blocked price fall (B11):** the same I could hold the price target up through forced-seller absorption. That is speculative, with no clean simple form. The free alternative is to test a `k_p(τ, K)` slow-down: price discovery slows when capital K is depleted.
   - **Conflicts:** none with A (no rate at reset). It must leave C 0–125's fast price fall intact.
   - **Risk:** unbounded extrapolation of the drain. Floor K and fit K_min from the reserve run (§6).
4. **B17 and B18: static nonlinear level maps.**
   - **Depth:** `d* = c_d·/(1 + w·τ)` (1 parameter, the same count as now).
   - **Price:** `rate` enters as `r^p` (1 parameter), or `F` locks toward `r^p`.
   - **Captures:** the 70–85% pulses and mid-levels that the scorer uses heavily. A (0 and 1 only) is unchanged by construction. This is cheap and should come first in any refit.
5. **B21: joint interaction after recovery** (66.6 against the additive 74).
   - **Simplest:** a price-target term `−w_rτ·r²·τ`, or a price impact that scales with 1/depth (the H1 rule). It needs to be zero at r = 0.5 (C 125–250 shows no interaction).
   - **Alternative:** history. Funding not fully released after the 50-tick gap, plus fix 1, may account for part of it. Fit fix 1 first and check what is left before adding a term.
6. **B20, B13 depth dips: M2 during fast falls at low depth.**
   - Make the M2 capacity loss multiplicative on the tax-reduced depth, not additive on base depth. This is a small gain, so do it last.

**Parameter-pinning watch.** v1's `w_r` came out negative (−0.134, so the rate *raises* price directly and `w_f` does all the work), and `k_in` is pinned at 0.999. After fix 1, refit with those two freed and check that they move off their limits.

## 6. Reserve-step proposal (for approval; not spent)

**Budget.** `round2-experiments.md` §4.4: 1,400 left before round 2, with 1,200 used by B and C, which leaves **200**. Confirm with the free `python run_schedule.py --budget market` first.

**Largest unknown.** Does the joint-from-reset regime (B11 / B12) come from **tax during the reset transient**, or does it need **rate and tax together**? And does the drain continue past 150 ticks? Scoring episodes all start from reset, and the sustained and composition categories hold controls for thousands of ticks, so this regime decides a large block of the score. v1 predicts depth 41, while the data points toward 0.

**Run D: one fresh reset, 200 steps, run as two `--continue` segments.**

| Ticks | Action (rate, tax) | Steps | What each outcome decides |
|---|---|---:|---|
| 0–99 | (0, 0.05): tax only from reset | 100 | **Depth < 35 and still falling at tick 100:** the drain is tax × reset state, and rate is not needed, so drop the r factor from fix 3's drain. **Depth settles at about 41:** the drain needs rate × tax (fix 3 as written). **Price drift about −0.09/tick** (as in B): tax slows reset price discovery (the k_p(τ, K) form). **About −0.27/tick** (as in A): the blocked fall in B is rate-specific. **Volume plateau about 2.7:** the reset-inventory unwinding reading of B16. **About 1.8:** the plateau needs the rate. |
| 100–199 | (0.1, 0.05): add the rate | 100 | **Price falls to ≤ 75 within 70 ticks:** tax does not block rate transmission once the reset transient has passed, so the B 0–150 block is reset-specific. **Price keeps drifting slowly:** tax-from-reset puts the market into a state that blocks rate transmission, and that state persists at least 200 ticks (gate on K). **Depth:** whether the drain starts or accelerates when the rate is added, which fits the drain's r-coefficient and, if it continues to tick 200, gives the long-run slope for K_min. |

**Alternative, if the user prefers a long-run answer over the causal split:** a fresh reset with joint (0.1, 0.05) for 200 ticks. It replicates B across a different reset initial state (B24; does the drain rate scale with initial depth?) and extends the drain to 200 ticks, which bounds K_min. The cost is again 200 steps. It is less informative about the cause, so it is second choice.

**Not recommended for the reserve:**

- volume plateau at tax 0.5 from a clean state;
- rate 0.07 alone.

Both are static-map questions that fixes 2 and 4 can interpolate with bounded forms.
