# Portfolio Selection Flow

Status: Active
Last Verified: 2026-05-13

## Purpose

이 문서는 Backtest에서 후보를 만들고, Practical Validation에서 검증하고, Final Review에서 최종 판단한 뒤 Selected Portfolio Dashboard에서 사후 확인하는 현재 사용자 흐름을 설명한다.

예전의 긴 workflow redesign 문서는 구현 전 분석과 migration 계획이 섞여 있었다. 이 문서는 현재 제품에서 사용자가 실제로 따라야 하는 흐름만 남긴다.

## Current Flow

```text
Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Selected Portfolio Dashboard
```

| Step | Screen | What It Does | Durable Record |
|---|---|---|---|
| 1 | Backtest Analysis | 단일 전략 실행, compare, saved mix replay, 비중 조합을 수행하고 검증 후보 source를 만든다 | `PORTFOLIO_SELECTION_SOURCES.jsonl` |
| 2 | Practical Validation | 선택된 source를 12개 practical diagnostic으로 검증한다 | `PRACTICAL_VALIDATION_RESULTS.jsonl` |
| 3 | Final Review | 최종 select / hold / reject / re-review 판단과 사용자 최종 메모를 남긴다 | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` |
| 4 | Selected Portfolio Dashboard | 선정된 포트폴리오를 최신 기간과 가상 투자금 기준으로 다시 확인한다 | 사용자가 명시적으로 저장할 때만 monitoring log |

## Stage Ownership

| Stage | Owns | Does Not Own |
|---|---|---|
| Backtest Analysis | 후보 생성, 전략 비교, saved mix replay, 비중 조합 | 최종 판단 |
| Practical Validation | 실전 투입 전 검증, provider data gap, stress / sensitivity evidence | 투자 승인, 최종 사용자 메모 |
| Final Review | 최종 후보 판단과 최종 메모 저장 | 새 비중 실험, provider data 수집 |
| Selected Portfolio Dashboard | 선정 이후 성과 재확인, monitoring signal, optional allocation check | broker order, live approval, auto rebalance |

## Source Contract

Portfolio Selection V2의 기준 id는 `selection_source_id`다.

```text
PORTFOLIO_SELECTION_SOURCES
  -> PRACTICAL_VALIDATION_RESULTS
    -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2
      -> Selected Portfolio Dashboard read-only monitoring
```

기존 `registry_id`, Review Note, Pre-Live registry, Portfolio Proposal registry는 legacy compatibility로 남을 수 있지만, 현재 주 흐름의 필수 저장 단계는 아니다.

## User-Facing Rules

- 사용자는 Backtest Analysis에서 후보를 만들고 Practical Validation으로 보낸다.
- Practical Validation은 후보가 실전 검토에 충분한 근거를 갖는지 보여준다.
- `NOT_RUN`은 pass가 아니다. 데이터나 구현이 부족해 검증하지 못했다는 뜻이다.
- Final Review가 최종 판단 위치다. 중간 단계에서 최종 메모를 반복해서 저장하지 않는다.
- Selected Portfolio Dashboard는 선정 이후 상태 확인 화면이다. 주문이나 자동 리밸런싱을 만들지 않는다.

## Main Files

| Area | Files |
|---|---|
| Backtest stage routing | `app/web/backtest_common.py`, `app/web/backtest_workflow_routes.py`, `app/web/pages/backtest.py` |
| Backtest Analysis | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare.py` |
| Practical Validation | `app/web/backtest_practical_validation*.py` |
| Final Review | `app/web/backtest_final_review*.py` |
| Selected Dashboard | `app/web/final_selected_portfolio_dashboard*.py`, `app/web/runtime/final_selected_portfolios.py` |
| Selection V2 persistence | `app/web/runtime/portfolio_selection_v2.py` |

## Update Rules

이 문서는 아래가 바뀌면 갱신한다.

- Backtest 상단 stage가 바뀔 때
- selection source / validation result / final decision record 관계가 바뀔 때
- Practical Validation과 Final Review의 stage ownership이 바뀔 때
- Selected Portfolio Dashboard가 read-only monitoring 경계를 넘어서거나 저장 경계가 바뀔 때
