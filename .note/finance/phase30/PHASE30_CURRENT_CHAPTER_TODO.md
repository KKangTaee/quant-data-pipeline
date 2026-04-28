# Phase 30 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 현재 목표

Phase 30의 목표는 후보를 바로 투자 승인으로 확정하는 것이 아니다.
Phase 29에서 만든 후보 검토 workflow를 바탕으로,
후보 묶음을 포트폴리오 제안과 paper / pre-live monitoring surface로 연결하는 것이다.

## 작업 단위 진행 순서

Phase 30 전체 목표와 첫 작업을 구분해서 읽는다.

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 30 전체 목표 | 후보 묶음을 Portfolio Proposal / Pre-Live Monitoring으로 연결한다 | `active` |
| 첫 번째 작업 | 사용 흐름 재정렬 + `backtest.py` 리팩토링 경계 검토 | `completed` |
| 두 번째 작업 | Portfolio Proposal UI 전에 proposal row 계약 정의 | `completed` |
| 이후 작업 후보 | 실제 모듈 분리 또는 Proposal Draft UI / persistence 구현 | `pending` |

첫 작업은 기능 구현이 아니라
사용 흐름 재정렬과 `backtest.py` 리팩토링 경계 검토였다.

현재 두 번째 작업은 Portfolio Proposal UI 구현 전에
proposal row가 무엇을 담아야 하는지 계약을 먼저 정의하는 것이다.

## 1. 사용 흐름 재정렬

- `completed` Phase 30 문서 bundle 생성
  - portfolio proposal phase를 열되, 첫 작업을 product-flow reorientation으로 둔다.
- `completed` Guide의 `테스트에서 상용화 후보 검토까지 사용하는 흐름` 갱신
  - Candidate Draft / Candidate Review Note / Current Candidate Registry / Pre-Live / Portfolio Proposal의 위치를 한 흐름으로 설명한다.
- `completed` Phase 30 first work-unit 문서 작성
  - 사용 흐름 재정렬과 리팩토링 경계 검토의 목적을 기록한다.

## 2. `backtest.py` 리팩토링 경계 검토

- `completed` 현재 `backtest.py` 책임 범위 정리
  - Single Strategy, Compare, Weighted / Saved Portfolio, History, Candidate Review, Pre-Live, registry helper가 한 파일에 섞여 있음을 기록한다.
- `completed` 점진 분리 후보 정리
  - Candidate Review / Pre-Live / History / Saved Portfolio / chart and result display / strategy forms 순서로 분리 후보를 정한다.
- `pending` 실제 코드 분리는 별도 작업 단위에서 진행
  - 이번 첫 작업은 경계 검토와 문서화까지다.

## 3. 이후 구현 후보

- `completed` Portfolio Proposal row 계약 정의
  - 후보 묶음의 목적, 후보 역할, 비중 근거, risk constraints, evidence snapshot, blocker, operator decision 필드를 정한다.
- `completed` Portfolio Proposal 저장소 위치와 append-only 정책 검토
  - 향후 후보 저장 위치는 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`로 제안하되, 이번 작업에서는 파일 생성 / append 구현을 하지 않는다.
- `pending` Proposal Review UI 초안
- `pending` Pre-Live monitoring surface 연결

## 4. Validation

- `completed` `python3 -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py`
- `completed` finance refinement hygiene check
- `completed` `git diff --check`
- `pending` targeted manual validation

## 5. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` second work-unit 문서 생성
- `completed` `WEB_BACKTEST_UI_FLOW.md` sync
- `completed` roadmap / doc index / work log / question log sync

## 현재 판단

Phase 30은 active 상태로 열었지만, 아직 Portfolio Proposal 기능 구현 단계는 아니다.
먼저 사용자가 전체 흐름을 다시 이해할 수 있게 만들고,
그 흐름에 맞춰 `backtest.py`의 점진 리팩토링 경계를 정했다.
두 번째 작업으로 Portfolio Proposal row 계약을 정의했다.
다음 작업에서는 실제 모듈 분리 또는 Proposal Draft UI / persistence 구현 중 하나를 선택한다.
