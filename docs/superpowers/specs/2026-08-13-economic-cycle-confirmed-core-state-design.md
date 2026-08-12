# Economic Cycle Confirmed Core State Design

**Date:** 2026-08-13

**Status:** User-approved direction; written-spec review pending

**Scope:** RTDSM core-state confirmation, actual chronological model checkpoint,
and READY-only route UI integration

## Why this change

The raw RTDSM four-quadrant signal passed phase occupancy, three-release
revision stability, NBER semantics, and independent transition sample checks.
It failed only because 48 of 177 raw phase episodes lasted one month, a 27.12%
share above the pre-registered 25% maximum.

Lowering the threshold after seeing 27.12% would weaken the validation contract.
The approved correction is to stop treating every raw monthly quadrant as the
official state. The raw quadrant becomes a candidate signal, while a separate
point-in-time state machine owns the official phase.

This is an internal state-definition change. It does not restore the old
four-quadrant UI. The existing circular route presentation remains the product
visual if and only if the full publication gate later passes.

## Alternatives considered

### Selected: two-release confirmation state machine

- deterministic and auditable at every historical origin
- prevents a one-release reversal from rewriting the official phase
- adds at most one official-release confirmation lag
- permits every destination; no fixed adjacent cycle order

### Rejected: zero-band hysteresis

A dead zone around level and momentum zero would reduce flips with less lag,
but the band width would be another result-sensitive threshold. It is harder to
explain and reproduce across indicator revisions.

### Rejected: hidden-state or Markov smoothing

A probabilistic latent-state model could smooth the path, but it adds another
model before the forecast model, is difficult to audit, and is too complex for
the available independent transition count.

## Canonical state contract

### Raw signal

The existing RTDSM calculation remains unchanged:

- four real-time series: `IPT`, `H`, `EMPLOY`, and `RUC`
- expanding robust scaling at each official monthly origin
- three-release smoothed level and three-release momentum
- raw quadrant: recovery, expansion, slowdown, or contraction

The raw quadrant is diagnostic evidence only. It is never displayed as the
official current phase and never becomes a forecast target directly.

### Official confirmed phase

The state machine processes origins in chronological order:

1. Bootstrap requires two consecutive usable releases with the same raw phase.
   Before that, the official phase is unavailable.
2. When the raw phase equals the official phase, any candidate is cleared and
   official duration increases.
3. A different raw phase starts a candidate with streak `1/2`; the official
   phase does not change.
4. A second consecutive usable release with the same candidate confirms the
   transition at that second release. The transition is not backdated.
5. A different candidate replaces the prior candidate and restarts at `1/2`.
6. An unavailable release clears the candidate streak, stays unavailable for
   training/publication, and cannot bridge confirmation across a data gap.
7. All other phases are valid candidates, including contraction to slowdown or
   contraction to expansion. No circular order constrains the state machine.

Every confirmed record carries:

- `raw_phase`
- `confirmed_phase`
- `candidate_phase` and `candidate_streak`
- `confirmed_transition_from` and `confirmed_transition_to`
- `episode_id` and confirmed `phase_duration`
- original data status and source origin

## State validation contract

The 25% raw one-month episode result remains an audit diagnostic, not a gate on
the confirmed state. This is not threshold relaxation: the product label has a
new, pre-declared definition.

The confirmed state must pass all of these checks before any actual model fit:

- two-release invariant: no confirmed transition before the second consecutive
  candidate and no confirmed episode shorter than two usable releases
- source coverage: all four RTDSM series available at the evaluated origin
- confirmed phase occupancy: every phase at least 8% and at most 50%
- three-release revision stability: independently confirmed real-time and
  three-release-revised histories agree exactly at least 60% and by level side
  at least 80%, with at least 96 overlapping origins
- NBER recession semantics: at least 65% of recession months are on the
  recovery/contraction side
- NBER peak and trough capture: the existing 70% windows remain unchanged
- confirmed transition sample: at least 180 usable origins, 48 transitions,
  eight origins and destinations per phase, and the existing final-25% support

