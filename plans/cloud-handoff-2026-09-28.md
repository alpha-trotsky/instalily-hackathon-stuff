# Cloud handoff: instalily-hackathon-stuff, 2026-09-28

This file carries a local Claude Code session over to a cloud session. It is deliberately **not in git**. It holds:

- the task in progress;
- the standing rules;
- the new information (per-system public scores);
- the analysis done this session;
- the scratch scripts, which lived outside the repo.

There are no credentials in this file.

**Repo state:**

- `main` is at `a5237bb` ("Consolidated handoff in overnight-report.md; point CLAUDE.md at it"). It is pushed and in sync with `origin/main`.
- The working tree was clean when this was written. Nothing from this session was committed.
- The only files git ignores are the credentials JSON and `__pycache__`. In the cloud, the gateway key comes from the environment (see CLAUDE.md: `gateway.make_client()` with no key uses the cloud proxy).

**Start by reading:**

1. `CLAUDE.md`.
2. `plans/overnight-report.md` (the consolidated handoff of the overnight run).
3. This file.
4. Per-system detail when you need it: `plans/<system>-plan.md`, `plans/<system>-review.md` and `toronto26-participant-kit/briefs.md`.

---

## 1. The pending task (user's words, verbatim)

> Epidemic, hospital queue, market, social contagion, powergrid, and wildlife have all been predicted not great. They indicate to me that modelling choices are off and leave things unaccounted for.
>
> On the other hand the rest (anything above 0.8) indicates to me correct modelling choices that just need more domain to produce a better fit.
>
> I want you to go into the tank, think and analyse the modelling and the domain exploration for the models that did not do well first. Hypothesize on why not. Create domain tests on how to improve understading of the relationship. Critique them given that you only have anywhere from 1400 to 700 steps left. Finalize the experiment choices. Present the experiment choices to me. I want experiments to clearly show what solution will be preferred based on what the experiment tells us AND to argue that this domain exploration will capture all of the domain/range mapping and will not let any important relationships go unnoticed.
>
> Then i want you likewise to tank and present your way of moving forwards with the models that are already working well and on how their predictive power can be improved with more data.
>
> Reread the claude.md, read the overnight file, and read the case information case by case.
>
> DO NOT spend steps until i say you can spend steps after approving this plan.

**Status:**

- The reading is done: CLAUDE.md, the overnight report, `briefs.md`, `PROMPT.md`, and all ten plans and nine reviews.
- A free in-sample diagnostic and model screening of the draft experiments are done for 6 systems (section 5).
- **Not yet done:**
  - the finished written plan presented to the user;
  - screening for reservoir, ad_auction, supply_chain and traffic. The reservoir screen was interrupted before it ran.
- **No steps have been spent.** Every step needs the user's explicit approval of the plan first.

Suggested deliverable:

- Write `plans/round2-experiments.md` with, per system:
  - the diagnosis;
  - ranked hypotheses;
  - experiments, each with its exact schedule, step count, predictions under each hypothesis and decision rule;
  - a coverage matrix;
  - a critique, what was cut, and the residual risk.
- Give a digest in chat.
- Per the project convention, exact schedules also go into `plans/<system>-plan.md` before spending.
- Also add the public scores to the table in `plans/overnight-report.md` §2. They are not recorded in the repo yet.

## 2. Standing rules (from memory and CLAUDE.md; still in force)

- **Steps are irreversible.** Before any paid run:
  - explain in detail what the run is, why it has that design, what each outcome would mean, and the exact step cost;
  - then wait for an explicit "yes".
  - The overnight pre-authorization is used up.
- Spend steps **only** via `toronto26-participant-kit/run_schedule.py`. It saves every step, refuses to overwrite, and `--confirm N` must equal the step count.
  - `--budget <system>` is a free read.
  - `--continue file.json` extends a run.
- Log every spend in `plans/<system>-plan.md`.
- **Never upload.** The user uploads.
- Never print or copy the gateway key, and never put it in a file or ZIP.
- Don't touch the market data, `models/market/` or `submission-market-v1.zip` unless the user asks for market work. Market improvement is now in scope (it is one of the weak six), but ask first.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Commit and push only when asked, or as part of an agreed workflow.
- Write plan and status files as UTF-8 (a cp1252 write once truncated a file).
- The user sees only the overall public number per system (no per-category breakdown, per an earlier memory note). It may still be worth asking whether the "View" link shows per-observable or per-category scores.
- **Upload limits:**
  - 3 accepted uploads per system per Toronto day, shared between the public and final phases.
  - Final uploads opened 2026-09-28 12:00 and close **2026-09-30 12:00 Toronto**.
  - **Public uploads do NOT become final submissions.** Each system needs its own final upload before the deadline, so remind the user and reserve slots.

## 3. Budgets (free read, 2026-09-28 ~13:50 UTC)

| System | Steps left | Public score |
|---|---:|---:|
| social_contagion | 1,000 | **0.6271** |
| wildlife | 1,000 | **0.6611** |
| hospital_queue | 700 | **0.6721** |
| market | 1,400 | **0.6838** |
| epidemic | 1,055 | **0.7201** |
| power_grid | 1,000 | **0.7418** |
| traffic | 700 | 0.8335 |
| supply_chain | 700 | 0.8447 |
| reservoir | 1,000 | 0.8521 |
| ad_auction | 1,000 | 0.8786 |

The average is 0.7465. The user's earlier "0.71" was before these per-system numbers. Top competitors are around 0.8.

These public scores are the uploads of `submission-overnight-all.zip`, which contains market v1.

## 4. Key findings of this session's analysis

### 4.1 Public vs in-sample: a diagnostic

