# Reservoir review (Phase B reviewer)

Reviewer: separate agent, 2026-09-27. Zero steps spent. CAP 1,000, spent 950, **reserve 50**.
Scripts, logs and plots are in `toronto26-participant-kit/fits/reservoir/review/`:
`look.py` (segment table and mass balance), `season.py`/`season.log` (period fit), `exch.py`/`exch.log` (level
exchange and groundwater excess per 10 ticks), `evalplot.py` → `err_m13_all.png`, `err_m12_all.png` (fit errors),
`longrun.py`/`longrun.log` (4,000-tick stability), `probe.py`/`probe.log` (reserve-probe predictions),
`m13_all.json`, `m12_all.json` (quick R1+R2 refits: 1 restart, `ks,af,gf` fixed, init from the R1 fits).

Score σ = 0.1·std (level 20.2, inflow 0.157, outflow 0.45, quality 0.00102). Noise σ: level 4.4, inflow 0.075,
outflow ≤ 0.05, quality 0.0055.

## 1. Independent behaviour list (written from the raw data and plots, before reading the plan)

| ID | Behaviour | Evidence |
|---|---|---|
| R1 | Level is a stock with a hard spill cap ≈ 941. At the cap, outflow = request + spill ≈ inflow − 1.1 | R1 plot; `look.py` |
| R2 | Inflow is a clean sinusoid tied to time since reset, mean 11.280, amplitude 2.2527, zero phase at t = 0, period **67.7547 ± 0.004** (phase fixed at 0; 67.7582 ± 0.0076 with a free cosine term). R1 alone gives 67.770 and R2 alone 67.736. The per-cycle mean and amplitude are flat within ±0.01 over 8 cycles, with no slow modulation | `season.log` |
| R3 | Delivered outflow = min(request, capacity(V)); capacity falls with level (≈ 16.5 at 940, 12.2 at 380), with or without aeration | R1 470–530, R2 40–280, 340–370 |
| R4 | Unexplained exchange E = ΔL − (I − O): ≈ −2.0 while the level rises fast, −1.1 at the cap, −0.5 at V ≈ 320–500 | `exch.log` |
| R5 | Inflow excess over the season appears only at low, falling levels. It starts late and at a history-dependent level: R1 at V ≈ 770 after 39 ticks of drain (after 470 ticks full), R2 at V ≈ 630 after 60 ticks (after 40 ticks full). It **persists at 0.25–0.55 through flat low-level stretches (R2 140–280, 180 ticks, no decay trend)** and stops within ≈ 4 ticks when the level rises fast | `exch.log` gw column |
| R6 | Quality reset transient: the first reading is ≈ the initial reading + 0.04, then it rises to ≈ 0.95 in ≈ 10 ticks | first 12 ticks of both runs |
| R7 | R1 quality steps down ≈ 0.005 during the irrigation hold (0.950 → 0.945 from t ≈ 140) and does not recover under full recovery (200–300: 0.941–0.946) | 10-tick means |
| R8 | With aeration off, quality falls ≈ 0.02–0.03 over ≈ 80 ticks and settles near 0.925 when deep. Deep withdrawal steepens the fall | R1 300–410, R2 40–240 |
| R9 | **The end level of recovery after anoxia depends on history.** R1 (aeration on at 410 while *deep*, level full): a fast rise to 0.933, then a **plateau at 0.930–0.937 for 140 ticks** that never returns to 0.946, even after depth returns to shallow at 450. R2 (aeration on at 240 while *shallow*, level drawn to 320 then refilled): a ≈ 15-tick delay, then a **full recovery to 0.947** | 10-tick means |
| R10 | A second short pulse lowers quality faster than the first 30 ticks of the long pulse | R2 340–369 vs 40–69 |
| R11 | The first two R1 inflow readings sit +0.68 and +0.40 above the season, while R2's do not | `season.log` |
| R12 | Outflow noise scales with the flow (0.004 at 2, 0.05 at 12) | — |

## 2. Comparison with the catalogue (v2) and the current fits

