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
| Source map | 현재 Selected Dashboard evidence와 runtime read model의 source ownership 확인 | Next: `selected-monitoring-source-map-v1` |
| Recheck readiness | DB latest market date, benchmark, replay contract, default period 확인 | Existing `app/runtime/final_selected_portfolios.py` readiness read model |
| Symbol freshness | portfolio / benchmark ticker별 DB latest date, row count, stale status 확인 | Existing selected dashboard symbol freshness table |
| Provider evidence | selected component ticker weight 기준 provider holdings / exposure / operability context 확인 | Existing DB provider loader / dashboard provider evidence |
| Recheck comparison | latest recheck result와 Final Review baseline 비교 | Existing comparison helper, policy refinement pending |
| Review signals | recheck, provider, drift, continuity 상태를 hold / watch / re-review signal로 번역 | Existing Review Signals surface, policy refinement pending |
| Allocation drift | 사용자가 명시 입력한 current value / holding 기반 drift 확인 | Existing optional input, read-only boundary refinement pending |
| Continuity / dossier | Final Review evidence packet, selected route, timeline, trigger, dossier 연결 확인 | Existing continuity check and Decision Dossier |

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
