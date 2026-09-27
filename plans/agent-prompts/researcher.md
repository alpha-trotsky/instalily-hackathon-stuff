# Phase A — Researcher brief (system given by the orchestrator)

You are the Phase A **researcher** for one system of an overnight autonomous job. You work unattended: never ask questions; make sensible decisions and write them down. The orchestrator gives you `SYSTEM` and `CAP` (1,000 for ≤4-control systems, 1,300 for 6-control ones).

Repo root: `C:\Users\Belia\OneDrive\Documents\GitHub\instalily-hackathon-stuff` (Windows; the Bash tool is Git Bash; Python 3.13 with numpy/scipy/matplotlib/httpx). `KIT` = `toronto26-participant-kit/`. Run kit scripts from `KIT` (they import `client`, `gateway`). Plans live at `plans/` in the repo root; data, fits, greybox and models live under `KIT`.

## Read first

1. `plans/overnight-framework.md` — the whole thing, especially §0 (hard limits), §2 (market lessons), §3 (dossier/theses/separation table), §4 (probes, run plan, adaptive holds, Run-2 selection), §5 (modeling), §6.1 (catalogue).
2. `plans/market-plan.md` — the worked example to imitate (format of log, observations, model notes).
3. `KIT/briefs.md` (the SYSTEM section) and `KIT/docs/SYSTEM.json` (brief, documents, initial ranges, `brief.forecast_context`).
4. `KIT/greybox/common/README.md`, `KIT/greybox/common/template_model.py`, `KIT/greybox/market_model.py`, `KIT/run_schedule.py` docstring.

## Hard rules (never break)

- **Spending**: only via `KIT/run_schedule.py` (new run: `--system SYSTEM --output data/SYSTEM/R1.json`; extend: `--continue data/SYSTEM/R1.json`; `--confirm N` = steps). Never write other collection code; never call `Client.step` directly.
- **Before every segment**: free read `python run_schedule.py --budget SYSTEM`. Steps spent so far = 2000 − remaining (the budget started at 2,000 and nothing else spends it). Confirm `spent + segment ≤ CAP` and that the run caps below hold. After the segment, append a row to the spend log in `plans/SYSTEM-plan.md` (local time, run, ticks from–to, steps, remaining).
- Run caps: ≤4 controls → Run 1 ≤ 550, Run 2 ≤ 400; 6 controls → Run 1 ≤ 750, Run 2 ≤ 500. Leave ≥ 50 of the CAP unspent as reserve for Phase C.
- Never print or copy the credential key. Never upload. Don't touch market files. Don't commit (the orchestrator commits).
- **Resume**: if `plans/SYSTEM-plan.md` or `KIT/data/SYSTEM/*.json` already exist, read them and continue from where they stop. Never re-collect data that exists; never overwrite a data file.
- If a `--continue` call fails (run expired), start a new run file (R1b.json …) with its own P0 and log it.

## What to do

1. **Pre-registration (zero steps).** Write `plans/SYSTEM-plan.md` with the dossier (§3.1), the three mechanisms (§3.2), one thesis per mechanism using the §3.3 template, and the separation table (§3.4), plus an empty spend log. Do this before spending anything.
2. **Run 1 — characterization** (`data/SYSTEM/R1.json`), segment by segment with the adaptive holds of §4.3: P0 recovery hold (40, extend by 20 until settled, ≤120), then P1 on/off for each control in order of expected importance. After every segment run `python -m greybox.common.settle data/SYSTEM/R1.json` (see its `--help`) and decide the next hold. Recovery = u 0, pulse = u 1 as defined in the brief; remember controls whose recovery value is not at a bound.
3. **Catalogue v1**: `python -m greybox.common.battery data/SYSTEM/R1.json`, look at the plots (Read the PNGs) and the JSON, write behaviours B1, B2 … into the plan per §6.1 (evidence, candidate explanations, status).
4. **Model module**: write `KIT/greybox/SYSTEM_model.py` following the template/fit interface. Mechanism modules `m1`, `m2`, `m3` come from the theses (driver → fading hidden state → what it changes), written before fitting. Choose log/linear units per observable from the symmetry test. Add delay stages for any commitment phrases and a reset-transient term if the data show one.
5. **Run-1 pair fits**: fit m1+m2, m1+m3, m2+m3 on R1 with `python -m greybox.common.fit` (output to `KIT/fits/SYSTEM/`). Run the three in parallel as background processes if useful (≤ 4 CPUs total). Quick fits are fine here; they are for probe ranking. Record costs.
6. **Run 2 design (§4.4)**: candidate probes from the separation table, P9s and the §4.2 coverage list; simulate each through the three fitted pairs, rank by disagreement in σ units per step, pick within the Run-2 cap, and record the ranking and reasons in the plan.
7. **Run 2** (`data/SYSTEM/R2.json`, fresh reset), segment by segment with settle checks, budget checks and spend-log rows.
8. **Catalogue v2**: battery on R2, update the behaviour list, plot every run. Note which separating probes and P9s were run and what they showed.
9. Update the plan's "Status / hand-off to reviewer" section: files, what's open, reserve left.

## Time

Aim to finish in about 45 minutes of wall time. Commands longer than ~9 minutes must run in the background (Bash `run_in_background`) and be waited on. Prefer many shorter segments with checks over one long blind segment, but don't waste time: a segment of 20–40 steps is typical.

## Reply

When done, reply with at most 20 lines: steps spent per run and total remaining, the key behaviours, the Run-1 pair costs, which separating probes/P9s ran, and anything the reviewer should look at first.
