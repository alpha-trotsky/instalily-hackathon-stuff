# Overnight framework: research and model 9 systems autonomously

Written 2026-09-26. Paste this whole file into a Claude Code session opened at the repo root, and tell it to run the plan.

**Goal:** by morning, have a tested forecaster and a submission ZIP for each of these systems:

`epidemic`, `traffic`, `power_grid`, `supply_chain`, `wildlife`, `reservoir`, `ad_auction`, `social_contagion`, `hospital_queue`

`market` is already done. Do **not** spend market steps or change `models/market/`.

The user uploads the ZIPs in the morning. **Never upload anything.**

---

## 0. Standing authorization and hard limits

- **Spending authorization.** The user pre-authorizes paid simulator steps for this job, within the caps below. Don't stop to ask; log every spend instead.

  | Controls | Systems | Cap per system |
  |---:|---|---:|
  | 3 or 4 | epidemic, wildlife, ad_auction, social_contagion, power_grid, reservoir | **1,000** |
  | 6 | traffic, supply_chain, hospital_queue | **1,300** |

  Never exceed the cap.
- **Before every segment:**
  - Read `client.budget(system)` and confirm the segment fits inside both the cap and the remaining budget.
  - Record the spend in `plans/<system>-plan.md` (date, run, ticks, steps, remaining).
- **Collect data only with `toronto26-participant-kit/run_schedule.py`.**
  - It saves after every step and refuses to overwrite.
  - `--continue` extends the same simulator run without a reset.
  - `--confirm N` must equal the number of steps.
  - It handles OneDrive file locks.
  - Never write collection code that bypasses these protections.
- **Credentials.** Always get a client from `toronto26-participant-kit/gateway.py` (`make_client()`). It tries these sources in order:
  1. the gitignored credentials file (local machine);
  2. the `GROUNDTRUTH_GATEWAY_URL` / `GROUNDTRUTH_KEY` environment variables;
  3. no key at all, in a cloud session, where the agent proxy adds it (§0.1).

  For a free budget read, run `python toronto26-participant-kit/run_schedule.py --budget <system>`. Never print the key, copy it into a file, or put it in a ZIP.
- **Scope.** Don't touch market data, market models or `submission-market-v1.zip`. Don't upload anything.
- **Backups.** After each system is finished, commit and push. On a local machine, push to `origin main`. In a cloud session, push to the session's own working branch; never push to `main` and never force-push. End the commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Every system must end with a valid submission folder**, even if something fails. The fallbacks, in order, are:
  1. the pair model;
  2. a relaxation-only model;
  3. the persistence baseline.

  A missing system scores 0.

## 0.1 If this is a Claude Code cloud session

You are in a cloud session if the environment variable `CLAUDE_CODE_REMOTE` is `true`. In that case:

- **The credentials file is not in the clone, and that is expected.**
  - Don't look for the key or ask for it. `gateway.make_client()` sends requests without an `Authorization` header, and the environment's **API credential** for `gt-gateway-wavddee32q-uc.a.run.app` adds it outside the VM.
  - `make_client()` also points `SSL_CERT_FILE` at the system CA bundle, so httpx trusts the proxy.
- **First action (free).** Run `python toronto26-participant-kit/run_schedule.py --budget epidemic`. It must print a JSON budget.
  - **401/403:** the credential isn't being attached. Retry once. If it still fails, write the error into `plans/overnight-status.md`, do Phase 0 (it needs no steps), then stop. Don't guess at other ways to authenticate.
  - **TLS/SSL error:** set `SSL_CERT_FILE` to the bundle named in `REQUESTS_CA_BUNDLE` (or `/etc/ssl/certs/ca-certificates.crt`) and retry.
  - **Connection blocked:** the host isn't reachable. Record it and stop, as for 401.
