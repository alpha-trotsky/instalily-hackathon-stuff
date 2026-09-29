# Round 3: runs, held-out v2 results and verdicts (2026-09-29)

All 1,335 reserve steps are spent. Every system's budget is 0. Raw data is in `toronto26-participant-kit/data/<system>/`, and segment files are in `KIT/fits/round3/segments/`.

**Held-out scoring.** `python fits/round3/heldout3.py SYSTEM [--model FOLDER] [--files ...] [--segs]`
- σ = 0.1 × std after tick 20 of all data, including round 3. It is fixed for every round-3 comparison.
- The continuation files (hospital R4c, wildlife R4c) are scored on their new ticks only (350+).
- The shipped v2 results are in `KIT/fits/round3/v2_on_r3_<system>.json`.

**Continuations.** Only the latest run per system is still live. hospital R3c and wildlife R3c were refused with 404 and cost 0 steps. The fallbacks used:
- hospital: R4c, recovery for 100 ticks;
- wildlife: R4c, joint 0.7 for 120 ticks, then release for 30.

**Earlier public lessons still apply:**
- Only the leave-one-out test (B) predicted public scores. Test (A) and in-sample fits misled us three times: market v1, epidemic old-only, social ratchet.
- Blending v1 with v2 lost in every system.
- Data from new regimes carried a lot of public score: the epidemic fit on old runs only lost 0.055.

## Per system: run, shipped v2 held out, verdict

Cells are last-10-tick means (data vs v2). err is (v2 − data)/σ.

### social_contagion R6 (fresh reset)
- **Run:** seeding 6.3 + bridge 0.42, incentive 0, for 60 ticks; then incentive 1.4 added, for 60.
- **v2 held-out score:** 0.499 (A 0.629, B 0.368).
- **Segment 1 (ticks 50–59):** A 155.3 vs v2 161.0 (+1.0σ); B 89.3 vs 82.1 (−2.4σ).
  - **Verdict:** the bridge costs A beyond its effort share, and v2 already has that.
- **Segment 2:** A 196.2 vs 194.7; B 136.5 vs 120.9 (**−5.3σ**).
  - A peaks at about 200 around tick 90–100, then slowly declines (195 at tick 117, about −0.3/tick). B is flat at 136.
  - The same action from reset with incentive on from tick 0 (R4 0–99) gave **164 / 101**.
  - **Verdict:** order effect. Incentive added after recruitment gives +32 A and +35 B over incentive given with recruitment.
    - Part of the A gain may be transient: it is declining at the end. B is clearly higher.
    - v2 is history-free. It is right here by accident and wrong for R4, and it misses B's incentive response.

### hospital_queue R4c (continuation of R4, recovery, ticks 350–449)
- **v2 held-out score:** 0.211 (wait 0.023, queue 0.233, discharges 0.376).
- **Data:**
  - wait keeps rising at about 1/tick, 170 → **238 at tick ~420**, then **collapses** (207 at 447);
  - queue drains slowly, 100 → 91.5 (about 0.09/tick);
  - discharges 11.07, below the arrival rate of 11.49.
- **v2:** wait 0, queue 23, discharges 11.5 (errors −45σ, −6σ, +1σ).
- **Verdict:** a finite stranded cohort exists after long overloads. It is admitted at a trickle and its age keeps growing. The cohort is exhausted around 70 ticks into this segment, when the wait peaks and starts to collapse.
  - The queue plateau (~90–100) outlives it and drains at τ ≈ 1,000.
  - R1's tail after a similar pulse showed no wait jump. The trigger is still open.
  - Needed: a stranded/residual pool with a slow drain, plus a FIFO age that is reported for the admitted stranded patients.

