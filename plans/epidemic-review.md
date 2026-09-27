# Epidemic review (Phase B, §6.2)

Reviewer: separate agent, 2026-09-27. Spent 0 steps. Budget: 945 of the 1,000 CAP is spent, so **55 steps
are left in reserve**.
Review artefacts are in `toronto26-participant-kit/fits/epidemic/review/`:
- `raw_R1.png` and `raw_R2.png`: cases in linear and log units, hospital load and controls, made before I read the plan.
- `fit_errors.png`: the 7 existing fits on R1 and R2, with errors in units of the scoring σ (8.34 cases, 4.19 beds).
- `longrun_4000.png`: the fits over 4,000 steps under 6 fixed or block schedules.
- Scripts: `plot_raw.py`, `eval_fits.py`, `longrun.py`, `screen_reserve.py` and `screen_reset.py`.

## 1. Independent behaviour list (written from the raw data before reading the plan)

| ID | Behaviour | Evidence |
|---|---|---|
| R1 | The reset transient is a whole epidemic wave. Cases go 114 → 502 by tick 23–24 → about 45 by tick 90 with no controls, growing about 9%/tick early on. The shape is the same in both runs (peak 502 at tick 24 vs 502 at tick 22), and cumulative cases over ticks 0–40 are equal (14,393 vs 14,386). | raw_R1/R2 |
| R2 | In the first two observations cases equal the initial reading (114.0, 114.0), then jump +19% in one tick. After that, growth *slows* from +19% to +7%/tick within 10 ticks, long before susceptibles are depleted. So the hidden E/I start is not on the growth eigenmode. | printout t = 0–11 |
| R3 | Hospital load first dips by 25–30% (37.7 → 26.9 and 44 → 31) with its minimum at tick 3–4, then rises. The admission pipeline starts empty. | raw plots |
| R4 | A hard bed ceiling at 155.2 (median; noise std 0.7). It holds about 45–50 ticks, well after the case peak (a waiting list drains), then hospital load decays about 5%/tick. | R1 22–71, 243–264; R2 21–64 |
| R5 | Hospital load lags cases by about 20 ticks (R2: case peak at 272, hospital peak at 293). The ratio H(t)/cases(t−20) is *not* constant: 0.64–0.98 in R1 and 0.61–0.97 in R2. | printout |
| R6 | Mask: after a 1-tick latency cases fall by 4–6%/tick for about 6 ticks, and the log slope changes by about −0.04/tick. On and off are log-symmetric (−0.34 / +0.40). u = 0.5 gives about half the effect (−0.16 / +0.18). A later mask pulse (R2 at 350) has the same size as the first (−0.33 vs −0.34). | table of 6-tick "jumps" (below) |
| R7 | Closure: no fast component either way. The 6-tick jumps are −0.06/+0.06 in R1 and +0.02/+0.05 in R2 (noise level), and only the slope changes, by about ±0.015. Cases kept rising for about 7 ticks after the closure at 225. | same table |
| R8 | Vaccination: no immediate effect. There is a slow decline (95 → 80 over 60 ticks in R1) that continues for about 10 ticks after vaccination stops, then reverses. During the capped first wave (R2 10–39) the effect is small at most: the R2/R1 case ratio drifts from 1.07 to 0.92, confounded by the different initial reading. | R1 315–434; R2 vs R1 0–40 |
| R9 | Resurgence after the reset wave, with and without restrictions. R1 goes 45 → 64 at 1.7%/tick with no controls. R2 goes from a floor of **15.5 at tick 89 under full mask+closure** up to **89, where it is flat at ticks 220–239 (log slope −0.0004/tick)**, still restricted. | raw_R2 |
| R10 | The release after the 200-tick joint hold gives a *smaller* fast jump (+0.31 in log) than releases after short restrictions (+0.40, +0.42, +0.40). This could be fatigue or a state effect. The fits show it does not discriminate: m23_all_quick has no fatigue and reproduces +0.33. | jump table |
| R11 | The restricted plateau (about 89 cases, R2 220–239) is about the same as the unrestricted post-wave level (80–100, R1 270–435). So the level after about 150+ ticks is roughly **insensitive to the restriction**. | raw plots |
| R12 | Adding closure to mask adds little to the fast drop (joint −0.37 vs mask −0.34). Closure's effect is slow and appears as a change in slope. | jump table |
| R13 | Under closure, hospital load rises relative to cases: the cap was reached at about 200 cases during the R1 closure but needed about 450 in wave 1. The R2 hospital decline slowed during the closure at 300–329. | raw plots |
| R14 | Noise is tiny and multiplicative: cases about 0.5% (diff2 estimate; the plan says 0.23%), hospital about 0.3%. Misfit dominates everything. | printout |

