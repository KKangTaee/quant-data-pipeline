# Overview Tab Module Split V1 Risks

- `app/web/overview/legacy_dashboard.py` still contains the large pre-split implementation. This is intentional for V1 compatibility, but it must not be treated as the final structure.
- Primary tab modules currently delegate to legacy helpers. V2 should move each tab's controls, session-state helpers, and render orchestration into the owning tab module.
- Existing tests still rely on several private helper contracts from `app.web.overview_dashboard`. The wrapper preserves those imports; V2/V3 should move tests toward public module contracts as helpers are relocated.
