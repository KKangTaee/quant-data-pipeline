# Phase 36 Completion Summary

## 현재 상태

- 진행 상태: `implementation_complete`
- 검증 상태: `manual_qa_pending`

## 목적

Phase36은 Final Review에서 선정된 포트폴리오를 Operations 화면에서 다시 읽고,
사용자가 지정한 최신 기간으로 즉시 재검증하는 첫 운영 대시보드 phase다.
실제 또는 가정 보유 상태 기준 drift는 보조 고급 점검으로 둔다.

## 쉽게 말하면

Final Review에서 `투자 가능 후보`로 저장한 포트폴리오를 나중에 다시 찾고,
선정 당시의 전략 contract를 최신 날짜까지 다시 돌려 성과가 유지되는지 확인하는 기능을 만들었다.
목표 비중 대비 현재 보유 상태 차이는 Monitoring Playbook의 `Holding Drift Check`에서 추가로 확인한다.

## 이번 phase에서 실제로 완료된 것

### 1. Final Review selected row read model

- `app/web/runtime/final_selected_portfolios.py`를 추가했다.
- Final Review 최종 판단 파일인 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`을 읽는다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` 또는 `selected_practical_portfolio=true`인 row만 운영 대상으로 변환한다.
- target weight total, component 수, benchmark, evidence route, validation / robustness / paper observation 상태, operator next action을 dashboard row로 만든다.

쉽게 말하면:

- 새 저장소를 만들지 않고, Final Review가 이미 남긴 최종 선정 기록을 운영 화면에서 읽을 수 있게 했다.

### 2. Operations dashboard page

- `app/web/final_selected_portfolio_dashboard.py`를 추가했다.
- `app/web/final_selected_portfolio_dashboard_helpers.py`를 추가했다.
- `app/web/streamlit_app.py`의 Operations navigation에 `Selected Portfolio Dashboard`를 추가했다.
- summary cards, wrapping source boundary cards, compact selected portfolio table, responsive filter, Snapshot / Portfolio Blueprint, tabbed Performance Recheck, Monitoring Playbook, audit expander를 제공한다.

쉽게 말하면:

- 최종 선정 포트폴리오 목록과 상세를 Operations에서 다시 열고, 최신 기간으로 바로 재검증할 수 있다.

### 3. Performance Recheck

- selected component의 `registry_id`로 Current Candidate Registry의 저장 contract를 찾는다.
- 사용자가 `Recheck start`, `Recheck end`, `Virtual capital`을 입력하면 같은 contract를 해당 기간으로 replay한다.
- 기본 시작일은 원래 검증 시작일, 기본 종료일은 DB latest market date다.
- portfolio value, total return, CAGR, MDD, benchmark spread를 표시한다.
- 원래 baseline CAGR / MDD와 recheck CAGR / MDD 변화를 비교한다.
- 결과는 `Summary`, `Equity Curve`, `Result Table`, `What Changed`, `Contribution`, `Extremes` tab으로 나누어 보여준다.
- component contribution과 strongest / weakest period는 각각 전용 tab에서 확인한다.
- 이 재검증은 새 decision / proposal / alert row를 저장하지 않는다.

쉽게 말하면:

- 선정 당시 좋았던 포트폴리오를 오늘 기준 최신 데이터까지 다시 돌려 보고, 여전히 좋아 보이는지 바로 확인할 수 있다.

### 4. 실행 경계 유지

- dashboard의 `Live Approval`, `Broker Order`, `Auto Rebalance` 버튼은 disabled 상태다.
- Phase36은 실제 주문, broker API, 자동매매, 투자금 자동 배분을 만들지 않는다.

쉽게 말하면:

- 이 화면은 운영 관찰 대시보드이지 주문 실행 화면이 아니다.

### 5. Monitoring Playbook / Allocation Check

- operator context는 `Monitoring Playbook`으로 바꿔 선정 근거, 관찰 기준, Holding Drift Check, Execution Boundary를 같은 흐름에서 보여준다.
- `Trigger Board`는 Performance Recheck와 Holding Drift Check의 최신 상태를 읽어 `Clear`, `Watch`, `Breached`, `Needs Input`으로 운영 trigger를 번역한다.
- 원본 operator reason / constraints / next action / trigger list는 `Original Operator Notes` 접힘 영역에서 확인한다.
- target allocation은 Snapshot의 `Portfolio Blueprint`에 배치하고, 실제 또는 가상 보유 상태 점검은 `Holding Drift Check` tab으로 분리했다.
- drift check는 기본 화면이 아니라 운영 점검 tab으로 이동했다.
- component별 현재 비중을 수동 입력하는 계약을 유지한다.
- component별 현재 평가금액을 입력하면 전체 평가금액 대비 current weight로 변환한다.
- component별 holding symbol, shares, current price를 입력하면 shares x price 기준 current value와 current weight로 변환한다.
- shares x price 입력에서는 선택적으로 DB latest close를 불러와 현재가 입력을 보조한다.
- target weight와 current weight의 차이를 drift로 계산한다.
- `Rebalance threshold`, `Watch threshold`, `Total tolerance`를 UI에서 조정할 수 있다.
- route는 `DRIFT_ALIGNED`, `DRIFT_WATCH`, `REBALANCE_NEEDED`, `DRIFT_INPUT_INCOMPLETE`로 읽는다.
- `Drift Alert / Review Trigger Preview`에서 drift 결과를 `운영 경고 없음`, `관찰 경고`, `리밸런싱 검토 경고`, `입력 확인 경고`로 다시 읽는다.
- Final Review에 남긴 review trigger를 drift 경고와 함께 보여준다.

쉽게 말하면:

- 현재 계좌를 연결하지 않아도, 사용자가 현재 비중이나 평가금액, 보유 수량과 가격을 입력하면 목표 비중에서 얼마나 벗어났는지 `Holding Drift Check`에서 바로 볼 수 있다.
- 이 결과도 주문 지시가 아니라 리밸런싱 검토 신호다.
- drift가 커졌을 때 어떤 review trigger를 같이 봐야 하는지 한 화면에서 확인할 수 있다.

### 6. 문서 동기화

- Phase36 plan, TODO, first work unit, checklist, completion, next phase preparation을 정리했다.
- roadmap / doc index / code analysis / high-level finance map을 새 Operations dashboard 기준으로 맞췄다.

## 아직 남아 있지만 closeout blocker는 아닌 것

- 실제 account holding 자동 연결
- 리밸런싱 주문 초안
- alert registry 저장 / 자동 알림 / trigger breach 자동화

쉽게 말하면:

- 이번 phase는 선정 포트폴리오를 운영 화면으로 옮기고, 사용자가 지정한 최신 기간으로 performance recheck를 실행하는 단계다.
- Drift와 DB latest close는 실제 보유 상태 확인을 위한 보조 기능이다. 실제 계좌 보유 수량 자동 읽기, alert persistence, 주문 workflow는 다음 phase로 넘긴다.

## closeout 판단

Phase36 구현은 implementation_complete / manual_qa_pending 상태다.

사용자는 `.note/finance/phases/phase36/PHASE36_TEST_CHECKLIST.md`로 `Operations > Selected Portfolio Dashboard`를 확인하면 된다.
