# Market plan: identify the active mechanisms, then fit a model that stays stable over 4,000 steps

Agreed 2026-09-26. Market is the pilot, so reuse this structure for the other nine systems as `plans/<system>-plan.md`.

## Context

The goal is a `market` forecaster that predicts 4,000 steps offline, starting from a noisy initial reading and the full action schedule. The brief (`toronto26-participant-kit/briefs.md`) lists three memory mechanisms. Exactly two are active (`PROMPT.md`), and that choice is fixed for every run, phase and participant:

- **M1, funding:** inventory ties up funding until settlement.
- **M2, risk capacity:** adverse price moves reduce risk capacity.
- **M3, momentum:** investors shift exposure toward recently successful strategies.

The brief also describes a preparation → execution pipeline for orders: "a new policy does not cancel commitments already made."

- **Budget:** 2,000 paid steps, none spent as of 2026-09-26.
- **Deadline:** final uploads close 2026-09-30 12:00 Toronto time.

## Working rules

- **Before every run that spends steps:** explain in detail what the run is, why it has that design, what each possible outcome would mean, and the exact step cost. Then ask for permission. No steps are spent without an explicit yes.
- **Public checkpoint:** after about 500–1,000 steps, fit a model and upload it to the public leaderboard before spending the rest. The public score is our only unbiased feedback, because our own data comes from experiments we chose.

---

## 1. How experiments tell which mechanism is absent

We can't switch mechanisms on and off. Instead, each mechanism is a hidden state with a different **driver**, meaning the history variable it responds to:

| | Driver | Timescale |
|---|---|---|
| M1 funding | inventory × interest rate | settlement time |
| M2 risk capacity | size and direction of price moves | capacity recovery time |
| M3 momentum | recent price returns, fed back into price | momentum memory |

Signatures:

| Test | M1 funding | M2 risk capacity | M3 momentum |
|---|---|---|---|
| Price overshoot or ringing after a step | no | no | **yes** |
| Abrupt step versus slow ramp to the same level | about the same | step hits depth harder | **step overshoots, ramp does not** |
| On-step versus off-step (is the response a mirror image?) | roughly a mirror | **asymmetric: only the adverse direction reduces depth** | symmetric overshoot |
| Same price move caused by rate versus by tax | **rate-specific**, so the effects differ | **control-agnostic**, so the effects are the same | control-agnostic |
| Two pulses with a short versus long gap | 2nd pulse stronger if the gap is shorter than settlement time | 2nd pulse stronger if the gap is shorter than recovery time | weak dependence |

### Decision tree

1. **Is M3 present?** Stage A step responses show whether price overshoots.
   - Pipeline lags and coupling between observables can also cause overshoot. The confirming test is **step versus ramp**: momentum overshoot grows with how abrupt the change is.
   - If there is no momentum signature, M3 is the absent one and the answer is **M1 + M2**.
2. **If M3 is present, is the other one M1 or M2?**
   - *Asymmetry:* does depth drop after only one direction of price move?
   - *Control specificity:* does the same price move have different after-effects when a rate pulse caused it than when a tax pulse caused it?
   - An asymmetric, control-agnostic response points to **M2**. A rate-specific response that depends on inventory points to **M1**.
3. **Statistical confirmation:** fit M12, M13 and M23. Compare them on held-out rollout score, then run the bootstrap check in §3.

Write the expected signatures down *before* looking at each new dataset. This guards against confirmation bias.

---

## 2. The model

### Notation

- Controls are normalized to [0, 1]: `r = interest_rate / 0.1` and `τ = transaction_tax / 0.05`.
- The model works in log space, `y = log(price, volume, depth)`. This keeps all values positive and treats effects as multiplicative.

### Delay pipeline (preparation → execution)

Each control passes through two first-order lags. Both stages start at 0, which matches the reset rule that orders and commitments start empty.

```
q1 ← q1 + a_p·(u − q1)        # preparation
q2 ← q2 + a_e·(q1 − q2)       # execution  → effective control û = q2
```

This gives an S-shaped, delayed response: a policy change never acts instantly. If the data shows pure dead time, replace this with a d-step shift register.

### Observables relax toward a target that depends on the controls

```
y_i ← y_i + k_i(û)·(y*_i − y_i)
k_i(û) = sigmoid(κ_i0 + κ_ir·r̂ + κ_iτ·τ̂)          ∈ (0,1) always
y*_i  = c_i + w_ir·r̂ + w_iτ·τ̂ + w_irτ·r̂·τ̂ + memory terms
```

