# Practical Validation 1차 필수 검증 Taxonomy Audit

Status: Design Complete
Date: 2026-07-08

## Summary

사용자 지적은 타당하다. 현재 1차 필수 검증은 화면 카테고리는 정리됐지만, service-level check ownership은 아직 섞여 있다. 가장 큰 문제는 `validation_efficacy`가 독립적인 검증 방법론 평가가 아니라 source, replay, benchmark, data, provider, PIT, survivorship, robustness까지 다시 읽는 umbrella audit으로 작동한다는 점이다.

개선 기준은 다음이다.

1. 하나의 check는 하나의 owner module만 가진다.
2. 다른 모듈은 owner 결과를 의존성으로 참조할 수 있지만, 같은 실패를 다시 gate failure로 만들지 않는다.
3. 필수 검증, 조건부 검증, downstream reference, Final Review handoff preview를 분리한다.
4. `validation_efficacy`는 `validation_method_strength`로 축소해 walk-forward / OOS / regime split만 소유한다.

## Current Required Modules

| Current module | Current role | Problem |
|---|---|---|
| `source_integrity` | source id, active component, target weight, Data Trust, execution boundary, curve evidence | Data Trust와 execution boundary가 다른 audit에도 반복된다. |
| `latest_replay` | Runtime recheck, runtime period coverage | `validation_efficacy`와 `data_coverage`가 period/replay를 다시 읽는다. |
| `benchmark_parity` | Benchmark/comparator period, frequency, coverage parity | `validation_efficacy`가 benchmark parity를 다시 읽는다. |
| `validation_efficacy` | Source contract, Data Trust, runtime replay, period coverage, benchmark parity, walk-forward, OOS, regime, provider freshness, robustness, PIT, survivorship, execution boundary | 중복의 중심. method strength만 소유해야 한다. |
| `data_coverage` | DB price window, provider freshness, PIT price window, universe/listing, survivorship/delisting, storage boundary | PIT/survivorship/provider freshness는 이 모듈이 owner여야 한다. |
| `construction_risk` | component weight concentration, provider look-through, top holding, holdings overlap, asset exposure | ETF-like / weighted mix에만 적용해야 한다. |
| `backtest_realism` | cost model, net cost curve, turnover, cost/slippage sensitivity, liquidity, net performance, rebalance timing, tax/account, execution boundary | tax/account는 downstream reference 성격이 강하다. |
| `stress_robustness` | stress, rolling, sensitivity, overfit | `validation_efficacy`의 robustness row와 중복된다. |

## Current Conditional / Reference Modules

| Current module | Current role | Target classification |
|---|---|---|
| `provider_investability` | ETF provider operability / holdings / exposure / provider gap action | Conditional for ETF-like source. Provider freshness 자체는 `data_bias_control` owner. |
| `leverage_inverse` | leveraged / inverse ticker suitability | Conditional only when leveraged/inverse symbols exist. |
| `risk_contribution` | weighted mix correlation / risk contribution / drop-one dependency | Sub-check under portfolio construction for weighted mix. |
| `component_role_weight` | weighted mix component role / target weight / rationale | Sub-check under portfolio construction for weighted mix. |
| `macro_regime` | tactical / hedged macro regime fit | Conditional for tactical or hedged profile. |
| `monitoring_baseline` | selected dashboard downstream seed | Downstream reference, not 1차 필수 검증. |
| `tax_account_scope` | tax / account scope | Final Review reference, not Practical Validation hard blocker. |
| `selected_route_preflight` | Final Review save blocker preview | Handoff preview, not validation category. |

## Duplicate Ownership Inventory

| Check / row | Current appearances | New owner | Action |
|---|---|---|---|
| Selection source / active components / target weight | `source_integrity`, `validation_efficacy.Backtest source contract` | `candidate_contract` | Keep once. Remove from validation efficacy route. |
| Data Trust | `source_integrity`, `validation_efficacy.Data Trust boundary` | `candidate_contract` for source handoff; detailed data quality stays in `data_bias_control` | Do not double-block. |
| Runtime recheck | `latest_replay`, `validation_efficacy.Runtime replay evidence` | `latest_replay` | Validation method may depend on it but not grade it. |
| Runtime period coverage | `latest_replay`, `validation_efficacy.Runtime period coverage`, `data_coverage.PIT price window coverage` | `latest_replay` for replay coverage; `data_bias_control` for PIT price window | Split semantic ownership. |
| Benchmark parity | `benchmark_parity`, `validation_efficacy.Benchmark parity` | `comparison_basis` | Remove from validation efficacy route. |
| Provider freshness | `provider_investability`, `validation_efficacy.Provider / freshness evidence`, `data_coverage.Provider snapshot freshness` | `data_bias_control` for freshness; `provider_investability` for ETF operability/holdings/exposure | Separate freshness from investability action. |
| Robustness / stress | `stress_robustness`, `validation_efficacy.Robustness / stress coverage`, Robustness Lab board | `stress_robustness` | Validation method can reference stress summary only as context. |
| PIT / look-ahead | `validation_efficacy.PIT / look-ahead guard`, `data_coverage.PIT price window coverage` | `data_bias_control` | Remove from validation efficacy route. |
| Survivorship / universe | `validation_efficacy.Survivorship / universe guard`, `data_coverage.Survivorship / delisting control`, `data_coverage.Universe / listing evidence` | `data_bias_control` | Remove from validation efficacy route. |
| Execution / storage boundary | `source_integrity`, `validation_efficacy.Execution / storage boundary`, `data_coverage.Data storage boundary`, `backtest_realism.Execution boundary`, construction/risk/role storage boundary rows | Per-module evidence storage boundary as INFO/reference; not a repeated blocker | Keep as non-gating metadata unless the owner module lacks required evidence. |
| Tax / account scope | `backtest_realism.Tax / account scope`, `tax_account_scope` | `tax_account_scope` downstream reference | Exclude from 1차 필수 route. |

