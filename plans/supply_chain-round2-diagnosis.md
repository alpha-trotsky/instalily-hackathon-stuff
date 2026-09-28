# supply_chain: round-2 diagnosis (R4, R5)

Diagnostician pass, 2026-09-28. **No steps were spent and no model was changed.** The scripts and plots are in `toronto26-participant-kit/fits/supply_chain/round2/`:

- `analyze.py` runs v1 (`fits/round2/v1_models/supply_chain`) on R1–R5 and writes the segment table, the loss ranking (`segment_loss.json`), the plots and `arrays.npz`.
- `sales.py` computes implied retail sales per window.
- `retail_law.py` fits retail-sales laws driven by the **observed** shipments, which isolates the retail block.
- Plots: [R4_v1.png](../toronto26-participant-kit/fits/supply_chain/round2/R4_v1.png), [R5_v1.png](../toronto26-participant-kit/fits/supply_chain/round2/R5_v1.png), old runs [R1_v1.png](../toronto26-participant-kit/fits/supply_chain/round2/R1_v1.png), [R2_v1.png](../toronto26-participant-kit/fits/supply_chain/round2/R2_v1.png), [R3_v1.png](../toronto26-participant-kit/fits/supply_chain/round2/R3_v1.png), and retail laws [retail_law.png](../toronto26-participant-kit/fits/supply_chain/round2/retail_law.png).
- σ (score) = 0.1 × std after tick 20 over R1–R5 = **1.12 / 12.1 / 34.7** (shipments / supplier / retail), as in `heldout.py`.

## 1. Summary

1. On the new runs, v1 scores **0.353** (R4 0.333, R5 0.373), against 0.49–0.66 on the old runs. It is **below persistence** on shipments (0.20 vs 0.25, 0.24 vs 0.25) and roughly level with persistence on retail. The interior of the pulse box, the extrapolation blind spot from §1.3, is where it breaks.
2. Pre-registered rule 1 **fires strongly**. Shipments at orders 80 sit **+15% to +60%** above the model, not 10%. The receiving ladder pins the curve as **shipments = min(49.2·r, 34.8)**, a kink near r ≈ 0.71. v1's power law (r/1.5)^0.51 misses it by up to −11.6σ.
3. Pre-registered rule 2: maintenance 0.3 has **no effect** when receiving limits the flow (24.62 vs 24.58; v1 predicted +2.9σ). Maintenance acts on the upstream or drive limit U only, not multiplicatively on receiving.
4. Loss split: retail 43%, shipments 40%, supplier 17%. **About 70% is persistent level error.** Every interior hold has shipments −6 to −12σ and retail −6 to −13σ. Retail fails for two reasons: it inherits the shipment deficit, and its sales law is wrong in its own right (0.39–0.46 even when fed the observed shipments).
5. Top fixes: (1) a min(receiving capacity, upstream U) service structure; (2) a retail sales law that tracks arrivals; (3) order-driven supply: a supplier plateau at cap − q, and a supply step 25–30 ticks after orders start. The reserve (100 steps) should isolate which pulse control lifts receiving capacity by about 10% in the joint pulse (§6).

## 2. Decision-rule verdicts

The rules are from `plans/round2-experiments.md` §5.3. Values are the mean of the last 10 ticks of each segment. Candidates are the three fits screened in `fits/round2/final_supply_chain.out`: `base_all2` (= shipped v1), `phi_all` and `base_all`.

**Rule 1.** "If shipments on every orders-80 segment sit about 10% above the model, fix the service-rate structure. The receiving ladder then pins the curve."

| Segment (orders) | Data | v1 / phi_all / base_all | Data vs v1 | Error (σ) |
|---|---:|---:|---:|---:|
| R5 r 1.0 (80) | 34.7 | 25.9 / 26.8 / 26.0 | +34% | −7.9 |
| R5 r 0.7 (80) | 34.5 | 21.5 / 22.5 / 21.8 | **+60%** | −11.6 |
| R5 r 0.5 (80) | 24.6 | 18.1 / 19.0 / 18.5 | +36% | −5.8 |
| R5 r 0.5 + maintenance 0.3 (80) | 24.6 | 21.4 / 22.2 / 21.9 | +15% | −2.8 |
| R4 u1 (80) | 19.1 | 17.6 / 18.1 / 17.8 | +9% | −1.3 |
| R4 u.7 (56), interior | 36.6 | 24.1 / 24.7 / 24.4 | +52% | −11.2 |
| R4 u.85 (68), interior | 28.0 | 21.3 / 21.8 / 21.6 | +31% | −6.1 |