- `k(û)` is a bounded x·u interaction: the controls change *how fast* the system responds. It can't destabilize the model because it always stays in (0, 1). An unconstrained `C (x ⊗ u)` term can.
- `r̂·τ̂` is the interaction between the two controls, which the "composition" scoring category tests.

### Memory modules

Each module has a gain `g`. At `g = 0` the module still runs but has no effect, the same as a multiplier of 1.

- **M1 funding:**
  - An inventory proxy `I` is a leaky state driven by traded volume relative to baseline.
  - Funding lock: `f ← f + a1·(tanh(β1·r̂·I) − f)`.
  - It enters the volume and depth targets as `−g1v·f` and `−g1d·f`.
- **M2 risk capacity:**
  - `R ← R + a2·(1 − R) − b⁻·relu(−Δy_price) − b⁺·relu(Δy_price)`, clipped to [0.05, 1].
  - It enters the depth target as `+g2·log R`, so depth is multiplied by `R^g2`.
  - The two directions get separate coefficients, because we don't know which one is "adverse".
- **M3 momentum:**
  - `s ← s + a3·(Δy_price − s)`, a moving average of returns.
  - It adds `g3·s` to the price update.
  - This is the only real feedback loop. `g3` is capped so that the linearized price and momentum system has spectral radius < 1.

### Why the model can't blow up

- Every rate is in (0, 1).
- Every memory state is leaky and has a bounded driver.
- The only feedback loop has a capped gain.

So every constant control setting has a bounded fixed point, and nothing can diverge over 4,000 steps.

This is a discrete-time model. Stability means every eigenvalue satisfies |λ| < 1. "Negative eigenvalues" is the continuous-time condition. In discrete time a negative real λ flips sign every tick, which would show up as sawtooth noise.

**Runtime guard in `predict`:** clip outputs to a wide plausible band, for example 0.2× to 5× the observed range. If any value is non-finite, fall back to the last good value or to persistence.

### Size and fitting

- **Parameter count:** about 23 for the base model (3 observables × 7 parameters, plus 2 pipeline rates), plus 3–5 per memory module. That makes about 30 in total.
- **Fitting method:** `scipy.optimize.least_squares` on **full simulated rollouts**, not one-step-ahead predictions.
  - Residuals are scaled by σ, and the `soft_l1` loss approximates the saturating score `1/(1+|e|/σ)`.
  - Parameters are transformed to their valid ranges with sigmoid or softplus.
  - The fitting horizon is gradually lengthened: 100 steps, then 300, then the full run. Use several random restarts.
- **Noise σ:** estimated from the differences between consecutive steps in flat segments.
- **Initial state:** the `initial` reading is noisy, so it gets an optional fitted shrinkage weight.

### Model ladder

Each rung is kept only if it improves the held-out rollout score:

1. persistence
2. relaxation + delay
3. + control-dependent rates and the control interaction term
4. pair models M12, M13, M23, plus M123 as a diagnostic

---

## 3. Choosing the pair: parametric bootstrap (the fake-data check)

### Why not just fit all three and let one go to zero?

We *do* fit M123 as a diagnostic, and ideally the absent mechanism's gain comes out near 0. We don't rely on that alone, for three reasons:

- With noisy data, an unused module can absorb misfit from other parts of the model and end up with a spurious nonzero gain. Memory states integrate history, so that false effect can grow over a 4,000-step forecast.
- "Exactly two" is a hard fact. Comparing the three pairs uses it directly, with fewer parameters per model.
- A winning score on real data doesn't tell us whether the win is real or noise. The bootstrap check does.

### Procedure

1. **Fit on the real data.** Fit M12, M13 and M23 to all real runs. Record each model's leave-one-run-out rollout score. Call the best one the *winner*.
2. **Generate synthetic data from every fitted pair**, not only the winner.
   - Run each fitted model on **the exact action schedules we sent to the real simulator**, starting from the same initial readings.
   - Add measurement noise at the σ we measured, independently per observable and tick.
   - Repeat for N ≈ 20 noise draws per pair. That gives 60 synthetic datasets, with no simulator steps spent.
3. **Redo the whole selection on each synthetic dataset.** Fit all three pairs, score them with leave-one-run-out, and record which pair wins.
4. **Build a confusion matrix** of true generating pair (rows) against selected pair (columns):

   |  | selected M12 | selected M13 | selected M23 |
   |---|---:|---:|---:|
   | true M12 | … | … | … |
   | true M13 | … | … | … |
   | true M23 | … | … | … |

