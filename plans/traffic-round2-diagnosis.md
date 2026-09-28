# Traffic round-2 diagnosis (R4 = TR1, R5 = TR2)

Diagnostician pass, 2026-09-28. **No simulator steps were spent** and no model was changed.
Scripts, tables and plots: `toronto26-participant-kit/fits/traffic/round2/`. All paths below are relative to
`toronto26-participant-kit/`. σ = score σ = 0.1 × std after tick 20 of all traffic data (R1–R5), as in `heldout.py`:
flow_a 0.93, flow_b 0.71, speed_a 1.29, speed_b 1.02.

Plots (data black, v1 red, error panel in σ, controls panel):
[R4](../toronto26-participant-kit/fits/traffic/round2/R4_v1.png),
[R5](../toronto26-participant-kit/fits/traffic/round2/R5_v1.png); the old runs on the same footing:
[R1](../toronto26-participant-kit/fits/traffic/round2/R1_v1.png),
[R2](../toronto26-participant-kit/fits/traffic/round2/R2_v1.png),
[R3](../toronto26-participant-kit/fits/traffic/round2/R3_v1.png). Battery plots: `fits/traffic/round2/R4_r0_battery.png`, `R5_r0_battery.png`.

| Script | Output |
|---|---|
| `plots.py` | `R*_v1.png` |
| `segtable.py R4 R5` | per-segment levels, v1 error and loss split (`segtable_R4_R5.json`; old runs: `old_segtable.txt`) |
| `rank.py` | score-loss ranking (`rank_R4_R5.json`, `old_rank.txt`) |
| `cands.py` | v1/m12/m13/m23 on the real R4/R5 schedules (`cands.out`) |
| `burst.py`, `modetest.py` | burst floor of the flows; the "predict the mode" test |
| `longrun.py` | v1 at 2,000-tick holds of every round-2 setting |

## 1. Summary

1. **The congestion onset lies below u = 0.7.** At u.7 both routes congest. Route B sits at its usual congested state (speed_b 15.9, bursty flow_b 12.8), and A is part-congested (speed_a 12.3 and still falling). m13 is rejected (+11σ). v1 is −3σ on speed_a, and no candidate fits all four observables.
2. **The main new structural fact is capacity versus green share.** A's congested flow is flat for green 0.3–0.5 (≈ 17–19) and falls steeply below ≈ 0.25 (15.2 at 0.255, 10.5 at 0.20, 7.5 at 0.15). B's congested flow is 12.2–13.5 and speed_b 15.0–16.1 in **every** congested hold, whatever green_B (0.5–0.85), lane, crew, freight or toll. v1 uses a power law in green for both routes, so it is off by −6σ (A at green 0.3), +4σ (B at u.7) and −3σ (A at u.7).
3. **The top speed losses share one cause.** v1's A capacity at interior green is too low, so v1 builds too large an A queue. That gives speed_a −3σ through the whole u.7 hold, a drain after u.7 that is 8 ticks too slow (speed_a −8σ, segment score 0.15), and a post-release peak that is 6σ too low.
4. **Flows are about 57 % of the lost score, and about 70 % of that is a burst floor.** The target is the noiseless bursty series, and the best constant scores only 0.2–0.35 in congestion. Predicting the mode (0) was tested and loses. Only level errors on flows are fixable.
5. **Minor findings.** There is no memory across a 40–50-tick empty gap. B8 (the speed_b ratchet) did not recur. The reset transient under control is missed (the speeds first rise), and so is the onset speed. freight 0 has a real effect (flows up, speed_a +1), but it lies outside the scored family. Reserve: one 100-step run that tests the green-share knee in isolation, which is also a scored single-control pulse.

## 2. Decision-rule verdicts

These are the rules in `round2-experiments.md` §5.4. "Measured" is the mean of the last 10 ticks unless marked. The candidate values are the real-schedule rollouts (`cands.out`), which agree with `final_traffic.out` to within 0.1. Errors are prediction − data, in σ, in the order fa, fb, sa, sb.

