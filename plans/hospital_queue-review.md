# hospital_queue review (Phase B reviewer, 2026-09-27)

I spent no steps. The budget is 1,250 of CAP 1,300 spent, leaving a reserve of 50.
Files are under `toronto26-participant-kit/fits/hospital_queue/review/`:

- `refit.py` is the converged refit driver. It uses the same `Problem`/residuals as `greybox.common.fit`, with `diff_step` 1e-2 then 1e-3 in repeated rounds.
- `eval_review.py` produces per-window errors in score-σ units and the plots.
- The fits are `*_all*.json` and the logs are `*.log`.
- The plots are `R1_base_m2_m12_m23.png`, `R2_base_m2_m12_m23.png`, `R*_oldbase_basefree_base.png` and `R*_base_r1c_m12_r1.png`.

Score σ (0.1×std after tick 20, both runs): wait 2.87, queue 11.6, discharges 0.447.

## 1. Independent behaviour list (written before reading the plan)

- **R1 Recovery equilibrium.** Queue 23.0, discharges 11.49 (= arrivals) and wait 0. It is the same in both runs and after every full drain. Noise in this state is tiny: queue about 0.17 and discharges about 0.06.
- **R2 Reset transient.** Discharges are 0 for 2 ticks (2-tick service pipeline), then bursts of 18/7.5/24/18/15/20/15. The queue peaks at 59 at tick 2 and reaches 23 by tick 9. That clears about 16.7 patients per tick, far above the capacity seen at staffing 20 with an aged backlog (R4).
- **R3 wait_time is a filtered estimate.** In both runs it decays geometrically (×0.885 per tick) once nobody waits, from the reset and after the R2 drain. Under load it lags the queue by about 10 ticks.
- **R4 Recovery is critically loaded.** At staffing 20 with a backlog, discharges are 11.3–11.9 (R1 205–240 and 620–750). That is 0–3 % above the 11.49 arrivals. Backlogs therefore drain mainly through leaving: about 1.6 %/tick at 250 waiting and about 0.8 %/tick at 80 waiting. After a large load the tail lasts hundreds of ticks (R1: queue 99 at 170 ticks after release). This is the main 4,000-step effect, and the base captures it (see table).
- **R5 Staffing cut vs restore asymmetry.** The cut takes effect at once (2.6 = about 5/20 of capacity). After a restore, capacity ramps over 25–50 ticks: R1 175 gives 8.1, 9.4, 10.5, 11.4 (10-tick means), and R1 580 gives 5.5, 8.3, 9.3, 11.1. R2 350 (12.5 → 20 plus overtime) starts at 12.4, which matches 12.5 effective staff, and ramps to 23.6 over about 25 ticks. R1 240 (overtime alone, 65 ticks after the restore) jumps to 23.5 at once. This is the handover signature.
- **R6 Overtime about doubles capacity at recovery and adds about 50 % under electives.** The jump is immediate. There is no fade within 40-tick holds and no undershoot after R1's 30-tick overtime on E (8.85 before, 8.7 after). In R2 there is a possible slow capacity loss:
  - L before overtime: 6.3 → 7.2.
  - Spaced overtime, off phases: 6.1, 6.2, 5.6, 5.1.
  - After the block: 5.3 → 5.8, recovering.
  - This is confounded with the queue creeping up (263 → 313) under electives.
