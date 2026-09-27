# Overnight report (2026-09-27)

All nine systems have a tested gray-box forecaster and a submission ZIP, and so does market (unchanged). Nothing was uploaded. Every system stayed within its cap: 945–1,000 steps for the 3–4-control systems and 1,300 for the 6-control systems. Market was not touched.

## What to do first

1. **Upload `toronto26-participant-kit/submission-overnight-all.zip`** (all ten folders at the ZIP root, verified end to end). Alternatively, upload the per-system ZIPs one at a time. Remember each system gets 3 accepted uploads per Toronto day, shared between the public and final phases.
2. **Compare public scores with the local cross-run scores below.** Market's public score (0.68) was close to its local σ = 0.1×std estimate. A system that falls far below its local score has a structural problem to look at first. The weakest local margins over persistence are social_contagion (0.255 vs 0.223) and hospital_queue (0.541 vs 0.312). supply_chain and traffic ship base-only models.
3. **Fallback swaps if a public score disappoints** (the parameter files already exist):
   - power_grid: m1 alone (`fits/power_grid/v1/m1_all.json`);
   - social_contagion: M2+M3;
   - epidemic: the no-mechanism fit, which scored best on the Run-1 → Run-2 test.
4. **Unspent budget:** only epidemic's 55-step reserve is left inside its cap. Every other system is at its cap. The account still holds 700–1,055 steps per system outside the caps. Spending them needs your go-ahead.

## Per-system summary

The score columns show the model fitted on Run 1 and scored on Run 2 (or its continuation), with σ = 0.1×std after tick 20. Every shipped model was then refitted on all data.

| System | Steps spent / remaining | Model shipped | Confidence | Model (R1→R2) | Persistence | Gates | ZIP |
|---|---|---|---|---:|---:|---|---|
| epidemic | 945 / 1,055 | 3-age-group SEIR-like model, m1+m3 (behaviour fatigue + postponed gatherings) | unresolved (the bootstrap refits did not converge) | 0.344 (0.75/0.73 in-sample) | 0.168 | all pass | `submission-epidemic-v1.zip` |
| wildlife | 1,000 / 1,000 | two-region food → prey → predator model, food renewal + nursery (mA+mB) | unresolved (real margin is about ½ the smallest bootstrap margin) | 0.417 | 0.066 | all pass; no extinction or cycles in 100 constant settings | `submission-wildlife-v1.zip` |
| ad_auction | 1,000 / 1,000 | audience rings + pacing + fulfillment queue, M2+M3 (fatigue + broad priming, τ₃ fixed at 200) | accepted by the bootstrap rule, but pinned parameters remain | 0.391 | 0.107 | all pass | `submission-ad_auction-v1.zip` |
| social_contagion | 1,000 / 1,000 | two communities with a core population and a bridge lag, M1+M2 (credibility + expectations) | medium (bootstrap 5/5 and 3/5) | 0.255 | 0.223 | all pass | `submission-social_contagion-v1.zip` |
| power_grid | 1,000 / 1,000 | synchronised cooling + share/frequency structure, m1+m3 | moderate (~65%): M2 ruled out by a direct charging test | 0.439 | 0.175 | all pass | `submission-power_grid-v1.zip` |
| reservoir | 1,000 / 1,000 | stock + seasonal inflow (P = 67.7547) + groundwater heads, M1+M3 | M1 high; M3 vs M2 unresolved | 0.533 | 0.083 | all pass | `submission-reservoir-v1.zip` |
| traffic | 1,300 / 700 | revised two-route base, no mechanisms | not identifiable (the pairs never beat the base; an optimizer limit) | 0.266 base (R3: 0.530) | 0.058 | contract and range checks pass; 75 sawtooth flags accepted (only under per-tick random controls) | `submission-traffic-v1.zip` |
| supply_chain | 1,300 / 700 | bounded pipeline base with rework loop, no mechanisms | not identifiable | 0.464 | 0.137 | contract and range checks pass (50.8 s for 40 episodes); 61 sawtooth flags accepted (rework-loop echoes that die out) | `submission-supply_chain-v1.zip` |
| hospital_queue | 1,300 / 700 | queue/service model with deterioration and a long-stay pool, m1+m2 (fatigue + handover) | moderate (M3 rejected on three follow-up nulls) | 0.541 | 0.312 | all pass | `submission-hospital_queue-v1.zip` |
| market | 600 / 1,400 (untouched) | M1+M2 (v1, public 0.6838) | — | — | — | — | `submission-market-v1.zip` |

All ZIPs are in `toronto26-participant-kit/`. Each was built by `greybox/common/package.py`, which re-runs the contract check from an extracted copy and scans for credential values.

## Top 3 open issues per system

