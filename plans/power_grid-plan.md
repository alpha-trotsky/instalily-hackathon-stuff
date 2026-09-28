# Power grid plan: pre-registration, runs, behaviour catalogue

Phase A researcher, started 2026-09-27 01:45 (overnight job, `plans/overnight-framework.md`). CAP = 1,000 steps
(Run 1 ≤ 550, Run 2 ≤ 400, reserve ≥ 50). Budget at start: 2,000 remaining (free read). No earlier plan or data.

Paths below: data/fits/greybox are under `toronto26-participant-kit/`.

## 1. Dossier (§3.1) — written before any step was spent

**Brief (quoted, abridged only by paragraph):** "Grid load in power units, frequency in Hz, and renewable share of
delivered generation. Price signal reduces desired demand; reserve dispatch requests additional supply in power
units. A tick is one dispatch interval. / Supply requests can be limited by available physical resources. Reserve
resources differ in power, duration and thermal response, and share a charging connection. Dispatch allocates supply
according to operating cost and system conditions. / Flexible cooling loads have different thermal response times.
Price shifts their thermostat settings: each load warms while off, cools while on, and switches at separate upper and
lower temperature limits. Aggregate consumption depends on the distribution of temperatures and which loads are
already running. / A price pulse can synchronize some loads and cause a later rebound; thermal heterogeneity
disperses that synchronization. Every reset starts with the same asynchronous population at reference price 0.8,
without random hidden phases. Charging allowance limits grid power available for refilling reserves. / Interconnector
setting opens remote delivery capacity, whose temperature depends on recent flows. Renewables can be curtailed at
that connection. Conventional governors respond to frequency with finite response times and output limits."

**Observables** (docs initial-reading ranges):

| Observable | Initial range | Notes |
|---|---|---|
| load | 90 – 120 | power units; demand actually served (price-responsive, cooling loads, possibly reserve charging) |
| frequency | 49.8 – 50.2 | Hz; set by supply–demand imbalance, restored by governors (finite response, output limits) |
| renewable_share | 0.2 – 0.4 | fraction of delivered generation; curtailed at the interconnector; diluted by reserve supply |

**Controls** (u = (value − recovery)/(pulse − recovery)):

| Control | Bounds | Recovery | Pulse | u | Range of u | Notes |
|---|---|---:|---:|---|---|---|
| price_signal | [0, 2] | 1.5 | 0.0 | (1.5 − p)/1.5 | [−0.33, 1] | **recovery not at a bound**: 1.5–2.0 (u < 0) is the untested side. Pulse = price 0 = *highest* demand. Reset reference price is 0.8 (u = 0.47), so recovery (1.5) is itself a price step from the reset reference → reset transient in load |
| reserve_dispatch | [0, 150] | 0 | 150 | r/150 | [0, 1] | requested extra supply in power units; "can be limited by available physical resources" |
| charging_allowance | [0, 1] | 1 | 0 | 1 − c | [0, 1] | pulse = no recharging of reserves |
| interconnector | [0, 1] | 1 | 0.2 | (1 − x)/0.8 | [0, 1.25] | **pulse (0.2) is not at a bound**: 0–0.2 (u 1–1.25) untested. Recovery = fully open |

**Structure from the brief (base model, not mechanisms):**
- Demand: desired demand falls with price. Cooling loads are a thermostat population whose setpoints shift with
  price; aggregate consumption depends on the temperature distribution → load responds with a lag (thermal
  response times) and possibly overshoot.
- Supply: conventional (governors: frequency droop with finite response time and output limits → frequency returns
  toward 50 after an imbalance, but possibly not fully when a governor saturates), renewables (share of delivered
  generation, curtailed at the interconnector), remote delivery through the interconnector, reserves (dispatch
  request, limited by available resources: power, duration = energy, thermal response = ramp).
- Frequency: imbalance (supply − demand) → frequency deviation; governors close the gap → expect a spike then
  decay back toward ~50 after any step in load or supply. Frequency is probably rate-like (responds to changes).
- **Delay / commitment phrases → lag stages:** "finite response times" (governors), "thermal response" (reserves,
  cooling loads), "temperature depends on recent flows" (interconnector). No explicit pipeline/commitment phrase.
- **Time since reset:** "Every reset starts with the same asynchronous population at reference price 0.8" → the
  cooling population starts desynchronized at setpoints for price 0.8; the first action (recovery 1.5) is a price
  step → a deterministic reset transient (possibly a synchronized dip then rebound). No seasonality phrase.
- **Organizer-suggested comparisons (P9):** the brief has no explicit "compare …" sentence. Implied: "A price pulse
  can synchronize some loads and cause a later rebound" → P9a price pulse vs price ramp (synchronization);
  "Charging allowance limits grid power available for refilling reserves" → P9b recovery after a dispatch pulse with
  charging on vs off; "temperature depends on recent flows" → P9c interconnector reopened after a short vs long
  closure.

## 2. The three mechanisms (§3.2)

The brief has no single sentence listing three parallel processes. It describes three hidden-state processes with
memory, one per paragraph, each tied to one control; governors and price-demand are ordinary dynamics (base).
Confidence moderate (~65%) that these are the intended three:

- **M1 thermostatic synchronization / rebound** (cooling loads): "A price pulse can synchronize some loads and cause
  a later rebound; thermal heterogeneity disperses that synchronization."
- **M2 reserve energy depletion / recharge**: "Reserve resources differ in power, duration and thermal response, and
  share a charging connection … Charging allowance limits grid power available for refilling reserves."
- **M3 interconnector heating / curtailment**: "Interconnector setting opens remote delivery capacity, whose
  temperature depends on recent flows. Renewables can be curtailed at that connection."

Alternative reading (lower confidence): the three reserve attributes "power, duration and thermal response". If the
data show several reserve timescales but no load rebound or line heating, revisit.

## 3. Theses (§3.3)

### M1 thermostatic synchronization