| Rule / question | Measured (fa, fb, sa, sb) | v1 | m12 | m13 | m23 | Verdict |
|---|---|---|---|---|---|---|
| TR1 u.7, ticks 50–149: "does the congestion onset lie below or above u.7? (sa 8.4 / 15 / 26 / 10.5)" | 15.25, 12.78, **12.30**, 15.88. speed_a is unsettled: the exponential asymptote is 11.9 (k 0.04). speed_b is at the B floor and flow_b is bursty | 12.2, 15.7, 8.4, 17.6 (−3.3, +4.1, −3.0, +1.7) | 14.0, 14.2, 15.0, 17.5 (−1.3, +2.0, +2.1, +1.6) | 15.4, 17.9, 26.3, 27.4 (+0.1, +7.2, **+10.9, +11.2**) | 10.7, 12.9, 10.5, 17.2 (−4.9, +0.2, −1.4, +1.3) | **Onset is below u.7** (congested). m13's uncongested branch is rejected. On speed_a, m23 and m12 are nearest; no candidate is within 2σ on all four. |
| TR1 u.7, ticks 0–49 (first 50) | 15.94, 11.98, 24.85, 17.38 | −0.1, +6.0, −4.5, +4.0 | +1.1, +5.0, −0.5, +7.2 | −0.4, +8.0, +1.1, +9.9 | −1.6, +3.9, −2.4, +7.8 | B congests faster than every candidate predicts (speed_b is at 17 by tick 45). |
| TR1 rec 50 after u.7: "the drain splits 6σ" | 0, 0, 48.42, 48.70 (A empty at +26, B at +28) | −4.7σ on sa (segment score 0.15) | −0.1 (0.47) | +0.9 (0.22) | −2.2 (0.22) | **The drain is fast.** v1 is worst, and m12 matches both the end level and the segment best. Cause: v1's A queue is too large (§5, change 1). |
| TR1 "locate the congestion onset in heavy share between u.7 and u.85" | u.7 → sa 12.3; u.85 → 8.6 (asymptote ≈ 7.0); u1 → 7.1 (still falling) | — | — | — | — | **Not bracketed.** Both are congested. A's congestion deepens continuously with u (12.3 → 8.6 → 7.1), and B is already saturated at u.7. With R3 (B congested at toll 2.5 alone), the onset on the ray is at u ≲ 0.5–0.6. |
| TR1 u1 (80 ticks after 50 recovery) | 7.54, 12.20, 7.15, 16.13 | −0.4, +1.8, −0.1, −0.4 | −0.3, +1.6, −0.1, −0.4 | −1.0, +2.8, −0.4, −0.4 | −0.6, +1.7, −0.1, −0.3 | All candidates are fine at the level (it is in-sample, as in the R2 joint pulse). B's flow is too high in all of them. |
| TR1 u.85 (90) | 9.71, 12.40, 8.59, 15.81 | 0.0, +3.4, −0.6, +0.8 | −0.3, +2.5, −0.6, +0.7 | −1.6, +2.0, −0.9, +0.5 | −1.1, +1.1, −0.7, +0.7 | Levels are within 1σ except flow_b (+1 to +3σ in all candidates). speed_a is unsettled (asymptote ≈ 7.0). |
| TR2 background B = ramp 1 + toll 1.5: "congested background (speeds 14–16)" | 20.32, 10.69, 14.01, 15.01 (sa still falling, asymptote ≈ 11.5) | −4.0, −0.2, +0.3, +0.8 | −3.8, +0.3, +1.2, +1.2 | −5.1, −0.5, +0.5, +0.9 | −5.2, −1.3, +0.7, +0.9 | **Confirmed congested.** v1's A flow is too low. |
| TR2 freight 0: "speed_a to 8.7" (never probed; G10) | 18.85, 11.51, **9.62** (settled), 14.91. Mean of the last 20: total flow 32.8, against 28.9 at the end of B | −4.3, −1.2, −0.7, +0.5 | −4.5, −0.6, −0.6, +0.7 | −5.7, −1.5, −0.6, +0.5 | −5.5, −2.1, −0.8, +0.6 | **Freight 0 has an effect that no candidate has.** Throughput rises (A +2, B +1.8 veh/tick) and speed_a is about +1 above v1's trend. v1's 2,000-tick B+freight0 hold is identical to B (`longrun.py`), so the 8.7 was just B's settling. Caveat: B's speed_a was still drifting. |
| TR2 signal 0.3 | 16.07, 12.85, 8.40, 15.65 | **−6.1**, −0.1, −0.3, +0.4 | −7.8, … | −7.9, … | −8.4, … | **A's capacity at green 0.3 is far above the power law** (flow_a 16.9 for the last 20, against 10.4). B is unchanged at green_B 0.7. |
| TR2 lane 0.3: "fix G12" | 16.72, 11.13, 7.84, 15.28 | −2.5, −0.9, +0.6, +0.1 | −4.1, −2.5, +0.5, −0.2 | −3.8, −2.3, +0.6, −0.1 | −4.3, −3.6, +0.4, −0.1 | **Weak.** Relative to v1's trend, speed_a is about 1 lower (v1 has wl_A = 0). This is confounded with the drift in B34 and with signal switching back at the same tick. G12 stays open. |
| TR2 clearance 0.5 | 21.24, 13.27, 7.48, 14.98 | −4.4, −1.9, **+1.0**, +0.8 | −6.2, −1.8, +1.0, +0.8 | −6.4, −2.8, +1.1, +0.5 | −6.3, −3.4, +0.8, +0.7 | Small: speed_a is about 1.3 lower than v1 and throughput a little higher. Confounded with the drift. |
| Residual risk: the period-2 oscillation under per-tick switching | not tested | | | | | Still open. |