5. **Read it:**
   - **Strong diagonal**, for example ≥ 80% correct in every row: our experiments can identify the pairs. Trust the real-data winner.
   - **Weak diagonal for the winner's row:** the real win could be luck. Either design a more discriminating experiment (see below) or stop claiming to know the mechanism, and submit the best-scoring model.
   - **A column that wins from every row:** the selection is *biased* toward that pair. Our schedules or the model structure favor it regardless of the truth. If that column is also the real-data winner, its win means little.
   - **Spread of scores:** the gap between the winner and the runner-up on real data should be larger than the typical gap seen on synthetic data where the runner-up was the true pair.

### Using it before spending steps (screening experiments)

The same machinery ranks *candidate* experiments at zero cost:

1. Take the pair models fitted so far, or hand-set plausible parameters before any data exists.
2. For each candidate schedule, for example step versus ramp, or rate-caused versus tax-caused price moves, do the following:
   - add it to the schedules we already have;
   - generate synthetic data;
   - rerun the confusion-matrix check.
3. Spend steps on the candidate that improves the diagonal the most per step.
4. A quicker proxy for the same idea is to simulate each candidate through all three fitted pairs and pick the schedule where their forecasts differ most, measured in units of σ.

### Checking the method itself (before any real data)

Build a hand-set model with known mechanisms, for example M1 + M3 active. Treat it as a fake simulator, run the full pipeline on the planned Stage A and Stage B schedules, and check that M13 is recovered. If it isn't, fix the method or the experiment design before spending anything.

---

## 4. Guarding against bias from our own exploration and against the long horizon

- **Self-selected data:**
  - Design experiments that look like the four scoring categories: sustained operation, action order, recovery spacing, and joint controls.
  - Recovery scenarios use 70–100% of the pulse level, so emphasize values near 0 and near the maximum. Include one mid-level hold to test linearity.
  - Cross-validate by holding out whole runs, not random time steps.
  - Hold out one run generated by a random four-category schedule generator, not hand-designed.
  - Treat the public leaderboard as the real test set. If the public score is much worse than the local score, we are overfitting to our own designs, so simplify the model.
- **Forecast horizon longer than our data:**
  - Scoring runs 4,000 steps, but we can never observe more than 2,000 steps in total. Long-horizon behavior therefore has to come from model structure: a bounded fixed point, leaky states, and capped feedback.
  - Include one hold of at least 400 steps to catch slow drift, such as warehouses filling or cash running down. If the level is still moving at the end, add a slow state.
  - The score saturates, so a bounded but wrong forecast still earns partial credit, while a diverging one scores about 0.

## 5. Budget, with a public checkpoint

| Phase | Steps | Content | Gate |
|---|---:|---|---|
| A. Timescales | ~550 | One run: recovery 50 → rate only at max 125 → recovery 125 → tax only at max 125 → recovery 125 | Explain first and get permission. Learn time constants, noise σ, on/off asymmetry and overshoot. Decision-tree step 1. |
| B1. Targeted tests | ~300–400 | Chosen after A with the screening method in §3. Likely step versus ramp, plus rate-caused versus tax-caused moves of the same size. | Explain first and get permission. |
| **Public checkpoint** | 0 | Fit, then upload market to the public leaderboard (1 of 3 daily slots). Compare with the persistence score and the local leave-one-run-out score. | Report the results. |
| B2 / C | ~800–1,000 | Order and spacing runs, one long hold (≥ 400 steps), and one held-out run from the random generator. The exact mix depends on the checkpoint result. | Explain first and get permission. |
| Reserve | ~200 | Unexpected behavior. | |

### Tentative breakdown of the first ~1,000 steps

The steps are normalized so that `r = rate/0.1` and `τ = tax/0.05`. Stage A is firm. B1a and B1b are re-screened after Stage A (§3).

| Run | Steps | Segments | Main question |
|---|---:|---|---|
| A | 550 | recovery 50 → r=1 for 125 → recovery 125 → τ=1 for 125 → recovery 125 | Timescales, delay, σ, overshoot, whether on and off responses mirror each other, whether levels return to baseline |
| B1a | 200 | recovery 40 → r ramps 0→1 over 60 → r=1 for 60 → recovery 40 | Step versus ramp, compared with the abrupt rate step in A (the M3 test) |
| B1b | 250 | recovery 30 → τ=1 for 80 → recovery 30 → r=1 for 80 → recovery 30 | The reverse of A's order with a short gap: history and order effects, and control specificity (M1 versus M2) |

