# Phase 31 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 현재 목표

Phase 31의 목표는 Portfolio Proposal 이후에 또 다른 수동 판단 기록을 추가하는 것이 아니다.
기존 current candidate / Pre-Live record / Portfolio Proposal draft를 읽어서
실전 검토 후보로 더 진행할 수 있는 포트폴리오 구조인지 검증하는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 31 전체 목표 | Portfolio Risk / Live Readiness validation pack을 만든다 | `active` |
| 첫 번째 작업 | 입력 계약과 validation result 모델 정의 | `pending` |
| 두 번째 작업 | `Backtest > Portfolio Proposal`에 validation surface 추가 | `pending` |
| 세 번째 작업 | component risk / overlap / concentration table 추가 | `pending` |
| 네 번째 작업 | Phase 32 robustness handoff 요약 정리 | `pending` |

## 1. Phase kickoff 준비

- `completed` Phase 31 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase31/`이다.
- `completed` Phase 31 plan 구체화
  - Phase31을 duplicate decision record가 아니라 Portfolio Risk / Live Readiness validation으로 정의했다.
- `completed` 첫 번째 작업 단위 문서 생성
  - 입력 계약과 validation model을 먼저 고정한다.
- `completed` Phase31~35 방향성 기록
  - Phase31 이후 Phase32~35를 robustness, paper ledger, final selection, post-selection 운영 guide로 본다.

## 2. 첫 번째 작업 후보

- `pending` validation input contract 정의
  - 단일 후보 direct path와 proposal draft path를 같은 입력 형태로 읽는다.
- `pending` validation result schema 정의
  - route label, score, blockers, next action, component summary 필드를 정한다.
- `pending` helper 함수 위치 결정
  - 우선 후보는 `app/web/backtest_portfolio_proposal_helpers.py`다.
- `pending` UI 배치 결정
  - `Backtest > Portfolio Proposal` 안에 `Validation Pack` tab을 추가할지, 기존 feedback 영역 안에 넣을지 결정한다.

## 3. Validation

- `pending` `python3 -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `pending` portfolio proposal helper import smoke
- `pending` current candidate / pre-live / proposal registry load smoke
- `pending` targeted manual validation

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `pending` implementation 후 `WEB_BACKTEST_UI_FLOW.md` sync
- `pending` implementation 후 `SCRIPT_STRUCTURE_MAP.md` sync 여부 검토
- `completed` roadmap / doc index / work log / question log sync

## 현재 판단

Phase 31은 준비가 시작된 active phase다.
다만 Phase 30은 아직 manual QA pending 상태이므로,
Phase 31 구현 중에도 Phase 30 QA checklist를 닫기 전까지는 Phase 30을 complete로 올리지 않는다.