The fits used for this table are the R1+R2 refits of m13 and m12. The error plots are `err_m13_all.png` and
`err_m12_all.png`: red is a 9-tick moving average of pred − obs, and the band is ±score σ.

| Behaviour | Catalogue | Component | Captured? (evidence) |
|---|---|---|---|
| R1 spill cap | B1 | base Vs, ks | **yes.** Level error stays within ±10 (< σ) |
| R2 season | B2 | base c_in, A_s, A_c, P | **partly.** The rollout fits bias it: A_s is 2.18 (m13) or 2.17 (m12) against 2.2527 ± 0.0035 from the direct fit, P is 67.769 (m13) against 67.7547 ± 0.004, and A_c is nonzero → G2 |
| R3 capacity | B4 | qmax, beta | **yes.** Outflow error is within ±0.2, apart from switch transients. The fouling term is unused (af → 0) |
| R4 exchange | B5 | e0, e1, m1 seepage | **net yes, split wrong.** At a sustained low level the model loses 0.17/tick against ≈ 0.55 in the data, and it offsets that with too little groundwater excess → G1 |
| R5 groundwater excess | B6 | m1 (lagging head H, th1) | **no.** th1 fits negative (−10 or −0.5), so the threshold is not supported. Inflow error is −0.2 to −0.4 over R2 150–280 (the model's excess decays while the data's persists), and +0.3 at R1 185–205 (the model predicts an excess where none was seen). Over a 4,000-tick sustained pulse the model's excess falls to 0.01–0.1 (`longrun.log`) → G1 |
| R6 reset transient | B7 | lam_q·z | **roughly.** The model overshoots by ≈ +0.007 around t = 5–10 in R1 (and predicts 0.96 at t = 10 under a pulse, `probe.log`) → G7 |
| R7 quality step at irrigation | B8 (read as "slow drift") | m12: g2q; m13: none | **open.** This may be the M2 contaminant return that the theses tested only through inflow → G4 |
| R8 anoxia decline | B9, B10 | wqa, wqx, m3 | **mostly.** Errors are within ±0.005 in R2 40–240 |
| R9 history-dependent recovery level | not in the catalogue (P9a/P9b read as "no effect") | none | **no.** m13 errors are +0.010 to +0.013 in R1 380–550 and −0.008 in R2 290–340. No parameter set can match both runs → G3 |
| R10 faster second drop | B11 | m3 (partly) | small. Model error +0.006 in R2 350–365 |
| R11 early inflow readings | B11 (v1) | none | not captured. Low impact (2 ticks) |
| R12 flow-scaled noise | noise note | NOISE | irrelevant to scoring |
| — | B13 sustained-pulse level | base + m1 | **model equilibrium ≈ 290–295** (both pairs, `longrun.log`). Its reliability depends on G1 |

## 3. Probes, P9 and coverage (§4.2)

- **Probes run:** P0 in both runs, P1 for all four controls, P3 (release + irrigation), P7 (200 ticks), a P5-like
  second pulse, and the M1/M2 separator (release-only after the drain). All were run and evaluated.
- **M2 vs M3 separation is incomplete.** It rests on the absence of an M2 *inflow* return, but the brief says
  "return water **or contaminants**". The M2 quality signature was never tested as a separator, and R7 hints at it → G4.
- **P9a/P9b were evaluated as "no effect" by looking for a dip or jump inside R1.** Compared across runs, they show a
  **persistent −0.013 offset** after aeration was switched on while deep (R1) that did not appear when it was switched
  on while shallow (R2) → G3.
- **Not run:** P2 (mid levels), P4 (ramp), P6 (explicit order swap), release < 2 (u < 0), mid aeration or depth. For
  water these are linear or capacity-limited, so the risk is low. Mid aeration is a small quality risk (G8).
- **Starts from reset:** both runs began with 40 ticks of recovery. **No data exists on how hidden states behave when
  an episode begins with a non-recovery action.** Every scored episode starts from a reset, so this is untested for
  every episode whose first action is a pulse → G1 and the reserve probe.

## 4. Stability over 4,000 steps