Stage A hold lengths are provisional. If settling takes longer than about 100 steps, lengthen the later holds, and shorten them if settling is fast.

## 6. Code (under `toronto26-participant-kit/`)

Existing code to reuse:

- `client.py`: `Client.reset/step/budget`
- `collect.py`: saving after every step and refusing to overwrite an existing file
- `example_submission/predict.py`: the module-level cache and loading files relative to `__file__`

New files:

- `run_schedule.py`: runs an explicit schedule file. It checks the budget, prints the cost, asks for confirmation, saves after every step and refuses to overwrite.
- `greybox/model.py`: the simulator above, NumPy only, with switchable modules. It is copied unchanged into the submission folder.
- `greybox/fitting.py`: rollout least-squares, the horizon curriculum, restarts and σ estimation.
- `greybox/evaluate.py`:
  - the score metric;
  - leave-one-run-out CV and the pair comparison;
  - the bootstrap confusion matrix;
  - the four-category schedule generator;
  - experiment screening;
  - the long-horizon stability test.
- `data/market/*.json`: raw runs, never overwritten.
- `models/market/predict.py` and `params.json`: the submission.

## 7. Verification

- **Offline, before spending:** check the method on a hand-set fake simulator (§3).
- **After each fit:** the leave-one-run-out score must beat persistence for every observable.
- **Stability gate:** roll the fitted model for 40,000 steps under 200 random in-bounds schedules. Every value must stay finite and bounded, with no sawtooth.
- **Contract check:** call `predict` with `docs/market.json`'s `forecast_context` and 4,000 actions. Check that it returns 4,000 dicts containing all 3 observables with finite values. Time 40 episodes, which must be well under 1,200 s.
- **Public checkpoint:** as in §5.

## 8. Log

| Date | Event | Steps spent | Remaining |
|---|---|---:|---:|
| 2026-09-26 | Plan agreed | 0 | 2,000 |
| 2026-09-26 | Run A ticks 1–175, saved in `data/market/A.json`: recovery for 50, then rate at max for 125. The runner crashed at tick 118 because OneDrive locked the file; no data was lost and the run was continued on the same run_id. | 175 | 1,825 |

**Run A, ticks 1–175: observations**

- **Reset is not an equilibrium.** Volume falls from about 90 to about 3 within 15 ticks, decaying roughly geometrically at about 0.7 per tick, then drifts down to about 2.1. Depth jumps from 84 to about 99 by tick 8, then drifts down. Price holds flat at about 108 for about 12 ticks, which looks like a pipeline delay, then falls about 0.17 per tick, and it is still falling at tick 50.
- **Rate step (rate at max from tick 51):** price starts falling faster after about 5–10 ticks and settles near 73 by about tick 110, roughly 60 ticks after the switch. It may undershoot slightly, by about 1 unit, which is too small to call M3.
- **Depth dips while price falls and recovers while the rate is still on** (91 → 85.7 → 91). This could be the M2 signature, or plain coupling to price velocity. The rate-off step will test it: does depth also dip when price rises?
- **Volume** rises slightly while price falls (2.05 → 2.41), then settles at about 1.8.
- **Noise σ:** about 0.4 for price, 0.4–0.7 for depth and about 0.02 for volume, which looks roughly proportional to level.
- **Was 125 ticks long enough?** Yes for price and volume. Depth was still recovering until about tick 165.

| 2026-09-26 | Run A, ticks 176–325: recovery for 150, with the rate switched off | 150 | 1,675 |

**Run A, ticks 176–325: observations**

- **Rate-off response is slower than rate-on.** Price stays flat at about 72.5 for about 12–15 ticks after the switch (pipeline dead time), then rises to about 93 by about tick 300, roughly 110 ticks after the switch. The fall after rate-on took about 60 ticks, starting after roughly 5 ticks, while price was already drifting. A linear model with fixed rates would make these two responses symmetric. Possible explanations are a control-dependent relaxation speed k(u), or a memory that slows recovery (M1 funding still locked, or M2 capacity still depleted).
- **Rate effect on the price level:** about −20 (73 at rate max versus about 93 at recovery).
- **Depth dips during both moves, but asymmetrically:** −5 while price fell at about 0.45 per tick, −1.2 while it rose at about 0.22 per tick. This fits M2 with "adverse" meaning a falling price. It also fits a symmetric dip proportional to speed², since 2× the speed would give 4× the dip. The B1a ramp (a slow fall) separates the two: a big dip on a slow fall means direction matters, which points to M2.
- **Depth's long-run level (about 90–91) does not depend on the rate.** Volume's baseline (about 1.8) doesn't either. Volume rises during any price move, in either direction.
- **No clear overshoot in either direction** (≤ 1 noise unit). So far this is weak evidence that M3 is absent.
- **Price at recovery is still drifting slightly down** at tick 325 (93.0 → 92.6). The long-run equilibrium price with both controls at 0 is still unknown.
- **Noise σ from flat windows:** price about 0.3–0.35, depth about 0.25–0.3, volume about 0.008. That is roughly 0.3–0.45% of the level for each.