The 6-tick fast "jump" is log(c[s+6]) minus the value extrapolated from the pre-switch trend. It is computed by `eval_fits.py`, with the data jumps on the last line of its output.

| Switch | R1 120 mask on | R1 185 mask off (after 65) | R1 435 mask 0.5 | R1 495 joint on | R1 520 joint off (after 25) | R2 240 joint off (after 200) | R2 350 mask on | R2 380 mask off (after 30) | R1 225 / 270 closure | R2 300 / 330 closure |
|---|---|---|---|---|---|---|---|---|---|---|
| Data | −0.34 | +0.40 | −0.16 | −0.37 | +0.42 | **+0.31** | −0.33 | +0.40 | −0.06 / +0.06 | +0.02 / +0.05 |

## 2. Comparison with the catalogue, and model coverage

Fit quality comes from `eval_fits.py`: mean score 1/(1+|err|/σ) per run, cases/hospital.

| Fit | R1 | R2 | Note |
|---|---|---|---|
| base2_r1 | .72/.73 | .26/.32 | |
| m12_r1 | .79/.79 | .24/.27 | fitted on R1 only |
| m13_r1 | .79/.76 | .21/.26 | |
| m23_r1 | .73/.77 | .22/.31 | g3 = 28.6: **explosive** after the R2 lift (the fast jump is +2.71 in log) |
| m12_all_quick | .68/.63 | .53/.43 | |
| m13_all_quick | .67/.59 | .60/.49 | best on R2 |
| m23_all_quick | .59/.53 | .49/.46 | |

`fit_errors.png`: the R1 fits stay within about ±2σ on R1 but reach −8σ or worse on R2 from tick 50 onwards (the floor collapses to 1–5, and the rebound comes late and too big). The joint fits track R2 after tick 50 to within about ±3σ, but they miss the first-wave peak (330–440 vs 502, below −8σ) and lose the bed cap (Hcap drifted to 305–329, so hospital load reaches about 200).

