# hospital_queue: round-2 diagnosis (R3 = HQ1, R4 = HQ2)

Diagnostician pass, 2026-09-28. **No steps spent** (free `--budget` read: 100 remaining). No model changed.

- Scripts and outputs are in `toronto26-participant-kit/fits/hospital_queue/round2/` (paths below are relative to that folder). All of them are run from the kit folder:
  - `diag.py`: plots, per-segment levels and loss (`diag.out`, `diag.json`);
  - `rules.py`: decision rules and the candidates (`rules.out`);
  - `battery2.py`: settling, release ramps, noise and the wait relation (`battery2.out`);
  - `lossrank.py`: loss ranking (`lossrank.out`, `lossrank.json`);
  - `zoom.py`;
  - `probe_fit.py`: a diagnostic parameter-only refit, not a candidate (`probe_fit*.out`).
- **Plots:**
  - [R3_v1.png](../toronto26-participant-kit/fits/hospital_queue/round2/R3_v1.png), [R4_v1.png](../toronto26-participant-kit/fits/hospital_queue/round2/R4_v1.png): the new runs with the v1 prediction overlaid.
  - [R1_v1.png](../toronto26-participant-kit/fits/hospital_queue/round2/R1_v1.png), [R2c_v1.png](../toronto26-participant-kit/fits/hospital_queue/round2/R2c_v1.png): the old runs.
  - [zoom_reset_tail.png](../toronto26-participant-kit/fits/hospital_queue/round2/zoom_reset_tail.png): R3's reset under electives, and the R1 and R4 recovery tails aligned at release.
- **σ** (0.1 × std after tick 20, all data, as in `heldout.py`): wait 3.14, queue 11.06, discharges 0.425.
- **v1 held-out scores** (reproduced): R3 0.362 / 0.362 / 0.156, R4 0.315 / 0.573 / 0.215 (wait / queue / discharges), mean 0.33.

## 1. Summary

1. **Discharges under load are 1.5–3× v1's everywhere.** R3: −16σ, −11σ, −8σ. R4: −5σ to −6σ. The old E/L windows were −8σ to −12σ. The model routes elective load through a heavy work-per-patient penalty (`we·phi`, wpp up to ≈ 2.8). It then fits the queue by making leaving 2.5× too fast: θ is 3.2 %/tick, and the data give 1.1–1.4 %/tick in every drain. Discharges are 41 % of the lost score.
2. **Electives from reset are a separate long-stay track, not an instant flood (H1 partly holds).** At electives 5 the queue sits at about 100 for 30 ticks while nobody waits (wait 3–4). Discharges are 15.9 = 11.5 + 4.4, so all electives are served. About 77 electives are in service, which gives a length of stay (LOS) of about 17 ticks. Capacity then erodes, and a flood starts after about 40 ticks. v1 floods at once: queue +9σ, discharges −16σ.
3. **Capacity is linear in staffing (H2 rejected).** Staffing 15 holds the queue at 313 (drain 0.10/tick) with discharges 7.5, about 0.5 per staff. The level is set by leaving, not by the ceiling.
4. **H3 is inconclusive by its own rule.** The tail is not exponential: it drains linearly at about 2/tick, then plateaus at about 120 → 100 after about 105 ticks, the same in R1 and R4. v1 hits R4's +150 level (108 vs 106) only by coincidence. On R1 it falls through to 67 vs 99.
5. **New and largest single surprise (B31).** In R4's recovery tail, `wait_time` jumps from 20 to 169 (still rising) at tick 306 while the queue and discharges are identical to R1's tail, where wait decayed to 5.5. v1 is −50σ at the end. The trigger is unknown, and the reserve should resolve it (§6).

## 2. Decision-rule verdicts

Cells are the mean of the last 10 ticks of each segment: wait, queue, discharges. The σ-error is (candidate − data)/σ.

