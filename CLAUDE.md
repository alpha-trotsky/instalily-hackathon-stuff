# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Work for the Instalily x Google DeepMind Toronto 26 hackathon (individual competition). The goal is to research ten hidden black-box simulators through a paid HTTP gateway, then upload numerical forecasters that predict 4,000-step trajectories offline. `toronto26-participant-kit/` is the organizer-supplied starter kit. The full rules are in `PROMPT.md`, per-system physics hints and action bounds are in `briefs.md`, and setup and packaging steps are in `README.md`. Read `briefs.md` before modeling any system.

Systems (folder names must match exactly): `epidemic`, `market`, `traffic`, `power_grid`, `supply_chain`, `wildlife`, `reservoir`, `ad_auction`, `social_contagion`, `hospital_queue`.

Key dates (America/Toronto): final uploads open 2026-09-28 12:00 and close 2026-09-30 12:00.

## Simulator budget: treat it as irreversible spending

Each system has **2,000 simulator steps total for the whole event**. The budget never resets, and every `/step` call costs one step (reset, brief, documents and budget reads are free). Do not run `collect.py` or call `Client.step` without the user's explicit go-ahead, and check the budget first. Running `plans/overnight-framework.md` counts as that go-ahead, but only within its per-system caps (1,000 steps, or 1,300 for systems with 6 controls). Market has already spent 600 steps and is excluded from that run. Save every observation to disk as soon as it arrives. `collect.py` does this after every step and refuses to overwrite an existing output file; preserve that behavior in any new collection scripts.

## Workspace layout (our additions to the kit)

- `app-141-1d2abb-credentials.json` (repo root, gitignored): has the fields `gateway_url`, `gateway_key`, `portal_credential` and `team_id`. Load the key into `os.environ` only for the duration of a process. Never print it, copy it into files, or put it in a ZIP. `team_id` is the application ID, not a key. It doesn't exist in cloud sessions. There, the environment's API credential adds the key outside the VM.
- `toronto26-participant-kit/gateway.py`: `make_client()` builds a gateway client from the credentials file, from environment variables, or with no key for the cloud proxy. `python run_schedule.py --budget <system>` is a free budget read.
- `toronto26-participant-kit/run_schedule.py`: the only way to spend steps. It runs explicit segment schedules, saves after every step, refuses to overwrite, and `--continue` extends a run without a reset. `--confirm N` must equal the step count.
- `toronto26-participant-kit/greybox/`: the gray-box model, rollout fitter, parametric bootstrap and plotting, from the market work. `data/<system>/` holds raw runs, and `fits/<system>/` holds fitted parameters and logs.
- `plans/`: `market-plan.md` is the worked example (log, observations, model, bootstrap, public score). `overnight-framework.md` is the autonomous runbook for the other nine systems (run completed; see `overnight-report.md`). `<system>-plan.md` and `<system>-review.md` hold each system's full record.
- `toronto26-participant-kit/fetch_docs.py`: makes free reads only (brief, documents, budget) and writes `docs/<system>.json`. `brief.forecast_context` in those files is the exact `context` dict passed to `predict`, so use it for local tests.
- `docs/<system>.md`: human-readable digest of a system's published info (`market.md` exists so far). The documents add little beyond `briefs.md` except the initial-observation ranges.
- `models/<system>/`: submission folders. All ten hold gray-box models (`predict.py`, a model-module copy, `params.json`). Market is v1 (public 0.6838). The other nine come from the overnight run of 2026-09-27; the combined upload `submission-overnight-all.zip` scored 0.71 average publicly. **Start any new session by reading `plans/overnight-report.md`**: it has the handoff, per-system findings, remaining budgets, tooling gotchas and the next plan.

## Modeling approach agreed so far

