# Backtest Runtime Flow

## 목적

이 문서는 백테스트 실행이 UI 입력에서 finance strategy 결과까지 어떻게 이동하는지 설명한다.
전략 실행 오류, payload 복원 오류, result bundle 누락을 볼 때 먼저 확인한다.

Layer ownership과 storage / product surface boundary는 [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)를 기준으로 한다.

## 현재 큰 흐름

Single Strategy 실행 흐름:

```text
app/web/streamlit_app.py
  -> app/web/pages/backtest.py
  -> app/web/backtest_single_runner.py
  -> app/services/backtest_execution.py
  -> app/runtime/backtest.py
     -> app/runtime/backtest_strict.py for strict quality / value family
  -> finance/loaders/*
  -> finance/engine.py / finance/transform.py
  -> finance/strategy.py
  -> finance/performance.py
  -> result bundle / metadata / warnings
  -> Backtest UI latest result / history
```

Portfolio Mix / weighted portfolio 흐름은 일부 service layer로 이동했다.
수동 multi-strategy component 실행 loop와 error normalization은 `app/services/backtest_compare_execution.py`로 이동했고,
strategy별 runner catalog와 mix builder default / universe resolution은 `app/services/backtest_compare_catalog.py`로 이동했다.
weighted portfolio bundle construction은 `app/services/backtest_weighted_portfolio.py`로 이동했다.
saved portfolio replay execution / data assembly는 `app/services/backtest_saved_portfolio_replay.py`로 이동했다.
UI는 session state, history append call, notice, render side effect를 유지한다.

```text
app/web/streamlit_app.py
  -> app/web/pages/backtest.py
  -> app/web/backtest_compare.py
  -> app/services/backtest_compare_execution.py
  -> app/services/backtest_compare_catalog.py
  -> app/runtime/backtest.py
  -> finance/loaders/* / finance strategy runtime
  -> component result
  -> app/services/backtest_weighted_portfolio.py
  -> finance/performance.py / app/runtime/backtest.py
  -> weighted portfolio result
  -> app/services/backtest_saved_portfolio_replay.py
  -> saved replay result context
```

Risk-On Momentum 5D 흐름은 기존 rebalance engine과 다른 Daily Swing 연구 lane이다.

```text
app/web/streamlit_app.py
  -> app/web/pages/backtest.py
  -> app/runtime/backtest.py compatibility export
  -> app/runtime/backtest_risk_on_momentum.py::run_risk_on_momentum_5d_backtest_from_db
  -> finance/loaders/price.py / futures.py / fundamentals.py
  -> finance/transform.py
  -> finance/swing.py
  -> finance/indicators.py / finance/swing_macro.py / finance/swing_analysis.py
  -> result bundle + generated swing artifacts
  -> Backtest Analysis Swing Detail
```

이 lane은 Backtest Analysis 후보 연구 surface다.
Practical Validation / Final Review / Portfolio Monitoring daily signal governance 연결은 별도 승인 task 전까지 deferred다.

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | Finance Console navigation entry |
| `app/web/pages/backtest.py` | form, panel, result surface, history, Portfolio Mix Builder, saved portfolio UI |
| `app/web/backtest_single_runner.py` | Single Strategy payload 표시, Streamlit spinner, session state / history append |
| `app/services/backtest_execution.py` | Single Strategy runtime dispatch, elapsed timing, input/data/system error normalization |
| `app/services/backtest_compare_execution.py` | Manual multi-strategy component execution loop, elapsed timing, input/data/system error normalization |
| `app/services/backtest_compare_catalog.py` | Portfolio Mix Builder strategy runner catalog, default parameter, preset/manual universe resolution, runtime dispatch |
| `app/services/backtest_result_read_model.py` | Strategy data trust rows, weighted component contribution amount/share views |
| `app/services/backtest_weighted_portfolio.py` | Weighted portfolio result bundle construction from compared strategy bundles |
| `app/services/backtest_saved_portfolio_replay.py` | Saved portfolio replay strategy rerun, weighted bundle creation, replay source / history context assembly |
| `app/services/backtest_realism_audit.py` | Practical Validation / Final Review가 읽는 read-only backtest realism audit. 기존 runtime metadata와 compact validation evidence에서 비용, turnover, liquidity, net policy, rebalance, tax/account, execution boundary gap을 해석한다 |
| `app/services/backtest_robustness_run_set.py` | Practical Validation / Final Review가 읽는 read-only Robustness Experiment run-set read model. 기존 Robustness Lab, temporal validation, Backtest Realism compact evidence를 하나의 `robustness_run_set_id` 아래에서 묶고, full artifact나 raw rows는 reference만 남긴다 |
| `app/runtime/backtest.py` | UI payload를 DB-backed runtime 실행으로 변환하는 public compatibility facade. Price-only ETF runtime wrappers를 소유하고, split module runner / helper를 re-export한다 |
| `app/runtime/backtest_risk_on_momentum.py` | Risk-On Momentum 5D DB runtime implementation. `app.runtime.backtest`가 기존 public import path를 위해 runner를 re-export한다 |
| `app/runtime/backtest_real_money.py` | Real-money / guardrail / benchmark / deployment readiness helper implementation. `app.runtime.backtest`가 기존 public import path를 위해 constants and helper functions를 re-export한다 |
| `app/runtime/backtest_strict.py` | Strict quality / value / quality-value annual and quarterly runtime implementation. `app.runtime.backtest`가 기존 public import path를 위해 runner and strict helper functions를 re-export한다 |
| `app/runtime/backtest_result_bundle.py` | runtime 결과를 UI-facing result bundle / summary / chart / metadata contract로 변환 |
| `finance/loaders/*` | DB read path와 point-in-time snapshot 조회 |
| `finance/engine.py` | price-based strategy orchestration wrapper |
| `finance/transform.py` | moving average, interval return, date alignment 같은 전처리 |
| `finance/strategy.py` | 실제 strategy simulation |
| `finance/performance.py` | CAGR, Sharpe, drawdown, weighted portfolio 계산 |

