# Ad auction plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 (overnight job, `plans/overnight-framework.md`). CAP = 1,000 steps
(Run 1 ≤ 550, Run 2 ≤ 400, reserve ≥ 50). Budget at start: 2,000 remaining (free read).

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted):** "Observe auction win fraction, spend and completed conversions. Choose bid, per-tick budget and
targeting breadth. Broader targeting contains narrower audiences, whose members can be in different stages of
attention and purchase. A won impression is not necessarily an immediate conversion: started purchases remain
committed and compete for limited fulfillment work. Different audiences require different amounts of fulfillment
work. Converted customers take time to become available again. Rival campaigns may move a shared pool of capital
between audiences, repeated exposure may temporarily remove reachable people, and broad introduction may change
the effect of later follow-up. Equal spending can therefore leave different future opportunities. Initial reports
are the only random initial state; hidden populations and commitments begin from the same reference conditions on
every reset: people are available and unprepared, with no pending purchases or exposure recovery."

**Observables** and initial-reading ranges (docs):

| Observable | Initial range | Notes |
|---|---|---|
| win_rate | 0.25 – 0.5 | fraction in [0, 1]; auction outcome vs rival bids → likely logistic in bid; linear units probably |
| spend | 10 – 30 | per tick; recovery budget_cap = 20 sits inside the range → spend is probably **capped by budget** at recovery |
| conversions | 0.4 – 1.5 | completed purchases per tick; output of a commit → fulfillment pipeline (delayed, saturating) |

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u | Range of u | Notes |
|---|---|---:|---:|---|---|---|
| bid | [0, 5] | **1.5** | 5 | (bid − 1.5)/3.5 | [−0.43, 1] | recovery **not at a bound**: bid 0–1.5 is the untested side (bid 0 → probably no wins at all) |
| budget_cap | [0, 100] | **20** | 100 | (cap − 20)/80 | [−0.25, 1] | recovery **not at a bound**: cap 0 → spend 0 |
| targeting_breadth | [0.1, 1] | **0.55** | 0.775 | (t − 0.55)/0.225 | **[−2, 2]** | recovery **not at a bound**, and the in-bounds range is 4× the pulse span on each side. Narrow (0.1) and broadest (1.0) are both far outside the recovery→pulse segment |

No control's recovery value is at a bound; breadth especially needs P2-style levels outside [0.55, 0.775] (sustained
and joint scoring episodes may use any in-bounds value).

**Delay / commitment phrases → pipeline stages (base structure, not mechanisms):**
- "A won impression is not necessarily an immediate conversion: started purchases remain committed and compete for
  limited fulfillment work" → impressions → started purchases (a committed queue) → fulfillment at a limited
  capacity → conversions. Expect conversions to lag win_rate/spend and to **saturate** (capacity) and to keep
  flowing after bidding stops (queue drains).
- "Different audiences require different amounts of fulfillment work" → work per purchase depends on breadth
  (broad audiences probably need more work) → breadth changes the fulfillment throughput.
- "Converted customers take time to become available again" → a converted pool that returns to the available pool
  after a delay → sustained conversion depletes the available audience; slow recovery.
- Reset: "people are available and unprepared, with no pending purchases or exposure recovery" → queue empty,
  fatigue 0, priming 0, everyone available at reset. Expect a **reset transient**: conversions start low (queue
  empty) and build, or start high (full available pool) and deplete.

**Anything tied to time since reset:** no seasonality phrase. Only the reset transient.

**Cross couplings expected:** spend ≈ min(budget_cap, impressions × clearing price); win_rate = f(bid vs rival bid)
possibly throttled by budget (pacing); conversions driven by won impressions × audience responsiveness.

**Organizer-suggested comparisons (P9):** the ad_auction brief has no explicit "Compare …" sentence. The nearest is
"**Equal spending can therefore leave different future opportunities.**" → P9: produce (roughly) equal spend with
different compositions (bid-driven vs budget-driven vs breadth-driven), then run the same follow-up (recovery) and
compare conversions / win_rate afterwards. Also the mechanism sentence "broad introduction may change the effect of
later follow-up" names its own probe: broad-then-narrow vs narrow-then-broad (P6).

## 2. The three mechanisms (§3.2)

Quoted from the brief (one sentence, three clauses; confidence: high that these are the three candidates):

- **M1 rival capital:** "Rival campaigns may move a shared pool of capital between audiences".
- **M2 exposure fatigue:** "repeated exposure may temporarily remove reachable people".
- **M3 broad priming:** "broad introduction may change the effect of later follow-up".

## 3. Theses (§3.3)

### M1 rival capital

