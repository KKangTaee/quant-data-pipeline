# Strategy Promotion Contract

Status: Active
Last Verified: 2026-06-08

## Purpose

이 문서는 `backtest-dev`에서 나온 전략 분석, 개선, 추가 개발 결과를 `main-dev` 제품 workflow에 올리기 전에 확인해야 하는 handoff 계약이다.

핵심 목적은 단순히 "수익률이 좋다"는 이유만으로 전략이 아래 흐름에 들어오지 않게 하는 것이다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

이 contract는 전략 승인서, 투자 승인서, broker order, account sync, auto rebalance가 아니다. 제품 workflow에 연결할 수 있는 evidence가 충분한지 판정하기 위한 문서 기준이다.

## When This Contract Is Required

아래 중 하나라도 해당하면 Strategy Promotion Contract를 작성한다.

- `backtest-dev`가 새 strategy family를 구현했거나 기존 strategy family를 의미 있게 개선했다.
- research lane 결과를 Practical Validation source로 넘기려 한다.
- Final Review selected-route 또는 Portfolio Monitoring review trigger로 연결할 전략 governance를 만들려 한다.
- 기존 전략의 parameter / optimization / universe / data source / cost / liquidity 가정이 바뀌었다.

작은 UI copy, 단순 report append, generated artifact 확인, legacy run history inspection만으로는 이 contract를 새로 만들 필요가 없다.

## Contract File Location

전략별 promotion contract는 사람이 읽는 report artifact로 보관한다.

```text
.aiworkspace/note/finance/reports/backtests/runs/YYYY/<date>_<strategy>_promotion_contract.md
```

반복 참조할 핵심 판단은 해당 strategy hub 또는 `*_BACKTEST_LOG.md`에 요약한다. Registry / saved JSONL은 제품 workflow source-of-truth이므로 이 contract로 대체하거나 재작성하지 않는다.

## Required Decision States

| State | Meaning | Product Workflow Effect |
|---|---|---|
| `PROMOTE_READY` | 필수 contract와 evidence가 충족됐다 | Practical Validation source payload 생성 또는 연결 검토 가능 |
| `REVIEW_REQUIRED` | 선택 차단은 아니지만 명시 review trigger가 필요하다 | Final Review open review item 또는 Portfolio Monitoring review trigger로 이어진다 |
| `BLOCKED` | selected-route로 올릴 수 없는 hard blocker가 있다 | Practical Validation / Final Review / Portfolio Monitoring 연결 금지 |
| `NOT_RUN` | 필요한 실험, replay, 또는 evidence가 실행되지 않았다 | pass가 아니며 critical field라면 blocker로 본다 |

`PROMOTE_READY`는 live-ready가 아니다. Practical Validation과 Final Review가 읽을 수 있는 source payload를 만들 준비가 됐다는 뜻이다.

## Minimum Required Fields

| Group | Required Fields | Product Effect If Missing |
|---|---|---|
| Identity | strategy family, owner, target use case | ownerless research note로 남기고 promotion review 불가 |
| Universe | universe definition, historical membership, survivorship assumption | survivorship / coverage `BLOCKED` 또는 critical `NOT_RUN` |
| Data / PIT | point-in-time data assumption, provider / macro / factor source boundary, available-at limitation | PIT / look-ahead `BLOCKED` 또는 `REVIEW_REQUIRED` |
| Parameters | parameter set, optimization history, frozen promotion parameter | overfit / reproducibility `BLOCKED` |
| IS / OOS | in-sample / out-of-sample split, holdout policy | validation efficacy critical `NOT_RUN` |
| Walk-forward / Stress | walk-forward, regime, stress evidence | robustness critical `NOT_RUN` or `REVIEW_REQUIRED` |
| Realism | cost, slippage, turnover, liquidity / capacity assumption | Backtest Realism selected-route blocker if net proof is absent |
| Comparator | benchmark / comparator policy, parity period / frequency / coverage | benchmark parity blocker |
| Replay | replay contract, rerun command or runtime owner, expected payload shape | Practical Validation source payload blocker |
| Artifacts | generated artifact location, artifact retention / commit policy | evidence traceability `REVIEW_REQUIRED`; raw generated artifact should not be staged by default |
| Failures | known failure cases, excluded tickers, data gaps, runtime warnings | unresolved blocker or open review item |
| Evidence State | explicit `NOT_RUN` / `REVIEW` / `BLOCKED` rows and reasons | cannot be treated as passed evidence |
| Practical Validation | source payload conditions, selection / holdings history, compact result evidence | Practical Validation handoff blocker |
| Final Review | selected-route blockers and open review items | Final Review selected save blocker or review carry-forward |
| Monitoring | review trigger, recheck cadence, stale evidence triggers | Portfolio Monitoring cannot define review signals |

## Handoff Flow

| Step | Owner | Required Action | Output |
|---|---|---|---|
| 1. Strategy research / improvement | `backtest-dev` | Produce strategy result, reports, artifacts, and filled promotion contract | Candidate promotion contract |
| 2. Contract completeness check | `backtest-dev` or `main-dev` | Run structural checklist helper or manual checklist | missing / ready section list |
| 3. Main product review | `main-dev` | Classify `PROMOTE_READY`, `REVIEW_REQUIRED`, `BLOCKED`, `NOT_RUN` | promotion review decision |
| 4. Practical Validation handoff | `main-dev` after approval | Build or connect source payload only if contract supports it | validation source candidate |
| 5. Final Review selected-route | `main-dev` product workflow | Existing selected-route gate decides monitorable state | final decision row if selected |
| 6. Portfolio Monitoring | Operations workflow | Read selected row and track review triggers | monitoring scenario / optional snapshot |