| 2026-09-26 | Run A, ticks 326–450: tax at max, rate at 0 | 125 | 1,550 |

**Run A, ticks 326–450: observations**

- **Depth collapses immediately and with no dead time:** 90.6 → 41.3 (−54%). It moves 90.7 → 84.3 on the first tax tick and settles in about 30 ticks. Tax therefore acts on depth directly, not through the order pipeline.
- **Price rises and then partly falls back while the tax stays on.** After about 10 ticks of delay it rises from 92.5 to a peak of 98.8 around tick 390, then falls back to about 94.1 by tick 450, while the tax is still at max.
  - This looks overshoot-like, but the faster rate-driven fall did not overshoot, and M3 would predict that it should. So this is more likely a tax-specific two-timescale response (a fast push up, then a slower pull back) than momentum.
- **Volume** bumps twice, once during the rise and once during the fall back, and returns to about 1.82 at the price peak. This supports volume ≈ base + c·|price velocity|.
- **Depth barely moves during the slow price fall** (−0.2 at 0.12 per tick), which is uninformative for M2 versus speed².
- **Noise at depth 41:** σ ≈ 0.12, about 0.3% of the level, which confirms that noise is proportional to level.

| 2026-09-26 | Run A, ticks 451–600: recovery with the tax switched off. Run A is complete. | 150 | 1,400 |

**Run A, ticks 451–600: observations**

- **Depth recovery mirrors the tax-on drop.** The first tick jumps 41.3 → 47.3 with no dead time, and depth is back at about 90.6 by tick 485. The speed is about 12–13% of the remaining gap per tick in both directions. So the tax acts on depth directly, symmetrically and with no memory: depth returns to its pre-tax level (about 91).
- **The price response is not a mirror image.** Tax-on gave a +6.3 hump that settled at +1.6. Tax-off gives only a small step down, 94.2 → 93.0, after about 30 ticks of dead time, with at most a −0.5 dip. So the tax's effect on price depends on history or state.
  - One hypothesis: price impact scales inversely with depth. While depth was collapsed, some remaining order imbalance moved price much more.
- **Every level returns to the same value after each pulse:** price about 93.0, depth about 91 and volume about 1.78 with both controls at 0. No lasting level shift is visible after recoveries of 125–150 ticks. History shows up in the transients, not in the settled levels.

**Run A summary: settled levels**

| Setting | price | volume | depth |
|---|---:|---:|---:|
| recovery (0, 0) | ~93.0 | ~1.78 | ~91 |
| rate max | ~73 | ~1.81 | ~90.5 |
| tax max | ~94.1 (after the hump) | ~1.82 | ~41.3 |

## Model v1 (2026-09-26): M1 + M2 + depth withdrawal

The code is in `toronto26-participant-kit/greybox/market_model.py` (simulator, standard library only) and `greybox/fit_market.py` (rollout least squares). Fits are saved in `fits/market/`.

**Relationships found in Run A**

| Driver → output | Relationship |
|---|---|
| rate → price | −21% (93 → 73). Pipeline delay of 5–15 ticks. The fall takes about 60 ticks and the recovery about 110. The asymmetry is modeled as M1: funding locks almost instantly (k_in ≈ 1) and releases slowly (k_out ≈ 0.04). |
| rate → volume, depth | No direct effect on the level. Only indirect effects through price moves. |
| tax → depth | Direct and immediate, no pipeline: −54% (91 → 41). About 13% of the gap closes per tick. Symmetric in *linear* units, no memory. |
| tax → price | Small sustained effect of +1.2%. The +6 hump appears on tax-on only, and is explained by the depth-withdrawal term below. |
| tax → volume | None directly. |
| price speed → volume | V ≈ 1.8·(1 + 76·rise + 63·fall), where rise and fall are the log-return per tick. Volume lags by about 3 ticks. The correlation with \|ΔP\| is 0.92. |
| price moves → depth (M2) | Leaky memory with a timescale of about 20 ticks. Falls hurt depth about 2× more than rises (m_dn ≈ 11.7, m_up ≈ 5.7). |
| depth falls → price | Leaky memory of about 55 ticks of the *falling* fraction of depth pushes the price target up. Rising depth has no effect. This one-sided term replaces the symmetric tax high-pass ("hump"), which wrongly predicted a mirror dip on tax-off. |
| reset | A decaying state z (about 9 ticks) shifts all targets. The price pipeline starts at the initial reading, which is why price holds flat for about 12 ticks. |

