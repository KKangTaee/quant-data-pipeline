# Phase 12 Selected Monitoring / Recheck Operations Design

Status: Active
Created: 2026-05-29

## Design Principle

Phase 12는 "최종 선정했다"를 "계속 보유해도 된다"로 자동 해석하지 않는다.
Selected Portfolio Dashboard는 선정 이후 운영 확인 surface이지만, live trading system은 아니다.

기본 방향은 다음이다.

- Final Review decision row는 source-of-truth로 읽되 새 판단 row를 자동 생성하지 않는다.
- recheck readiness / freshness / provider / continuity / signal / comparison은 read-only evidence로 유지한다.
- monitoring log는 explicit user action일 때만 optional record로 남긴다.
- stale, missing, failed, partial, `NOT_RUN` evidence는 pass로 숨기지 않는다.
- UI에서 provider, FRED, broker, account API를 직접 fetch하지 않는다.

## Evidence Layers

| Layer | Purpose | Initial Source |
| --- | --- | --- |
| Source map | 현재 Selected Dashboard evidence와 runtime read model의 source ownership 확인 | Complete: `selected-monitoring-source-map-v1` |
| Recheck readiness | DB latest market date, benchmark, replay contract, default period 확인 | Existing `app/runtime/final_selected_portfolios.py` readiness read model |
| Symbol freshness | portfolio / benchmark ticker별 DB latest date, row count, stale status 확인 | Existing selected dashboard symbol freshness table |
| Provider evidence | selected component ticker weight 기준 provider holdings / exposure / operability context 확인 | Existing DB provider loader / dashboard provider evidence |
| Recheck comparison | latest recheck result와 Final Review baseline 비교 | Existing comparison helper, policy refinement pending |
| Review signals | recheck, provider, drift, continuity 상태를 hold / watch / re-review signal로 번역 | Existing Review Signals surface, policy refinement pending |
| Allocation drift | 사용자가 명시 입력한 current value / holding 기반 drift 확인 | Existing optional input, read-only boundary refinement pending |
| Continuity / dossier | Final Review evidence packet, selected route, timeline, trigger, dossier 연결 확인 | Existing continuity check and Decision Dossier |

## 12-1 Source Map Result

12-1 found that Phase 12 should start from existing read-only evidence rather than new monitoring persistence.

Reusable sources:

- `load_final_selected_portfolio_dashboard()` already reads `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` through the V2 final decision loader.
- `build_selected_portfolio_recheck_readiness()` already checks selected component contract, Current Candidate Registry replay contract, DB latest market date, default period, and storage boundary.
- `build_selected_portfolio_recheck_symbol_freshness()` already reads DB price freshness metadata for portfolio and benchmark symbols.
- `build_selected_portfolio_provider_evidence()` already reads selected provider evidence from existing provider DB snapshots through `build_provider_context()`.
- `build_selected_portfolio_recheck_comparison()`, `build_selected_portfolio_monitoring_timeline()`, `build_selected_portfolio_continuity_check()`, and `build_decision_dossier()` already expose read-only monitoring / dossier evidence.

Main gaps:

- Performance Recheck and symbol freshness depend on Current Candidate Registry replay contracts even though Final Review V2 decision row is the canonical selected source.
- Recheck readiness and symbol freshness are separate surfaces; stale / missing price should influence the same operations preflight route.
- Review Signals duplicates CAGR / MDD / benchmark spread thresholds already present in Recheck Comparison.
- Timeline, recheck result, drift check, and alert preview are session-state evidence, not durable monitoring history.

Implementation order now moves to 12-2 recheck readiness / freshness operations contract.

## 12-2 Recheck Readiness / Freshness Contract Result

12-2 added `selected_recheck_operations_preflight_v1`.

The contract combines:

- selected replay contract readiness
- DB latest market date
- default recheck period
- portfolio / benchmark symbol freshness
- read-only execution boundary

Replay contract source priority is now:

1. Final Review selected component embedded contract
2. Current Candidate Registry fallback by `registry_id`
3. Blocked when neither source can build a replay payload

The same resolver feeds readiness, symbol freshness symbol resolution, and Performance Recheck execution.
This prevents a preflight route from reporting ready when the later recheck execution cannot use the same contract.

Preflight route mapping:

| Route | Meaning |
| --- | --- |
| `RECHECK_PREFLIGHT_READY` | readiness and symbol freshness are ready |
| `RECHECK_PREFLIGHT_REVIEW` | recheck can run but stale / watch / review evidence needs confirmation |
| `RECHECK_PREFLIGHT_NEEDS_DATA` | missing price, DB latest date error, or data input gap needs action |
| `RECHECK_PREFLIGHT_BLOCKED` | selected replay contract or symbol resolution is blocked |

The contract adds no JSONL registry, monitoring log auto write, user memo, preset, approval, order, or auto rebalance path.

Implementation order now moves to 12-3 selected provider evidence staleness contract.

## 12-3 Selected Provider Evidence Staleness Contract Result

12-3 added `selected_provider_evidence_staleness_contract_v1` under the existing `selected_provider_evidence_v1` result.

Selected provider evidence now evaluates each provider row by the maximum severity of:

- diagnostic status
- coverage source
- coverage weight
- freshness

Required selected provider areas:

- `ETF Operability`
- `ETF Holdings`
- `ETF Exposure`

Policy mapping:

| Evidence | Selected Monitoring Status |
| --- | --- |
| fresh actual evidence with sufficient coverage | `PASS` |
| stale actual evidence | `REVIEW` |
| partial / bridge / proxy / mixed coverage | `REVIEW` |
| positive but less than 80% required coverage | `REVIEW` |
| missing required provider area or zero required coverage | `NEEDS_INPUT` |
| error / blocked provider evidence | `BLOCKED` |

