# Overnight report and handoff (2026-09-27)

This is the single entry point for a fresh session. It consolidates the overnight run: results, per-system findings, data, tooling, lessons, and the next plan. Per-system detail lives in `plans/<system>-plan.md` (dossier, theses, spend log, behaviour catalogue, review responses, model selection, hand-off) and `plans/<system>-review.md`. The running log of the night is `plans/overnight-status.md`.

## 1. Current state

- **Public leaderboard: 0.7465 average across the ten systems** (per-system scores in §2, reported 2026-09-28; the earlier "0.71" predates them). Top competitors are around 0.8. Round 2 is planned in `plans/round2-experiments.md`.
- **Uploaded:** `toronto26-participant-kit/submission-overnight-all.zip`, which holds all ten folders at the ZIP root (nine new models plus market v1). Per-system ZIPs `submission-<system>-v1.zip` are in the same folder.
- **Submission folders:** `toronto26-participant-kit/models/<system>/` (`predict.py`, a copy of the model module, `params.json`). `params.json` stores the full natural-unit parameter dict and its `source_fit`.
- **Budget:** each system has its own 2,000 steps for the whole event; budgets are not shared. The overnight caps (1,000 or 1,300 per system) are used up. **Remaining per system:**

  | System | Remaining |
  |---|---:|
  | epidemic | 1,055 |
  | wildlife, ad_auction, social_contagion, power_grid, reservoir | 1,000 each |
  | traffic, supply_chain, hospital_queue | 700 each |
  | market | 1,400 |

  Spending more needs the user's explicit go-ahead with the logic explained first; the overnight pre-authorization is used up.
- **Upload limits:** 3 accepted uploads per system per Toronto day, shared between the public and final phases. Final uploads open 2026-09-28 12:00 and close 2026-09-30 12:00 (Toronto).

## 2. Per-system results

"R1→R2" is the local score of a model fitted on Run 1 only and scored on Run 2, with σ = 0.1×std after tick 20. It is pessimistic against public scores: the shipped models are refitted on all data, and 0.71 public came in well above these numbers.

| System | Shipped model (`greybox/<system>_model.py`) | Source fit | Confidence | R1→R2 | Persistence | Public |
|---|---|---|---|---:|---:|---:|
| epidemic | 3 age groups; m1 behaviour fatigue + m3 postponed gatherings; bed cap 155.2 fixed; importation floor | `fits/epidemic/final.json` | unresolved | 0.344 (in-sample 0.75/0.73) | 0.168 | 0.7201 |
| wildlife | 2 regions food→prey→predator with transit pipeline; mA food renewal + mB nursery; linear two-state predators; harvest refuge | `fits/wildlife/final.json` | unresolved | 0.417 | 0.066 | 0.6611 |
| ad_auction | audience rings + budget pacing + fulfillment queue; M2 exposure fatigue + M3 broad priming (τ₃ fixed at 200, multiplier bounded to [0.2, 1.8]) | `fits/ad_auction/final.json` | accepted, with pinned params | 0.391 | 0.107 | 0.8786 |
| social_contagion | 2 communities, never-disappointed core (42/29), bridge lag of about 50 ticks; M1 credibility (drops while members leave) + M2 expectations | `fits/social_contagion/v1/final.json` | medium | 0.255 | 0.223 | 0.6271 |
| power_grid | M1 synchronised cooling (load ringing), reserve multiplies share, governor; m1+m3 | `fits/power_grid/v1/m13_all.json` | moderate (M2 ruled out) | 0.439 | 0.175 | 0.7418 |
| reservoir | stock with spill cap of about 940; seasonal inflow `11.2801 + 2.2527·sin(2πt/67.7547)`; groundwater fast bank head (reset value about 560) + slow head; remobilised quality pool; M1+M3 | `fits/reservoir/v1/final.json` | M1 high, M3 unresolved | 0.533 | 0.083 | 0.8521 |
| traffic | revised two-route base (heavy-share capacity, multiplicative controls, saturating speed, 1/green signal delay, per-route buffers, speed ≤ free flow); no mechanisms | `fits/traffic/final_v1.json` | not identifiable | 0.266 (R3: 0.530) | 0.058 | 0.8335 |
| supply_chain | bounded pipeline: 3-tick path up to about 30/tick, overflow to a 21-tick path, 22% rework loop on a 10-tick cycle, mix through a 19-tick lag; no mechanisms | `fits/supply_chain/v1/base_all2.json` | not identifiable | 0.464 | 0.137 | 0.8447 |
| hospital_queue | queue/service with handover ramp, deterioration (work rises with number waiting), permanent long-stay pool; `wf` = 0; m1 fatigue + m2 handover | `fits/hospital_queue/final_m12.json` | moderate | 0.541 | 0.312 | 0.6721 |
| market | M1+M2 (v1), unchanged | `models/market/params.json` | — | — | — | 0.6838 |