## Proposed Required Taxonomy

| New module | User-facing question | Owns | Depends on |
|---|---|---|---|
| `candidate_contract` | 어떤 후보를 검증하는지 명확한가 | source id, active components, target weight, source snapshot, handoff Data Trust summary, curve evidence | Backtest Analysis handoff |
| `latest_replay` | 최신 DB 기준으로 같은 전략이 다시 실행됐는가 | runtime recheck, replay id, replay mode, runtime period coverage | Candidate contract |
| `comparison_basis` | 후보와 비교 기준이 같은 조건인가 | benchmark/comparator/cash/simple/custom baseline coverage, frequency, period parity | Latest replay and curve evidence |
| `data_bias_control` | 데이터가 검증 결과를 왜곡하지 않는가 | DB price window, provider freshness, PIT window, universe/listing, lifecycle/survivorship/delisting | Latest replay period |
| `validation_method_strength` | 검증 방법이 충분히 설득력 있는가 | walk-forward, OOS holdout, regime split | Latest replay, comparison basis, data bias control |
| `realism_tradability` | 실전 운용 해석에 필요한 비용/유동성 근거가 있는가 | transaction cost, net cost curve, turnover, cost/slippage sensitivity, liquidity, net performance, rebalance timing | Candidate contract, provider evidence where applicable |
| `stress_robustness` | 특정 구간이나 설정에만 의존하지 않는가 | stress window, rolling validation, sensitivity, overfit warning | Latest replay and curve evidence |
| `portfolio_construction` | 포트폴리오 내부 구성이 납득 가능한가 | component concentration, look-through, top holding, overlap, asset bucket, risk contribution, component role/weight | Provider investability for ETF-like / weighted mix |

## Conditional / Reference Taxonomy

| Module | Applies when | Role |
|---|---|---|
| `provider_investability` | ETF-like source | Provider operability, holdings, exposure, provider gap action. |
| `leverage_inverse` | leveraged/inverse symbols exist | Complexity and suitability review. |
| `macro_regime` | tactical source or hedged/tactical profile | Macro/regime fit review. Sentiment remains context only. |
| `tax_account_scope` | Final Review | Tax/account memo or review item. |
| `monitoring_baseline` | Operations / Portfolio Monitoring | Monitoring seed reference. |
| `selected_route_preflight` | Always after module plan | Final Review handoff preview, not validation category. |

## Dependency Rule

`validation_method_strength` should not duplicate upstream failures. If latest replay, comparison basis, or data bias control is not ready, it should report a dependency summary rather than repeating each missing row as its own route failure.

Initial implementation should avoid adding a new user-facing status. Use:

- owner module: `NEEDS_INPUT`, `BLOCKED`, `REVIEW`, or `PASS`.
- dependent module: no duplicate route row; optional `INFO` dependency note excluded from gate calculation.

This keeps the existing status policy stable while removing duplicate blockers.

## Gate Rule

Final Review movement should be blocked by owner module status only.

- `BLOCKED`, `NEEDS_INPUT`, `NOT_RUN` in required owner modules block.
- `REVIEW` generally moves to Final Review as an open review item unless selected-route policy explicitly treats it as `REVIEW_REQUIRED`.
- Conditional modules block only when they apply and their configured severity is selection-critical.
- Reference modules never block Practical Validation movement.
- `selected_route_preflight` can block movement as a handoff preview, but it must be shown separately from validation categories.

## Flow 4 Grouping

Flow 4 should keep category-first display, but categories should reflect ownership:

1. 후보 계약 / 최신 재검증
2. 비교 기준 동등성
3. 데이터 품질 / 편향 통제
4. 검증 방법론 강도
5. 실전 운용 현실성
6. 강건성
7. 포트폴리오 구성
8. 후보 특성별 추가 근거
9. Final Review 이동 요약

## Next Code Work

1. Add owner matrix tests around `validation_efficacy` duplicate rows.
2. Refactor `build_validation_efficacy_audit` so its route rows only include walk-forward, OOS, and regime split.
3. Move PIT/survivorship/provider freshness ownership entirely to `build_data_coverage_audit`.
4. Keep `latest_replay` and `benchmark_parity` as module planner checks, not validation efficacy rows.
5. Update board registry and workspace display text to the new module labels while preserving backward-compatible module ids where necessary.
6. Update Final Review evidence read model tests so selected-route policy still blocks owner module failures and no longer double-counts validation efficacy duplicates.