## Runtime wrapper 기준

`app/runtime/backtest.py`의 `run_*_backtest_from_db(...)` public export는 제품 실행 경로의 중심이다.
8A부터 Risk-On Momentum 5D 구현은 `app/runtime/backtest_risk_on_momentum.py`로 이동했고,
8B부터 real-money / guardrail / benchmark / deployment readiness helper 구현은 `app/runtime/backtest_real_money.py`로 이동했다.
8C부터 strict quality / value / quality-value annual and quarterly wrapper 구현은 `app/runtime/backtest_strict.py`로 이동했다.
기존 caller compatibility를 위해 `app.runtime.backtest`에서도 같은 runner / constants / helper functions를 계속 export한다.
`build_backtest_result_bundle(...)` 구현은 `app/runtime/backtest_result_bundle.py`가 담당하지만,
기존 caller 호환성을 위해 `app.runtime.backtest`와 `app.runtime`에서도 같은 이름으로 계속 export한다.

대표 함수:

- `run_equal_weight_backtest_from_db(...)`
- `run_gtaa_backtest_from_db(...)`
- `run_global_relative_strength_backtest_from_db(...)`
- `run_risk_parity_trend_backtest_from_db(...)`
- `run_dual_momentum_backtest_from_db(...)`
- `run_risk_on_momentum_5d_backtest_from_db(...)` via `app/runtime/backtest_risk_on_momentum.py`
- `run_quality_snapshot_strict_annual_backtest_from_db(...)` via `app/runtime/backtest_strict.py`
- `run_value_snapshot_strict_annual_backtest_from_db(...)` via `app/runtime/backtest_strict.py`
- `run_quality_value_snapshot_strict_annual_backtest_from_db(...)` via `app/runtime/backtest_strict.py`
- quarterly prototype strict family runtime 함수들 via `app/runtime/backtest_strict.py`

## Boundary Summary

- `app/web/*`는 form, session state, history display, user feedback을 소유한다.
- `app/services/*`는 Streamlit-free dispatch, error normalization, read model, evidence interpretation을 소유한다.
- `app/runtime/backtest.py`는 public compatibility facade와 price-only ETF wrapper를 유지한다. Strategy family나 helper family가 커지면 전용 `app/runtime/backtest_*` module로 구현을 옮기고 기존 export를 유지한다.
- `finance/loaders/*`는 DB read path와 point-in-time snapshot을 소유하며 external fetch나 registry write를 하지 않는다.
- `finance/*` strategy modules는 계산과 분석을 소유하며 UI session state나 live approval을 만들지 않는다.
- result bundle / metadata / warnings는 사용자가 data trust와 runtime assumption을 읽기 위한 계약이며, broker order나 auto rebalance 지시가 아니다.

## Result bundle 기준