Held-out score of the whole runs (`cands.py`): R4 v1 0.361, m12 0.385, m13 0.348, m23 0.376. R5 v1 0.452, m12 0.445, m13 0.454, m23 0.448. m12's R4 edge is all speed_a (the u.7 level and the drain). It is not a mechanism signal: the m12 all-data fit carries a different A capacity.

## 3. Behaviour catalogue (new runs; numbering continues from B23)

Categories: S = sustained, O = action order, R = recovery history, C = composition. Error sizes are v1 − data in σ.

| ID | Behaviour | Evidence | v1 status | Categories |
|---|---|---|---|---|
| **B24** | **Reset transient under control.** Before any vehicle completes, the speeds first *rise* from the reading toward free flow (R4: 36.3 → 43.9 by tick 4, 36.6 → 41.4 by tick 3; R5 speed_b 36.5 → 39.8 by tick 2; k ≈ 0.2–0.25). They turn down at ticks 3–5, well before the first exit at tick 11–12. | R4/R5 ticks 0–12 | **Not captured.** v1's speeds fall from tick 0 (in-transit load acts at once, kv 0.107). Max error −8.9σ (sa, R4), −6.5σ (sb, R5); loss ≈ 20–23 tick-units per episode. | all (every episode) |
| **B25** | **u.7 congests.** B saturates by about tick 45. A is capacity-bound and smooth: flow_a 18.6 at ticks 15–30, falling smoothly to 15.2 by tick 60 (fullness penalty). speed_a falls in two phases: to about 28 in 15 ticks, then slowly (k 0.04) to 12.3, **unsettled** at 150 ticks. | R4 0–150; settle: sa not settled (drift 3σ, asymptote 11.9) | **Not captured (level):** fa −3.3, fb +4.1, sa −3.0, sb +1.7 for about 100 ticks. Loss 403, the largest segment. | S, R, C |
| **B26** | **A's capacity is a knee in green share.** Congested flow_a is ≈ 19 at green 0.5 (R5 B), 16.9 at 0.3, 15.2 at 0.255 (u.7), 10.5 at 0.2025 (u.85) and 7.5 at 0.15 (u1; R2 6.66). In PCU (v1's heavy share and pce) the points below 0.26 lie on one line, ≈ 70–77 PCU per unit green. Above ≈ 0.3 A is capped by something else (≈ 25–30 PCU). | segtable R4/R5; R2 joint | **Not captured.** v1's `(green/0.5)^0.61` gives 14.5 / 10.4 / 12.2 / 9.7 / 7.1. Error −6σ at 0.3, −3.3σ at 0.255. | S, C |
| **B27** | **B's congested state is invariant.** flow_b is 12.2–13.5 and speed_b 15.0–16.1 in all 8 congested round-2 holds and the old ones: green_B 0.5–0.85, lane 0–0.65, clearance 0–1, freight 0–1, toll 0–1.5. B has a fixed bottleneck of ≈ 12.5 veh/tick (≈ 16–17 PCU) that green does not reach. | R4, R5, R2 joint, R1 toll 0 | **Not captured.** v1's flow_b moves with green_B (10.5 → 15.7): +4.1σ at u.7, +3.4σ at u.85, −1 to −4σ in R5. speed_b is +0.5 to +1.7σ. The same error is in the old data: R2 joint +1.8σ, R2 second pulse +6σ, R1 toll 0 −2.6σ. | S, C |
| **B28** | **The drain after u.7 is fast.** A empties 26 ticks after ramp-off and B 28. Both speeds reach halfway at +27 and **jump together** (+6 in one tick at tick 175, when the last A vehicles exit). | R4 150–200 | **Not captured (dynamics):** v1's A takes 34 ticks and B 23. speed_a is −8σ on average (segment score 0.15). | R |
| **B29** | **On/off asymmetry.** Onset from an empty network is fast: speed half-times 9 ticks (A) and 6 (B) at u1. Recovery is slow and delayed by the queue drain: 26–34 ticks after u1. It is asymmetric in both linear and log units. This is a plain queue-storage dynamic. | R4 200 / 280 | **Partly captured.** The recovery shape is fine for B. The onset is too slow (v1 half-times 14 and 12), with errors up to +10σ at ticks 205–215. | R, O |
| **B30** | **Speeds keep rising into the next pulse** for the 5–6-tick dead time. Peaks are speed_a 30.8 at tick 316 and speed_b 44.7 at 315. This is not an overshoot. | R4 305–320 | **Not captured:** v1 peaks at 22.5 and 40 (−6σ and −4σ). A consequence of B28 and B29. | R |
| **B31** | **Dead time is longer on B at heavy mix or lane closure.** Flows restart after 10–11 (A) vs 16 (B) ticks at u1, 12 vs 14 at u.85, and 11–12 on both at toll 1.5 (with lane 0 or 0.455). Confirms G11 and makes it B-specific. The toll and lane effects are confounded on the ray. | R4 200, 310; R5 0 | Not captured (DT fixed at 11). Small, because flows are bursty. | R |
| **B32** | **No memory across a 40–50-tick empty gap.** u1 after (u.7 + 50 recovery) in R4 and joint after (joint + 40 recovery) in R2 S7 follow the same path. speed_a at +10/+20/+45/+60 is 27.0/18.5/9.6/8.3 vs 27.1/18.0/10.4/8.6; speed_b 24.0/19.5/16.8/15.6 vs 23.2/19.2/16.7/15.4. | R4 vs R2 | **Captured** (v1 has no memory). This is evidence against fronts or fatigue that outlive an empty network. | R, O |
| **B33** | **Free flow returns** to 48.4–48.9 after release. No B8 ratchet: speed_b is 48.7 and still rising at the end of the 50-tick recovery. | R4 190–199 | Captured. B8 should be dropped as a target. | R |
| **B34** | **Slow speed_a drift in congested holds.** speed_a is unsettled after 80–150 ticks: u.7 k ≈ 0.04 (asymptote 11.9), u.85 k ≈ 0.03 (≈ 7.0), u1 still −0.025/tick at 80 ticks. In R5 it steps down 9.7 → 8.2 → 7.7 → 7.55 across the gray-code segments. B does not drift (settles in ≈ 50 ticks). | settle tables | **Open.** v1 settles in ≈ 100 ticks and holds that level to 2,000 ticks (`longrun.py`). The long-run level at every interior setting is an extrapolation. | S |
| **B35** | **freight 0 (the untested side):** throughput +3–4 veh/tick in total and speed_a +1 relative to v1's trend. It settles in < 20 ticks. The sign agrees with R1's freight 1 in congestion (fewer vehicles and falling speed_a): a lighter served mix passes more vehicles. | R5 50–90 | **Not captured.** v1 shows no long-run effect at all: −0.7σ sa, −4.3σ fa. Outside the scored family (scoring pulses freight 0.5 → 1). | (C) |
| **B36** | **lane 0.3 and clearance 0.5 in congestion:** speed_a is about 1 below v1's trend and throughput slightly higher. | R5 130–200 | Not captured (+0.6 and +1.0σ on sa), but confounded with B34. Weak evidence. | (C) |
| **B37** | **Burst structure.** Burst quanta scale with ramp: 5.6 / 13.0 / 18.6 at ramp 0.7 vs 8.1 / 18–20 / 25.5–28.4 at ramp 1 (ratio ≈ 0.7). A capacity-bound A is smooth with periodic spikes; B is bursty. Per-tick burst σ is 5.5–10. The best constant scores only 0.20–0.35 in congested holds. | `burst.py`; R4 0–60 printout | Unavoidable for a smooth model. v1 scores 0.1–0.45 there. **"Predict 0 (the mode) when congested" was tested and rejected**: only 2–7 % of ticks are exactly 0, and the flow score falls from 0.47 to 0.40 for A and from 0.43 to 0.38 for B (`modetest.py`). | all |
| **B38** | **Relationships.** speed_b leads speed_a by 3 ticks (level corr 0.85, R4), and the level corr is 0.82 at lag 0 in R5. B congests first and drains first. Total congested throughput is ≈ A-capacity(green) + 12.5. Demand far exceeds it in every round-2 setting (v1 D = 38–67 veh/tick), so congested flows equal capacities and say nothing about demand. | battery `R4_battery.txt`, `R5_battery.txt` | Captured by the structure. | — |
| **B39** | **Noise.** Speeds vary 0.2–0.3 % in settled holds (σ 0.025 at 8–14). Flows in smooth capacity-bound stretches ≈ 0.1. Unchanged from B22. | settle σ | n/a | — |

