# Reservoir round 2: diagnosis of R4/R5 against v1

Diagnostician pass, 2026-09-28. **No steps spent, no model changed.** Every number below is reproducible for free from
`toronto26-participant-kit/`. The scripts, logs and plots are in `fits/reservoir/round2/`:

| Script | What it does | Log |
|---|---|---|
| `plots_table.py` | Plots, per-segment last-10 table, raw score-loss ranking | `plots_table.log` |
| `nrloss.py` | Noise-reduced loss ranking and level/dynamics/transient classification | `nrloss.log` |
| `rules.py` | Decision rules: candidates run on the **actual** initial readings | `rules.log` |
| `water.py` | Groundwater excess, exchange and refill lag | `water.log` |
| `qnoise.py` | Quality noise, seasonal check, noise-reduced quality loss | `qnoise.log` |
| `qtest.py` | Quality-only refit of v1 variants (diagnostic only) | `qtest.log` |

**Plots** (black dots = data, red = v1, pink band = ±score σ):

- [R4_v1.png](../toronto26-participant-kit/fits/reservoir/round2/R4_v1.png) and [R5_v1.png](../toronto26-participant-kit/fits/reservoir/round2/R5_v1.png) show the data and v1 for each observable, with a controls panel.
- [R4_err.png](../toronto26-participant-kit/fits/reservoir/round2/R4_err.png) and [R5_err.png](../toronto26-participant-kit/fits/reservoir/round2/R5_err.png) show the error in σ, with a 9-tick moving average.

**Definitions:**

- σ is the score σ, 0.1 × std of all reservoir data after tick 20 (R1–R5, as in `heldout.py`): level 24.5, inflow 0.156, outflow 0.405, quality **0.00102**.
- Ticks are 0-based observation indices.
- Held-out v1 scores on the new runs (`heldout_v1_reservoir.json`):

  | Run | level | inflow | outflow | quality |
  |---|---:|---:|---:|---:|
  | R4 | 0.870 | 0.698 | 0.878 | **0.142** |
  | R5 | 0.812 | 0.757 | 0.851 | **0.190** |

  The mean is 0.650.

## 1. Summary

1. **Quality accounts for 66% of v1's noise-reduced loss on R4/R5.** The error is a persistent **level offset**, and v1 is too low everywhere: −20σ over R4's 200-tick recovery, and −3.5 to −9.5σ in every R5 segment. Water (level, inflow, outflow) is fine, within 0.2–0.6σ.
2. **v1's "recovery quality drifts down with time since reset" is falsified.** R4 recovers to **0.950 at t = 300–449**; v1 says 0.930. The data point to history instead: a post-anoxia offset persists **only when little water has been drawn from depth** (R1, R5). Drawing the reservoir down through a deep outlet (R2, R4) leaves no offset (§3, B17).
3. **Aeration dose-response is strongly convex in "no aeration".** Aeration 0.3 removes about 65–75% of the anoxia effect, where v1 (linear in u) removes 30%. This is the pulse-box interior (aeration 0.15–0.3) that the scorer uses most.
4. **Water side.** Three errors remain:
   - The groundwater reset excess (+1.3 to +2.2 at tick 0 when the initial level is below 560) is missed entirely.
   - The sustained low-level excess is about 0.1–0.15 too small.
   - During refill, v1 loses too much water to the bank, so the level lags by up to 1σ and spill starts about 5 ticks late.
5. **Mechanisms.** M1 is confirmed again. The pre-registered M3-vs-M2 rule gives **no selection**: both candidates are 12–20σ off, and the value that falsified m13 is its G3 term, not M3 itself. There is weak new evidence against M2: 250 ticks of irrigation in R4 left no delayed water or quality return.

## 2. Decision-rule verdicts

Each quantity is the mean of the last 10 ticks of its segment. Candidates were re-run on the actual initial readings (`rules.py`). The pre-run numbers in `final_reservoir.out` used a different initial level, so only the rule-1 and rule-3 quality values are comparable with those.

