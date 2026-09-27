# greybox/common: shared research tools

These tools are generalized from the market pilot (`greybox/*_market.py`). Run every command from `toronto26-participant-kit/` as `python -m greybox.common.<tool>`. None of them spends simulator steps: none calls `Client.step`, `collect.py` or `run_schedule.py`.

| File | Purpose |
|---|---|
| `core.py` | Data and model loading, units, noise σ, the score metric, random schedules, brief/docs parsing |
| `settle.py` | Settling check for a segment (framework §4.3) |
| `battery.py` | The standard analysis battery with plots and a JSON of measurements (§6.1) |
| `fit.py` | Generic full-rollout least-squares fitter (§5). **Its docstring defines the model-module interface.** |
| `bootstrap.py` | Parametric bootstrap: confusion matrix and winning margins (§6.3) |
| `gates.py` | Local score, stability and contract gates (§7) |
| `package.py` | Builds `models/<system>/` and the ZIP, then re-verifies from the extracted copy (§7.4) |
| `predict_template.py` | The generic `predict.py` that `package.py` copies into each submission folder |
| `template_model.py` | Starting point for a new system's model. Copy it to `greybox/<system>_model.py` and edit its top block. |

## Conventions

- **Data arguments** accept `path.json` or `path.json:0,2` (0-based run indices). Every run in a file is one episode. Continued runs (several `run_schedule.py` calls) are a single run.
- **Ticks** are 0-based observation indices, and `--start/--end` are slice bounds `[start, end)`. Index 0 is the reading after the first action, which the market plan calls "tick 1".
- **σ has two meanings.**
  - *Noise σ* is estimated from second differences within holds (MAD/0.6745/√6). It is used for settling checks and to scale fit residuals.
  - *Score σ* is 0.1 × the std of each observable after tick 20. It is used for local scores and matches the public leaderboard (lesson 7).
- **Normalized controls** use `u = (value − recovery)/(pulse − recovery)`, with the recovery and pulse values parsed from the brief text.

## Model-module interface (full contract in `fit.py`'s docstring)

Required:
- `SPEC`: `{name: (initial natural value, kind)}`
- `MODULES`: `{module: ([owned params], {param: off value})}`
- `to_natural(name, raw)` and `to_raw(name, value)`
- `normalize(action, bounds) -> tuple`
- `simulate(p, initial, actions) -> T rows × observables`, in natural units

Optional:
- `OBSERVABLES`: output order; the default is the brief's order.
- `UNITS`: `{obs: 'log'|'linear'}`
- `NOISE`: `{obs: σ in those units}`
- `CLAMP`: `{obs: [lo, hi]}`
- `FIXED`
- `params_for`, `free_names`

A fit activates a **set of module names**. Parameters owned by inactive modules are held at their "off" values. Residuals are `(units(pred) − units(obs))/σ` for every tick and observable of every episode, concatenated, so multiple runs and files are fitted jointly with equal weight per tick. Non-finite values are replaced by 1e4 and all residuals are clipped to ±1e4. The optimizer uses `loss='soft_l1'` with `f_scale=2`. Costs are comparable only between fits that share the same data, window, units and σ.

`simulate` must re-initialize all hidden state on every call and must never raise for finite parameters. It may use only math, NumPy and SciPy, because the file is copied into the submission as-is.

## CLI examples

```sh
# settling check (default: the run's last hold); prints a table plus JSON with "all_settled"
python -m greybox.common.settle data/epidemic/R1.json
python -m greybox.common.settle data/epidemic/R1.json --start 40 --end 120

# battery -> data/epidemic/R1_battery.json + R1_r0_battery.png (next to the data unless --out)
python -m greybox.common.battery data/epidemic/R1.json

# fit a pair jointly on two runs; --units/--noise override the module's UNITS/NOISE (else auto-estimated)
python -m greybox.common.fit --model greybox/epidemic_model.py --data data/epidemic/R1.json data/epidemic/R2.json \
    --modules m1,m2,reset --restarts 3 --out fits/epidemic/m12_all.json
# cross-run test: fit on R1, then score on R2 (--eval also works inside fit)
python -m greybox.common.fit --model greybox/epidemic_model.py --data data/epidemic/R1.json --modules m1,m2 \
    --eval data/epidemic/R2.json --out fits/epidemic/m12_r1.json
python -m greybox.common.gates score --model greybox/epidemic_model.py --params fits/epidemic/m12_r1.json \
    --data data/epidemic/R2.json --ref data/epidemic/R1.json data/epidemic/R2.json

# bootstrap (3 draws default; every candidate refit on each synthetic dataset, in parallel)
python -m greybox.common.bootstrap --fits fits/epidemic/m12_all.json fits/epidemic/m13_all.json \
    fits/epidemic/m23_all.json --out fits/epidemic/bootstrap.json

# gates
python -m greybox.common.gates stability --model greybox/epidemic_model.py --params fits/epidemic/final.json --system epidemic --data data/epidemic/R1.json
python -m greybox.common.gates contract models/epidemic --system epidemic

# package (refuses models/market and submission-market-*); --dry-run builds in a temp dir
python -m greybox.common.package --system epidemic --model greybox/epidemic_model.py --params fits/epidemic/final.json --version v1
python -m greybox.common.package --all-zip submission-overnight-all.zip --folders models/epidemic models/market ...
```

## Notes from validation (market, `fits/common_validation/`)

- `fit.py` reproduces the market M1+M2+withdraw fit on `data/market/A.json` exactly: log units, σ = 0.004, full 600 ticks, cost 6826.74, the same value as `fits/market/m12_withdraw_train600.json`. It takes 37 s with 3 parallel restarts.
- **Horizon curriculum** (`--horizons 100,300`) was worse on market (8689 against 6827). Use it only when a direct fit is stuck, and compare the costs.
- **Restart perturbation.** The default is now 0.1, where `fit_market.py` used 0.3. At 0.3, restarts mostly land in bad basins. At 0.1, restart 2 found the same minimum.
- The template model, configured for market, fits in about 40 s (27 params) to a train score of 0.62 with σ = 0.1×std, against 0.66 for the hand-built market model. Its rollout costs about 2.5 ms per 600 ticks.
- **Contract check.** The existing `models/market` passes. Its NaN-initial case returns NaN, which counts as a warning, not a failure. The generic `predict.py` falls back to `params.json` `fallback` levels instead.