`longrun.log`: recovery, pulse, pulse at u = 0.7, release 12 alone, release 10 alone, and alternating 200/200. All
stay finite and bounded (level 265–942, inflow 11.3, quality 0.92–0.95).

Parameters at their limits:
- `af` sits at 0, so fouling is unused. Drop it.
- `ks` is fixed at 0.99. That is fine.
- `th1` is negative, so the threshold is unused.
- In m12, `th2` is 0.977 (near its cap) and `g2` is −0.06, so the M2 inflow return is unused.

The level has two operating regimes. Under a sustained request above ≈ 10.2 it settles near 290. Below that it sits at
the cap. The knife edge falls between release 10 and 12, and there the forecast depends on the loss and groundwater terms.

## 5. Gaps

**G1 (high). Groundwater excess at a sustained low level, and its reset convention.**
- *Evidence.* The data's excess persists at 0.25–0.55 over R2 140–280. The model decays it toward 0 because H catches
  up with V. At the equilibrium near 290 the model gives an excess of 0.01–0.1 and a loss of 0.17. The data suggest
  an excess of ≈ 0.4 and a loss of ≈ 0.55. The net is similar, so the level is roughly right, but the inflow is
  ≈ 0.3–0.4 low (≈ 2σ, an inflow score of ≈ 0.3 instead of ≈ 0.9) for every tick of every sustained-pulse episode.
  The onset rule (39 vs 60 ticks, V 770 vs 630) is not reproduced, and H0 = initial level is an untested guess.
- *Fix.* Model the excess as G = g·max(Href − V, 0) with a *fixed or slowly charged* reference head Href, plus a fast
  shut-off driven by the rising level (for example a factor (1 − c·max(ΔV, 0))), and keep a separate level-dependent
  loss. Fit Href's charging rate from R1 (long full period, early onset) against R2 (short full period, late onset).
- *Test.* The reserve probe below.

**G2 (high, free to fix). Season parameters.**
- *Evidence.* The direct fit (phase fixed at 0) gives c = 11.2801, A = 2.2527, P = 67.7547 ± 0.004. A rollout fit
  gives P = 67.769 and A_s = 2.18, because level misfit pulls on the season. That costs 0.07 in amplitude and about
  0.8 ticks of phase at t = 4,000, roughly 0.1 of inflow error late in an episode.
- *Fix.* Fix c_in, A_s and P at the direct-fit values, and fix A_c = B_s = B_c = 0.
- *Answer to "is the period pinned?"* Yes. With the phase fixed, one standard error of P is ≈ 0.24 ticks of phase at
  t = 4,000 (≤ 0.05 of inflow). P = 67.75 lies within 1.2 standard errors. A 50-step probe cannot improve this
  (a fresh run has no long baseline).

**G3 (high for quality). The recovery level after anoxia depends on history (deep + aeration, or turnover).**
- *Evidence.* R9, the P9a/P9b re-reading in §3, and the m13 errors (+0.01 in R1 410–550, −0.008 in R2 290–340).
  Quality is a quarter of the score and σ = 0.001, so a 0.013 offset held for hundreds of ticks is costly.
- *Fix (candidate drivers).*
  - (a) A bottom pool built during anoxia is **remobilized into the whole column when aeration comes on while deep**,
    as the brief puts it: "aeration can … remobilize deeper material", "a deep release can change later surface
    quality".
  - (b) A volume-weighted contaminant concentration that only **flushing or turnover (outflow/V, refill with river
    water)** removes. R2 drained to 320 and refilled; R1 stayed full.
  - Fit both on R1+R2. (a) predicts that R1-style recovery does not depend on the level. (b) predicts that it does.

**G4 (medium). M2 was rejected on its inflow signature only.**
- *Evidence.* R1 quality falls 0.005 from the start of irrigation (t ≈ 140) and stays down.
- *Fix.* Refit m12 with only the quality branch (g2q; g2 = 0) against m13, using ≥ 3 restarts. Pair choice should
  also consider the G3 structure, because M3 is the natural home for (a).

