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

Spend summary: R1 = 550 steps (cap 550). Budget remaining 1,450 (spent 550 of CAP 1,000).

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