| Field | Content |
|---|---|
| Quote | "Rival campaigns may move a shared pool of capital between audiences" |
| Hidden state | R: rival capital in the audiences we target (fixed total pool, redistributed) |
| **Driver** | our pressure on an audience: our spend (or bid) in the targeted audience; possibly the audience's profitability (conversions) |
| **What it changes** | the competing bid → **win_rate** (and cost per impression → spend at a given cap); indirectly conversions |
| Timescales | builds over 10–50 ticks; fades (capital moves back) over 10–100 ticks |
| P1 bid on/off | present: win_rate jumps up at bid-on then **drifts down** during the hold (rivals move in); after bid-off win_rate **undershoots** the old baseline, recovers slowly. Absent: monotone steps, no drift |
| P1 budget on/off | present: more spend in the audience attracts rivals → win_rate drifts down under a budget pulse even at fixed bid |
| P1 breadth | present: moving to a different audience mix finds a different rival allocation; win_rate transient when breadth changes that fades as rivals follow |
| P5 gap | present: second bid pulse starts from a lower win_rate after a short gap |
| P6 order | order effects in win_rate, not conversions-per-impression |
| P8 same spend, other cause | present: win_rate response depends on spend (whatever the cause) |
| P7 long hold | drift in win_rate over > 100 ticks |

### M2 exposure fatigue

| Field | Content |
|---|---|
| Quote | "repeated exposure may temporarily remove reachable people"; "no … exposure recovery" at reset |
| Hidden state | E: exposure-fatigued (unreachable) people in the targeted audience; recovers over time |
| **Driver** | won impressions per reachable person (≈ win_rate × volume / audience size) — narrow targeting fatigues faster |
| **What it changes** | reachable audience → impressions available → **conversions** (and possibly win_rate/spend if the auction has fewer eligible impressions) |
| Timescales | builds 10–50 ticks; recovers 20–100 ticks |
| P1 bid on/off | present: conversions rise then **sag** during a sustained high-bid hold; after bid-off conversions dip **below** baseline (fatigued audience) then recover. Absent: conversions settle at a plateau set by capacity |
| P1 breadth | present: narrower targeting fatigues faster (bigger sag); broadening relieves fatigue |
| P5 gap | **second pulse weaker after a short gap** than after a long gap |
| P6 broad→narrow vs narrow→broad | broad first also exposes the narrow sub-audience (contained) → narrow follow-up **weaker** |
| P7 long hold | slow decline to a fatigue equilibrium |

### M3 broad priming

| Field | Content |
|---|---|
| Quote | "broad introduction may change the effect of later follow-up"; "people are available and unprepared" at reset; "members can be in different stages of attention and purchase" |
| Hidden state | P: prepared (introduced) fraction of the audience; builds with broad exposure, fades slowly |
| **Driver** | won impressions × breadth (broad introduction); possibly only breadth above the recovery level |
| **What it changes** | conversion probability of later (narrower) impressions → **conversions per win** (gain mode); may also shift which audience stage is reached |
| Timescales | builds 10–50 ticks; fades 50–200 ticks |
| P1 breadth on/off | present: after a broad pulse, conversions at recovery breadth are **above** the pre-pulse baseline for a while (primed audience); absent: return straight to baseline |
| P1 bid | present: conversions rise slowly during a hold (priming accumulates) — the opposite of M2's sag |
| P5 gap | second pulse **stronger** after a short gap (priming remains) |
| P6 broad→narrow vs narrow→broad | **narrow follow-up stronger after broad introduction** (opposite sign to M2) |
| P7 long hold | slow rise in conversions per win |

## 4. Separation table (§3.4)

| Probe | M1 rival capital | M2 exposure fatigue | M3 broad priming |
|---|---|---|---|
| P1 bid on (hold) | win_rate up then **drifts down** | conversions up then **sag**; win_rate flat | conversions **creep up** |
| P1 bid off | win_rate **undershoots**, slow recovery | conversions **dip below** baseline | conversions stay **above** baseline for a while |
| P1 budget on/off | win_rate drifts down (spend attracts rivals) | conversions sag if more wins | slight priming |
| P1 breadth on/off | win_rate transient on each change | broadening relieves fatigue; narrowing back → dip | after broad pulse, conversions **above** baseline |
| P5 two pulses, short vs long gap | 2nd pulse lower win_rate (short gap) | 2nd pulse **weaker** conversions (short gap) | 2nd pulse **stronger** conversions (short gap) |
| P6 broad→narrow vs narrow→broad | win_rate order effect | narrow after broad **weaker** | narrow after broad **stronger** |
| P8 same spend via bid vs via budget | same win_rate drift for same spend | depends on wins, not spend | depends on breadth × wins |
| P7 long hold (≥200) | win_rate drift | conversions slow decline | conversions slow rise |

