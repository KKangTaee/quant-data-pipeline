# Phase 8 Investability Data Evidence Expansion Design

Status: Active
Created: 2026-05-28

## Design Boundary

Phase 8은 데이터 근거의 의미를 강화하는 phase다.
사용자-facing 저장 기능을 늘리지 않고, ingestion -> DB -> loader -> audit 흐름을 유지한다.

```text
official / free source
  -> finance/data/*
  -> finance_meta.nyse_symbol_lifecycle
  -> finance/loaders/universe.py
  -> Data Coverage Audit / Validation Efficacy / Final Review gate
```

## Lifecycle Evidence Model

`nyse_symbol_lifecycle`은 symbol별 lifecycle event와 coverage evidence를 담는다.

| Field group | Meaning |
| --- | --- |
| `symbol`, `kind` | normalized ticker and stock / ETF kind |
| `listing_status` | row가 말하는 listing 상태 |
| `source`, `source_type` | source identity와 source category |
| `coverage_status` | actual / partial / bridge / proxy / missing / error |
| `first_seen_date`, `last_seen_date` | coverage interval |
| `inactive_detected_at` | inactive / delisting detection date |
| `event_type`, `event_date` | row가 나타내는 lifecycle event의 의미와 기준일 |
| `related_symbol`, `related_cik` | ticker change / merger 같은 related entity |
| `evidence_json` | source-specific compact evidence |

## PASS / REVIEW Principle

Data Coverage Audit은 source를 보수적으로 해석한다.

| Evidence | Audit meaning |
| --- | --- |
| current listing snapshot only | REVIEW |
| SEC Form 25 row only | delisting evidence, not complete membership |
| historical listing row covering requested period | PASS candidate |
| computed snapshot coverage covering requested period | PASS candidate if source contract is documented |
| missing lifecycle row | NEEDS_INPUT or REVIEW depending other DB evidence |

## First Implementation Slice

이번 slice는 source crawler를 추가하기 전에 schema / row contract를 먼저 정리한다.

- Add event fields to `nyse_symbol_lifecycle`.
- Fill event fields in current NYSE listing snapshot rows.
- Fill event fields in SEC Form 25 delisting rows.
- Load event fields through `finance/loaders/universe.py`.
- Keep JSONL boundary unchanged.

## Next Source Slice

`historical-membership-source-review-v1` 결과, 다음 구현은 Nasdaq public Symbol Directory current snapshot ingestion으로 정한다.

```text
Nasdaq public SymDir files
  -> finance/data/symbol_directory.py
  -> finance_meta.nyse_symbol_lifecycle
  -> finance/loaders/universe.py
  -> Data Coverage Audit
```

이 slice는 complete historical membership을 만들지 않는다.
row는 `source_type=current_listing_snapshot`, `coverage_status=partial`, `event_type=listing_observed`로 저장한다.

Implementation status:

- `finance/data/symbol_directory.py` normalizes public Symbol Directory rows.
- `app/jobs/ingestion_jobs.py` exposes `run_collect_symbol_directory_snapshots()`.
- The collector writes only DB lifecycle rows and reports no registry / memo / preset side effects.

## Tradeoff

Phase 8-1만으로 survivorship 문제가 완전히 해결되지는 않는다.
하지만 event semantics를 먼저 고정해야 이후 ticker change, merger, historical membership source를 같은 table에 안전하게 적재할 수 있다.