| Behaviour (mine / catalogue) | Model component | Captured? |
|---|---|---|
| R1 / B1, B10 first wave | SEIRS, S0 | R1 fits: yes. Joint fits: **no** (peak −15 to −35%). The structure cannot fit the first wave and R9 at the same time. |
| R2 early growth-rate decay and flat first 2 ticks | E0 = c0/(K·sigE), I0 = rI·E0 | Partly: all fits show a +4σ spike at ticks 1–3. Low weight. |
| R3 / B3 hospital dip | P0 = fp·c0 (fp → 0) | Yes |
| R4 / B2 bed cap and queue | Hcap, Q, qab | R1 fits: yes. Joint fits: no, because Hcap was left free (plan item 4). |
| R5 / B17 hospital/case ratio varies across waves | none (single group) | **Not captured**, except the closure part (hc) |
| R6 / B5 mask fast, log-symmetric, linear | wm | Yes, in every fit |
| R7, R12 / B6, B16 closure slow, no jump | lag a_c, wc | Approximately. a_c is pinned at 1 in m12_all_quick, which contradicts R7. |
| R8 / B7 vaccination lagged and weak | m2 W-stage, ev, kappa | **Open**: a_m2 → 1 in 3 of 4 fits and kappa pinned at 0 |
| R9 / B8, B11 floor of 15.5, then recovery to 89 under restriction | only m1 fatigue in the joint fits | **Not captured** by any fit that also keeps R1/R4 |
| R10 / B12 smaller release jump after a long hold | falls out of the dynamics in all joint fits | Yes, but it does not discriminate between pairs |
| R11 plateau ≈ unrestricted level | nothing explicit | **Not captured** (not in the catalogue) |
| R13 / B4, B15 closure raises hospital/case | hc | Yes |
| R14 noise | NOISE = 0.01 (residual scale) | Fine |
| B9 damped endemic oscillation | SEIRS ω ≈ 0.017 | Yes over the observed window. It settles within about 600 ticks in every fit (longrun plot). |
| B13 vaccination during the capped wave has no effect | kappa | Open (kappa = 0) |
| B14 initial reading barely matters | reset rule | Yes (checked only at 114 and 124, near the bottom of the 100–240 range) |
| (neither list) extinction under sustained restriction | none; I → 0 is absorbing | **Not captured**, and it is a stability risk (G3) |

## 3. Probe and coverage audit (§4.2, §6.2 item 3)

- **M1/M3 separator** (long restriction and lift, R2 40–299): run ✓. It was evaluated qualitatively and by unconverged quick fits only. There is no converged pair comparison and no bootstrap yet.
- **M2 separator** (vaccination on/off, R1 315–434): run ✓, but it is one weak instance. m2 is switched off in 3 of the 4 fits that contain it, so it is **not effectively evaluated**. M2 can be neither confirmed nor excluded.
- **P9a** was run, but case counts were not matched (126 falling vs 75 rising), so closure and mask were not compared "at similar case counts". Recorded, but it was only a weak test.
- **P9b** was run in both orders, but the orders are confounded. "Before" fell in the capped first wave (the hospital cap throttles clinics, and S is high). "After" was only 25 ticks and overlapped the post-release rebound. The pair measures state rather than order.
- **P9c** (hospital recovery): hospital load was followed only for 20–60 ticks after each pulse. It did not settle after the R2 300–379 pulses.
- **P5 gap test: not run.** P6 is covered only through the confounded P9b.
- **Coverage gaps outside §4.2 that scored scenarios need:**
  - The **reference pulse with all three controls together** was never run.
  - Vaccination was never combined *simultaneously* with a restriction.
  - There were no mid-levels for closure or vaccination.
  - No intervention was applied during the first wave's growth phase (ticks 0–20). Every scored episode starts from a reset, and sustained-operation episodes presumably apply controls from tick 0.

## 4. Theses: missed drivers (§6.2 item 4)

- **M1 is only driven by the control level (fatigue).** The obvious alternative, a behavioural response to *risk*, is missing: contact reduction driven by a fading memory of hospital_load (or cases).
  - This would explain R11 (the level is insensitive to restrictions) and the floor at 15.5. When cases are low, people relax, so restrictions lose their bite.
  - It would also blunt the first-wave peak differently from fatigue.
  - The test is free: fit a variant m1b with `mult *= exp(-g·Hm/Hcap)`, where `Hm` is an EMA of H.
