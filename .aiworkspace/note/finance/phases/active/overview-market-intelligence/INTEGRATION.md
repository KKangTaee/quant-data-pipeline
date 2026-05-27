# Overview Market Intelligence Integration

## Files Expected To Change

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard_helpers.py`
- `app/web/overview_dashboard.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`

## Integration Rules

- Do not mutate registry / saved / run history JSONL.
- Do not add remote fetches to Overview render code.
- Do not add paid API assumptions.
- Keep service Streamlit-free.
- Run UI-engine boundary check after implementation.

## First Slice Result

- Implemented and verified in `sub-dev`.
- Overview reads local DB snapshots only.
- Events tab is intentionally a placeholder until FOMC / earnings ingestion is implemented.