| Field | Content |
|---|---|
| Quote | "A price pulse can synchronize some loads and cause a later rebound; thermal heterogeneity disperses that synchronization." |
| Hidden state | S: synchronized fraction of cooling loads (phase coherence) + a load "debt" (loads that were forced on/off will switch back together) |
| **Driver** | **rate of change of price** (a price step moves many setpoints at once); a ramp moves them gradually |
| **What it changes** | load directly: rebound of opposite sign after the initial response, damped oscillation (ringing) |
| Timescales | rebound after one thermal cycle (~10–50 ticks?); dispersion over a few cycles |
| P0 | present: reset transient (0.8 → 1.5 price step) shows a load dip then overshoot/ringing; absent: monotone relaxation |
| P1 price on (1.5 → 0) | present: load spikes up then **rebounds below** the new level, ringing; absent: first-order rise |
| P1 price off | present: load dips then **rebounds above**; absent: first-order fall |
| P1 reserve / charging / interconnector | nothing on load |
| P4 step vs ramp (price) | present: step rings, ramp does not; absent: same end level, no difference beyond lag |
| P5 two price pulses short vs long gap | present: second pulse response depends on phase (short gap: interferes with the rebound) |
| P6 order swap | small |
| P7 long hold | load settles to a constant once desynchronized |

### M2 reserve depletion / recharge

| Field | Content |
|---|---|
| Quote | "Reserve resources differ in power, duration and thermal response, and share a charging connection"; "Charging allowance limits grid power available for refilling reserves"; "Supply requests can be limited by available physical resources" |
| Hidden state | E: stored reserve energy (state of charge, 1 at reset); possibly a thermal state of reserve units |
| **Driver** | accumulated reserve dispatch (energy delivered); refill rate ∝ charging_allowance × (1 − E) |
| **What it changes** | delivered reserve supply (∝ min(request, available power(E))) → frequency and renewable share; possibly load (recharging draws grid power) |
| Timescales | depletion over "duration" (tens–hundreds of ticks at 150); refill over tens–hundreds of ticks |
| P1 reserve on (hold) | present: frequency/renewable-share effect of dispatch **fades during the hold** (energy runs out, staged if resources differ in duration); absent: sustained effect |
| P1 reserve off | present: with charging 1, load rises while reserves recharge (if charging counts as load), frequency dips; absent: mirror of on |
| P1 charging off (alone, reserves full) | nothing |
| P5 two dispatch pulses short vs long gap | present: **2nd weaker after a short gap** (and weaker still with charging 0); absent: equal |
| P9b recovery with charging on vs off | present: next dispatch after charging-off recovery is weak; absent: no difference |
| P7 long dispatch hold | slow fade of delivered reserve |

### M3 interconnector heating / curtailment

| Field | Content |
|---|---|
| Quote | "Interconnector setting opens remote delivery capacity, whose temperature depends on recent flows. Renewables can be curtailed at that connection." |
| Hidden state | H: line temperature (fading memory of flow through the interconnector) |
| **Driver** | flow through the interconnector (∝ opening × remote delivery); recent flows heat, low flow cools |
| **What it changes** | available remote capacity (derated when hot) → renewable curtailment → renewable_share (and supply → frequency) |
| Timescales | heating/cooling over tens–hundreds of ticks |
| P0 (interconnector 1) | present: renewable_share **drifts down slowly** as the line heats from reset; absent: flat after the transient |
| P1 interconnector 0.2 (close) | present: share drops, then partly recovers as the line cools (or stays); absent: a step to a new level |
| P1 interconnector reopen | present: share jumps **above** the old level (line cool), then **decays** as it reheats (asymmetric vs close); absent: mirror image |
| P5/P9c reopen after short vs long closure | present: higher initial share after a long closure; absent: equal |
| P7 long hold open | slow drift of share |

## 4. Separation table (§3.4)

| Probe | M1 thermostat | M2 reserve energy | M3 line heat |
|---|---|---|---|
| P0 reset transient | load dip/overshoot (0.8→1.5 price) | nothing | slow share drift |
| P1 price on/off | **load ringing / rebound** | nothing | nothing |
| P1 reserve on (long hold) | nothing | **effect fades during hold** | small (via flows) |
| P1 reserve off | nothing | recharge load / frequency dip | nothing |
| P1 interconnector close/reopen | nothing | nothing | **asymmetric: reopen overshoot then decay** |
| P4 price step vs ramp | **step rings, ramp doesn't** | nothing | nothing |
| P5 dispatch pulses short vs long gap | nothing | **2nd weaker after short gap** | nothing |
| P9b charging on vs off after dispatch | nothing | **next dispatch weaker if charging off** | nothing |
| P9c interconnector reopen after short vs long closure | nothing | nothing | **higher share after long closure** |
| All-controls pulse and release | ring on release | reserve effect fades; recharge after | share recovers with heat lag |

Pairs:
- **M1 vs M2:** P4 price step vs ramp (M1 only) vs P5 dispatch gap test (M2 only).
- **M1 vs M3:** P1 price on/off ringing (M1) vs interconnector reopen asymmetry / P9c (M3).
- **M2 vs M3:** long dispatch hold fade + P5 (M2) vs interconnector reopen overshoot (M3): different controls, one
  predicts an effect where the other predicts nothing.

## 5. Spend log

