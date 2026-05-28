# Integrated Investability Gate QA V1

Status: Complete
Started: 2026-05-28

## 이걸 하는 이유?

Validation Efficacy, Data Coverage, Backtest Realism audit은 각각 selected-route gate에 연결됐다.

이번 작업은 세 audit과 기존 provider / robustness / paper observation / final evidence gate가 함께 작동할 때 `SELECT_FOR_PRACTICAL_PORTFOLIO`를 과도하게 허용하거나, 반대로 보류 / 재검토까지 막는 문제가 없는지 통합 contract로 고정한다.

## Scope

- Investability packet의 ready / review / blocker 통합 경로 service contract 추가
- 세 audit이 모두 ready일 때 selected-route가 허용되는지 확인
- 여러 `REVIEW` gap은 selected-route만 막고 hold / re-review는 허용하는지 확인
- 여러 `NEEDS_INPUT` / `BLOCKED` gap은 selected-route blocker로 모이는지 확인
- waiver, live approval, order, auto rebalance, 새 저장소가 생기지 않는지 확인

## Non-Goals

- 새 DB schema 또는 ingestion 구현
- 새 JSONL registry / memo / preset 저장 기능
- waiver UI / persistence
- Final Review 화면 레이아웃 변경

## Exit Criteria

- `FinalReviewEvidenceReadModelContractTests`에 통합 gate QA contract가 추가된다.
- 전체 service contract test가 통과한다.
- 문서가 현재 통합 gate QA 완료 상태를 반영한다.

## Implemented Slice

- `tests/test_service_contracts.py`
  - ready 통합 fixture 추가
  - 세 audit과 provider / robustness / paper / final evidence가 모두 ready일 때 selected-route 허용 contract 추가
  - provider + 세 audit의 다중 `REVIEW` gap이 selected-route만 차단하고 hold / re-review는 허용하는 contract 추가
  - 세 audit의 다중 `NEEDS_INPUT` / `BLOCKED` gap이 selected-route blocker로 모이는 contract 추가
