# Market Research Editorial Navigation V2 Risks

Status: Design
Last Updated: 2026-07-22

## Open Risks

1. text tab 전환 뒤 button hit area가 너무 작아지지 않도록 vertical padding과 focus target을 실제 QA한다.
2. 420px에서 `지수 가치평가` full label과 3-column layout이 clipping되지 않는지 확인한다.
3. iframe width를 full content에 맞춘 뒤 desktop 우측 빈 공간이 어색하지 않은지 module alignment와 함께 확인한다.
4. active family underline과 active view fill이 theme light/dark에서 충분한 대비를 갖는지 확인한다.
5. CSS-only polish가 V1 changed-view rerun, URL/session/fallback을 건드리지 않도록 Python 회귀를 유지한다.

## Deferred

- command bar, left rail, drawer, sticky navigation
- recent/saved research
- module body redesign
