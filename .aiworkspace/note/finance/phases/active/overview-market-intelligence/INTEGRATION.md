# Overview Market Intelligence Integration

## Files Expected To Change

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard_helpers.py`
- `app/web/overview_dashboard.py`
- `app/jobs/ingestion_jobs.py`
- `finance/data/market_intelligence.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`

## Integration Rules

- Do not mutate registry / saved / run history JSONL.
- Do not add remote fetches to Overview render code.
- Do not add paid API assumptions.
- Keep service Streamlit-free.
- Run UI-engine boundary check after implementation.

## First Slice Result

- Implemented and verified in `sub-dev`.
- Overview reads local DB snapshots only.
- Events tab reads `finance_meta.market_event_calendar` rows for FOMC and earnings prototype.

## Closeout Result

- Overview Market Intelligence has DB-backed Market Movers, Sector / Industry leadership, FOMC events, and bounded earnings prototype.
- Refresh operations are documented in `docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`.
- Future work should focus on visualization polish, earnings official-source validation, and event estimate cleanup rather than adding provider fetches to Overview render code.
