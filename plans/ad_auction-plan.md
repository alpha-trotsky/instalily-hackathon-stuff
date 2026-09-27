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
