# Look-through Exposure Board V1 Design

Status: Complete
Created: 2026-05-28

## Design Position

이번 task는 ingestion 기능이 아니라 provider read model과 UI surface를 보강하는 작업이다.

Data path:

```text
finance/data/etf_provider.py
  -> finance_meta.etf_holdings_snapshot / etf_exposure_snapshot
  -> finance/loaders/provider.py
  -> app/services/backtest_practical_validation_provider_context.py
  -> Practical Validation / Final Review
```

## Board Contract

`look_through_board`는 raw holdings 전체가 아니라 아래 compact rows만 가진다.

| Field | Meaning |
|---|---|
| `status` | holdings / exposure diagnostic status를 합친 board status |
| `summary` | Final Review에서 읽을 한 줄 해석 |
| `summary_rows` | coverage, freshness, top holding, top overlap, unknown exposure 요약 |
| `asset_bucket_rows` | portfolio weight 기준 asset bucket exposure |
| `top_holding_rows` | holdings overlap top rows |
| `fund_coverage_rows` | ETF별 holdings / exposure coverage, freshness, as-of |
| `exposure_detail_rows` | exposure snapshot의 상위 compact evidence rows |
| `limitations` | 1차 look-through / compact evidence 한계 |

## Storage Boundary

- full holdings row는 DB에 남긴다.
- Practical Validation result에는 top rows와 compact summary만 저장한다.
- Final Review는 Practical Validation result를 읽고, provider data를 다시 fetch하지 않는다.
- 새 registry나 user memo 저장 기능은 만들지 않는다.

## UI Contract

Practical Validation:

- Provider Coverage 바로 아래에 Look-through Exposure Board를 표시한다.
- Summary / Asset Buckets / Top Holdings / Fund Coverage / Exposure Detail로 나눠 읽는다.
- Provider Data Gaps는 기존처럼 부족 데이터 수집 action을 담당한다.

Final Review:

- Practical Diagnostics summary 아래에서 board summary를 보여준다.
- 상세 row는 expander 안에 두어 최종 판단 화면이 과밀해지지 않게 한다.

## Implementation Files

| File | Implemented Change |
|---|---|
| `app/services/backtest_practical_validation_provider_context.py` | Added compact look-through board builder inside provider context |
| `app/services/backtest_practical_validation_diagnostics.py` | Added compact look-through metrics without duplicating full board outside provider context |
| `app/services/backtest_evidence_read_model.py` | Expanded final decision evidence rows with saved look-through summary rows |
| `app/web/backtest_practical_validation.py` | Rendered full Look-through Exposure Board in Practical Validation |
| `app/web/backtest_final_review.py` | Rendered compact board summary in Final Review |
| `app/web/backtest_final_review_helpers.py` | Preserved board through existing provider coverage snapshot only, avoiding duplicate top-level storage |
| `tests/test_service_contracts.py` | Added provider look-through board contract assertions and final decision evidence expansion coverage |