This flow does not create a parallel approval stage. It creates the evidence contract before a strategy can enter the existing product gates.

## Practical Validation Source Payload Conditions

A promoted strategy must identify how its output becomes a Practical Validation source. At minimum, the handoff must include:

- strategy family and strategy key
- frozen parameter set
- universe label and membership rule
- period start / end and data as-of assumptions
- benchmark / comparator policy
- result summary and equity curve boundary
- selection / holdings history snapshot or replay path
- cost / turnover / liquidity compact evidence
- excluded ticker / malformed row / missing provider warnings
- generated artifact path for details that should not be stored in workflow JSONL
- source payload fields that are unavailable and why

If the strategy cannot provide a replayable payload or selection / holdings history where the downstream audit needs it, the contract must mark the missing part as `BLOCKED` or critical `NOT_RUN`.

## Final Review Selected-Route Blockers

The contract should treat the following as selected-route blockers unless a later approved policy says otherwise.

| Blocker | Why It Blocks |
|---|---|
| Missing replay contract | Final Review cannot prove the selected row can be rechecked |
| Critical PIT / look-ahead uncertainty | Good historical performance may be contaminated |
| Survivorship assumption unresolved for stock universe | Universe membership may be hindsight-biased |
| Benchmark / comparator parity missing | Performance spread is not interpretable |
| Optimization history hidden | Overfit risk cannot be reviewed |
| OOS / walk-forward not run for optimized strategy | Validation efficacy is insufficient |
| Gross-only performance with missing cost / slippage proof | Selected-route net performance policy is not supported |
| Liquidity / capacity unknown for tradable universe | Portfolio Monitoring cannot define operability triggers |
| Generated artifact absent for trade / scanner details | Audit trail cannot inspect source detail |
| Critical evidence marked `NOT_RUN` | `NOT_RUN` is missing evidence, not pass |

General `REVIEW_REQUIRED` evidence can become an open review item, but the contract must name the owner, expected follow-up, and Portfolio Monitoring trigger.

## Portfolio Monitoring Review Triggers

Every promoted strategy should define at least one monitoring trigger. Examples:

- benchmark underperformance threshold
- drawdown deterioration threshold
- replay failure or stale DB source
- provider / macro / factor evidence staleness
- liquidity / capacity coverage drop
- universe membership refresh gap
- macro regime change that invalidates the original use case
- generated artifact mismatch between selected decision and latest replay

Monitoring trigger definitions are read-only review criteria. They do not create live approval, broker order, account sync, or auto rebalance.

## Connection To Existing Reports And Strategy Hubs

- Raw or one-off result reports start under `runs/YYYY/`.
- Repeated strategy-family evidence is summarized in `strategies/<STRATEGY>_BACKTEST_LOG.md`.
- Strategy hub pages should summarize current promotion state if the strategy becomes a recurring candidate.
- Practical Validation and Final Review registries remain the product source-of-truth after the strategy enters the workflow.
- Generated trade logs, scanner rows, full holdings, full macro series, and raw provider responses stay in generated artifacts or DB. They are not copied into workflow JSONL.

## Risk-On Momentum 5D Example

This example explains required evidence only. It does not approve Risk-On Momentum 5D for Practical Validation, Final Review, or Portfolio Monitoring.

| Contract Area | Example Requirement For Risk-On Momentum 5D | Expected Current Treatment |
|---|---|---|
| Identity | Daily swing research lane, owner `backtest-dev`, target use case such as short-term risk-on stock momentum | Required |
| Universe | S&P 500 / Top1000 / Top2000 / manual stock universe and historical membership policy | Missing historical membership means `REVIEW_REQUIRED` or `BLOCKED` depending on use case |
| PIT | Daily OHLCV, futures macro Mean-Z, annual statement shadow availability assumptions | Any unavailable-at ambiguity must be explicit |
| Parameters | D+1 open execution, exit mode, ATR / fixed thresholds, max holding days, macro mode | Frozen promotion parameter required |
| Optimization | Any comparison / sensitivity used to choose parameters | Hidden optimization is `BLOCKED` |
| OOS / Walk-forward | Holdout or walk-forward evidence separate from parameter selection | Missing evidence is critical `NOT_RUN` |
| Cost / Liquidity | Slippage, turnover, trade count, capacity / liquidity assumption for selected universe | Gross-only results cannot be selected-route ready |
| Replay | Runtime owner and replay command / payload shape for latest DB data | Missing replay is `BLOCKED` |
| Artifacts | Generated trade log / scanner artifact location | Required for audit; do not stage generated artifact by default |
| Monitoring | Macro-off trigger, benchmark underperformance, drawdown deterioration, replay failure | Required before Portfolio Monitoring linkage |

## Template And Helper

Use [templates/STRATEGY_PROMOTION_CONTRACT_TEMPLATE.md](./templates/STRATEGY_PROMOTION_CONTRACT_TEMPLATE.md) for new handoff packets.

If the helper is available, run:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_strategy_promotion_contract.py path/to/promotion_contract.md
```

The helper checks required section completeness. It does not validate performance truth, approve a strategy, or update registries.