## 3. Key findings per system (what the data showed)

- **epidemic**
  - The reset launches a full first wave: cases rise from about 114 to 502 at tick 22 and fall back to about 45. It repeats almost exactly on every reset, whatever the initial reading.
  - Beds cap hard at 155.3 and stay there about 50 ticks past the peak.
  - Masks act fast and proportionally: −28% on, +40% off, and 0.5 gives −14%. School closure acts slowly and raises the hospital-to-case ratio. Vaccination acts after about 7 ticks, weakly.
  - Under 200 ticks of masks + closure, cases bottomed at 15.5 and then climbed back to about 89 with the restrictions still on (fatigue). Lifting them caused a wave to 193.
  - Long-run level: about 89–107 at recovery, about 42–52 at full pulse, about 74–78 with masks + closure.
- **wildlife**
  - Boom and bust after reset: prey grow +5–6/tick, stall, then fall. The reset peak is about 196 north and 160 south, set by a hidden food stock.
  - Hunting 7 settles prey at 25.5 N / 11.4 S. The habitat pulse is symmetric (−45% N, −35% S).
  - Opening the corridor lowers all four totals, because animals in transit are not counted. Closing it brings delayed arrivals.
  - Predators decay slowly toward about 2.4, independent of level.
  - Under a joint pulse, prey hold near 10; on release they regrow capped at +6–7/tick.
- **ad_auction**
  - The budget cap throttles everything: spend pins at the cap (20).
  - Rested audiences deplete: spend 73 → 26 in 40 ticks at bid 5 / cap 100. A second pulse after 15 ticks is much weaker, and recovery takes 100+ ticks.
  - Fulfillment capacity is limited: conversions stay flat at 5.4, then drop once the backlog clears. Conversions respond with a 2-tick delay.
  - Long-run levels at the full pulse: win_rate 0.559, spend 34.4, conversions 4.47. The reset is deterministic.
- **social_contagion**
  - Removing the incentive crashes both communities within about 45 ticks to a fixed floor (A about 43–46, B about 29–33).
  - Growth continues 50+ ticks after a bridge campaign ends (a lag). Outreach has a 5–7 tick dead time. Noise is proportional (0.25%), so log units fit.
  - Bridge does nothing when seeding is 0. Under seeding alone, A settles at 230; under the full pulse, 199 / 131.
- **power_grid**
  - Price steps cause load overshoot and ringing with a 60–90 tick period, and the period depends on price.
  - Frequency caps at about 52.03 Hz. Reserve 150 cuts renewable share from about 0.34 to 0.06 within one tick.
  - The charging-off test showed no share rise, so M2 (reserve depletion) is inactive.
  - The initial share reading has no effect. The reset transient (reference price 0.8 → 1.5) is identical across runs.
- **reservoir**
  - Level is a stock with a spill cap of about 940. Delivered outflow is limited to about `16.5·(level/940)^(1/3)`.
  - Inflow is seasonal and the phase is fixed from reset. A sustained all-controls pulse drains to about 290–295.
  - After a reset, inflow runs +2.3 above season for about 12 ticks: the groundwater head starts at about 560.
  - Quality falls about 0.025 with aeration off and settles near 0.925. The recovery level depends on withdrawal depth when aeration returns.
- **traffic**
  - Demand is exactly proportional to ramp. Speed falls steeply at low load: 49 / 35.6 / 31 at flow 0 / 12 / 24.
  - Vehicle mix, not volume, causes congestion: toll 2.5 already congests route B.
  - Route learning is confirmed: the A/B split drifts slowly toward the faster route.
  - Route B shows a persistent standing queue after congestion (speed_b stays at 15 for 95 ticks).
- **supply_chain**
  - Supplier stock caps at about 362; stock floors at 0. With no orders, shipments go to 0.
  - Shipments start 3 ticks after orders.
  - After orders stop, a backlog of about 1,650 goods drains through a 22% rework loop in 10-tick steps.
  - Retail levels off because sales rise with stock (data about 975 at orders 80).
  - With maintenance off, throughput steps down to 37.2 after about 88 ticks, and a pause restores it for about 22–26 ticks.