| Local time | Run | Ticks (0-based obs idx) | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-27 01:45 (start) | — | — | 0 | 2,000 |
| 2026-09-27 01:45 | R1 | 0–39 (P0 recovery) | 40 | 1960 |
| 2026-09-27 01:45 | R1 | 40–59 (P0 ext) | 20 | 1940 |
| 2026-09-27 01:45 | R1 | 60–79 (P0 ext) | 20 | 1920 |
| 2026-09-27 01:46 | R1 | 80–99 (P0 ext) | 20 | 1900 |
| 2026-09-27 01:46 | R1 | 100–119 (P0 ext; stopped at the 120 cap, load still ringing) | 20 | 1880 |
| 2026-09-27 01:46 | R1 | 120–159 (P1 price 0 on) | 40 | 1840 |
| 2026-09-27 01:46 | R1 | 160–184 (price on, ext) | 25 | 1815 |
| 2026-09-27 01:47 | R1 | 185–209 (price on, ext) | 25 | 1790 |
| 2026-09-27 01:47 | R1 | 210–249 (P1 price off = recovery) | 40 | 1750 |
| 2026-09-27 01:47 | R1 | 250–279 (price off, ext) | 30 | 1720 |
| 2026-09-27 01:47 | R1 | 280–319 (P1 reserve 150 on) | 40 | 1680 |
| 2026-09-27 01:47 | R1 | 320–349 (reserve on, ext) | 30 | 1650 |
| 2026-09-27 01:48 | R1 | 350–389 (P1 reserve off) | 40 | 1610 |
| 2026-09-27 01:48 | R1 | 390–429 (P1 interconnector 0.2) | 40 | 1570 |
| 2026-09-27 01:48 | R1 | 430–469 (P1 interconnector reopen 1.0) | 40 | 1530 |
| 2026-09-27 01:48 | R1 | 470–499 (recovery ext) | 30 | 1500 |
| 2026-09-27 01:49 | R1 | 500–524 (P1 charging 0) | 25 | 1475 |
| 2026-09-27 01:49 | R1 | 525–549 (charging back to 1). **R1 complete: 550 steps** | 25 | 1450 |
| 2026-09-27 01:55 | R2 | 0–39 (P0 recovery, fresh reset) | 40 | 1410 |
| 2026-09-27 01:56 | R2 | 40–89 (interconnector 0) | 50 | 1360 |
| 2026-09-27 01:56 | R2 | 90–129 (reopen, recovery) | 40 | 1320 |
| 2026-09-27 01:56 | R2 | 130–169 (price 0.75, P2) | 40 | 1280 |
| 2026-09-27 01:56 | R2 | 170–219 (all-controls pulse) | 50 | 1230 |
| 2026-09-27 01:57 | R2 | 220–269 (all-controls pulse, ext) | 50 | 1180 |
| 2026-09-27 01:57 | R2 | 270–319 (all-controls pulse, ext) | 50 | 1130 |
| 2026-09-27 01:57 | R2 | 320–369 (release to recovery) | 50 | 1080 |
| 2026-09-27 01:58 | R2 | 370–399 (reserve 150 re-pulse, charging 1). **R2 complete: 400 steps** | 30 | 1050 |

| 2026-09-27 02:22 | R2c (copy of R2, `--continue`) | 400–404 (reserve 150, charging 0, price 1.5, ic 1; continuity check: share 0.075, f 51.79 ✓) | 5 | 1045 |
| 2026-09-27 02:22 | R2c | 405–449 (same action; Phase C G1 charging A/B). **Total spent 1,000 = CAP** | 45 | 1000 |

Spend summary: R1 = 550 steps (cap 550). Budget remaining 1,450 (spent 550 of CAP 1,000).
Spend summary after R2: R1 550 + R2 400 = **950 of CAP 1,000**; budget remaining **1,050**; Phase C reserve **50**.

## 6. Run 1 observations (`data/power_grid/R1.json`, 550 ticks, initial reading load 115.4, f 49.95, share 0.350)

Schedule: recovery 0–119 | price 0 120–209 | recovery 210–279 | reserve 150 280–349 | recovery 350–389 |
interconnector 0.2 390–429 | recovery 430–499 | charging 0 500–524 | recovery 525–549. Plot
`data/power_grid/R1_r0_battery.png`, battery `data/power_grid/R1_battery.json`.

Noise σ (second differences, flat stretches): load ≈ 0.09, frequency ≈ 0.02, share ≈ 0.0004 (very small).

- **Reset transient (price 0.8 → 1.5 at tick 0):** load jumps 115.4 → 100.6 on the first tick, keeps falling to 72.2
  at tick 14, then **overshoots** to 105.5 (tick 45), dips to 89.6 (tick 100), rises again (94 at tick 119): a
  lightly damped oscillation with period ≈ 80–90 ticks. Not settled at 120 (accepted, cap).
- **Price 0 on (tick 120):** instant jump 94 → 141 (+47), rises to 169 (tick 134), then **rebounds** far below the
  new level (100 at tick 166), peak 125.8 (184), trough 116.7 (197), rising at 209. The settled level at price 0 is
  ≈ 120 (+25 vs ≈ 95 at price 1.5). Strong M1 signature (synchronised loads, rebound).
- **Price off (tick 210):** instant drop 124 → 99, trough 64 (tick 228, −30 below settle), peak 114 (276),
  trough 79 (313), peak 113 (342): the ringing persists for > 130 ticks with little damping, period ≈ 65–85.
  After ≈ tick 360 the amplitude is small (±5).
- **Frequency** mirrors load (f ≈ 50 − 0.03·(L − L_ref) + supply terms), with partial restoration (droop): at
  price 1.5 settled load ≈ 95 → f ≈ 50.2–50.4; at price 0, load 120 → f ≈ 49.4. Hard **upper clip at ≈ 52.03**
  during reserve 150 (flat 52.0 while load swings 113 → 79). Minimum seen 48.37.
- **Reserve 150 (tick 280):** renewable share collapses 0.34 → 0.06 in 1 tick (curtailed: dispatch replaces
  renewables), then creeps to 0.073 in 20 ticks and stays; frequency pinned at 52 (surplus), declining to 51.5 only
  as load rises. **No visible depletion in 70 ticks at 150** (but frequency is clipped, so fading supply would be
  hidden unless it reached the share).
- **Reserve off (tick 350):** share **overshoots to 0.505** and decays to 0.39 over ≈ 15 ticks; frequency **dips to
  49.15** then recovers over ≈ 30 ticks. Consistent with governors having backed down during the surplus (finite
  response time) → temporary shortfall → renewables fill a larger share. Could also be M3 (line cooled while
  renewables were curtailed). Separate with a reserve pulse at interconnector 0.2 or with the P9c test.
- **Interconnector 0.2 (tick 390):** share drops at once 0.39 → 0.22, then drifts slowly down to 0.21; frequency
  drops to ≈ 49.4–49.6 and stays (less supply). Load unaffected.