**Verdict: the rule fires. Fix the service-rate structure.** Every orders ≥ 56 segment is above every candidate, and the three candidates agree with each other to within 1σ while all being wrong (the §1.3 warning).

The ladder pins the curve. Receiving 1.5 / 1.0 / 0.7 / 0.5 / 0.35 gives 34.8 / 34.7 / 34.4 / 24.6 / 17.2 (the last from R1). That is exactly **min(49.2·r, 34.8)**: 49.2 × 0.5 = 24.6, 49.2 × 0.35 = 17.2, 49.2 × 0.7 = 34.4. Receiving-limited segments are flat with no cycle. Segments limited by the upstream U carry the period-2 cycle (B7), as at R5 r 1.0: 38.7/30.8.

**Rule 2.** "Maintenance .3 vs 0 vs 1 gives the maintenance dose-response."

| Comparison | Data | Candidates' prediction |
|---|---|---|
| r 0.5, maintenance 1 → 0.3 (R5 100–149 → 150–199) | 24.58 → 24.62 (Δ = +0.04, 0.03σ) | +3.3 (+2.9σ) |
| maintenance 0 at r 0.35 (joint pulses R4 u1 and R1 all-controls) | 19.1–19.3, vs 17.2 at maintenance 1 in R1 | confounded: rush, mix and effort also at pulse |
| maintenance 0 at r 1.5 (old R1/R2, U-limited) | 43.8 → settles at 37.2 after about 88 ticks | — |

**Verdict: maintenance does not scale receiving capacity.** It only moves the upstream limit U, which binds for r ≳ 0.7. The dose-response between 0 and 1 in the U-limited regime **is still unmeasured**, because the 0.3 point landed in the receiving-limited regime. v1's multiplicative `(1 + wm(1 − m))` is structurally wrong.

**Other pre-registered numbers.** These were stated in `final_supply_chain.out` and are not rules. Data vs v1:

| Segment | shipments | supplier | retail |
|---|---|---|---|
| u.7, ticks 50–149 | **36.6** vs 24.1 | 330.7 vs 337.7 | **722** vs 257 |
| recovery 60 | 2.1 vs 2.7 | 362.1 vs 361.8 | 281 vs 160 |
| u1 | 19.1 vs 17.6 | 345.5 vs 344.2 | 134 vs 8 |
| recovery 30 | 41.3 (burst) vs 31.8 | 361.6 vs 361.8 | 259 vs 223 |
| u.85 | **28.0** vs 21.3 | 341.1 vs 340.5 | **406** vs 204 (predicted range 175–220) |
| SU2 ladder | 34.7 / 34.5 / 24.6 / 24.6 vs 25.9 / 21.5 / 18.1 / 21.4 | — | — |

## 3. Behaviour catalogue (round 2; continues B1–B17 of `plans/supply_chain-plan.md`)

Categories: **S** sustained, **O** order, **Rc** recovery history, **C** composition. Error = v1 − data, in score σ.

