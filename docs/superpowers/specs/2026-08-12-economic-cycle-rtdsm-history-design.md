# Economic Cycle RTDSM History Expansion Design

Date: 2026-08-12  
Status: approved by the user's 2026-08-12 implementation instruction

## Why this exists

The current point-in-time economic-cycle panel has only 148 usable monthly
origins and 32 independent confirmed transitions. That is not enough to train
or validate the requested next-destination probabilities. The next safe step is
to extend real-time history before building a forecast model or UI.

This design adds an official Philadelphia Fed RTDSM history path and reruns the
already-approved sample gate. It does not publish a probability, alter the
current observed phase, or change the asset checkpoint section.

## Source contract

The primary source is the Federal Reserve Bank of Philadelphia Real-Time Data
Set for Macroeconomists. The first implementation uses four full-history
workbooks:

| Provider ID | Meaning | Vintage cadence | Earliest vintage | Experimental role |
| --- | --- | --- | --- | --- |
| `IPT` | Total industrial production index | monthly | 1962:M11 | activity |
| `H` | Aggregate weekly hours index, total | monthly | 1971:M9 | activity |
| `EMPLOY` | Nonfarm payroll employment | monthly | 1964:M12 | labor/income |
| `RUC` | Unemployment rate | quarterly | 1965:Q4 | labor/income |

Each workbook is a wide matrix: observation months are rows and provider
vintages are columns. A monthly vintage header is conservatively known at the
end of that month. A quarterly RTDSM vintage is conservatively known at the end
of its middle month: Q1 February, Q2 May, Q3 August, and Q4 November. Exact
release times are not inferred.

Non-numeric cells such as `#N/A` are absent observations, not numeric zeroes.
The collector must validate the sheet name, `DATE` column, provider prefix,
unique monotonic vintage headers, parseable observation months, and at least one
numeric value before producing rows.

The official files currently contain malformed XLSX core timestamps such as
`T 8:20:58`. The parser may repair only that metadata timestamp in memory. It
must not alter worksheet values.

## Storage and ingestion design

Use `finance_meta.macro_series_vintage_observation` because its business key
already represents `(series, observation, realtime_start, source)` and the
writer is source-neutral. Store provider-native IDs so RTDSM rows cannot collide
with the existing FRED IDs.

RTDSM rows use:

- `source = philadelphia_fed_rtdsm`
- `source_type = official`
- `source_mode = rtdsm_full_history_monthly` or
  `rtdsm_full_history_quarterly`
- `realtime_start = conservative known-at month end`
- `realtime_end = day before the next vintage`, with the latest vintage open
  through `9999-12-31`
- `observation_date = first day of the observation month`

Ingestion is idempotent and batch-based. An incremental run includes the latest
already-stored vintage again so its formerly open `realtime_end` is closed when
a new vintage appears. Provider downloads use bounded retries and emit only a
compact summary; raw workbooks and parsed rows are not written to repository
artifacts.

## Experimental long-history state

The RTDSM path is research-only and separate from the current eight-indicator
observed-state runtime.

For each month-end origin, choose the latest RTDSM vintage known at that origin
and calculate:

- `IPT`: six-month annualized log change
- `H`: three-month annualized log change
- `EMPLOY`: three-month annualized log change
- `RUC`: negative three-month level change

Each signal receives a 60-month expanding robust z-score using only values known
at that origin. Activity is the equal-weight mean of `IPT` and `H`; labor/income
is the equal-weight mean of `EMPLOY` and `RUC`. The composite level is the
three-month mean of their equal-weight average, and momentum is its three-month
change. Quadrant names remain recovery, expansion, slowdown, and contraction.

This long-history state is not allowed to overwrite the current phase. It may
become a model-development label source only after parity and sample gates pass.

## Gates

The implementation produces one audit report with two independent decisions.

### Sample support gate

Reuse the existing next-transition feasibility thresholds unchanged:

- at least 180 usable origins
- at least 48 independent two-release confirmed transitions
- at least 8 transitions from and to every phase
- latest 25% holdout contains at least 12 events and at least 2 destinations in
  every phase

### Common-period parity gate

Compare RTDSM long-history phase labels with the current strict-PIT observed
state only on months where both are available. Before seeing the production
result, lock these minimums:

- at least 96 overlapping usable months
- exact four-phase agreement at least 60%
- Cohen's kappa at least 0.40
- level-side agreement at least 75%, where recovery/contraction are below-trend
  and expansion/slowdown are above-trend

The combined decision is `GO_MODEL_EXPERIMENT` only when both gates pass.
Otherwise it is `NO_GO_PARITY` or `NO_GO_DATA`, and destination/imminence model
development stops.

## Failure behavior

- HTTP, XLSX structure, or source-contract failure fails the affected series;
  it does not silently substitute current revised data.
- A partial provider run is reported as partial and cannot produce a combined
  model-development GO decision.
- Missing cells remain missing.
- ADS is deferred to a later coincident cross-check because its all-vintages
  workbook is much larger and is not needed to establish the long transition
  sample. It cannot be used to rescue a failed RTDSM parity result after the
  fact.

## Alternatives considered

1. **Shared vintage ledger with provider-native IDs — selected.** Reuses the
   stable PIT business key and existing idempotent writer without conflating
   series identities.
2. **New RTDSM-only table.** Clearer physical isolation but duplicates the same
   vintage semantics and adds schema/loader maintenance before it is justified.
3. **Research-only workbook bypass.** Fastest audit, but it would leave no
   repeatable ingestion-to-DB-to-loader path and would not satisfy the product's
   data-boundary rules.

## Frozen scope

- current eight-indicator phase calculation and current snapshot materialization
- destination probability and transition-imminence models
- Overview service, React component, Data Freshness button, and probability UI
- every calculation, payload field, and visual in `자산별 확인 포인트`

