# Social contagion plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 (overnight job, `plans/overnight-framework.md`). CAP = 1,000 steps
(Run 1 ≤ 550, Run 2 ≤ 400, reserve ≥ 50). Budget at start: 2,000 remaining (free read). A previous attempt was cut
off before spending anything (no plan or data existed).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Observe adopter totals in two communities. Seeding funds outreach, incentive changes the offer,
and bridge outreach allocates effort between local recruitment and introductions across communities.
Relationship-led, incentive-led and deliberative audiences mix differently. Interested people must complete
onboarding through a workforce also needed by existing members; promises accompany waiting cohorts. Disappointed
former members need time before reconsidering. Credibility, incentive expectations and cross-community relationships
can retain history. Compare local versus bridge campaigns, incentive before versus after recruitment, and recovery
with new outreach stopped. Initial members have a fixed disclosed-style community mix and no paid promises; other
queues begin empty."

**Observables** (docs initial-reading ranges):

| Observable | Initial range | Notes |
|---|---|---|
| adopters_a | 30 – 70 | member total, community A (stock; changes by joins − departures) |
| adopters_b | 20 – 55 | member total, community B |

Both are stocks (counts), so they integrate flows: expect ramps (not steps) after a control switch, and the level
reached depends on the hold length. "Settled" for a stock means the net flow has reached 0 (joins = departures).

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u | Range of u | Notes |
|---|---|---:|---:|---|---|---|
| seeding | [0, 10] | 0 | 9 | s/9 | [0, 1.11] | outreach funding; probably the main driver of new interest |
| incentive | [0, 2] | 0 | 2 | i/2 | [0, 1] | the offer; drives incentive-led audience; creates paid promises |
| bridge_outreach | [0, 1] | 0 | 0.6 | b/0.6 | [0, 1.67] | **fraction** of outreach effort sent across communities; pulse 0.6 is not the upper bound, so 0.6–1.0 is the untested side. As an allocation of seeding effort it may do nothing when seeding = 0 |

All recovery values are at the lower bound (0). Recovery = everything off: no outreach, no offer.

**Population / structure facts from the brief (base model, not mechanisms):**
- Two communities A and B, each with three audience types: relationship-led (respond to contacts with members:
  social contagion ∝ adopters, and to bridge introductions), incentive-led (respond to the incentive), deliberative
  (slow, respond to accumulated exposure). "mix differently" → the type shares differ between A and B.
- Initial members have "a fixed disclosed-style community mix" → the initial adopters are split into types by a
  fixed rule (deterministic given the reading).
- **Delay / commitment phrases → pipeline stages:**
  - "Interested people must complete onboarding through a workforce also needed by existing members" →
    interested queue → onboarding (capacity-limited) → member. Capacity available for onboarding = workforce −
    service load ∝ members. So adoption **saturates**, and a large member base slows its own onboarding.
    Expect a lag between a seeding switch and the adopter ramp, and continued joins after seeding stops (queue
    drains).
  - "promises accompany waiting cohorts" → each waiting cohort carries the incentive promised when it became
    interested. Changing the incentive does not change promises already made (commitment delay). Initial state:
    "no paid promises".
  - "Disappointed former members need time before reconsidering" → departures go to a disappointed pool that returns
    to the susceptible pool after a delay (not immediately re-recruitable).
  - "other queues begin empty" → interested/onboarding/disappointed queues are empty at reset → a **reset transient**
    in the joins (nothing in the pipeline at first).
- **Time since reset:** no seasonality phrase. Only the reset transient.

**Organizer-suggested comparisons (P9), quoted:**
- P9a "Compare local versus bridge campaigns" → same seeding with bridge 0 vs bridge 0.6 (or 1.0); compare A and B.
- P9b "incentive before versus after recruitment" → incentive then seeding vs seeding then incentive (an order swap,
  P6).
- P9c "recovery with new outreach stopped" → after a campaign, seeding 0 (and bridge 0), incentive kept vs dropped;
  watch whether adopters keep growing (contagion/queue), hold, or decline (churn).

## 2. The three mechanisms (§3.2)

Quoted: "**Credibility, incentive expectations and cross-community relationships can retain history.**"
Confidence high that these are the three candidates (exactly two active).

- **M1 credibility**
- **M2 incentive expectations**
- **M3 cross-community relationships**

## 3. Theses (§3.3)

### M1 credibility

| Field | Content |
|---|---|
| Quote | "Credibility … can retain history"; "promises accompany waiting cohorts" |
| Hidden state | C: organisational credibility (trust), baseline 1 |
| **Driver** | broken / delayed promises: waiting-cohort size or waiting time (onboarding backlog, i.e. outreach that outruns the workforce); possibly churn (disappointed departures) |
| **What it changes** | conversion of outreach into interest (response **size** to seeding, both communities), and possibly churn |
| Timescales | builds (loss) over 20–50 ticks of overload; recovers over 50–200 ticks |
| P1 seeding on (hold) | present: adoption rate rises, then **slows** below what the capacity limit alone gives once a backlog forms; absent: rate set by capacity only |
| P1 seeding off | present: continued slow decline/weak growth afterwards; the next campaign is weaker. Absent: queue drains, then flat |
| P1 incentive | little direct effect (unless an unpaid promise hurts credibility) |
| P1 bridge | none specific |
| P5 two seeding pulses, short vs long gap | **2nd pulse weaker after a short gap** (credibility still low) |
| P6 incentive before/after recruitment | little |
| P7 long hold | slow decline of the join rate under sustained heavy seeding |

### M2 incentive expectations

