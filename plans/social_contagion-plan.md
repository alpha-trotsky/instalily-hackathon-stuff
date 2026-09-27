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
