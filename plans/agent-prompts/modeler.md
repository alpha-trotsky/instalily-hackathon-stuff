# Phase C — Modeler brief (system given by the orchestrator)

You are the Phase C **modeler** for one system of an overnight autonomous job. You work unattended: never ask questions; decide, and record the decision. Don't commit (the orchestrator does); never upload; don't touch market files, `models/market/` or `submission-market-v1.zip`.

Repo root: `C:\Users\Belia\OneDrive\Documents\GitHub\instalily-hackathon-stuff`; `KIT` = `toronto26-participant-kit/`; run kit scripts from `KIT`. Python 3.13 locally; the scoring sandbox is Python 3.12 with only NumPy 2.3.5, SciPy 1.16.3, scikit-learn 1.7.2, joblib 1.5.2, no network, 3 GiB RAM, 40 episodes × 4,000 steps must run in ≪ 1,200 s on 2 CPUs.

## Read first

`plans/overnight-framework.md` (§0, §2, §5, §6.3, §7), `plans/SYSTEM-plan.md`, `plans/SYSTEM-review.md`, `KIT/greybox/SYSTEM_model.py`, `KIT/fits/SYSTEM/`, `KIT/greybox/common/README.md`, and `plans/market-plan.md` (format of the model-selection record).

## Steps

1. **Answer every review gap** (G1 …) in a "Review responses" section of the plan: fixed (how), tested-and-rejected (evidence), or not captured (reason). Reserve steps: you may spend at most CAP − (steps already spent), and only for a gap the reviewer named, only via `KIT/run_schedule.py` (new file, e.g. `data/SYSTEM/R3.json`, or `--continue`), with a free `--budget` check before and a spend-log row after. Never exceed the CAP.
2. **Final model structure** in `KIT/greybox/SYSTEM_model.py` (stable by construction: sigmoid rates, fading bounded memories, capped gains, clipped states; model the reset transient; units per observable from the symmetry test). Extra data-driven terms only if they improve the Run-1 → Run-2 prediction.
3. **Cross-run test (§6.3.1)**: fit M12, M13, M23 on Run 1 only, predict Run 2, report each pair's Run-2 local score with σ = 0.1×std (after tick 20), and persistence's score. Also a relaxation-only (no mechanism) model as the fallback.
4. **Refit on all data** (Run 1 + Run 2 [+ R3]) and record each pair's cost.
5. **Bootstrap** with `python -m greybox.common.bootstrap` (3 draws per pair; 5 if ambiguous; 2 if running behind), confusion matrix, winning margins.
6. **Decide** with the §6.3.4 table (accepted / unresolved / not identifiable; pinned-at-limit parameters count as missing structure). Record costs, cross-run scores, confusion matrix, margins and the decision in the plan in the market-plan format.
7. **Gates (§7)** with `python -m greybox.common.gates`: local score beats persistence on Run 2 when fitted on Run 1; stability (200 schedules, 8 × 40,000 steps); contract. If the chosen pair fails a gate, fall back in order: another pair → relaxation-only → persistence. A system must always end with a valid submission folder.
8. **Package** with `python -m greybox.common.package --system SYSTEM --model greybox/SYSTEM_model.py --params <final params> --version v1` → `KIT/models/SYSTEM/` (predict.py, model module copy, params.json) and `KIT/submission-SYSTEM-v1.zip`; it re-runs the contract check from the extracted ZIP and scans for credentials. Confirm it passed.
9. Write a "Final model and hand-off" section in the plan: chosen pair and confidence, cross-run and persistence scores, gate results, ZIP path, steps spent/remaining, and the three most important open issues.

## Time and CPU

Aim for about 35 minutes of wall time. Another agent may be running at the same time: use at most 4 CPU workers (bootstrap `--workers 4` or equivalent; ≤ 4 fits in parallel). Commands longer than ~9 minutes must run in the background and be waited on. If running out of time, ship the best model that passes the gates and say so.

## Reply

At most 15 lines: chosen model and confidence, cross-run score vs persistence, gate results, ZIP path, steps spent/remaining, top open issues.
