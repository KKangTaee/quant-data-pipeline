# Phase 10 Walk-forward / OOS / Regime Validation Design

Status: Active
Created: 2026-05-29

## Design Principle

Phase 10은 "더 많이 저장"하는 방식이 아니라 "이미 존재하는 성과 / 가격 / macro / validation evidence를 더 엄격하게 해석"하는 방식으로 시작한다.
필요한 신규 데이터는 무료 API 또는 공개 source를 우선 검토하고, 검증 효력을 높이는 경우에만 DB-backed ingestion으로 연결한다.

## Evidence Layers

| Layer | Purpose | Initial Source |
| --- | --- | --- |
| Source map | 현재 백테스트 결과, curve, benchmark, macro, robustness evidence가 어디에서 오는지 확인 | `app/services/backtest_practical_validation*.py`, `app/services/backtest_evidence_read_model.py`, DB loaders |
| Split contract | walk-forward / OOS window를 같은 의미로 읽기 위한 compact schema 정의 | result bundle curve, benchmark curve, DB price proxy |
| Regime contract | market condition bucket별 성과 / drawdown / benchmark spread 확인 | macro loader, market context, stress / monthly return helpers |
| Audit rows | `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 표시 | Practical Validation / Final Review read model |
| Gate policy | selected-route 가능 여부에 overfit / OOS / regime gap 반영 | investability packet / selected-route gate |

## Route Semantics

| State | Meaning |
| --- | --- |
| `PASS` | 충분한 기간과 source를 바탕으로 split / OOS / regime evidence가 기준을 만족 |
| `REVIEW` | 일부 evidence는 있으나 기간, coverage, source strength, sensitivity가 부족 |
| `NEEDS_INPUT` | 실행에 필요한 curve / benchmark / macro / split source가 없음 |
| `BLOCKED` | evidence가 명확히 deployable-fit 판단을 막는 수준으로 약함 |

`NOT_RUN`은 pass가 아니다. 실행하지 못한 검증은 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.

## Candidate Implementation Boundaries

초기 구현 후보는 아래 경계 안에서 다룬다.

- `app/services/backtest_practical_validation_stress_sensitivity.py`: rolling / stress / monthly return helper 재사용 여부 확인
- `app/services/backtest_validation_efficacy.py`: validation efficacy audit 확장 후보
- `app/services/backtest_evidence_read_model.py`: Final Review gate policy 연결 후보
- `app/web/backtest_practical_validation.py`: read-only evidence display 후보
- `app/web/backtest_final_review.py`: investability packet / selected-route evidence display 후보
- `finance/loaders/macro.py`, `finance/loaders/market.py` equivalent source: regime source 확인 후보

실제 파일 변경은 10-1 source map / gap audit 후 결정한다.

## Data Boundary

- full split curve, raw optimization grid, raw provider response는 workflow JSONL에 저장하지 않는다.
- 필요한 raw / series data는 DB에 두고 loader가 compact summary를 제공한다.
- Practical Validation JSONL에는 기존 흐름이 허용하는 compact evidence만 둔다.
- user memo, preset, approval, order, auto rebalance 성격의 저장은 추가하지 않는다.

## User Flow Target

사용자는 기존 흐름을 유지한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Selected Portfolio Dashboard
```

Phase 10이 끝나면 Practical Validation과 Final Review에서 "이 전략은 전체기간 수익률은 좋아도 OOS / regime evidence 때문에 보류해야 한다"는 결론을 더 명확히 볼 수 있어야 한다.
