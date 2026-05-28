# Validation Efficacy Gate Policy Link V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

`validation-efficacy-hardening-v1`은 검증 효력 audit을 화면과 evidence packet에 표시했지만, selected-route gate policy에는 아직 직접 반영하지 않았다.

이번 작업은 실전 검토 통과 후보 선정 전에 `Validation Efficacy Audit`의 `NEEDS_INPUT` 또는 `BLOCKED` 상태가 pass처럼 지나가지 않도록 만드는 것이다.

## Scope

- Investability gate policy에 validation efficacy group 추가
- `VALIDATION_EFFICACY_BLOCKED` / `VALIDATION_EFFICACY_NEEDS_INPUT`은 selected-route 저장을 차단
- `VALIDATION_EFFICACY_REVIEW`는 profile-aware review required로 표시
- Final Review / selected gate read model이 기존 selected-route blocker 흐름을 그대로 사용
- 새 DB write, JSONL registry, memo, preset, approval, order, rebalance 없음

## Non-Goals

- 새 validation evidence 수집
- provider / macro ingestion 변경
- Backtest realism, cost, slippage 구현
- PIT / survivorship DB-backed 원천 보강
- waiver UI / persistence

## Exit Criteria

- service contract test에서 validation efficacy gate blocker 확인
- 기존 ready packet 경로는 audit ready일 때 계속 selected 가능
- 문서에 gate 반영 범위와 저장 경계 반영

## Implemented Slice

- `app/services/backtest_evidence_read_model.py`
  - `validation_efficacy` gate policy group 추가
  - 모든 profile에서 validation efficacy group을 selected-route critical group으로 포함
  - `Validation Efficacy Audit` packet check를 gate policy group에 매핑
  - `VALIDATION_EFFICACY_NEEDS_INPUT` / `VALIDATION_EFFICACY_BLOCKED`는 `BLOCK`, `VALIDATION_EFFICACY_REVIEW`는 `REVIEW_REQUIRED`로 해석
- `tests/test_service_contracts.py`
  - validation efficacy `NEEDS_INPUT`이 selected route를 차단하는 contract 추가