- **Interconnector reopen (tick 430):** share jumps to 0.376 (no overshoot), creeps to a plateau 0.388, then
  **falls** 0.388 → 0.343 (ticks 457–478) at constant load, rises again to 0.382 (tick 498): a slow share
  oscillation (period ≈ 50–60) not explained by load. Candidate: M3 line heating with curtailment when hot
  (or dispatch hysteresis). The P0 share also plateaus at 0.379–0.39 (ticks 77–102, 380–389, 446–456): a **cap on
  the renewable share ≈ 0.38–0.39** (curtailment for system conditions).
- **Charging 0 (tick 500, reserves not recently used for 150 ticks):** no clear effect on load or frequency
  (load +3 over 25 ticks is the ongoing drift). Share held flat at 0.378 during charging 0, and began falling 4 ticks
  after charging returned to 1 (0.376 → 0.336). Possibly coincidence with the share oscillation; untested.

**Settled levels (approximate):**

| Setting | load | frequency | share |
|---|---:|---:|---:|
| recovery (1.5, 0, 1, 1) | ≈ 94–96 (ringing ±5) | ≈ 50.1–50.4 | 0.34–0.39 (oscillating) |
| price 0 | ≈ 120 | ≈ 49.4 | ≈ 0.32–0.34 |
| reserve 150 | load unaffected | 52.0 (clipped) | 0.073 |
| interconnector 0.2 | unaffected | ≈ 49.4 | 0.21 |
| charging 0 | unaffected | unaffected | ≈ 0.378 |

## 7. Model v0 and Run-1 pair fits

Model module `toronto26-participant-kit/greybox/power_grid_model.py` (written from the theses before fitting; see
its docstring). Base: price-dependent load level with instant + slow part, reserve delivery, renewable share relaxing
to a target with a curtailment cap `Smax`, frequency from the supply–load imbalance with a governor (droop, finite
response, output limit) and hard clip [47.97, 52.03]. Reset convention: the price before tick 0 is the reference 0.8
and the slow load state starts at its 0.8 equilibrium. m1 = damped resonator on load driven by the price *step*
(rate of change); m2 = reserve energy E (depletes with delivery, refills ∝ charging_allowance, delivered reserve
fades when E is low, recharging draws load); m3 = interconnector heat H (fading memory of renewable flow S·x,
curtailment when H > h3). Units linear for all three (share is a fraction, load/frequency symmetric enough for
now). Fit residual σ: load 0.5, frequency 0.03, share 0.003 (≈ 5× the noise, to balance the observables).

Run-1 pair fits (2 restarts, `fits/power_grid/m{12,13,23}_r1.json`, plot `fits/power_grid/r1_pairs.png`):

| Pair | Cost | Train score (σ = 0.1×std) | Notes |
|---|---:|---:|---|
| m1+m2 | 14,605 | 0.495 | m2 unused (d2 → 0) |
| m1+m3 | **14,238** | **0.504** | g3 = 0.41 (small; fits a bit of the share oscillation) |
| m2+m3 | 25,730 | 0.449 | cannot ring: load stays first-order; g2L pinned large (misfit sink) |
| persistence | — | 0.215 | |

**Reading:** m1 is required (without it the load ringing is impossible: cost +11,000). m12 vs m13 is a tie: Run 1
contains no probe that exercises either reserve depletion (reserve dispatch was only 70 ticks, with charging on)
or long low interconnector flow. Not captured in v0: the share spike 0.505 after reserve release (clipped by
Smax), the slow share oscillation at recovery, the full depth of the reset dip (72 vs model 78).

## 8. Run 2 design (§4.4)

`fits/power_grid/rank_probes.py` → `fits/power_grid/probe_ranking.json`: each candidate (after a 40-tick P0) is
simulated through the three R1 pairs and through module on/off variants (m12 with a hypothetical M2 of ~150 ticks
of full-dispatch energy; m13 with g3 = 0 / 1.5); mean |difference| in score-σ units over the probe:

| Probe | Cost | m12 vs m13 | m12 vs m23 | M2 hyp on/off | M3 on/off |
|---|---:|---:|---:|---:|---:|
| C1 all-controls pulse 150 + release 60 | 210 | 0.18 | 10.3 | **1.22** | 0.15–0.25 |
| C1s all-controls pulse 60 + release 60 | 120 | 0.26 | 7.3 | 0.01 | 0.25–0.39 |
| C2 reserve 150 + charging 0 100, gap, re-pulse | 190 | 0.22 | 5.8 | 0.02 | 0.22–0.38 |
| C3 interconnector 0 for 60, reopen 50 | 110 | 0.29 | 1.9 | 0.00 | 0.16–0.22 |
| C4 price ramp 1.5→0 over 40, hold, ramp back | 110 | 0.23 | 4.3 | 0.00 | 0.56–1.14 |
| C5 price 0.75 60, back 50 | 110 | 0.22 | 3.9 | 0.00 | 0.72–1.48 |
| C6 reserve 60 for 100, off 40 | 140 | 0.35 | 1.8 | 0.01 | 0.21–0.40 |
| C7 ic 0.2 + reserve pulse at 0.2 | 110 | 0.26 | 2.4 | 0.01 | 0.06–0.08 |
| C8 reserve 150 pulses with a 10-tick gap | 90 | 0.18 | 2.5 | 0.02 | 0.05–0.10 |

Reasons for the choice: the fitted m12 and m13 agree everywhere (≤ 0.35 σ) because neither module was
exercised, so the ranking must lean on the "module on" hypotheses. M2 only becomes visible when stored energy runs
low, i.e. a **long full dispatch with charging off** (C1, the only probe with a clear M2 signal); M3's model
signal is small everywhere, but its thesis signature (overshoot after reopening a line that carried no flow) needs
a **full closure (interconnector 0)**; the R1 closure at 0.2 kept 55% of the flow. m1 vs the rest separates on any
price move and is already established, so the price ramp (C4) is dropped. Chosen (400 steps):