Pairs:
- **M1 vs M2:** which observable carries the memory: win_rate drift/undershoot (M1) vs conversions sag/dip with flat
  win_rate (M2). P1 bid hold and P8.
- **M1 vs M3:** win_rate memory (M1) vs conversions-per-win memory after broad exposure (M3); P1 breadth off and P6.
- **M2 vs M3:** **opposite signs** on P5 (2nd pulse weaker vs stronger) and P6 (narrow after broad weaker vs
  stronger), and on the bid-off step (dip vs elevation).

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 (start) | — | — | 0 | 2,000 |
| 2026-09-27 01:12 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 2026-09-27 01:12 | R1 | 40–59 (P0 recovery, ext) | 20 | 1940 |
| 2026-09-27 01:13 | R1 | 60–79 (P0 recovery, ext) | 20 | 1920 |
| 2026-09-27 01:13 | R1 | 80–119 (P1 bid 5 on) | 40 | 1880 |
| 2026-09-27 01:13 | R1 | 120–144 (P1 bid 5 on, ext) | 25 | 1855 |
| 2026-09-27 01:14 | R1 | 145–184 (P1 bid off = recovery) | 40 | 1815 |
| 2026-09-27 01:14 | R1 | 185–209 (P1 bid off, ext) | 25 | 1790 |
| 2026-09-27 01:14 | R1 | 210–249 (P1 budget 100 on) | 40 | 1750 |
| 2026-09-27 01:15 | R1 | 250–279 (P1 budget off = recovery) | 30 | 1720 |
| 2026-09-27 01:15 | R1 | 280–329 (P1 breadth 0.775 on) | 50 | 1670 |
| 2026-09-27 01:15 | R1 | 330–354 (P1 breadth on, ext) | 25 | 1645 |
| 2026-09-27 01:16 | R1 | 355–404 (P1 breadth off = recovery) | 50 | 1595 |
| 2026-09-27 01:16 | R1 | 405–434 (bid 0: other side of recovery) | 30 | 1565 |
| 2026-09-27 01:17 | R1 | 435–469 (recovery after bid 0) | 35 | 1530 |
| 2026-09-27 01:17 | R1 | 470–479 (recovery) + 480–509 (breadth 0.1: other side) | 40 | 1490 |
| 2026-09-27 01:17 | R1 | 510–544 (recovery after narrow). **R1 complete: 545 steps** | 35 | 1455 |

Spend summary so far: R1 = 545 steps (cap 550). (Timestamps: machine clock, approximate to a minute.)

## 6. Run 1 observations (`data/ad_auction/R1.json`, 545 ticks, initial reading win 0.376 / spend 15.8 / conv 0.877)

Schedule: recovery 0–79 | bid 5 80–144 | recovery 145–209 | budget 100 210–249 | recovery 250–279 | breadth 0.775
280–354 | recovery 355–404 | **bid 0** 405–434 (other side) | recovery 435–479 | **breadth 0.1** 480–509 (other side) |
recovery 510–544. Plot: `data/ad_auction/R1_r0_battery.png`; battery JSON `data/ad_auction/R1_battery.json`.

Settled / end-of-hold levels (means of the last 10–20 ticks):

| Setting (ticks) | win_rate | spend | conversions | conv/spend | spend/win |
|---|---:|---:|---:|---:|---:|
| recovery, P0 end (60–79) | 0.254 | 13.42 | 3.18 | 0.237 | 52.9 |
| bid 5 (125–144) | 0.332 | **20.00 (cap)** | 3.20 | 0.160 | 60.2 |
| recovery (190–209) | 0.265 | 13.17 | 3.28 | 0.249 | 49.7 |
| budget 100 (230–249) | 0.268 | 12.65 | 3.20 | 0.253 | 47.2 |
| recovery (260–279) | 0.268 | 12.53 | 3.12 | 0.249 | 46.8 |
| breadth 0.775 (335–354) | 0.230 | 17.74 | 3.53 | 0.199 | 77.1 |
| recovery (385–404) | 0.265 | 12.08 | 3.00 | 0.248 | 45.5 |
| bid 0 (425–434) | 0.000 | 0.00 | → 0 (drain) | — | — |
| breadth 0.1 (500–509) | 0.308 | 3.15 | 0.84 (still falling) | 0.265 | 10.2 |

- **The reset reading is not informative.** The first observation is win 0.147, spend 20.1, conv 0.005 whatever the
  initial reading (0.376 / 15.8 / 0.877): the pipeline starts empty and the audience fully rested.