- **Python packages.** If `python -c "import numpy, scipy, matplotlib, httpx"` fails, install them with `python -m pip install numpy scipy matplotlib httpx`. If pip refuses with "externally managed", add `--break-system-packages`.
- **The VM has 4 vCPUs and 16 GB of RAM.** Run the bootstrap with 3 workers (its default is CPU count − 1), and run at most 3 fits in parallel. If a system is running behind schedule, use 2 bootstrap draws per pair instead of 3.
- **Never end your turn while work remains.** An idle cloud session is reclaimed, and its background processes are lost.
  - Run long jobs in the background and wait on them with blocking checks (for example an `until` loop inside one Bash call of up to 10 minutes). Repeat until they finish.
  - Keep going until every system is done and `plans/overnight-report.md` is written.
  - If the session is resumed after being reclaimed, follow the resume rule in §1.
- **Git.** Commit and push to the session's own branch after each system. The user will collect the ZIPs from that branch.

## 1. Context management (one session, orchestrator + subagents)

The orchestrator (the main session) keeps only summaries. All heavy work happens in subagents that read and write files. All state lives on disk, so a context reset or summary never loses work.

- **Status file:** `plans/overnight-status.md` has one row per system with the fields phase, steps spent, remaining, current best model and ZIP path. Update it after every phase.
- **On resume after a context reset:** read the status file first, then continue from the recorded phase. Before spending, check the data files already on disk; never re-collect data that exists.

**Per-system pipeline.** Run the systems sequentially. Each phase is a fresh subagent that is given this file, the system name, and the paths below.

| Phase | Agent | Does | Writes |
|---|---|---|---|
| A | **Researcher** | Dossier and theses (§3), Run 1, behaviour catalogue v1, Run-1 pair fits, Run 2 design and execution, catalogue v2 | `plans/<system>-plan.md`, `data/<system>/*.json`, plots |
| B | **Reviewer** | Independent behaviour review (§6.2) | `plans/<system>-review.md` |
| C | **Modeler** | Resolves every review gap, builds the final model, runs cross-run validation, fits all data, runs the bootstrap, checks the gates, packages | `greybox/<system>_model.py`, `fits/<system>/`, `models/<system>/`, `submission-<system>-v1.zip` |
| D | Orchestrator | Updates the status file, commits and pushes, moves to the next system | — |

- **Phase C and steps:** Phase C may spend at most the leftover reserve (§4), and only for a targeted gap the reviewer named.
- **System order:** simplest first, so the most models exist by morning:

  epidemic → wildlife → ad_auction → social_contagion → power_grid → reservoir → traffic → supply_chain → hospital_queue

- **Soft time limit: about 75 minutes per system.** Past that, ship the best model that passes the gates, mark it in the status file, and move on. Come back at the end if there is time left.

**Phase 0 (orchestrator, once, zero steps):** have a "toolsmith" subagent generalize the market tooling into `toronto26-participant-kit/greybox/common/`, then validate it by reproducing the market M1+M2 fit on `data/market/A.json` to within 5% of its cost. The tools are:

| Tool | Purpose |
|---|---|
| `settle.py` | Settling check (§4.3). Given a segment's observations and the noise σ, report whether each observable has settled, its estimated settling time and its remaining drift. |
| `battery.py` | The standard analysis battery (§6.1): plots and a JSON of every measured quantity. |
| `fit.py` | Generic rollout fitter. Takes a model module that exposes `SPEC`, `MODULES`, `simulate`, `normalize`, `to_natural`, `to_raw`, like `greybox/market_model.py`. Includes restarts and overflow-safe residuals. |
| `bootstrap.py` | Generic parametric bootstrap with block-resampled residuals and a confusion matrix, as in `greybox/bootstrap_market.py`. |
| `gates.py` | Local score with σ = 0.1×std, persistence comparison, stability test and contract check (§7). |
| `package.py` | Builds `models/<system>/` and `submission-<system>-v1.zip`, then re-tests from the extracted ZIP. |