| Segment | Ticks | Steps | Purpose |
|---|---|---:|---|
| P0 recovery | 0–39 | 40 | reset transient replicate with a new initial reading (b_init) |
| interconnector 0 | 40–89 | 50 | M3: line cools with zero flow (u = 1.25, untested side of the pulse) |
| reopen (recovery) | 90–129 | 40 | M3: overshoot above the ≈ 0.39 plateau then decay? (vs R1 reopen after 0.2: none). P9c |
| price 0.75 | 130–169 | 40 | P2 mid level (linearity of the price effect, u = 0.5) |
| **all-controls pulse** (price 0, reserve 150, charging 0, ic 0.2) | 170–319 | 150 | tip 4 joint pulse; P3; M2 depletion with no recharge; long hold (P7-lite) |
| release to recovery | 320–369 | 50 | recovery from a joint pulse: M1 rebound, M2 recharge load draw, M3 reopen after low flow |
| reserve 150 only (charging 1) | 370–399 | 30 | P5/P9b: second dispatch after a short gap; weaker if M2 (energy not yet refilled) |

Not in Run 2 (budget): price ramp P4 (M1 already clear), a 200-tick P7 (the 150-tick joint hold is the longest), a
mid-level reserve. Holds are adapted with the settle check; Phase C reserve = 50.

## 9. Run 2 observations (`data/power_grid/R2.json`, 400 ticks, initial reading load 101.1, f 50.08, share 0.242)

Run as designed (§8), no hold changed. Plot `data/power_grid/R2_r0_battery.png`, battery `R2_battery.json`.

- **Reset replicate:** despite a different initial reading (load 101 vs 115, share 0.24 vs 0.35) the trajectory
  is the same as R1 after ≈ 20 ticks (R1 − R2 load: 12.1 at tick 0, 5.2 at tick 5, 0.5 at tick 20, mean 0.49 over
  ticks 10–39; share differs by ≤ 0.004 from tick 0). The initial load reading decays away at ≈ 17%/tick; the
  renewable share **ignores** its initial reading entirely. Hidden state is the fixed reference (b_init ≈ 0 for
  the slow part; the initial load deviation is a fast transient).
- **Interconnector 0 (tick 40):** share 0.36 → 0.16 at once (0.21 at 0.2, 0.38 at 1: not proportional; ≈ 0.15 of
  local renewables plus remote delivery). Frequency −0.9 Hz, then governors recover +0.4 Hz over 40 ticks.
- **Reopen after full closure (tick 90), the M3 / P9c test:** share → 0.372, plateau 0.379, then declines to 0.336
  as load rises. **No overshoot**, and the share trajectory after reopening is the same as R1's at the same ticks
  without any closure (R1 ticks 77–119). A line that cooled for 50 ticks gave no extra delivery → **evidence
  against M3** (unless a share cap ≈ 0.38–0.39 masks it; but that level was exceeded, to 0.505 in R1 and 0.415 in
  R2).
- **Price 0.75 (P2):** instant +24 (half of the +47 at price 0 → linear), peak +39 at 10 ticks (vs +75), then a
  rebound to 94 at tick 169, below the recovery level, while price is still 0.75. Ringing amplitude roughly linear
  in the step size.
- **All-controls pulse (tick 170, 150 ticks):** load 94 → 145 (peak tick 183) → 114 (210) → 128 (225) → ≈ 122–129
  (settled ≈ 124–125, slightly above R1's price-0 level ≈ 120: charging 0 / reserve may add ≈ +4, or it is the
  0.75 → 0 history). Frequency is **not** clipped here (load high, interconnector 0.2): 49.6–50.5, settling ≈ 50.2.
  Share 0.040 → 0.050, creeping up slowly over the whole 150 ticks. **No sign of reserve depletion** after 150 ticks
  at full dispatch with charging 0 (frequency tracks load only; share never climbs back).
- **Release (tick 320):** load drops to 63 (tick 339) and rebounds to 109 (tick 375): M1 ringing on release.
  Share 0.41, plateau 0.384 while load is very low (63–66), then 0.415 at load 95: the share "cap" is not a
  fixed fraction. Frequency rises (load fell); no shortfall dip this time.
- **Second dispatch after a 50-tick gap (tick 370, P5/P9b):** share 0.092 → 0.063 → 0.074 and frequency 51.95 → 51.78,
  almost identical to R1's first dispatch (share 0.100 → 0.059 → 0.072; linear fit of f on load in the dispatch:
  f at load 100 = 51.80 in R1 vs 51.76 here). **No weaker second pulse** → weak evidence against M2 at the energy
  scale tested.

## 10. Behaviour catalogue v2 (§6.1; v1 after Run 1 is the observation list in §6, merged here)