**epidemic**
1. Fits stop at the evaluation limit and restarts differ 2× in cost, so the pair choice is weakly supported. The Run-1-only no-mechanism fit scored best in the cross-run test (0.410).
2. School closure is poorly pinned (parameters at their limits). The 55-step reserve could go to closure at 1.0 from a fresh reset.
3. Never observed: all three controls together, and controls during the first wave's growth phase.

**wildlife**
1. The pause about 18 ticks into regrowth and the following peak are missed. The juvenile delay and its starting state are pinned at their limits.
2. Worst stretch: R2 ticks 120–250, the regrowth bump early in the long hunting hold.
3. Fits used a single restart, and only 2 bootstrap draws were run.

**ad_auction**
1. The conversions bump and dip after bid steps (τ ≈ 15–20) are not captured, nor is the plateau and drop in the long hold.
2. The slow memories (M3 τ = 200 set by hand, M2 τ ≈ 150) have not been checked beyond 455 ticks.
3. The reset win_rate transient is wrong (0.05 vs 0.147). Bid between 0 and 1.5 and cap below 20 were never tested.

**social_contagion**
1. The long-run recovery level (96.5 / 83.7) dominates 4,000-step scoring and is extrapolated. No run held recovery for more than 100 ticks.
2. Mid-level controls, seeding + incentive at bridge 0, and bridge values between 0.6 and 1.0 are untested.
3. M1 vs M3 is only moderately resolved.

**power_grid**
1. Frequency is weak (0.285 vs 0.251 for persistence): the dip after reserve release is missed, and the secondary-control gain is at its limit.
2. Load ringing is under-predicted, and its period at price 0 is wrong (~67 vs ~50 ticks).
3. Middle reserve levels and prices above 1.5 were never observed. M3 has no signature of its own.

**reservoir**
1. The groundwater excess under a sustained pulse is under-predicted (0.1 vs 0.25–0.55), up to about 2σ on inflow.
2. Quality misses the overshoot after a reset and a +0.005 recovery offset. The scoring σ for quality is about 0.001, so these are costly.
3. The level forecast fitted on Run 1 alone got worse with the new groundwater terms (0.53 vs 0.78). They need all three runs to be determined.

**traffic**
1. Flow bursts from a feedback oscillation appear under fast-switching schedules. The output is smooth under held settings and on the real data (checked: 0.14/tick vs 2.0 in the data; smoothing the output does not raise the score).
2. Pairs lose to the base only because of the optimizer. A staged fit with the base frozen and more restarts is needed before any mechanism can be selected.
3. Route B's speed at the end of the long hold is off by about +4. Not modelled: the slow speed fall at zero demand, the dead time at toll 0, where lane closure acts, and the freight-priority-0 side.

**supply_chain**
1. Shipments at orders 80 are 31.7 against 34.8 (about −2.5σ on every sustained tick), so long-run retail is 781 against about 975.
2. The release burst after orders stop is missed. At production effort 0 the model stops production, while the data show the supplier refilling to its cap.
3. No module captures the step down about 88 ticks after maintenance stops, or the slower second drawdown, so the mechanism pair is undecided.

**hospital_queue**
1. Discharges under electives are 8–13σ too low, the largest remaining error. The likely fix is separate capacity per patient class.
2. The long-stay pool grows toward about 88 under long elective holds; only about 11.5 was observed.
3. The crash after the diagnostic-allocation switch is not captured. The fatigue build-up rate is at its limit.

## Process notes

- **Tooling bug (fixed mid-run):** `greybox/common/core.py` `params_for` let `--init` values override disabled modules, so a fit started from another pair's parameters kept that pair's modules switched on.
  - The fix was made after power_grid.
  - An audit found all shipped `params.json` files clean: every disabled module sits exactly at its off values.
  - The rival-pair costs recorded for epidemic, wildlife and ad_auction may still have been affected.
- **Other tooling changes:** `package.py`'s default data pattern now skips `*_battery.json`. `bootstrap.py` gained an opt-in `--warm`.
- **Interruptions:** three API usage limits interrupted agents (about 01:30, 02:50–06:30 and 10:50–12:40 Toronto). Every paid step had already been saved. Agents were relaunched as resumes, and no data was lost or re-collected.
- **Reserve runs:** the extra probes were written to copies (`R2c.json`) or new runs (`R3.json`). The original run files were never modified.
- **Where the details are:** each system's full record is in `plans/<system>-plan.md` (dossier, theses, separation table, spend log, catalogue, review responses, model selection, hand-off), with the independent reviews in `plans/<system>-review.md`. The running log is `plans/overnight-status.md`.
- `submission-overnight-interim.zip` was a safety bundle built mid-run. It is superseded by `submission-overnight-all.zip`.