- **Budget cap binds only on a rested audience or at high bid.** Spend sits exactly at the cap (20 ± noise) for 28
  ticks after reset, for 12 ticks after the bid-0 rest and during the whole bid-5 hold; otherwise spend < cap. While
  the cap binds, win_rate is **throttled** (reset: 0.147 rising to 0.25 as the cap stops binding; bid 5: jumps to
  0.29, then creeps up to 0.345 while spend stays capped). → win_obs ≈ p_win(bid) × min(1, cap / uncapped spend).
- **Rested audience → depletion.** After every rest (reset, bid 0 for 30, breadth 0.1 for 30 which rests the outer
  audience) spend falls from the cap to ~13 over ~40 ticks and conversions overshoot (4.4, 4.2, 3.97) before settling
  at ~3.1. Consistent with a reachable pool that is depleted by exposure and/or by conversions and recovers slowly.
  After 30 ticks of bid 0 the pool is **not fully** recovered (throttled win 0.213 vs 0.147 at reset; capped 12 ticks
  vs 28) → pool recovery time ≳ 50–100 ticks.
- **Budget 100 at bid 1.5: no effect** (win, spend flat; conversions continue a slow drift). Budget matters only
  jointly with a high bid or a rested audience (P3 bid+budget is the key composition test).
- **Bid 5 on:** win +0.04 at once, spend to the cap at once, conversions bump 3.13 → 3.85 (peak 9 ticks later) and
  sag back to 3.2 (pool depletion). **Bid off:** win drops to 0.222 (below the pre-pulse 0.25) and recovers over
  ~30 ticks to 0.266; spend drops to 10.2 (below baseline) and recovers over ~30; conversions dip to 2.26 then
  overshoot to 3.30 before a slow return. On/off not mirror images (on: fast; off: undershoot + slow recovery).
- **Breadth 0.775 on:** win drops 0.27 → 0.20 then creeps up to 0.23; spend 12.5 → 19 then slowly down to 17.7;
  conversions **dip first** (3.11 → 2.94 over 8 ticks) although spend rose 50%, then rise to 3.55.
  **Off:** win jumps to 0.285 then creeps down to 0.265; spend 12.5 dipping to 11.9; conversions **rise** to 3.77
  (8 ticks) although spend fell 30%, then fall **below** the old baseline (2.93 at tick 404, still falling).
- **Breadth 0.1 (narrow):** win 0.27 → 0.355 then **creeps down** to 0.30 (rival pressure building in the narrow
  audience?); spend 2.6 rising to 3.2; conversions drain towards ~0.7. Back to 0.55: win 0.228 then creeps up to
  0.27; spend 18.3 → 14 (outer audience rested); conversions overshoot to 3.97.
- **Bid 0:** win and spend 0 at once (noise floor ~0.003, clipped at 0). Conversions: **2-tick dead time**, then a
  geometric drain ≈ 0.86/tick (0.14 of the committed stock completes per tick). Restart: 2-tick dead time, then a
  near-linear rise of +0.25–0.3/tick (multi-stage pipeline / limited fulfillment).
- **Slow drift at recovery:** settled recovery spend 13.42 (tick 70) → 12.53 (270) → 12.08 (395); conversions
  3.18 → 3.12 → 3.00. A slow component (> 200 ticks) — P7 needed.
- **Noise σ:** win 0.0047 (constant, additive; 1.9% of level), spend 0.066 (~0.5%, partly proportional),
  conversions 0.012 (~0.4%). Values at 0 are clipped at 0 (win/spend during bid 0).
- **Couplings:** conversions follow spend with a lag (level corr 0.84 at lag 10); diff corr 0.61 at lag 6.