| Field | Content |
|---|---|
| Quote | "incentive expectations … can retain history"; "Initial members … no paid promises" |
| Hidden state | E: expected incentive (a fading average of the incentive offered/paid) |
| **Driver** | the incentive level (control) |
| **What it changes** | attraction ∝ incentive **relative to E** (a raised offer attracts, then adapts); members/waiting cohorts whose expectation exceeds the current offer are disappointed → **churn** when the incentive is cut |
| Timescales | E adapts over 20–100 ticks |
| P1 incentive on | present: join burst that **fades** during the hold (adaptation); absent: sustained higher join rate |
| P1 incentive off | present: **churn**: adopters fall below the pre-incentive trajectory (asymmetric vs on); absent: join rate drops back, no losses |
| P1 seeding | none (at incentive 0 E stays 0) |
| P5 two incentive pulses | 2nd pulse weaker after a short gap (E still high) |
| P6 incentive before vs after recruitment (P9b) | present: incentive **after** recruitment (for existing members) vs **before** (recruits join expecting it): different churn when it ends; absent: order-independent up to linear dynamics |
| P7 long hold at incentive | slow fade of the incentive effect |

### M3 cross-community relationships

| Field | Content |
|---|---|
| Quote | "cross-community relationships can retain history"; "bridge outreach allocates effort between local recruitment and introductions across communities" |
| Hidden state | R: stock of cross-community ties |
| **Driver** | bridge introductions (seeding × bridge_outreach), possibly adopters in both communities |
| **What it changes** | cross-community contagion: B's recruitment driven by A's members (and vice versa) — coupling strength between A and B |
| Timescales | builds over 20–50 ticks of bridge work; fades over 100+ ticks |
| P1 seeding (bridge 0) | none: local campaigns stay local; B responds only via its own local share |
| P1 bridge (seeding > 0) | present: B (the smaller community) gains; after bridge stops, B **keeps growing** (ties persist); absent: B's extra growth stops when bridge stops |
| P9a local vs bridge | present: effect of bridge **outlasts** the campaign; absent: only a reallocation during the campaign |
| P5 | a 2nd bridge campaign after a short gap is stronger (ties remain) |
| P7 | slow drift of the A/B coupling |

## 4. Separation table (§3.4)

| Probe | M1 credibility | M2 incentive expectations | M3 cross-community ties |
|---|---|---|---|
| P1 seeding 9 on, hold | join rate slows under backlog | nothing | nothing (bridge 0) |
| P1 seeding off | weak afterwards; next campaign weaker | nothing | nothing |
| P1 incentive on/off | small | **burst that fades; churn after off** | nothing |
| P1 bridge (with seeding) on/off | small | nothing | **B keeps benefiting after bridge off** |
| P5 seeding pulses short vs long gap | **2nd weaker (short gap)** | nothing | nothing |
| P6/P9b incentive before vs after recruitment | small | **order effect in churn** | nothing |
| P9a local vs bridge | nothing specific | nothing | **bridge effect persists** |
| P9c recovery with outreach stopped | continued weak joins/decline if credibility low | churn if incentive dropped too | B still gains from ties |
| P7 long hold (all controls) | slow decline of join rate | slow fade of incentive effect | slow A/B coupling drift |

Pairs:
- **M1 vs M2:** P5 seeding gap test at incentive 0 (M1 effect, M2 nothing) vs P1 incentive off (M2 churn, M1 none).
- **M1 vs M3:** P1 bridge on/off with seeding (M3 persistence in B) vs P5 seeding gap test with bridge 0 (M1 only).
- **M2 vs M3:** incentive on/off (M2) vs bridge on/off (M3): different controls, one predicts an effect where the
  other predicts nothing.

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 (start) | — | — | 0 | 2,000 |
| 2026-09-27 01:37 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 2026-09-27 01:37 | R1 | 40–59 (P0 recovery, ext) | 20 | 1940 |
| 2026-09-27 01:37 | R1 | 60–79 (P0 recovery, ext) | 20 | 1920 |
| 2026-09-27 01:37 | R1 | 80–99 (P0 recovery, ext; stopped at 100: steady organic growth, not settling) | 20 | 1900 |
| 2026-09-27 01:38 | R1 | 100–139 (P1 seeding 9 on) | 40 | 1860 |
| 2026-09-27 01:38 | R1 | 140–164 (P1 seeding on, ext) | 25 | 1835 |
| 2026-09-27 01:38 | R1 | 165–189 (P1 seeding on, ext) | 25 | 1810 |
| 2026-09-27 01:38 | R1 | 190–229 (P1 seeding off = recovery; P9c local) | 40 | 1770 |
| 2026-09-27 01:38 | R1 | 230–254 (seeding off, ext) | 25 | 1745 |
| 2026-09-27 01:38 | R1 | 255–279 (seeding off, ext) | 25 | 1720 |
| 2026-09-27 01:39 | R1 | 280–329 (P1 incentive 2 on) | 50 | 1670 |
| 2026-09-27 01:39 | R1 | 330–354 (incentive on, ext) | 25 | 1645 |
| 2026-09-27 01:39 | R1 | 355–404 (P1 incentive off = recovery) | 50 | 1595 |
| 2026-09-27 01:39 | R1 | 405–434 (P1 bridge 0.6 alone, seeding 0) | 30 | 1565 |
| 2026-09-27 01:39 | R1 | 435–474 (seeding 9 + bridge 0.6: bridge campaign, P9a half) | 40 | 1525 |
| 2026-09-27 01:40 | R1 | 475–519 (recovery after bridge campaign; P9c bridge) | 45 | 1480 |
| 2026-09-27 01:40 | R1 | 520–549 (recovery, ext). **R1 complete: 550 steps** | 30 | 1450 |

Spend summary so far: R1 = 550 steps (cap 550). Budget remaining 1,450.

## 6. Run 1 observations (`data/social_contagion/R1.json`, 550 ticks, initial reading A 61.5 / B 38.6)

Schedule: recovery 0–99 | seeding 9 100–189 | recovery 190–279 | incentive 2 280–354 | recovery 355–404 |
bridge 0.6 alone 405–434 | seeding 9 + bridge 0.6 435–474 | recovery 475–549. Plot `data/social_contagion/R1_r0_battery.png`,
battery `R1_battery.json`.