### market D (fresh reset)
- **Run:** tax 0.05 alone for 80 ticks, then rate 0.1 + tax 0.05 for 120.
- **v2 held-out score:** 0.231 (price 0.28, volume 0.19, depth 0.22).
- **Segment 1 (tax alone from reset):**
  - depth settles at **41.9**, with no drain (v2 48.8, +2.9σ);
  - price is flat at about **94.7** from tick 0 (v2 90.4, −5.1σ);
  - volume 1.82 (v2 1.71).
  - **Verdict:** the drain needs the rate, and tax alone is just the static depth curve. Tax from reset *blocks the price relaxation*: price stays near 95.
- **Segment 2 (rate added at tick 80):**
  - depth drains steadily, 41.9 → **22.1 at tick 197, still falling** about 0.15/tick (v2 16.7);
  - price 94.6 → **82.8**, still falling about 0.06/tick (v2 86.5, +4.3σ);
  - volume rises to 2.72, then falls to 2.36 (v2 2.80, **+11σ**).
  - **Verdict:** the drain is rate × (inventory locked since reset under tax), and it is **not reset-specific**: it starts 80 ticks in. In B, the joint pulse after a recovery (B 475) had no drain, which fits funding cleared in recovery.
  - v2's drain is too fast and too deep, and its volume is too high.

### epidemic R6 (fresh reset)
- **Run:** mask 0.85 for 120 ticks, then recovery for 35.
- **v2 held-out score:** 0.489 (cases 0.50, beds 0.48).
- **Segment 1 (ticks 110–119):** cases 43.2 vs 50.1 (+0.8σ); beds 40.6 vs 48.3 (**+1.8σ**).
  - First wave: peak about 264 near tick 25, down to 45 by tick 100, then flat (no creep).
- **Release jump over 6 ticks:** ln(60.1/43.3) = **+0.33 ≥ +0.29**, the pre-registered threshold.
  - **Verdict: no mask-driven fatigue.** A long mask hold keeps its full effect. v2's mix_m1 of about 0.5 (partly mask-driven fatigue) should move towards closure-only fatigue (mix → 1).
- **End of recovery:** 133 / 59.6 vs v2 142 / 66.3 (+1.1σ / +1.5σ).
- **Overall:** v2 is too high on beds under masks.

### wildlife R4c (continuation of R4)
- **Run:** joint 0.7 (hunting 4.9, habitat 0.37, corridor 0.7) for ticks 350–469, then recovery for 470–499.
- **v2 held-out score:** 0.425 (prey N 0.49, predators N 0.25, prey S 0.59, predators S 0.37).
- **Joint hold, prey:** 21.6 / 19.7 vs v2 26.3 / 22.7 (+1.0σ / +0.7σ).
  - Prey settle near the R3 asymptote (about 22/23), which answers "is it set by the controls?" with yes.
- **Joint hold, predators:** **1.857 / 1.830** vs v2 1.748 / 1.748 (−2.1σ / −1.7σ).
  - That lies between additive (1.75) and max-type (1.93). The composition is sub-additive: predator depressions partly overlap.
- **Release peak:** 154 / 136 vs v2 150.5 / 139.8. Close to v2, and larger than R3's 133/110 after a 60-tick pulse, so the boom grows with pulse length.

### power_grid R5 (fresh reset)
- **Run:** price 0 + reserve 150 + charging 1 + interconnector 1 for 60 ticks; then interconnector 0.2 for 30; then recovery for 20.
- **v2 held-out score:** 0.378 (load 0.44, **frequency 0.16**, share 0.54).
- **Segment A:** frequency **51.37** vs v2 51.03 (−4.5σ).
  - It is *above* the additive static map (51.15), so it does not saturate. The reserve effect at high load is stronger than v2's.
- **Segment B (interconnector 0.2):** frequency **49.77** vs v2 50.21 (+5.9σ).
  - The interconnector effect under reserve at high load is about 1.6 Hz, much stronger than v2's. v2's kx → 0 was pinned the wrong way.
  - Against R4 joint 1 (50.11, charging 0) at matched load, charging 1 gives −0.34, which is > 2σ. **The charging (M2) loophole may reopen**; check it against the interconnector interaction first.