제품 UI가 안정적으로 동작하려면 runtime 결과가 다음 정보를 유지해야 한다.

- `result_df`: 날짜별 balance / return table
- `summary`: CAGR, Sharpe, MDD 같은 성과 요약
- `meta`: strategy settings, contract, coverage, warning context
- `warnings`: 데이터 부족, excluded ticker, stale data 같은 사용자 주의사항
- selection history가 있는 전략은 selection row와 interpretation context

Phase 27 이후 result bundle meta에는 Data Trust Summary가 읽을 수 있도록 아래 값도 포함한다.

- `result_rows`: 실제 result table row 수
- `actual_result_start`: 실제 결과 시작일
- `actual_result_end`: 실제 결과 종료일
- `price_freshness`: ticker별 최신 가격 날짜 / stale / missing 진단
- `excluded_tickers`: 실행 중 제외된 ticker
- `malformed_price_rows`: 가격 결측 행이 있는 ticker 요약

Phase 28 이후 새 backtest history record도 재실행 / form 복원 QA를 위해
일부 result-window / data-trust 값을 같이 보존한다.

- `result_rows`
- `actual_result_start`
- `actual_result_end`
- `price_freshness`
- `requested_tickers`
- `excluded_tickers`
- `malformed_price_rows`
- `guardrail_reference_ticker`

Saved Portfolio replay로 생성되는 history context에는 재진입 확인을 위해
`weights_percent`도 함께 남긴다.
strategy별 세부 override는 saved portfolio record의 `compare_context.strategy_overrides`가 기준이다.

Phase 28 이후 compare / weighted portfolio history context에는 component별 data trust rows도 남긴다.

- `strategy_data_trust_rows`: strategy compare record에 저장되는 전략별 data trust snapshot
- `component_data_trust_rows`: weighted portfolio record에 저장되는 구성 전략별 data trust snapshot

이 값은 성과 계산 자체를 바꾸지 않고, 사용자가 compare / weighted / saved replay 결과를 읽을 때
각 component의 실제 결과 기간과 데이터 품질 조건을 다시 확인하게 하는 metadata다.

Phase 28 이후 Real-Money / Guardrail parity는 별도의 성과 계산 로직을 새로 만들지 않고,
이미 result bundle meta나 saved portfolio override에 남아 있는 값을 읽어 scope table로 보여준다.

- annual strict: benchmark / investability / promotion / guardrail 입력을 full strict surface로 해석한다.
- strict quarterly prototype: portfolio handling과 risk-off contract는 저장하지만, promotion guardrail surface는 deferred로 해석한다.
- ETF 전략군: Equal Weight / GTAA / Global Relative Strength / Risk Parity Trend / Dual Momentum의 ETF operability, cost, benchmark, ETF guardrail first pass를 strategy별 지원 범위로 해석한다.

이 scope table은 runtime result를 바꾸지 않는다.
사용자가 history / saved replay 전에 어떤 검증 범위의 결과인지 이해하게 하는 metadata 해석 layer다.

## Real-Money / Guardrail / Pre-Live runtime 기준

runtime은 단순 성과표만 반환하지 않는다.
특히 실전형 후보 검토가 붙은 전략은 아래 진단 정보를 같이 남겨야 한다.
8B 이후 이 helper family의 구현 owner는 `app/runtime/backtest_real_money.py`이며, `app/runtime/backtest.py`는 compatibility export만 유지한다.

- gross / net / cost result
- turnover / cost assumption
- `cost_model_source_contract_v1`: cost bps가 단순 assumption인지, `_apply_transaction_cost_postprocess`를 통해 `Total Balance` / `Total Return` 결과 곡선에 적용됐는지 나타내는 compact proof
- `turnover_evidence_contract_v1`: turnover가 holdings delta에서 실제 추정됐는지, rebalance cadence만 있는지, 또는 holdings column 부족으로 추정하지 못했는지 나타내는 compact proof
- `net_cost_curve_contract_v1`: gross / net / estimated cost curve가 실제로 연결됐는지, measurable cost impact / zero-cost / missing turnover estimate / missing proof를 분리하는 compact proof
- `cost_slippage_sensitivity_contract_v1`: 기존 validation payload의 cost / slippage sensitivity evidence가 explicit인지, generic robustness-only인지, missing인지 분리하는 read-only proof
- `liquidity_capacity_contract_v1`: provider operability context의 coverage, freshness, source strength, compact capacity metrics를 읽어 fresh official actual evidence와 weak / stale / legacy evidence를 분리하는 compact proof
- benchmark overlay와 benchmark-relative diagnostics
- investability filter 결과
- liquidity / coverage policy status
- underperformance / drawdown guardrail trigger state
- promotion / shortlist / deployment 또는 pre-live review status