| ID | Behaviour | Evidence | Candidate explanation | Status |
|---|---|---|---|---|
| B1 | Load rings after every price step: overshoot ≈ 1.6× the settled change, then a rebound below/above the new level, period ≈ 60–90 ticks, weakly damped (> 130 ticks at large amplitude after price off in R1) | R1 ticks 120–350; R2 130–170, 320–400; `R1_r0_battery.png` | **M1** thermostat synchronisation | modeled by m1 resonator (single mode; amplitude after R1 price-off under-predicted) |
| B2 | Instant load jump on a price step (+47 for 1.5 → 0 on the first tick, +24 for 1.5 → 0.75); settled change only +25 | R1 t120, t210; R2 t130 | non-thermostatic demand + synchronised switching | modeled (wLi instant + m1 resonator) |
| B3 | Reset transient: load dips to ≈ 72 at tick 14 and rings; identical in R1 and R2 | both runs 0–120 | M1 driven by the reference-price step 0.8 → 1.5 | modeled (reset price 0.8); depth of the first dip under-predicted (78 vs 72) |
| B4 | Initial load reading fades in ≈ 20 ticks; initial share reading ignored | R1 vs R2 ticks 0–39 | fixed hidden reference state | partly (model starts share at the reading; it should start at the reference) |
| B5 | Price effect linear in u (P2 at u = 0.5 ≈ half of u = 1: instant and peak) | R2 130–170 | base | modeled (linear) |
| B6 | Frequency ≈ 50 − 0.03·(load − ref) + supply terms; partial restoration (droop) | both runs | governor droop, finite response | modeled (governor loop) |
| B7 | Frequency hard clip at ≈ 52.03 (flat while load swings) | R1 283–340, R2 374–378 | frequency / output limits | modeled (fixed clip) |
| B8 | Reserve 150 curtails renewables within 1 tick (share 0.34 → 0.06), then share creeps 0.059 → 0.073 in ≈ 20 ticks; under the joint pulse 0.040 → 0.050 over 150 ticks | R1 280–300, R2 170–320 | dispatch by operating cost; the creep = dispatch settling, or M2 fading reserve, or M3 line cooling | **not captured** in the joint pulse: the additive share target goes to 0 (model 0.0 vs data 0.045) |
| B9 | Share spike after reserve release (0.505 in R1, decays to 0.39 in ≈ 15 ticks) with a frequency dip to 49.15 | R1 350–365 | governors backed down during the surplus (finite ramp) → shortfall; alternatively M3 | not captured (Smax clip) |
| B10 | Share plateau ≈ 0.38–0.39 at recovery, exceeded only after releases | R1 77–102, 380–389, 446–456; R2 96–102 | curtailment for system conditions | modeled as a hard cap Smax (wrong for B9, B11) |
| B11 | Slow share oscillation at recovery (0.34–0.39, period ≈ 50–60) not explained by load alone | R1 430–550, R2 90–130 | lagged 1/load dilution + cap; M3 hysteresis (weak) | open |
| B12 | Interconnector: share 0.38 (x = 1), 0.21 (0.2), 0.16 (0), instant both ways; frequency −0.7 to −0.9 Hz then partial governor recovery | R1 390–470, R2 40–130 | remote delivery capacity | modeled (linear in x; the nonlinear shape is not) |
| B13 | No overshoot on reopening after 50 ticks at x = 0 or 40 ticks at x = 0.2 | R1 430, R2 90 | **M3 absent** (or masked) | evidence |
| B14 | No reserve depletion in 150 ticks of full dispatch with charging 0; a second dispatch after 50 ticks equals the first | R2 170–320, 370–400 vs R1 280–310 | **M2 absent**, or reserve energy ≫ 150 ticks × 150 | evidence |
| B15 | Charging 0 alone (reserves full): no effect | R1 500–525 | M2 idle | consistent with both |
| B16 | Under the joint pulse the load ringing damps within ≈ 60 ticks; settled load ≈ 124–125 (vs ≈ 120 for price 0 alone) | R2 170–320 | smaller price step (0.75 → 0); possibly a charging/reserve load effect | open |
| B17 | Noise σ: load ≈ 0.09, frequency ≈ 0.02, share ≈ 0.0004, not level-dependent | settle output | — | — |

**Mechanism reading after R2.** M1 is certain (B1–B3; every pair without m1 is ≈ 11,000–17,000 cost units
worse). Between M2 and M3 both direct probes came back **null** (B13, B14). Exactly two are active, so one of these
nulls is misleading: either M2 needs a far longer dispatch (energy scale ≫ 150 ticks at 150; under surplus the
dispatcher may deliver much less than 150, so energy drains slowly), or M3's heating only acts above a flow level
not reached (the line cooled at x = 0, but capacity was not the binding limit on reopening). Candidate M3 traces:
the slow share creep during dispatch at x = 0.2 (B8: line cooling → more import) and the recovery share
oscillation (B11). Candidate M2 traces: the same creep (reserve fading, renewables refilling) and the ≈ +4 load
under the joint pulse (B16). The creep is the key ambiguous observation.

**Pair fits on R1 + R2** (2 restarts, `fits/power_grid/m{12,13,23}_all.json`, plot `fits/power_grid/all_pairs.png`):

| Pair | Cost (R1+R2) | Train score | R1-fit → R2 score (σ = 0.1×std; persistence 0.173) | Notes |
|---|---:|---:|---:|---|
| m1+m2 | **30,289** | 0.472 | 0.367 | d2 = 0.006, e2 = 0.97: m2 used to fake the share creep in the joint pulse (B8) |
| m1+m3 | 31,511 | 0.459 | 0.365 | g3 = 0.59 |
| m2+m3 | 47,495 | 0.447 | 0.294 | no ringing; g3 = 31.9 and Smax = 2.1 (absurd) |

The m12 vs m13 margin (1,200) comes from the share misfit in the joint pulse (B8), which is base-model structure,
so it is **not** evidence yet.

## 11. Status / hand-off to reviewer

Files: `plans/power_grid-plan.md` (this), `toronto26-participant-kit/data/power_grid/R1.json` (550 ticks),
`R2.json` (400 ticks), battery JSON/PNGs next to them, `greybox/power_grid_model.py` (v0), `fits/power_grid/`
(`m*_r1.json`, `m*_all.json`, logs, `rank_probes.py`, `probe_ranking.json`, `r1_pairs.png`, `all_pairs.png`).

Spent 950 of CAP 1,000 (R1 550, R2 400); simulator budget remaining 1,050; **Phase C reserve 50**.

Probes run: P0 ×2; P1 for all four controls; P2 price 0.75; P3 via the all-controls joint pulse + release (tip 4);
separating probes for M3 (full closure → reopen, P9c) and M2 (150-tick full dispatch with charging 0, then a second
dispatch after a 50-tick gap, P5/P9b); longest hold 150 (joint pulse). Not run: price ramp (P4/P9a), mid-level
reserve, P6 order swap, a ≥ 200-tick hold.

Open, in priority order for the modeler:
1. **Share structure (B8, B9, B10, B12):** the additive linear share target is wrong. Model delivered renewables and
   total generation explicitly (e.g. share = min(renewables available × capacity(x), headroom) / generation,
   curtailed by reserve surplus; governor lag gives the post-release spike). This misfit currently decides the m12
   vs m13 comparison.
