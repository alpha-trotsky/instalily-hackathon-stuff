# Round 2 report (2026-09-28)

## Contents

- Diagnosis per system: `plans/<system>-round2-diagnosis.md`
- Model record per system: "Round 2 model (v2)" section in `plans/<system>-plan.md`
- Experiment design: `plans/round2-experiments.md`

## Summary

**Deliverable:** `toronto26-participant-kit/submission-round2-final.zip`.

- Nine systems are v2. Market stays v1.
- An alternative, `submission-round2-alt-market-v2.zip`, is identical except market is v2 (see §3).
- Both ZIPs pass the package check: the ZIP is extracted, 40 × 4,000 steps are run per system, and the credential scan is clean.
- **Final uploads only** (the public phase is closed).
- Round 2 spent 8,220 steps. Reserves are untouched (§4).

## 1. How each model was chosen

1. **Diagnosis.** One diagnostician agent per system catalogued every behaviour in the new runs. It evaluated the pre-registered decision rules and ranked where v1 loses score.
2. **Modelling.** A separate modeler agent per system built v2 from that diagnosis. Rules:
   - make the simplest structural change;
   - keep every term bounded;
   - each added term must improve the held-out score.
3. **Validation.** v1 never saw the round-2 runs, so the comparisons are:
   - **(A)** v2 fitted on the old runs only, scored on the new runs;
   - **(B)** leave one new run out;
   - **(C)** v2 fitted on all data, which is the shipped fit.
4. **Scoring σ.** σ = 0.1 × std of all data. Scores are the mean over observables of 1/(1 + |err|/σ).

## 2. Results

- The new runs deliberately cover hard, never-seen regimes, so all absolute numbers sit far below public scores. Compare columns within a row only.
- The "Old runs" column is the in-sample score on the old runs, v1 → shipped fit.

| System | Public (v1) | v1 on new runs | v2 (A) | v2 (B) | Old runs | Shipped |
|---|---:|---:|---:|---:|---|---|
| supply_chain | 0.845 | 0.353 | **0.547** | 0.346 / 0.606 | 0.555 → 0.588 | v2 |
| social_contagion | 0.627 | 0.282 | 0.375 | **0.426** | 0.718 → 0.683 | v2 |
| epidemic | 0.720 | 0.531 | **0.629** | 0.605 | 0.741 → 0.701 | v2 |
| power_grid | 0.742 | 0.399 | 0.459 | 0.450 | 0.538 → 0.536 | v2 |
| wildlife | 0.661 | 0.419 | 0.475 | 0.469 | 0.510 → 0.600 | v2 |
| hospital_queue | 0.672 | 0.331 | 0.382 | 0.390–0.401 | 0.556 → 0.533 | v2 |
| traffic | 0.834 | 0.407 | 0.430 | 0.438 | 0.552 → 0.547 | v2 |
| reservoir | 0.852 | 0.650 | 0.666 | 0.667 | 0.681 → 0.682 | v2 |
| ad_auction | 0.879 | 0.524 | 0.537 | 0.525–0.594 | 0.581 → 0.586 | v2 |
| market | 0.684 | 0.326 | 0.364 | 0.303 / 0.395 | 0.697 → 0.608 | **v1** (§3) |

### Design choices and what they predict