| Run / segment | Data | final_m12 (v1) | σ-err v1 | v5_base | σ-err v5 |
|---|---|---|---|---|---|
| R3 0–49 electives 5 | 6.5, **143**, **13.2** | 18.8, 305, 5.9 | +3.9, **+14.7**, **−17.2** | 16.9, 277, 9.1 | +3.3, +12.1, −9.6 |
| R3 50–99 electives 10 | 32.9, 272, 9.5 | 32.0, 309, 5.1 | −0.3, +3.4, −10.4 | 32.9, 292, 8.8 | 0.0, +1.9, −1.7 |
| R3 100–149 staffing 15 + electives 10 | 50.3, 317, 7.1 | 44.1, 311, 3.8 | −2.0, −0.5, −7.8 | 49.1, 301, 6.6 | −0.4, −1.5, −1.4 |
| R3 150–199 staffing 15 alone | 50.9, **313**, 7.6 | 36.0, 289, 6.3 | −4.8, −2.2, −3.1 | 44.8, 290, 6.8 | −1.9, −2.1, −1.8 |
| R3 200–249 recovery | 33.2, 213, 11.4 | 17.7, 197, 10.2 | −5.0, −1.5, −2.6 | 25.8, 221, 10.1 | −2.4, +0.7, −3.0 |
| R4 0–89 joint .7 | 68.3, 322, **4.65** | 52.9, 310, 2.57 | −4.9, −1.1, −4.9 | 46.1, 299, 6.90 | −7.1, −2.1, +5.3 |
| R4 90–139 recovery 50 | 41.6, 257, 11.2 | 32.1, 260, 8.4 | −3.0, +0.2, −6.4 | 31.7, 244, 9.7 | −3.2, −1.2, −3.5 |
| R4 140–199 joint 1 | 101.3, 327, 2.11 | 110.9, 312, 1.02 | +3.0, −1.3, −2.5 | 93.8, 300, 3.25 | −2.4, −2.4, +2.7 |
| R4 200–274 recovery +75 | 33.1, 215, 12.1 | 28.2, 224, 9.5 | −1.6, +0.8, −6.2 | 27.8, 210, 10.2 | −1.7, −0.5, −4.4 |
| R4 275–349 recovery +150 | **163.2**, 106, 12.6 | 5.1, 108, 13.2 | **−50.3**, +0.2, +1.5 | 8.6, 95, 12.4 | −49.2, −1.1, −0.4 |