- **R7 Electives flood the system to a ceiling of 270–330** within about 11 ticks. The ceiling creeps upward and depends on the configuration (after diagnostic 0.75 it is about 320).
- **R8 Diagnostic allocation is non-monotone.**
  - 0.75 on E: discharges 9.7 → 4.9.
  - Back to 0.4: 8.8 within 5–10 ticks, with no crash.
  - 0.1 on L: discharges rise **gradually** (5.6, 7.6, 5.7, 7.0, 7.5 … 9.3 after about 20 ticks), and the queue drains from 310 to 168. About 140 of the "queue" were patients inside service stages.
  - Back to 0.4 in R2: discharges crash to 2–3 for about 15–20 ticks. That is far longer than the 2-tick pipeline delay seen at reset. Pipeline refill alone does not explain 15–20 ticks, so a reassignment handover dip is plausible (P9b's intended signature).
- **R9 Follow-up has no effect of any kind.**
  - E (R1 500–530): discharges 8.8 → 8.8.
  - Recovery (R2 30–110): 11.49 ± 0.015.
  - After a burst (R2 380–455): nothing.
  - So there is no capacity cost and no returns within 120 ticks.
- **R10 Urgent priority** makes no visible difference except a slightly flatter wait trend.
- **R11 Quantised long-stay residual after the fast (overtime) drain in R2.** The queue sits at 49.5 with wait 0 and discharges exactly 11.5, so about 26 extra patients are inside services and nobody is waiting. It then drops in single quanta: −11.6 at tick 427, where discharges exceed 11.5 by the same 11.5 (conservation holds, so nobody left), and −3.4 at tick 451. It sits at 34.5 until tick 500. The end of R1 shows similar drops (696–702 and 722–729) on top of a waiting backlog, and period-2 alternation of discharges (10.65/11.5). This looks like cohorts of heavy-work patients, probably deteriorated or elective patients admitted during the drain, finishing together.
- **R12 Discharges under load are bursty,** ranging 0–18 per tick (σ about 2). That is 4–5× the score σ of 0.45, so a smooth mean is the right target. Queue noise is about 0.7 % of level.

## 2. Comparison with the catalogue, and fit evidence

Converged refits on **R1+R2 jointly** use `refit.py`, with A0 = 11.5, kmu = 0.65 and nsv = 2 fixed (as the plan intended).

The original `fit.py` runs stop after 6–30 evaluations: a finite-difference step of 1e-8 against the soft-min and clip kinks. Its base on both runs had cost 25,718. With a larger diff_step and repeated rounds it reaches 21,025.

**Model costs (R1+R2, linear, σ 1/3/1):**

| Fit | Cost | Δ vs base | Train score R1 / R2 | Key params |
|---|---:|---:|---|---|
| base (wf free), `base_fx` | 21,153 | +128 | 0.473 / 0.548 | **wf 0.44** (local minimum) |
| **base (wf = 0)**, `base_fx_wf0b` | **21,025** | 0 | 0.458 / 0.543 | we 2.4, θ 0.013, Wmax 205 |
| m1 | 20,828 | −197 | – | g1 0.13, a1u 0.028, a1d 0.038 |
| m2 | 20,259 | −766 | 0.479 / 0.538 | g2 0.35, a2 0.052 (τ ≈ 19), **k2d → 0** |
| **m1+m2**, `m12_all_b` | **20,192** | −833 | 0.480 / 0.539 | g1 **0.048**, a1u 0.017, a1d 0.018; g2 0.38, a2 0.050, k2d 0 |
| m2+m3 | 20,223 | −802 | 0.481 / 0.535 | **Pc 1.4e5, a3 0.0008, wr 79**: absurd; a slow mix hack, like the R1 m23 |
| m1+m3 | 20,561 | −464 | – | wr −6.6 (unphysical), a3 0.002 |
| (first m12 attempt from SPEC init) | 20,482 | – | – | worse than m2 alone → the optimizer is still start-dependent |

**Reading:**

- M2 is the only module worth a lot (−766). M1 adds only 67, as a 5 % capacity loss with τ ≈ 57 ticks.
- m23 is 31 cost worse than m12 and gets there only through absurd m3 parameters (lesson 9).
- So **m1+m2 is favoured.** The deciding evidence is the two direct M3 nulls (R9), not the cost margin, which is tiny.
- The base misfit (about 20,000) dwarfs every mechanism term, so the pair ranking is not yet meaningful (lesson 6). The table below shows why.

| Behaviour (mine / catalogue) | Captured? | Evidence (score-σ mean \|err\|, m12_all_b) |
|---|---|---|
| R1 / B2 equilibrium | yes (base) | R2 30–110: 0.1/0.2/0.4 |
| R2 / B1, B20 reset transient | **not captured** | The model queue decays 60 → 23 over about 55 ticks; the data does it in 8. R1 0–60 queue error 1.1σ, discharges 3.6σ. |
| R3 / B3 wait filter | partly | Staffing 5: model 65 vs data 97 (5.7σ over 60–240). Wait is 4–6σ off in the R2 diagnostic windows. |
| R4 / B6, B13 critical recovery and long tail | **yes (base)** | R1 580–750 queue 0.3σ. After a 100-tick pulse at u = 0.85, the model returns to 23 by about tick 500. |
| R5 / B5, B17 slow restore | yes (m2) | R1 175–240 discharges 5.4σ (base) → 3.8σ (m2) |
| R6 / B7, B16 overtime and fatigue | gain yes; fatigue weak (m1, g1 0.05) | overtime on E: model 11.2 vs data 13.8 |
| R7 / B8, B12 elective flood and ceiling | queue yes, **discharges no** | E discharges: model 4.7 vs data 9.7 (**11.7σ**, R1 310–350; 8.5–9.6σ through 470). L: 8.4σ. |
| R8 / B9, B18 diagnostic allocation | **not captured** | R2 290–350: wait 4–6.5σ, queue 2–3σ, discharges 5–7σ. The converged base now gets the right sign at d = 0.1 (queue 310 → 225, data 168), but not the size, the gradual onset or the 15–20 tick crash. k2d → 0 in every fit. |
| R9 / B11, B15 follow-up null | **only with wf fixed at 0** | The R1-only fits (in use) have wf = 0.36–0.40, so follow-up 0 raises capacity 1.6×. The R2 tick-30 spike in `R2_base_r1c_m12_r1.png` is a pure artifact. |
| R10 / B10 urgent | small (wu) | – |
| R11 / B19 quantised long-stay residual | **not captured** | R2 380–500 queue 0.3–0.8σ (model 23 vs data 34.5–49.5) |
| R12 / B14 bursty discharges | n/a (smooth target) | – |

## 3. Probes, P9 and coverage (§4.2)

- P0 was run in both runs. Every control got a P1; the urgent and follow-up off-steps are only inside the all-controls release. P2 used staffing 0.5, and P3 used staffing + elective plus the all-controls pulse. The P7 requirement (≥ 200 ticks at one setting) was **not met**; the longest holds are R1's 170-tick recovery and R2's 120-tick one. P6 (order swap) and P4 (step vs ramp) were not run.
- **P9a** (overtime spacing) was run. It was evaluated only by eye (B16); no fitted m1 was checked against it. In this review m1 gains just 67 cost on top of m2.
- **P9b** was run but **mis-evaluated as pure pipeline.** The gradual rise at 0.1 and the 15–20 tick crash on return point to reassignment handover. The model's k2d cannot use this because the tandem structure is wrong (G3).
- **P9c** was run and evaluated properly: null. Together with the direct A/B at R2 30–110, M3 is excluded for return delays up to about 120 ticks.
- Every mechanism pair has at least one separating probe that was run.

## 4. Theses: missed drivers

- **Base deterioration is missing.** "Patients waiting can deteriorate": work per patient should rise with time spent waiting. It is the most economical explanation for three things together:
  - staffing-20 capacity of about 16.7 on the fresh reset queue vs about 11.4 on an aged backlog 65 ticks after the restore (R1 205–240), with no overtime before and M2 mostly faded;
  - R11's heavy cohorts that occupy beds and finish together;
  - part of the downward drift under electives (R6).
- The current `phi` state tracks only the elective share of **arrivals**.
- **M2 driver:** the brief says "team changes". The P9b data suggest reassignment by diagnostic allocation counts too, but it cannot be fitted until the tandem stage split is right.
- **M1 driver:** plain overtime is the right reading. Fatigue "later" might also scale with workload, but there is no data to test that.
- **Controls whose recovery value is not at a bound:**
  - diagnostic_allocation 0.1 was tested only on L;
  - urgent_priority below 0.6 was never tested (u down to −1.5);
  - staffing 1 (u = 1.27) was never tested.

## 5. Model code and stability (4,000 steps)

- The states are bounded:
  - W ≤ Wmax, and Xa + Bk ≤ Ca and Xt ≤ Cb by construction;
  - F ∈ [0, 1], H ≤ 40, and phi clipped;
  - L1 and L2 are driven by bounded D.
- 20 random 4,000-step schedules for m12_all_b gave all finite values, with max wait 653, queue 329 and discharges 23.5. The wait of 653 at staffing 1 is plausible but untested.
- **Pinned or absurd parameters:**
  - kd = 1.0 (at the sigmoid limit; the Dm filter is off) in every converged fit;
  - wu at 835 in one stuck restart;
  - wr of 79 or −1,869 whenever m3 is on;
  - Pc at 1.4e5.
- The optimizer is start-dependent: one wf = 0 start stuck at 44,905 and another reached 21,025. Use ≥ 3 starts with `refit.py`-style diff_step.

## 6. Gaps

| # | Sev. | Gap | Evidence | Suggested fix / test |
|---|---|---|---|---|
| **G1** | **high** | Follow-up capacity cost `wf` = 0.36–0.40 in every existing fit. Scored episodes with follow-up 0–0.3 (recovery scenarios) would get about 1.6× capacity. The data say there is none. | R9; the wf = 0 base is *better* (21,025 vs 21,153) | Fix `wf = 0` (or drop the term), and fix A0 = 11.5, kmu = 0.65, nsv = 2. |
| **G2** | **high** | Discharges on the elective bases are about 2× too low (E: 4.7 vs 9.7; overtime on E: 11.2 vs 13.8; L 8σ). The single `we·phi` work penalty cannot fit both E (staffing 20) and L (staffing 12.5) while the queue sits at the ceiling. | windows R1 310–530 and R2 110–290 | Split capacity per class, or make elective work a separate treatment demand. Let the ceiling queue be Wmax plus service stages. Refit the base before any pair comparison (lesson 6). |
| **G3** | **high** | Tandem, diagnostic-allocation structure: d = 0.1 is right in sign but not in size or timing, and it misses the 15–20 tick crash on return. k2d → 0. | R2 290–350: 4–7σ | The treatment stage should hold a large blocked-chair reserve (Cb ≫ Ca, reserve of about 140 under L). Then retest k2d (handover on reassignment) against that corrected pipeline. |
| **G4** | medium-high | Long-stay residual occupancy (R11/B19) is not modelled. About 11.5–26 patients in service drain in quanta; scoring cost is about 1σ on queue for as long as it persists. | R2 380–500 | Add a heavy-work in-service compartment filled by admissions of deteriorated patients (driver: waiting age or EMA of wait), with a slow completion rate. The reserve probe below gives its lifetime. |
| **G5** | medium | Deterioration of waiting patients (a base mechanism) is missing. It would explain reset capacity of 16.7 vs about 11.4 on an aged backlog. It is currently absorbed partly by M2 and M1, which inflates their gains. | R2 vs R1 205–240 | A work-per-patient state driven by the waiting population's age. Refit m2 and m12 after adding it. If g1 then goes to 0, the M1 case rests on "exactly two" alone. |
| **G6** | medium | The reset transient is wrong: the model takes about 55 ticks, the data about 8. Probably the initial composition is light, or part of it starts past assessment. | R1 0–60, R2 0–30 | Put the reading's excess over 23 in a fast-drain stage (rate about 0.3, 2-tick delay). Its 4,000-step weight is small but present in every episode. |
| G7 | medium | wait_time under-predicted during the staffing-5 overload (65 vs 97), and kd pinned at 1. | R1 60–240 | Let wait = W / capacity (current μ) rather than W / EMA(D). |
| G8 | low | Fatigue (M1) is tiny (g1 0.05, τ about 57) and confounded with the elective drift. The pair choice m1+m2 rests on the M3 nulls. | table | Accept m1+m2. Keep g1 small and bounded (for example ≤ 0.2) so random overtime-heavy schedules cannot collapse capacity. |
| G9 | low | Tooling: `fit.py` stops early (diff_step), and `battery.py` KeyError on holds under 15 ticks. | logs | Add a `--diff-step` option to fit.py (default 1e-3). Use `--min-hold 15`. |
| G10 | low | Untested regions: urgent < 0.6, staffing < 5, diagnostic 0.1 at recovery, and no P7 ≥ 200. | §3 | Keep the model monotone and clipped there. The stability gate must include these extremes. |

## 7. Reserve spending (50 steps): recommended, only if R2 can be continued

**Continue R2 without a reset at the recovery action for 50 steps** (observation ticks 500–549). This gives:

- whether the 34.5 residual (G4) leaves in another quantum;
- when that happens: the cohort lifetime since admission around tick 375, which sets the length of the recovery tail in the model;
- whether it settles at 23 or persists (lifetime of at least 170 ticks).

It needs no new P0, and it is the one gap that a model structure alone cannot settle.

```sh
cd toronto26-participant-kit
python run_schedule.py --budget hospital_queue      # free; expect 750
python run_schedule.py --continue data/hospital_queue/R2.json --confirm 50 --segments '[{"steps": 50, "action": {"staffing": 20.0, "elective_scheduling": 0.0, "diagnostic_allocation": 0.4, "urgent_priority": 0.6, "overtime": 0.0, "followup_capacity": 1.0}}]'
```

- **If the continue call fails** (run expired), **do not spend.** A fresh run cannot rebuild the residual inside 50 steps: it needs at least 110 ticks of load plus drain. Keep the reserve.
- **Not recommended:** a fatigue probe. It would need a loaded base (≥ 15 ticks) plus overtime on and off (≥ 50 ticks) and would still be confounded with the elective drift (G5). Fatigue's fitted effect is about 5 %.
- G1–G3 and G5–G7 are modelling work on existing data and need no steps.