- **The throttling driver is H/Hcap.** The brief's "hospital pressure" more naturally means waiting-list pressure, the queue Q > 0, which occurs only at the cap. A queue-driven throttle `1/(1+kappa·Q/Hcap)` would explain B13 (no vaccination effect while capped) and leave vaccination at full strength elsewhere. The smooth H/Hcap form cannot do both, which is plausibly why kappa collapses to 0.
- **"Developing immunity" is read only as vaccine-derived.** Infection-derived immunity that develops with a lag (E/I → W-like stage → R) is an equally literal reading. It would change the post-wave refill timing (R9) without touching vaccination.
- **"Vaccination uses a shared clinic workforce."** Nothing models the workforce as shared with clinical referrals. If it is shared, vaccination would slow referrals, so hospital load dips during vaccination and catches up afterwards. The R1 hospital/case ratio fell from 0.74 to 0.66 during the 315–374 vaccination hold. This is weak evidence and worth one free fit term.
- **"School closure changes where contacts occur."** This means contacts are displaced, not removed. The single-group model implements closure as a β reduction plus a severity shift (hc). An age-structured model, with closure moving child contacts into households, would produce R5, R7, R12, R13 and possibly R9/R11 from one structure.
- Time since reset: there is nothing beyond the deterministic first wave, which is handled. All control recovery values are at a bound, so no side of any control is left untested. Both delay phrases have stages: the queue for referrals and the W stage for developing immunity.

## 5. Model code: stability over 4,000 steps (§6.2 item 7)

- **Extinction is absorbing.** Under a sustained pulse, mask, random or block schedule, `m12_r1` goes to exactly 0 cases and 0 hospital load for over 3,000 ticks, and `m13_r1` goes to 0–5 (see `longrun_4000.png`). The data contradict this: under a full 200-tick restriction cases never fell below 15.5. A zero forecast scores badly against any real level of about 50–90. The model needs an importation/seeding floor (for example `new += eps·S`) or a lower bound on I.
- **The long-run level under sustained restriction is the widest spread between fits**: 0 (R1 fits) vs 33–55 (joint fits) for the pulse schedule. The only data point is the R2 plateau of about 89 (with no vaccination). This level dominates the sustained-operation and joint scenario scores over 4,000 ticks, far more than the first wave does.
- Pinned parameters:
  - `S0` → 0.96–1
  - `ev` = 1
  - `kappa` → 0 (1e-12)
  - `fp` → 0
  - `a_c` = 1 (m12_all_quick)
  - `gF_m1` = 1 (m12_r1, m12_all_quick)
  - `a_m2` → 1
  - `g3` = 28.6 with `ain` = 0.0007 (m23_r1)

  Per lesson 9, the pinned gains stand in for missing structure. **Do not ship m23_r1**: its lift response is explosive.
- `Hcap` is free and drifts in the joint fits. Fix it at 155.2 (plan item 4 agrees).
- The queue Q is bounded only through qab. If qab → 0, a long capped period would keep hospital load at the cap indefinitely. Put a floor on qab, for example ≥ 0.005.
- Population fractions are conserved and clipped, so there is no overflow. The simulation takes 9 ms per 4,000 steps, so runtime is not a concern.

## 6. Gaps

