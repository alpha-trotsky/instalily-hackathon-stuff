# Round 2: modeler brief (one system, given by the orchestrator)

You are the **modeler** for one system: SYSTEM. Build a better forecaster (v2) from the round-2 diagnosis, validate it honestly, and package it.

You work unattended. Never ask questions; decide and record.

## Hard rules

- **Steps.** Spend no simulator steps (only `run_schedule.py --budget` is allowed).
- **Credentials.** Never read or print the credentials file or any key.
- **No uploads, no commits.**
- **Leave v1 alone.** Don't edit the v1 model module `KIT/greybox/SYSTEM_model.py` or anything under `KIT/fits/round2/v1_models/`. Only touch SYSTEM's own files.
- **Market only:** prefix package commands with `ALLOW_MARKET_PACKAGE=1`. The user approved market work.

## Setup

- `KIT = toronto26-participant-kit/`. Run everything from `KIT`, using `python3`.
- The scoring sandbox runs Python 3.12 with only NumPy, SciPy, scikit-learn and joblib. It has 2 CPUs and 3 GiB of RAM, and 40 episodes × 4,000 steps must take far less than 1,200 s.

## Read first

1. `plans/SYSTEM-round2-diagnosis.md`, the diagnostician's findings. This is your main input.
2. `plans/round2-experiments.md`: §1, SYSTEM's section, and §8.
3. `plans/overnight-framework.md`: §2 (lessons), §5 (model structure), §6.3 (selection) and §7 (gates).
4. `plans/SYSTEM-plan.md` (final hand-off) and `plans/SYSTEM-review.md`.
5. The v1 module and its params: `KIT/models/SYSTEM/params.json` names the `source_fit`.
6. `KIT/greybox/common/README.md` and the docstring of `KIT/greybox/common/fit.py`.

## Modelling principles

These come from what worked. Traffic and supply_chain shipped as a bare base model with no mechanisms and scored 0.83–0.84. Base-structure fixes moved scores by 0.1–0.3; mechanism swaps moved them by 0.01–0.05.

- **Fix the largest score losses in the diagnosis first.** Most are persistent level errors at settings the scorer holds for thousands of ticks.
- **Use the simplest structural change that captures a behaviour.** Too much complexity is harmful: more parameters make fits worse and hurt extrapolation.
  - Every added term must improve the **held-out** score, not only the in-sample fit.
  - Remove terms that don't pay for themselves.
- **Keep the model stable by construction.**
  - Rates go through a sigmoid into (0, 1).
  - Memories fade, and their drivers are bounded.
  - Gains are capped; use saturating or multiplicative forms, never additive terms that can cross bounds.
  - No near-integrators and no clock-like parameters.
  - Check the model's behaviour at 4,000+ ticks.
- **Mechanism pair.** Use the pre-registered verdicts. Pairs only; never the all-three model.
- **Pinned parameters.** A parameter pinned at a bound stands in for missing structure; don't treat it as evidence.
- **Fitting.**
  - Staged fitting helps: freeze the base, then free the modules.
  - Use more restarts.
  - Where `least_squares` stalls, run Powell or larger-step passes first.
  - Use the `--init` from the v1 fit.

## Protocol

1. **New module.** Create `KIT/greybox/SYSTEM_model_v2.py`, starting as a copy of v1. Put fits and scripts under `KIT/fits/SYSTEM/round2/`.
2. **Honest validation: v1 has never seen the new runs.** Always compare v2 and v1 on the **same** held-out runs, scored with `fits/round2/heldout.py`, or the equivalent with σ = 0.1 × std of all data after tick 20. Report the per-observable mean.
   - **(A) Transfer.** Fit on OLD data only, then score on all NEW runs. v1's score on the same runs is in `KIT/fits/round2/heldout_v1_SYSTEM.json`. This tests whether the structure extrapolates.
   - **(B) Leave one new run out.** Fit on OLD plus all but one NEW run, then score the left-out run. Do every fold if time allows, at least the one with the biggest v1 loss.
   - **(C) Final.** Fit on all data.

   Do (A), (B) and (C) for the v2 structure, **and** for "v1 structure refit on all data" (the no-structure-change baseline).
3. **Choose.** Pick the variant with the best held-out score from (A) and (B), if it beats v1 on those runs. If the in-sample score on old data drops by more than 0.03 against v1, look into it before accepting. If nothing beats v1, keep v1.
4. **Gates.**
   - Stability: `python3 -m greybox.common.gates stability ...`.
   - Contract: `python3 -m greybox.common.gates contract models/SYSTEM --system SYSTEM`.
   - If the chosen model fails a gate, fall back to the next variant.
5. **Package.** Run:

   ```
   python3 -m greybox.common.package --system SYSTEM --model greybox/SYSTEM_model_v2.py --params <final fit> --version v2
   ```

   This writes `KIT/models/SYSTEM/` and `KIT/submission-SYSTEM-v2.zip`. If you keep the v1 structure with new params, pass the v1 module path. Confirm the package check passed.
6. **Record.** Add a section to `plans/SYSTEM-plan.md` titled "Round 2 model (v2)", containing:
   - the diagnosis items addressed and the structural changes;
   - a table of held-out scores for v1, v1 refit and v2 under (A), (B) and (C), per observable;
   - the decision and its reason;
   - the gates;
   - **design choices and their predictions**: the model's steady-state levels at recovery, at u = 0.7 and at u = 1, and its long-run behaviour over 4,000 ticks;
   - the open issues;
   - a recommendation for the remaining reserve steps, with the exact schedule and what it would decide.

## Time and CPU

- Another two modelers may run at the same time, so use at most 2 CPU processes.
- Commands over about 9 minutes go in the background, and you wait on them.
- Aim for 60–90 minutes. If time runs short, package the best validated variant and say so.

## Reply

At most 15 lines:

- the chosen variant;
- the held-out scores of v1 vs v2 under (A) and (B), and v2 under (C);
- the structural changes;
- the gates;
- the ZIP path;
- the top open issues;
- the reserve-step recommendation.