- Start each system with a first-order relaxation model: the target level is `c + W·controls`, and `y += k·(target − y)`. Add slow hidden states, saturation, and then mechanistic structure only when a backtest shows the need.
- Fit parameters by minimizing error over full simulated rollouts (for example `scipy.optimize.least_squares`), not one-step-ahead regression. Rollouts are 4,000 steps and the observations are noisy.
- Experiments should hold settings long enough to settle (step responses, pulse-then-recover, reversed orders), not random blocks. Market Run A (600 steps) followed this pattern. See `plans/market-plan.md`.
- For the organizer's hidden `sigma`, use 0.1 × each observable's standard deviation when scoring locally. With 1 × std, market's local estimate was 0.93, while its public score was 0.68.

## Commands

Run from `toronto26-participant-kit/`, because the scripts use `from client import Client`. The dev environment uses Python 3.12 with `numpy` and `httpx`, plus `google-genai` for Gemma research only.

This machine runs Windows. Credentials come from the JSON file above, or you can set them in PowerShell:

```powershell
$env:GROUNDTRUTH_GATEWAY_URL = 'https://gt-gateway-wavddee32q-uc.a.run.app'
$env:GROUNDTRUTH_KEY = '<learning key>'      # never write into files or the ZIP
$env:GEMMA_API_KEY = '<Google AI Studio key>' # research only
```

```sh
python fetch_docs.py                                                                   # free
python collect.py --system power_grid --steps 128 --output power-grid-research.json   # SPENDS 128 steps
python fit.py power-grid-research.json --output example_submission/model.json
```

The repo has no test suite or linter. To validate a forecaster, import `predict.py` and call it locally with a context dict and 4,000 in-bounds actions. Check that it returns 4,000 dicts containing every observable with finite values, and time the run: 40 episodes must fit in 1,200 s on 2 CPUs.

Packaging: put system folders at the ZIP root with no enclosing `models/` folder (see README §3). Limits are 30 MiB zipped and 300 MiB expanded. Each system gets 3 accepted uploads per Toronto day, shared between the public and final phases, and a crash after acceptance still uses the slot.

## Architecture / data flow

- `client.py`: a thin `httpx` wrapper around the gateway (`reset`, `step`, `budget`, `brief`, `documents`). Mutations send an `Idempotency-Key` and retry once on transport errors with the same key. Pass your own `request_id` if you retry at a higher level.
- `collect.py` → research JSON: `{family, brief, runs: [{initial, actions[], observations[]}]}`. The `brief` contains `observables` (list) and `interventions` (name → `[low, high]`). The starter probe uses random piecewise-constant actions held for `--block` ticks.
- `fit.py` → `model.json`: a ridge-regularized linear state-space model `x' = A x + B u + bias`. `x` holds observables standardized by center and scale, and `u` holds actions min-max normalized by the brief bounds. `A` is rescaled to spectral radius ≤ 0.995 for stability. This is only a baseline. The real systems have hidden state, delays, saturation and history effects, so observables alone do not form a Markov state.
- `example_submission/predict.py`: the submission contract `predict(initial, interventions, context) -> list[dict]`. It caches the loaded model in a module global, re-initializes trajectory state from `initial` on every call, clamps outputs to ≥ 0, and falls back to persistence when there is no `model.json`.

## Submission constraints that shape code

- The scoring sandbox has Python 3.12 with only NumPy 2.3.5, SciPy 1.16.3, scikit-learn 1.7.2 and joblib 1.5.2. It has no network, simulator or LLM access, and 3 GiB RAM.
- Load model files relative to `__file__`. Each system folder is evaluated independently, so copy shared helpers into every folder that needs them.
- Model weights may persist across calls, but simulated state must never carry over between episodes.
- Scoring compares forecasts with noiseless observables using `1/(1+|err|/sigma)`, averaged over observables, ticks and 40 episodes. The four scenario categories are weighted equally: sustained operation, action order, recovery history, and composition of controls. `initial` is noisy, so smoothing or estimating the true initial state helps.
- In every system, the physical parameters and active mechanisms are fixed across participants and phases, and exactly 2 of the 3 candidate mechanisms listed in `briefs.md` are active. Hidden state resets to a fixed deterministic convention with no random prehistory, so a model fitted in development transfers directly to final scoring.
- Leaderboard rank is the mean over all ten systems, and a missing system scores 0. A persistence baseline for every system beats leaving systems out.
