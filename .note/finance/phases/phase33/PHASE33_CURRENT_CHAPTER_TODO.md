# Phase 33 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 33의 목표는 Phase 32를 통과한 후보나 Portfolio Proposal을 바로 최종 선정하는 것이 아니다.
실제 돈을 넣기 전에 paper tracking 조건을 append-only ledger로 남기고,
Phase 34 final selection decision pack이 읽을 수 있는 관찰 기록 기반을 만드는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 33 전체 목표 | Paper Portfolio Tracking Ledger를 만든다 | `implementation_complete` |
| 첫 번째 작업 | Paper ledger row 계약과 저장소 경계 정의 | `completed` |
| 두 번째 작업 | Paper ledger draft / save UI 추가 | `completed` |
| 세 번째 작업 | 저장된 paper ledger review surface 추가 | `completed` |
| 네 번째 작업 | Phase 34 final selection handoff 정리 | `completed` |

## 1. Phase kickoff

- `completed` Phase 32 closeout 확인
  - Phase 32는 `complete / manual_qa_completed` 상태다.
- `completed` Phase 32 next phase preparation 확인
  - Phase 33 방향은 `Paper Portfolio Tracking Ledger`다.
- `completed` Phase 33 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase33/`이다.

## 2. 첫 번째 작업 준비 항목

- `completed` paper ledger row schema 정의
  - source type, source id, tracking start date, target weights, benchmark, review cadence, triggers를 정한다.
- `completed` append-only 저장소 경계 정의
  - 예상 저장소는 `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`이다.
- `completed` Phase 32 handoff -> paper ledger draft 변환 기준 정의
  - `phase33_handoff.requirements`를 ledger draft의 최소 입력으로 사용한다.

## 3. 두 번째 작업

- `completed` `app/web/runtime/paper_portfolio_ledger.py` 추가
  - paper ledger JSONL path / append / load helper를 proposal registry와 분리했다.
- `completed` Validation Pack 아래 `Paper Tracking Ledger Draft` 추가
  - preview만으로는 저장되지 않고, `Save Paper Tracking Ledger`를 눌러야 저장된다.
- `completed` 작성 중 proposal 저장 경계
  - 아직 proposal registry에 저장되지 않은 작성 중 proposal은 paper ledger preview는 가능하지만 save는 차단한다.

## 4. 세 번째 작업

- `completed` 저장된 paper ledger review surface 추가
  - `저장된 Paper Tracking Ledger 확인`에서 ledger list / component / trigger / raw detail을 확인한다.
- `completed` source / status / benchmark / review cadence / weight total을 요약한다.

## 5. 네 번째 작업

- `completed` Phase34 final selection handoff 계산
  - `READY_FOR_FINAL_SELECTION_REVIEW`
  - `NEEDS_PAPER_TRACKING_REVIEW`
  - `BLOCKED_FOR_FINAL_SELECTION_REVIEW`
- `completed` Phase34 handoff를 저장 row와 review surface에서 같이 보여준다.

## 6. Validation

- `completed` `.venv/bin/python -m py_compile app/web/runtime/paper_portfolio_ledger.py app/web/runtime/__init__.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `completed` `python3 -m py_compile app/web/runtime/paper_portfolio_ledger.py app/web/runtime/__init__.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `completed` ledger helper smoke
- `pending` user manual QA

## 7. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` second / third / fourth work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` Backtest UI flow / script map / operations guide / README / AGENTS sync

## 현재 판단

Phase 33은 implementation_complete / manual_qa_pending 상태다.
첫 번째부터 네 번째 작업까지 구현과 문서 동기화가 끝났고,
이제 사용자가 `PHASE33_TEST_CHECKLIST.md` 기준으로 manual QA를 진행하면 된다.
