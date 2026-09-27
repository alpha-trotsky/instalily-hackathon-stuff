# market

Everything the organizers publish about the `market` system, taken from `docs/market.json` (fetched from the gateway on 2026-09-26). Sections 1–5 restate the official text. Section 6 is my interpretation and is marked as hypotheses.

Budget at fetch time: **2,000 / 2,000 simulator steps remaining.**

---

## 1. What you observe and control

**Observables** (what the simulator reports, and what you forecast). All three change every tick. The ranges below apply only to the first reading after a reset.

| Name | Meaning | Initial reading after reset |
|---|---|---|
| `price` | Market price | uniform in 90 – 110 |
| `volume` | Traded volume | uniform in 80 – 120 |
| `depth` | Order-book depth (an aggregate) | uniform in 80 – 120 |

**Interventions** (what you set every tick; forecast schedules stay inside these bounds):

| Name | Min | Max | Units |
|---|---:|---:|---|
| `interest_rate` | 0.0 | 0.1 | fraction per trading period |
| `transaction_tax` | 0.0 | 0.05 | fraction per trading period |

Every action must name both controls.

**Reference actions:**

| | interest_rate | transaction_tax |
|---|---:|---:|
| Recovery | 0.0 | 0.0 |
| Pulse | 0.1 | 0.05 |

Recovery scenarios in scoring move each control independently to between 70% and 100% of the way from recovery to pulse. Using the recovery action costs paid steps; it is **not** a reset.

---

## 2. How the system works (official description)

**Participants**
- Producer and consumer groups differ in **reservation values**, **storage capacities** and **placement speeds**.
- Production **consumes working cash**. Final consumption **returns revenue**.

**Orders**
- Orders move through **preparation → execution**.
- A new policy **does not cancel commitments already made**, so orders in the pipeline finish under the old conditions.

**Dealers**
- Completed trades transfer goods and cash between customers and **finite dealer books**.
- Dealers share **settlement** and **outside hedging** resources.

**Memory mechanisms (three candidates, exactly two active)**
1. Inventory may **tie up funding until settlement**.
2. Adverse price moves may **reduce risk capacity**.
3. Investors may **shift desired exposure toward recently successful strategies**.

**About `depth`**
- Reported depth is an aggregate. The **side, location and settlement status** of the available capacity can change what a later reversal does. Equal `depth` readings can therefore hide different internal states.

---

## 3. Reset and initial state

- Reset randomizes **only** the three observables, within the ranges above. The initial reading includes the same measurement noise as research observations.
- All hidden quantities start from **fixed reference conditions, identical on every reset**. Any dependence on the initial observables is deterministic. There is no random prehistory.
  - Customer warehouses: **half full**
  - Customer working cash: **full**
  - Dealer books: **neutral**
  - Orders and settlement commitments: **empty**
- Public and final hidden episodes use this same reset rule.

---

## 4. Operating rules (same for all systems)

- Controls act on the evolving state. **The same action can have different effects after different histories.**
- There is no hidden translation controller: actions are applied in the physical units above.
- Research observations are noisy. Forecasts are scored against the **noiseless** observables.

---

## 5. Evaluation (same for all systems)

- The same physical parameters and active mechanisms apply to every participant, and to development, public and final scoring.
- Each phase has **40 secret episodes of 4,000 steps**:
  - 10 sustained operation
  - 10 intervention order
  - 10 recovery spacing
  - 10 joint intervention
- Your `predict` receives the noisy initial observation and the complete 4,000-step action schedule. It gets no feedback during the episode.

`context` passed to `predict` (from `forecast_context`):

```python
{
  "protocol": "forecaster-v1",
  "revision": "research-forecast-v8",
  "family": "market",
  "observables": ["price", "volume", "depth"],
  "intervention_bounds": {"interest_rate": [0.0, 0.1], "transaction_tax": [0.0, 0.05]},
  "brief": "<brief text>",
  "documents": [<the 3 documents>],
}
```

---

## 6. My reading: hypotheses, not facts

- **Delays are certain.** Both the "preparation → execution" pipeline and "commitments already made" mean a control change should appear with a lag, not instantly. A first-order relaxation model will capture part of this. A pure delay or a second hidden stage may be needed.
- **Interest rate** plausibly acts through working cash and dealer funding (production cost, inventory financing). **Transaction tax** plausibly acts on trading activity (`volume`) and dealer willingness to quote (`depth`).
- **Telling the three mechanisms apart:**
  - *Funding tied up until settlement:* the effect should depend on how much inventory was built up, and should clear on the settlement timescale regardless of price path.
  - *Risk capacity reduced after adverse price moves:* depth should drop after a sharp price move and recover slowly. The order of up versus down moves should matter.
  - *Momentum-chasing exposure:* expect overshoot or oscillation in `price` after a change, rather than smooth settling.
- **Candidate first experiment** (about 450 steps, **not yet run**): hold recovery for 150 steps, then pulse for 150, then recovery for 150. Check (a) whether it settles, (b) how fast, and (c) whether it returns to the same level afterwards (memory) and whether it overshoots (momentum).
