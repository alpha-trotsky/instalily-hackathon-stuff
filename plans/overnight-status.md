# Overnight status

Orchestrator session started 2026-09-27. Framework: `plans/overnight-framework.md`. Paths below are relative to the repo root; the kit lives in `toronto26-participant-kit/` (data, fits, models, greybox, docs and ZIPs are under it).

Budget at start (free read, 2026-09-27): every system 2,000 remaining; market 1,400 (not touched).

## Phase 0 — shared tooling

| Item | State |
|---|---|
| `greybox/common/` (settle, battery, fit, bootstrap, gates, package) | done (see `greybox/common/README.md`) |
| Market M1+M2 reproduction within 5% | passed: 6826.742 vs reference 6826.742 (0.0%); contract, stability, bootstrap smoke test and package dry-run all pass |

## Systems

| # | System | Cap | Phase | Steps spent | Remaining | Current best model | ZIP |
|---|---|---:|---|---:|---:|---|---|
| 1 | epidemic | 1000 | not started | 0 | 2000 | persistence baseline | — |
| 2 | wildlife | 1000 | not started | 0 | 2000 | persistence baseline | — |
| 3 | ad_auction | 1000 | not started | 0 | 2000 | persistence baseline | — |
| 4 | social_contagion | 1000 | not started | 0 | 2000 | persistence baseline | — |
| 5 | power_grid | 1000 | not started | 0 | 2000 | persistence baseline | — |
| 6 | reservoir | 1000 | not started | 0 | 2000 | persistence baseline | — |
| 7 | traffic | 1300 | not started | 0 | 2000 | persistence baseline | — |
| 8 | supply_chain | 1300 | not started | 0 | 2000 | persistence baseline | — |
| 9 | hospital_queue | 1300 | not started | 0 | 2000 | persistence baseline | — |

Phases: A researcher → B reviewer → C modeler → D commit/push.

## Log

- 2026-09-27: status file created; budgets verified.
- 2026-09-27 ~00:40: Phase 0 done (toolsmith). 8 CPUs; a ~30-param 600-tick fit takes ~40 s.