| ID | Behaviour and evidence | v1 status | Categories |
|---|---|---|---|
| **B18** | **Receiving is a hard capacity, not a power law.** Shipments = min(49.2·r, U), with U = 34.8 at the recovery settings of the other controls. At the kink (r 0.7 → 34.4) the level is unchanged from r 1.0 (34.7), but the cycle vanishes within 1 tick (R5 t = 50). Receiving changes act within 1 tick (R5 t = 50 and t = 100). | **Not captured.** −7.9 / −11.6 / −5.8σ at r 1.0 / 0.7 / 0.5, on every tick of each hold | S, C |
| **B19** | **Maintenance is inert while receiving limits the flow.** r 0.5: maintenance 0.3 changes nothing (24.62 vs 24.58, both settled with drift < 1σ). | **Not captured.** +2.8σ over 50 ticks | C |
| **B20** | **Joint-pulse levels.** u.7 36.6: U-limited, with a period-2/4 cycle 32/36–39. u.85 28.0: flat, so receiving-limited, giving 28.0/0.5225 = **53.6·r**. u1 19.1: 19.1/0.35 = **54.6·r** (R1 all-controls 19.3 agrees). In the joint pulse, receiving capacity is **about 10% above** the 49.2 of the single-control ladder. u.7 needs ≥ 52.7·r. Which control (maintenance < 0.3, rush, mix or effort) adds the 10% is unknown. | **Not captured.** −11.2 / −6.1 / −1.3σ | S, C |
| **B21** | **Reset transient under control.** Shipments are 0 for 3 ticks, then spike 17–35 for ticks 3–12. Next comes a **supply-limited phase** while the supplier is at 0: 25.9 (R5: effort 1, mix 0.5) and 33.4 (R4 u.7: effort 1.35, mix 0.71). The flow then **steps to U at t ≈ 33 (R5)** and to about 36 at t ≈ 55–60 (R4), with the supplier still at 0. The supplier starts refilling only at **t = 78 (R5)** and **t = 86 (R4)**, at +9.6 and +14 per tick, up to the plateau. Retail starts rising by tick 7 (R4) or 12 (R5). | Partly. R5's 25.9 phase is right. **u.7 phase 24.1 vs 33.4 (−7σ)**. The supplier refills 13–24 ticks too early (**+28σ peak**, about 20 ticks). Retail ≈ 0 until t ≈ 40 (inherited from the shipment deficit) | all four (every episode) |
| **B22** | **Pulse start from recovery: plateau at cap − q, then a dip, then a jump.** On the first tick the supplier drops by exactly one order (362 → 287 at q 80; → 294 at q 68). It stays flat 15–23 ticks, drains 5–8 per tick for 6–11 ticks (to 259 / 203), then jumps back to about 340 within 2–5 ticks, **27–29 ticks after the switch**. Shipments are 0 for 4 ticks after a switch from empty-pipeline recovery (R4 t = 210–213). | **Not captured.** v1 drains to 75–77 (**−15 to −17σ**, about 40 ticks per pulse start) | O, Rc |
| **B23** | **Supply step 25–30 ticks after orders start** (it unifies B6 and B22). Something upstream roughly doubles about 25–30 ticks after orders begin: R1 t = 40 → 65, R5 0 → 33, R4 210 → 239 and 300 → 327. The step is abrupt (1–2 ticks), which points to a fixed pipeline delay (the second-class intake or treatment path) rather than a smooth adaptive lag. | Partly. v1's 21-tick slow path gives a step at the wrong time and size | O, Rc |
| **B24** | **Release after a pulse: burst about 20 ticks later.** After u.7 (t = 150): 26–28 for 16 ticks, then a **burst of 53–61 for 7 ticks** (t + 17…23), 15–21 for 8, 12–14 for 19, then a 0.5 tail. After u1 (t = 270): 44–47 (5 ticks), 36–40 (5), 25–29 (14), then a **burst of 52–59** (t + 24…29). Total shipped: recovery 60 1,226 (v1 1,257, so the total is right and the shape wrong); recovery 30 1,111 (v1 875). The supplier returns to the cap within 1 tick (captured). | **Not captured** (G4). −25σ in the bursts, +15σ between them | Rc |
| **B25** | **Retail sales track arrivals and stock** (implied sales = shipments − ΔR, `sales.py`). At similar R ≈ 360–400, sales are 30.5 when shipments are 34.5 and **23.8 when shipments are 24.6** (R5). They fall about 0.7 × Δshipments within about 17 ticks of a receiving cut. When arrivals stop, sales do *not* drop to 0: 16.9 at shipments 2.8 (R1 205–240) and 29.9 at shipments 14 (R4 175–200). Linear fit: sales ≈ 13.8 + 0.27·ship + 0.013·R, rms 3.0 (≈ 230 retail units of equilibrium error ≈ 6.6σ). | **Not captured.** With observed shipments fed in, the v1 law scores retail 0.39 (R4) and 0.42 (R5). An EMA-of-shipments term lifts that to 0.44 and 0.52, but R1 drops 0.03 | S (long-run level) |
| **B26** | **Retail never settles, and it overshoots.** No new segment settles (drift −1.8 to +5 per tick at the end of 100–150-tick holds). In u.85 retail climbs 345 → 498 (t = 324) while sales ramp from 22.7 to 30, then falls at −1.8 per tick at R ≈ 400 with shipments 28. At R5's end retail is still rising at +0.75 per tick at R ≈ 400 with shipments 24.6. So the retail equilibrium is not monotone in shipments across settings (mix 0.755 vs 0.5?), or sales lag by tens of ticks. | **Not captured.** −6 to −13σ throughout (partly inherited) | S |
| **B27** | **Cycle only in the U-limited regime** (confirms B7). Segments limited by receiving are flat (R5 r 0.7 and 0.5, u.85, u1). U-limited ones cycle: R5 r 1.0 38.7/30.8, u.7 a period-4 pattern of 36.4 ×3 / 32 that turns irregular at 32–39. The supplier shows ±8–12 swings during the post-pulse plateau (R4 240–270). | Mean only. That is fine for scoring | — |
| **B28** | **Supplier plateau under orders.** About 342 when receiving limits the flow (r 0.5 / 0.52 / 0.7), 330–333 when U limits it (u.7, R1 D). | Captured (≤ 0.6σ) | S |
| **B29** | **Noise** (`settle`): shipments 0.08–0.26, supplier 0.7–1.4, retail 1.3–1.4. Tiny compared with the score σ, so every visible error is structural. | — | — |