| Setting (ticks) | A mean | B mean | A slope/tick | B slope/tick |
|---|---:|---:|---:|---:|
| reset trough (≈16–17) | 46.3 | 29.1 | — | — |
| recovery, end of P0 (90–99) | 63.0 | 47.9 | +0.23 | +0.22 |
| seeding 9, end (180–189) | 230.5 | 119.6 | −0.06 (settled) | +0.22 |
| recovery after local campaign (270–279) | 131.0 | 91.7 | −0.47 | −0.21 |
| incentive 2 (345–354) | 131.5 | 107.1 | +0.05 | +0.17 |
| recovery after incentive (395–404) | 44.5 | 30.8 | −0.09 (settled) | +0.03 |
| bridge 0.6 alone (425–434) | 47.2 | 35.6 | +0.20 | +0.23 |
| seeding 9 + bridge 0.6, end (465–474) | 118.2 | 68.2 | +1.75 | +1.27 |
| recovery after bridge campaign (490–499) | 140.9 | 97.3 | −0.13 | **+1.09** |
| recovery, end (540–549) | 132.4 | 116.8 | −0.32 | −0.16 |

- **Reset transient:** both communities fall ~25% in ~16 ticks (A 61.5 → 46.3, B 38.6 → 29.1; initial rate
  ≈ −2.8%/tick), then grow organically at ≈ +0.2/tick in both (no outreach, no offer) for the rest of P0 (not settled
  at 100). Suggests a fixed share (~25%) of the initial members leaves at once (incentive-led members with "no paid
  promises", or members with an initial expectation), and word of mouth / reconsideration drives slow growth.
- **Local campaign (seeding 9, bridge 0):** 5–7 tick dead time (onboarding pipeline), A rises up to +6/tick and
  saturates at 230 after ~70 ticks (settled); B rises up to +1.9/tick (local seeding also reaches B, ~⅓ as strongly)
  and is still rising at the end (+0.2/tick). Saturation in A: pool depletion and/or churn balance.
- **Stopping the local campaign (P9c local):** ~6 ticks of plateau (queue drain), then A declines at ≈ 2%/tick of
  the excess, slowing (k_lin ≈ 0.02; 230 → 131 in 90 ticks, not settled). B follows (121 → 92). **No sustained
  growth after local outreach stops.**
- **Incentive 2 (seeding 0):** A's decline stops at once (from −0.6 to +0.05/tick) — the incentive **retains**
  members; B grows +0.3 → +0.15/tick (incentive-led audience larger in B). No fading of the effect within 75 ticks.
- **Incentive off:** an immediate (0-tick delay) **crash in both**: A 131 → 44, B 108 → 31 at ≈ 5%/tick of the level
  in both (k ≈ 0.1), settled in ~40 ticks at the reset-trough level (44 / 31). On/off strongly asymmetric
  (k_on/k_off 0.16–0.18): the offer gave +3 / +16, its removal took −87 / −77. **Removing the incentive causes a
  disappointment departure of far more members than the incentive attracted** — M2 signature (expectations), or a
  base "paid promise" structure where incentive-led members leave when payment stops.
- **Bridge 0.6 alone (seeding 0):** growth +0.2/tick in both, the same as organic growth at P0 → bridge without
  seeding does nothing measurable (it allocates outreach effort, and there is none).
- **Bridge campaign (seeding 9, bridge 0.6) vs local campaign:** A rises at most +2.9/tick (local: 6.0 — ≈ half,
  consistent with 40% of effort moved away from local plus the post-crash history); B at most +1.3/tick (local 1.9).
  During the campaign bridge did **not** raise B's rate.
- **Stopping the bridge campaign (P9c bridge):** A keeps rising for ~15 ticks (+15, pipeline drain) then is flat
  and slowly declining (140 → 131 over 60 ticks, much slower than after the local campaign). **B keeps growing
  strongly for ~45 ticks after the campaign stopped (75 → 116, +1.1/tick, near-linear, then stops abruptly at
  ~118 and starts to decline).** After the local campaign B rose only ~1 before falling. Candidates: M3 persistent
  cross-community ties (A members keep recruiting in B), or a B onboarding backlog (bridge introductions queued
  in B faster than B's workforce onboards them; the near-linear rise that stops abruptly looks like a queue draining
  at capacity).
- **Noise:** proportional, 0.25% of level (σ ≈ 0.24 A, 0.17 B over the run) → log units.
- Couplings: A and B levels correlate 0.91 with B lagging A by 6 ticks; ΔA and ΔB correlate 0.85 at lag 0 (the
  incentive crash dominates).

## 7. Behaviour catalogue v1 (after Run 1)

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 | Reset: −25% in both communities within 16 ticks, then slow organic growth | R1 0–100 | fixed initial mix with a share of members that leaves (incentive-led, no promises) or an initial expectation (M2 with E0 > 0); WOM growth | open |
| B2 | Organic growth at recovery ≈ +0.2/tick in both, near-linear, > 100 ticks | R1 20–100, 405–435 | word of mouth (∝ members) and/or reconsideration of the disappointed pool | open |
| B3 | Seeding: 5–7 tick dead time, A +6/tick, saturates at 230; B +1.9/tick, slower | R1 100–190 | onboarding pipeline (queue + workforce capacity); pool depletion; B gets a smaller share of local outreach | open |
| B4 | After seeding stops: short plateau, then slow decline (k ≈ 0.02), no settling in 90 ticks | R1 190–280 | churn of members above the organic equilibrium; queue drain first | open |
| B5 | Incentive retains: stops A's decline at once, raises B | R1 280–355 | incentive lowers churn (all members) and recruits incentive-led people (more in B) | open |
| B6 | **Incentive off: immediate crash to the reset-trough level, ≈ 5%/tick in both, far larger than the on-effect** | R1 355–405 | M2 disappointment (expectation > offer); or base: incentive-led members leave when payments stop | open — key M2 evidence |
| B7 | Bridge without seeding: no effect | R1 405–435 | bridge is an allocation of seeding effort | modeled as allocation (base) |
| B8 | Bridge campaign: A rises half as fast as local, B not faster | R1 435–475 | 40% of effort moved from local to introductions; history (post-crash disappointed pool) | open |
| B9 | **After the bridge campaign B keeps growing +1.1/tick for 45 ticks, then stops abruptly; A flat and declines slowly** | R1 475–550 | M3 persistent cross-community ties; or a B onboarding backlog from introductions (queue drain at capacity) | open — key M3 evidence |
| B10 | Noise proportional 0.25% | battery | measurement noise | log units |

Separating evidence still needed (for Run 2): M1 has no signature yet (needs a P5 seeding gap test at incentive 0);
M2 vs base promises (needs the incentive-off step vs ramp, and short vs long incentive holds); M3 vs B backlog
(needs a second bridge campaign, a longer post-bridge observation and a local-vs-bridge comparison from the same
state).

## 8. Model module and Run-1 pair fits

Module: `toronto26-participant-kit/greybox/social_contagion_model.py` (v0, ~17 ms per 550-tick rollout; log units,
residual σ 0.01). Base structure from the brief + catalogue: per community (A, B) two audience types
(r = relationship/deliberative, i = incentive-led) with potential pools N_c·(1−φ_c | φ_c); interest from word of
mouth (β_c M_c/N_c), local outreach (σ_c × seeding(1−b), through 2 lag stages = dead time B3), bridge introductions
(τ_c × seeding·b × M_other/N_other) and, for type i, the incentive (ι ui); an onboarding queue with a capacity
κ_c/(1 + ω M_c/100) (workforce shared with members) and abandonment; churn d_k·exp(−γ ui) (incentive retains, B5)
into a disappointed pool that reconsiders at ρ. Reset: a fixed share ψ_c of the reading is type i (B1), queues empty.
Mechanism modules written from the theses before fitting:
- m1 credibility: fading memory of the waiting time (queue / capacity) lowers all interest by exp(−g1 Cm).
- m2 incentive expectations: E ← E + a2(ui − E), E(0) = e0; extra churn g2·max(E − ui, 0) for all members.
- m3 cross-community ties: R ← R + a3u·(seeding·b)(1 − R) − a3d R; extra cross-community interest g3 R M_o/N_o.

Plotting: `fits/social_contagion/plotfit.py` (run with `PYTHONPATH=.` from the kit).

Fits on R1 (all 550 ticks, log units, σ 0.01, soft_l1; pairs init from `init_r1.json` = base params with pinned
values moved into the interior and module params at SPEC defaults (nonzero gains); 1 restart, max_nfev 400 —
quick fits for probe ranking only):

| Fit | Cost | Train score (σ = 0.1 std) | Module params | Notes |
|---|---:|---:|---|---|
| base (`base_r1`) | 6,884 | 0.633 | — | 2 restarts; restart 0 stopped at nfev 97. Pinned: qa → 1, psiB → 1, om → 0, gret → 0, iota ≈ 10 (large). Misses B9 (B's continued growth after the bridge campaign) and the incentive-on transient |
| m1+m2 (`m12_r1`) | 3,477 | 0.718 | a1 0.019, g1 1.18; a2 0.06, g2 0.033, **e0 → 1 (pinned)** | iota 162 (pinned large), qa → 1, psiA → 0 |
| m1+m3 (`m13_r1`) | 3,938 | 0.693 | a1 0.04, **g1 → 21**; a3u 0.0016, a3d → 0, **g3 → 10 (cap)** | iota → 5e21 (runaway), stopped at nfev 168 |
| **m2+m3** (`m23_r1`) | **1,648** | **0.796** | a2 0.043, g2 0.078, e0 0.13; a3u 0.0003, a3d 0.0012, **g3 → 10 (cap)** | iota → 0, dr 0.066, psiB → 1 |

Plot `fits/social_contagion/pairs_r1.png` (base + three pairs). Readings:
- m2+m3 fits R1 best by a wide margin: m2 (disappointment when the offer falls below the expectation) explains the
  incentive-off crash (B6) and, with e0 0.13, part of the reset drop (B1); m3 explains B's continued growth after the
  bridge campaign (B9). m3's rates are very slow and g3 is at its cap: R acts as a near-permanent accumulator of bridge
  work — standing in for structure (possibly a B onboarding backlog), not yet evidence.
- The pairs without m2 need a runaway incentive attraction (iota) to fake the incentive-on step; the pairs without m3
  miss B9 (A overshoots, B undershoots after the bridge campaign).
- Pinned parameters everywhere (qa → 1, ψ → 0/1, g3 at cap): the base is not yet right; the modeler must revisit
  the onboarding queue (qa → 1 means the queue is not used) and the initial mix.

## 9. Run 2 design (§4.4)

Candidates simulated through the three R1 pairs after a common 30-tick P0 (`fits/social_contagion/run2_design.py`);
disagreement = mean |Δ| / (0.1 std) over the three pair differences, per 100 steps:

| Candidate | Steps | Pair diff 12-13 / 12-23 / 13-23 (σ) | Score /100 steps |
|---|---:|---|---:|
| I P3 seeding 9 + incentive 2 (60) + rec 40 | 100 | 2.7 / 7.6 / 7.9 | **6.07** |
| G bridge 1.0 campaign (seeding 9) 40 + rec 60 | 100 | 7.1 / 4.7 / 2.3 | 4.70 |
| A2 P7 full pulse (9, 2, 0.6) 150 + rec 60 | 210 | 5.8 / 10.1 / 12.2 | 4.45 |
| A P7 full pulse 200 + rec 60 | 260 | 6.0 / 12.4 / 13.5 | 4.10 |
| B P9b incentive before: inc 40, seed+inc 40, rec 40 | 120 | 2.6 / 5.5 / 5.9 | 3.89 |
| J short incentive 15 + rec 45 | 60 | 1.5 / 2.2 / 2.5 | 3.42 |
| E P2 seeding 4.5 (80) + rec 40 | 120 | 2.6 / 5.9 / 3.4 | 3.33 |
| H local campaign 40 + rec 60 | 100 | 1.3 / 3.6 / 2.9 | 2.58 |
| F M2 incentive 60, ramp down 30, rec 30 | 120 | 1.4 / 3.9 / 3.9 | 2.57 |
| C P9b incentive after: seed 40, inc 40, rec 40 | 120 | 2.5 / 2.7 / 2.6 | 2.15 |
| F2 M2 incentive 60, step down, rec 60 | 120 | 1.5 / 3.3 / 2.9 | 2.15 |
| D P5 seeding 30 / gap 20 / 30 + rec 40 | 120 | 1.3 / 2.7 / 2.2 | 1.73 |
| K P7 recovery 200 | 200 | 0.2 / 1.2 / 1.3 | 0.45 |

The largest total disagreement is the long full-pulse hold (A: 12–13 σ for m23 vs the others) and the joint
seeding + incentive composition (I); per step, I and the bridge-1.0 campaign (G) rank highest.

**Chosen Run 2 (400 steps, fresh reset):**

| Ticks | Segment | Probe / purpose |
|---|---|---|
| 0–24 | recovery 25 | P0 (reset replicate; different initial reading) |
| 25–54 | incentive 2 alone (30) | **P9b "incentive before recruitment"** (R1 280 was incentive *after* the local campaign); M2 expectation builds before recruits arrive |
| 55–254 | full pulse action seeding 9, incentive 2, bridge 0.6 (200) | **P7** long hold (settled level under sustained controls, tip 5), **P3** joint composition (I, A), **all-controls pulse** (tip 4) |
| 255–304 | recovery 50 (all controls released at once) | **all-controls release**, P9c recovery with outreach stopped, M2 crash after a 230-tick expectation |
| 305–344 | seeding 9, bridge 1.0 (40) | **G / M3 probe**: bridge at its upper bound (u = 1.67, other side of the pulse); a second bridge campaign from a post-crash state like R1 435 (P5-style repeat, M1) |
| 345–399 | recovery 55 | M3: does B keep growing after the bridge stops (R1 B9 replicate at a higher bridge share)? |

Not covered (reasons): P2 seeding mid-level (E) and the M2 ramp-vs-step test (F) — no room next to the ≥200 P7
and the all-controls release; P9b "after" half comes from R1 (incentive after the local campaign), not a clean
same-state comparison; P5 seeding gap test (D) ranked low. Candidates for the Phase-C reserve: E (P2) or F (M2 ramp).

## 10. Run 2 spend log (continues §5)

| Local time | Run | Ticks | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 01:50 | R2 | 0–24 (P0 recovery, fresh reset) | 25 | 1425 |
| 2026-09-27 01:50 | R2 | 25–54 (incentive 2 alone: P9b "before") | 30 | 1395 |
| 2026-09-27 01:50 | R2 | 55–104 (full pulse 9/2/0.6, part 1) | 50 | 1345 |
| 2026-09-27 01:50 | R2 | 105–154 (full pulse, part 2) | 50 | 1295 |
| 2026-09-27 01:51 | R2 | 155–204 (full pulse, part 3) | 50 | 1245 |
| 2026-09-27 01:51 | R2 | 205–254 (full pulse, part 4; P7 total 200, settled) | 50 | 1195 |
| 2026-09-27 01:51 | R2 | 255–304 (all-controls release to recovery) | 50 | 1145 |
| 2026-09-27 01:51 | R2 | 305–344 (seeding 9 + bridge 1.0) | 40 | 1105 |
| 2026-09-27 01:51 | R2 | 345–399 (recovery after bridge 1.0). **R2 complete: 400 steps** | 55 | 1050 |

Spend summary: R1 = 550 (cap 550), R2 = 400 (cap 400), total **950**. Budget remaining 1,050; **50 steps of the
1,000 CAP are left as the Phase-C reserve.**

Phase C reserve (modeler, review G4; free budget read before: 1,050 remaining):

| Local time | Run | Ticks | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 02:05 | R3 (fresh reset) | 0–14 P0 recovery, 15–49 seeding 9 / incentive 0 / bridge 0.6 (M1 probe, review §4) | 50 | 1000 |

**Total spent: 1,000 = CAP. No further steps may be spent on social_contagion.**

## 11. Run 2 observations (`data/social_contagion/R2.json`, 400 ticks, initial reading A 48.6 / B 37.8)

Plot + battery: `data/social_contagion/R2_r0_battery.png`, `R2_battery.json`. R1 fits predicting R2:
`fits/social_contagion/pairs_r1_on_R2.png` (scores σ = 0.1 std: base 0.396, m12 0.234, m13 0.248, m23 0.240).

| Segment (ticks) | adopters_a | adopters_b |
|---|---|---|
| P0 (0–24) | 48.6 → 37.4 at tick 15 (×0.77), then +0.1/tick | 37.8 → 28.3 (×0.75), then flat — **same proportional reset drop as R1 (×0.75)** |
| incentive 2 alone (25–54) | +0.55/tick (39 → 55) | +0.5/tick (29.5 → 43.4) — from a low member base the offer recruits in **both** communities (R1, after the campaign: A flat, B +0.3) |
| full pulse 9/2/0.6 (55–254) | dead time 5, max +4.9/tick, **settled 199.2** | dead time 7, max +1.75/tick, 131.4 (drift < 0.02/tick at the end) |
| all-controls release (255–304) | **0-tick-delay crash**, 199 → 43.1 (k ≈ 0.09), floor at ~tick 300 | 131 → 32.8 at tick 287, then **rises again** (+0.27/tick) |
| seeding 9 + bridge 1.0 (305–344) | 43 → 55.5, slow, accelerating (no local effort) | 37 → 53.5 (+0.4 → +0.8/tick) |
| recovery after bridge 1.0 (345–399) | **keeps growing 55.9 → 102.8** (+0.8 → +1.1 → +0.5/tick) | **keeps growing 53.9 → 96.5** (+0.9 → +1.0 → +0.4/tick) |

Separating probes and P9 that ran:
- **All-controls pulse and release (tip 4):** ran. The release after 200 ticks of full pulse crashes both
  communities to the **same floor as R1's incentive-off crash and the reset trough** (A ≈ 43–46, B ≈ 29–33) within
  ~45 ticks. The crash takes **members recruited by seeding too**, not only incentive-led recruits: every R1 fit
  predicted a floor of 100–150. Contrast with R1 190 (seeding off at incentive 0): a slow 2%/tick decline.
  → Members who joined or stayed **while the incentive was on** leave at ≈ 9%/tick when it is cut. Strong evidence
  for M2 (an expectation built by the offer, and disappointment when the offer falls below it), or for a base
  "paid promise" structure that covers everyone recruited under an offer.
- **P7 full pulse (200):** ran; settled levels A 199.2, B 131.4. A under the full pulse (199) is **lower** than under
  seeding alone in R1 (230): bridge 0.6 moves 40% of effort off local recruitment. B (131) is higher than under
  seeding alone (≈ 121, still rising slowly).
- **P3 composition (seeding + incentive + bridge):** covered by the full pulse. The effects are not additive (A is
  lower than under seeding alone despite the incentive).
- **P9b incentive before recruitment:** incentive alone from a low base recruits +0.5/tick in both communities, then
  the full campaign. R1's incentive *after* recruitment (at 131 / 92 after a campaign) only held A and raised B. Both
  ended with the same crash on removal. Not a clean same-state comparison.
- **P9a local vs bridge / M3 probe (bridge 1.0):** ran. Bridge 1.0 (no local effort) grows both communities slowly
  during the campaign, and **both keep growing ~1/tick for 55+ ticks after it stops**, at first faster than during the
  campaign. R1 (bridge 0.6) showed the same in B only. A queue backlog would drain at most at the capacity rate seen
  during the campaign; here growth **accelerates after the stop** and involves both communities → **self-sustaining
  cross-community recruitment through relationships that outlast the campaign (M3)**.
- **P9c recovery with new outreach stopped:** R1 190 (local: slow decline), R1 475 (bridge 0.6: A flat, B +1.1/tick
  for 45 ticks), R2 345 (bridge 1.0: both +1/tick for 55 ticks). With the incentive also stopped (R2 255): crash.
- **P5 / M1:** no clean seeding gap test was run. The R2 bridge campaign after the crash only partly repeats R1's
  post-crash campaign (different bridge share), so M1 (credibility) has **no separating evidence**.
- Not run: P2 (seeding mid-level), the M2 ramp-vs-step incentive removal, the P5 seeding gap test.

## 12. Behaviour catalogue v2 (after Run 2)

B1–B10 from §7 stand. Updates and new behaviours:

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 (upd.) | The reset drop is proportional: ×0.75–0.77 of the reading in both communities and both runs, in ~15 ticks | R1/R2 0–20 | fixed initial mix: ~25% of initial members leave (disappointed expectation e0 > 0, or type i without promises) | open |
| B6 (upd.) | **Removing the incentive crashes both communities to a fixed floor (A 43–46, B 29–33)**, whatever recruited the members (incentive alone in R1, the full campaign in R2), at ≈ 5–9%/tick with a 0-tick delay | R1 355–405, R2 255–305 | M2 disappointment for everyone who experienced the offer; the floor is a core that never expects the offer (≈ the reset trough) | open — key, not captured by any R1 fit |
| B11 | The floor after a crash ≈ the reset trough: the core population is the same after every crash | R1 16, 405; R2 15, 300 | core members (relationship-led initial members) are not subject to disappointment | open |
| B12 | The full pulse settles at A 199 / B 131 (seeding alone: 230 / ≥ 121) | R2 55–254 vs R1 100–190 | the bridge share takes effort from local recruitment in A and adds to B | open: base (allocation) |
| B13 | Incentive alone from a low base: +0.5/tick in both communities | R2 25–55 | the incentive attracts type i in both communities; the response scales with the susceptible pool | open |
| B14 | **After a bridge campaign, growth continues (and accelerates) for 50+ ticks in both communities (bridge 1.0) or in B (bridge 0.6)** | R1 475–550, R2 345–400 | M3 persistent cross-community ties feeding contagion; a queue backlog (weaker: growth is faster after the stop than during) | open — key M3 evidence |
| B15 | During bridge 1.0 (no local effort) both communities grow slowly and accelerate | R2 305–345 | introductions scale with the other community's members (few after the crash) | open: base |
| B16 | After the R2 crash, B turns up by itself (+0.27/tick from tick 287) while A is flat | R2 287–305 | the disappointed pool reconsidering, or ties from the earlier bridge 0.6 (M3) | open |

## 13. Status / hand-off to reviewer

- **Files:** data `toronto26-participant-kit/data/social_contagion/R1.json` (550 ticks) and `R2.json` (400 ticks),
  with battery PNG/JSON next to them. Model `greybox/social_contagion_model.py` (v0). Fits
  `fits/social_contagion/{base,m12,m13,m23}_r1.json` (+ `.log`), `init_r1.json`; plots `base_r1.png`,
  `pairs_r1.png`, `pairs_r1_on_R2.png`; tools `fits/social_contagion/run2_design.py`, `plotfit.py`.
- **Budget:** 950 of the 1,000 CAP spent; remaining budget 1,050; **Phase-C reserve 50 steps.** Suggested use: the
  M2 separating test (incentive on ~20, then a **ramp** down over ~15 instead of a step; M2 predicts a much smaller
  crash) or P2 (seeding 4.5), whichever the reviewer ranks higher. A fresh reset costs its own P0 (~20).
- **Open, in priority order:**
  1. **The crash floor (B6/B11).** No R1 fit predicts that removing the incentive strips every non-core member. The
     base needs a core (never-disappointed) population ≈ the reset trough and a non-core population whose departures
     depend on the offer history (m2: expectation vs the current offer). The v0 base splits members by how they were
     recruited (type i vs r), which is wrong here: members recruited by seeding under incentive 2 left too.
  2. **M3 (B14):** strong evidence that bridge work leaves persistent cross-community recruitment. In the R1 fits m3
     has g3 at its cap and near-zero rates (an accumulator), so the functional form is wrong. The post-bridge growth
     is self-reinforcing (it scales with members of both communities × ties) and lasts 50+ ticks. Consider ties driven
     by introductions (seeding × bridge) that fade slowly and multiply cross-community word of mouth.
  3. **M1 has no separating evidence.** With M2 (B6) and M3 (B14) both strongly indicated, the working hypothesis is
     **m2 + m3**. m1 was never directly tested (no seeding gap test).
  4. Pinned parameters in the R1 fits (qa → 1, ψ at 0/1, runaway iota, g3 at its cap): the queue/onboarding structure
     is not identified. The dead time (5–7 ticks) is carried by the outreach lag stages.
  5. Not measured: seeding mid-level (P2), and a long recovery hold (> 100 ticks). The organic growth at recovery was
     still going at tick 100 (R1), and the post-bridge growth was still going at the end of R2.

## 14. Phase C: R3 analysis (the M1 probe, review §4)

`data/social_contagion/R3.json`: fresh reset (initial reading A 42.8 / B 52.6), P0 recovery for ticks 0–14, then
seeding 9 / incentive 0 / bridge 0.6 for ticks 15–49. It uses the same controls as R1 435–469, but from a pristine state.

| | Start A / B | Gain at +5 | +10 | +20 | +35 |
|---|---|---|---|---|---|
| R1 435 (80 ticks after the incentive crash) | 48.3 / 36.7 | +1.2 / +1.0 | +7.2 / +3.4 | +34.2 / +12.8 | +69.4 / +30.7 |
| **R3 15 (pristine)** | 33.6 / 38.8 | +1.3 / −0.7 | +8.0 / +0.1 | +38.8 / +8.8 | **+78.8 / +25.6** |
| R2 55 (pristine, *with incentive 2*) | — | | | +61 / +23 | +105 / +44 |

- **Decision rule (review §4).** M1 as the reviewer framed it predicts a pristine gain that approaches R2's, with the
  same ratio in A and B: ×1.5–1.8. The data give ×1.14 in A and ×0.83 in B, which is within about 15% of R1 and in
  opposite directions. **So the slow, crash-driven credibility loss is rejected, and R8 is composition** (incentive ×
  seeding in R2's pristine campaign), plus pool effects.
- **Models fitted on R1 only predict R3 well:** m12_r1 scores 0.782 and m23_r1 scores 0.836, against 0.349 for
  persistence. m12_r1 predicts 35-tick gains of +75 / +27, against +79 / +26 observed. The R1 structure transfers to
  a campaign from a clean reset.
- **Reset replicate (G8):** A falls 42.8 → 33.5 (×0.78) and B falls 52.6 → 38.2 (×0.73), reaching the trough in about
  13 ticks. That matches R1/R2 (×0.75). Note that R3's troughs (A 33.5) lie **below** the crash floor (A 43). The reset
  drop is proportional to the reading, and the crash floor is a separate core.
- **The fitted M1 is a different thesis.** In the final m1 module, credibility is driven by the **departure rate**
  (the review's alternative driver), with a short memory (a1 = 0.13, about 7 ticks) and g1 = 6.3. It suppresses new
  interest while members are leaving: during the reset drop, during the incentive crash, and at a level of about 0.5 of
  normal churn. Eighty ticks after a crash it has recovered fully, so R3 cannot test it. It is consistent with R3.

## 15. Review responses (G1–G9)

Model v1: `greybox/social_contagion_model.py`. The docstring documents the changes, and v0 is kept as
`fits/social_contagion/social_contagion_model_v0.py`.

| Gap | Response |
|---|---|
| G1 base not identified | **Fixed.** Every parameter is a sigmoid box, and the pools are finite (N 80–3000). m12_all fits NA 297 / NB 185, which is physical because A saturates at 230. The capacity queue (kap/om/qa were pinned) is replaced by a first-order onboarding stage, kon 0.136 (interior). The one type per community replaces v0's unidentified i/r split. m12_all has **one parameter at a bound: gret = 0** (no incentive retention of churn), which is an optional base effect at zero, not a gain at a cap. Fits use 3 restarts. The `--horizons` curriculum was not needed, because the direct fits converge |
| G2 crash floor | **Fixed.** Cores K_c are never disappointed; the m2 disappointment acts only on M − K. m12_all fits **KA 42.4 / KB 28.9**, against observed floors of 43–44 / 31–33. The reset drop is separately an "expectant" share ψ of the reading (ψA 0.20, ψB 0.29), so a reading that differs from the floor is handled (R2, R3) |
| G3 bridge-path lag | **Fixed.** Introductions pass through a separate 3-stage lag, fitted at a_b = 0.058 (a mean delay of about 50 ticks). With it, **m3 is no longer needed.** m2 alone costs 8,798 and m2+m3 costs 8,723 (only 75 better), with a3u and a3d pinned at their minima (R becomes an integrator again). The continued growth after a bridge campaign (B14/R10) is the introduction pipeline draining |
| G4 M1 untested | **Tested** with the 50-step reserve (R3, §14). The slow crash-credibility thesis is rejected. The departure-driven fast credibility (the review's alternative driver) is supported by the cost: m1 adds 930 over m2 alone, against 75 for m3 |
| G5 coverage holes | **Not captured (no steps left).** P2 mid-level seeding, clean P3 at bridge 0, bridge on/off at constant seeding, the P5 gap test and the M2 ramp test were never run. Flagged as extrapolation risk. The model is smooth in u (the h(·) saturating interest), but linearity in seeding is unverified |
| G6 long-run level | **Addressed.** The m12_all equilibrium is unique and history-free, at **96.5 / 83.7** under recovery, reached by about t500 from any history (recovery, after a 200-tick seeding campaign, after a full pulse, after bridge). m23_all gives 101.9 / 88.2 and m2 is similar. It is consistent with R1's post-campaign decline heading towards about 110 / 90 at k 0.025 (review R4), and with the slow growth from the reset trough. The crash floor is transient: it lasts while the disappointed pool D reconsiders (ρ 0.063) and credibility recovers. It is still an extrapolation, since no undisturbed hold of more than 100 ticks exists. Full-pulse hold 199.2 / 132.0, flat. Incentive hold 131 / 95 |
| G7 incentive recruitment | **Fixed:** bounded iota per community, fitted at 0.0063 / 0.0060 (interior) |
| G8 reset shape | **Fixed:** the expectant share leaves through a ramping hazard, h(kr·L) with L rising at ar = 0.089, which gives the accelerating drop. kr 0.60 (interior) |
| G9 stability | **Passed:** see §17. Every parameter is inside its box except gret at 0 |

Tooling note: `fit.py --init` does **not** reset the parameters of modules that are inactive in the new fit to their
off values (`core.params_for` applies `fitted` after the off values). A first m2-only fit warm-started from m12_all
therefore kept g1 = 6.3 and silently reproduced m12. It was rerun from an init with g1 = 0
(`fits/social_contagion/v1/init_m2_from_m12.json`). Bootstrap `--warm` is not affected, because each candidate starts
from its own fit.

## 16. Model selection (framework §6.3)

Data: R1 (550) + R2 (400) + R3 (50). Log units, σ = 0.01, soft_l1. Fits are in `fits/social_contagion/v1/`, and
per-run scores use σ = 0.1 × std of R1+R2 after tick 20.

**Cross-run test (fit on R1 only, predict R2):** from `gates score`.

| Fit | R1 cost | at bounds | R2 score | R3 score |
|---|---:|---|---:|---:|
| m12_r1 | 583 | gret, a1, KB | **0.255** | 0.782 |
| m23_r1 | 732 | tauA, gret, KB, a3u | 0.252 | 0.836 |
| m13_r1 | 16,571 | — | 0.114 (fails) | — |
| base_r1 (relaxation, no mechanism) | 14,334 | — | 0.151 (fails) | — |
| persistence | | | 0.223 | 0.349 |

R1 alone cannot predict R2's joint seeding + incentive + bridge pulse (an unseen composition), so every R1 fit transfers
poorly to R2. m12 and m23 tie, and both only just beat persistence. m13 and the no-mechanism base are worse than
persistence, **so both pairs without M2 are rejected.**

**Refit on all data:**

| Fit | Cost | R1 / R2 / R3 score | at bounds |
|---|---:|---|---|
| **m12_all** | **7,868** | 0.682 / 0.717 / 0.817 | gret |
| m23_all | 8,723 | 0.692 / 0.681 / 0.816 | gret, psiB, ar, a3u, a3d |
| m2 only | 8,798 | — | gret, psiB, ar |
| m13_all | 63,063 | 0.441 / 0.480 / 0.639 | tauA, iotaA, iotaB |
| base_all | 63,434 | 0.440 / 0.397 / 0.760 | 6 params |

**Bootstrap** (`bootstrap5.json`: m12_all against m23_all, since m13 was rejected by 55k in cost; 5 draws per truth,
warm-started, 1 restart, block 50, skip 20):

| truth \ selected | m12 | m23 |
|---|---:|---:|
| m12 | **5** | 0 |
| m23 | 2 | **3** |

- **Margins when the truth wins:** m12 490–1,110; m23 36–243.
- **Real data:** m12 wins by **855**, which is ≥ the smallest m12 bootstrap margin (490) and inside m12's range.
- **Decision (§6.3.4):** the diagonal is 8/10. The real margin is inside the m12-truth range and far above any m23-truth
  margin. m23 also has three module/base parameters pinned (a3u and a3d at their minima, which is missing structure),
  and m3 adds only 75 over m2 alone. **Accept M1 + M2, confidence medium.** m12 can absorb m23-generated data 2/5 times,
  so m12 is the more flexible model. The M1 in the fit is a fast, departure-driven credibility, not the slow thesis
  that R3 rejected.

## 17. Final model and hand-off

- **Submitted model:** M1 + M2 (`fits/social_contagion/v1/m12_all.json`, copied to `final.json`), in
  `greybox/social_contagion_model.py` v1. Confidence **medium**. M2 is certain (every fit without it fails). M1 over
  M3 rests on a cost margin of 855 and a 5/5 + 3/5 confusion matrix.
- **Scores:**
  - Cross-run (fit on R1, predict R2): 0.255 against 0.223 for persistence, which passes but only just. The
    composition was not in R1.
  - All-data fit: 0.68 / 0.72 / 0.82 on R1 / R2 / R3.
- **Gates:**
  - Local score: passes (0.255 > 0.223).
  - Stability: **passes**. 200 schedules, 8 × 40,000 steps, 0 failures, range 20–217 (A) / 13–137 (B), worst alternation
    0.016. File `fits/social_contagion/v1/stability_m12.json`.
  - Contract: **passes** from the extracted ZIP. 40 × 4,000 steps take 5.0 s, all malformed-input cases are OK, and the
    credential scan is clean.
- **Package:** `toronto26-participant-kit/models/social_contagion/` (predict.py, social_contagion_model.py,
  params.json) and `toronto26-participant-kit/submission-social_contagion-v1.zip` (5.6 KB). Package with explicit
  `--data R1 R2 R3`, because the default glob picks up `*_battery.json` and fails.
- **Budget:** 1,000 of the 1,000 CAP spent (R1 550, R2 400, R3 50). The gateway has 1,000 remaining, none of it
  allocated.
- **Open issues:**
  1. **Long-run recovery level (96 / 84) is an extrapolation.** It dominates 4,000-step scoring, and no undisturbed
     hold of more than 100 ticks exists. m12 and m23 agree within 6%. The rejected fits (m13, base) give 54 / 40.
  2. **Composition and mid-level controls are untested (G5):** mid-level seeding, seeding + incentive at bridge 0, and
     bridge share between 0.6 and 1.0. The weak cross-run score shows how much R2's composition taught the model.
  3. **M1 against M3 is only moderately resolved.** m23 truth is misclassified 2/5 times. The fitted M1
     (departure-driven, fast) was not directly probed. If the public score is weak, the fallback candidate is
     m23_all (8,723), which has near-identical long-run levels.