The selected provider evidence result also adds a Look-through Coverage policy row so holdings / exposure board gaps cannot be hidden behind otherwise passing provider display rows.

The contract adds no provider collection, JSONL registry, monitoring log auto write, user memo, preset, approval, order, or auto rebalance path.

Implementation order now moves to 12-4 recheck comparison / review signal policy.

## 12-4 Recheck Comparison / Review Signal Policy Result

12-4 added `selected_review_signal_policy_v1`.

Review Signals now reads performance deterioration rows from Recheck Comparison instead of recalculating CAGR / MDD / benchmark spread thresholds in the Streamlit layer.

Policy inputs:

- Final Review evidence route and blockers
- Recheck Operations Preflight route
- Selected Provider Evidence route
- Recheck Comparison rows
- optional Actual Allocation drift check

Performance threshold ownership:

| Review Signals Row | Policy Owner |
| --- | --- |
| Performance Recheck input | Recheck Comparison |
| CAGR vs selected baseline | Recheck Comparison |
| MDD vs selected baseline | Recheck Comparison |
| Benchmark spread | Recheck Comparison |
| Component evidence coverage | Recheck Comparison |
| Recheck period coverage | Recheck Comparison |

Route mapping:

| Source | Route / Status | Review Signal Status |
| --- | --- | --- |
| Recheck Preflight | ready / review / needs data / blocked | `CLEAR` / `WATCH` / `NEEDS_INPUT` / `BREACHED` |
| Provider Evidence | ready / review / needs data / blocked | `CLEAR` / `WATCH` / `NEEDS_INPUT` / `BREACHED` |
| Recheck Comparison row | pass / watch / needs input / breached | `CLEAR` / `WATCH` / `NEEDS_INPUT` / `BREACHED` |
| Actual Allocation drift | not checked | `OPTIONAL` |

The policy adds no JSONL registry, monitoring log auto write, user memo, preset, approval, order, or auto rebalance path.

Implementation order now moves to 12-5 optional allocation drift evidence boundary.

## 12-5 Optional Allocation Drift Evidence Boundary Result

12-5 added `selected_allocation_drift_evidence_boundary_v1`.

The boundary combines:

- current weight input source
- drift evidence
- alert preview evidence
- storage boundary
- execution boundary

Boundary false fields are explicit:

- `db_write`
- `registry_write`
- `monitoring_log_auto_write`
- `input_persistence`
- `alert_persistence`
- `account_connection`
- `broker_sync`
- `live_approval`
- `order_instruction`
- `auto_rebalance`

Actual Allocation can still surface `WATCH` or `BREACHED` drift evidence, but breached drift means manual review signal only.
The Dashboard now labels the session-only action as `Reflect Session Signal` and shows an Allocation evidence boundary table.

The contract adds no JSONL registry, monitoring log auto write, raw holding input persistence, user memo, preset, account connection, broker sync, approval, order, or auto rebalance path.

Implementation order now moves to 12-6 decision dossier / continuity operations refinement.

## Route Semantics

| State | Meaning |
| --- | --- |
| `CLEAR` | 최신 evidence가 selected portfolio monitoring 조건을 지지 |
| `WATCH` | evidence는 있으나 staleness, 약화, partial coverage, drift가 있어 관찰 필요 |
| `NEEDS_INPUT` | recheck, DB price, provider evidence, component contract, allocation input 부족 |
| `BREACHED` | threshold 초과, baseline 훼손, blocker 재등장 등 재검토 필요 |
| `OPTIONAL` | 사용자가 입력하지 않아도 core monitoring 판단을 막지 않는 보조 evidence |

`NOT_RUN`은 pass가 아니다.
Performance Recheck 미실행, provider evidence 미수집, DB latest price 부족, continuity gap은 최소 `NEEDS_INPUT` 또는 `WATCH`로 남겨야 한다.

## Candidate Implementation Boundaries

초기 구현 후보는 아래 경계 안에서 다룬다.

- `app/runtime/final_selected_portfolios.py`: selected dashboard row, continuity, recheck readiness, symbol freshness, provider evidence, recheck comparison, drift, alert preview, timeline read model
- `app/web/final_selected_portfolio_dashboard.py`: dashboard render, Performance Recheck, monitoring tabs, optional allocation input
- `app/web/final_selected_portfolio_dashboard_helpers.py`: readiness / freshness / provider / comparison / drift / signal table display
- `app/services/backtest_evidence_read_model.py`: Final Review status, selected decision checks, dossier read model
- `app/web/backtest_final_review.py`: saved final decision and dossier source relationship 확인 후보
- `tests/test_service_contracts.py`: service contract 고정

## Data Boundary

- full price history는 DB / loader / runtime replay 영역에 둔다.
- provider holdings / exposure full row와 raw response는 DB 영역에 둔다.
- dashboard는 compact readiness, freshness, coverage, comparison, drift, signal evidence를 표시한다.
- monitoring timeline은 current decision row와 session-state recheck / drift / alert preview를 읽는 read model이다.
- user memo, preset, account integration, order draft, live approval, auto rebalance storage는 추가하지 않는다.

## User Flow Target

사용자는 기존 흐름을 유지한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Selected Portfolio Dashboard
```

Phase 12가 끝나면 사용자는 Operations에서 "선정 당시에는 통과했지만, 최신 데이터 / provider evidence / recheck / drift 기준으로 지금은 재검토해야 하는지"를 더 명확히 볼 수 있어야 한다.