**Held-out test:** train on ticks 1–450 and predict 451–600. The score uses std as the stand-in σ.

| Model | Held-out score | RMSE price / volume / depth |
|---|---:|---|
| persistence | 0.374 | — |
| M1+M2 + hump | 0.753 | 8.2 / 0.105 / 0.89 |
| **M1+M2 + withdraw** | **0.934** | 0.89 / 0.031 / 0.62 |
| M1+M3 + withdraw | 0.928 | 0.88 / 0.031 / 1.02 |
| M2+M3 + withdraw | 0.843 | 2.3 / 0.069 / 2.7 |

**Mechanism evidence**

- **M2 is strong:** without it, depth error roughly triples during the rate segment.
- **M1 is supported:** M2+M3 is the worst pair.
- **M3 is weak:** M1+M3 improves price only around the undershoot near ticks 110–130, with its gain pinned at the 0.9 cap, and it loses depth accuracy.
- **All three together is degenerate:** fitting M1+M2+M3 produces absurd depth coefficients. This is the spurious-module problem.
- **Bootstrap not yet run:** the M1+M2 versus M1+M3 comparison hasn't been checked on synthetic data yet.

**Stability:** 200 random schedules, including 8 of 40,000 steps, all stayed finite and bounded (price 72–104, volume 1.8–2.5, depth 37–91). 40 episodes of 4,000 steps take 4.2 s.

**Parametric bootstrap (2026-09-26)**

The script is `greybox/bootstrap_market.py` and the results are in `fits/market/bootstrap.json`.

- **Setup:** 5 synthetic datasets from each fitted pair (full-600 fits with withdraw), all on Run A's exact schedule and initial reading. The noise is circular-block-resampled real log residuals (block length 50, reset transient excluded), so each dataset carries misfit of realistic size and autocorrelation. All three pairs are refit on each dataset, 2 restarts each.
- **Confusion matrix:** m12 → m12 5/5, m13 → m13 5/5, m23 → m23 4/5. The one miss was a failed m23 optimization with a cost of 11,910.
- **Margins:** when a pair is true, it wins by about 470–2,300 cost units.
- **Real data:** m12 6,827, m13 6,791, m23 8,290.
  - **M2+M3 is rejected**, since its gap of about 1,460 is in the bootstrap range. So **M1 is present**.
  - **M1+M2 versus M1+M3 is a tie** (a 36-unit gap). That is outside what either synthetic world produces, which means the real system has structure that neither pair model captures. m12 patches depth, and m13 patches the price undershoot. The next step is to fix the structure and run the targeted tests (a ramp for M3, a slow price fall for M2). Adding data alone won't settle it.
- **Submitted:** M1+M2, because it has the best held-out score, the best depth fit, and no feedback gain pinned at the cap.

**Submission v1:** `submission-market-v1.zip` contains `market/{predict.py, market_model.py, params.json}` and uses the full-600 m12+withdraw fit. The contract check passes: 40×4,000 steps are finite and take about 2 s, run from the extracted ZIP.

**Public checkpoint (2026-09-26):** `submission-market-v1.zip` scored **0.6838** publicly, against a local held-out estimate of 0.934.

- **σ sensitivity:** the local score depends heavily on the stand-in σ. Scaling the std stand-in by 0.1–0.2 turns the same held-out errors into 0.65–0.77 (price 0.60, volume 0.55, depth 0.80 at 0.1×), which brackets the public score. The organizer σ is therefore probably about 5–10× smaller than each observable's std.
- **Going forward:** evaluate locally with σ = 0.1×std, not std.
- **Distribution shift is not excluded:** joint controls, intermediate levels and long holds are all still untested.

**Open gaps:** only levels 0 and max have been tested, so the effect at intermediate control levels (whether the response is linear) is unknown. Joint controls are untested. We don't know whether the equilibrium of about 93 depends on the initial reading, since there has been only one reset.


## Round 2 spend log (approved by the user 2026-09-28; schedules in `plans/round2-experiments.md`)

