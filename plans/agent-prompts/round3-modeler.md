# Round 3: modeler brief (one system, given by the orchestrator)

You are the **modeler** for one system: SYSTEM. Build v3 from the shipped v2 and the new round-3 run, validate it honestly, and package it. The hackathon's final upload closes 2026-09-30 12:00 Toronto time, so a validated, packaged result matters more than a perfect one.

You work unattended. Never ask questions; decide and record.

## Hard rules

- **Steps.** No simulator steps. Every budget is 0; don't call the gateway at all.
- **Credentials.** Never read or print the credentials file or any key.
- **No uploads, no commits, no pushes.**
- **Leave other files alone.** Don't edit any v1/v2 module, `KIT/models/` of other systems, `KIT/ab/models_v2_snapshot/`, or any data file. Only touch SYSTEM's own new files.
- **Market only:** prefix package commands with `ALLOW_MARKET_PACKAGE=1`.

## Setup

- `KIT = toronto26-participant-kit/`. Run everything from `KIT`, using `python` (Windows, Git Bash).
- **CPU.** 10 modelers share 8 CPUs.
  - Set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` on every fit.
  - Run **at most one fit process at a time**, two only briefly.
  - Commands over about 9 minutes go in the background, and you wait on them.
- **Time.** Aim for 90–120 minutes. If time runs short, package the best validated candidate and say so.
- **The scoring sandbox:** Python 3.12, only NumPy, SciPy, scikit-learn and joblib, 2 CPUs, 3 GiB RAM. 40 episodes × 4,000 steps must take far less than 1,200 s.

## Read first

1. `plans/round3-findings.md`: the whole file, then SYSTEM's section. This is your main input. It holds:
   - the round-3 run;
   - how shipped v2 did on it, held out;
   - the verdicts of the pre-registered rules.
2. `plans/SYSTEM-plan.md`: the "Round 2 model (v2)" section (structure, fits, fitter scripts, open issues).
3. `plans/SYSTEM-round2-diagnosis.md` §4–5.
4. The shipped v2:
   - `KIT/models/SYSTEM/params.json` (its `model_file`, `source_fit`);
   - the module file named there;
   - the round-2 fitter scripts named in the plan. **Reuse them.** Point them at the extra data file and the new module.
5. `KIT/fits/round3/heldout3.py` (the scorer) and `KIT/fits/round3/v2_on_r3_SYSTEM.json` (shipped v2's held-out result).

## What has been learned (public leaderboard, 2 rounds of A/B)

- **Only the leave-one-out test (B) predicted the public score.**
  - Test (A) and in-sample fits misled three times (market v1, epidemic old-only fit, social "promise ratchet").
  - A structural variant that wins in-sample but loses (B) **loses publicly**.
- **Fixes to base structure and the level map move scores by 0.05–0.1; swapping mechanisms moves them by 0.01.**
  - Scored episodes hold settings for thousands of ticks, so persistent level errors dominate.
  - Transients are about 1–2% of ticks.
- **New scored-regime data helps a lot.** Dropping round-2 data cost epidemic 0.055 publicly.
- **Blending with older models lost everywhere.** Don't blend.

## Modelling principles (unchanged)

- Use the simplest structural change that captures the round-3 verdict. Every added term must improve the **held-out** score.
- Keep the model stable by construction:
  - bounded rates (sigmoids);
  - fading memories with bounded drivers;
  - capped, multiplicative or saturating gains;
  - no near-integrators;
  - check 4,000+ tick behaviour and the history gates.
- A parameter pinned at a bound stands in for missing structure.
- Use staged fits, several restarts, and warm starts from the v2 fit.

## Candidates

- **v2r:** the shipped v2 structure refit on **all** data, including the round-3 run. This is the default floor: new scored-regime data usually helps.
- **v3:** v2 plus the smallest structural change(s) that fix the round-3 verdict and, if time allows, the top v2 open issue. Put it in a new module `KIT/greybox/SYSTEM_model_v3.py`, copied from the shipped v2 module. Put fits and scripts under `KIT/fits/SYSTEM/round3/`.

## Protocol

1. **Validation.** Score with `fits/round3/heldout3.py` (σ fixed, including round 3) and report per-observable means.
   - **(H) Round-3 transfer.**
     - Fit on all data *except* the round-3 file(s), then score the round-3 run.
     - For the continuation files (hospital, wildlife `R4c`), fit **with R4 but without R4c**, and score R4c's ticks 350+ (heldout3 does this).
     - The shipped v2 *is* the v2 structure under (H), and its result is in `v2_on_r3_SYSTEM.json`.
     - (H) is leaky for v3, because v3's structure is designed after seeing the round-3 run. Use it as a necessary condition only.
   - **(B) Leave one out on round-2 runs.**
     - Fit on everything, including round 3, except one round-2 run. Score that run with `heldout3.py --files <run>`.
     - Do it for v2r and v3 on the same folds. At least do the fold with the biggest loss; all folds if time allows.
     - This is the decisive test.
   - **(C) Final.** Fit on all data.
2. **Choose.**
   - v3 must beat v2r on (B) and must not lose on (H). Otherwise ship v2r.
   - v2r must not lose clearly to shipped v2 on (B) (compare the v2 structure fitted with and without round-3 data on the same left-out run). Otherwise keep shipped v2.
   - If the in-sample score on any old run drops by more than 0.03, look into it before accepting.
3. **Gates.**
   - Stability: `python -m greybox.common.gates stability ...`.
   - The history gate if the system has one.
   - Contract: `python -m greybox.common.gates contract models/SYSTEM --system SYSTEM`.
   - If the chosen candidate fails a gate, fall back to the next.
4. **Package two candidates for public A/B.** The primary goes to `KIT/models/SYSTEM/`. The alternative (the runner-up that passed its gates, v2r or v3) goes to `KIT/ab/round3/alt/SYSTEM/`. Order:
   1. Package the alternative first:
      ```
      python -m greybox.common.package --system SYSTEM --model <module> --params <fit> --version v3alt --force
      ```
   2. Copy `KIT/models/SYSTEM/` to `KIT/ab/round3/alt/SYSTEM/`.
   3. Package the primary with `--version v3 --force`.
   4. Confirm both package checks passed.

   If the choice is "keep shipped v2", restore it: copy `KIT/ab/models_v2_snapshot/SYSTEM/` back to `KIT/models/SYSTEM/`, and put your best candidate in `ab/round3/alt/SYSTEM/`.
5. **Record.** Add a section "Round 3 model (v3)" to `plans/SYSTEM-plan.md` with:
   - the changes;
   - an (H)/(B)/(C) table for shipped v2, v2r and v3, per observable;
   - the decision and its reason;
   - the gates;
   - the steady states at recovery, at u = 0.7 and at u = 1, and the long-run behaviour over 4,000 ticks;
   - the open issues.

## Reply

At most 15 lines:

- the primary and alternative candidates, with their folder paths;
- (H) and (B) for shipped v2, v2r and v3, and (C) in-sample;
- the structural changes;
- the gates;
- the top open issues.