| System | Changes | Predictions |
|---|---|---|
| **supply_chain** | Service is now min(receiving capacity 49.5·r, upstream limit U); maintenance, mix, rush and idle act on U only. Retail sales now depend on a bounded moving average of arrivals. | All states settle by about tick 1,000. Shipments at orders 80 alone settle at 32.1 (data 34.8). |
| **social_contagion** | M1 (credibility) removed; the M2 linear-gap model is refit on R1–R5. The more elaborate "promise ratchet" lost the leave-one-out test and was not shipped. | Recovery ends at 95/80 (measured ≈ 93/77). Crash floor 65/49. Cutting incentive from 2 to 1 gives 139/77 (measured 143/75). |
| **epidemic** | m12 (closure moves children's contacts home). Vaccination is weighted to the elderly: it cuts hospital load per case more than it cuts cases. Mask fatigue is kept; the data rejected removing it. | Stable through the 8 × 40,000-step stress runs, with cases from 15.6 to 630. |
| **power_grid** | Frequency is a lag towards a static map of load, saturating reserve and interconnector; the pinned secondary loop is removed. The load swing has a floor at 65.7 and higher gain. Renewable share has a floor under reserve. Pair m1+m3; M2 dropped. | Load stays between 65.7 and 191 over 4,000 ticks. |
| **wildlife** | Predators follow one prey signal shared by both regions. The corridor depresses predators for as long as it is open. Predators fall faster when their target is low, which fixes the reset tail under controls. Pair mA+mB. | All of the gain is on predators. A known flaw remains: hunting 7 lands at a different long-run level depending on history, as in v1. |
| **hospital_queue** | The elective work penalty and long-stay pool are removed; electives are plain arrivals. The staffing-increase handover is proportional and bounded. `wait_time` is now the realised first-come-first-served wait. | After long overloads the queue drains to 23; the data plateau near 100 (open issue). |
| **traffic** | Capacity is a soft minimum of a green-share limit (74.9 PCU per unit green) and fixed route caps (A 26.8, B 17.9). Speed now reacts to load with a 3-tick delay. No mechanisms. | The congested B route settles at about 12.4 at every high setting. |
| **reservoir** | Quality: a bounded overshoot after reset settles to a 0.948 baseline. An anoxia pool is cleared by deep withdrawal and released when aeration returns. The aeration response is convex. Fast groundwater store at reset. M1+M3. | Quality score noise-reduced 0.12–0.18 → 0.38–0.42. |
| **ad_auction** | Purchase-side exposure fatigue added (τ ≈ 44). Fulfilment capacity is now sharp and binding, which reproduces the plateau and the drop. | The binding-capacity choice is not confirmed by held-out data. |

## 3. Why market ships as v1

- **Held-out gain is small and partly leaky.** v2 beats v1 held out only modestly. Test (A) mostly reflects starting values informed by the diagnosis, and (B) is a tie on one fold.
- **v2 loses on run A in every segment:**
  - the reset transient: price score 0.67 → 0.24;
  - the single-control holds: price and depth score about 0.05–0.12 lower.
- **The public score says the scorer's episodes look like run A for v1.** v1's public score (0.684) matches its fit on run A (0.697). On runs B and C, which are joint pulses from reset, v1 scores 0.33. The scorer's episodes therefore sit much closer to A than to B or C, and that is where v2 loses.
- **v2 has an untested 4,000-tick extrapolation:** at full tax, depth is stuck at 16.
- **Use the alternative ZIP instead** if you believe the joint-from-reset regime dominates scoring.

## 4. Where to spend the last steps

Each schedule below was proposed by the diagnostician, sharpened by the modeler, and recorded in each plan with exact commands and v2's predictions. Each run tests the largest remaining risk in a shipped v2. After any run: refit (C) including it, rerun validation (B), and re-package as v3.

| System | Left | Schedule | Decides |
|---|---:|---|---|
| social_contagion | 120 | Fresh reset. Seeding 6.3 + bridge 0.42 at incentive 0 for 60 ticks, then incentive 1.4 for 60 | Whether bridge costs A, or incentive order does. This is the level map, the largest remaining loss. |
| epidemic | 155 | Fresh reset. Mask 0.85 for 120 ticks, then recovery for 35 | Whether masks fatigue on their own or only through closure. Release jump ≥ +0.28 vs ≤ +0.25. |
| wildlife | 150 | Continue R3 (copy to R3c). Joint .7 for 120 ticks, then release for 30 | The joint-box long-run level (v2 38/32 vs about 22?), whether predator depressions combine additively or max-type, and the release peak after long pulses. |
| power_grid | 110 | Fresh reset. Price 0 + reserve 150 at interconnector 1 for 60, interconnector 0.2 for 30, recovery for 20 | Whether frequency effects add or saturate at high load (v2 predicts 51.03), and the last charging (M2) question. |
| hospital_queue | 100 | Continue R4 at recovery for 50 (R4c), then R3 for 50 (R3c) | Whether the post-overload queue plateau of about 100 is real. v2 drains to 23; if real, add a stranded-backlog state. |
| supply_chain | 100 | Fresh reset. Orders 80 for 35 ticks, then add lead_time_buy 0.44 for 65 | The shape of rush's dose-response, which is unidentified without R4. |
| traffic | 100 | Fresh reset. B background (recovery + ramp 1 + toll 1.5) for 30, then signal 0.255 for 35, then signal 0.2025 for 35 | The green-capacity knee: v2 predicts flow_a 10.4 / 8.2. |
| reservoir | 100 | Two 50-step fresh runs: release 12, aeration 0, deep then shallow, 30 ticks each + 20 recovery | Whether a short anoxic pulse leaves any quality offset, and how the pool is cleared. |
| ad_auction | 200 | Fresh reset. Bid 1.5 / cap 100 / breadth .775 for 50, recovery 35, bid 5 / cap 20 / breadth .775 for 50, recovery 35 (170 + 30 settle) | Whether capacity binds, and the purchase cut under throttling. |
| market | 200 | Fresh reset. Tax 0.05 for 100 ticks, then add rate 0.1 for 100 | Whether the reset drain needs tax only or rate + tax. Would decide v1 vs v2 for market. |

## 5. Open issues (the biggest per system)

| System | Open issue |
|---|---|
| social_contagion | A's pulse-level map sits near 200 (data 164 at u.7) |
| epidemic | Beds under closure are too low; the child-contacts-home parameter is pinned |
| wildlife | Habitat level too high; hunting 7 settles at different levels depending on history |
| power_grid | Load ringing is still linear |
| hospital_queue | The recovery-tail plateau |
| supply_chain | The retail law |
| traffic | A's flow with a full queue |
| reservoir | The aeration exponent is pinned (a threshold?) |
| ad_auction | High-bid spend still +0.8σ |
| market | See §3 |


## 6. Public results of the round-2 upload (reported by the user, 2026-09-28)

The user uploaded the alternative ZIP, `submission-round2-alt-market-v2.zip`, so all ten systems are v2.

| System | v1 public | v2 public | Change |
|---|---:|---:|---:|
| wildlife | 0.6611 | 0.7535 | +0.092 |
| power_grid | 0.7418 | 0.7985 | +0.057 |
| hospital_queue | 0.6721 | 0.7241 | +0.052 |
| social_contagion | 0.6271 | 0.6780 | +0.051 |
| epidemic | 0.7201 | 0.7604 | +0.040 |
| market | 0.6838 | 0.7225 | +0.039 |
| ad_auction | 0.8786 | 0.8912 | +0.013 |
| supply_chain | 0.8447 | 0.8560 | +0.011 |
| traffic | 0.8335 | 0.8442 | +0.011 |
| reservoir | 0.8521 | 0.8584 | +0.006 |
| **mean** | **0.7465** | **0.7887** | **+0.042** |

**What this tells us:**

- Every system that won on the held-out test also won on public. The held-out protocol predicts the direction of the public change.
- The §3 argument for keeping market v1 was wrong: v2 gained +0.039. The run-A in-sample fit is not a proxy for the scorer.

## 7. Public A/B: 50/50 blend of v1 and v2 (2026-09-28 evening)

| System | v2 | Blend | Change |
|---|---:|---:|---:|
| ad_auction | 0.8912 | 0.8867 | −0.005 |
| epidemic | 0.7604 | 0.7522 | −0.008 |
| hospital_queue | 0.7241 | 0.7210 | −0.003 |
| market | 0.7225 | 0.7089 | −0.014 |
| power_grid | 0.7985 | 0.7744 | −0.024 |
| reservoir | 0.8584 | 0.8576 | −0.001 |
| social_contagion | 0.6780 | 0.6608 | −0.017 |
| supply_chain | 0.8560 | 0.8523 | −0.004 |
| traffic | 0.8442 | 0.8422 | −0.002 |
| wildlife | 0.7535 | 0.7333 | −0.020 |

**Result:** the blend loses in all ten systems, market included. v1 adds nothing, so v2 stays the base.

**Consequence:** the blend is now the latest public upload, so tonight's daily sweep scores it (public standings only). **Nothing has been uploaded to the Final tab yet.** Slots reset at Toronto midnight.
