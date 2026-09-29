# Round 3 handoff: experiment design with the last steps, plus AB-B results

Written 2026-09-29 (Toronto night) for a fresh Claude Code session with clean context. No credentials here.

## Opening prompt (paste into the new session)

> Read `CLAUDE.md`, then `plans/round3-handoff.md` (this file), then `plans/round2-report.md`. We are in the last ~36 hours of the hackathon (final uploads close 2026-09-30 12:00 Toronto).
>
> Two jobs:
> 1. I will give you the public results of `submission-AB-B-variants.zip`. Interpret them with the decision rules in §4 and say which model each system should use.
> 2. Design round 3: how to spend the last 1,335 simulator steps (§5).
>    - Challenge the draft schedules, and pick per system by expected score gain per step.
>    - Present exact schedules with predictions and decision rules for my approval.
>    - **Do not spend any steps until I say yes.**
>
> Branch: `alpha-trotsky/epic-meitner-6fhk84`. The gateway key is in the gitignored `app-141-1d2abb-credentials.json` at the repo root. If it is missing (fresh container), ask me for it; never print it or write it into tracked files.

## 1. Where things stand

**Public scores:**

| System | v1 (overnight) | **v2 (round 2, current best)** | 50/50 blend v1+v2 | AB-B variant (fill in) |
|---|---:|---:|---:|---:|
| ad_auction | 0.8786 | **0.8912** | 0.8867 | |
| epidemic | 0.7201 | **0.7604** | 0.7522 | |
| hospital_queue | 0.6721 | **0.7241** | 0.7210 | – |
| market | 0.6838 | **0.7225** | 0.7089 | – |
| power_grid | 0.7418 | **0.7985** | 0.7744 | – |
| reservoir | 0.8521 | **0.8584** | 0.8576 | – |
| social_contagion | 0.6271 | **0.6780** | 0.6608 | |
| supply_chain | 0.8447 | **0.8560** | 0.8523 | – |
| traffic | 0.8335 | **0.8442** | 0.8422 | – |
| wildlife | 0.6611 | **0.7535** | 0.7333 | – |
| **mean** | 0.7465 | **0.7887** | 0.7650 | |

The user believes 0.7887 is about top 3.

**Files:**

- **Best known submission:** `toronto26-participant-kit/submission-round2-alt-market-v2.zip`. It holds all ten v2 models, identical to `toronto26-participant-kit/models/*` today.
- `submission-round2-final.zip` is the same except it has market v1. It is worse; don't use it.
- `submission-AB-A-blend50.zip` (blend) lost in all ten systems; drop it.

**Uploads:**

- **The Final tab is empty so far.** Public uploads never become final.
- The first upload after midnight should put `submission-round2-alt-market-v2.zip` in the **Final** tab.
- Each system gets 3 uploads per Toronto day, shared between the public and final tabs.
- Every upload that includes a system uses one of that system's slots.

## 2. What we learned (use this when designing)

- **The held-out protocol predicts public.** Every system whose v2 beat v1 on runs it was not fitted on also rose publicly (+0.006 to +0.092).
  - Holding out a run is the real validation.
  - The old-run in-sample fit is not. I wrongly kept market at v1 on that basis; v2 won by +0.039.
- **Base structure beats the mechanism choice.** The biggest gains came from structural fixes:
  - wildlife: the predator block, +0.092;
  - power_grid: a static frequency map, +0.057;
  - hospital_queue: removing the elective work penalty and reporting wait first-come-first-served, +0.052;
  - social_contagion: dropping M1, +0.051.
- **Blending with v1 hurts everywhere.** v1 adds nothing; build on v2.
- **Long-run levels dominate scoring.**
  - Episodes are 4,000 ticks, so a persistent 1σ offset caps an observable at 0.5 for the whole hold.
  - The reset transient is only about 1–2% of ticks.
- **Round 2 designs worked well:**
  - fresh reset with controls from tick 0;
  - pulse-box interior at u = 0.7, 0.85 and 1;
  - long holds;
  - gap-300 vs gap-20 spacing;
  - ladders that change one control at a time.

## 3. Why the three weakest systems lag (theses to test)

In all three, the level a hold settles at depends on **history, order or composition**, which a relaxation base with fast memories can't carry.