`insample.py` (appendix) runs each shipped `models/<s>/predict.py` on all our data and scores it with σ = 0.1×std after tick 20.

| System | Public | In-sample | Gap (public − in-sample) | Per-observable in-sample |
|---|---:|---:|---:|---|
| ad_auction | 0.879 | 0.588 | +0.29 | win 0.66, spend 0.68, **conv 0.42** |
| supply_chain | 0.845 | 0.557 | +0.29 | **shipments 0.43**, supplier 0.54, retail 0.69 |
| traffic | 0.834 | 0.555 | +0.28 | fa 0.53, **fb 0.43**, sa 0.65, sb 0.60 |
| power_grid | 0.742 | 0.532 | +0.21 | **load 0.45, freq 0.43**, share 0.71 |
| reservoir | 0.852 | 0.680 | +0.17 | level 0.87, inflow 0.71, outflow 0.88, **quality 0.26** |
| wildlife | 0.661 | 0.521 | +0.14 | prey N 0.59, **pred N 0.41**, prey S 0.63, **pred S 0.46** |
| hospital_queue | 0.672 | 0.556 | +0.12 | wait 0.58, queue 0.71, **discharges 0.38** |
| market | 0.684 | 0.660 | +0.02 | price 0.65, **volume 0.47**, depth 0.87 |
| epidemic | 0.720 | 0.739 | **−0.02** | cases 0.77, hospital 0.71 |
| social_contagion | 0.627 | 0.738 | **−0.11** | A 0.75, B 0.72 |

Our data is deliberately hard (switches and transients), so public is normally far **above** in-sample. For epidemic and social_contagion, public is at or **below** in-sample. The models fit what we measured but fail on the scoring distribution: **extrapolation failure** into regimes we never observed, mainly long-run levels at settings we never held.

- Wildlife, hospital and power_grid have poor in-sample fits: structural misfit on data we already have. Free model fixes should help there.
- Market suffers from both problems.
- **Caveat:** the organizer σ is unknown and may scale differently per system. For example, our epidemic σ is inflated by the 500-case first wave. Treat this as a signal, not proof.

### 4.2 Theses for the plan

- **Mechanism choice is not the main lever.** Traffic and supply_chain shipped with *no* mechanisms and scored 0.83–0.84. Overnight, mechanism swaps changed local scores by only 0.01–0.05, while base-structure fixes moved them by 0.1–0.3. This partly corrects the user's framing: "modelling choices are off" is right, but it means base structure and level mapping, not the mechanism pair. Say this clearly but respectfully.
- **The long-run level map dominates the score.** Episodes are 4,000 steps, so transients are a few percent of ticks. A persistent 1σ offset caps an observable at 0.5 for the whole hold. Our longest holds were about 200 ticks, and most settings were never held to steady state.
- **The overnight probe ranking had a blind spot.** It ranked probes by *disagreement between candidate pair fits*. All the candidates share one base, so they agree even where all of them extrapolate wrongly. The screening below confirms this:
  - social, epidemic and power_grid candidates disagree by less than 2σ in untested regimes;
  - wildlife and hospital disagree by 3–6σ.

  New experiments must be chosen by **coverage of the scoring distribution**, not by pair disagreement.
- **The scoring distribution** (docs):
  - 40 episodes × 4,000 steps: 10 sustained operation, 10 action order, 10 recovery spacing, 10 joint intervention.
  - Every episode starts from a reset, so controls are likely applied during the reset transient.
  - Recovery scenarios pulse to 70–100% of the pulse distance **independently per control**, so intensities 0.7–1 matter.
  - The other categories probably use the recovery and pulse family and single-control or joint compositions. Mid-levels and the other side of the recovery value are a hedge.
- **The simulator is deterministic.** Measurement noise is about 0.2–0.5% and the reset state is fixed, so one observation per setting is enough. Spend steps on new states, not on replicates.
- **Design patterns to use:**
  - **Controls from tick 0.** Scoring starts from reset, and this saves a P0.
  - **Continuation ladders.** Step through levels, each held just past its settling time. Go up and back down to expose hysteresis and order effects.
  - **Gray-code corner tours.** Each step flips one control, so compositions and single-control steps are covered in different backgrounds.
  - **One or two long holds (≥ 250–300 ticks)** at the most common scoring regimes: the recovery action and the centre of the pulse box.
  - **Recovery-spacing runs:** pulses at intensities 0.7, 0.85 and 1, separated by a short and a long gap.
- **Coverage argument template:** for each system, build a matrix of relationships against evidence. Mark each cell as existing data ✓, new experiment ●, or explicit extrapolation ✗ with its justification. The relationships are:
  - (a) steady-state gain of each control on each observable at u = 0, about 0.7 and 1, to catch nonlinearity;
  - (b) the other side of recovery, where recovery is not at a bound;
  - (c) pairwise and all-joint interactions;
  - (d) on/off dynamics, dead times and asymmetry;
  - (e) history: gap and order effects;
  - (f) long-run levels (≥ 250-tick holds);
  - (g) the reset transient with controls from tick 0.

  Be honest that "all relationships" cannot be guaranteed with 700–1,400 steps. Name the residual extrapolations.
- **The public leaderboard is a zero-step A/B oracle.** Scoring uses the same 40 public episodes for every upload, so paired differences between variants are reliable. Use spare public slots to test model variants that are expensive in steps, for example social_contagion's long-run recovery equilibrium at 96/84 vs at the floor. Budget the slots: 3 per system per day, shared with the final phase, and the final upload must be separate.
- **Suggested process:**
  1. Free structural fixes on existing data (wildlife predators, hospital per-class elective capacity, power_grid thermostat load model, supply_chain D-level shipments bias).
  2. Run round 2 at about 80% of each budget, after approval.
  3. Refit.
  4. Public A/B.
  5. A small round 3 for confirmation.
  6. Final uploads before 09-30 12:00.