| Rule | Measured | Verdict |
|---|---|---|
| **H1:** queue at electives 5 < 80 and discharges up by about the elective rate → separate elective service. Flood to 250+ → shared queue right. | Ticks 3–30: queue 102, discharges **15.9** (+4.4 = the elective rate), wait 3.4, so nobody waits. Ticks 30–50: discharges 13.7 and the queue rises 2.2–2.4/tick to 143, unsettled. At electives 10 the queue reaches 272 and is still rising 0.9/tick. | **Neither branch cleanly, closer to H1.** Electives have their own long-stay service: about 77 in service, LOS ≈ 17 ticks. That track saturates after about 30–40 ticks, and then the shared queue floods. Implement per-class elective service (§5.1), with a finite elective pool that overflows into the shared queue. Both candidates are wrong: +12σ to +15σ on queue at electives 5. |
| **H2:** staffing 15 alone drains ≥ 1/tick → capacity at 15 exceeds arrivals → concave capacity. | Drain **0.10/tick** (316 → 312), discharges 7.5. Per-staff capacity is 0.53 at staffing 5 (R1), 0.50 at 15 and 0.57 at 20. | **H2 rejected.** Keep capacity ∝ staffing (linear). Staffing 15 does overflow the hospital, as the model predicted, but the level is 313, not 289: leaving is slower (B24). |
| **H3:** exponential fit to the queue over recovery +150. Asymptote ≤ 40 → replace the pool; ≈ 100 → keep. | Not exponential. The fit gives an asymptote of −603 from +0, 54 from +50 and 99 (τ 26) from +100. Linear drain of 2.0–2.3/tick down to about 150, then a regime switch at +106: discharges flat at 11.1 (below the 11.49 arrivals), queue 120 → 101 at 0.46/tick plus quanta. R1's tail is identical: plateau 99 at +170, draining 0.1–0.2/tick. | **Formally inconclusive; in substance "≈ 100, not permanent".** A pool of about 75–100 above baseline exists 150 ticks after a joint pulse, and it drains slowly (τ ≈ 200–400). v1's Lq is only 5.7 here; v1 reaches 108 through the W backlog and θ and would fall to 67 by +170 (R1: −2.1σ). Replace the Lq form, and settle its lifetime with the reserve (§6). |
| Plan note: "fatigue after a pulse" (R4 joint 1 after joint .7 + 50 recovery, vs R1's pulse after E) | Joint 1: discharges 2.11, queue 327, wait 101 (+0.65/tick). R1 pulse: 1.88, 327, 107. No drift over 90 ticks of overtime .7 (discharge slope −0.008/tick). | No visible history or fatigue effect on the pulse level. See B26 for the one place fatigue may show. |

## 3. Behaviour catalogue (new runs; continues B1–B20)

Status is against v1 (`final_m12`). "|e|" is the mean absolute error over the segment in σ. Scoring categories: S = sustained, O = order, R = recovery, C = composition.

| ID | Behaviour | Evidence | v1 status | Categories |
|---|---|---|---|---|
| **B21** | **Reset under electives: a separate long-stay track.** At electives 5 the queue goes 66 → 99 in 2 ticks and holds about 100 for 30 ticks. Wait stays 3–4, so nobody waits. Discharges average 15.9 = 11.49 + 4.4. That puts the elective arrival rate at ≈ 0.88 per unit of `elective_scheduling`, or ≈ 17.6 at 20; v1 has Ae = 23.5. About 77 extra patients are in service, so elective LOS ≈ 77/4.4 ≈ 17 ticks (routine ≈ 2). | `zoom_reset_tail.png` (left); R3 ticks 3–30 | **Not captured.** Queue +9σ mean (+14.7σ at the end), discharges −16σ, wait +1.8σ | S, C (every episode with electives from reset) |
| **B22** | **Delayed flood at small elective load.** After about 30–40 ticks at electives 5, discharges fall 15.9 → 13.4 and the queue climbs 2.2–2.4/tick, unsettled at tick 50 (settle: drift 27σ). Wait starts rising at tick 42. At electives 10 the queue reaches 272 (+0.9/tick) and discharges 9.5. So the elective track saturates, and then the shared queue floods. | R3 30–100 | **Not captured** (v1 floods from tick 0): queue +5.5σ over electives 10 | S, C |
| **B23** | **Capacity ∝ staffing; staffing 15 does not clear arrivals.** Discharges are 7.5 at staffing 15 with no electives (R3 150–200), 11.35 at 20 during a drain, and 2.67 at 5 (R1). The staff cut acts at once (R3 tick 100: 9.5 → 6.1). The queue equilibrium at staffing 15 (313) satisfies arrivals − discharges = leaving: 11.49 − 7.49 = 4.1 ≈ 1.4 % of (queue − 23). | R3 100–200, `rules.out` | Direction captured. Level not: queue −2.2σ, discharges −3.1σ, wait −4.8σ | S, C |
| **B24** | **Leaving rate ≈ 1.1–1.4 %/tick of (queue − 23) in every drain.** Values: R3 200–250 1.2 %, R4 110–140 1.3 %, R4 220–275 1.2 %, R4 250–305 1.1 %, R1 620–700 1.1 %, R3 staffing 15 1.4 %. From conservation: leaving = 11.49 − discharges − dq/dt. Above that, overflow at the ceiling takes the excess (joint .7: 19/tick; joint 1: 27/tick). | `rules.py` conservation table (§5.1) | **Not captured (compensation).** v1 has θ = 3.16 %/tick on W and discharges 2–3 too low, so the queue slope matches for the wrong reason. | all |
| **B25** | **Discharges under load are 1.5–3× v1's.** Joint .7: 4.65 vs 2.57. Joint 1: 2.11 vs 1.02. Staffing 15 + electives 10: 7.1 vs 3.8. Electives 10: 9.5 vs 5.1. The old data show the same (E −10σ to −12σ, L −8σ). The cause is v1's `we·phi` work penalty (we = 2.0, and phi decays with τ ≈ 14). | `diag.out`; lossrank | **Not captured**: level error, −5σ to −16σ | S, C, R |
| **B26** | **The release ramp (M2) is reproducible and fast; its start depends on history.** 5-tick mean discharges after a Δstaff = 15 release: R1 580 gives 4.8, 6.2, 8.5, 8.0, 9.7 …; R4 200 gives 4.7, 6.6, 8.7, 8.5, 9.8 …; both reach about 11 by +45–50. A pure staffing cut (R1 175) starts higher: 8.0, 8.2, 9.7. Δstaff = 5 (R3 200): 9.4, 10.3, 11.1, so full within about 10 ticks. Δstaff = 10.5 (R4 90): 5.2, 8.0, 8.3, 9.1. The lower start after overtime pulses is the only candidate fatigue (M1) signature; the alternative is pipeline refill after diagnostic .75. | `battery2.out` | **Not captured (dynamics).** v1 ramps far too slowly (R4 90–140 end −6.4σ, 200–275 −6.2σ) because the handover, fatigue and slow phi-decay penalties stack. | R, O |
| **B27** | **No fatigue drift or pulse-history effect on levels.** 90 ticks at overtime .7 (R4 0–90): discharge slope −0.008/tick. Joint 1 after joint .7 matches R1's pulse after E (2.11 vs 1.88; queue 327 vs 327). | R4 | Consistent with v1's small, bounded m1 | O, R |
| **B28** | **Ceiling depends on configuration: 313–327 in the new runs.** Joint .7 322, joint 1 327, staffing 15 + electives 10 317, staffing 15 313. From reset under joint .7 the queue climbs 25/tick and reaches the ceiling at tick 13 (settled by 20). | R4 0–20 | Mostly captured: v1 310–312, −1σ to −1.3σ. Ramp captured. | S |
| **B29** | **The reset dead time depends on the controls.** Discharges are 0 for 2 ticks at staffing 20 (R3, as in B1/B20) but **5 ticks** under joint .7 (staffing 9.5, diagnostic .645), then a burst of 27.7. | R4 ticks 0–5 | Not captured: v1 starts discharges at 5.6 at tick 0. Transient, small. | all (reset) |
| **B30** | **wait_time is a realized (FIFO) wait, not a current Little's estimate.** The ratio wait / ((queue − 23)/discharges) is 0.4–0.9 while filling, 1.0–1.35 at steady load, and **1.9–2.3 in every drain** (R1, R2c, R3, R4). Patients admitted now joined when the queue was larger. In R3 the level correlation queue → wait peaks at lag 15 (0.985). | `battery2.out` | **Partly captured.** v1's slow EMA (kw 0.035) lags, but the level is too low in drains (R3 recovery −5σ, R4 recovery 50 −3.9σ) and under joint .7 (−4.9σ at the end) | R, S |
| **B31** | **Wait blow-up in the recovery tail (R4), absent in R1.** At tick 306 (+106 after release, queue about 140 → 120, a 24.7 discharge burst), discharges switch to a smooth 11.1 ± 0.07 and wait jumps 20 → 60 in 4 ticks, 118 by 320 and 169 by 349 (still +1.2/tick). The ratio in B30 reaches 11–17. R1's tail has the **same queue and discharge path** (aligned plot), yet its wait decays 17 → 5.5. The approach looks like an EMA (k ≈ 0.1) toward an age of about 150–180, which is the age of patients who arrived during the pulse (ticks 140–200). | `zoom_reset_tail.png` (right) | **Not captured**: −50σ at the end, 63 tick-units lost in 75 ticks | R (possibly large in scoring) |
| **B32** | **Post-pulse residual plateau of about 100–120, draining slowly in quanta.** Reached about +105–125 ticks after the release in both R1 and R4. Drain is 0.46/tick in R4 (quanta at 340, 342, 347: −5, −8, −4 with discharge bursts of 14.7, 18.4, 14.9) and 0.1–0.2/tick in R1. The discharge level in this regime is 11.1, below the 11.49 arrivals. | R1 700–750, R4 306–350 | **Not captured.** v1 drains straight through (R1 end: 67 vs 99, −2.1σ; its tail discharges are too high, 13.4 vs 11.1, +5.6σ). The R4 +150 match is a coincidence. | R |
| **B33** | **Noise is unchanged.** Under load: queue σ 1–2.7, discharge bursts σ 0.7–2.8 (quanta 0–25), wait 0.2–1.1. Smooth regime: discharges σ 0.07. Discharge noise is 2–7× the score σ, so a smooth mean is the target (B14). | `battery2.out` | n/a | – |

**Battery items.**

- **Delays:**
  - electives on → queue responds the next tick (R3 50: +9.5/tick);
  - staffing cut → immediate;
  - staffing restore → ramp (B26);
  - no dead time on overtime or diagnostic changes in these runs.
- **On/off asymmetry:**
  - Queue fill is +25/tick (13 ticks). The drain is linear at about −2/tick over 150+ ticks, because rising discharges offset falling leaving. It is strongly asymmetric in both linear and log units.
  - Staffing cut vs restore is asymmetric in both units (B26).
- **Settling** (`greybox.common.settle`):
  - only discharges settle within segments;
  - queue settles at the ceiling holds (R3 100–150 at 26 ticks; R4 joint .7 at 20; joint 1 at 12);
  - wait never settles within 50–90 ticks, so the pre-registered level cells for wait are lower bounds while filling.
- **Return to baseline:** no run returned to 23 within 150 ticks of recovery (B32).
- **Relationships:** conservation (B24), the wait ratio (B30), and discharges vs staff (B23).

## 4. Score-loss ranking

Loss is Σ over ticks of 1 − 1/(1 + |err|/σ), in tick-units. New runs total **R3 159 / 160 / 211** and **R4 240 / 149 / 275** (wait / queue / discharges). Discharges are 41 % of the lost score, wait 33 % and queue 26 %.

| # | Run, segment | Obs | Loss | Mean signed σ | Type | Likely cause |
|---|---|---|---:|---:|---|---|
| 1 | R4 0–90 joint .7 | discharges | 72.7 | −5.4 | level | `we·phi` work penalty (B25) |
| 2 | R4 275–350 recovery +150 | wait | 62.9 | −22.8 (−50 at the end) | level, then growing | B31 wait blow-up |
| 3 | R4 200–275 recovery +75 | discharges | 60.7 | −5.9 | level/dynamics | slow release ramp (B26) + penalty |
| 4 | R4 0–90 joint .7 | wait | 59.0 | −2.7 | level | wait map (B30) |
| 5 | R4 275–350 recovery +150 | discharges | 57.1 | −0.9 (\|e\| 5.0) | dynamics | v1 ramps through 11.5 to 13.2; data flat at 11.1 with quanta (B32) |
| 6 | R3 0–50 electives 5 | discharges | 46.0 | −16.2 | level | B21 (no elective track) |
| 7 | R3 50–100 electives 10 | discharges | 45.6 | −11.5 | level | B25 |
| 8 | R4 0–90 joint .7 | queue | 45.2 | −0.8 | level | ceiling −1σ (B28) |
| 9 | R4 140–200 joint 1 | discharges | 45.2 | −2.6 | dynamics | B25 + discharge bursts |
| 10 | R3 100–150 staffing 15 + electives 10 | discharges | 43.3 | −7.6 | level | B25 |
| 11 | R3 200–250 recovery | wait | 41.9 | −5.2 | level | B30 (drain ratio about 2) |
| 12 | R3 50–100 electives 10 | queue | 41.5 | +5.5 | level | B22 (v1 floods too early and too high) |
| 13 | R3 150–200 staffing 15 | discharges | 40.9 | −4.6 | level | B23/B24 compensation |
| 14 | R3 0–50 electives 5 | queue | 39.9 | +9.0 | level | B21 |
| 15 | R4 90–140 recovery 50 | wait / discharges | 39.5 / 39.1 | −3.9 / −6.2 | level | B30 / B26 |

Full list: `lossrank.out`. Type is from the sign consistency of the error and the share of loss in the first 20 ticks. Transient errors are minor: only R3 50–100 wait qualifies, and the reset dead time is too short to rank.

**Old data (v1 on R1 and R2c; loss R1 337 / 245 / 535, R2c 204 / 150 / 291).** The same error families were already there:

- E/L discharges −8σ to −12σ, level, 25–35 per 30-tick window (B25);
- R1 175–240 release discharges −3.3σ (B26);
- R1 580–750 tail: the largest old item, discharges 135 (+5.6σ at the end) and queue −2.1σ at the end (B32);
- R2 290–350 diagnostic 0.1 switch (G3).

New in round 2: the reset under electives (B21/B22) and the wait blow-up (B31); both were invisible in the old data. The wait-in-drain error (B30) was present but small in the old runs.

**Parameter-only check** (`probe_fit.py`, diagnostic). Refitting 9–10 of v1's parameters (Ae, we, θ, wd, kw, Wmax, Cb, a2, g2 ± qe, aphi) on all four runs:

- R3 rises 0.29 → 0.40–0.44;
- R1 and R2c fall 0.04–0.09;
- g2 pins at its bound of 1, aphi → 0 and qe → 0.

So the misfit is **structural** (lesson 9), not a mis-tuned parameter set.

## 5. Explanations and minimal model changes, in priority order

1. **Per-class elective service instead of the elective work penalty.** Fixes B21, B22, B25 and B24; top-ranked losses 1, 3, 6, 7, 10, 12–14; about 45 % of the new-run loss.
   - **Explanation:** base structure ("routine, urgent and elective cases need different assessment and treatment work"), not a mechanism. Electives are admitted into their own finite long-stay pool:
     - LOS ≈ 17 ticks;
     - pool size ≈ 75–100, the level at which R3's flood starts;
     - modest staff work.
     The pool is counted in the queue. When it is full, electives wait in the shared W and slowly erode shared capacity (R3: 15.9 → 13.4 → 9.5).
   - **Minimal change:**
     - add a state `E_in` with inflow min(elective arrivals, free pool) and outflow `E_in/LOS`, and put the rest into W;
     - set `we` ≤ 0.3, bounded, or drop it;
     - refit Ae (≈ 17.6 at 20) and θ (expect ≈ 1.2–1.4 %).
   - **Conflicts:**
     - R1/R2 E and L discharges (9.6, 6–7) must still be reproduced. They are in the same direction; v1 was already too low there.
     - The R2c permanent residual of 34.5 after an overtime drain contradicts a 17-tick LOS. Keep a small separate residual term, or let it fall out of the pool quanta.
     - The ceiling of 313–327 must remain (Wmax + pools).
2. **Faster release ramp, with fatigue as a one-sided after-penalty.** B26; losses 3, 15, and part of 1 and 9.
   - **Explanation:** M2 handover (Δstaff-driven, full recovery within about 45–50 ticks for Δ = 15 and about 10 for Δ = 5). The lower start after overtime pulses (4.7 vs 8.0) is either M1 fatigue that decays over about 20–30 ticks or pipeline refill after diagnostic .75.
   - **Minimal change:** make the handover deficit ∝ Δs/s with an explicit bound, not `g2·H`, which pins at 1. Remove the slow phi-decay penalty (it goes away with change 1). Keep `g1` bounded (≤ 0.3) with an overtime-driven F.
   - **Conflict:** none with R1 175/580 or R2 350, which show the same ramps. Check that the no-drift result in B27 holds (F must not accumulate during a 90-tick overtime .7 hold).
3. **wait_time as a realized FIFO wait.** B30, and potentially B31; losses 4, 11, 15; about 25 % of the new-run loss.
   - **Explanation:** a plain dynamic. The reported wait is the waiting time of the patients admitted now (patients admitted during a drain arrived when the queue was larger), passed through the existing EMA (reset decay ×0.885/tick, B1).
   - **Minimal change:** keep cumulative arrival and admission curves (or a ring buffer of arrival ticks) for W, and set the wait target = t − arrival tick of the cohort now admitted. Leaving removes patients proportionally. Output EMA with k ≈ 0.12.
   - **Conflicts:**
     - B1 (reset decay from the reading) is kept by the EMA.
     - B3 (staffing 5: wait 97 ≈ (q − 23)/D) is consistent: at steady state a FIFO wait equals Little's.
     - It is bounded by construction (≤ t).
4. **Post-pulse residual plateau and wait blow-up.** B31, B32; losses 2 and 5; the R1 tail was the largest old loss.
   - **Explanation:** unknown, with two candidates:
     - (a) Priority classes. Routine patients are admitted first, and a stranded cohort (electives, or patients who arrived during the pulse) is admitted only at spare capacity. Once the routine backlog clears (+106), the admitted patients are that old cohort, so the FIFO wait jumps to their age, about 150–180, and grows about 1/tick. This combines changes 1 and 3.
     - (b) The residual about 100 are in long-stay service in both runs (not waiting). The R4 jump comes from something pulse-specific that R1 lacked: the prior joint-.7 history, urgent .88–1 held longer, or 150 overtime ticks.
     R1 and R4 have identical queue and discharge tails, so only the composition of the residual differs.
   - **Minimal change** (only after the reserve decides):
     - for (a), two waiting classes with priority admission, and the realized wait from change 3 applied to admitted patients;
     - replace `Lq` (phi-driven, permanent) with a pool filled by the backlog left at release and drained at τ ≈ 200–400 in the tail regime, where discharges are 11.1 < arrivals.
   - **Conflict:** R1's tail wait (decaying to 5.5) must be reproduced by the same model. Under (a) that requires R1's stranded cohort to have left, or never to have been admitted. This is the untested point.
5. **Reset dead time of 2–5 ticks** (B29): transient, low weight. A 2-stage minimum service delay, with the treatment stage slower at low (1 − d) × staff. Fixes the tick-0 discharges of 5.6 vs 0.
6. **Do not add concavity to capacity (H2 rejected)**, and do not touch follow-up (still no effect in any data). Round 2 confirms that the M1+M2 pair is not contradicted: no returns, and fatigue at most in the release start.

## 6. Reserve-step proposal (100 remaining, confirmed by a free `--budget` read)

**What is still unknown:**

- whether B31 is generic (it follows any flood once the routine backlog clears) or pulse-specific;
- how long the post-pulse plateau (B32) and a rising wait persist.

Both feed thousands of recovery-category ticks. Only continuations can answer: a fresh reset needs at least 15 ticks of flood plus about 110 of drain to reach the regime, which exceeds 100 steps. Continuations worked hours later (overnight report).

```sh
cd toronto26-participant-kit
python3 run_schedule.py --budget hospital_queue                      # free; expect 100
cp data/hospital_queue/R4.json data/hospital_queue/R4c.json           # continued copies, like R2c
cp data/hospital_queue/R3.json data/hospital_queue/R3c.json
REC='{"staffing": 20.0, "elective_scheduling": 0.0, "diagnostic_allocation": 0.4, "urgent_priority": 0.6, "overtime": 0.0, "followup_capacity": 1.0}'
# 1) R4 tail +50 (ticks 350-399)
python3 run_schedule.py --continue data/hospital_queue/R4c.json --confirm 50 --segments "[{\"steps\": 50, \"action\": $REC}]"
# 2) R3 tail +50 (ticks 250-299; its queue, 204 and draining 2.2/tick, reaches about 150 at tick 275)
python3 run_schedule.py --continue data/hospital_queue/R3c.json --confirm 50 --segments "[{\"steps\": 50, \"action\": $REC}]"
```

**Total: 100 steps.** Run 1) first. If a continuation is refused (run expired), **do not spend**: a fresh run can't rebuild the state within the reserve.