- **Segment C (recovery):** load trough 64.3 (the floor holds); frequency 50.80 vs 51.02; share 0.43 vs 0.41.

### supply_chain R6 (fresh reset)
- **Run:** orders 80 with lead_time_buy 0.44 for 50 ticks, then lead_time_buy 0.32 for 50 (everything else at recovery, receiving 1.5).
- **v2 held-out score:** 0.451 (shipments 0.38, supplier 0.58, retail 0.40).
- **Shipments:**
  - lead 0.44: **31.0** vs v2 31.5 (−11% vs the 34.8 base; OK);
  - lead 0.32: **24.0** vs v2 29.9 (**+5.4σ**), a slow move over about 30 ticks.
  - With R1's lead 0.2 → 22.5, the rush dose-response is −11% / −31% / −35% at 0.44 / 0.32 / 0.2: a steep knee between 0.44 and 0.32.
- **Stocks at lead 0.32:** supplier 334 vs 265 (−5.6σ); retail **103 vs 428 (+9.3σ)**. Retail drains when shipments fall, and v2 keeps it high. This is the retail law again.

### traffic R6 (fresh reset)
- **Run:** background B (signal 0.5, lane 0, toll 1.5, ramp 1, freight 0.5, clearance 1) for 30 ticks; then B + signal 0.255 for 35; then B + signal 0.2025 for 35.
- **v2 held-out score:** 0.432 (flow_a 0.28, flow_b 0.27, speed_a 0.48, speed_b 0.69).
- **flow_a:** **18.6 and 18.6** (≈ 21 at the end) vs v2 10.2 / 8.2 (**−9σ / −11σ**).
  - **Verdict H2:** green share alone does *not* cut A's capacity down to 0.20. The u = 0.7/0.85 drop on the ray comes from lane closure, clearance or freight moving with it.
  - v2's knee (kg = 74.9 per unit of green) is wrong and must be moved onto the other controls.
- **flow_b:** 11.7 / 12.7 vs 10.6. **speed_a:** 11.6 / 9.0 vs 8.8 / 7.8.
- **Replicate:** segment 1 vs R5 ticks 0–29 is for a burst-determinism check (not yet done).

### reservoir R6XD / R7XS (two fresh resets)
- **Runs:** release 12, aeration 0, depth 1 (XD) or depth 0 (XS) for 30 ticks, then recovery for 20.
- **v2 held-out score:** 0.689 (quality 0.31 / 0.25; the water side is fine at 0.89–0.93).
- **Quality plateau (ticks 40–49):** XD **0.950**, XS **0.955**; v2 0.947 / 0.946 (−3σ / **−8.5σ**; σ(quality) = 0.001).
  - A short anoxic pulse leaves **no offset** below 0.950. The shallow pulse ends *higher* than the deep one.
  - The decision table row "XD < XS" says deep withdrawal lowers later surface quality (sign flip on the depth term). Also, v2's post-pulse quality is too low in general.

### ad_auction R5 (fresh reset, bid / cap / breadth)
- **Run:**
  - 1.5 / 100 / 0.775 for 50 ticks;
  - recovery for 35;
  - 5 / 20 / 0.775 for 50;
  - recovery for 65.
- **v2 held-out score:** 0.530 (win 0.57, spend 0.65, conversions 0.37).
- **Segment 1:** conversions **5.05 vs v2 4.36 (−5.7σ)**. Spend 20.0 vs 21.1; win 0.236 vs 0.239.
  - A rested broad start converts more than v2 allows. The capacity plateau from rest is higher, or the fatigue is too strong early on.
- **Segment 3 (throttled):** conversions 3.03 vs 3.06 ✓. Win **0.165** vs 0.191 (+1.7σ). The throttle cuts purchases proportionally, as v2 has it.
- **Segment 4 (recovery):** fine (≤ 1.1σ). There is no win undershoot below 0.25.