## 7. Behaviour catalogue v1 (after Run 1)

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B1 | First observation ignores the initial reading: win 0.147, spend = cap, conv ≈ 0 | R1 0–2 | fixed reset convention: empty pipeline, fully available audience | open (model from convention) |
| B2 | Spend = min(cap, uncapped spend); while capped, win_rate is throttled below the bid-determined level | R1 0–28, 80–144, 435–447 | budget pacing: win_obs = p_win × min(1, cap/S_u) | open |
| B3 | Rested audience: spend at cap then decays to ~13 over ~40 ticks; conversions overshoot 4.2–4.4 | R1 0–79, 435–479, 510–544 | pool depletion by exposure (M2) and/or by conversions (base "converted customers take time") | open |
| B4 | Pool recovery is slow: 30 ticks of bid 0 recover only part of the reset condition | 0.213 vs 0.147 throttled win; 12 vs 28 capped ticks | slow return of converted / exposed people (τ ≳ 50–100) | open |
| B5 | Budget 100 at bid 1.5 has no effect | R1 210–279 | cap not binding | open (structure of B2) |
| B6 | Conversions: 2-tick dead time, geometric drain 0.86/tick, near-linear rise | R1 405–447 | committed purchases pipeline (≥ 2 stages) with limited fulfillment | open |
| B7 | Breadth on: conversions dip before rising; breadth off: conversions rise (bump to 3.77) before falling below baseline | R1 280–300, 355–404 | (a) breadth-dependent fulfillment work with a backlog (base); (b) M3 priming by broad introduction; (c) depletion of primed people | open — key separation target |
| B8 | win_rate high-pass on breadth: broad → drop then creep up; narrow → jump then creep down; reverse on return | R1 280–380, 480–545 | M1 rival capital following our targeting/spend density (τ ~ 20–30) | open — M1 candidate |
| B9 | After bid-off, win_rate undershoots (0.222) then recovers (τ ~ 30) while spend recovers from 10.2 | R1 145–209 | M1 rivals attracted during our high-bid phase; or pool/price effect | open |
| B10 | Bid 5 conversions bump (3.85) then sag to 3.2 at constant capped spend | R1 80–144 | pool depletion (B3) + fewer impressions per spend at the higher price | open |
| B11 | Slow drift at recovery over the whole run (spend 13.4 → 12.1, conv 3.18 → 3.0) | table above | slow pool / rival component (> 200 ticks) | open — needs P7 |
| B12 | Noise: win additive σ 0.0047; spend σ 0.066; conv σ 0.012; zeros clipped | battery | measurement noise | linear units |

Units: win_rate linear (bounded fraction, additive noise); spend linear (hard cap, zeros); conversions linear (zeros
during drain). All three hit 0 in R1, so log units are ruled out.

## 8. Model module and Run-1 pair fits

Module: `toronto26-participant-kit/greybox/ad_auction_model.py` (physical-unit controls; ~8 ms per 545-tick
rollout). Base structure from the brief's facts + catalogue: 5 nested audience rings (breadth edges 0, .1, .325,
.55, .775, 1), per-ring availability, auction win prob `bid^h/(bid^h+K_r^h)`, price `pi0 (bid/1.5)^rho`,
**budget pacing** (smooth min of uncapped spend and the cap; throttle also lowers win_rate, B2), purchases → 2-tick
dead time → prepare stage → fulfillment queue with **ring-dependent work per purchase** and a work capacity (B6,
B7a), and a pool of unavailable (committed/converted) people that returns at rate `ret` (B3/B4). Reset: everything
empty/available (B1; the initial reading is ignored). Mechanism modules written from the theses before fitting:
m1 rival capital per ring (driver: our spend density in the ring, raises the competing threshold), m2 exposure
fatigue per ring (driver: impressions per ring member, removes reachable people), m3 broad priming (global, driver:
exposure of the rings above 0.55, multiplies purchase propensity by 1 + g3 P).

Fits on R1 (all 545 ticks, linear units, σ = NOISE, soft_l1, init = base params without module params, module
gains started nonzero; max_nfev 400–500, 1 restart — quick fits for probe ranking only):

| Fit | Cost | Train score (σ = 0.1 std) | RMSE win / spend / conv | Module params | Notes |
|---|---:|---:|---|---|---|
| base (`base_r1`) | 23,509 | 0.552 | 0.0127 / 0.713 / 0.289 | — | om 3.1 (broad rings need ~2× work), capf 2.13 (capacity binds), ret 0.0085 (pool return τ ≈ 120) |
| m1+m2 (`m12_r1`) | 20,979 | 0.561 | 0.0171 / 0.641 / 0.245 | a_m1 0.038, g1 1.06; **a_m2 → 1.0 (pinned)**, e2 0.69 | m2 acts as a static cut, not a memory |
| **m1+m3** (`m13_r1`) | **20,062** | 0.556 | 0.0194 / 0.691 / 0.227 | a_m1 0.036, g1 0.25; **a_m3 → 1.0, g3 −5.0 (pinned)** | m3 used as an instantaneous broad-exposure penalty |
| m2+m3 (`m23_r1`) | 22,845 | 0.560 | 0.0128 / 0.747 / 0.277 | a_m2 0.0096, e2 0.08; a_m3 → 1, g3 −5.1 | |

Plot: `fits/ad_auction/pairs_r1.png` (and `base_r1.png`). Readings:
- m1 (rival capital) buys the win_rate / spend undershoot after bid-off (B9) — both m1 pairs beat m23 by ~2,000.
  But the m1 fits also predict a win_rate **overshoot** after the bid-0 rest (440–460) that the data do not show,
  and they do not reproduce the narrow-breadth creep-down (B8). The m1 driver (our spend density) is probably wrong
  or incomplete — flag for the modeler.
