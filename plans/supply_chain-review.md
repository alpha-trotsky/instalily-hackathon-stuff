# Supply chain review (Phase B)

Reviewer: Phase B, resumed after an API cut-off. **No simulator steps were spent** (1,250 of CAP 1,300 used; 50
reserve left). Scripts, fits and plots are in `toronto26-participant-kit/fits/supply_chain/review/`:

- `sc_rv.py`: a reviewer variant of `greybox/supply_chain_model.py` with three base fixes. **F1**: dispatch is
  gated by production effort (`dcap·min(e/ed, 1)`). **F2**: two terminal classes split by mix, with a 21-tick
  class-2 path and separate server and space shares (`s2`). **F3**: sales rise with retail stock (`kR·R`).
- `chain_rv.sh`: chained fits on R1 and R2 together (2 restarts × 4 passes, perturbation 0.02–0.03).
- `v0_base_all.json` is the v0 base refitted on both runs. `rv_base_all.json` and `rv_m12/m13/m23_all.json` are
  the variant base and the three pairs, all refitted on both runs.
- `rvplot.py` → `rv_cmp_all.png`: observed data with the five fits and their errors in score-σ units, for R1 and R2.
- `stab4000.py`: 4,000-tick held-action extrapolation of the variant fits.

Score σ (0.1 × std over R1 and R2) is 1.21 for shipments, 10.6 for supplier stock and 37.0 for retail stock.

## 1. Independent behaviour list

This list was written from the raw traces (black lines in `rv_cmp_all.png` and the run battery plots) before the
plan's catalogue was compared. The resume left little time, so this pass is shorter than usual.

- **R1 Hard limits.** Supplier stock is capped at about 362 and floored at 0. Retail is floored at 0. Shipments
  are exactly 0 without orders once the pipeline is empty.
- **R2 Reset transient.** Shipments are 0 from tick 0, whatever the reading. The supplier refills at about
  12 per tick after a 2-tick delay. Retail drains at about 28 per tick to 0.
- **R3 Order-on drawdown and refill.** When orders start, the supplier drains to 0, then refills to a plateau
  about 33 below the cap. The drain and refill slopes depend on production effort: with effort 1.5 the supplier
  never empties and refills at about 36 per tick. A second order pulse drains more slowly (R1 tick 240).
- **R4 Two shipment levels in each order period.** Shipments sit near 25 for about 20 ticks, then reach the
  service level of about 35. The service level includes a period-2 oscillation (38.7/30.8) whose amplitude is
  several σ.
- **R5 Post-order release.** When orders stop, shipments run at the service level for about 20 ticks, burst to
  about 50 for 6 to 12 ticks, then fall in 10-tick steps with a ratio of about 0.21 (R1 ticks 200–240 and
  680–750).
- **R6 Rush.** Rush produces a dip, then a burst to about 50, then a sustained 22.5. After rush is released,
  shipments sag and the supplier drains from 340 to 200. This after-effect lasts more than 30 ticks (R1 ticks
  410–520).
- **R7 Controls that set the service rate.** Receiving 0.35 gives 17.2 at once. Maintenance 0 gives 43.8
  after 4 ticks. Mix 0.8 gives about 28 after about 19 ticks.
- **R8 Long no-maintenance hold.** Shipments hold at 43.8, then oscillate around 41, then step down to a steady
  37.2 about 88 ticks after maintenance stops (R2 ticks 130–330). Either pause, maintenance or idle, restores the
  higher level for 22–26 ticks.
- **R9 Idle pause (effort 0 with orders on).** The supplier refills to the cap within 3 ticks, so dispatch stops.
  After the restart, shipments are 0 for 3 ticks and the supplier drains to about 100 (R2 ticks 390–470).
- **R10 Retail levels off.** Retail flattens at about 975 when shipments are 34.7, and at about 1,180 when
  shipments are 37.2. Sales therefore rise with stock until they match arrivals.
- **R11 Noise is tiny compared with the structured errors.** Shipments have σ ≈ 0.1, supplier stock ≈ 1.35 and
  retail ≈ 2. Every visible error comes from structure.

These match catalogue v2 (B1–B17) one for one: R1=B1, R2=B2, R3=B3/B4/B5, R4=B6/B7, R5=B8/B13, R6=B9, R7=B6/B10/B11,
R8=B15, R9=B14, R10=B16. I found no behaviour that the researcher missed. The catalogue is thorough, and my
additions below are about the models, not the data.

## 2. Did the fixed base help? Pairs judged against it

All fits below were refitted on R1 and R2 together. The table shows train scores at the score σ.

