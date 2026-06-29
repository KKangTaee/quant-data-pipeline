# Design

Status: Active
Last Updated: 2026-06-19

## Service Model

`app/services/overview_market_context_analog.py` remains the owner of the historical analog and nested `macro_conditioned_analog` payload.
3차-C adds a nested audit payload without replacing the broad analog rows or the existing pilot rows:

```text
historical_analog["macro_conditioned_analog"]["macro_dimension_audit"]
```

The audit has its own schema version and a list of dimension items. Each item includes `id`, `label`, `status`, `status_label`, `usage`, `source`, `detail`, latest/as-of date, coverage range, and anchor preview count.

## Dimension Rules

- `sector_relative_strength`: `USED`, because it is the broad anchor condition.
- `gld_safe_haven_context`: `USED` when GLD condition is already used by the pilot; otherwise insufficient.
- `futures_rate_pressure_context`: `USED` when 3B futures condition is used; otherwise insufficient.
- `T10Y3M`, `VIXCLS`, `BAA10Y`: `AVAILABLE_REFERENCE` when stored rows exist through selected as-of. They show bucket preview count only and do not filter the pilot sample.
- Events: `DEFERRED` or `INSUFFICIENT_HISTORY`; near-term event rows remain Market Context annotation.
- Sentiment: `DEFERRED` or `INSUFFICIENT_HISTORY`; stored CNN / AAII history remains context only.

## Macro Bucket Preview

Stored macro series are loaded with `finance.loaders.macro.load_macro_series_observations()`.
Rows after selected as-of are excluded. For each series, the current/as-of bucket is computed from the latest available row at or before the broad analog as-of date, and anchor preview count is the number of broad anchors with the same bucket using rows at or before each anchor date.

The preview answers “if this dimension became a future hard condition, how many broad anchors would share the current bucket?” It does not shrink `macro_conditioned_analog["rows"]`.

## UI

`app/web/overview_ui_components.py` renders `맥락 차원 상태` inside the existing `Macro 조건 포함 pilot` block.
It groups dimension items as compact rows instead of an operational job table and emphasizes `사용`, `참고`, `조건 부족`, and `보류` labels.

## Boundaries

This remains a context-only Overview read model. It does not introduce provider fetches, schema changes, storage writes, predictions, recommendations, validation gates, Final Review decisions, or Operations monitoring semantics.
