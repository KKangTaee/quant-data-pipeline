# Strategy Promotion Contract Handoff Design

Status: Draft
Created: 2026-06-08

## Current Flow Audit

현재 제품 workflow는 아래 durable chain을 중심으로 동작한다.

```text
Backtest Analysis
  -> PORTFOLIO_SELECTION_SOURCES.jsonl
  -> Practical Validation
  -> PRACTICAL_VALIDATION_RESULTS.jsonl
  -> Final Review
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl
  -> Operations > Portfolio Monitoring
```

Backtest Analysis는 후보 source 생성과 1차 readiness를 맡고, Practical Validation은 source traits 기반 module gate와 compact evidence를 만든다. Final Review는 selected-route gate를 통과한 후보만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장하고, Portfolio Monitoring은 저장된 selected row를 read-only monitoring 대상으로 읽는다.

## Gap

`reports/backtests/TEMPLATE.md`는 개별 backtest report 작성에는 적합하지만, `backtest-dev` 결과물을 제품 workflow로 승격할 때 필요한 계약 필드가 부족하다. 특히 아래 항목이 독립 contract로 고정돼 있지 않다.

- historical membership / survivorship assumption
- point-in-time data assumption
- parameter set and optimization history
- in-sample / out-of-sample / walk-forward separation
- cost / slippage / turnover / liquidity assumption
- replay contract and generated artifact location
- `NOT_RUN`, `REVIEW`, `BLOCKED` evidence
- Practical Validation source payload readiness
- Final Review selected-route blockers
- Portfolio Monitoring review triggers

## Placement Decision

| Artifact | Location | Purpose |
|---|---|---|
| Contract guide | `.aiworkspace/note/finance/reports/backtests/STRATEGY_PROMOTION_CONTRACT.md` | main-dev가 handoff를 판정할 때 읽는 durable rule |
| Contract template | `.aiworkspace/note/finance/reports/backtests/templates/STRATEGY_PROMOTION_CONTRACT_TEMPLATE.md` | backtest-dev가 전략별로 채워서 넘기는 문서 형식 |
| Optional helper | `.aiworkspace/plugins/quant-finance-workflow/scripts/check_strategy_promotion_contract.py` | template / submitted contract의 필수 section 누락 점검 |
| Helper tests | `tests/test_strategy_promotion_contract.py` | helper가 missing required section을 잡는지 검증 |

Backtest reports 폴더를 선택하는 이유는 이 contract가 registry source-of-truth를 대체하지 않는 사람이 읽는 handoff / report artifact이기 때문이다. 채택된 장기 workflow boundary는 필요한 만큼 `docs/flows/PORTFOLIO_SELECTION_FLOW.md`, `docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md`, `docs/ROADMAP.md`, `docs/INDEX.md`에 요약한다.

## Promotion Decision States

| State | Meaning | Product Workflow Effect |
|---|---|---|
| `PROMOTE_READY` | 필수 contract와 evidence가 충족됐다 | Practical Validation source payload 생성 또는 연결 검토 가능 |
| `REVIEW_REQUIRED` | 선택 차단은 아니지만 명시 review trigger가 필요하다 | Final Review open review item 또는 Monitoring review trigger로 이어져야 함 |
| `BLOCKED` | selected-route로 올릴 수 없는 hard blocker가 있다 | Practical Validation / Final Review / Portfolio Monitoring 연결 금지 |
| `NOT_RUN` | 필요한 실험 또는 evidence가 실행되지 않았다 | pass가 아니며, critical field라면 blocker로 판정 |

## Practical Validation Handoff Criteria

Practical Validation source payload로 넘기려면 strategy output이 최소한 다음을 제공해야 한다.

- strategy family, owner, target use case
- source id 또는 proposed source naming rule
- universe definition and candidate membership policy
- replayable parameter set
- benchmark / comparator policy
- result period and curve payload boundary
- selection / holdings history snapshot or replay path
- cost / turnover / liquidity compact evidence
- data trust warnings, excluded tickers, generated artifact location
- `NOT_RUN` / `REVIEW` / `BLOCKED` evidence summary

## Final Review And Monitoring Criteria

Final Review selected-route로 올릴 수 없는 blocker는 `BLOCKED` 또는 critical `NOT_RUN`으로 남긴다. 일반 `REVIEW_REQUIRED`는 open review item으로 이어질 수 있지만, source payload, replay, benchmark parity, PIT / survivorship, net performance, liquidity, selected-route evidence가 비어 있으면 selected-route blocker로 본다.

Portfolio Monitoring에 연결되는 경우에는 strategy-specific review trigger를 반드시 남긴다. 예: benchmark underperformance, drawdown deterioration, liquidity / provider freshness staleness, macro regime trigger, replay failure, generated artifact mismatch.

## Risk-On Momentum 5D Example Boundary

Risk-On Momentum 5D는 현재 Backtest Analysis research lane으로 구현돼 있고, Practical Validation / Final Review / Portfolio Monitoring governance 연결은 deferred 상태다. 이 task는 해당 전략을 승인하지 않는다. 다만 promotion contract 예시에서는 아래처럼 필요한 항목을 표시한다.

- daily swing family, `backtest-dev` owner, research lane handoff
- S&P 500 / Top1000 / Top2000 / manual stock universe와 historical membership assumption
- D+1 open execution, ATR / fixed exit, macro mode parameter set
- generated trade / scanner artifact location
- OOS / walk-forward / stress / cost-slippage / liquidity evidence가 없으면 `NOT_RUN` 또는 `REVIEW_REQUIRED`
- Practical Validation source payload가 아직 없으면 `BLOCKED`

## Verification Design

문서 중심 검증:

- `git diff --check`
- `find .aiworkspace/note/finance/reports/backtests -maxdepth 3 -type f | sort`
- helper가 추가되면 focused pytest와 `py_compile`

코드 helper가 추가되는 경우 TDD로 진행한다.