| Date | Run | File | Steps | Remaining after |
|---|---|---|---:|---:|
| 2026-09-28 14:44–14:55 UTC | MK1 (fresh reset) | `data/market/B.json` | 600 | 800 |
| 2026-09-28 14:44–14:55 UTC | MK2 (fresh reset) | `data/market/C.json` | 600 | 200 |

Segment files: `toronto26-participant-kit/fits/round2/segments/market_*.json`. Server budget confirmed after the runs.

## Round 2 model (v2) (2026-09-28)

Modeler pass per `plans/agent-prompts/round2-modeler.md`. No steps spent, nothing uploaded or committed. Module `toronto26-participant-kit/greybox/market_model_v2.py` (v1 copy plus switchable modules; with only m1,m2,withdraw active it reproduces v1 to 1e-14). Scripts, fits, logs and plots: `toronto26-participant-kit/fits/market/round2/v2/` (`run.py` fits a variant on a fold and scores held-out runs with σ = 0.1×std after tick 20 of A+B+C = 0.865 / 0.0354 / 2.37, identical to `fits/round2/heldout.py`; `plot.py`; `probe.py`).

**Diagnosis items addressed (structural changes, all bounded):**

| Module | Change | Diagnosis item | Final value |
|---|---|---|---|
| conv | rate enters as r^p_r in the price target and M1 lock | B18 (convex rate map) | p_r = 1.30 |
| gate | M1 release k_out·exp(−g_τ·τ): settlement needs trading | B15 (price hysteresis under tax), fix 1 | g_τ = 4.42 (release ×0.11 at τ=0.5, ×0.012 at τ=1) |
| dmap | depth tax factor 1/(1+w_dh·τ) replaces 1+w_dτ·τ | B17 | w_dh = 1.156 (diagnosis: 1.19) |
| m2mult | M2 capacity loss multiplicative on tax-reduced depth, floored at 0.05 | B20, fix 6 | flag |
| inv | reset inventory I (=1 at reset, unwinds at k_I·(1−τ)); capital K∈(0,1]: dK = b_K(1−K) − a_K·r·I·K; K scales depth, slows price discovery k_p·K^n_K, forced selling a_K·r·I raises volume | B11, B12, B13, B16 (joint from reset), fix 3 | a_K 0.041, b_K 0.026, k_I 0.069, n_K 4.0 (pinned at bound), b_I 15.6 |
| jx | price target −w_x·r⁴·τ | B21 (joint after recovery 66.6) | w_x = 0.136 |
| vjx | slow volume decline under r·τ | B16 (joint volume decay) | a_sv 0.013, w_sv 0.088 |
| vfl | volume ×(1 + b_fl·4τ(1−τ)·max(F−r,0)) | B16 (tax-0.5 plateau 2.08) | b_fl 0.63 |

**Held-out and in-sample scores** (mean of price / volume / depth per run; σ as above):

| Test | Runs scored | v1 (shipped) | v1 structure refit | v2 |
|---|---|---|---|---|
| (A) transfer: fit A | B | .232/.202/.337 = 0.257 | same as v1 (refit reproduces cost 6826.7) | .229/.182/.469 = 0.293 |
| | C | .363/.246/.577 = 0.395 | same as v1 | .355/.261/.687 = 0.434 |
| | **mean** | **0.326** | 0.326 | **0.364** |
| (B) fit A+B | C | 0.395 | .352/.278/.326 = 0.319 | .286/.231/.668 = 0.395 |
| (B) fit A+C | B | 0.257 | .261/.221/.355 = 0.279 | .266/.160/.484 = 0.303 |
| | **mean** | **0.326** | 0.299 | **0.349** |
| (C) fit A+B+C (in-sample) | A | .635/.567/.889 = 0.697 | .488/.420/.683 = 0.530 | .554/.509/.762 = 0.608 |
| | B | 0.257 | .295/.269/.431 = 0.332 | .405/.346/.622 = 0.458 |
| | C | 0.395 | .505/.268/.590 = 0.454 | .576/.474/.755 = 0.602 |
| | mean | 0.450 | 0.439 | **0.556** |

(A)-fold v2 values for the new modules are prior-driven (A cannot identify them; SPEC starting values were informed by the diagnosis, which saw B and C), so the transfer gain is partly prior, not evidence. The (B) folds are weak tests: each new run holds unique regimes (B: joint from reset; C: half rate, tax after rate, tax 0.5), so a fold cannot learn what only the held-out run shows (A+B→C misses convexity and the gate; A+C→B misses the reset drain). Depth gains are robust across every test; price/volume gains are mostly in-sample.