## 4. Score-loss ranking

The loss is Σ over ticks of 1 − 1/(1 + |err|/σ), from `rank.py`; a perfect forecast has 0. The total over R4 + R5 is 1,461 tick-units: flow_a 409, flow_b 425, speed_a 326, speed_b 301. Of the 834 flow units, ≈ 577 are the **burst floor**, meaning the loss of the best constant over the settled part.

The loss is split three ways:
- **transient**: the first min(20, n/3) ticks of the segment;
- **level**: the part removed by shifting v1 by its median late error;
- **dynamics**: the rest.

| # | Run, ticks | Setting | Obs | Loss | Transient / level / dynamics | Late bias | Type |
|---:|---|---|---|---:|---|---:|---|
| 1 | R4 0–150 | u.7 | speed_a | 112 | 14 / **56** / 41 | −3.0σ | **level** (B25/B26) |
| 2 | R4 0–150 | u.7 | flow_b | 105 | 8 / 4 / 93 | +4.0σ | burst floor 90; level part small in score terms but +4σ in mean |
| 3 | R4 0–150 | u.7 | speed_b | 102 | 14 / **52** / 36 | +1.9σ | **level** (B27) |
| 4 | R4 0–150 | u.7 | flow_a | 84 | 7 / 0 / 77 | −1.9σ | burst floor 59; about 18 reducible (level) |
| 5 | R4 310–400 | u.85 | flow_a, flow_b | 68 + 68 | — | 0 / +3.8σ | burst floor |
| 6 | R4 200–280 | u1 | flow_b | 63 | 9 / 3 / 51 | +5.6σ median | burst floor 44 |
| 7 | R4 310–400 | u.85 | speed_a | 53 | 11 / **19** / 23 | −1.6σ | level + dynamics (B34 drift, B30 peak) |
| 8 | R4 310–400 | u.85 | speed_b | 51 | 16 / **19** / 16 | +0.9σ | level (B27) + transient (B30) |
| 9 | R4 150–200 | recovery after u.7 | speed_a | 43 | 13 / 7 / **23** | −8.1σ | **dynamics** (B28) |
| 10 | R4 200–280 | u1 | speed_a | 40 | 14 / 7 / 19 | −1.0σ | onset dynamics (B29) |
| 11 | R4 200–280 | u1 | speed_b | 35 | **16** / 1 / 18 | −0.1σ | onset transient (B29) |
| 12 | R5 (all segments) | B / freight 0 / signal 0.3 / lane 0.3 / clearance 0.5 | flows | 22–34 each | — | fa −1 to −5σ | burst floor about 90 %; A level −3 to −5σ (B26, B35) |
| 13 | R4 150–200 | recovery after u.7 | speed_b | 29 | 7 / 2 / 20 | −0.5σ | dynamics (B28) |
| 14 | R4 150–200 | recovery after u.7 | flow_a | 26 | **10** / 0 / 16 | — | transient (A drains 8 ticks too long) |
| 15 | R5 0–50 | reset + B | speed_b / speed_a | 23 / 19 | **12 / 8** transient | +0.5σ | **transient** (B24) |
| 16 | R5 freight 0, clearance 0.5, lane 0.3, signal 0.3 | | speed_a | 11–15 each | level 5–9 each | −0.7 to +1.0σ | level (B35/B36, confounded with B34) |