2. **M2 vs M3 is unresolved** (both direct probes null). Re-examine the share creep in the joint pulse and the
   recovery share oscillation once the base share model is right. If the reserve (50) is used, candidates: a long
   mid-level dispatch that keeps frequency unclipped (e.g. reserve 60 with price 0) for M2, or interconnector fully
   open under high renewable flow (low load: price 2.0) for M3 line heating.
3. M1 resonator: one mode fits the first swings but under-predicts the long ringing after price off (R1 210–350) and
   the first reset dip; try two modes or amplitude-dependent damping. Step vs ramp is untested.
4. Initial state: the load reading is a fast transient (≈ 17%/tick) toward the fixed reference; the share reading
   should be ignored (start share from the reference, not the reading).
5. Untested sides: price 1.5–2.0 (u < 0), interconnector 0–0.2 tested only at 0 (share 0.16).

## 12. Phase C: charging test (R2c) and review responses

Phase C modeler (resumed after an API cut-off). Paths under `toronto26-participant-kit/`; fits in `fits/power_grid/v1/`.

### 12.1 Charging A/B during full dispatch (reviewer §6 decision rule)

`data/power_grid/R2c.json` = R2 continued (ticks 400–449: price 1.5, reserve 150, **charging 0**, interconnector 1);
the continuity check passed (share 0.0746, f 51.79 at tick 402 vs 0.0739 / 51.78 at 399). Twin with charging 1:
R2 370–399 (same run, same load phase) and R1 280–349.

| Measure | R2c charging 0 (400–449) | Twin charging 1 | Rule for "M2 active" |
|---|---:|---:|---|
| share ~ a + b·t + c·(L−100): rise over the hold | **−0.0017** (slope −3.5e-5/tick) | R1 300–349: +0.0014; R2 380–399: +0.0002/tick | ≥ +0.004 |
| frequency at L = 100 (linear fit, unclipped ticks) | 51.739 | 51.757 (R2), 51.783 (R1) | > 0.2 Hz below twin |

Frequency is 0.02–0.04 Hz below the twins (≈ 1–2 noise σ) and stayed unclipped (51.66–51.91) the whole hold, so
the reviewer's caveat (fade hidden by the 52 clip or share saturation) does not apply to the frequency channel.
**Verdict: no charging-dependent reserve fade → M2 inactive by the rule; choose m1+m3 by elimination.** This comes
on top of the earlier M2 nulls (B14: 150 ticks of full dispatch with charging 0 in R2, and an equal second dispatch).

### 12.2 Consistency of the resumed state; a fitting bug found

- `greybox/power_grid_model.py` (v1) is consistent: every saved v1 fit re-evaluates to its logged cost except the
  old `m23_all` (fitted before the D2MAX cap was added; refitted).
- **Bug (affects any system):** `core.params_for` applies `fitted` *after* the off-values, so `fit --init X` with X
  from a fit that had other modules active **leaks those modules back in** (their params are held fixed at X's
  values, not switched off). The earlier `v1/m1_all`, `m12_all`, `m12_r1` and the first bootstrap were warm-started
  from m13 and silently kept M3 on (g3 = 1.33) — that is why all pairs tied at 27,017. They are moved to
  `v1/leaky/`. I did not change `core.py` (other agents are running); I sanitized my init files instead
  (`v1/init_*.json`, inactive-module params reset to SPEC/off). **Orchestrator: check other systems' fits made
  with `--init` from a different pair, and consider forcing off-values last in `params_for`.**
- The clean m1-only fit (26,477) beat the leaky m13 (27,017), so m13 was in a poor basin; re-started from the
  m1 fit with a small M3 (g3 0.3, h3 0.36) it reached 26,271 (`m13_all.json`; old one kept as `*_capbasin.json`).

### 12.3 Review responses

| Gap | Response |
|---|---|
| G1 M2 vs M3 | **Fixed by the probe** (§12.1): no fade with charging off → M2 inactive → m1+m3. With the v1 base, M2 is unused in every clean fit anyway (d2 → 1e-9, m12 cost = m1 cost). M3 remains weakly supported (see §13): it is chosen by elimination, not by its own signature. |
| G2 M2 fading to nothing | **Fixed**: `D2MAX = 3.3e-4` caps the fade at ≈ 5% per 150 ticks of full dispatch; the shipped model has M2 off (d2 = 0). |
| G3 load ringing, price-dependent period | **Partly fixed**: resonator stiffness and damping depend on price (`kap = kap1·e^{kk1·up}`, `rho = rho1^{1+kr1·up}`); fitted kk1 = 0.37, kr1 = 0.20 → period ≈ 67 ticks at price 0, 80 at 1.5 (data ≈ 50 / 65–85). Load RMSE over R1 210–350 still 7.2. A thermostat-population model was **not tried** (time). |
| G4 mid-level reserve | **Not captured** (no data within CAP): smooth `1/(1+wSr·Rd)` kept; flagged. |
| G5 onset undershoot / release spike | **Partly fixed**: lagged surplus memory B (`exp(wSB·(B−D))`, kb = 0.32) plus governor coupling `exp(−wSG·G)`. Release spike: model 0.475 at tick 351 vs 0.494 data (was 0.40 capped), but it decays too fast; the post-release frequency dip (49.15) is still missed (model 50.3). |
| G6 governor / secondary loop | **Fixed as structure**: governor with output limit Gm and finite response kg, plus a leaky integral secondary loop Z (clipped ±Zm). kz pinned at 1.0 and kg ≈ 1.0 (instant): the loop wants to be faster than the parameterization allows — base-structure misfit, not a mechanism. |
| G7 coverage (P3, P4, P6, P7, price > 1.5) | **Not captured** (budget spent); price > 1.5 extrapolates linearly (load ≈ 84 at price 2). |
| G8 initial load reading | **Fixed**: `(L0 − Lref0)·qi^(t+1)`, fitted qi = 0.94, Lref0 = 118. |
| G9 P9b blind to fast recharge | Noted; the R2c probe (charging 0) covers it and was null. |
| G10 optimizer noise | Addressed by warm cross-starts (m13 from m1's basin, m1/m12 from m13's base); the m13 − m1 gap (≈ 200) is below the reviewer's ±500 optimizer-noise estimate. |

