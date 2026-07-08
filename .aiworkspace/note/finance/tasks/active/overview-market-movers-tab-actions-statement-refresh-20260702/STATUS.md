# Status

- 2026-07-02: User approved splitting Market Movers investigation actions by tab and adding a targeted financial statement collection action in the SEC filing tab.
- 2026-07-02: Implemented tab-local News / SEC metadata actions, selected-symbol EDGAR statement refresh through `app/jobs/overview_actions.py`, and same-place elapsed-time result display in the SEC filing tab.
- 2026-07-02: Focused red-green tests, compact metadata regressions, and the broader OverviewAutomation / OverviewMarketIntelligence contract classes pass.
- 2026-07-02: Browser QA on `http://localhost:8502` confirmed News tab shows only the News metadata action, SEC tab shows SEC metadata and statement collection actions, the old combined action is absent, and no horizontal overflow appears at 1280px width. Live EDGAR collection was not executed during QA.