| # | Severity | Gap | Evidence | Fix / test |
|---|---|---|---|---|
| G1 | **high** | The single-population SEIRS cannot fit the first wave (R1) and the restricted floor and recovery (R9) at the same time. No existing fit is usable across both runs. | fit_errors.png: R1 fits reach −8σ or worse on R2, and joint fits reach −8σ or worse on the first wave | Build a 2–3-group SEIRS. Closure should cut child–child contacts and shift part of them to households. Give each group its own severity (this replaces hc and explains R5/B17). Share β-multipliers for masks. Then refit the pairs on this core with `--fix Hcap`. |
| G2 | **high** | The long-run level under sustained controls is unconstrained. Fits range from 0 to 55 under the pulse; the data show a plateau of about 89 after 200 restricted ticks (R11). This dominates the 4,000-step scores. | longrun_4000.png; R2 220–239 slope ≈ 0 | Require the chosen model to reproduce the plateau at 89 under restriction *and* 80–100 unrestricted. Report each candidate's 4,000-step equilibrium for recovery, pulse, mask only and 0.5 levels in the plan. If candidates disagree by more than 2σ, prefer the one whose restricted equilibrium is close to the unrestricted one (the data say so). |
| G3 | **high** | Absorbing extinction: forecasts go to 0 for thousands of ticks. | longrun: m12_r1 and m13_r1 under pulse, mask, rand and blocks | Add an importation term (fitted or small fixed) or a floor on I. Add a gate: under any sustained schedule, the predicted cases after tick 1,000 stay ≥ 5. |
| G4 | medium | The M1 thesis is missing the risk-driven behaviour driver (hospital/case memory). The existing m1 fits "succeed" only through pinned gF and a near-integrator memory. | §4; plan §8 | Fit an m1b variant driven by an EMA of H (free, no steps) in both pairs that contain m1. Compare the cross-run score (R1 → R2). |
| G5 | medium | Vaccination is effectively unidentified. a_m2 → 1, kappa → 0, and there is only one weak on/off instance, so M2 can be neither accepted nor rejected. The P9b pair is confounded by state. | plan §8/§10; R8 | Try a queue-driven throttle (Q > 0 only at the cap) and infection-derived developing immunity. If m2 still collapses, treat pairs containing m2 as "not identifiable" rather than rejected. |
| G6 | medium | The all-three reference pulse, vaccination combined with a restriction, and any control during the first wave's growth phase were never observed. Recovery-spacing and joint scenarios use exactly these. | coverage audit §3 | See the reserve recommendation below. Otherwise rely on multiplicative composition, which is supported for mask+closure (R12). |
| G7 | medium | The quick joint fits are unconverged (nfev small, one pass), and there is no bootstrap or confusion matrix yet, so the pair decision has no basis. | plan §10 | Run §6.3 after G1–G3. Use interior starting values, not values at sigmoid limits. |
| G8 | low | P9a was not at matched case counts, and P9c's hospital recovery holds were short. Neither was evaluated quantitatively. | §3 | Evaluate from the G1 model's residuals over R2 300–399. No new data is needed. |
| G9 | low | Early transient: the first 2 ticks are flat, then +19%, with growth decaying faster than the fits produce (a +4σ spike at ticks 1–3). The initial reading was tested only at 114 and 124 (the range is 100–240). | fit_errors.png | Free parameters for the E0/I0 split (already rI). Check the peak timing extrapolated to c0 = 240 for plausibility (it should be earlier by at most about 5 ticks). |
| G10 | low | A shared clinic workforce may couple vaccination to referrals. | R1 315–374 hospital/case ratio fell from 0.74 to 0.66 | One optional term, `referrals *= 1 − s·u_v`. Keep it only if the R1 → R2 score improves. |

## 7. Reserve (55 steps): recommendation

- **Do not spend before G1–G3 are addressed.** The current fits disagree by about 2–4σ even on a plain recovery continuation, so screening reserve probes through them ranks baseline misfit, not mechanisms. With `screen_reserve.py`, "rec 55" alone scores 2.4σ of pairwise disagreement, more than most probes. The biggest gap (G2, long-run level) cannot be reached with 55 steps from a reset.
- **If the modeler still has an unresolved gap after G1–G3, spend the full 55 on one fresh reset:**
  - **Schedule:** `school_closure = 1.0, mask_mandate = 0, vaccination_rate = 0` from tick 0 for 55 steps.
  - **Why this is the best use of 55 steps:**
    - The first wave is deterministic (R1/R2 agree), so R1 and R2 are a free, model-free control.
    - Closure is the least understood control. Among the existing fits, closure from reset has the largest disagreement of the from-reset candidates (5.2σ; `screen_reset.py`), and its signature distinguishes the age-structure hypothesis of G1: does early closure lower the peak and raise the hospital/case ratio?
    - The first wave appears in every scored episode.
  - **Second choice:** the reference-like pulse at 0.85 on all three controls from tick 0 for 55 steps. It covers G6 (all-three composition during the first wave) and gives clean vaccination-at-low-hospital-load information for G5 in ticks 0–20.
  - Record the spend in the plan's spend log. The run needs no P0, because the reset wave is the control.
