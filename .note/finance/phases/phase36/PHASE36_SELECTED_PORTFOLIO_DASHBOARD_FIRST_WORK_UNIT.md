# Phase36 Selected Portfolio Dashboard First Work Unit

## 목적

Phase36 첫 번째 작업은 Final Review에서 선정된 포트폴리오를 Operations 화면에서 읽을 수 있게 만드는 것이다.

## 쉽게 말하면

Final Review에서 `투자 가능 후보`로 저장한 포트폴리오를 나중에 다시 찾아보려면, Backtest workflow가 아니라 운영 화면에 모아 보여야 한다.

## 왜 필요한가

Phase35는 Final Review를 마지막 판단 단계로 고정했다.
따라서 Phase36이 Final Review 안에 새 단계나 새 저장 버튼을 추가하면 같은 문제를 다시 만든다.

이 작업은 역할을 나눈다.

- Final Review: 최종 판단을 저장한다.
- Selected Portfolio Dashboard: 저장된 최종 선정 포트폴리오를 운영 관점으로 읽는다.

## 구현 범위

### 새 read model

- 파일:
  - `app/web/runtime/final_selected_portfolios.py`
- 역할:
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`을 읽는다.
  - `decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO` 또는 `selected_practical_portfolio == true` row만 dashboard 대상으로 고른다.
  - target weight, benchmark, evidence, paper observation, operator next action을 dashboard row로 변환한다.

### 새 Operations page

- 파일:
  - `app/web/final_selected_portfolio_dashboard.py`
  - `app/web/final_selected_portfolio_dashboard_helpers.py`
- 역할:
  - summary card
  - selected portfolio table
  - status / source / benchmark filter
  - 선택 row 상세
  - target allocation table
  - evidence checks
  - current weight / drift check
  - disabled Live Approval / Broker Order / Auto Rebalance boundary

### navigation

- 파일:
  - `app/web/streamlit_app.py`
- 역할:
  - `Operations > Selected Portfolio Dashboard` page를 추가한다.

## 상태 계산

Phase36 first pass status:

| status | 의미 |
|---|---|
| `normal` | selected row, active component, target weight 100%, blocker 없음 |
| `watch` | selected row지만 evidence / validation / robustness / paper route가 보수적으로 볼 필요가 있음 |
| `rebalance_needed` | 후속 phase에서 current weight / drift 계산이 들어오면 사용할 상태 |
| `re_review_needed` | evidence 또는 paper observation blocker가 남아 있음 |
| `blocked` | selected row가 아니거나 component / target weight가 운영 대상으로 불충분함 |

## 이번 작업에서 제외한 것

- 새 registry 저장
- 현재 가격 자동 조회
- 실제 보유 수량 / 계좌 연결
- 리밸런싱 주문 초안
- broker API
- 자동매매

## 완료 판단

이 작업은 `Operations > Selected Portfolio Dashboard`에서 최종 선정 포트폴리오 목록, 상세 운영 기준, 수동 현재 비중 기반 drift 판정을 읽을 수 있으면 완료로 본다.