**Most of what can be recovered is in the speeds.**
- Speed level: 215 units, mostly u.7 and u.85 (B25–B27).
- Speed dynamics and transients: about 160 units (the drain, the onset and the reset: B24, B28–B30).
- Flow levels are worth only ≈ 50–80 units because of the floor. In the mean, though, they are off by 3–6σ (A too low at interior green, B too high at high green_B).

**Old data (v1 in-sample; `old_rank.txt`, total 2,237 units).** The same classes of error were already there:
- The flow burst floor dominates: R2 joint pulse flows 153 + 107.
- B's flow level: R2 joint +1.8σ, R2 second pulse +6.1σ, R1 toll 0 −2.6σ. This is B27 in-sample. The fit averaged an invariant B capacity into a green slope.
- speed_b level at B7 (R1 605–700, +2.6σ) and R1 toll 0 speed_a level (−2.7σ).

What is **new** in round 2 is A at interior green (B26). Before round 2, green had only been held at 0.5 and 0.15 in congestion, so the power law was never tested between them.

## 5. Explanations and minimal model changes, in priority order

1. **Capacity = min(green-limited, fixed route cap), in PCU. This covers B25, B26, B27 and B28, and partly B30 and B7.**
   - Explanation: a plain dynamic, a saturating capacity. The brief's "signal timing divides new crossing admissions" limits admissions only while green is scarce. Beyond that, a downstream or exit capacity binds. B always has green_B ≥ 0.5 on the scored ray, so it always sits on its flat part. That explains why B is invariant.
   - Change: `cap_r = smin(κ_r·green_r, Cmax_r) · (other factors)` in PCU, with a soft-min (for example a p-norm, p ≈ 4–8, so the fit stays smooth). This replaces `(green/0.5)^wg`.
   - Starting values: κ_A ≈ 70–80 PCU per unit green, Cmax_A ≈ 25–30 PCU, Cmax_B ≈ 16–17 PCU (12.5 veh at the toll-1.5 mix). κ_B is poorly identified (green_B < 0.5 in congestion was never held), so share κ.
   - Expected gain: it removes the oversized A queue at u.7, which fixes speed_a −3σ, the drain −8σ and the post-release peak, and it pins flow_b and speed_b.
   - Conflicts:
     - R1 signal 0.15 at D: A carried 11.2 veh at toll 5 uncongested. At the light mix this needs κ_A·0.15 ≥ ≈ 12.5 PCU, so κ_A ≥ 84. That sits slightly above the congested estimate, so check it in the fit. If they clash, add a mild lane/crew factor at u1.
     - **B7 (R1 605–700):** B demand of 12 against Cmax_B ≈ 12.5 makes a nearly neutral queue, which is the persistence the review asked for. The change should *improve* B7.
     - R2 S3 (green_B 0.1 at demand 6) stays uncongested. No conflict.