## 13. Model selection record (v1 model, σ_fit load 0.5 / f 0.03 / share 0.003)

**Cross-run test (§6.3.1)**: fit on R1 only, predict R2c (450 ticks), score σ = 0.1×std after tick 20 (R1+R2c).

| Pair | R1 cost | R2c score | load / f / share | Notes |
|---|---:|---:|---|---|
| m1 only (fallback) | 13,635 | **0.4406** | — | relaxation + m1; no hidden-reserve/line state |
| m1+m2 | 13,635 | 0.4406 | — | d2 → 1e-9: identical to m1 |
| m1+m3 | **13,418** | 0.4393 | 0.446 / 0.285 / 0.587 | g3 2.6, h3 0.351, a3 0.026 |
| m2+m3 | 24,289 | 0.3994 | — | no ringing |
| persistence | — | 0.1754 | 0.185 / 0.251 / 0.090 | |

**Refit on R1 + R2c** (`v1/m*_all.json`): m1 26,477; m1+m2 26,473 (d2 → 1e-9); **m1+m3 26,271** (g3 1.18,
h3 0.353, a3 0.028 ≈ 36-tick line memory); m2+m3 43,824.

**Bootstrap** (`v1/bootstrap.json`, 2 draws per pair, warm-started from clean fits, 1 restart, block 50):

| Truth \ selected | m1+m2 | m1+m3 | m2+m3 |
|---|---:|---:|---:|
| m1+m2 | 1 | 1 | 0 |
| m1+m3 | 0 | 2 | 0 |
| m2+m3 | 0 | 0 | 2 |

Winning margins: m13 197, 294; m12 140; m23 474, 2,263. When m12 is the truth, m13 still wins one draw by 61
(M3's extra freedom). Real data: m13 26,271, m12 26,473, m23 43,824 → real margin 202, inside the m13-true
range but also reachable when m12 is true.

**Decision (§6.3.4).** M1 is **accepted** (every pair without m1 is ≥ 17,000 worse, m23 row accuracy 2/2, margins
474–2,263). M2 vs M3 is **unresolved by cost** (margin 202 ≈ optimizer noise; M2 collapses to d2 = 0 in every
clean fit, so m12 ≡ m1 and the bootstrap cannot separate "M2 inactive" from "M2 invisible"). The direct evidence
decides: the reviewer's charging A/B (§12.1) is null, as are the 150-tick charging-off hold and the second dispatch;
M3 has no clean own signature either (no reopen overshoot), but its fitted term (≈ 36-tick lagged line load with
soft curtailment above S·x ≈ 0.35) is modest, bounded and costs nothing cross-run (0.4393 vs 0.4406).
**Chosen: m1+m3 by elimination, confidence moderate (~65%).** Parameters pinned at a limit: kS = 1, kg ≈ 1,
kz = 1 (all "instant" base rates; the secondary frequency loop wants more gain → base-structure misfit, listed
below). No mechanism parameter is pinned.

## 14. Final model and hand-off (Phase C)

- **Model:** `greybox/power_grid_model.py` v1, modules m1+m3, params `fits/power_grid/v1/m13_all.json`
  (fit on R1 + R2c, cost 26,271, train score 0.530 vs persistence 0.207). M2 off (d2 = 0; D2MAX cap in the code).
- **Cross-run (R1 → R2c):** m1+m3 0.4393 (load 0.446, f 0.285, share 0.587) vs persistence 0.1754; m1-only
  fallback 0.4406; m2+m3 0.3994.
- **Gates:** local score beats persistence on R2c (0.439 > 0.175) ✓; stability (200 schedules × 4,000 + 8 × 40,000)
  0 failures, ranges load 28–175, f 47.97–52.03 (clips), share 0.024–0.56 ✓ (`v1/stability_m13.json`); contract ✓
  (from the extracted ZIP, 40 × 4,000 steps in 4.5 s, all malformed-input cases ok, credential scan clean).
- **Package:** `toronto26-participant-kit/models/power_grid/` (predict.py, power_grid_model.py, params.json) and
  `toronto26-participant-kit/submission-power_grid-v1.zip` (6 KB). Note: `package` needs `--data data/power_grid/R1.json
  data/power_grid/R2c.json` explicitly (the default glob picks up the battery JSONs and crashes).
- **Steps:** 1,000 of CAP 1,000 spent (R1 550, R2 400, R2c 50); simulator budget remaining 1,000. No steps spent in
  this resume.
- **Top open issues:**
  1. **Frequency** is the weak channel (cross-run 0.285 vs persistence 0.251): the post-release dip (49.15) and the
     joint-pulse drift are missed, and the secondary loop is pinned at kz = 1. A faster/unbounded integral loop or
     governor ramp limits are the next thing to try.
  2. **Load ringing** still under-predicted (RMSE 7.2 over R1 210–350); the price-dependent resonator gets the
     period only partly (67 vs ≈ 50 ticks at price 0). A small thermostat-population model (G3) is untried.
  3. **Mid-level reserve and price > 1.5 are unobserved** (G4, G7); M3's selection rests on elimination, not a
     positive signature. If a later public score disagrees, m1-only (`v1/m1_all.json`) is the drop-in alternative.
- **Tooling bug for the orchestrator:** `core.params_for` lets `--init` params re-enable inactive modules (§12.2).


## Round 2 spend log (approved by the user 2026-09-28; schedules in `plans/round2-experiments.md`)

| Date | Run | File | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-28 14:44–14:55 UTC | PG1 (fresh reset) | `data/power_grid/R3.json` | 380 | 620 |
| 2026-09-28 14:44–14:55 UTC | PG2 (fresh reset) | `data/power_grid/R4.json` | 510 | 110 |

Segment files: `toronto26-participant-kit/fits/round2/segments/power_grid_*.json`. Server budget confirmed after the runs.
