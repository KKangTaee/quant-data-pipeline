# Phase 31 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 31의 목표는 Portfolio Proposal 이후에 또 다른 수동 판단 기록을 추가하는 것이 아니다.
기존 current candidate / Pre-Live record / Portfolio Proposal draft를 읽어서
실전 검토 후보로 더 진행할 수 있는 포트폴리오 구조인지 검증하는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 31 전체 목표 | Portfolio Risk / Live Readiness validation pack을 만든다 | `implementation_complete` |
| 첫 번째 작업 | 입력 계약과 validation result 모델 정의 | `completed` |
| 두 번째 작업 | `Backtest > Portfolio Proposal`에 validation surface 추가 | `completed` |
| 세 번째 작업 | component risk / overlap / concentration table 추가 | `completed` |
| 네 번째 작업 | 다음 robustness 검증 단계 안내 요약 정리 | `completed` |

## 1. Phase kickoff 준비

- `completed` Phase 31 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase31/`이다.
- `completed` Phase 31 plan 구체화
  - Phase31을 duplicate decision record가 아니라 Portfolio Risk / Live Readiness validation으로 정의했다.
- `completed` 첫 번째 작업 단위 문서 생성
  - 입력 계약과 validation model을 먼저 고정했다.
- `completed` Phase31~35 방향성 기록
  - Phase31 이후 Phase32~35를 robustness, paper ledger, final selection, post-selection 운영 guide로 본다.

## 2. 구현 완료 항목

- `completed` validation input contract 정의
  - 단일 후보 direct path와 proposal draft path를 같은 validation input 형태로 읽는다.
- `completed` validation result schema 정의
  - `validation_route`, `validation_score`, `hard_blockers`, `paper_tracking_gaps`, `review_gaps`, `next_action`, `component_rows`, `handoff_summary`를 반환한다.
- `completed` helper 함수 구현
  - `app/web/backtest_portfolio_proposal_helpers.py`에 Phase 31 validation helper를 추가했다.
- `completed` UI 배치
  - `Backtest > Portfolio Proposal`에서 단일 후보 direct path, 작성 중 proposal, 저장된 proposal 모두 Validation Pack으로 읽을 수 있다.
- `completed` component risk / overlap / concentration first pass
  - target weight, core anchor, max weight, family / benchmark / universe / factor overlap, Pre-Live / Data Trust / Real-Money 상태를 component table로 보여준다.
- `completed` 다음 단계 안내 요약
  - validation 결과의 `handoff_summary`가 다음 Robustness / Stress Validation Pack으로 넘길 수 있는지 표시한다.

## 3. Validation

- `completed` `python3 -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `completed` `.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `completed` 단일 후보 validation helper smoke
  - `READY_FOR_ROBUSTNESS_REVIEW`, score `10.0` 확인
- `completed` 임시 2개 후보 proposal validation helper smoke
  - 같은 계열 / benchmark overlap 때문에 `NEEDS_PORTFOLIO_RISK_REVIEW`, score `9.0` 확인
- `completed` QA 피드백 반영 smoke
  - target weight 0% 상태는 `Portfolio Construction` 안내로만 보이고, core anchor가 없을 때는 `Component Role` 보강 안내로 분리되는지 확인
- `pending` targeted manual validation

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` `WEB_BACKTEST_UI_FLOW.md` sync
- `completed` `SCRIPT_STRUCTURE_MAP.md` sync
- `completed` `FINANCE_COMPREHENSIVE_ANALYSIS.md` sync
- `completed` `README.md` sync
- `completed` roadmap / doc index / work log / question log sync
- `completed` Proposal Role / Target Weight 사용법과 저장 blocker 수정 안내 문구 보강

## 현재 판단

Phase 31은 implementation_complete / manual_qa_pending 상태다.
사용자는 `PHASE31_TEST_CHECKLIST.md` 기준으로 `Backtest > Portfolio Proposal`의 Validation Pack을 확인하면 된다.
Phase 30은 아직 manual QA pending 상태이므로, Phase 31 완료가 Phase 30 QA 완료를 대신하지 않는다.