**G5 (medium). The pair fits are not decision-grade.**
- *Evidence.* The R1+R2 refits stopped at nfev 32 and 70 (tolerance reached from the R1 start point). Costs are 3,495
  (m13) and 3,547 (m12), a near tie. th1 < 0, th2 is near its cap, and g2 < 0.
- *Fix.* Apply G2 and drop fouling first, then run 3 restarts with perturbation and a 100 → 300 → full curriculum. Do
  not judge pairs before G1 and G3 are addressed (§2 lesson 6: a near tie means missing structure).

**G6 (medium, evaluation). Local scores against noisy observations have a ceiling.**
- *Evidence.* A perfect model scores 0.86 on level, 0.75 on inflow, 0.95 on outflow and **0.29 on quality** against
  the noisy data. The "quality ≈ 0.08" figure is partly this ceiling and partly the R1-only fits' 0.02 errors. The
  R1+R2 refits have smoothed |err| of 0.0033–0.0041.
- *Fix.* Report a noiseless proxy (score against a 9-tick moving average inside holds, or error of the smoothed
  residual) when comparing models.

**G7 (low). Quality reset transient.**
- *Evidence.* The model overshoots (+0.007 at t ≈ 5–10). Its predicted 0.96 at t = 10 under a pulse start is
  untested.
- *Fix.* Start q from a smoothed initial estimate and use a first-order rise without overshoot. The reserve probe
  also tests this.

**G8 (low). Untested inputs.** Mid aeration or depth, release < 2, ramps and order swaps. Water behaviour is
structurally safe. Quality interpolation in aeration is assumed linear.

**G9 (low). Inflow readings at R1 t = 1–2 (+0.68, +0.40).** Ignore.

## 6. Reserve spending: recommended (50 steps, one probe)

G1 justifies the reserve. It is the largest scoring risk that data can still settle. It covers inflow, and through
the net balance the level, in every sustained-pulse or pulse-start episode. It also tests the reset convention for
every hidden state under a non-recovery start, which neither run covered.

**Schedule:** a fresh reset (free), then **50 steps of the reference pulse**
`{"release_rate": 12.0, "irrigation_allocation": 8.0, "withdrawal_depth": 1.0, "aeration": 0.0}` from tick 0, with
no recovery prefix. Run it as a new run (for example `R3`) with the usual save-every-step script, in chunks of 25
with a budget check before each.

**Predictions** (`probe.log`; the two pairs agree):

| Initial level | Level at t = 50 | Excess, t 1–10 | Excess, t 11–25 | Excess, t 26–50 | Outflow | Quality at t = 10 | Quality at t = 50 |
|---:|---:|---:|---:|---:|---|---:|---:|
| 400 | ≈ 357 | 0.02 | 0.02 | 0.07 | C(V), ≈ 12.4 → 12.0 | ≈ 0.96 | ≈ 0.94 |
| 500 | ≈ 415 | 0.03 | 0.05 | 0.11 | C(V), ≈ 13.4 → 12.6 | ≈ 0.96 | ≈ 0.94 |
| 600 | ≈ 476 | 0.04 | 0.07 | 0.15 | C(V), ≈ 14.2 → 13.2 | ≈ 0.96 | ≈ 0.94 |

**How to read the outcome** (inflow noise 0.075, so a 10-tick mean resolves about 0.05):
- **Excess ≥ 0.25 within ≈ 20 ticks:** a fixed regional head (Href ≈ 650–800). The excess persists indefinitely at
  low levels. Use G = g·max(Href − V, 0) with a constant Href, and refit the loss.
- **Excess ≈ 0 for all 50 ticks:** the bank is charged by time spent at a high level (slow Href starting low at
  reset). The sustained-pulse excess is then bounded by that charge.
- **A small growing excess, as predicted:** the current lagging-head structure is adequate at reset, and only the
  late persistence (G1) needs a slower H.
- **Also read off:** capacity at levels 350–600 from reset (checks that fouling really is zero at reset), the quality
  reset transient under anoxia (G7), and the early anoxic decline from the reference profile (G3's pool starting value).