**Battery items, briefly:**

- **Settled?** Shipments settled in R5 r 0.7, r 0.5 and r 0.5 + maintenance 0.3, and in R4 u.85 (49 ticks) and u.7 (drift 3.6σ, cycle). The supplier settled in R5's last two segments. **Retail settled nowhere.**
- **Delays:** receiving takes 1 tick; a pulse start from an empty pipeline takes 4 ticks; the supply step takes 25–30; the release burst takes 17–29.
- **On/off asymmetry:** strong. Switching on takes shipments to the new level within 5 ticks. Switching off drains for 50+ ticks with a burst. In linear units, the u1 → recovery release sends 27% more goods than the v1 drain; in log units the tail (0.5 → 0) dominates. Log is useless here because of the hard zeros.
- **Overshoot:** yes in retail (u.85) and in the release bursts. There is no ringing beyond the cycle.
- **Return to baseline:** the supplier returns to the cap within 1 tick. Retail drains at 15 per tick (R4 190–210). Shipments reach a 0.5 tail by t + 50.
- **Relationships:** the supplier plateau falls as U-limited shipments rise (B28). Retail is the integral of shipments − sales (B25).

## 4. Score-loss ranking

Loss = Σ over ticks of [1 − 1/(1 + |err|/σ)] (tick-equivalents lost). Total **1,177 of 1,800**: retail 503, shipments 472, supplier 202. The first 20 ticks of each segment carry 31% of the loss.

| # | Run | Segment | Observable | Loss | Mean bias (σ) | Type | Already in old data? |
|---:|---|---|---|---:|---:|---|---|
| 1 | R4 | u.7 50–149 | retail | 92.8 | −12.9 | **level** (inherited + sales law) | retail was in-sample-fit (R1 D 549 vs 632) |
| 2 | R4 | u.7 50–149 | shipments | 89.9 | −9.3 | **level** (B18/B20) | yes, smaller: D 31.8 vs 34.8 (−2.7σ) |
| 3 | R4 | u.85 | shipments | 85.4 | −5.9 | **level** (B20) | no (interior never held) |
| 4 | R4 | u.85 | retail | 84.7 | −6.0 | **level** | — |
| 5 | R4 | u.7 50–149 | supplier | 54.8 | +7.8 | **dynamics** (refill 24 ticks early, B21) | yes (B3, "+15σ at tick 60" in the review) |
| 6 | R4 | recovery 60 | retail | 49.6 | −6.6 | level (inherited) | — |
| 7 | R4 | u1 | retail | 47.6 | −4.0 | level (inherited) | — |
| 8 | R5 | r 0.7 | shipments | 46.0 | −11.5 | **level** (B18 kink) | no (r between 0.35 and 1.5 never held) |
| 9 | R4 | u.85 | supplier | 45.5 | −4.0 | **dynamics** (B22 drain to 77) | not seen before |
| 10 | R4 | recovery 60 | shipments | 45.4 | +0.5 (mae 7.1) | **transient** (B24 burst) | yes (G4, R1 B8/B13) |
| 11 | R5 | r 0.5 | retail | 45.1 | −9.2 | level | — |
| 12 | R5 | r 0.5 + m 0.3 | retail | 45.0 | −8.9 | level | — |
| 13 | R5 | r 0.7 | retail | 44.9 | −9.0 | level | — |
| 14 | R5 | r 0.5 | shipments | 42.6 | −5.8 | **level** (B18) | no |
| 15 | R4 | u1 | supplier | 41.9 | −8.2 | **dynamics** (B22) | R1 all-pulse similar |
| 16 | R4 | u.7 0–49 | shipments | 40.9 | −7.2 | transient/level (B21 supply phase) | no |
| 17 | R5 | r 0.7 | supplier | 31.6 | +12.1 | dynamics (refill early) | yes |
| 18 | R4 | recovery 30 | shipments | 22.6 | −7.0 | transient (B24) | yes |

