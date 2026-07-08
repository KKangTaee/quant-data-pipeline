# Runs

## 2026-06-30 TDD Red

```bash
uv run python -m unittest tests.test_service_contracts -k "prefers_edgar_annual"
uv run python -m unittest tests.test_service_contracts -k "market_mover_research_snapshot_reads_existing_db_loaders"
uv run python -m unittest tests.test_service_contracts -k "market_mover_research_snapshot_model_formats_korean_metrics"
```

Expected failures:

- `build_market_mover_research_snapshot()` did not accept `statement_fundamentals_loader`.
- PER / EPS detail did not include EDGAR source evidence.

## 2026-06-30 Focused Green

```bash
uv run python -m unittest tests.test_service_contracts -k "prefers_edgar_annual"
uv run python -m unittest tests.test_service_contracts -k "market_mover_research_snapshot_reads_existing_db_loaders"
uv run python -m unittest tests.test_service_contracts -k "market_mover_research_snapshot_model_formats_korean_metrics"
```

Result: all selected tests passed.

## 2026-06-30 Phase Verification

### Compile

```bash
uv run python -m py_compile app/services/overview/why_it_moved.py app/web/overview/components/market_movers.py app/web/overview/market_movers_helpers.py
```

Result: exit 0.

### Guide-style filtered pytest

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "market_mover or why_it_moved or fundamental"
```

Result: exit 0, `68 passed, 422 deselected, 3 warnings`.

Warnings: existing `edgar` deprecation warnings.

### Whitespace

```bash
git diff --check
```

Result: exit 0.

### Streamlit / Browser QA

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Result: app served at `http://localhost:8525`.

Browser checks:

- Overview opened successfully.
- Market Movers selected.
- Selected-symbol research snapshot showed annual EDGAR source details.
- Quarterly 10-K row was shown only as blocked correction-needed evidence.
- Mobile viewport `390x844` check returned `itemCount=5`, `hasEdgar=true`, `hasQuarterlyBlock=true`, `overflowing=[]`.

Screenshot artifact:

```text
.aiworkspace/note/finance/run_artifacts/market_movers_edgar_source_mobile_20260630.png
```