**Market references to imitate:**

- `plans/market-plan.md`: the full worked example, including the thesis, the log, observations, the model, the bootstrap and the public checkpoint.
- `toronto26-participant-kit/greybox/market_model.py`, `fit_market.py`, `bootstrap_market.py`, `plot_fit.py`
- `toronto26-participant-kit/models/market/`

## 2. Lessons from market (apply to every system)

1. **Reset is not an equilibrium.** Market volume fell from 90 to 2 within 15 ticks, and price drifted for about 100 ticks. Always start a run with a recovery hold, and model the reset transient; it appears in every scored episode.
2. **On and off responses can differ.** The asymmetry is the evidence for memory or nonlinearity. Always pair a step on with a step off.
3. **Test on/off symmetry in both log and linear units.** Market depth was symmetric in linear units and asymmetric in log. Model each observable in the units where it is symmetric.
4. **Symmetric transient terms (high-pass filters) predicted a mirror dip that did not happen.** When an effect appears on only one switch, model it with a one-sided driver, for example "fading memory of depth *falls*".
5. **Never trust the all-three-mechanisms model.** An unused module soaks up misfit and produces absurd coefficients. Compare pairs only.
6. **A near-tie between pairs in the bootstrap means the model is missing something**, not that more data is needed. Fix the model structure.
7. **Local σ.** Public scores match local scores computed with σ ≈ 0.1× each observable's std, not 1× std. Market scored 0.68 publicly while the local std-based estimate was 0.93.
8. **Relationships between outputs matter.** Market volume ≈ base × (1 + c·|rate of price change|), and depth dips followed a fading memory of price falls. Always scan levels, rates of change, absolute rates and lags between outputs.
9. **Watch for parameters pinned at their limits.** One pinned at a limit, such as a feedback gain at its cap, is standing in for missing structure. It is not evidence for a mechanism.

---

## 3. Before spending: dossier, theses and separation table

Write these into `plans/<system>-plan.md` **before any step is spent**, from `briefs.md` and `docs/<system>.json`. This is pre-registration: it guards against fitting a story to the data afterwards.

### 3.1 Dossier

- Observables, with the ranges of their initial readings.
- Controls, with their bounds and their recovery and pulse values.
- **Normalized coordinate:** `u_i = (value − recovery_i) / (pulse_i − recovery_i)`. So u = 0 is recovery and u = 1 is pulse; scoring's recovery scenarios use u ∈ [0.7, 1].
  - Note every control whose recovery value is *not* at a bound, for example traffic `signal_timing` 0.5 and ad_auction `bid` 1.5. The range on the other side of recovery is otherwise never tested.
- Every delay or commitment phrase in the brief, for example "already travelling animals can still arrive" or "conveyors retain their destination". Each one implies a pipeline delay.
- Anything tied to time since reset, for example seasonal river supply or a reference price of 0.8. It is deterministic and therefore learnable.
- The organizer-suggested comparisons, quoted word for word. These become required probes (P9).

### 3.2 The three mechanisms

Quote them from the brief. If the brief doesn't name exactly three (power_grid, wildlife and reservoir are ambiguous), list the best three candidates from the text and state how confident you are.

### 3.3 One thesis per mechanism, using this template

| Field | Content |
|---|---|
| Quote | exact brief text |
| Hidden state | what accumulates (for example fatigue, or immunity) |
| **Driver** | what feeds it: a control, an output's level, an output's rate of change, or accumulated exposure |
| **What it changes** | size of response, settling speed, delay, rebound/overshoot, or an output directly |
| Timescales | how fast it builds, how fast it fades (guesses) |
| Prediction per probe | for each probe P1–P9: what we would see with the mechanism **present** and with it **absent** |

### 3.4 Separation table

Rows are the probes, columns are the three mechanisms, and each cell holds the predicted effect.

