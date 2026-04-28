# Phase 30 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

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
| 세 번째 작업 | registry JSONL I/O helper를 runtime module로 분리 | `completed` |
| 네 번째 작업 | Portfolio Proposal Draft UI / persistence 구현 | `completed` |
| 다섯 번째 작업 | Portfolio Proposal Monitoring Review surface 구현 | `completed` |
| 여섯 번째 작업 | Portfolio Proposal Pre-Live Feedback surface 구현 | `completed` |
| 일곱 번째 작업 | Portfolio Proposal Paper Tracking Feedback surface 구현 | `completed` |
| 이후 작업 후보 | Candidate Review / Pre-Live / History / Saved Portfolio 추가 모듈 분리 | `deferred_special_refactor_task` |

첫 작업은 기능 구현이 아니라
사용 흐름 재정렬과 `backtest.py` 리팩토링 경계 검토였다.

현재 일곱 번째 작업까지 완료되어, 저장된 Portfolio Proposal draft를 최신 Pre-Live 상태와 paper tracking 성과 snapshot 관점에서 다시 읽을 수 있다.

## 1. 사용 흐름 재정렬

- `completed` Phase 30 문서 bundle 생성
  - portfolio proposal phase를 열되, 첫 작업을 product-flow reorientation으로 둔다.
- `completed` Guide의 `테스트에서 상용화 후보 검토까지 사용하는 흐름` 갱신
  - Candidate Draft / Candidate Review Note / Current Candidate Registry / Pre-Live / Portfolio Proposal의 위치를 한 흐름으로 설명한다.
- `completed` Guide의 `단계 통과 기준` 분리
  - `4단계에서 5단계로 넘어가는 최소 기준`을 단계형 흐름 본문에서 분리해 `Guides > 단계 통과 기준`에 두었다.
  - `Promotion Decision != hold`, `Deployment != blocked`, 핵심 blocker 없음이 Compare 진입 기준이며 투자 승인 기준이 아니라는 점을 명시했다.
- `completed` Guide의 `GTAA Risk-Off 후보군 보는 법` 보강
  - `Defensive Tickers`와 GTAA universe의 교집합만 실제 fallback 후보로 쓰인다는 점을 manual QA 보조 설명으로 추가했다.
- `completed` Real-Money `5단계 Compare 진입 평가` 박스 추가
  - `Real-Money > 현재 판단`에서 10점 만점의 Compare 진입 점수, 판정, 다음 행동, 점수 계산 기준을 먼저 보여준다.
- `completed` Phase 30 first work-unit 문서 작성
  - 사용 흐름 재정렬과 리팩토링 경계 검토의 목적을 기록한다.

## 2. `backtest.py` 리팩토링 경계 검토와 첫 코드 분리

- `completed` 현재 `backtest.py` 책임 범위 정리
  - Single Strategy, Compare, Weighted / Saved Portfolio, History, Candidate Review, Pre-Live, registry helper가 한 파일에 섞여 있음을 기록한다.
- `completed` 점진 분리 후보 정리
  - Candidate Review / Pre-Live / History / Saved Portfolio / chart and result display / strategy forms 순서로 분리 후보를 정한다.
- `completed` registry JSONL I/O helper 첫 분리
  - `app/web/runtime/candidate_registry.py`를 추가하고 current candidate / candidate review note / pre-live registry read / append helper를 옮겼다.
- `pending` Candidate Review / Pre-Live / History / Saved Portfolio의 추가 모듈 분리
  - 이번 코드 분리는 전체 리팩토링이 아니라 첫 작은 helper split이다.

## 3. 이후 구현 후보

- `completed` Portfolio Proposal row 계약 정의
  - 후보 묶음의 목적, 후보 역할, 비중 근거, risk constraints, evidence snapshot, blocker, operator decision 필드를 정한다.
