# Monitoring Snapshot / Review Loop V2 Plan

Status: Active
Owner skill: finance-backtest-web-workflow
Started: 2026-06-08

## Goal

`Operations > Portfolio Monitoring`에서 사용자가 scenario update 결과를 확인한 뒤 명시적으로 monitoring snapshot / review record를 저장하고, 이후 latest / previous snapshot과 current scenario의 차이를 볼 수 있게 한다.

## 이걸 하는 이유?

현재 Portfolio Monitoring은 Final Review selected 후보를 사후 관찰하는 제품 흐름의 끝단이지만, scenario result가 주로 session state에 머문다. 선정 이후 benchmark delta, drift, provider freshness, review signal, open issue, operator note, next review date가 append-only compact evidence로 쌓이면 "좋은 백테스트 후보"가 아니라 "지속적으로 검토되는 후보"로 제품 경험이 강화된다.

## Scope

- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` append-only snapshot schema / helper.
- Portfolio Monitoring scenario result에서 compact snapshot evidence 생성.
- latest snapshot / previous snapshot / current scenario comparison read model.
- Portfolio Monitoring UI의 explicit `Save Monitoring Snapshot` / `Record Review` action.
- No-live approval / broker order / account sync / auto rebalance boundary copy.
- Focused tests, compile checks, diff hygiene, 가능한 Browser QA.
- Durable docs sync for changed flow / file ownership.

## Out Of Scope

- 새 strategy 개발 또는 Risk-On Momentum governance 연결.
- live approval, broker order, account sync, auto rebalance.
- monitoring log 자동 저장.
- `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`를 monitoring evidence source-of-truth로 변경.
- full holdings, full macro series, raw provider response JSONL 저장.
- Candidate Review / Portfolio Proposal / Candidate Library / Run History 삭제.
- generated run history, screenshots, temp artifacts stage / commit.

## Roadmap

| 차수 | 목적 | 바뀔 화면 / 파일 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차 | Snapshot schema / append helper / read model 구현 | `app/runtime/portfolio_selection_v2.py`, `app/runtime/final_selected_portfolios.py`, focused tests | explicit snapshot row를 append-only로 저장하고 다시 읽어 latest / previous / comparison을 만들 수 있음 | 2차 UI 저장 action이 이 helper를 호출 |
| 2차 | Portfolio Monitoring UI에 저장 action과 history / latest comparison 연결 | `app/web/final_selected_portfolio_dashboard.py`, 필요한 helper | scenario update 뒤 사용자가 명시 버튼으로 snapshot을 저장하고 latest / previous / current scenario 차이를 확인 | 3차 QA와 docs sync |
| 3차 | 검증, Browser QA, 문서 정렬, commit | docs flow / project map / task docs / root logs | focused tests, py_compile, `git diff --check`, 가능한 Browser QA 통과 또는 미실행 사유 기록 | 다음 후보는 Strategy Promotion Contract 또는 Robustness Registry |

## Stop Condition

사용자가 Portfolio Monitoring Scenario를 실행한 뒤 명시적으로 snapshot / review를 저장할 수 있고, 저장된 row가 append-only로 다시 읽히며, Portfolio Monitoring에서 최신 저장 snapshot과 이전 snapshot, 현재 session scenario의 주요 변화가 보이면 이번 task를 종료한다.