For each **pair** of mechanisms (M1/M2, M1/M3, M2/M3), name at least one probe where the two predictions differ, ideally one where one predicts an effect and the other predicts nothing. If a pair has no separating probe, the design is not finished.

---

## 4. Test-case creation

### 4.1 Probe library

Every mechanism probe is a **comparison between two schedules**, never a single observation. A single observation mixes the mechanism with the ordinary dynamics; the difference between the two schedules isolates it.

| Probe | Schedule | What it reveals | Scoring category it covers |
|---|---|---|---|
| P0 Baseline | recovery from reset until settled | the reset transient, noise σ | all |
| P1 Step on/off | one control to u = 1, hold, back to u = 0, hold | size of effect, delay, settling speed, **whether on and off mirror each other**, whether levels return to baseline | — |
| P2 Mid level | the same control at u = 0.5 | whether the effect scales linearly | sustained |
| P3 Joint | two controls at u = 1 together | whether effects add or interact | composition |
| P4 Step vs ramp | same end level reached abruptly versus gradually | mechanisms driven by rates of change (momentum, synchronization, adaptation) | — |
| P5 Gap test | two equal pulses with a short gap versus a long gap | build-up and recovery memory (fatigue, depletion, capacity) | recovery spacing |
| P6 Order swap | A then B, versus B then A | dependence on history | action order |
| P7 Long hold | at least 3× the longest settling time seen | slow drift | sustained |
| P8 Same effect, different cause | the same output change produced by two different controls | whether a mechanism responds to a control or to the output itself | — |
| P9 Organizer-suggested | as quoted in the dossier | what the organizers are pointing at | — |

**Comparisons inside one run:** the two halves must be separated by enough recovery that outputs return to baseline, which you confirm with the settling check. Otherwise put the two halves in different runs. Resets are free, but each new run pays for its own P0.

### 4.2 Run plan and budget

Runs 1 and 2 must together include:

- P0 in each run
- P1 for every control
- P2 for the most important control
- P3 for the top two controls
- at least one separating probe per mechanism pair (§3.4)
- every P9
- one P5 or P6 (the recovery and order scoring categories)
- one P7 of at least 200 steps

There is **no separate held-out run.** The public upload is the held-out test. Model structure is instead checked by fitting on Run 1 and predicting Run 2 (§6.3).

| Run | ≤4-control cap | 6-control cap | Content |
|---|---:|---:|---|
| 1. Characterization | ≤ 550 | ≤ 750 | P0, then P1 for each control, in order of expected importance from the brief |
| — | 0 | 0 | Catalogue v1, fit the 3 pair models on Run 1, choose Run 2 probes (§4.4) |
| 2. Separation and coverage | ≤ 400 | ≤ 500 | Fresh reset (this also tests whether the starting reading matters). P0, P2, P3, the separating probes, P9, P5/P6 and P7 |
| Reserve | ~50 | ~50 | Holds that haven't settled, or a gap named by the reviewer |

### 4.3 Adaptive holds (no human in the loop)

- **Run one segment at a time**, using `run_schedule.py --continue` to extend the same run, and run the settling check after each segment. The simulator run stays alive between calls; continuing the same run after several minutes worked in market.
- **P0:** start with 40 steps of recovery. Extend in chunks of 20 until settled, up to 120.
- **First P1 (most important control):**
  - Hold the on-step for 40 steps, then extend in chunks of 25 until settled, up to 150.
  - Do the same for the off-step.
  - Record the settling time τ for each observable.
- **Later holds:** `hold = clamp(3 × τ_max_seen, 30, 150)`.
- **6-control systems:** every control gets a P1. Only the top 3, by effect size seen or expected, get full-length holds. The rest get `clamp(2 × τ, 30, 60)`.
- **"Settled"** means that a decay curve fitted to the last half of the segment predicts less than 2σ of further drift, where σ is the noise estimated from flat stretches.
- **Budget guard:** before each segment, project the cost of the rest of the run. If it would exceed the run's cap, shorten the remaining holds, lowest-priority controls first. Never drop a P1 entirely.
- **If a continue call fails** (for example because the run expired): start a new run with P0 and record this in the log.
- **If a hold never settles within 150 steps** (slow systems such as reservoir, epidemic and wildlife): accept it, record the timescale as "> 150", and plan P7 to be longer.