- **hospital_queue**
  - At recovery the hospital is under-loaded (queue 23, discharges 11.49 = arrivals).
  - Handover: capacity ramps back over 25–50 ticks after staffing is restored, but drops instantly on a cut.
  - Follow-up 0 has no effect (M3 absent).
  - Electives flood the queue to 270–330. After heavy load, a residual queue of 34.5 persists for good.
  - Switching diagnostic allocation back crashes discharges for about 15 ticks.

## 4. Where the remaining error is (diagnosis)

- **The mechanism pair is not the main problem.** Switching mechanisms off barely changes scores: hospital no-mech 0.540 vs 0.541, power_grid m1 alone 0.441 vs 0.439, traffic and supply_chain pairs never beat the base. Correct pairs are worth about 0.01–0.05 per system.
- **Sustained offsets dominate.** The per-tick score is 1/(1+|err|/σ), so a persistent 1σ bias caps an observable at 0.5 for the whole 4,000-tick episode. Known offsets:
  - supply_chain shipments −2.5σ at orders 80, and retail 781 vs about 975;
  - hospital_queue elective discharges −8 to −13σ;
  - reservoir sustained groundwater excess (about 2σ) and quality (σ ≈ 0.001);
  - power_grid frequency (barely above persistence) and load-ringing period;
  - traffic route B speed +4 at the end of the long hold;
  - ad_auction reset win_rate transient (0.05 vs 0.147).
- **The control space is barely sampled.** Each system saw about 5–10 distinct settings, mostly recovery, full pulse and single-control steps. Scoring holds arbitrary settings and combinations (4 equally weighted categories: sustained, action order, recovery history, composition), so steady states elsewhere are interpolated. Mid-levels and one-sided ranges are largely untested.
- **Runs are short compared with the scored episodes:** 500–800 ticks against 4,000, so long-run levels are extrapolated.
- **Fits are under-converged.** They hit evaluation limits, restarts differ 2–5× in cost, and bootstraps were cut to 2 draws.

## 5. Next plan (proposed, not started)

1. Get the per-system public scores and rank systems by room to gain (1 − score). A system raised by 0.2 lifts the mean by 0.02.
2. **Free work first** on the weakest systems: fix structure against the worst systematic residuals, run staged fits with the base frozen and more restarts, use Powell before `least_squares` where it stalls, and check the model past 4,000 ticks.
3. **Paid steady-state mapping, with explicit approval per system.** Many holds at varied settings (mid-levels, combinations, one-sided ranges, long recovery), each held just past the settling time already measured. Write exact schedules and step counts into `plans/<system>-plan.md` for approval before spending.
4. Re-upload per system, keeping one daily slot for a rollback.
5. Ready fallback swaps: power_grid m1 alone (`fits/power_grid/v1/m1_all.json`), social_contagion M2+M3, epidemic no-mechanism.

Top open issues per system, from the hand-offs:

- **epidemic:** unconverged fits (restarts differ 2×); closure poorly pinned; never observed all three controls together or controls during the first-wave growth.
- **wildlife:** the regrowth pause and the peak after it are missed (juvenile delay pinned); worst stretch is R2 ticks 120–250; single-restart fits.
- **ad_auction:** conversion bump/dip after bid steps (τ ≈ 15–20) and the long-hold plateau/drop are missed; slow memories untested beyond 455 ticks; wrong reset win_rate; bid 0–1.5 and cap < 20 untested.
- **social_contagion:** the long-run recovery level (96.5/83.7) is extrapolated, with no recovery hold longer than 100 ticks; mid-levels untested; M1 vs M3 only moderately resolved.
- **power_grid:** frequency weak (dip after reserve release missed; secondary-control gain at its limit); ringing period wrong at price 0; middle reserve levels and price > 1.5 unobserved.
- **reservoir:** sustained groundwater excess under-predicted; quality overshoot after reset and the recovery offset missed; level extrapolation from Run 1 is weaker.
- **traffic:** a feedback oscillation under per-tick switching (smooth under holds); pairs need a staged fit to beat the base; route B end-of-hold speed, the zero-demand speed fall, the dead time at toll 0, where lane closure acts, and freight priority 0 are missing.
- **supply_chain:** shipment bias at orders 80 → low retail; the release burst is missed; production effort 0 stops production in the model, while the data show refill to the cap; the maintenance step-down at about 88 ticks is not modelled.
- **hospital_queue:** elective discharges far too low (likely separate capacity per patient class); the long-stay pool extrapolates to about 88 under long elective holds (11.5 observed); the diagnostic switch crash is missing; fatigue rate pinned.

