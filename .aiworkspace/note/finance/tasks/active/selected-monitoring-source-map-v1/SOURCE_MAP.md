# Selected Monitoring Source Map V1

Status: Complete
Created: 2026-05-29

## Summary

현재 프로젝트에는 Phase 12의 1차 구현에 필요한 monitoring / recheck 재료가 이미 있다.

핵심 gap은 새 저장소 부재가 아니라 source ownership과 policy split이다.
Selected Portfolio Dashboard는 Final Review V2 decision row를 source-of-truth로 읽지만, Performance Recheck와 symbol freshness는 Current Candidate Registry의 replay contract를 다시 찾아야 한다.
또한 Recheck Comparison은 runtime read model에 있고 Review Signals는 UI helper에서 별도 threshold로 다시 계산되어 정책 drift 위험이 있다.

따라서 다음 구현은 새 JSONL 저장이 아니라 `Recheck Readiness / Freshness Contract`를 먼저 고정해 Final Review V2 row, replay contract, DB latest market date, price freshness gap을 하나의 사전 점검 contract로 정리하는 것이다.

## Current Evidence Sources

| Evidence Area | Current Source | Existing Strength | Gap | Candidate Owner |
| --- | --- | --- | --- | --- |
| Selected source-of-truth | `app/runtime/final_selected_portfolios.py` `load_final_selected_portfolio_dashboard()` reads `load_final_selection_decisions_v2()` | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`만 읽고 selected route / flag로 filter | docs 일부 legacy text는 V1 decision file을 언급함. Canonical path는 V2로 고정 필요 | 12-6 continuity / docs refinement |
| Dashboard row status | `build_final_selected_portfolio_dashboard_row()` and `_derive_operation_status()` | selected row, active components, target weight total, Final Review blockers를 compact status로 변환 | latest recheck / provider staleness / freshness는 base `operation_status`에 반영되지 않음 | 12-4 review signal policy |
| Final Review continuity | `build_selected_portfolio_continuity_check()` | selected route, investability packet, component target, trigger, timeline boundary, recheck input, storage boundary 확인 | Performance Recheck 미실행은 `NEEDS_INPUT`으로 드러나지만, 이 상태와 Review Signals policy가 별도 surface로 분산 | 12-6 continuity operations |
| Monitoring timeline | `build_selected_portfolio_monitoring_timeline()` | Final Review selection, evidence gate, Performance Recheck, Actual Allocation drift, alert preview를 source-labeled row로 표시 | recheck / drift / alert은 session state evidence라 durable monitoring record가 아님. 이 경계는 dossier / UX에서 계속 명시 필요 | 12-6 continuity / dossier |
| Performance Recheck execution | `build_selected_portfolio_performance_recheck()` | selected component를 Current Candidate Registry row로 replay하고 portfolio / benchmark summary, component contribution, period extremes 제공 | Final decision row 자체가 replay contract를 충분히 carry하지 않으면 registry_id dependency 때문에 recheck가 막힘 | 12-2 readiness / freshness |
| Recheck readiness | `build_selected_portfolio_recheck_readiness()` | selected component contract, candidate replay contract, DB latest market date, default period, storage boundary 확인 | replay contract lookup이 Current Candidate Registry에 치우쳐 있고, embedded final decision contract fallback 정책이 약함 | 12-2 readiness / freshness |
| Symbol freshness | `build_selected_portfolio_recheck_symbol_freshness()` with `finance.loaders.price.load_price_freshness_summary()` | portfolio / benchmark ticker별 latest date, row count, days lag를 DB metadata로 확인 | symbol resolution도 candidate replay contract에 의존. Missing / stale은 잘 드러나지만 12-2에서 readiness와 한 contract로 묶어야 함 | 12-2 readiness / freshness |
| Provider evidence | `build_selected_portfolio_provider_evidence()` with `build_provider_context()` | selected component ticker weight로 operability / holdings / exposure / look-through evidence를 기존 DB snapshot에서 읽음 | provider symbol resolution fallback은 가능하지만 fallback은 `REVIEW`; stale / partial / NOT_RUN handling은 더 명시적 contract로 유지 필요 | 12-3 provider staleness |
| Recheck comparison | `build_selected_portfolio_recheck_comparison()` | latest recheck와 Final Review baseline의 CAGR / MDD / benchmark spread / component coverage / period coverage 비교 | Review Signals UI helper가 유사 threshold를 별도로 계산해 policy duplication 위험 | 12-4 comparison / signals |
| Review Signals board | `app/web/final_selected_portfolio_dashboard.py` `_build_review_trigger_board()` | operator-facing trigger table로 CAGR deterioration, MDD expansion, benchmark underperformance, allocation drift 표시 | runtime comparison contract와 threshold / status vocabulary가 분리됨. Single policy owner 필요 | 12-4 comparison / signals |
| Actual Allocation / drift | `build_selected_portfolio_current_weight_inputs()`, `build_selected_portfolio_drift_check()`, `build_selected_portfolio_drift_alert_preview()` | current value, shares x price, current weight input을 read-only drift / alert preview로 변환 | optional session-state check임. account holdings / order workflow로 확장하면 scope 초과 | 12-5 allocation drift boundary |
| Latest close assistance | `load_latest_selected_portfolio_prices()` with `finance.loaders.price.load_latest_prices()` | shares x price 입력 보조로 DB latest close를 읽음 | input assistance이지 execution proof가 아님. stale / missing latest close가 drift signal에 어떤 영향인지 12-5에서 명시 필요 | 12-5 allocation drift boundary |
| Decision Dossier | `build_decision_dossier()` | Final Review decision evidence와 optional selected monitoring timeline을 markdown으로 export | report 파일 자동 저장은 없음. session timeline 포함 여부가 durable record와 혼동될 수 있음 | 12-6 dossier / continuity |
| Optional monitoring log | `append_selected_portfolio_monitoring_log()` exists in `portfolio_selection_v2.py` | 명시 사용자 action용 optional append helper는 존재 | Selected Dashboard active path에서 자동 append call은 없음. 이 경계 유지 필요 | 12-7 closeout storage gate |

## Stage Ownership

| Stage | Current Role | Phase 12 Gap |
| --- | --- | --- |
| Final Review | selected decision row, investability packet, gate policy, selected components, review trigger 저장 | selected row가 replay에 필요한 full contract를 항상 carry하는지 불확실 |
| Selected Dashboard runtime | final decision row를 dashboard row / readiness / freshness / provider / comparison / drift / timeline으로 변환 | read model은 많지만 정책 owner가 분산되어 있음 |
| Current Candidate Registry | selected component registry_id로 replay payload를 복원 | V2 final decision flow가 legacy/current candidate registry availability에 의존 |
| Price DB / loader | latest market date, symbol freshness, latest close read path 제공 | stale / missing price가 readiness와 review signal에서 일관되게 severity로 이어져야 함 |
| Provider DB / context | provider / holdings / exposure / look-through compact evidence 제공 | stale / partial / fallback provider evidence가 selected monitoring policy로 통합되어야 함 |
| Streamlit session state | latest recheck, drift check, alert preview 보관 | session-only evidence를 durable monitoring record처럼 오해하지 않게 해야 함 |
| Decision Dossier | final decision + optional session timeline export | auto report save가 아니며, session timeline 포함 여부가 명확해야 함 |

## Gap Audit

| Gap | Severity | Reason | Recommended Fix |
| --- | --- | --- | --- |
| Performance Recheck depends on Current Candidate Registry replay contract | High | Final Review V2 row가 selected source-of-truth인데 recheck는 registry_id로 Current Candidate row를 다시 찾아야 함 | 12-2에서 replay contract priority를 `final decision embedded contract -> current candidate registry fallback`로 정리하거나, blocker message를 더 명확히 고정 |
| Recheck readiness와 symbol freshness가 별도 surface로만 보임 | High | contract가 준비돼도 price freshness가 stale이면 최신 recheck로 볼 수 없음 | 12-2에서 readiness / freshness를 같은 operations contract로 묶고 combined route를 정의 |
| Review Signals와 Recheck Comparison threshold가 중복됨 | High | `_build_review_trigger_board()`와 `build_selected_portfolio_recheck_comparison()`이 CAGR / MDD / spread threshold를 별도로 계산 | 12-4에서 comparison contract를 policy owner로 삼고 UI Review Signals는 그 결과를 렌더링하게 정렬 |
| Base dashboard `operation_status`가 latest monitoring evidence를 반영하지 않음 | Medium | selected row가 `normal`이어도 recheck / provider / freshness는 stale일 수 있음 | 12-4에서 latest monitoring route를 별도 summary로 표시하거나 operation status와 분리된 "current monitoring status"를 정의 |
| Provider evidence contract는 좋지만 Phase 12 severity와 통합 전 | Medium | provider evidence의 `SELECTED_PROVIDER_REVIEW / NEEDS_DATA`가 timeline / review signals와 일관되게 이어지지 않음 | 12-3에서 selected provider staleness route와 monitoring signal mapping을 고정 |
| Session-state evidence가 durable record로 오해될 수 있음 | Medium | Performance Recheck, drift, alert preview는 session only이며 reload 후 사라질 수 있음 | 12-6에서 continuity / dossier / timeline에 session-only label과 write boundary를 더 명확히 유지 |
| Actual Allocation input이 account/order 기능처럼 확장될 위험 | Medium | shares x price 입력과 latest close assistance가 실제 holdings 연결처럼 보일 수 있음 | 12-5에서 optional input contract, stale latest close handling, no-order boundary를 고정 |
| Docs 일부가 V1 final decision path를 언급 | Low | current code uses V2 canonical file; legacy docs can confuse future implementation | 12-6 또는 closeout에서 Selected Dashboard docs wording 정리 |

## Recommended Task Order

1. `recheck-readiness-freshness-contract-v1`
   - Final decision selected row, embedded component contract, Current Candidate Registry fallback, DB latest market date, symbol freshness를 하나의 operations preflight로 정리한다.
   - missing replay contract, stale symbol, missing benchmark price, DB latest date error는 pass가 아니다.
   - 새 JSONL 저장 없이 existing row / DB loader만 읽는다.

2. `selected-provider-evidence-staleness-contract-v1`
   - selected provider evidence route를 monitoring signal에 연결한다.
   - fresh official actual evidence, stale actual evidence, partial coverage, fallback contract, missing provider DB를 구분한다.
   - provider collection은 UI에서 실행하지 않고 Ingestion -> DB -> Loader 경계를 유지한다.

3. `recheck-comparison-review-signal-policy-v1`
   - `build_selected_portfolio_recheck_comparison()`을 Review Signals의 policy owner로 삼는다.
   - UI helper의 duplicated threshold를 제거하거나 comparison result를 그대로 표시하게 한다.
   - failed / missing / partial recheck가 `Clear`로 보이지 않게 한다.

4. `allocation-drift-evidence-boundary-v1`
   - Actual Allocation input이 optional, session-only, no-order evidence임을 contract와 tests로 고정한다.
   - latest close assistance의 missing / stale state가 drift interpretation에서 어떻게 표시되는지 정한다.

5. `decision-dossier-continuity-operations-v1`
   - continuity check, timeline, dossier가 V2 final decision source와 session-only monitoring evidence를 일관되게 표시하게 한다.
   - docs의 V1/V2 final decision path 혼동을 정리한다.

## Storage Boundary

- 새 JSONL registry는 만들지 않는다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` 자동 append는 만들지 않는다.
- user memo, preset, comment, time log 저장은 만들지 않는다.
- full price history, provider holdings, exposure, macro series는 workflow JSONL에 저장하지 않는다.
- account holdings API, broker order, live approval, auto rebalance는 scope 밖이다.
- 필요한 데이터 보강은 `Ingestion -> DB -> Loader -> UI` 경로로만 검토한다.

## Test Scope For Next Implementation

For 12-2:

- selected final decision row에 embedded contract가 있으면 Current Candidate Registry 없이 readiness가 가능해야 하는지 결정
- Current Candidate Registry missing이면 readiness는 `BLOCKED` 또는 `NEEDS_INPUT`으로 남는지
- DB latest market date가 baseline_end를 넘지 않으면 `REVIEW`로 남는지
- symbol freshness가 stale / missing이면 combined readiness가 pass가 아닌지
- benchmark symbol missing이 portfolio symbol missing과 함께 표시되는지
- execution boundary가 `db_write=False`, `registry_write=False`, `monitoring_log_auto_write=False`, `order_instruction=False`, `auto_rebalance=False`를 유지하는지

Suggested checks:

- `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py`
- `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`
