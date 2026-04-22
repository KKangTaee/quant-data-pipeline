# Phase 28 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 현재 목표

Phase 28의 목표는 새 전략을 급하게 늘리는 것이 아니다.
현재 Backtest 화면에 있는 전략 family들이 어떤 기능을 지원하고,
어떤 차이는 아직 검토 대상인지 사용자가 바로 이해할 수 있게 만드는 것이다.

## 1. Strategy Capability Snapshot

- `completed` Single Strategy capability snapshot 추가
  - strategy 선택 직후 해당 전략의 cadence, data trust, Real-Money/Guardrail, history/replay 지원 범위를 보여준다.
- `completed` Compare strategy box capability snapshot 추가
  - compare에서 선택한 각 전략 박스 안에 같은 snapshot을 표시한다.
- `completed` annual / quarterly / GRS 차이 설명
  - annual strict는 가장 성숙한 Real-Money/Guardrail surface, quarterly는 prototype, GRS는 price-only ETF 전략임을 구분한다.

## 2. 다음 작업 후보

- `completed` history / load-into-form / run-again parity 점검
  - annual, quarterly, GRS의 핵심 설정값이 다시 열었을 때 빠지지 않는지 확인한다.
  - `History Replay / Load Parity Snapshot`으로 선택한 history record의 저장 상태를 먼저 볼 수 있게 했다.
- `completed` saved portfolio replay parity 점검
  - compare에서 만든 strategy override가 saved replay에서 같은 의미로 복원되는지 본다.
  - `Saved Portfolio Replay / Load Parity Snapshot`으로 저장 포트폴리오의 전략 목록, weight, date alignment, strategy override 저장 상태를 볼 수 있게 했다.
- `pending` Data Trust Summary 확장 범위 결정
  - 단일 실행 외 compare / saved replay에서 데이터 신뢰성 정보를 어디까지 보여줄지 정한다.
- `pending` Real-Money / Guardrail parity 결정
  - quarterly와 price-only ETF 전략에 어떤 검증 surface를 붙일지 정한다.

## 3. Validation

- `completed` `python3 -m py_compile app/web/pages/backtest.py app/web/runtime/history.py`
- `completed` `.venv` import smoke + history parity helper smoke
- `completed` finance refinement hygiene check
- `completed` `git diff --check`
- `pending` targeted manual UI validation
- `completed` generated history files unstaged 확인

## 4. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` Phase 28 plan / TODO 작성
- `completed` first work-unit 문서 생성
- `completed` second work-unit 문서 생성
- `completed` third work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` code_analysis sync

## 현재 판단

Phase 28은 active 상태다.
첫 작업 단위인 `Strategy Capability Snapshot`은 구현됐고,
두 번째 작업 단위로 history record의 재실행 / form 복원 가능성을 확인하는
`History Replay / Load Parity Snapshot`도 추가됐다.
세 번째 작업 단위로 saved portfolio의 replay / load 가능성을 확인하는
`Saved Portfolio Replay / Load Parity Snapshot`도 추가됐다.
다음 판단은 Data Trust Summary 확장 범위와 Real-Money / Guardrail parity 결정을 어디까지 다룰지다.
