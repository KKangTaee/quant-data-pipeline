# Phase 12 Selected Monitoring / Recheck Operations Risks

Status: Complete
Created: 2026-05-29

## Risks

- Selected Portfolio Dashboard가 운영 화면이라는 이유로 live approval, order, rebalance 기능처럼 오해될 수 있다.
- monitoring timeline이나 review signal을 자동 저장하면 사용자가 원하지 않은 log sprawl이 다시 생길 수 있다.
- Performance Recheck 미실행 또는 실패가 `CLEAR`처럼 보이면 선정 이후 위험이 숨겨진다.
- stale price data 또는 stale provider snapshot이 충분한 evidence처럼 보일 수 있다.
- optional actual allocation input이 account integration이나 broker order draft로 확장될 수 있다.
- `FINAL_PORTFOLIO_SELECTION_DECISIONS` legacy naming과 V2 registry naming이 문서 / runtime에서 혼재할 수 있다.

## Mitigation

- Start with `selected-monitoring-source-map-v1` before implementation.
- 12-2 added a shared recheck operations preflight so missing replay contract, stale / missing price, and DB latest date errors do not route to ready.
- 12-3 added selected provider evidence freshness / coverage policy so stale actual evidence, partial / proxy / bridge coverage, and missing required provider areas do not route to pass.
- 12-4 added selected review signal policy so CAGR / MDD / benchmark spread thresholds are owned by Recheck Comparison and preflight / provider route gaps appear in Review Signals.
- 12-5 added selected allocation drift evidence boundary so actual allocation drift / alert preview remains manual, session-only evidence with no storage, account, broker, order, or auto rebalance behavior.
- 12-6 added selected decision source consistency so Decision Dossier, Continuity, Timeline, and Review Signals expose the same Final Decision V2 source and session evidence boundary.
- Continuity blocks missing or mismatched timeline source contracts, and Decision Dossier markdown labels timeline contract consistency.
- 12-7 integrated QA confirmed compile, full service contracts, UI / engine boundary, hygiene, diff, docs, and storage boundary checks.
- Keep Selected Portfolio Dashboard read-only unless a later task explicitly changes scope and user confirms it.
- Treat missing / failed / stale / partial evidence as `NEEDS_INPUT`, `WATCH`, or `BREACHED`, not pass.
- Keep all full provider / holdings / macro / price data in DB or runtime calculation boundaries.
- Do not add monitoring log automatic append, user memo, preset, account integration, approval, order, or auto rebalance paths.
- Source map must identify current V1 / V2 final decision registry naming and document the canonical path before code changes.
