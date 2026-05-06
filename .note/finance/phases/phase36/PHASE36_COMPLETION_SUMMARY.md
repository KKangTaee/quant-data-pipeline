# Phase 36 Completion Summary

## 현재 상태

- 진행 상태: `implementation_complete`
- 검증 상태: `manual_qa_pending`

## 목적

Phase36은 Final Review에서 선정된 포트폴리오를 Operations 화면에서 다시 읽는 첫 운영 대시보드 phase다.

## 쉽게 말하면

Final Review에서 `투자 가능 후보`로 저장한 포트폴리오를 나중에 다시 찾고, 구성 비중과 검증 근거, 다음 행동을 한 화면에서 보는 기능을 만들었다.

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
- summary cards, source 설명, selected portfolio table, filter, selected row detail, target allocation table, evidence checks, raw JSON expander를 제공한다.

쉽게 말하면:

- 최종 선정 포트폴리오 목록과 상세를 Operations에서 다시 열 수 있다.

### 3. 실행 경계 유지

- dashboard의 `Live Approval`, `Broker Order`, `Auto Rebalance` 버튼은 disabled 상태다.
- Phase36은 실제 주문, broker API, 자동매매, 투자금 자동 배분을 만들지 않는다.

쉽게 말하면:

- 이 화면은 운영 관찰 대시보드이지 주문 실행 화면이 아니다.

### 4. 문서 동기화

- Phase36 plan, TODO, first work unit, checklist, completion, next phase preparation을 정리했다.
- roadmap / doc index / code analysis / high-level finance map을 새 Operations dashboard 기준으로 맞췄다.

## 아직 남아 있지만 closeout blocker는 아닌 것

- current price 기반 current weight 계산
- target vs current weight drift 계산
- `rebalance_needed` 자동 판단
- 리밸런싱 주문 초안
- risk alert / trigger breach 자동화

쉽게 말하면:

- 이번 phase는 선정 포트폴리오를 운영 화면으로 옮겨 보는 첫 단계다.
- 실제 현재 비중과 리밸런싱 필요 여부는 current price / holding 계약이 있어야 하므로 다음 phase로 넘긴다.

## closeout 판단

Phase36 first pass는 implementation_complete / manual_qa_pending 상태다.

사용자는 `.note/finance/phases/phase36/PHASE36_TEST_CHECKLIST.md`로 `Operations > Selected Portfolio Dashboard`를 확인하면 된다.