| Fit | Cost | R1 ship / sup / ret | R2 ship / sup / ret | Mean |
|---|---:|---|---|---:|
| v0 base (plan model) | 13,471 | 0.420 / 0.629 / 0.448 | 0.346 / 0.478 / 0.568 | **0.482** |
| variant base (F1–F3) | 11,490 | 0.330 / 0.634 / 0.474 | 0.393 / 0.537 / 0.534 | **0.483** |
| variant + m1+m2 | 11,201 | 0.323 / 0.636 / 0.483 | 0.377 / 0.561 / 0.509 | 0.481 |
| variant + m1+m3 | 11,343 | 0.315 / 0.631 / 0.491 | 0.343 / 0.548 / 0.528 | 0.476 |
| variant + m2+m3 | 11,411 | 0.307 / 0.625 / 0.488 | 0.349 / 0.529 / 0.531 | 0.471 |

- **F1–F3 lower the cost by 15% but leave the score unchanged.** R2 improves: shipments +0.05, supplier +0.06,
  and the supplier no longer collapses to 0 in the idle pause (R9). R1 shipments get worse by 0.09. The variant
  predicts 20–25 shipments in the R1 release tail (ticks 700–750), where the data show about 0, because the
  refit makes the backlog capacity `Bmax` about 2,500, far larger than before. That is +20σ over 50 ticks.
- **No pair beats the fixed base on score.** The differences are 0.002–0.012, and the cost gains (2.5%, 1.3%,
  0.7%) come entirely from **pinned parameters that act as clocks counting time since reset**, not as mechanisms:
  - m1+m2: `a1` = 4e-4 with `g1` = 1 (pinned), and `a2` = 1e-4 with `g2s` ≈ 1 and `g2p` = 1 (pinned). Both
    states become slow linear ramps from reset. `g1r` = −0.25 (rework falls as congestion rises), which is
    physically backwards.
  - m1+m3: m3 is effectively off (`a3u` = 9e-27, `g3` = 3.8e6, `a3d` = 1). m1 is again a slow ramp with `g1` = 1.
  - m2+m3: m2 is off (`a2` = 5e-16). m3 has `a3u` = 3e-6 and `a3d` = 1, so it is effectively off too.
- **Verdict: the pair question cannot be settled with this base.** None of the mechanism modules, as written,
  captures R8 (the step to 37.2 about 88 ticks into the no-maintenance hold, undone by either pause) or R3/B4
  (the slower second drawdown). The optimiser instead uses them to absorb drift. The plan's leaning of M3 plus
  either M1 or M2-heat still rests only on B4 and B15 read by eye. For submission, use the **variant base with
  no mechanism modules** until the gaps below are fixed.

## 3. Comparison table (behaviour → captured by the best fit?)

"Best fit" is the variant base, `rv_base_all`. The error figures come from `rv_cmp_all.png`.

| Behaviour | Component | Captured? | Evidence and error |
|---|---|---|---|
| B1 limits | Smax, min/max clipping | yes | supplier error ≈ 0 at the cap and floor |
| B2 reset transient | empty pipelines, DP = 2, dz·z | yes | < 2σ |
| B3 production vs effort under orders | e^pe·(p0 + po·Po) | partly | R2 ticks 30–130: +15σ supplier at tick 60 (the model drains too little, then too fast) |
| B4 second drawdown slower | m3 (intended) | **no** | R1 tick 240: −10σ supplier; m3 fits turn themselves off |
| B5 plateau = cap − shipments | dispatch after refill | yes | < 1σ |
| B6 25-then-35 shipment phase | F2 class-2 path, DT2 = 21 | partly | the step exists, but the level is 21 in the model vs 25–26 in the data (−4σ for about 20 ticks at each order start) |
| B7 period-2 oscillation | none (the mean is predicted) | mean only, and biased | model 32.3 vs data mean 34.8 at D: **−2σ at every D tick** |
| B8/B13 release burst and rework tail | rework loop φ = 0.18, LR = 10 | tail yes, burst **no** | R1 ticks 200 and 680–700: −15 to −25σ burst; +20σ tail at 700–750 (see §2) |
| B9 rush response | wl·(1 − lagged lead time) | **no** | `wl` = 3,250 with `al` = 8e-10, so rush has almost no effect. Errors of −20σ at 450 and +10σ supplier at 500–520 |
| B10/B11 maintenance and mix service levels | wm, wmix with lag amix | yes in-sample; **unsafe out of sample** | `amix` = 0.0015 with `wmix` = −5.4 is a near-integrator (§4, G2) |
| B12/B16 retail sales and equilibrium | D0 + Dg·Ss + kR·R | in-sample yes (±5σ); **long-run wrong** | at D the model's 4,000-tick retail settles at 572 vs about 975 in the data, and at 801 vs about 1,180 with maintenance 0 (≈ 11σ held for thousands of ticks) |
| B14 idle pause stops dispatch | F1 dispatch gate | partly | the supplier no longer goes to 0, but it rises only to about 250, not the cap. The 3 ticks of 0 shipments on restart are missed (+30σ spike, R2 tick 415) |
| B15 step down after 88 ticks without maintenance | m1, m2 (intended) | **no** | flat about 39 vs 43.8 → 41 → 37.2 (±4σ for about 90 ticks) |
| B17 orders 40 | dispatch ≤ q | yes (mean) | about ±6σ, the size of the oscillation |

