# Institutional Portfolios Context-First Redesign V1 Status

Status: Completed
Started: 2026-07-18

## Progress

- 2026-07-18: 1차 current product / code / actual UI audit completed.
- 2026-07-18: User confirmed that the default first screen should prioritize understanding the selected manager's portfolio context over manager comparison / discovery.
- 2026-07-18: 2차 written design drafted for context-first IA, complete holdings explorer, explicit security search, mapping coverage, change-board correctness, responsive states, and QA.
- 2026-07-18: 3차 implementation completed with `institutional_portfolios_workbench_v2`, deterministic context summary, separated coverage, gated comparison state, 50-row full holdings explorer, explicit security search, and unresolved security state.
- 2026-07-18: 4차 actual DB and Browser QA completed for Berkshire / Bridgewater / Duquesne, desktop and 420px responsive layout, mapped / unresolved security flow, and durable documentation.
- 2026-07-18: Reviewer follow-up 420px interaction QA confirmed primary / secondary tab navigation, holdings mapping filter, issuer / CUSIP unresolved guardrail with no price action, and AAPL mapped detail / chart flow. Canonical roadmap pointer and full-row serialization latency risk were aligned without implementation code changes.

## Current Step

전체 roadmap `4/4` complete.

Bridgewater actual payload의 `993` holding row가 explorer `993` row와 일치하고, 50-row pagination으로 `1–50 / 993`, `51–100 / 993`을 확인했다. 이전 분기가 없는 actual manager는 change groups를 표시하지 않는다.

## Next Action

별도 후속 승인이 있으면 historical filing backfill 또는 verified security master를 독립 task로 연다. 현재 맥락 우선 개편은 추가 provider 없이 완료 상태다.

## Current Scope Boundary

- 이번 task는 service / Streamlit event boundary / React workbench / focused test / Browser QA / durable docs를 소유했다.
- historical quarter backfill, external security master, paid provider, chart library migration은 승인된 구현 범위가 아니다.