Backtest Realism Audit은 이 metadata를 새로 계산하거나 저장하지 않는다.
기존 result bundle / Practical Validation evidence에 붙어 있는 비용, turnover, liquidity, net spread, rebalance cadence 같은 값을 읽어 실전성 공백을 `PASS / REVIEW / NEEDS_INPUT / BLOCKED`로 표시한다.
`transaction_cost_bps`만 있고 `cost_application_status=applied_to_result_curve` 또는 그에 준하는 cost application proof가 없으면 assumption-only `REVIEW`로 해석한다.
turnover는 holdings-derived estimate가 있을 때만 strong evidence로 보고, cadence-only 또는 legacy turnover metadata는 `REVIEW`로 해석한다.
net cost curve proof는 measurable gross-net delta와 positive estimated-cost rows가 있을 때 strong evidence로 보며, cost application flag만 있는 legacy source는 과대평가하지 않는다.
cost / slippage sensitivity proof는 explicit cost bps / slippage / spread sensitivity evidence가 있을 때만 strong evidence로 보며, 일반 robustness sensitivity만 있으면 `REVIEW`로 남긴다.
liquidity / capacity proof는 fresh official actual provider evidence와 compact capacity metrics가 있을 때만 strong evidence로 보며, bridge / proxy, stale / unknown, partial coverage, legacy pass-only source는 `REVIEW` 또는 `NEEDS_INPUT`으로 남긴다.
metadata가 없으면 pass로 추정하지 않고 보강 필요로 남긴다.

주의:

- `Real-Money`는 실제 투자 승인 자체가 아니라 실행 가능성 진단 계층이다.
- `Pre-Live`는 real-money 진단 이후 paper / watchlist / hold / reject / re-review 같은 운영 상태를 기록하는 계층이다.
- runtime metadata가 없으면 UI는 숫자를 보여줄 수 있어도 왜 그 결과가 나왔는지 설명하기 어렵다.

## Date alignment 주의

`finance/transform.py`의 alignment 계층은 결과 기간을 크게 바꿀 수 있다.

- `add_ma(...)`: moving average warmup 이전 구간 제거
- `add_interval_returns(...)`: trailing return warmup 이전 구간 제거
- `align_dfs_by_date_intersection(...)`: 모든 ticker에 공통으로 있는 날짜만 유지
- `align_dfs_by_date_union(...)`: 공통 날짜보다 넓은 union 기준이 필요한 경우 사용

ETF basket 전략에서 특정 ticker의 가격 이력이나 결측이 부족하면,
전체 결과가 짧아지거나 ticker가 excluded 처리될 수 있다.
이 경우 조용히 지나가지 말고 warning / metadata에 남겨야 한다.

`Global Relative Strength`는 Phase 27 첫 작업부터 price freshness preflight와
Data Trust Summary metadata를 남기는 첫 적용 대상이다.

## Refinement / Compare 해석

반복 backtest refinement를 다시 볼 때는 아래 순서로 추적한다.

```text
app/web/streamlit_app.py
  -> app/web/pages/backtest.py
  -> app/runtime/backtest.py
  -> finance/engine.py / finance/strategy.py
  -> result bundle / report / saved replay
```

구분:

- `Compare`는 여러 전략의 개별 후보를 나란히 보는 연구 / 분석 표면이다.
- `Weighted Portfolio`는 compare 결과를 월별 composite로 합치는 포트폴리오 합성 표면이다.
- `Saved Portfolio`는 compare + weights + date policy를 저장해 rerun할 수 있게 만든 재현용 setup이다.

이 셋은 곧바로 투자 승인이나 live-ready 판단을 만드는 계층이 아니다. 현재 제품 흐름에서는 Backtest Analysis에서 후보 source를 만들고, Practical Validation과 Final Review를 거쳐야 최종 후보 판단으로 이어진다.

## 갱신해야 하는 경우

- 새 `run_*_backtest_from_db(...)` 함수가 추가될 때
- result bundle shape가 바뀔 때
- warning / metadata 계약이 바뀔 때
- date alignment 정책이 바뀔 때
- real-money / pre-live / history replay가 runtime output을 새 방식으로 읽게 될 때