**Decision:** ship v2 (`full` variant, final fit `fits/market/round2/v2/full_ABC_s3.json`, cost 75416, two restarts agree to 1 unit). It beats v1 under (A) (+0.038) and (B) (+0.023) and the v1-structure refit everywhere. The v1-structure refit is worse than v1 on held-out runs, so the structure, not new data, is what helps. **In-sample on A drops 0.09 vs v1 (0.697 → 0.608)**, above the 0.03 threshold: investigated — the v1 structure refit on all data drops A even more (0.530), so the loss is the price of fitting three regimes jointly, concentrated in A's reset price transient (ticks 10–60, model falls too early) and A's volume bumps. Accepted because v1's A fit does not transfer (0.26–0.40 on B, C). Per-module ablations were not run (each fit takes 8–18 min on the shared machine); in the first final fit vjx and vfl went to ~0 and returned in the refined fit, so their value is unproven.

**Gates:** stability (200 × 4,000 + 8 × 40,000 random schedules) pass, 0 failures, ranges price 65–113, volume 1.6–77 (reset burst), depth 16–121. Contract on `models/market` pass (40 × 4,000 in 1.1 s, deterministic, all malformed-input cases ok). `ALLOW_MARKET_PACKAGE=1 python3 -m greybox.common.package ... --version v2` wrote `models/market/` (predict.py, market_model_v2.py, params.json) and `submission-market-v2.zip` (market/ at root), package check passed. Heldout.py on the package: A 0.608, B 0.458, C 0.602. v1 remains in `fits/round2/v1_models/market/` and `submission-market-v1.zip`.

**Design choices and predictions** (`probe.py`, initial 100/100/100; price/volume/depth):

| Hold | t=600 | t=4000 |
|---|---|---|
| recovery (0,0) | 93.1 / 1.77 / 90.1 | same |
| rate 0.7 | 80.3 / 1.77 / 90.1 | same |
| tax 0.7 | 93.8 / 1.77 / 49.8 | same |
| joint 0.7 (from reset or after recovery) | 79.0 / 1.70 / 49.8 | same |
| rate 1 | 73.5 / 1.77 / 90.1 | same |
| tax 1 | 94.0 / 1.77 / 41.8 | same |
| joint 1 after recovery | 64.8 / 1.62 / 41.8 | same |
| **joint 1 from reset** | 80.2 / 2.73 / 16.1 | **65.1 / 2.67 / 16.2** |
| joint 0.85 from reset | 73.0 / 1.67 / 45.3 | 73.0 / 1.66 / 45.5 |

Everything settles; no drift after ~600 ticks except joint 1 from reset, where tax exactly 1 stops inventory unwinding (1−τ = 0), so capital stays at b_K/(b_K+a_K) ≈ 0.39 forever: depth floors at 16, volume stays 2.7, and price creeps to 65 over ~2,000 ticks (k_p·K⁴). Any τ < 1 unwinds the reset inventory within a few hundred ticks.

**Open issues**

1. Joint-at-full-tax-from-reset is extrapolated from 150 ticks of one run: the drain floor (data still falling at 12, model floors at 16), whether it needs the rate, and whether the (1−τ) unwind is right at τ = 0.7–0.99 are all unknown. This is the largest risk for the sustained and joint categories.
2. Pinned parameters: n_K = 4 (upper bound; the price block wants to be stronger than K⁴ allows — missing structure for B11), k_in = 1 and a_c = 1 (M2 memory collapsed to instantaneous).
3. Unmodelled: B volume spikes under joint 0.7 (up to 3.0 near tick 440) and at 540–580; the C price overshoot to 95 after tax-off (M3-like); A reset price transient timing.
4. No ablations; vjx/vfl/jx each rest on one or two segments.

**Reserve recommendation (200 steps, not spent):** run the diagnosis §6 Run D, one fresh reset: ticks 0–99 (rate 0, tax 0.05), then `--continue` ticks 100–199 (rate 0.1, tax 0.05). Against v2: v2 predicts tax-only from reset gives depth ≈ 43 with no drain (the drain needs r·I) and normal price drift; adding the rate at tick 100 predicts only a small drain because I has unwound only while τ<1 — under tax 1 v2 keeps I = 1, so v2 predicts the full drain (depth to ~17) and a blocked price fall starting at tick 100. If the data drain at 0–99 without rate, the drain is tax × reset state (drop r from the drain); if depth keeps falling below 16 after tick 150 of rate+tax, lower the K floor (raise a_K/b_K). Either outcome refits only the `inv` module (5 params) on A+B+C+D.