### 4.4 Choosing the Run 2 probes

1. Start from the separation table, the P9 list and the coverage list in §4.2.
2. Fit the three pair models on Run 1 (§5).
3. For each candidate probe, simulate it through all three fitted pairs. Then rank probes by how much the pairs disagree, in units of σ, per step of cost.
4. Pick the highest-ranked probes that complete the coverage list within the Run 2 cap. Record the ranking and the reasons in the plan.

---

## 5. Modeling (can change later; test data cannot)

**Structure.** Follow the same pattern as `greybox/market_model.py`:

- **Outputs.** Each output moves a fraction k ∈ (0, 1) per tick toward a target, `target = baseline + Σ control effects (+ interaction terms) + mechanism terms + coupling terms + reset-transient term`.
- **Delay stages.** Add first-order lag stages wherever the dossier found a commitment or delay phrase. Each stage starts empty, following the reset convention.
- **Mechanism modules.** Each mechanism is a fading hidden state driven by the driver written down in its thesis (§3.3). Each module has a gain; a gain of 0 turns it off.
  - Write the modules **from the theses before fitting.**
  - Extra data-driven terms, such as market's depth-withdrawal term, are allowed only if they improve the Run-1 → Run-2 prediction (§6.3).
- **Coupling terms between outputs.** Take these from the catalogue, for example output B driven by |rate of change of output A|.
- **Units.** Log or linear per observable, according to the on/off symmetry test. Use log for positive quantities with multiplicative effects.
- **Time since reset.** Include a deterministic time term if the dossier found seasonality.
- **Stability by construction:**
  - every rate is in (0, 1), through a sigmoid;
  - memory states fade, and their drivers are bounded;
  - feedback gains are capped;
  - states are clipped to wide physical ranges.

**Fitting:**

- `scipy.optimize.least_squares` on **full rollouts**.
- Residuals in noise units (log residual / relative noise, or residual / σ), with `loss='soft_l1'`, `f_scale=2`.
- 3 restarts; residuals must not overflow.
- If a fit is stuck, lengthen the horizon gradually (100 steps → 300 → full).

---

## 6. Behaviour catalogue, review and model selection

### 6.1 Behaviour catalogue (researcher; v1 after Run 1, v2 after Run 2)

Run the standard battery on every run and every observable:

1. The reset transient: shape and duration.
2. Settled level at every setting tested, as a table.
3. Delay before a response, for each switch.
4. Settling time for on versus off, in **both** log and linear units, and the symmetry verdict.
5. Overshoot or undershoot, and ringing.
6. Whether the level returns to its previous baseline after each pulse.
7. Relationships between outputs:
   - correlations of levels, rates of change, |rates of change| and signed rise/fall parts, at lags −10 to +15;
   - regressions on fading memories of rises and falls, at memory rates 0.02–0.3.
8. Noise σ for each observable, and whether it scales with the level.
9. Anything that doesn't fit the theses.

Every behaviour gets an **ID** (B1, B2, …) with:

- **Evidence:** a plot path or a number.
- **Candidate explanations:** which mechanism(s), a plain dynamic, or unknown.
- **Status:** `modeled by <component>`, `not captured`, or `open`.

Also plot every run, as in `data/market/A_0-600.png`: one panel per observable plus a controls panel.

### 6.2 Review (reviewer, a separate agent)