Full list: `fits/supply_chain/round2/segment_loss.json`.

**By type (approximate):**
- **Level: about 70%.** The shipments level is set by B18/B20. Retail is set by the shipment deficit plus the sales law.
- **Dynamics: about 17%.** This is the supplier drawdown and refill timing (B21, B22, B23).
- **Transient: about 13%.** This is the release bursts and the reset spikes (B24, B21).

**Old data.** v1 scores R1 0.513, R2 0.491 and R3 0.660. The same errors were present there, but small: D −2.7σ, r 0.35 −1.9σ, maintenance 0 settled +2.5σ. There was also the known rush error: 34.2 vs 22.5 (+10σ), unchanged. The old runs held receiving only at 0.35 and 1.5, which sit on either side of the kink, so a power law could fit both endpoints and still miss the whole mid-range. This is exactly the interior-coverage blind spot of §1.3.

## 5. Explanations and minimal model changes, in priority order

**1. Service structure: min(receiving capacity, upstream limit)** (B18, B19, B20, B27; loss rows 2, 3, 8, 14, and most of the inherited retail rows).
- *Explanation:* plain dynamics. The final terminal serves at most kr·r per tick. Upstream (dispatch, transport, drive service) delivers at most U. The brief's "primary intake, receiving and maintenance share drive service" puts maintenance and effort in U, not in kr. The period-2 cycle belongs to the U-limited regime, which fits a shared resource alternating between users.
- *Minimal change:* replace `mu0·(r/1.5)^ar·(1 + wm(1 − m))·…` with `served = min(kr·r·(1 + x·pulse-term), U)`. Here U = U0·(1 + wm(1 − m))·mix-factor·rush-factor, with U0 ≈ 34.8/(1 − φ) and kr ≈ 49.2/(1 − φ).
  - The joint-pulse +10% on kr needs one bounded term. Until the reserve says which control drives it, the safest choice is a term on the pulse-side distance of maintenance, rush and mix, bounded to [0, 0.15].
  - Use a smooth min, e.g. a soft-min with small width, so least_squares can move through the kink.
- *Conflicts:* none known. It also fixes the old D bias (G5: 31.7 → 34.8) and keeps r 0.35 = 17.2. The B15 maintenance-0 decay (43.8 → 37.2) then belongs to U. That suits an m2 heat state on U, which fits the reviewer's "threshold heat" idea and is no longer confounded with receiving.

**2. Retail sales law** (B25, B26; loss rows 1, 4, 6, 7, 11–13; about 43% of all loss).
- *Explanations, simplest first:*
  - (a) Sales depend on recent arrivals: an EMA of shipments with τ ≈ 7–15, plus a weak stock term. This is plain dynamics.
  - (b) Two goods classes with class-specific demand. The brief says "two classes", mix changes the class shares, and a class sells out independently. This would explain why the equilibrium is not monotone between u.85 (mix 0.755) and R5 (mix 0.5).
  - (c) Unknown.
- *Minimal change:* sales = min(R + ship, D0 + g·EMA(ship; a) + kR·R + dz·z), with g ∈ [0, 1] and a ∈ [0.05, 0.3] (bounded, so it cannot act as a clock). With observed shipments this raises R4/R5 retail from 0.39/0.42 to 0.44–0.47/0.52 and costs R1 0.03 (`retail_law.py`).
- *Conflicts:* R1 205–240 (sales 17 with no arrivals) resists a pure arrival-driven law. So add the EMA *on top of* the kR·R term, not instead of it. Test (b) with a two-compartment retail stock split by delayed mix before adding anything bigger.
- **The long-run retail level is the largest single risk for 4,000-tick episodes.** No hold in any run has settled retail except R1 D (975) and R2 maintenance 0 (1,180).

