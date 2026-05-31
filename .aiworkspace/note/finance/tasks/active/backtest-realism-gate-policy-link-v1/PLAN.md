# Backtest Realism Gate Policy Link V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

`backtest-realism-hardening-v1`은 비용, turnover, liquidity, net performance, tax/account scope 같은 실전성 공백을 화면과 evidence packet에 표시했다.

이번 작업은 그 공백이 남아 있는데도 `SELECT_FOR_PRACTICAL_PORTFOLIO`가 통과되는 문제를 막기 위해 Backtest Realism Audit을 selected-route gate policy에 연결한다.

## Scope

- Investability gate policy에 `backtest_realism` group 추가
- `BACKTEST_REALISM_NEEDS_INPUT` / `BACKTEST_REALISM_BLOCKED`는 selected-route 저장 차단
- `BACKTEST_REALISM_REVIEW`는 선정 전 review-required로 표시
- 기존 investability packet / selected-route gate 흐름 재사용
- 새 DB write, JSONL registry, memo, preset, approval, order, rebalance 없음

## Non-Goals

- core strategy cost model 변경
- 새 provider ingestion 또는 DB schema 변경
- tax optimizer / broker integration
- waiver UI / persistence
- Data Coverage Hardening 구현

## Exit Criteria

- service contract test에서 Backtest Realism `NEEDS_INPUT` blocker 확인
- service contract test에서 Backtest Realism `REVIEW` review-required 확인
- 기존 ready packet 경로는 realism audit ready일 때 계속 selected 가능
- 문서에 gate 반영 범위와 저장 경계 반영

## Implemented Slice

- `app/services/backtest_evidence_read_model.py`
  - `backtest_realism` gate policy group 추가
  - 모든 profile에서 backtest realism group을 selected-route critical group으로 포함
  - `Backtest Realism Audit` packet check를 gate policy group에 매핑
  - `BACKTEST_REALISM_NEEDS_INPUT` / `BACKTEST_REALISM_BLOCKED`는 `BLOCK`, `BACKTEST_REALISM_REVIEW`는 `REVIEW_REQUIRED`로 해석
- `tests/test_service_contracts.py`
  - Backtest Realism `NEEDS_INPUT`이 selected route를 차단하는 contract 추가
  - Backtest Realism `REVIEW`가 hold / re-review를 요구하는 contract 추가
