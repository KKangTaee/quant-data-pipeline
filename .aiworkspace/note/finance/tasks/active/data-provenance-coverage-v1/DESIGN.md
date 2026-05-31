# Data Provenance Coverage V1 Design

Status: Complete
Created: 2026-05-28

## Design Position

이번 task는 ingestion schema 변경이 아니라 read-model hardening이다.

기존 DB tables already include:

- `source`
- `source_type`
- `source_ref`
- `coverage_status`
- `as_of_date` 또는 `observation_date`
- `collected_at`
- `missing_fields_json`

따라서 첫 slice에서는 새 column을 추가하지 않고, loader 결과를 Practical Validation provider context에서 compact provenance로 요약한다.

## Proposed Provider Provenance Contract

Each provider coverage area should expose:

| Field | Meaning |
|---|---|
| `freshness_status` | `fresh`, `stale`, `unknown`, `not_run` |
| `source_mix` | official / database_bridge / computed_proxy source type summary |
| `source_type_weights` | portfolio target weight 기준 source_type coverage |
| `coverage_status_weights` | actual / partial / bridge / proxy / missing / error weight |
| `as_of_range` | compact min / max snapshot date |
| `collected_range` | compact min / max collection timestamp |
| `stale_symbols` | max staleness threshold를 넘은 ETF symbol |
| `stale_weight` | stale symbols의 target weight 합 |
| `symbol_rows` | symbol별 compact source / coverage / as-of / stale row |

Macro context uses series count rather than portfolio weight.

## Freshness Policy

- ETF provider snapshot default freshness threshold: 45 days.
- Macro default freshness threshold remains 10 days.
- If ETF snapshot coverage would otherwise be `PASS` but stale weight is positive, diagnostic status becomes `REVIEW`.
- Staleness is not automatically `BLOCKED` because provider snapshot recency depends on issuer update cadence.
- `NOT_RUN` still means missing loader result or missing evidence, not pass.

## Storage Boundary

- No full holdings, exposure, macro series, or raw provider response is stored in JSONL.
- Practical Validation result stores compact provenance only.
- Final Review reads the compact result; it does not refetch provider data.

## Implemented Files

| File | Change |
|---|---|
| `app/services/backtest_practical_validation_provider_context.py` | Added provider context schema v2, compact provenance / freshness summaries, 45-day ETF provider staleness policy, and display row source/freshness columns |
| `app/services/backtest_practical_validation_diagnostics.py` | Added compact provenance fields to Practical Validation metrics provider coverage summary |
| `tests/test_service_contracts.py` | Added provider context provenance contract test |