**3. Order-driven supply and the 25–30-tick supply step** (B21, B22, B23; loss rows 5, 9, 15, 16, 17).
- *Explanations:*
  - (a) A fixed second-path delay of about 25–30 ticks. The second class or treatment path comes online after its pipeline fills ("the second class normally follows its own intake"; buffers start empty). The abrupt 1–2-tick steps favour this.
  - (b) M3 adaptive production commitments, a smooth ramp. This fits the steps less well, but B4 (the slower second drawdown) still needs a memory.
- *Minimal change:*
  - On the first tick of orders, withdraw one order q from S.
  - Then let production track dispatch: make-to-order, production ≥ min(q, cap_e), with no drain while supply matches.
  - Move the slow path to a delay of about 27 ticks (currently DT2 = 21), with its rate as a free, bounded parameter.
  - Also make the supply-limited level depend on effort and mix (25.9 at e 1 / mix 0.5, 33.4 at e 1.35 / mix 0.71).
- *Conflicts:* B14 (idle pause: effort 0 stops dispatch). A make-to-order production path gated by effort is consistent with it. B4 needs checking after the change.

**4. Release burst** (B24; rows 10 and 18; about 6%).
- *Explanation:* goods on the slow path arrive at the terminal after dispatch has stopped. With r back at 1.5 (capacity 74) and no dispatch load on shared drive service, the terminal serves at a higher U ≈ 55.
- *Minimal change:* an idle-U, i.e. U × (1 + wid) when q = 0, which reuses v1's `wid`. v1 fitted `wid` = 0 only because the power-law service could not express it.
- *Conflicts:* none. It becomes identifiable once change 1 is in.

**5. Carried over, not tested by round 2:**
- the rush level (R1: v1 34.2 vs 22.5, +10σ);
- B15 (the step to 37.2 after 88 ticks without maintenance);
- B4 (the second drawdown).

These become fittable only after change 1. Framework lesson: if the new U or kr terms pin at a bound, that signals missing structure. Do not paper over it with a slow state.

## 6. Reserve-step proposal (100 steps; not spent)

**Open question.** Which pulse control lifts receiving capacity by about 10% in the joint pulse (B20)? The candidates are maintenance < 0.3, rush, mix and effort. It matters for every recovery-spacing and composition episode (pulse at 70–100% per control, where r is 0.35–0.7 and so receiving-limited). With the wrong attribution, single-control pulses are off by about 2–3σ on every tick.

Receiving-limited holds respond within 1–5 ticks and are flat (R5), so short single-factor holds suffice.

**R6: fresh reset.** The background is orders 80, receiving 0.5, and every other control at recovery. Each change is gray-code: one control moves from the background.

| Ticks | Change from the background | Steps | Reads |
|---|---|---:|---|
| 0–24 | maintenance 0 | 25 | 24.6 → no effect; ≈ 27 → maintenance < 0.3 lifts kr (threshold between 0.3 and 0) |
| 25–54 | maintenance 1, lead_time_buy 0.2 (rush) | 30 | rush alone at r 0.5. The level after about 10 ticks gives the rush effect on kr. The transient gives the rush dynamics in the receiving-limited regime (R1 had it only in the U regime) |
| 55–84 | lead 1, mix 0.8 | 30 | mix alone (19-tick delay, so read ticks 75–84) |
| 85–99 | mix 0.5, production_effort 1.5 | 15 | effort alone (expect instant) |

**Total: 100 steps** (`--confirm 100`). The retail trace comes for free, as a further sales-law check at shipments ≈ 25.

**Decision table:**

| Outcome | Model change |
|---|---|
| One segment gives ≈ 26.5–27.5 and the others 24.6 | Attribute the 10% to that control alone (one bounded gain) |
| None rises | The lift is an interaction (e.g. maintenance 0 × rush). Fit kr on the u-ray directly: kr(u) = 49.2·(1 + c·u), bounded |
| Two rise | Use additive gains, checked against u.85 and u1 (53.6 and 54.6) |

**Why not retail?** Retail is the biggest loss, but it needs holds of 300+ ticks to settle (τ of hundreds of ticks), which 100 steps can't buy. It has to be fixed from existing data (R1–R5 hold about 20 usable sales windows).