| # | Rule (§5.2) | Measured | m13 (v1, shipped) | m12_all | Verdict |
|---|---|---|---|---|---|
| 1 | RS1 recovery quality settles M3 vs M2. Pre-registered: m13 0.930, m12 0.937–0.939 | R4 250–299: **0.9521**; R4 300–449: **0.9496** | 0.9298 (−21.9σ); 0.9296 (−19.6σ) | 0.9389 (−13.0σ); 0.9366 (−12.8σ) | **No selection.** The data lie beyond both candidates, on m12's side, so the rule's literal reading leans M2. But the value that separated them is m13's G3 remobilization term, fed by aeration-on while deep. R4 held aeration 0.3 and depth 0.7 for 250 ticks, and v1 builds a near-permanent Cm from it, which the data refute. With gC = 0, v1 gives 0.941 (−8.5σ), and m12 is off by the same shared baseline. The mechanism pair stays **M1 + (M2 or M3) unresolved**, with weak evidence against M2 (B21). |
| 2 | Release 10.5 pins the outflow cap's level exponent. Pre-registered 515, from a different initial level | R5 0–149: level **458.5**, outflow **10.54** = request | 443.6 (−0.6σ), outflow 10.50 | 443.6 | **Rule not applicable.** At V = 410–480 the capacity C(V) ≈ 12.6–13.2 exceeds 10.5, so delivery equals the request and the exponent is not exercised (outflow error 0.1σ). The segment instead measures the **mid-level net balance**. The level rose slowly, from 411 to about 460 with season ripple, not settled, about 0.1/tick more than v1 (B24). The 4,000-tick knife-edge forecast (563–635) is still an extrapolation. |
| 3 | Aeration ladder gives quality's dose-response | aeration 0.3, shallow: **0.9444**; aeration 0.15 + depth 0.5: **0.9352**; aeration 0 + depth 0.5: **0.9292** (none settled, still drifting) | 0.9375 / 0.9311 / 0.9214 (−6.7 / −4.1 / −7.6σ) | 0.9405 / 0.9348 / 0.9312 (−3.8 / −0.4 / +2.0σ) | **Convex dose-response.** From a 0.949 start, aeration 0.3 lost only about 0.005 in 80 ticks. Aeration 0 lost about 0.017 in 60 ticks (R1 300–359). So aeration 0.3 has 25–35% of the full anoxia effect, where linear u gives 70%. Fit ua_eff = ua^γ with γ ≈ 3 (B18). v1 over-predicts the decline at every interior level. |

## 3. Behaviour catalogue (new runs; continues B1–B13 of `reservoir-plan.md`)

Each row gives the status against v1, the σ error and the categories affected: **S** sustained, **O** order, **R** recovery, **C** composition.

