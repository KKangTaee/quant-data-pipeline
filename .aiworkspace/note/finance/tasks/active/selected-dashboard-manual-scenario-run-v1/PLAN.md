# Selected Dashboard Manual Scenario Run V1

## 이걸 하는 이유?

Selected Portfolio Dashboard에서 전략을 추가하거나 설정을 바꿀 때 하단 개별 전략 상세가 eager render되면서 사용자가 `포트폴리오 시나리오 실행`을 누르기 전에 재검증이 도는 것처럼 느껴진다.
Monitoring Scenario는 사용자가 명시적으로 실행 버튼을 눌렀을 때만 업데이트되어야 하며, 전략 추가 / 설정 저장은 saved setup만 바꿔야 한다.

## Scope

- `app/web/final_selected_portfolio_dashboard.py`
- Selected Dashboard section 2 strategy add / slot edit feedback
- Selected Dashboard section 3 portfolio-wide scenario and individual strategy detail rendering
- Durable docs / root handoff logs after implementation

## Out Of Scope

- New background worker / async job queue
- DB schema or strategy runtime rewrite
- Broker, account, live approval, auto rebalance
- Section 4 Monitoring Signals redesign

## Acceptance

- Adding a strategy does not execute portfolio-wide or per-strategy Performance Recheck.
- Strategy slot edits mark previous scenario output stale instead of silently reusing it as fresh.
- Individual strategy detail renders only for the selected strategy, avoiding eager rendering of all strategy tabs.
- Portfolio-wide scenario still runs only from `포트폴리오 시나리오 실행`.
- Browser QA confirms no Streamlit traceback on the dashboard.
