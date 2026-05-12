# Finance Flows

Status: Active
Last Verified: 2026-05-13

## Main User Flow

```text
Workspace > Ingestion
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Selected Portfolio Dashboard
```

## Backtest Selection Flow

| Step | What Happens | Main Files |
|---|---|---|
| Backtest Analysis | 단일 전략, compare, saved mix로 후보 source 생성 | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare.py` |
| Practical Validation | 후보 source를 12개 진단으로 검증 | `app/web/backtest_practical_validation*.py` |
| Final Review | 최종 select / hold / reject / re-review 판단 | `app/web/backtest_final_review*.py` |
| Selected Dashboard | 선정 이후 성과 재확인과 monitoring signal 확인 | `app/web/final_selected_portfolio_dashboard*.py` |

## Practical Validation Provider Flow

```text
Workspace > Ingestion
  -> ETF provider source map discovery
  -> ETF operability / holdings / exposure snapshot
  -> FRED macro market-context snapshot
  -> MySQL
  -> finance/loaders/provider.py / macro.py
  -> Practical Validation diagnostics
```

## Flow Rules

- Practical Validation result는 최종 투자 승인 기록이 아니다.
- Final Review decision도 broker order나 auto rebalance가 아니다.
- Selected Dashboard는 read-only monitoring surface다.
- 부족 provider data는 Practical Validation Provider Gaps에서 확인하고, 수집 가능한 항목은 ingestion job을 통해 보강한다.

## Detailed Flow Docs

| Need | Document |
|---|---|
| Backtest UI, history, saved replay, Practical Validation, Final Review 화면 흐름 | [BACKTEST_UI_FLOW.md](./BACKTEST_UI_FLOW.md) |
| 후보 생성부터 최종 선정 후 dashboard까지의 Portfolio Selection V2 흐름 | [PORTFOLIO_SELECTION_FLOW.md](./PORTFOLIO_SELECTION_FLOW.md) |