Raw one-month share, rejected-candidate count, candidate disagreement share,
and confirmation lag are recorded for audit. They do not become thresholds
after the actual run.

If any gate fails, status is `NO_GO_CORE_STATE`; the production phase, model,
service, and UI remain unchanged.

## Transition dataset and model

The dataset consumes the official confirmed history directly. It must not apply
a second confirmation pass.

### Targets

- transition pressure: a confirmed official phase change within the next three
  usable official releases
- destination: the next confirmed official phase, conditional on a transition

The destination class set remains all four phases. At inference, the current
confirmed phase receives zero destination probability and the remaining phases
are renormalized to one.

### Inputs

The existing RTDSM feature set remains. It adds only evidence known at the
forecast origin:

- raw-vs-confirmed disagreement flag
- candidate streak (`0` or `1` before a transition)
- one-hot candidate destination
- confirmed phase and confirmed duration

The current product's eight indicators remain corroboration only and never
enter historical fitting.

### Validation

The existing episode-weighted deterministic NumPy models and chronological
validation remain authoritative:

- complete future episodes are held out
- target-known time must be strictly before the scoring episode
- regularization selection uses prior training episodes only
- calibration uses prior OOF predictions only
- pressure is compared with global-rate and duration-hazard baselines
- destination is compared with phase-frequency and fixed-cycle baselines
- both Brier and log loss must beat the strongest baseline by at least 2%
- pressure ECE at most 0.10; destination ECE at most 0.12
- both model support gates must pass for combined `READY`

No heuristic percentage or fallback probability is published on failure.

## Persistence and service boundary

The research experiment remains read-only until the combined state and model
decision is `READY`.

Only then may a new versioned artifact and snapshot be saved through the
existing economic-cycle result tables. The stored payload must include:

- confirmed state and candidate evidence
- state audit and source cutoff
- pressure and destination parameters and calibration
- chronological model/baseline metrics and support counts
- current pressure, primary destination, alternatives, and invalidation evidence

The normal runtime remains `DB -> loader -> service -> React`. Render and refresh
paths never fetch RTDSM workbooks or fit a model.

## Product UI contract

There is no return to a four-quadrant chart.

If the combined gate and actual snapshot readback pass, the existing circular
route area is updated to show:

- official confirmed current phase
- current raw candidate as `후보 1/2`, or `새 전환 후보 없음`
- calibrated transition pressure, explicitly defined as the next three official
  releases rather than a countdown
- primary next destination plus alternative destination probabilities
- supporting, contradicting, and invalidation evidence
- source date, model version, and eight-indicator corroboration confidence

The route graphic may connect the current node to any primary or alternative
destination. It must not imply the fixed
`recovery -> expansion -> slowdown -> contraction` order.

The `자산별 확인 포인트` calculation, service payload, component markup, labels,
and CSS selectors are frozen. Regression tests must prove the same cards remain.

If the confirmed state passes but either model gate fails, no probability or
new route UI is published. A later current-state-only migration would require a
separate user review.

## Error handling and rollback

- incomplete current RTDSM input: current research inference is unavailable;
  do not substitute latest revised values
- confirmation interrupted by missing input: reset candidate streak
- state gate failure: stop before actual model fitting
- model gate failure: stop before persistence and UI
- materialization failure after `READY`: retain the prior compatible production
  snapshot and expose the failure only through existing operational evidence
- service normalization or probability simplex failure: omit the new outlook
  payload instead of rendering partial probabilities

## Verification and completion

The work is complete only when the applicable checkpoint passes:

1. unit tests demonstrate no backdating, gap reset, unrestricted destinations,
   and no second confirmation in the dataset
2. actual DB state report records raw and confirmed diagnostics
3. if state `READY`, actual chronological OOS metrics and baselines are recorded
4. if model `READY`, artifact write/readback and service contract pass
5. if UI is reached, Python tests, React tests, production build, and desktop plus
   narrow Browser QA pass with one screenshot
6. the current circular route remains the visual and asset cards remain unchanged

The mandatory stopping point is itself a valid result. A failed checkpoint is
not converted into a product feature by changing thresholds afterward.
