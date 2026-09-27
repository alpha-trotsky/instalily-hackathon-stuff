# Overnight status

Orchestrator session started 2026-09-27. Framework: `plans/overnight-framework.md`. Phase prompts: `plans/agent-prompts/`. Paths below are relative to the repo root; the kit lives in `toronto26-participant-kit/` (data, fits, models, greybox, docs and ZIPs are under it).

Budget at start (free read, 2026-09-27): every system 2,000 remaining; market 1,400 (not touched).

## Phase 0 — shared tooling

| Item | State |
|---|---|
| `greybox/common/` (settle, battery, fit, bootstrap, gates, package) | done (see `greybox/common/README.md`) |
| Market M1+M2 reproduction within 5% | passed: 6826.742 vs reference 6826.742 (0.0%); contract, stability, bootstrap smoke test and package dry-run all pass |

## Systems

| # | System | Cap | Phase | Steps spent | Remaining | Current best model | ZIP |
|---|---|---:|---|---:|---:|---|---|
| 1 | epidemic | 1000 | **done (v1)**; 55 reserve unspent | 945 | 1055 | 3-age-group model, m1+m3 fitted on all data, "unresolved". Cross-run R1→R2: m13 0.344, m12 0.374, no-mech 0.410, persistence 0.168. All-data m13 0.75/0.73 on R1/R2. Gates pass | `toronto26-participant-kit/submission-epidemic-v1.zip` |
| 2 | wildlife | 1000 | **done (v1)**; cap fully spent | 1000 | 1000 | food renewal + nursery (mA+mB), "unresolved" (real margin ~½ smallest bootstrap margin). Cross-run R1→R2c: mA+mB 0.417, mB+mC 0.406, mA+mC 0.302, persistence 0.066. Gates pass; no extinction/cycles in 100 constant settings | `toronto26-participant-kit/submission-wildlife-v1.zip` |
| 3 | ad_auction | 1000 | **done (v1)**; cap fully spent | 1000 | 1000 | M2+M3 (`m23f`, M3 memory fixed at τ=200), "accepted" by bootstrap rule (margin 109 vs min 78) but pinned params remain. Cross-run R1→R2c: m23f 0.391, base 0.355, persistence 0.107. Gates pass | `toronto26-participant-kit/submission-ad_auction-v1.zip` |
| 4 | social_contagion | 1000 | **done (v1)**; cap fully spent | 1000 | 1000 | M1+M2 (core population + bridge lag in base), medium confidence (bootstrap 5/5 and 3/5; real margin inside M1+M2 range). Cross-run R1→R2 0.255 vs persistence 0.223 (weak: R1 lacked seeding+incentive). All-data fit good; gates pass | `toronto26-participant-kit/submission-social_contagion-v1.zip` |
| 5 | power_grid | 1000 | B done, C running (resumed; cap spent on R2c) | 1000 | 1000 | persistence baseline (R1→R2: m12 0.367, m13 0.365, persistence 0.173) | — |
| 6 | reservoir | 1000 | B done, C running | 950 | 1050 | persistence baseline (R1→R2: m13 0.578, m12 0.577, base 0.345) | — |
| 7 | traffic | 1300 | A running (resumed; R1 745 done) | 745 | 1255 | persistence baseline | — |
| 8 | supply_chain | 1300 | not started | 0 | 2000 | persistence baseline | — |
| 9 | hospital_queue | 1300 | not started | 0 | 2000 | persistence baseline | — |

Phases: A researcher, B reviewer, C modeler, D commit/push. Phases are pipelined across systems (the next system's research overlaps the current system's review or modeling); each system still runs A, B, C in order and never exceeds its own cap.

## Log

- 2026-09-27: status file created; budgets verified.
- Phase 0 done (toolsmith). 8 CPUs; a ~30-param 600-tick fit takes ~40 s.
- epidemic A done (~15 min): R1 545 + R2 400 = 945 steps; 55 reserve. Open: rebound under long restriction (age groups?), pinned params, bed cap 155.3.
- epidemic B done: review gaps G1 (age groups), G2 (long-run level ~89 under controls), G3 (extinction floor). C started; wildlife A started in parallel.
- wildlife A done (~21 min): R1 540 + R2 400 = 940; 60 reserve. P5 gap test not run. B started; ad_auction A started.
- Status file was accidentally truncated by a cp1252 write error and rebuilt from the orchestrator's notes; later edits use UTF-8.
- epidemic C done (~23 min): shipped m1+m3 (age-group model), unresolved (bootstrap refits didn't converge). If time at the end: spend the 55 reserve on the reviewer's probe (fresh reset, school closure 1.0 from tick 0) and refit with longer warm starts.
- ~01:30 Toronto: API session limit hit; the ad_auction reviewer and social_contagion researcher died at start (0 steps). Wildlife C had already spent its 60 reserve (R2c.json; wildlife now 1000/1000 of cap). Snapshot committed; relaunched ad_auction B and social_contagion A.
- ad_auction C done (~25 min): M2+M3 shipped; 55 reserve spent on broad→narrow probe (R2c). greybox/common/bootstrap.py gained an opt-in --warm flag.
- ~02:50–06:30 Toronto: second API usage limit; all four running agents died. On disk: power_grid R2c (+50, cap spent), social_contagion R3 (+50, cap spent), traffic R1 complete (745), reservoir review mostly written. All four relaunched as resumes at ~06:35.
- social_contagion C done (resume, ~5 min): M1+M2 shipped. Tooling fix by orchestrator: package.py default data glob now skips *_battery.json. Known trap: fit.py --init keeps parameters of modules that are switched off; zero gains explicitly.