| ID | Behaviour | Evidence | v1 status | Categories |
|---|---|---|---|---|
| B14 | **Reset transient under control (quality).** From a reading of 0.79–0.87, quality reaches 0.95 within 3–10 ticks and **overshoots to a peak at t ≈ 10–30**. The peak grows with early withdrawal: R3 (pulse) 0.964, R4 (u = 0.7) 0.963, R5 (release 10.5) 0.957–0.960, R1/R2 (recovery) 0.952–0.956. It then decays toward the setting's level with τ ≈ 20–40 ticks. | 10-tick means (`rules.log`, `plots_table.log`); R4 10–29 | Roughly captured. The start is right, but the peak is 0.005–0.007 low (R4 0–99 −3.5σ). v1 builds the overshoot from a slow z term that decays over 130 ticks, which drives B15. | S, O, R, C (every episode) |
| B15 | **The aerated baseline is 0.950 and does not drift with time since reset.** R4 300–449 (level full, t = 300–449) holds 0.9496, with slope ≈ 0. R5 0–149 (release 10.5, aerated) holds 0.952–0.955. | R4 recovery, settle: quality settled, drift 0.27 noise σ | **Not captured: −20σ.** v1 has cq = 0.940 plus a z decay of +0.017 at a_z = 0.0076, so it predicts 0.930–0.941 after t ≈ 300 whatever the history. On old data the same error was already there at −4σ (R2 280–339, 370–399). | S, R (every late tick) |
| B16 | **Aeration off: slow decline; aeration on: fast recovery.** The decline has no dead time and τ ≈ 55 ticks (R2, R4) or is longer and near-linear when full (R1, R5). Recovery after aeration is restored is 70–80% complete within 5–15 ticks (R5 390: 0.929 → 0.934 in 10 ticks, τ ≈ 7–15), then plateaus. The on/off asymmetry is 4–8×. Log(1 − q) units do not remove it; the asymptotes differ by the same ratio. | `qtest`/τ fits in this report; R5 385–410 | Partly captured. v1's on-recovery τ is 15–25 (too slow, costs 2–4σ for about 20 ticks after each aeration return), and its off-decline is too steep at the interior (B18). | O, R |
| B17 | **The persistent post-anoxia offset depends on deep flow-through (or drawdown), not on anoxia dose.** Plateau after aeration returns, relative to 0.950: | See the table after this one | **Not captured** (v1's Cm is gated by depth at the moment aeration returns and decays only through dC ≈ 0.0005). R4: −20σ. R5 end: +1σ, correct by accident. R2 280–339: −4.4σ. Deep flushing and low level are confounded in our data (R2 and R4 both drew down deep), so a reserve probe is needed (§6). | R, O |
| B18 | **Convex aeration dose-response** (rule 3). Aeration 0.3 costs about 0.004–0.009 (R5 150–229 at full; R4 100–249 at low level, depth 0.7: 0.9435), against 0.017–0.023 for aeration 0. The effect ratio is 0.25–0.37, so γ ≈ 2.8–3.4 in ua^γ. | R5 ladder, R4 100–249, R1 300–359, R2 190–239 | **Not captured:** −7 to −10σ at aeration 0.15–0.3. | S, C (pulse interior) |
| B19 | **Groundwater reset excess** = 0.0149·(561 − V0)+, decaying about ×0.6–0.7 per tick. R4 (V0 476): +1.31, 0.73, 0.58, 0.43. R5 (411): +2.22, 1.51, 1.00, 0.88. It fits R1 (515: +0.68) and R3 (404: +2.33) on one line, and R2 (601: 0). | `water.log` first 8 ticks | **Not captured.** v1 gives +0.06 (R4) and +0.29 (R5), up to 14σ on tick 0 and about 5 ticks > 2σ per episode. The fitted H0 = 443 is a compromise between this and B20. | all (first ~10 ticks, when V0 < 560) |
| B20 | **Sustained groundwater excess at low level.** ≈ 0.0021·(490 − V)+: R4 at V 285–365 gives +0.24 to +0.43, and R5 at V 430–470 gives 0 to +0.10. It shuts off **within 5–10 ticks** when the level starts rising (R4 250–259: +0.23 → −0.01). | `water.log` 25-tick blocks; R4 240–275 | **Partly captured.** v1 is 0.08–0.16 too low at V ≈ 300 (−0.5σ on 150 ticks of R4), and its shut-off takes about 25 ticks (+0.1–0.2 too high for 20 ticks). | S (pulse holds), R |
| B21 | **No irrigation return.** After 250 ticks of irrigation 5.6 (R4), the excess is 0.00 ± 0.02 over 275–449, and quality **rises** from 0.944 to 0.952, with no delayed dip. | R4 250–449 | Consistent with v1 (m13 has no M2). **Evidence against M2**, in both its water and quality branches. | — |
| B22 | **The capacity law holds from reset under control.** Delivery = min(request, 16.5·(V/940)^⅓). u = 0.7 requests 14.6 and delivers 13.1 → 11.2 as V falls 470 → 285. Release 10.5 at V 410–480 delivers exactly 10.5. | `water.log` outflow columns | **Captured** (±0.05, ≤ 0.15σ). | S, C |
| B23 | **Bank-charging loss during refill is smaller than v1's.** The exchange E during a fast rise is −1.4 to −1.6 (R4 275–324, R5 150–199), where v1 gives −1.8 to −2.1. At the cap it relaxes from −1.5 to −0.8 over 100 ticks (R4). | `water.log` | **Not captured.** Level lags by up to −30 (−1.2σ) at R5 200–212 and −0.6σ on average over the refill. Spill starts about 5 ticks late (outflow 6.76 vs 5.65 at R5 200–224). | R, O |
| B24 | **Mid-level net balance at release 10.5.** The level rose from 411 to about 460 over 150 ticks (+0.1–0.3/tick net, season-modulated), and E ≈ −0.56 to −0.70 at V ≈ 450. | R5 0–149 | Slightly off: v1 is 15 low at the end (−0.6σ). Half of that is the B19 transient (+5.5 volume) and half is too much loss (≈ 0.07/tick). | S |
| B25 | **Quality noise** is 0.0047–0.0054 in every run, independent of level and setting, about **5σ per tick**. Quality has no seasonal component (amplitude ≤ 0.0002). The other noise σ: level 3.1–3.8, inflow 0.050–0.063, outflow 0.044–0.053 (unchanged). | `qnoise.log`; settle σ | n/a. Local quality scores are therefore ceiling-bound (~0.3 raw), while the organizer scores against noiseless truth, **so a level offset in quality costs far more publicly than locally.** | — |
| B26 | **Surprise.** In R4, a partial-anoxia pulse at low level (aeration 0.3, depth 0.7, 250 ticks) left quality *higher* afterwards (0.950) than the full-reservoir recovery in R1 (0.941 at t = 200–249, after irrigation 8 at full). R1's 200–249 dip (−0.009, after irrigation) remains unexplained. It is the only remaining hint of an irrigation effect, and R4 argues against it (B21). | R1 200–249 vs R4 300–449 | Open | R |

**B17 evidence table** (plateau relative to 0.950):

| Case | Anoxia dose (Σ(1 − aeration)) | Deep flow-through Σ depth·D/V | Lowest level | Plateau | Offset |
|---|---:|---:|---:|---:|---:|
| R1 300–410 → 420–469 | 110 | 0.51 | 927 | 0.9335 | −16σ |
| R2 340–370 → 380–399 | 30 | 0.63 | 686 | 0.9414 | −8σ |
| R5 150–390 → 400–449 | 204 | 0.85 | 477 | 0.9381 | −12σ |
| R2 40–240 → 290–339 | 200 | 5.20 | 377 | 0.9468 | −3σ |
| R4 0–250 → 300–449 | 175 | 6.11 | 271 | 0.9506 | +0.5σ |

The offset falls monotonically as deep flow-through (or drawdown) rises, and it is uncorrelated with dose.

**Settling** (`python3 -m greybox.common.settle`, per segment):

- **Level and outflow.** Settled in every hold except the refills. The release-10.5 level is flagged settled by the exponential fit, but it is still rising at about 0.1/tick under the season ripple.
- **Inflow and outflow flagged "unsettled".** That is the season, not a drift.
- **Quality.** Flagged settled in every hold except R5 230–309. However, the settle threshold (2 × noise σ = 0.01 ≈ 10 score σ) is too coarse for quality. By 10-tick means, R5 150–389 and R4 100–249 were still drifting by 0.002–0.005 per 80 ticks.

## 4. Score-loss ranking (noise-reduced)

Method: error series pred − obs, smoothed within each segment by a centred moving average (9 ticks for water, 21 for quality) to remove the per-tick noise, then Σ(1 − 1/(1 + |e|/σ)). Classification:

- **transient:** more than 60% of the loss is in the first 20 ticks of the segment;
- **level:** the 2nd-half mean error is more than 1.5 × its spread;
- **dynamics:** otherwise.

Raw (noisy) rankings are in `plots_table.log` and give the same order.

**New runs (total 1,152 obs-ticks lost of 3,600): quality 756 (66%), inflow 169, level 117, outflow 110.**

| Rank | Segment | Observable | Lost | Share | 2nd-half err | Type | Cause |
|---:|---|---|---:|---:|---:|---|---|
| 1 | R4 300–449 recovery | quality | 143 | 12.4% | −20.1σ | level | B15 time-decay baseline plus B17 spurious Cm |
| 2 | R4 100–249 u = 0.7 | quality | 129 | 11.2% | −9.9σ | level | B18 linear aeration, B17 Cm |
| 3 | R5 0–149 release 10.5 | quality | 111 | 9.6% | −5.6σ | level | B14/B15: the aerated baseline stays about 0.953 with outflow |
| 4 | R4 0–99 u = 0.7 | quality | 76 | 6.6% | −3.6σ | level | B14 peak too low, B18 |
| 5 | R5 310–389 aeration 0, depth 0.5 | quality | 72 | 6.3% | −9.4σ | level | B18, B15 |
| 6 | R5 230–309 aeration 0.15, depth 0.5 | quality | 71 | 6.1% | −7.5σ | level | B18 |
| 7 | R5 150–229 aeration 0.3 | quality | 70 | 6.1% | −8.5σ | level | B18 |
| 8 | R4 100–249 | inflow | 53 | 4.6% | −0.5σ | dynamics | B20 sustained excess too small |
| 9 | R4 250–299 | quality | 48 | 4.1% | −20.8σ | level | B15/B17 |
| 10 | R5 390–449 recovery | quality | 37 | 3.2% | −0.3σ | dynamics | B16: on-recovery too slow; the plateau is right by accident |
| 11 | R5 0–149 | inflow | 33 | 2.9% | −0.3σ | dynamics | B19 reset excess |
| 12 | R5 0–149 | level | 30 | 2.6% | −0.4σ | level | B19 + B24 |
| 13 | R5 150–229 | level | 28 | 2.4% | −0.6σ | dynamics | B23 refill lag |
| 14 | R4 0–99 | inflow | 28 | 2.4% | −0.3σ | dynamics | B19 |
| 15 | R4 300–449 | outflow | 26 | 2.2% | 0.0σ | dynamics | B23: spill starts late |

**Old data (R1–R3, v1 in-sample): 894 lost, quality 572 (64%).** The quality errors there are **mixed in sign**, ±1.5–5σ:

- R2 280–339 −5.3σ: the same B15/B17 error, smaller;
- R1 360–409 +4.9σ;
- R2 0–39 +2.8σ.

The fit balanced them. The new runs have **one sign** (v1 too low) because they sit in regimes the old data never reached: a drawdown then refill without full anoxia, the aeration interior, and a long aerated hold at t > 300. The water errors B19, B20 and B23 were already present on old data (review G1, G7) at a similar size.

**Diagnostic quality-only refit** (`qtest.py`, water frozen at v1). Scores are raw/NR per run:

| Fit | R1 | R4 | R5 |
|---|---|---|---|
| v1 | 0.283/0.461 | 0.142/0.121 | 0.190/0.199 |
| v1 structure refit on R1–R5 | 0.250/0.318 | 0.264/0.346 | 0.291/0.379 |

R1 drops as R4 and R5 improve: **the v1 quality structure cannot fit R1 and R4 together.** The refit also pins a_z at 0.0006, lam_q at 0.09, dC at 0 and gC negative. That is framework lesson 9: pinned parameters mean missing structure.

A crude "flush" variant (γ exponent plus a deep-flow removal term) reached R4 NR 0.49 and R2 0.46. The optimizer left kfl at 0 and was numerically fragile (ua^γ at ua = 0), so it neither confirms nor rejects the flush term. The modeler should test it properly.

## 5. Explanations and minimal model changes, in priority order

1. **Remove the time-since-reset quality decay. Replace it with a fast reset overshoot and a 0.950 baseline** (B14, B15; ranks 1, 3, 4, 9).
   - *Explanation:* the reference profile is a plain dynamic, not a mechanism. After reset the column starts "fresh", the outlet overshoots while the early withdrawal draws the good layer, and it then relaxes within about 40 ticks.
   - *Change:* z decays at a_z ≈ 0.03–0.05. Let the overshoot amplitude scale with early delivered outflow, lam_q·(1 + c·D/12). Let cq be free, which should give ≈ 0.950. Every persistent drop must then come from a history state (items 2 and 4), never from t.
   - *Conflict:* R1's decline to 0.941 at t = 200–249 was carried by the slow z. It then needs item 4, or stays as a 2–5σ miss on about 50 R1 ticks. That is acceptable: R4's 200 ticks at 0.950 outweigh it, and the scorer's recovery holds are long.
2. **Rebuild the post-anoxia offset as a flushed pool** (B17; ranks 1, 2, 9, 10).
   - *Explanation:* M3 (deposited material and the anoxic release pool) together with the brief's "a deep release can change later surface quality by changing stored layers" and "aeration can … remobilize deeper material".
   - *Minimal change to m3:*
     - The pool Dm builds under anoxia (ua^γ, item 3) and is **removed by deep withdrawal**: −kfl·ud·D/V·Dm.
     - On aeration return, Dm is moved into the column (Cm) **at any depth**: kr·Dm·(1 − ua_eff), **dropping v1's ud gate**. R5 recovered at depth 0 and still plateaued.
     - Cm decays slowly (dC free, but bounded ≥ 0.002 so it cannot pin), and is optionally also removed by deep flow.
   - *Alternative, same data:* removal ∝ drawdown (turnover by refill: inflow/V while V is rising after V < V_full − Δ). R2 and R4 cannot tell these apart, so the reserve probe (§6) decides.
   - *Conflict:* none with old data. It keeps R1 410–550 (low deep flow, plateau), fixes R2 280–339 (−4.4σ now) and fixes R4.
3. **Convex aeration dose-response** (B18; ranks 2, 5, 6, 7).
   - *Change:* a one-parameter saturating form, ua_eff = ua^γ (γ ≈ 3, bounded 1–5, and use max(ua, 1e-9) to avoid the 0^γ fragility), in both the direct target term and the pool build rate.
   - *Explanation:* a plain dynamic, since oxygen transfer saturates. Framework rule: bounded, saturating form.
   - *Conflict:* none. The endpoints u = 0 and u = 1 are unchanged, so every old hold is unaffected. Only the interior moves, and old data have no aeration interior.
4. **Optional, after 1–3: the R1 post-irrigation dip** (B26).
   - *Candidates:* M2 contaminant return (but B21 argues against it), or plain noise over 20 ticks (the 10-tick-mean se is 1.7σ).
   - *Change:* do **not** add an M2 quality branch unless it improves R1 without hurting R4 in a joint fit. If it does, prefer the pair whose total holds up in the bootstrap, and record that it rests on one 50-tick segment.
5. **Groundwater: split the fast reset excess from the slow head** (B19, B20; ranks 8, 11, 14).
   - *Explanation:* M1, confirmed.
   - *Change:*
     - (a) A separate fast reset store: Qr = gr·max(561 − V0, 0)·ρ^t with ρ ≈ 0.65. The head 561 and gain 0.0149 come from four resets on one line. That frees H0 and gf1 from carrying the reset.
     - (b) The sustained excess g·max(Href − V, 0), with a fast shut-off factor (1 − c·max(ΔV, 0)) so it stops within 5 ticks of a rise (reviewer G1). Href charges slowly with time spent full (R1's excess at V ≈ 770 after 470 full ticks) and starts at ≈ 490 at reset.
   - *Conflict:* none known. R2's late onset and R1's early onset are still the test of Href's charging rate.
6. **Bank-charging loss during refill** (B23, B24; ranks 12, 13, 15).
   - *Change:* reduce the refill-loss gain (gf1 or af1) or make the bank's capacity saturate, so that E ≈ −1.5 during a fast rise and ≈ −0.6 at V ≈ 450. This will probably fall out of the refit once item 5(a) takes the reset job off H0 and gf1.
   - *Conflict:* R1/R2 refill E was −2.0 (review R4). Check it against R4/R5's −1.5; the difference may depend on the bank's starting state (R1/R2 were near-full before draining, R4/R5 low).

The water items (5, 6) are worth about 0.05–0.10 on inflow and level. The quality items (1–3) are worth far more publicly: quality is a quarter of the score, σ ≈ 0.001, and v1 is biased 5–20σ in the scorer's most common regimes.

## 6. Reserve-step proposal (100 steps left; **not to be spent by the diagnostician**)

**Unknown that matters most.** Why the post-anoxia offset vanishes in R2 and R4. The candidates are:

- (i) removal by **deep** withdrawal flow;
- (ii) removal by drawdown or refill turnover (any outlet);
- (iii) a low level while aeration returns.

These give different forecasts for common scored episodes, such as "pulse then recovery" with depth pulsed or not, and for starting levels of 400–600.

**Schedule: two fresh resets, 50 steps each (100 total).** Every action is within the brief's bounds.

| Run | Ticks 0–29 | Ticks 30–49 |
|---|---|---|
| **XD** (deep flush) | release 12, irrigation 0, **depth 1**, aeration 0 | recovery (release 2, irrigation 0, depth 0, aeration 1) |
| **XS** (shallow flush) | release 12, irrigation 0, **depth 0**, aeration 0 | recovery |

- Both runs draw the level down by about 30·1.3 ≈ 40 from a reset level of 400–600.
- Both have the same anoxia dose (30 ticks, as R2's second pulse, which left −8σ) and the same drawdown and outflow. They differ only in outlet depth.
- The quality observable is the plateau mean over ticks 38–49 (12 ticks, se ≈ 1.5σ).

**What each outcome decides:**

| XD | XS | Reading | Change to make |
|---|---|---|---|
| ≈ 0.950 | ≈ 0.940 | Deep withdrawal flushes the pool: **(i)** | Item 2, kfl·ud·D/V |
| ≈ 0.950 | ≈ 0.950 | Low level or any flow-through prevents it: **(ii) or (iii)** | Removal ∝ D/V or (V_full − V), not depth-gated |
| ≈ 0.940 | ≈ 0.940 | Neither. The R2/R4 clearance needs a long drawdown or refill (turnover over more than 50 ticks) | Removal by refill turnover. Also keep aeration-return recovery τ (B16) separate from the plateau |
| < XS | — | Deep withdrawal *adds* material (the brief: "deep release can change later surface quality") | Swap the sign on the depth term |

- **Side readings, for free from the same 100 steps:**
  - two more reset excess points (B19 check);
  - the quality overshoot under a shallow versus a deep pulse (B14 amplitude driver);
  - the capacity at V ≈ 400 from reset (B22).
- **Step count: 100 = the whole reserve.** Record it in `plans/reservoir-plan.md`'s round-2 spend log.
- **Fallback if only 50 are allowed:** run XS only (0–29 shallow anoxic pulse, then 20 recovery). Against R2's deep 30-tick pulse (−8σ plateau, 0.63 deep flow) it answers (i) versus (ii)/(iii), though at a different starting level.