## 5. Per-system hypotheses, draft experiments and screening results

Screening simulates the candidate all-data fits on each draft schedule (`screen.py` plus `scr_*.py`, appendix). Values are the mean of the last 10 ticks of each segment. "dis" is the mean pairwise disagreement in score σ.

**Caveat on all numbers:** these are model predictions, not data. Agreement between models is not evidence of being right (4.2).

### social_contagion (1,000 steps; 0.627, the lowest)

Observables A and B; σ(0.1std) = 6.14 / 3.46.

**Unknowns, ranked by scoring impact:**

- **U1: the long-run recovery equilibrium.** The model gives 96.5/83.7, but no recovery hold longer than 100 ticks was ever observed. Recovery ticks are a large share of recovery-spacing episodes.
- **U2:** the long-run path after a crash floor (43/31).
- **U3: pulse-box intensity 0.7–0.9.** The model predicts strong saturation: seeding 4.5 alone gives A 189, against 230 at seeding 9.
- **U4: partial incentive drops.** The model predicts that a 2→1 drop crashes A from 193 to 102. That is a huge untested extrapolation of M2's linear gap form.
- **U5: repeated pulses with short gaps.** M1's departure-driven credibility is the m12 vs m23 separator.
- **U6: compositions.** Seeding+incentive at bridge 0, and bridge 0.42.

**Draft SC-1** (fresh reset, 600 steps):

| Ticks | Action | m12 / m23 / m2 prediction (A, B) |
|---|---|---|
| 0–119 | pulse u0.8 (seeding 7.2, incentive 1.6, bridge 0.48) | 196/128 for all three |
| 120–419 | recovery 300 | crash to about 50–54/37–42; +150: 60–70/57–63; +300: **82/79 (m12) vs 101/88 (m23) vs 92/85 (m2)**, dis 1.7σ |
| 420–479 | pulse 2 (after the long gap) | |
| 480–499 | recovery, short gap 20 | |
| 500–559 | pulse 3 | ≈ 172–174 for all |
| 560–599 | recovery 40 | |

**Draft SC-2** (fresh reset, 330 steps):

| Action | Steps | m12 prediction (A, B) | m23 prediction (A, B) |
|---|---:|---|---|
| seeding 4.5 | 90 | 189/96 | |
| + incentive 2 (bridge 0) | 70 | 193/111 | |
| incentive 1 | 50 | **102/56** | **123/67** |
| incentive 0 | 50 | | |
| seeding 0 | 70 | | |

The drop segments disagree by 1.3–1.9σ.

**Decision rules (draft):**

- **Recovery tail.** Fit an asymptote to the recovery tail.
  - Within ±10% of 96/84: keep the structure.
  - Flat at the floor: a core-only equilibrium (reduce reconsideration and organic growth).
  - Higher: a larger organic pool.
- **Intensity.** Compare the u0.8 plateau with interpolation between recovery and u=1 (199/131) to set the curvature of the saturation.
- **Spacing.** Take the pulse-3 20-tick gain over the pulse-2 gain.
  - Below 0.85: M1 is confirmed, keep m12.
  - About 1: switch to the m23 fallback.
- **Partial drop.** Measure how big the crash is at incentive 1.
  - About half: the linear M2 form is right.
  - Full crash on any cut: disappointment is triggered by any cut.
  - None until 0: a payment-based structure.

Total 930 steps. Consider trimming to keep a ~100 reserve.

### epidemic (1,055 steps; 0.720)

σ = 8.34 cases / 4.19 beds.

**Unknowns:**

- **U1: long-run levels under sustained controls.** Model equilibria: rec 107, pulse ≈ 42–54, mask 65, mc 74, vacc 77. Data only reach tick 240 (mc plateau 89 at 220–239, where the model says it will decline further).
- **U2:** the sustained effect of vaccination (weakly identified).
- **U3:** controls during the first wave from reset (all episodes).
- **U4:** the all-three composition, never observed.
- **U5:** the long-run hospital level and ratio.
- **U6:** fatigue build and recovery.
- **U7:** period and damping of the endemic oscillation.

**Draft EP-1** (fresh reset, 450): all three at 0.85 (mask 0.85, closure 0.85, vacc 0.00255) from tick 0 for 300, then recovery 150.

| Segment | m13 (shipped) | m12 | base | m23 |
|---|---|---|---|---|
| Ticks 0–39 | 182/154 | 190/149 | 243/155 | 241/155 |
| Ticks 200–299 | 54/42 | 52/40 | 59/44 | 56/43 |
| Release | 143–160 | | | |
| rec +150 | about 88–92 | | | |