## 4. Stability over 4,000 ticks (`stab4000.py`, actions held from reset)

The table shows the mean over the last 500 ticks as shipments / supplier / retail.

| Held action | Variant base | + m1+m2 | + m1+m3 | + m2+m3 | Data (settled) |
|---|---|---|---|---|---|
| D (orders 80) | 32.3 / 329 / 572 | **10.4 / 351 / 0** | 27.6 / 334 / 445 | 32.9 / 329 / 653 | 34.8 / 330 / ≈ 975 |
| D + mix 0.8 | **0.0 / 362 / 0** | **0.0** | **0.0** | **0.0** | ≈ 28 after 40 ticks |
| D + rush | 32.6 | 33.5 | 42.8 | 23.5 | 22.5 after 60 ticks |
| D + maintenance 0 | 38.0 / 324 / 801 | **10.7 / 351 / 0** | 33.6 | 38.9 | 37.2 / 324.5 / 1,180 |
| orders 20 | 20.0 / 342 / 76 | 20.0 / 342 / 197 | 20.0 / 342 / 133 | 20.0 / 342 / 132 | not measured |

## 5. Gaps

- **G1 (high): pair fits use mechanism states as time-since-reset ramps.** In m1+m2, forecasts at plain D
  collapse from 31 to 10 shipments and retail goes to 0 over 4,000 ticks. Evidence: §2 parameters and the §4
  table.
  - **Fix:** bound the rates, for example `a1, a2 ≥ 0.005` (time constant ≤ 200 ticks), `a3u, a3d ∈
    [0.005, 0.5]`, and `g1, g2s, g2p ≤ 0.5`. Refit only after G2–G5 are in.
  - **Test:** reject any fit whose 4,000-tick held-D run in `stab4000.py` differs from its tick-300 value by more
    than 2σ.
- **G2 (high): mix and rush lags are near-integrators with large gains.**
  - Mix: `amix` ≈ 0.0015 with `wmix` −5 to −8. With mix held at 0.8 or above, shipments reach **0** in every fit.
    The brief allows mix from 0 to 1, and below 0.5 the same term multiplies service by up to about 4.5.
  - Rush: `wl`·`al` flips sign between fits (+3,250 vs −1e5) and integrates rush time.
  - These controls were observed only at 0.5/0.8 and 1/0.2.
  - **Fix:** fix `amix` at about 1/19 (the 19-tick delay seen in B11) or use a pure 19-tick delay. Make the mix
    effect bounded and saturating, e.g. `1 + wmix·clip(mix − 0.5, −0.3, 0.3)` with |wmix| ≤ 1.5, fitted to the
    observed 34.8 → 27.8. Do the same for rush: a lag with `al` ≥ 0.02 and a bounded gain.
- **G3 (high): the long-run retail level is wrong.** At D the model gives about 572 vs about 975 in the data, and
  with maintenance 0 about 801 vs about 1,180. That error is held for thousands of ticks in every "sustained
  operation" scenario.
  - The settled points (ship 34.7 → R 975, ship 37.2 → R 1,180) need a sales law in which the retail
    equilibrium rises steeply with shipments. Examples: `sales = min(R + ship, c·R^α)` with α ≈ 0.4–0.5, or
    `D0 + kR·R` with `Dg` = 0. The reset drain of 28 per tick at R ≈ 100 constrains the same law.
  - **Fix:** try sales = min(R + ship, a·R^α + b·ship), and **weight the settled R2 ticks 218–329 and R1 ticks
    540–625** more heavily in the loss.
- **G4 (high): the release burst and tail regressed.** The variant predicts 20–25 shipments after release in the
  R1 tail (ticks 700–750), where the data show about 0 (+20σ), and misses the burst to about 50 (−15 to −25σ).
  Every "recovery history" episode ends in this regime.
  - **Likely cause:** `Bmax` ≈ 2,500 plus the slow class-2 path hold too much backlog. The burst suggests the
    terminal serves faster (about 50) when nothing is being dispatched, because dispatch shares the drive.
  - **Fix:** use a service rate μ_idle ≈ 50 when d = 0 (one extra parameter), and cap `Bmax` near the
    ≈ 1,650 in transit that the plan estimated at R1 tick 160.