- `completed` Portfolio Proposal 저장소 위치와 append-only persistence 구현
  - 저장 위치는 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이다.
  - 첫 row를 저장할 때 파일이 생성되며, `app/web/runtime/portfolio_proposal.py`가 append / load helper를 담당한다.
- `completed` Proposal Draft UI 초안
  - `Backtest > Portfolio Proposal`에서 current candidate 여러 개를 골라 proposal objective, role, target weight, weight reason, operator decision을 저장 전 확인한다.
- `completed` Proposal Monitoring Review surface
  - 저장된 proposal draft를 monitoring state, blocker, review gap, component table, operator decision 관점으로 다시 읽는다.
- `completed` Pre-Live Feedback surface
  - 저장된 proposal snapshot과 현재 Pre-Live registry active record를 비교해 status drift, review overdue, feedback gap을 확인한다.
- `completed` Paper tracking performance feedback loop
  - 저장된 proposal evidence snapshot과 현재 Pre-Live result snapshot의 CAGR / MDD를 비교해 성과 악화, missing result, paper tracking 미진입 gap을 확인한다.
- `deferred` Candidate Review / Pre-Live / History / Saved Portfolio의 추가 `backtest.py` 모듈 분리
  - Phase 30 QA와 섞지 않고 별도 special refactor task에서 다룬다.

## 4. Validation

- `completed` `python3 -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py`
- `completed` `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py`
- `completed` portfolio proposal runtime import smoke
- `completed` current candidate registry validate
- `completed` pre-live candidate registry validate
- `completed` finance refinement hygiene check
- `completed` `git diff --check`
- `pending` targeted manual validation

## 5. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` second work-unit 문서 생성
- `completed` third work-unit 문서 생성
- `completed` fourth work-unit 문서 생성
- `completed` fifth work-unit 문서 생성
- `completed` sixth work-unit 문서 생성
- `completed` seventh work-unit 문서 생성
- `completed` Portfolio Proposal registry operations guide 생성
- `completed` `WEB_BACKTEST_UI_FLOW.md` sync
- `completed` roadmap / doc index / work log / question log sync
- `completed` manual walkthrough support guide sync
  - `GTAA Risk-Off 후보군 보는 법` Guide와 Phase 30 checklist 항목을 추가했다.
  - 4단계 pass 기준을 별도 `단계 통과 기준` Guide와 Phase 30 checklist에 추가했다.
  - Real-Money Compare 진입 평가 UI와 code flow 문서를 추가했다.

## 현재 판단

Phase 30은 implementation_complete / manual_qa_pending 상태이며, Portfolio Proposal Draft UI / persistence부터 paper tracking feedback까지 구현된 상태다.
먼저 사용자가 전체 흐름을 다시 이해할 수 있게 만들고,
그 흐름에 맞춰 `backtest.py`의 점진 리팩토링 경계를 정했다.
두 번째 작업으로 Portfolio Proposal row 계약을 정의했다.
세 번째 작업으로 registry JSONL I/O helper를 `app/web/runtime/candidate_registry.py`로 분리했다.
네 번째 작업으로 `Backtest > Portfolio Proposal`의 draft 작성 / 저장 / registry inspect 흐름을 추가했다.
다섯 번째 작업으로 `Monitoring Review` tab을 추가해 저장된 proposal draft를 다시 점검할 수 있게 했다.
여섯 번째 작업으로 `Pre-Live Feedback` tab을 추가해 proposal snapshot과 현재 Pre-Live 상태를 비교할 수 있게 했다.
일곱 번째 작업으로 `Paper Tracking Feedback` tab을 추가해 proposal 저장 당시 성과와 최신 Pre-Live result snapshot의 CAGR / MDD 변화를 비교할 수 있게 했다.
이제 사용자가 Phase 30 checklist로 targeted manual QA를 진행하면 된다.
Candidate Review / Pre-Live / History / Saved Portfolio 추가 모듈 분리는 Phase 30 이후 별도 special refactor task로 분리한다.