2. **Speed dynamics: a faster relaxation plus a short delay on the load term. This covers B24, B29 and partly B30.**
   - Explanation: a plain dynamic. "Reported speed combines observed completed journey times with current … mix": nothing has completed yet, so the reading relaxes toward free flow until vehicles are a few ticks into their journey.
   - Change: count in the load term `al·(n/100)^pa` only the pipeline cells older than about 3–4 ticks (a pure delay of the load input, not a lag), and let kv be refit.
   - Evidence: the data relaxes with k ≈ 0.2–0.25 at reset, and the onset half-times are 6–9 ticks against v1's 12–14.
   - Conflicts: none known. R1 and R2 already showed speed reacting 2–7 ticks after ramp-on. Check that the slow recovery (queue-limited) is still produced by the queue terms rather than by kv.
3. **The slow speed_a drift in congestion (B34), for the sustained category.**
   - Simplest explanation: a plain dynamic. A's arrivals exceed its capacity slightly, so the A queue fills its buffer slowly (qmax_A 560 PCU); speed_a follows the queue term (be_A·Q). The long flow_a decline 18.6 → 15.2 is the fullness penalty sp_A acting over the same buffer.
   - Change 1 alone may reproduce it, because a smaller A service gap means a slower fill. Refit first, then check the 150-tick asymptote (11.9 at u.7).
   - If not, use a bounded, saturating time-in-queue term, not an unbounded ramp (lesson 8).
   - Alternative explanations: M2 fatigue under clearance < 1, or M3 fronts. They are not needed: B32 shows no memory across an empty gap. Test them only if change 1 leaves a drift.