- **G5 (medium): the D-level bias from the period-2 oscillation.** The model gives 32.3 vs a data mean of 34.8,
  which is −2σ on every D tick. The fit is pulled by the 25-level phase and the oscillation.
  - **Fix:** fit shipments against a 2-tick moving average of the observations (the score's best target is the
    mean anyway), or add an explicit D-level anchor residual.
- **G6 (medium): the 25-then-35 phase at each order start.** The model uses 21 for 21 ticks, the data show 25–26
  for about 20 ticks. Fix: free DT2 in the range 18–24 and let the class-2 share differ from the service share,
  or model the first phase as "class-1 service only" with its own rate.
- **G7 (medium): idle-pause restart (B14).** The model misses the 3 ticks of 0 shipments on restart (+30σ spike)
  and does not refill the supplier to the cap. If production 0 empties the primary line, dispatch should
  restart through the DP + DT pipeline. Fix: dispatch = 0 when e = 0 (a hard gate; `ed` → 0 acts as a
  threshold) and a 3-tick transit restart from empty.
- **G8 (medium): no mechanism module captures B15** (the step down about 88 ticks into the no-maintenance hold,
  undone by either pause). Suggested m2-heat form: H integrates `(e·u_drive − cool)` with an **accumulation
  threshold**, where service drops once H exceeds H*. That gives a delayed step rather than a smooth decline, and
  both pauses cool it. The m1 alternative is congestion that builds with queue occupancy and drains when dispatch
  stops. Refit both after G1–G4.
- **G9 (medium): no module captures B4** (the second order pulse drains half as fast 80 ticks later). The m3 fits
  turn themselves off. Make m3 act on the **order-period withdrawal rate** with a fade time of 50–200 ticks
  (bounded), not on q/80 with an unbounded rise rate.
- **G10 (low): coverage.** Not yet tested:
  - mix below 0.5 or at 1.0, lead_time_buy between 0.2 and 1 or at 0, receiving below 0.35 or at 0, and orders
    below the service rate (about 20);
  - P9b (rush before vs after dispatch), which was never run as a comparison;
  - long recovery after heavy load, which is short (≤ 80 ticks), but its levels are trivial (cap, 0, 0).

  §4.2 coverage otherwise holds: P0, P1 for every control, P2, P3, P5, P7, P9a, P9c and the all-controls pulse
  and release.
- **G11 (low): fitting.** Chained fits need about 10 minutes per model. Set `--max-nfev` ≤ 300 per pass and add
  the parameter bounds from G1/G2 to cut the bad-basin restarts (costs 13k–20k).

## 6. Reserve spending (50 steps)

**Recommended: yes, one probe of orders ≈ 20** (below the service rate). P9b is not recommended now.

- **Why orders ≈ 20:**
  - Order quantity is the dominant control. Scoring episodes will spend much of their time at intermediate
    orders, but the data contain only q = 0, 40 (25 ticks) and 80.
  - Below the service rate the system is in a regime the data have never seen: no terminal queue, shipments
    presumably ≈ q, and the supplier no longer on its plateau.
  - All four fits predict exactly 20.0 / 342, which is pure extrapolation.
  - The probe also constrains the make-to-order production term (`po`, and m3) at a second level, the retail
    sales law (G3) at a second shipment level, and the rework tail and burst from a small backlog (G4: does the
    burst about 50 appear without a queue?).
- **Why not P9b:** it adds only an arm for one control. It separates M1 only, and the pair fits are not
  identifiable until G1–G4 are fixed, so its evidence could not be used tonight.

**Exact schedule (50 steps, fresh reset):**

| Ticks | Steps | Action |
|---|---:|---|
| 0–39 | 40 | order_quantity **20**; lead_time_buy 1.0, product_mix 0.5, production_effort 1.0, receiving_effort 1.5, maintenance 1.0 (recovery) |
| 40–49 | 10 | full recovery (order_quantity 0), to see the release burst and rework tail from a small backlog |

Starting orders at tick 0 costs nothing extra and matches how scoring episodes begin. With the reset transient,
the supplier starts at about 90, so the probe also shows whether production at q = 20 keeps up with withdrawal
from a low stock.

The alternative, if the modeler prefers mechanism evidence to coverage, is P9b "before": reset, then 0–29 D with
rush (lead 0.2) switched on at tick 0 together with orders, and 30–49 D without rush. Compare this with R1
ticks 410–470, the "after" arm. Its value is lower for the reasons above.

## 7. Submission advice

Ship the **variant base only** after the G2 fix (bounded mix and rush terms) and ideally G3 (the retail
law). Unfixed, the variant base forecasts 0 shipments for any sustained mix ≥ 0.8. Do not ship any of the pair
fits in their current form (G1).
