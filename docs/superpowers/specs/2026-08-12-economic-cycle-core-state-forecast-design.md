# Economic Cycle Core State And Transition Forecast Design

Date: 2026-08-12
Status: approved by the user on 2026-08-12

## Why this exists

The RTDSM expansion solved the original sample shortage: it produced 589 usable
monthly origins and 117 independent confirmed transitions. It did not justify a
forecast because the long four-indicator state agreed with the recent
eight-indicator state on only 54.2% of overlapping months. A model cannot be
trained on one phase definition and presented against another.

This design removes that contradiction. One long-history core state will define
the phase consistently in both historical training and current inference. The
recent eight-indicator state will become corroborating evidence for confidence,
risk, and explanation; it will no longer be a separate training label that the
long history must imitate.

## Product outcome

The finished economic-cycle surface should answer four separate questions:

1. What is the current core phase?
2. How much pressure exists for any confirmed transition within the next three
   official monthly releases?
3. If a transition occurs, which destination phase is most plausible, and what
   are the meaningful alternatives?
4. Which current eight-indicator and market-context observations support or
   contradict that path?

It does not promise an exact phase one or two calendar months from today. Asset
checkpoint calculations, payloads, markup, and styling remain frozen.

## Approaches considered

### A. Force the long state to reproduce the current eight-indicator state

Rejected. Lowering the parity threshold, changing indicators after seeing the
score, or training a short 142-month mapping and extrapolating it back to 1971
would preserve the current label cosmetically but create unstable historical
truth.

### B. Use one RTDSM core state across the full history — selected

`IPT`, `H`, `EMPLOY`, and `RUC` are available as provider-native real-time
vintages over the long sample. The same transforms, expanding scale, phase
definition, and confirmation rule apply to every historical and current origin.
The recent eight-indicator panel becomes a corroboration layer rather than an
incompatible label authority.

### C. Supervise four phases directly from NBER chronology

Rejected as the primary label. NBER provides recession peaks and troughs, not a
monthly four-phase truth. NBER chronology remains an independent semantic audit
for peaks, troughs, and recession concentration; it is not used as a model
feature or as a fabricated four-class label.

## Canonical core state

The first version reuses the already implemented point-in-time RTDSM signals:

- `IPT`: six-month annualized log change
- `H`: three-month annualized log change
- `EMPLOY`: three-month annualized log change
- `RUC`: negative three-month level change
- each signal: 60-month expanding robust z-score using only eligible vintages
- activity score: equal-weight `IPT` and `H`
- labor/income score: equal-weight `EMPLOY` and `RUC`
- raw level: equal-weight activity and labor/income
- level: three-month mean of raw level
- momentum: three-month level change

The quadrants remain:

- recovery: level below zero, momentum non-negative
- expansion: level non-negative, momentum non-negative
- slowdown: level non-negative, momentum negative
- contraction: level below zero, momentum negative

A transition is confirmed after the candidate phase is observed in two
consecutive official monthly origins. No fixed
`recovery -> expansion -> slowdown -> contraction` route is imposed. Every
other phase is a valid destination candidate.

## Core-state semantic and stability gate

The old eight-indicator parity gate is retired as a publication requirement
because the old state is no longer the training truth. Before the core state can
replace the product's current phase, all of these pre-registered checks must
pass:

- source coverage: all four RTDSM series available at the evaluated origin
- phase occupancy: every phase represents at least 8% and no more than 50% of
  usable monthly origins
- episode stability: one-month episodes are at most 25% of all phase episodes
- three-release revision stability: exact phase agreement at least 60% and
  level-side agreement at least 80% when an origin is recomputed using the
  vintage available three releases later
- NBER recession semantics: at least 65% of NBER recession months fall on the
  below-trend side (`recovery` or `contraction`)
- NBER peak capture: at least 70% of NBER peaks have `slowdown` or `contraction`
  within the window from six months before through three months after the peak
- NBER trough capture: at least 70% of NBER troughs have `recovery` within the
  window from three months before through six months after the trough
- existing independent transition sample gate remains `GO_EXPERIMENT`

NBER checks validate economic meaning only. They cannot be optimized or used as
training features. If this gate fails, the current product phase is not changed
and forecast fitting stops.

## Corroboration layer

The current eight-indicator panel remains point-in-time and keeps its current
activity/labor grouping. It produces:

- exact phase agreement or disagreement with the core state
- level-side agreement
- activity and labor direction agreement
- available/stale series counts
- confidence: `HIGH`, `MEDIUM`, or `LIMITED`
- supporting and contradicting evidence rows for explanations

It does not change the core phase mechanically, supply historical labels, or
alter model probabilities. Financial, leading, inflation, and policy context
may appear as conditional risk evidence, but it does not become a probability
input without separate long point-in-time validation.

## Forecast targets

Two targets use only the canonical core-state history.

### Transition pressure

Binary target:

`transition_confirmed_within_next_3_releases`

