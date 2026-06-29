# Design

## Read Model

`build_overview_source_confidence_catalog()`를 `app/services/overview_market_intelligence.py`에 추가한다.

Input은 기존 cockpit이 이미 사용하는 snapshots다.

- Market Movers snapshot
- Group Leadership snapshot
- Futures Macro snapshot
- Sentiment snapshot
- Events snapshot
- Collection Ops snapshot

Output은 `schema_version`, `status`, `summary`, `items`, `next_checks`, `boundary_note`를 가진 dict다. 이 모델은 DB fetch, provider fetch, write side effect가 없다. `build_overview_macro_context_cockpit()`가 기존 snapshots를 만든 뒤 catalog를 함께 넣는다.

## UI Placement

`render_macro_context_cockpit()` 안에서 `Next Deep Tabs` 아래, cockpit boundary 위에 `Source Confidence` compact lane을 둔다. 첫 화면 문맥 안에서 source / freshness를 읽게 하되, deep tab 자체를 대체하지 않는다.

## Status Semantics

- `OK`: source row가 fresh / official / available로 읽히며 review count가 없다.
- `REVIEW`: stale, due, estimate-only, missing, partial, failed, needs review가 있거나 data-health review target이 있다.
- `NO_DATA`: snapshot rows가 없다.

이 status는 data trust context일 뿐 validation PASS/BLOCKER나 monitoring signal이 아니다.
