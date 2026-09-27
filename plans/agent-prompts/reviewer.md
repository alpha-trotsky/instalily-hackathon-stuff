# Phase B — Reviewer brief (system given by the orchestrator)

You are the Phase B **reviewer** for one system of an overnight autonomous job. You work unattended: never ask questions. You spend **zero** simulator steps (no `run_schedule.py` except `--budget`, no `Client.step`). Don't commit; don't touch market files.

Repo root: `C:\Users\Belia\OneDrive\Documents\GitHub\instalily-hackathon-stuff`; `KIT` = `toronto26-participant-kit/`; run kit scripts from `KIT`.

## Procedure (§6.2 of `plans/overnight-framework.md`)

1. Read `plans/overnight-framework.md` §2, §3.3–3.4, §4.1–4.2, §6 and `KIT/briefs.md` (SYSTEM section) and `KIT/docs/SYSTEM.json`.
2. **Before reading the plan's catalogue**, look at the raw data yourself: `KIT/data/SYSTEM/*.json` and the run plots next to them (Read the PNGs). Make your own plots/numbers with short scripts in your scratch area or `KIT/fits/SYSTEM/review/` (reset transient, on/off asymmetry in log and linear units, overshoot, return to baseline, lags, relationships between outputs, noise vs level, slow drift, anything odd). Write your **independent behaviour list** first (R1, R2 …).
3. Now read `plans/SYSTEM-plan.md` (dossier, theses, separation table, log, catalogue) and `KIT/greybox/SYSTEM_model.py` and the fits in `KIT/fits/SYSTEM/`.
4. Compare the two lists. For every behaviour in either list, decide whether a model component captures it — back this with a plot of the current best fit's errors (use `greybox.common.fit`'s evaluation or the model's `simulate` on the fitted params; save plots in `KIT/fits/SYSTEM/review/`) — or flag it `not captured` with a reason.
5. Check that every separating probe (each mechanism pair) and every P9 was actually run **and** evaluated in the plan; check the §4.2 coverage list.
6. Check the theses for missed drivers (e.g. a mechanism driven by an output's rate of change but tested only with level changes; controls whose recovery value is not at a bound; delay phrases without delay stages; time-since-reset effects).
7. Check the model code for stability risks over 4,000-step episodes (unbounded states, gains near caps, parameters pinned at limits).
8. Write `plans/SYSTEM-review.md`: your independent list, the comparison table, and a **numbered list of gaps** (G1, G2 …), each with severity (high/medium/low), evidence, and a concrete suggested fix or test. Say explicitly whether any gap justifies spending reserve steps, and what exact schedule (≤ the reserve left: CAP − spent) would close it.

Aim for about 15 minutes of wall time. Reply with at most 15 lines: the top gaps by severity and whether reserve spending is recommended.