## 6. Data inventory (`toronto26-participant-kit/data/<system>/`)

- **Run lengths are ticks.** A `*c.json` file is a copy of a run continued without a reset, so it includes the original run's ticks. Don't double count it with its source file.
- **Run schedules** are in each file's `runs[].segments` and in the plan's spend log.
- **Battery outputs** are `*_battery.json/png`. They are analysis files, not data.

| System | Runs |
|---|---|
| epidemic | R1 545, R2 400 |
| wildlife | R1 540, R2 400, R2c 460 (R2 + 60-step joint pulse and release) |
| ad_auction | R1 545, R2 400, R2c 455 (R2 + 55-step broad→narrow probe) |
| social_contagion | R1 550, R2 400, R3 50 (fresh reset, M1 probe) |
| power_grid | R1 550, R2 400, R2c 450 (R2 + 50-step charging-off test) |
| reservoir | R1 550, R2 400, R3 50 (reference pulse from reset) |
| traffic | R1 745, R2 500, R3 55 (toll 2.5 from reset) |
| supply_chain | R1 750, R2 500, R3 50 (orders 20 from reset) |
| hospital_queue | R1 750, R2 500, R2c 550 (R2 + 50 ticks of recovery) |
| market | A 600 |

## 7. Tooling (`toronto26-participant-kit/greybox/common/`; see its README)

- **Tools:**
  - `fit.py`: rollout fitter (`--model`, `--data file.json[:runs]`, `--modules`, `--init`, `--fix`, `--eval`).
  - `bootstrap.py`: parametric bootstrap and confusion matrix; `--warm` starts refits from the real fits.
  - `gates.py`: local score, stability and contract checks.
  - `package.py`: builds `models/<system>/` and the ZIP, re-tests from the extracted copy and scans for credentials. `--all-zip` builds the combined ZIP.
  - `settle.py` and `battery.py`: analysis.
  - `template_model.py` and `predict_template.py`.
- **The model-module interface** (`SPEC`, `MODULES`, `simulate`, `normalize`, `to_natural`, `to_raw`) is documented in `fit.py`'s docstring.
- **Collection:** only via `run_schedule.py` (saves every step, refuses to overwrite; `--continue` extends a run; `--confirm N`; `--budget <system>` is a free read). Continuing a run worked even hours later (power_grid, hospital_queue).
- **Gotchas:**
  - Before the fix, `--init` from another pair's fit leaked that pair's modules (fixed in `core.params_for`). All shipped params were audited clean.
  - `--init` from a fit whose mechanism gains are 0 keeps them stuck at 0.
  - `least_squares` stalls on some models (traffic, hospital_queue). Use Powell passes first, or a larger finite-difference step (`fits/traffic/review/myfit.py`, `fits/hospital_queue/review/refit.py`).
  - `battery.py` needs `--min-hold 15` on short holds (hospital_queue).
  - Pass `--data` explicitly to `package.py` if in doubt.
  - Write status and plan files as UTF-8 (a cp1252 write truncated the status file once).
  - Subagents share the session scratchpad. Keep scripts under `fits/<system>/`, and never run broad `taskkill`.

## 8. Lessons from the night

- **Put the brief's structure in the base model:** age groups, regions, pipelines, core populations, per-route buffers. The biggest gains every time came from base-model fixes the reviewers found, not from mechanisms.
- **Take the three parallel clauses in the brief as m1–m3.** Wildlife's first reading was wrong.
- **Direct A/B probes separate mechanisms.** Examples: power_grid's charging-off test, hospital's follow-up-0 test, reservoir's reset probe. Bootstrap confusion matrices were mostly weak.
- **Bound every memory rate and gain.** Near-integrator or clock-like fitted parameters extrapolate to collapse over 4,000 steps (ad_auction M3, supply_chain m1+m2). Use saturating or multiplicative forms, not additive ones that cross bounds.
- **Always include an all-controls pulse and release, and a recovery hold longer than 100 ticks.** Scoring's recovery scenarios pulse all controls together.
- **Snapshot-commit often.** Three API usage limits killed agents mid-phase. On-disk state plus "resume" prompts lost nothing.

## 9. Process notes

- Pipelined phases across systems (A researcher → B reviewer → C modeler → D commit), with prompts in `plans/agent-prompts/`.
- The API usage limits hit at about 01:30, 02:50–06:30 and 10:50–12:40 Toronto time.
- `submission-overnight-interim.zip` was a mid-run safety bundle, superseded by `submission-overnight-all.zip`.