1. Look at the run plots and raw data **before reading the catalogue**, and write an independent list of behaviours.
2. Compare that list with the catalogue. Every behaviour in either list must end up with a model component (with a plot of the fit errors as evidence) or be flagged `not captured` with a reason.
3. Check that every separating probe and every P9 was actually run *and* evaluated in the plan.
4. Check the theses for missed drivers, for example a mechanism driven by an output's rate of change but tested only with level changes.
5. Write `plans/<system>-review.md` with a numbered list of gaps. The modeler must answer every one.

### 6.3 Model selection (modeler)

1. **Cross-run test of the structure.** Fit the three pairs M12, M13 and M23 on Run 1 only and predict Run 2. Report each pair's Run-2 score with σ = 0.1×std. This plays the role that the tax-off segment played in market.
2. **Refit on all data** (Run 1 + Run 2) and record each pair's cost.
3. **Bootstrap** (`greybox/common/bootstrap.py`):
   - For each fitted pair, 3 synthetic datasets on the real schedules, using block-resampled real log residuals (block 50, skipping the first 20 ticks).
   - Refit all three pairs on each; build the confusion matrix and the winning margins.
   - Increase to 5 draws if the result is ambiguous.
4. **Decision rules:**

   | Situation | Action |
   |---|---|
   | The confusion matrix has a strong diagonal and the real winning margin is at least the smallest bootstrap margin | Accept that pair. Submit it. |
   | The confusion matrix has a strong diagonal but the real margin is far below the bootstrap margins | Near tie: the model is missing something. Revisit the catalogue and the review gaps once, then submit the pair with the best cross-run score and flag it "unresolved". |
   | The confusion matrix has a weak diagonal | The experiments can't separate the pairs. Submit the best cross-run pair and flag it "not identifiable". |
   | A pair has a parameter pinned at a limit | Treat that as missing structure, not evidence. Prefer the other pair unless it is much worse. |

5. **Record everything:** the costs, cross-run scores, confusion matrix, margins and the decision go into the plan, in the same format as the market plan.

---

## 7. Gates before packaging

1. **Local score.** Use σ = 0.1× the std of each observable (after tick 20). It must beat persistence on Run 2 when the model is fitted on Run 1.
2. **Stability.** 200 random in-bounds schedules, 8 of them 40,000 steps long, with holds, fast switching, extremes and uniform random values, from random initial readings. Every value must be finite and inside a plausible range, with no sawtooth.
3. **Contract.**
   - `predict(initial, interventions, context)`, called with `docs/<system>.json`'s `forecast_context` and 40 random episodes of 4,000 in-bounds actions, returns 4,000 dicts with every observable, all finite.
   - Loading plus the 40 episodes takes far less than 1,200 s.
   - It never raises an exception; if anything fails it falls back to persistence.
4. **Submission folder.**
   - `models/<system>/` contains `predict.py`, a copy of the model module and `params.json`.
   - Standard library plus NumPy/SciPy only, files loaded relative to `__file__`, no state kept between episodes.
   - `package.py` builds `submission-<system>-v1.zip` with the `<system>/` folder at the ZIP root, re-runs the contract check from an extracted copy, and confirms that no credential value appears in any file. In a cloud session there is no credentials file to compare against. There, reject any file that contains `gateway_key`, `portal_credential` or an `Authorization` header value.

## 8. Morning deliverables

- One `toronto26-participant-kit/submission-<system>-v1.zip` per system.
- `toronto26-participant-kit/submission-overnight-all.zip`, containing all nine new system folders plus `market/` from `models/market/`, each folder at the ZIP root.
- `plans/overnight-report.md`, with one row per system:
  - steps spent and remaining;
  - selected pair and confidence (accepted / unresolved / not identifiable);
  - cross-run score and persistence score (σ = 0.1×std);
  - gate results and ZIP path;
  - the three most important open issues.

  Put a short "what to do first tomorrow" section at the top.
- For each system: `plans/<system>-plan.md` (dossier, theses, separation table, log, catalogue, decisions) and `plans/<system>-review.md`.
- Everything committed and pushed.
