# Phase 33 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 현재 목표

Phase 33의 목표는 Phase 32를 통과한 후보나 Portfolio Proposal을 바로 최종 선정하는 것이 아니다.
실제 돈을 넣기 전에 paper tracking 조건을 append-only ledger로 남기고,
Phase 34 final selection decision pack이 읽을 수 있는 관찰 기록 기반을 만드는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 33 전체 목표 | Paper Portfolio Tracking Ledger를 만든다 | `active` |
| 첫 번째 작업 | Paper ledger row 계약과 저장소 경계 정의 | `in_progress` |
| 두 번째 작업 | Paper ledger draft / save UI 추가 | `pending` |
| 세 번째 작업 | 저장된 paper ledger review surface 추가 | `pending` |
| 네 번째 작업 | Phase 34 final selection handoff 정리 | `pending` |

## 1. Phase kickoff

- `completed` Phase 32 closeout 확인
  - Phase 32는 `complete / manual_qa_completed` 상태다.
- `completed` Phase 32 next phase preparation 확인
  - Phase 33 방향은 `Paper Portfolio Tracking Ledger`다.
- `completed` Phase 33 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase33/`이다.

## 2. 첫 번째 작업 준비 항목

- `in_progress` paper ledger row schema 정의
  - source type, source id, tracking start date, target weights, benchmark, review cadence, triggers를 정한다.
- `pending` append-only 저장소 경계 정의
  - 예상 저장소는 `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`이다.
- `pending` Phase 32 handoff -> paper ledger draft 변환 기준 정의
  - `phase33_handoff.requirements`를 ledger draft의 최소 입력으로 사용한다.

## 3. Validation

- `pending` `.venv/bin/python -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `pending` ledger helper smoke
- `pending` targeted manual validation

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `pending` Backtest UI flow sync

## 현재 판단

Phase 33은 active / not_ready_for_qa 상태다.
아직 UI / 저장 helper 구현은 시작 전이며, 첫 작업은 paper ledger row 계약과 저장소 경계를 정하는 것이다.
