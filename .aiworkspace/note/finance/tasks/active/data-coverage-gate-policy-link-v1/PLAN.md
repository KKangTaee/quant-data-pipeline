# Data Coverage Gate Policy Link V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

`data-coverage-hardening-v1`은 DB price window, provider freshness, PIT replay, universe / survivorship evidence를 표시하지만 selected-route gate에는 아직 직접 반영하지 않았다.

이번 작업은 PIT / survivorship / DB coverage 공백이 남아 있는데도 `SELECT_FOR_PRACTICAL_PORTFOLIO`가 통과되는 문제를 막는다.

## Scope

- Investability gate policy에 `data_coverage` group 추가
- `DATA_COVERAGE_NEEDS_INPUT` / `DATA_COVERAGE_BLOCKED`는 selected-route 저장 차단
- `DATA_COVERAGE_REVIEW`는 선정 전 review-required로 표시
- 기존 investability packet / selected-route gate 흐름 재사용
- 새 DB write, JSONL registry, memo, preset, approval, order, rebalance 없음

## Non-Goals

- 새 historical universe source 수집
- DB schema 변경
- Data Coverage Audit 계산 로직 변경
- waiver UI / persistence

## Exit Criteria

- service contract test에서 Data Coverage `NEEDS_INPUT` blocker 확인
- service contract test에서 Data Coverage `REVIEW` review-required 확인
- 기존 ready packet 경로는 data coverage audit ready일 때 계속 selected 가능

## Implemented Slice

- `app/services/backtest_evidence_read_model.py`
  - `data_coverage` gate policy group 추가
  - 모든 profile에서 data coverage group을 selected-route critical group으로 포함
  - `Data Coverage Audit` packet check를 gate policy group에 매핑
  - `DATA_COVERAGE_NEEDS_INPUT` / `DATA_COVERAGE_BLOCKED`는 `BLOCK`, `DATA_COVERAGE_REVIEW`는 `REVIEW_REQUIRED`로 해석
- `tests/test_service_contracts.py`
  - Data Coverage `NEEDS_INPUT`이 selected route를 차단하는 contract 추가
  - Data Coverage `REVIEW`가 hold / re-review를 요구하는 contract 추가
