# Finance Flows

Status: Active
Last Verified: 2026-06-01

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
| Practical Validation | 후보 source를 12개 진단과 module gate로 검증하고, Gate 미통과 저장-only row는 audit trail로만 남긴다 | `app/web/backtest_practical_validation*.py` |
| Final Review | Practical Validation Gate를 통과한 후보만 source picker에 표시하고 최종 select / hold / reject / re-review 판단 | `app/web/backtest_final_review*.py` |
| Selected Dashboard | 선정 이후 성과 재확인과 read-only monitoring / recheck signal 확인 | `app/web/final_selected_portfolio_dashboard*.py` |

## Practical Validation Provider Flow

```text
Workspace > Ingestion
  -> ETF provider source map discovery
  -> ETF operability / holdings / exposure snapshot
  -> FRED macro market-context snapshot
  -> symbol lifecycle evidence
     (SEC Form 25 actual delisting evidence,
      Nasdaq current listing snapshot,
      SEC CIK / ticker cross-check,
      computed repeated-observation summary)
  -> MySQL
  -> finance/loaders/provider.py / macro.py / universe.py
  -> Practical Validation diagnostics
```

## Flow Rules

- Practical Validation result는 최종 투자 승인 기록이 아니다.
- Practical Validation의 `검증 결과 저장(기록용)`은 Final Review 후보 등록이 아니다. Final Review에는 Gate를 통과한 result만 표시한다.
- Practical Validation의 최신 runtime replay 결과는 현재 세션에서 사용자가 직접 실행한 뒤에만 표시한다.
- Final Review decision도 broker order나 auto rebalance가 아니다.
- Selected Dashboard는 read-only monitoring surface이며 monitoring log 자동 저장, live approval, broker order, auto rebalance를 하지 않는다.
- 부족 provider data는 Practical Validation Provider Gaps에서 확인하고, 수집 가능한 항목은 ingestion job을 통해 보강한다.
- Ingestion의 current listing snapshot, SEC identity cross-check, computed snapshot lifecycle row는 survivorship PASS 근거가 아니다. Form 25 delisting row도 delisting evidence이며, Form 25 부재를 active listing proof로 해석하지 않는다.

## Detailed Flow Docs

| Need | Document |
|---|---|
| Backtest UI, history, saved replay, Practical Validation, Final Review 화면 흐름 | [BACKTEST_UI_FLOW.md](./BACKTEST_UI_FLOW.md) |
| Backtest Analysis 1단계 closeout 현재 상태 | [BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md](./BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md) |
| 후보 생성부터 최종 선정 후 dashboard까지의 Portfolio Selection V2 흐름 | [PORTFOLIO_SELECTION_FLOW.md](./PORTFOLIO_SELECTION_FLOW.md) |
| Final Review selected-route waiver 허용 조건 | [STRUCTURED_WAIVER_POLICY.md](./STRUCTURED_WAIVER_POLICY.md) |