**social_contagion (0.678, 120 steps left)**
- The model puts community A near 200 under every combination. The data span 143–257:
  - joint pulse at u = 0.7 from reset: 164/101;
  - seeding 4.5 first, then incentive 2 added: 257/146;
  - after cutting incentive to 1: 143/75.
- **Hypothesis H-bridge:** bridge outreach costs A (it diverts local recruitment).
- **Hypothesis H-order:** incentive added *after* recruitment locks in retention ("promises accompany waiting cohorts").
- The current data can't separate the two.

**hospital_queue (0.724, 100 steps left)**
- **Knife edge:** at recovery, capacity barely exceeds arrivals (11.49), so a small capacity error means drain-to-23 vs flood-to-300.
- **Post-overload plateau:** the queue plateaus near 100 in both R1 and R4, and v2 drains to 23.
- **Wait jump:** in R4's tail, wait jumps from 20 to 169, matching the age of patients who arrived while urgent priority was 1.
- **Hypothesis H-starve:** a routine class is held back by urgent priority, creating a stranded backlog. v2 has one first-come-first-served queue with no classes.
- Urgent priority below its recovery value of 0.6 was never tested.

**market (0.7225, 200 steps left)**
- **One structure can't fit both run A and runs B/C.** Run A has single controls; runs B and C have joint rate + tax from reset.
- **Depth never settled:** under the joint pulse it was still falling at 12 when the segment ended. v2 assumes 16 for all 4,000 ticks.
- **Hysteresis under tax:** after rate + tax, price stays about 7 low while any tax is on.
- Volume σ is tiny (0.021).

## 4. AB-B: what each variant tests, and how to read the result

`submission-AB-B-variants.zip` contains only three systems. Compare each with its v2 public score above.

| System | Variant | Held out (old-only fit / leave-one-out) | If variant > v2 | If variant < v2 |
|---|---|---|---|---|
| social_contagion | "Promise ratchet" (`greybox/social_contagion_model_v2.py`, fit `fits/social_contagion/round2/v2/v2c_C.json`). A cut moves members to an at-risk pool; adds bridge-cost and incentive × seeding terms. | 0.395 vs v2 0.375 / 0.299 vs v2 0.426 | Supports H-order/H-bridge structure. Use it and design the social run to pin it. | Its extra terms overfit. Keep v2 and treat the level map as the target of the step run. |
| epidemic | v2 structure fit on **old runs only** (`fits/epidemic/round2/v2/A_pe.json`). Old-run score 0.744 vs 0.701. | 0.629 / – | The scorer looks like the old regimes, and the new extreme runs pull the fit away. Weight old data more in future fits. | Fitting new regimes helps. Keep the all-data fit. |
| ad_auction | v1 structure refit on all data (no binding capacity, no fatigue module). | – / 0.513–0.585 vs v2 0.525–0.594 | v2's binding capacity is wrong. Drop it. | v2's capacity plus fatigue is right. |

Variant folders are in `toronto26-participant-kit/ab/variantB/<system>`. The blend folders are in `ab/blend50/`.

## 5. Step budget and draft round-3 schedules (not approved, not spent)

Remaining steps, confirmed by a free budget read on 2026-09-29:

| System | Steps left |
|---|---:|
| social_contagion | 120 |
| wildlife | 150 |
| power_grid | 110 |
| hospital_queue | 100 |
| market | 200 |
| epidemic | 155 |
| traffic | 100 |
| supply_chain | 100 |
| reservoir | 100 |
| ad_auction | 200 |
| **total** | **1,335** |

**Draft schedules.** Sources are the diagnostician/modeler proposals in each `plans/<system>-plan.md` "Round 2 model (v2)" section and `plans/<system>-round2-diagnosis.md` §6. Where I refined one later, both are listed.