The displayed pressure is the calibrated probability of this event. High means
a confirmed phase change is more likely within the next three official
releases; low means the current core phase is more likely to persist over that
window. It is not a countdown.

### Destination

Multiclass target:

`next_confirmed_phase`

The class set is recovery, expansion, slowdown, and contraction, excluding the
current phase at inference. The target is the next actually confirmed phase,
not the next phase in a hard-coded cycle order. Destination probabilities are
presented conditional on a future transition and must sum to one over valid
destinations.

Monthly origins from one phase episode are not treated as independent events.
Training weights are normalized so each anchored phase episode has total weight
one, and chronological validation holds out complete episodes.

## Model inputs and algorithms

The initial model is deliberately small and interpretable.

Inputs:

- four RTDSM signal z-scores
- activity score and labor/income score
- level and momentum
- one-, three-, and six-release changes in level and momentum
- activity/labor dispersion and directional breadth
- current core phase and confirmed phase duration
- source freshness flags

Algorithms:

- transition pressure: deterministic NumPy L2-regularized binary logistic regression
- destination: deterministic NumPy L2-regularized multinomial logistic regression
- missing required core inputs: fail closed; no imputation from current revised
  data
- calibration: prior out-of-fold predictions only; binary Platt scaling and
  multiclass temperature scaling

Regularization strength is selected only inside each training window. The
current eight-indicator corroboration fields are excluded from fitting because
their strict real-time history is too short.

No new machine-learning dependency is added. The repository environment does
not include scikit-learn, so weighted fitting, prediction, and calibration use
small deterministic NumPy implementations with convergence and finite-value
checks.

## Chronological validation and publication gate

Validation uses expanding windows and complete episode blocks. No random row
split is allowed. A fold can score an origin only when its eventual target is
known before the following training cutoff.

Baselines:

- transition pressure: expanding global event rate and expanding
  phase-duration empirical hazard
- destination: expanding current-phase-conditioned destination frequency and
  deterministic fixed-cycle route

The strongest baseline for each metric is authoritative. Both models must pass.

### Transition-pressure gate

- at least 48 scored OOS transition events
- OOS Brier score and log loss each at least 2% better than the best baseline
- expected calibration error at most 0.10
- every chronological holdout block contains both event and non-event rows

### Destination gate

- at least 48 scored OOS destination events
- every destination has at least 8 OOS events and at least 2 in the final 25%
  holdout
- OOS multiclass Brier score and log loss each at least 2% better than the best
  baseline
- expected calibration error at most 0.12

The combined status is `READY` only when the core-state gate and both model
gates pass. A `LIMITED` or failed component does not receive a fallback
probability, heuristic percentage, or UI publication.

## Persistence and service boundary

Research validation is in-memory and side-effect free. Only a `READY` combined
result may be serialized to the existing
`economic_cycle_model_artifact` table under a new model version and materialized
as an `economic_cycle_snapshot`.

The artifact records:

- core feature schema and state-gate report
- pressure and destination parameters
- calibration parameters
- chronological fold metrics and baseline comparisons
- training cutoff and source coverage
- publication decision and reason codes

The snapshot records:

- canonical core observed state
- eight-indicator corroboration and confidence
- transition-pressure probability
- conditional destination probabilities
- primary and alternative destination paths
- supporting, contradicting, and invalidation evidence

Normal UI render remains `DB -> loader -> service -> React`; it never downloads
RTDSM workbooks, fits a model, or reruns validation.

## UI behavior after validation

If the core-state gate passes but either forecast gate fails, only the validated
core current-state migration is eligible for a later UI review; forecast
probabilities stay hidden. If all gates pass, the cycle route shows:

- current core phase
- transition pressure with a plain-language window definition
- primary destination and calibrated probability
- alternative destinations rather than a fixed circular arrow
- conditions that strengthen or invalidate the path
- current eight-indicator corroboration and data limitations

The existing asset checkpoint section remains unchanged.

## Failure and rollback behavior

- source or required-input failure returns `UNAVAILABLE`; it does not use latest
  revised data as historical truth
- core-state gate failure stops all forecast work
- either forecast gate failure prevents probability persistence and display
- a current materialization failure keeps the last compatible dated snapshot
  visible only within its explicit freshness policy
- the current production snapshot and UI are not replaced until actual DB and
  Browser QA pass

## Implementation boundaries

Expected new or changed owners:

- `finance/economic_cycle_core_state.py`: canonical state, revision and NBER
  semantic audit
- `finance/economic_cycle_transition_dataset.py`: episode-weighted targets and
  feature matrix
- `finance/economic_cycle_transition_model.py`: two regularized models,
  calibration, prediction
- `finance/economic_cycle_transition_validation.py`: chronological folds,
  baselines, gates
- existing RTDSM loader/history modules: only narrowly reusable read/build
  seams
- persistence, service, and React: changed only after the combined gate passes

No change is authorized for asset checkpoint calculations or design.