4. **freight priority on both sides (B35), low priority.**
   - Explanation: a plain dynamic. Priority changes the *served* mix. When the approach buffer is full, arrivals are rejected in the arrival mix, so v1's served mix returns to the arrival mix and priority has no steady effect.
   - Minimal change: rejections or diversion hit the lower-priority waiting class first (for example, divert a share ∝ `wait·(1 − priority weight)` of that class). The served mix then gets lighter at freight 0 and heavier at freight 1.
   - Consistent with R1 (freight 1: fewer vehicles, falling speed_a). Scoring never sets freight below 0.5, so the payoff is small. Do it only if cheap.
5. **B-route dead time (B31), low priority.** A second, heavier pipeline (DT_h ≈ 16) for B, or a DT_B that grows with lane or heavy share. It moves only 3–5 onset ticks of bursty flows per pulse.
6. **Lane and clearance in congestion (B36): no change yet.** The evidence is confounded with B34. Revisit after change 3.
7. **Flows: target level only (B37).** Keep a smooth forecast at the conditional level. Do not predict the mode. The level fixes from changes 1 and 4 are what move the flow score.

**Mechanisms.** None of the new behaviours needs M1, M2 or M3. B32 (identical second pulses after a 40–50-tick gap) and B33 (no ratchet) weaken the persistent-front and fatigue readings. Keep shipping the base, and retest the pairs only after change 1, with staged fits (base frozen).

## 6. Reserve-step proposal (100 steps, per `round2-experiments.md` §0; not spent here)

The biggest open question behind changes 1 and 3: **is A's drop at u.7 and u.85 caused by green alone (a knee), or by the lane, clearance and freight settings that move with it along the ray?** This is also a scored case: signal alone at 70–100 % with ramp on.

**TR3: fresh reset, 100 steps, one `run_schedule.py` call per segment.** Background B is signal 0.5, lane 0, toll 1.5, ramp 1, freight 0.5, clearance 1.

| Segment | Steps | Action | Purpose |
|---|---:|---|---|
| S1 | 30 | B | Builds congestion. It is also a replicate of R5 ticks 0–29 from reset. |
| S2 | 35 | B + signal 0.255 | A's capacity at green 0.255 with nothing else moved (signal at u = 0.7) |
| S3 | 35 | B + signal 0.2025 | the same at green 0.2025 (u = 0.85) |

Predictions, as last-20-tick means of flow_a (then flow_b):

| Model | S2 (0.255) | S3 (0.2025) | Note |
|---|---:|---:|---|
| v1 | 9.6 (13.3) | 8.4 (13.9) | m12, m13 and m23 give 7.7–8.9 and 6.5–7.6 |
| H1, green knee (change 1) | ≈ 14–15 (≈ 12.5) | ≈ 11 (≈ 12.5) | |
| H2, the ray's other controls cause the u.7 drop | ≈ 17–19 (≈ 12.5) | ≈ 17–19 (≈ 12.5) | |

What each outcome decides:
- **flow_a ≤ 15.5 in S2 and ≤ 12.5 in S3** → H1. Implement the capacity knee with κ from these two points, and hold wl, wc and kf near v1.
- **flow_a ≥ 16.5 in both** → H2. Green is weaker than thought. Put the u.7/u.85 reduction on lane/crew/freight (refit wl_A, wc_A, kf with lane and crew acting on A's junction). G12 is then answered as "lane acts on A in congestion".
- **flow_b outside 11.5–13.5, or speed_b outside 15–16.5**, at green_B 0.745–0.80 → B is not invariant, and Cmax_B needs a green term.
- speed_a in S2 and S3, compared with v1's 8.7 and 7.5, gives a second, smooth check on the same question (the flow means carry burst noise of about ±1.5).
- **The S1 replicate against R5 0–29:** if flows match tick for tick (|Δ| < 0.5 on ≥ 90 % of ticks), the bursts are deterministic given the schedule. A phase-true burst model could then be considered later: flows are about 57 % of the loss. If not, the smooth-level target is final.

Not recommended: extending holds to settle B34. It needs ≥ 300 ticks per setting, which does not fit, and change 1 may explain it for free. Continuing R5 with `--continue` would save the 30-tick build-up, but it risks a stale server state (review note) and loses the replicate.