| Probe | Outcome | Decides |
|---|---|---|
| 1) R4c +50 | Wait keeps rising about 1/tick and the queue stays at about 100 | Stranded cohort admitted at a trickle, its age growing: implement change 4(a) (priority classes + FIFO wait). Pool lifetime > 200. |
| | Wait peaks and collapses as the queue steps down toward 23–35 | Finite cohort: the collapse time gives the pool lifetime. Implement 4(a) with a finite cohort, and set the drain τ from the step-downs. |
| | Queue asymptote about 35 vs about 100 | Whether R2c's permanent 34.5 is the same object as the post-pulse pool (a single residual state) or not |
| 2) R3c +50 | The wait jump appears around the queue ≈ 150 crossing | **Generic**: every flood followed by recovery has it, so it carries large scoring weight. Change 4 is top priority. |
| | No jump (like R1) | Pulse-specific trigger (urgent ≥ 0.88, overtime, diagnostic .75, or the prior joint-.7 history). Keep v1-style wait decay by default and treat R4 as a bounded special case. Changes 1–3 take priority. |

Alternative, lower value: electives 5 for 100 ticks from reset, to get the sustained electives-5 level (R3 was unsettled at tick 50). Change 1 should predict it from R3 + E, and the flood trend (+2.4/tick) already suggests the ceiling.