| System | Draft schedule | Decides |
|---|---|---|
| social_contagion (120) | Fresh reset. Seeding 6.3 + bridge 0.42, incentive 0 for 60 ticks; then add incentive 1.4 for 60. | A ≈ 150–165 in the first half means H-bridge; ≈ 190–210 means not. The second half against R4's 164/101 tests H-order (does incentive after recruitment add R5's +60?). |
| hospital_queue (100) | **Refined:** continue R4 without a reset (copy to R4c), recovery for 40, then **urgent_priority 0** for 35, then recovery for 25. **Original:** R4c recovery 50 plus R3c recovery 50. | Whether the plateau near 100 and the rising wait persist. If priority 0 releases a stranded class (queue drops, wait spikes then falls), H-starve holds and the model needs two classes. Also covers the untested low-priority range. |
| market (200) | **Refined:** fresh reset, tax 0.05 alone for 80, then joint rate 0.1 + tax 0.05 for 120. **Original:** tax 100 then rate added for 100. | Whether the reset depth drain needs rate + tax or tax alone, and where joint-pulse depth settles long-run (v2 assumes 16). |
| wildlife (150) | Continue R3 (copy to R3c), joint .7 (hunt 4.9, hab .37, corr .7) for 120, then release for 30. | Joint-box long-run prey (v2 38/32 vs data trend ≈ 22); predator depressions additive (v2 1.75) or max-type (≈ 1.93); release peak after a long pulse. |
| epidemic (155) | Fresh reset, mask 0.85 for 120, then recovery for 35. | Whether masks fatigue on their own or only via closure. Release jump ≥ +0.28 vs ≤ +0.25. |
| power_grid (110) | Fresh reset, price 0 + reserve 150 + charging 1 + interconnector 1 for 60; interconnector 0.2 for 30; recovery for 20. | Whether frequency effects add (v2 51.03) or saturate at high load (50.2–50.5); the last charging (M2) question. |
| supply_chain (100) | Fresh reset, orders 80 (rest at recovery) for 35; then add lead_time_buy 0.44 for 65. | Rush dose-response: shipments ≥ 33 means a threshold, 26–29 means linear. |
| traffic (100) | Fresh reset. B = recovery + ramp 1 + toll 1.5 for 30; B + signal 0.255 for 35; B + signal 0.2025 for 35. | The green-capacity knee: v2 predicts flow_a 10.4/8.2; the knee hypothesis says 14–15/≈ 11. |
| reservoir (100) | Two fresh 50-step runs: release 12, aeration 0, depth 1 (then depth 0) for 30 ticks, plus 20 recovery. | Whether a short anoxic pulse leaves a quality offset, and deep vs shallow clearing of the pool. |
| ad_auction (200) | Fresh reset. Bid 1.5 / cap 100 / breadth .775 for 50; recovery 35; bid 5 / cap 20 / breadth .775 for 50; recovery 35 (+30 for settling). | Whether capacity binds from a rested start (plateau ≈ 5.4); the purchase cut under throttling. Should be read together with the AB-B ad_auction result. |

**Questions for the design session:**

1. **Rank systems by expected public gain per step.** The weak three have the most room (1 − score ≈ 0.28–0.32). Wildlife and epidemic have ready, sharp tests.
2. **For each run, check that the outcome changes the model** (a decision rule with a pre-registered threshold) and that a refit can happen before 09-30 12:00.
3. **Consider continuations (`--continue`) over fresh resets** where the interesting state already exists; they need no preparation steps. Continuing runs hours later has worked before.

## 6. Process that worked

**Collection and modelling:**

1. **Collect.** Collect only via `toronto26-participant-kit/run_schedule.py` with segment files. `fits/round2/final_schedules.py` shows how to build, bounds-check and screen segment files against candidate fits, and `fits/round2/run_all.sh` runs them in the background. Log each spend in `plans/<system>-plan.md`.
2. **Diagnose.** One diagnostician agent per system, following `plans/agent-prompts/round2-diagnostician.md`.
3. **Model.** One modeler agent per system, following `plans/agent-prompts/round2-modeler.md`. Validation:
   - (A) fit on old data, score the new runs;
   - (B) leave one new run out;
   - (C) fit on all data.
   Ship only if it beats the current model on held-out runs.

**Scoring and checks:**

- `fits/round2/heldout.py` scores a model on runs it wasn't fitted on; `compare.py` and `score_folder.py` compare model folders.
- The contract gate is `python -m greybox.common.gates contract <folder> --system <s>`.
- To combine system folders into one ZIP: `python -m greybox.common.package --all-zip <zip> --folders ...`. Its static import scan falsely flags market v1's `market_model` import when it is nested in a blend.
- `ALLOW_MARKET_PACKAGE=1` is needed to package market.

**Practical notes:**

- **CPU:** the machine has 4 CPUs. Prefix fits with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`; running 10 agents at once pushed the load to about 35.
- **Commits:** commit and push after every result (a stop hook enforces a clean tree).