- m3 and m2 both end up with memory rates pinned at 1 (static terms): they stand in for missing structure (the
  bid-5 conversion bump/sag B10 and the breadth transients B7), not evidence. No pair reproduces the bid-5
  conversions bump (3.85) or the post-bid-off conversion dip (2.26).
- All three pairs fit the win_rate throttle and the rested-audience depletion well; the base structure carries most
  of the fit.

## 9. Run 2 design (§4.4)

Candidates simulated through the three R1 pairs after a common 40-tick P0; disagreement = mean |Δ| / (0.1 std) over
pairs, per 100 steps:

| Candidate | Steps | Pair diff 12-13 / 12-23 / 13-23 (σ) | Score /100 steps |
|---|---:|---|---:|
| B P3 bid 5 + cap 100 (40) + rec 40 | 80 | 22.5 / 16.2 / 10.0 | **20.3** |
| E P2 bid 3.25 + cap 100 (40) + rec 40 | 80 | 21.1 / 12.0 / 11.0 | 18.4 |
| A P7 pulse action (5, 100, 0.775) 200 + rec 40 | 240 | 36.9 / 26.2 / 12.1 | 10.4 |
| J cap 100 + breadth 1.0 (40) + rec 40 | 80 | 6.4 / 7.5 / 4.5 | 7.7 |
| D P5 bid5+cap100 pulses, gaps 10 vs 40 | 200 | 18.6 / 12.7 / 10.3 | 6.9 |
| H breadth 1.0 (60) + rec 40 | 100 | 3.4 / 3.5 / 1.2 | 2.7 |
| C P6 breadth 1.0→0.1 vs 0.1→1.0 | 160 | 2.4 / 2.7 / 1.3 | 1.3 |
| I bid 5 + breadth 0.775 at cap 20 | 80 | 0.6 / 0.8 / 0.5 | 0.8 |
| G P7 recovery 200 | 200 | 0.3 / 0.5 / 0.6 | 0.2 |

The disagreement is dominated by the unthrottled high bid (bid 5 with cap 100), never seen in R1: every pair
extrapolates it differently. It is also the key composition test (B5: the cap only matters jointly with the bid).

**Chosen Run 2 (400 steps, fresh reset):**

| Ticks | Segment | Probe / purpose |
|---|---|---|
| 0–24 | recovery 25 | P0 (reset replicate; different initial reading) |
| 25–64 | bid 5, cap 100, breadth 0.55 (40) | **P3** joint bid+budget (top-ranked B) |
| 65–79 | recovery 15 | short gap |
| 80–99 | bid 5, cap 100 (20) | **P5** second pulse after a short gap (compare with the first 20 ticks of 25–64) |
| 100–124 | recovery 25 | |
| 125–139 | breadth 1.0 (15) | broad introduction (breadth other side, u = +2) |
| 140–159 | breadth 0.1 (20) | **P6 / M3 probe**: narrow follow-up after broad introduction; compare with R1 480–509 (narrow after recovery) |
| 160–359 | pulse action bid 5, cap 100, breadth 0.775 (200) | **P7** long hold (sustained level at the full pulse action; A) |
| 360–399 | recovery 40 | off-step after long exposure (recovery history) |

Not covered (reasons): P2 bid mid-level (E, rank 2) — no room after P7 ≥ 200; candidate for the Phase-C reserve.
Full P6 reversed order (narrow→broad) — R1 has narrow-from-recovery and broad-from-recovery as the reference halves.

## 10. Run 2 spend log (continues §5)

| Local time | Run | Ticks | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 01:29 | R2 | 0–24 (P0 recovery, fresh reset) | 25 | 1430 |
| 2026-09-27 01:30 | R2 | 25–64 (P3 bid 5 + cap 100) | 40 | 1390 |
| 2026-09-27 01:31 | R2 | 65–79 (gap recovery) + 80–99 (P5 second pulse bid 5 + cap 100) | 35 | 1355 |
| 2026-09-27 01:32 | R2 | 100–124 (recovery) + 125–139 (breadth 1.0) + 140–159 (breadth 0.1 after broad) | 60 | 1295 |
| 2026-09-27 01:33 | R2 | 160–209 (P7 pulse action, part 1) | 50 | 1245 |
| 2026-09-27 01:34 | R2 | 210–284 (P7 pulse action, part 2) | 75 | 1170 |
| 2026-09-27 01:35 | R2 | 285–359 (P7 pulse action, part 3; P7 total 200) | 75 | 1095 |
| 2026-09-27 01:36 | R2 | 360–399 (recovery after long exposure). **R2 complete: 400 steps** | 40 | 1055 |

Spend summary: R1 = 545 (cap 550), R2 = 400 (cap 400), total **945**. Budget remaining 1,055; **55 steps of the
1,000 CAP are left as the Phase-C reserve.**