**Rule:** if the level at 200–299 is ≥ 80 (the same insensitivity as R2's mc plateau), the equilibrium structure is wrong: strengthen fatigue or risk behaviour. If it is about 50–55, the structure is right, so just refit.

**Draft EP-2** (fresh reset, 400): vaccination 0.003 from tick 0 for 250, then off for 150. This also tests throttling while the hospital is capped from reset.

| Segment | Model prediction |
|---|---|
| Ticks 150–249 | 72–79 |
| Off +150 | 98–105 |

**M2 test:** does the decline continue for ≥ 10 ticks after vaccination stops (developing immunity)?

**Draft EP-3** (fresh reset, ~200–250): a single-control long hold, mask 0.7 or closure 1.0, from reset.

| Case | First wave (models) | Ticks 150–249 |
|---|---|---|
| mask 0.7 | 247–287 | ≈ 84–87 |
| closure 1.0 | 274–319 | ≈ 92–99 |

The first wave disagrees by 2.8σ, so closure from reset is the reviewer's old top reserve probe.

**Composition argument:** the model is multiplicative in transmission. MCV, V, MC (have) and M or C anchor the 8 corners; MV and CV are interpolated.

### wildlife (1,000 steps; 0.661)

σ: prey about 4.5 / 4.1, predators 0.057 / 0.055. **Predators are half the observables, with tiny σ, and score 0.41–0.46 in-sample.**

- **Free fix first:** the predator block.
- **Unknowns:**
  - the pulse-box interior: hunting 4.9–7 is strongly nonlinear, with habitat 0.1–0.37 and corridor 0.7–1;
  - release boom and bust after joint pulses: the peak comes out 140 against 172 in the data, and the stall is missed. This happens in every recovery-spacing episode, and the R2c release was cut at 25 ticks;
  - gap memory (food stock vs nursery);
  - predator long-run and slow tail;
  - habitat and corridor mid-levels.

**Draft WL-1** (fresh reset, 500):

| Segment | Steps | Result |
|---|---:|---|
| Joint 0.85 (hunting 5.95, protection 0.235, corridor 0.85) from reset | 80 | prey N **12.7 (AB) vs 31–41 (others)**, dis 3.9σ |
| Recovery (release +30: AB 131/124 vs BC 115/96) | 120 | |
| Joint 1.0 (7, 0.1, 1) | 60 | |
| Recovery, short gap | 30 | dis 3.1σ |
| Joint 0.7 (4.9, 0.37, 0.7) | 60 | prey N **24.5 (AB) vs 34–60**, dis 2.7σ |
| Recovery | 150 | |

**Draft WL-2** (fresh reset, 350):

| Segment | Steps | Result |
|---|---:|---|
| Hunting 5 | 80 | AB 66/40 vs AC 55/43 vs base 72/53 |
| + habitat 0.37 | 60 | AB 17 vs base 67 |
| Habitat 0.37 alone | 60 | |
| + corridor 0.7 | 60 | |
| Corridor 0.7 alone | 60 | |
| Recovery | 30 | |

Long holds (2,000 ticks) at joint 0.7 disagree by 6.3σ (prey N 16 vs 37–61). AC predicts predators collapsing to 0.48 at joint 1: **the pulse box is exactly where the models diverge.**

**Rules:**

- The pair ranking comes from the joint-pulse levels.
- If the release overshoot is again ≥ 20% above the model, add a cohort delay or a nursery food stock.
- The gap response separates food-stock memory (mA) from the juvenile deficit (mB).

Total 850 steps; reserve 150.

### power_grid (1,000 steps; 0.742)

σ: load 1.91, frequency 0.081, share 0.0143. In-sample, load is 0.45 and frequency 0.43.

- **Free fixes:**
  - a thermostat-population load model (the period depends on price, and the ringing is long);
  - the secondary frequency loop (kz is pinned);
  - the share spike after release.
- **Unknowns:**
  - mid-level reserve (pulse box 105–150): the model assumes share ∝ 1/(1+w·Rd), which gives 0.17 / 0.12 / 0.09 at 40 / 80 / 120 with frequency 50.1–51.0, and assumes no clip below 150;
  - interconnector 0.2–0.44 and 0.5;
  - price 0–0.45 and above 1.5;
  - charging mid-levels;
  - P3 pairs;
  - the M2 loophole: reserve depletion only on dispatch holds longer than 150;
  - recovery spacing.

  The candidates agree (dis < 2.5σ), so they cannot be used to screen.

**Draft PG-1** (fresh reset, 430):

| Segment | Steps | m13 prediction |
|---|---:|---|
| Price 2.0 (from reset) | 80 | load 92 |
| Price 0.45 | 70 | load 113 |
| Price 1.5 | 70 | load 101 |
| Reserve 40, 80, 120 | 35 each | |
| Reserve 80 + ic 0.5 | 35 | |
| ic 0.5 | 35 | share 0.289 |
| Recovery | 35 | |

**Draft PG-2** (fresh reset, 400):

| Segment | Steps |
|---|---:|
| Joint 0.7 (price 0.45, reserve 105, charging 0.3, ic 0.44) | 100 |
| Recovery | 60 |
| Joint 1 | 60 |
| Recovery | 30 |
| Joint 0.85 | 100 |
| Recovery | 50 |

Consider one long dispatch hold (reserve 150, charging 0) of 300+ ticks to close the M2 loophole.

### hospital_queue (700 steps; 0.672)

σ: wait 2.89, queue 11.8, discharges 0.44. In-sample, discharges are 0.38; elective discharges are 8–13σ too low.

- **Free fix:** per-class (elective) capacity.
- **Knife edge:** at recovery, capacity (about 11.4–16.7) barely exceeds arrivals (11.49). The shipped model predicts:
  - **electives 5 at staffing 20 → queue 308, discharges 5.9** (base v5: 281 / 9.0);
  - **staffing 12 with no electives → queue 297.**

  These are big, untested regimes that sustained holds will visit.
- **Lq long-stay pool:** after a 1,500-tick elective hold, the shipped model leaves a permanent queue of 69 at recovery; the base leaves 23. Only 11.5 was ever observed.

**Draft HQ-1** (fresh reset, 300):

| Segment | Steps |
|---|---:|
| Electives 5 | 60 |
| Electives 10 | 60 |
| Staffing 15 + electives 10 | 60 |
| Staffing 15 alone | 60 |
| Recovery | 60 |

Disagreement is 2–3.4σ.

**Draft HQ-2** (fresh reset, 400):

| Segment | Steps | final_m12 | base |
|---|---:|---|---|
| Joint 0.7 (staffing 9.5, electives 14, diag 0.645, urgent 0.88, overtime 0.7, follow-up 0.3) | 100 | discharges 2.6 | 6.9 |
| Recovery | 60 | | |
| Joint 1 | 60 | | |
| Recovery | 180 | queue 51 | 35 |

Joint 0.7 disagrees by 4.6σ. The recovery tail measures the Lq drain.

This is over budget (700 total). Trim, for example: HQ-1 to 250 and HQ-2 to 350, keeping a 100 reserve.

### market (1,400 steps; 0.684)

σ: price 0.92, volume 0.021, depth 1.93. There is a single 600-tick run with singles only.

- **Joint rate+tax has never been observed**, yet it is half the scoring (all recovery pulses, plus the joint category). The models assume additivity: the joint pulse gives price about 74 and depth 41.
- The plan's own hypothesis, "price impact ∝ 1/depth", predicts an interaction.
- Also untested: mid-levels, long holds, order swaps, and step vs ramp (M3).

**Draft MK-1** (fresh reset, 600):

| Segment | Steps | Prediction |
|---|---:|---|
| Joint 1 (rate 0.1, tax 0.05) from reset | 150 | dis 5.2σ, mainly the transient |
| Recovery | 150 | |
| Joint 0.7 (0.07, 0.035) | 125 | price ≈ 79–81, depth 55–56 |
| Recovery, short gap | 50 | |
| Joint 1 | 125 | |

**Draft MK-2** (fresh reset, 600): an order swap and mid-levels.

| Segment | Steps | Prediction |
|---|---:|---|
| Rate 0.05 | 125 | m12 82.7 vs m23 76.2 |
| + tax 0.05 | 125 | |
| Tax only | 125 | |
| Tax 0.025 | 125 | depth ≈ 66 |
| Recovery | 100 | |

That leaves about 200 in reserve.

### Strong systems: drafts only, no screening done yet

For each: pulse-box interior levels, mid-level ladders and one long hold, with ~100–250 kept in reserve.

- **ad_auction (1,000).**
  - Weak observable: conversions (bump and dip, capacity plateau).
  - Untested: bid mid-levels (0.75, 3.25, 4.05), cap 20–100 at high bid, breadth 0.7.
  - The slow memories (M2 τ 150, M3 τ 200, fixed by hand) are unverified beyond 455 ticks.
  - **AD-1** (500): pulse u0.7 (bid 4.05, cap 76, breadth 0.7) from reset for 250, recovery 100, pulse u1 50, recovery 25, pulse u0.85 75.
  - **AD-2** (300): bid ladder at cap 100 (3.25, 2.0, 0.75), recovery, then cap 50 and 30 at bid 5.
- **reservoir (1,000).**
  - Quality is the weak channel (0.26; σ 0.001).
  - Release 10–11 is a knife edge for the level (sweep: 10 → 923, 10.5 → 563–635, 11 → 283).
  - Pulse-box interior: release 9, irrigation 5.6, depth 0.7, aeration 0.3.
  - Aeration mid-levels are untested.
  - The long recovery quality drift (−3e-5/tick) is unresolved.
  - **RS-1** (450): pulse u0.7 from reset for 250, then recovery 200.
  - **RS-2** (450): release 10.5 for 150, then aeration 0.3 for 80, aeration 0.15 + depth 0.5 for 80, aeration 0 + depth 0.5 for 80, recovery 60.
  - The screening script `scr_rs.py` is in the appendix. It was interrupted and has not run.
- **supply_chain (700).**
  - The D-level shipments bias (31.7 vs 34.8) is a free fix. The retail equilibrium (781 vs 975) follows from it.
  - Receiving mid-levels set shipments (0.35 → 17.2).
  - Maintenance 0.3 is untested.
  - **SU-1** (400): pulse u0.7 from reset for 150, recovery 60, pulse u1 60, recovery 30, pulse u0.85 100.
  - **SU-2** (200): orders 80 with receiving 1.0, 0.7 and 0.5, then maintenance 0.3, 50 each.
- **traffic (700).**
  - Weak observable: flow_b.
  - The pulse box at u 0.7–0.85 is a different degree of congestion.
  - Untested: toll 1.5, freight 0, signal and lane mid-levels.
  - Recovery spacing drives the drain and speed memory.
  - **TR-1** (400): joint u0.7 from reset for 150, recovery 50, joint u1 80, recovery 30, joint u0.85 90.
  - **TR-2** (~200): mid-level single controls on top of D (ramp 1, toll 5), for example freight 0, signal 0.3, lane 0.5 + clearance 0.5.

## 6. Next steps for the cloud session

1. Finish screening reservoir, ad_auction, supply_chain and traffic with `screen.py`.
2. Finalize the experiments for each system:
   - trim each to about 80–90% of its budget;
   - write predictions under each hypothesis and a decision rule;
   - build the coverage matrix (a)–(g);
   - critique it: what was cut, and the risks left.
3. Write `plans/round2-experiments.md` and present a digest. Also:
   - propose the free fixes to do first;
   - propose the public A/B plan and the upload-slot schedule, including the separate final uploads.
4. Wait for the user's approval before any step. Then run per system via `run_schedule.py`: free `--budget` check first, log the spend, commit a snapshot after each run.
5. The overnight subagents hit API usage limits three times. Commit snapshots often.

## 7. Appendix: scratch scripts (these lived outside the repo)

Put them anywhere and run from `toronto26-participant-kit/`. Adjust the `sys.path.insert` lines to wherever you save `screen.py`.

### screen.py

```python
"""Simulate candidate fits on draft schedules; print end-of-segment levels and pairwise disagreement in score-sigma."""
import json, sys, re, numpy as np
sys.path.insert(0, '.')
from greybox.common import core


def load_params(p):
    d = json.load(open(p))
    return d['params'] if 'params' in d else d


def ranges_for(system):
    doc = json.load(open(f'docs/{system}.json'))
    docs = doc['documents']
    docs = docs['documents'] if isinstance(docs, dict) else docs
    txt = ' '.join(d['text'] for d in docs)
    m = re.search(r'ranges: (\{[^}]*\})', txt)
    return json.loads(m.group(1))


def run(system, model_spec, fits, schedules, datafiles, init=None, last=10):
    model = core.load_model(model_spec)
    eps = core.load_episodes(datafiles, model=model)
    names = eps[0]['names']
    bounds = eps[0]['bounds']
    sig = core.score_sigma(eps)
    rng = ranges_for(system)
    ini = init or {k: (v[0] + v[1]) / 2 for k, v in rng.items()}
    keys = [f.split('/')[-1].replace('.json', '') for f in fits]
    print(f'== {system}  obs={names}  sigma(0.1std)=', [round(float(s), 4) for s in sig])
    for sname, segs in schedules.items():
        acts, ends = [], []
        for sg in segs:
            acts += [sg['action']] * sg['steps']
            ends.append((len(acts), sg.get('label', '')))
        u = [model.normalize(a, bounds) for a in acts]
        preds = {f: core.rollout(model, load_params(f), {'u': u, 'initial': ini, 'names': names}) for f in fits}
        print(f'-- {sname} ({len(acts)} steps)')
        start = 0
        for end, lab in ends:
            row = [preds[f][max(start, end - last):end].mean(0) for f in fits]
            dis = 0.0
            if len(fits) > 1:
                dis = np.mean([np.mean(np.abs(preds[fits[i]][start:end] - preds[fits[j]][start:end]) / sig)
                               for i in range(len(fits)) for j in range(i + 1, len(fits))])
            print(f'  [{start:4d}-{end - 1:4d}] {lab:30s} dis={dis:5.2f}s | ' +
                  ' | '.join(k + ':' + ','.join(f'{v:.3g}' for v in r) for k, r in zip(keys, row)))
            start = end
```

### Per-system screening drivers

Each file starts with `import sys; sys.path.insert(0, '<dir of screen.py>'); from screen import run`.

```python
# scr_social.py
def A(s,i,b): return {'seeding':s,'incentive':i,'bridge_outreach':b}
R=A(0,0,0); P8=A(7.2,1.6,0.48)
sch={
 'SC-1 pulse0.8/long-rec/spacing':[dict(steps=120,action=P8,label='pulse u0.8 from reset'),dict(steps=50,action=R,label='rec: crash'),
   dict(steps=100,action=R,label='rec +150'),dict(steps=150,action=R,label='rec +300'),dict(steps=60,action=P8,label='pulse 2 (after long gap)'),
   dict(steps=20,action=R,label='short gap'),dict(steps=60,action=P8,label='pulse 3 (after 20 gap)'),dict(steps=40,action=R,label='rec')],
 'SC-2 ladder':[dict(steps=90,action=A(4.5,0,0),label='seeding 4.5'),dict(steps=70,action=A(4.5,2,0),label='+incentive 2 (bridge0)'),
   dict(steps=50,action=A(4.5,1,0),label='incentive 1 (partial drop)'),dict(steps=50,action=A(4.5,0,0),label='incentive 0'),dict(steps=70,action=R,label='seeding 0')],
 'long recovery 1500 from reset':[dict(steps=1500,action=R,label='rec')],
 'pulse u1 1500':[dict(steps=1500,action=A(9,2,0.6),label='pulse')],
 'incentive 1 hold 1000':[dict(steps=1000,action=A(0,1,0),label='inc 1')],
 'seeding 4.5 1000':[dict(steps=1000,action=A(4.5,0,0),label='seed 4.5')]}
b='fits/social_contagion/v1/'
run('social_contagion','greybox/social_contagion_model.py',[b+'m12_all.json',b+'m23_all.json',b+'m2_all.json'],sch,
    ['data/social_contagion/R1.json','data/social_contagion/R2.json','data/social_contagion/R3.json'])

# scr_epi.py
def A(c,m,v): return {'school_closure':c,'mask_mandate':m,'vaccination_rate':v}
R=A(0,0,0); P85=A(0.85,0.85,0.00255)
sch={
 'EP-1 all 0.85 from reset 300, rec 150':[dict(steps=40,action=P85,label='all .85: first wave'),dict(steps=60,action=P85,label='t40-99'),
   dict(steps=100,action=P85,label='t100-199'),dict(steps=100,action=P85,label='t200-299'),dict(steps=40,action=R,label='release'),dict(steps=110,action=R,label='rec +150')],
 'EP-2 vacc from reset 250, off 150':[dict(steps=40,action=A(0,0,0.003),label='vacc: first wave'),dict(steps=110,action=A(0,0,0.003),label='t40-149'),
   dict(steps=100,action=A(0,0,0.003),label='t150-249'),dict(steps=30,action=R,label='off +30'),dict(steps=120,action=R,label='off +150')],
 'EP-3 mask .7 from reset 250':[dict(steps=40,action=A(0,0.7,0),label='first wave'),dict(steps=110,action=A(0,0.7,0),label='t40-149'),dict(steps=100,action=A(0,0.7,0),label='t150-249')],
 'EP-3b closure 1 from reset 250':[dict(steps=40,action=A(1,0,0),label='first wave'),dict(steps=110,action=A(1,0,0),label='t40-149'),dict(steps=100,action=A(1,0,0),label='t150-249')],
 'long rec 3000':[dict(steps=600,action=R,label='rec to 600'),dict(steps=2400,action=R,label='rec to 3000')]}
b='fits/epidemic/v2/'
run('epidemic','greybox/epidemic_model.py',[b+'m13_all.json',b+'m12_all.json',b+'base_all.json',b+'m23_all.json'],sch,['data/epidemic/R1.json','data/epidemic/R2.json'])

# scr_wl.py
def A(h,p,c): return {'hunting_quota':h,'habitat_protection':p,'corridor_access':c}
R=A(0,1,0)
sch={
 'WL-1 spacing':[dict(steps=80,action=A(5.95,0.235,0.85),label='joint .85 from reset'),dict(steps=30,action=R,label='release +30'),
   dict(steps=90,action=R,label='release +120'),dict(steps=60,action=A(7,0.1,1),label='joint 1.0'),dict(steps=30,action=R,label='short gap 30'),
   dict(steps=60,action=A(4.9,0.37,0.7),label='joint .7'),dict(steps=30,action=R,label='release +30'),dict(steps=120,action=R,label='release +150')],
 'WL-2 ladder':[dict(steps=80,action=A(5,1,0),label='hunt 5'),dict(steps=60,action=A(5,0.37,0),label='hunt5+hab.37'),
   dict(steps=60,action=A(0,0.37,0),label='hab .37'),dict(steps=60,action=A(0,0.37,0.7),label='hab.37+corr.7'),
   dict(steps=60,action=A(0,1,0.7),label='corr .7'),dict(steps=30,action=R,label='rec')],
 'holds 2000':[dict(steps=2000,action=R,label='rec')],
 'joint1 2000':[dict(steps=2000,action=A(7,0.1,1),label='joint 1')],
 'joint.7 2000':[dict(steps=2000,action=A(4.9,0.37,0.7),label='joint .7')]}
b='fits/wildlife/v1/'
run('wildlife','greybox/wildlife_model.py',[b+'AB_all3.json',b+'AC_all.json',b+'BC_all2.json',b+'base_all.json'],sch,['data/wildlife/R1.json','data/wildlife/R2c.json'])

# scr_pg.py
def A(p,r,c,i): return {'price_signal':p,'reserve_dispatch':r,'charging_allowance':c,'interconnector':i}
R=A(1.5,0,1,1)
sch={
 'PG-1 price ladder + reserve ladder':[dict(steps=80,action=A(2.0,0,1,1),label='price 2.0 (from reset)'),dict(steps=70,action=A(0.45,0,1,1),label='price 0.45'),
   dict(steps=70,action=A(1.5,0,1,1),label='price 1.5'),dict(steps=35,action=A(1.5,40,1,1),label='reserve 40'),dict(steps=35,action=A(1.5,80,1,1),label='reserve 80'),
   dict(steps=35,action=A(1.5,120,1,1),label='reserve 120'),dict(steps=35,action=A(1.5,80,1,0.5),label='reserve 80 + ic .5'),
   dict(steps=35,action=A(1.5,0,1,0.5),label='ic .5'),dict(steps=35,action=R,label='rec')],
 'PG-2 joint spacing':[dict(steps=100,action=A(0.45,105,0.3,0.44),label='joint .7 from reset'),dict(steps=60,action=R,label='rec 60'),
   dict(steps=60,action=A(0,150,0,0.2),label='joint 1'),dict(steps=30,action=R,label='rec 30'),
   dict(steps=100,action=A(0.225,127.5,0.15,0.32),label='joint .85'),dict(steps=50,action=R,label='rec')],
 'reserve 150 ch0 2000':[dict(steps=2000,action=A(1.5,150,0,1),label='r150 c0')],
 'price 0 2000':[dict(steps=2000,action=A(0,0,1,1),label='p0')]}
b='fits/power_grid/v1/'
run('power_grid','greybox/power_grid_model.py',[b+'m13_all.json',b+'m1_all.json',b+'m12_all.json',b+'m23_all.json'],sch,['data/power_grid/R1.json','data/power_grid/R2c.json'])

# scr_hq.py
def A(s,e,d,u,o,f): return {'staffing':s,'elective_scheduling':e,'diagnostic_allocation':d,'urgent_priority':u,'overtime':o,'followup_capacity':f}
R=A(20,0,0.4,0.6,0,1); P7=A(9.5,14,0.645,0.88,0.7,0.3); P1=A(5,20,0.75,1,1,0)
sch={
 'HQ-1 elective/staffing ladder':[dict(steps=60,action=A(20,5,0.4,0.6,0,1),label='elective 5 from reset'),dict(steps=60,action=A(20,10,0.4,0.6,0,1),label='elective 10'),
   dict(steps=60,action=A(15,10,0.4,0.6,0,1),label='staff 15 + el 10'),dict(steps=60,action=A(15,0,0.4,0.6,0,1),label='staff 15 alone'),dict(steps=60,action=R,label='rec')],
 'HQ-2 joint spacing':[dict(steps=100,action=P7,label='joint .7 from reset'),dict(steps=60,action=R,label='rec 60'),dict(steps=60,action=P1,label='joint 1'),
   dict(steps=90,action=R,label='rec +90'),dict(steps=90,action=R,label='rec +180')],
 'elective 20 hold 1500 then rec 1500':[dict(steps=1500,action=A(20,20,0.4,0.6,0,1),label='E hold'),dict(steps=1500,action=R,label='rec after')],
 'staff 12 hold 2000':[dict(steps=2000,action=A(12,0,0.4,0.6,0,1),label='staff 12')]}
run('hospital_queue','greybox/hospital_queue_model.py',['fits/hospital_queue/final_m12.json','fits/hospital_queue/v5_base_all.json'],sch,['data/hospital_queue/R1.json','data/hospital_queue/R2c.json'])

# scr_mk.py
def A(r,t): return {'interest_rate':r,'transaction_tax':t}
R=A(0,0)
sch={
 'MK-1 joint spacing':[dict(steps=150,action=A(0.1,0.05),label='joint 1 from reset'),dict(steps=150,action=R,label='rec 150'),
   dict(steps=125,action=A(0.07,0.035),label='joint .7'),dict(steps=50,action=R,label='short gap 50'),dict(steps=125,action=A(0.1,0.05),label='joint 1 again')],
 'MK-2 order/mid':[dict(steps=125,action=A(0.05,0),label='rate .05'),dict(steps=125,action=A(0.05,0.05),label='+tax .05'),
   dict(steps=125,action=A(0,0.05),label='tax only'),dict(steps=125,action=A(0,0.025),label='tax .025'),dict(steps=100,action=R,label='rec')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')],
 'joint 3000':[dict(steps=3000,action=A(0.1,0.05),label='joint')]}
b='fits/market/'
run('market','greybox/market_model.py',[b+'m12_withdraw_train600.json',b+'m13_withdraw_train600.json',b+'m23_withdraw_train600.json'],sch,['data/market/A.json'])

# scr_rs.py (NOT YET RUN; reservoir)
def A(r,i,d,a): return {'release_rate':r,'irrigation_allocation':i,'withdrawal_depth':d,'aeration':a}
R=A(2,0,0,1)
sch={
 'RS-1 pulse .7 250 + rec 200':[dict(steps=100,action=A(9,5.6,0.7,0.3),label='pulse .7 t0-99'),dict(steps=150,action=A(9,5.6,0.7,0.3),label='pulse .7 t100-249'),
   dict(steps=50,action=R,label='rec +50'),dict(steps=150,action=R,label='rec +200')],
 'RS-2 release 10.5 & aeration ladder':[dict(steps=150,action=A(10.5,0,0,1),label='release 10.5'),dict(steps=80,action=A(2,0,0,0.3),label='aer .3'),
   dict(steps=80,action=A(2,0,0.5,0.15),label='aer .15 depth .5'),dict(steps=80,action=A(2,0,0.5,0),label='aer 0 depth .5'),dict(steps=60,action=R,label='rec')],
 'rec 3000':[dict(steps=3000,action=R,label='rec')]}
run('reservoir','greybox/reservoir_model.py',['fits/reservoir/v1/m13_all.json','fits/reservoir/v1/m12_all.json'],sch,['data/reservoir/R1.json','data/reservoir/R2.json','data/reservoir/R3.json'])
```

### insample.py (the public vs in-sample table in 4.1)

```python
import json, importlib.util, sys, numpy as np
runs = {'epidemic':['R1','R2'],'wildlife':['R1','R2c'],'ad_auction':['R1','R2c'],'social_contagion':['R1','R2','R3'],
 'power_grid':['R1','R2c'],'reservoir':['R1','R2','R3'],'traffic':['R1','R2','R3'],'supply_chain':['R1','R2','R3'],
 'hospital_queue':['R1','R2c'],'market':['A']}
for s, rl in runs.items():
    spec = importlib.util.spec_from_file_location(f'pred_{s}', f'models/{s}/predict.py')
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
    ctx = json.load(open(f'docs/{s}.json'))['brief']
    eps=[]
    for r in rl:
        for run in json.load(open(f'data/{s}/{r}.json'))['runs']:
            eps.append((run['initial'], run['actions'], run['observations']))
    names=list(eps[0][0].keys())
    allobs=np.concatenate([np.array([[o[n] for n in names] for o in ob])[20:] for _,_,ob in eps])
    sig=0.1*allobs.std(0); tot=[]
    for ini,act,ob in eps:
        pred=np.array([[p[n] for n in names] for p in mod.predict(ini,act,ctx)])
        o=np.array([[x[n] for n in names] for x in ob])
        tot.append((1/(1+np.abs(pred-o)/sig)).mean(0))
    m=np.mean(tot,0); print(s, round(m.mean(),3), dict(zip(names, np.round(m,2))))
```

## 8. Local memory files (they don't sync to the cloud; recreate them there if useful)

- **explain-before-spending-steps** (feedback):
  - In interactive sessions, explain the logic of any paid run in detail and get an explicit yes first: what it is, why this design, what each outcome means, and the exact cost.
  - The overnight framework was pre-authorized within its caps; that authorization is now used up.
  - The user checks progress on the public leaderboard, which is effectively the held-out test.
  - Steps can't be recovered.
- **market-plan-location** (project):
  - `plans/market-plan.md` is the pilot template: gray-box pipeline, relaxation and M-modules, pair fits, parametric bootstrap (the user likes it), and a staged budget with public checkpoints.
- **overnight-run-outcome** (project):
  - The 2026-09-27 overnight run finished all 9 systems.
  - `plans/overnight-report.md` is the handoff, and `submission-overnight-all.zip` was uploaded.
  - Each system has its own 2,000-step budget.
  - Subagents hit API usage limits 3 times, so snapshot-commit often and relaunch agents as resumes.
  - Now superseded by the per-system public scores in section 3.

## 9. Local-only items (irrelevant to the cloud)

`/doctor` this session changed two things:

- added `C:\Users\Belia\.local\bin` to the Windows user PATH;
- set `permissions.defaultMode = "auto"` in `~/.claude/settings.json`.

The CLAUDE.md trim was declined.