## 11. Run 2 observations (`data/ad_auction/R2.json`, 400 ticks, initial reading win 0.325 / spend 21.8 / conv 1.03)

Plot + battery: `data/ad_auction/R2_r0_battery.png`, `R2_battery.json`. R1 pair fits predicting R2:
`fits/ad_auction/pairs_r1_on_R2.png`.

| Segment (ticks) | win_rate | spend | conversions |
|---|---|---|---|
| P0 (0–24) | 0.145 → 0.217 (throttled) | 20 (cap) | 0 → 4.0 — **identical to R1** (reset is deterministic; the initial reading is irrelevant) |
| P3 bid 5 + cap 100 (25–64) | 0.55 → **creeps up** to 0.60 | **73 → 25.7** (τ ≈ 12, not settled) | peak **6.95** at tick 35, sag to 4.9 |
| gap recovery (65–79) | 0.272 → 0.255 (above baseline and falling: **no undershoot**, unlike the R1 bid-off) | 7.7 → 10.1 | 4.8 → 2.9 |
| P5 2nd pulse (80–99) | 0.59 → 0.60 | **33 → 24.6** (the first pulse started at 73) | peak **4.56** (first pulse 6.95) |
| recovery (100–124) | ~0.26 | 7.5 → 11.2 | 4.5 → 2.4 |
| breadth 1.0 (125–139) | 0.14 (throttled) | 20 (cap) | **dips** 2.45 → 2.10 |
| breadth 0.1 after broad (140–159) | 0.35 → 0.33 | 3.0 → 3.2 | **held ~2.19 for 6 ticks**, then drains (R1 narrow-after-recovery drained at once) |
| P7 pulse action 5/100/0.775 (160–359) | 0.49 → 0.56, settled **0.559** | 86 → **34.4** (τ ≈ 25; settled by ~270) | peak 6.1 (tick 176), **plateau 5.37–5.44 for 60 ticks (185–248)**, then an abrupt drop over 5 ticks to 4.9 and a slide to **4.47** (settled) |
| recovery after P7 (360–399) | 0.28 → 0.265 | 7.4 → 11.8 (**still rising**, slow) | 2 ticks flat at 4.44, drain to 2.59, then slowly up (2.67) |

Separating probes and P9 that ran:
- **P3 (bid × budget composition):** ran. The cap was the binding constraint throughout R1; with cap 100 the true
  bid-5 win probability is only **≈ 0.55–0.60**, far below every R1 fit's extrapolation (0.8–1.0). The R1 fits
  identified the auction curve from throttled data, so the modeler must refit on R1+R2.
- **P5 gap test:** ran (15-tick gap). The second pulse is much weaker (spend starts at 33 vs 73; conversions peak
  4.6 vs 7.0): a strong depletion memory that has not recovered in 15 ticks. Consistent with both the base
  unavailable pool (ret τ ≈ 120) and M2 fatigue; **not** with M3 priming (M3 predicted a stronger 2nd pulse).
- **P6 broad → narrow (M3 probe):** ran in short form. No conversion bump on the narrow follow-up after broad
  introduction; only a 6-tick hold, explained by the fulfillment backlog of broad (high-work) purchases. Weak
  evidence against a positive M3; a negative M3 ("broad introduction reduces the follow-up effect") is not excluded.
- **P7 long hold (200):** ran at the full pulse action. Settled levels measured cleanly (win 0.559, spend 34.4,
  conv 4.47); no slow drift after ~tick 270.
- **P9 "Equal spending can therefore leave different future opportunities":** partly. R1 bid 5 at cap 20 (spend
  20), R1 breadth 0.775 (spend ~19) and R2 breadth 1.0 at cap 20 (spend 20) give equal spend with different
  subsequent recoveries (B7, B9). Not a cleanly designed comparison; open.
- Not run: P2 (mid bid), the full reversed-order P6 (narrow → broad).

## 12. Behaviour catalogue v2 (after Run 2)

B1–B12 from §7 stand (B1 confirmed by the identical R2 reset). Updates and new behaviours:

| ID | Behaviour | Evidence | Candidate explanations | Status |
|---|---|---|---|---|
| B2 (upd.) | Throttle confirmed: the unthrottled bid-5 win rate is ≈ 0.55 at first; cap 100 does not bind after the first ticks (spend 73–86 < 100) | R2 25–64, 160–359 | auction curve p(bid) saturating near 0.6 at bid 5 (not a steep logistic) | open: R1 fits extrapolate p(5) ≈ 0.8–1.0 |
| B3 (upd.) | Depletion is large and fast at high spend: spend 73 → 26 in 40 ticks (bid 5, cap 100), 86 → 34 at the pulse action | R2 25–64, 160–270 | exposure/commitment depletion of the reachable pool; rested pool ~3× the settled level | open |
| B13 | **A second pulse after a 15-tick gap is much weaker** (spend 33 vs 73; conv peak 4.6 vs 7.0) | R2 80–99 vs 25–44 | slow pool return (base `ret`) and/or M2 fatigue; against M3 priming | open: key M2 evidence |
| B14 | **Fulfillment capacity plateau**: conversions flat at 5.37–5.44 for 60 ticks in the P7 hold, then an abrupt drop (5 ticks) to the inflow rate, sliding to 4.47 | R2 185–265 | capacity-limited fulfillment with a backlog built in the first 25 ticks of high spend; the abrupt end is the backlog clearing | open: base structure (capacity ≈ 5.4 conversions/tick at breadth 0.775) |
| B15 | Conversion peak 6.95 at breadth 0.55 vs 6.1 at 0.775 (plateau 5.4 at 0.775): capacity in conversions/tick depends on breadth | R2 35 vs 176 | work per purchase rises with breadth ("Different audiences require different amounts of fulfillment work") | open: base (`om`) |
| B16 | win_rate creeps **up** during every unthrottled high-bid hold (0.55 → 0.60; 0.49 → 0.56) | R2 25–64, 160–260 | M1 rivals withdraw capital from audiences we dominate; or a composition shift as core rings deplete (rings differ in competition) | open: M1 candidate |
| B17 | After a cap-100 pulse the recovery win_rate is **above** baseline (0.272–0.28) and falls; after the R1 cap-20 bid pulse it was **below** (0.222) and rose | R2 65–79, 360–399 vs R1 145–175 | M1 with a driver other than spend (e.g. rivals respond to our win share); or ring composition | open: the reviewer should check this contrast first |
| B18 | Slow spend recovery after long high exposure: 7.4 → 11.8 in 40 ticks, still rising | R2 360–399 | pool return τ ≈ 100+ (`ret` ≈ 0.0085 in the base fit) | open |
| B19 | 2-tick conversion dead time confirmed on every switch (R2 65, 360) | R2 | pipeline dead time (DEAD = 2) | modeled (base) |

R1-fitted models predicting R2 (RMSE win / spend / conv): base 0.176 / 7.33 / 1.33; m12 0.126 / 5.36 / 1.05;
m13 0.288 / 19.96 / 1.38; m23 0.197 / 10.42 / 1.26. All fail mainly on B2 (bid-5 win probability) and B14
(capacity), i.e. on extrapolating the base structure, not on the mechanisms. m12 is the least bad. Do not read the
pair ranking from these R1 fits.

## 13. Status / hand-off to reviewer

- **Files:** data `toronto26-participant-kit/data/ad_auction/R1.json` (545 ticks) and `R2.json` (400 ticks), with
  battery PNG/JSON next to them. Model `greybox/ad_auction_model.py`. Fits `fits/ad_auction/{base,m12,m13,m23}_r1.json`
  (+ `.log`), `init_r1.json` (base params without module params), plots `base_r1.png`, `pairs_r1.png`,
  `pairs_r1_on_R2.png`.
- **Budget:** 945 of the 1,000 CAP spent; remaining budget 1,055; **Phase-C reserve 55 steps.** Suggested use:
  P2 bid mid-level with cap 100 (bid 3.25, ~30 + 25 recovery), the highest-ranked uncovered probe.
- **Open, in priority order:**
  1. Refit the base on R1+R2. The auction curve (p(5) ≈ 0.56), fulfillment capacity (B14/B15) and depletion size
     (B3) are base structure and dominate the error. Compare mechanisms only after the base fits both runs.
  2. M1's driver. B8/B16/B17 show a slow win_rate component whose sign after a pulse depends on whether the pulse
     was throttled (cap 20) or not (cap 100). Spend density (the current m1 driver) predicts the wrong sign in places.
  3. M2 vs base depletion. Both deplete the pool, and P5 (B13) says the memory is strong. Separate the exposure
     (impressions) driver from the commitment (purchases) driver: impressions per purchase differ between bid 5
     and bid 1.5.
  4. M3. P5 and the short P6 show no positive-priming signature; the R1 pair fits use m3 only as a static
     broad-exposure penalty (a_m3 pinned at 1, g3 ≈ −5). M3 is probably the absent mechanism, but this is not
     established.
  5. Pinned parameters in the R1 pair fits: a_m2 → 1 (m12); a_m3 → 1 and g3 ≈ −5 (m13, m23). Base fits hit
     max_nfev (400–500), so they are not converged.
  6. Breadth extremes (0.1, 1.0) were each held only 15–30 ticks.
