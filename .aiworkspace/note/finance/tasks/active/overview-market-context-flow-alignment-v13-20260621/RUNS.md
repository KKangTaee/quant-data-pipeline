# Overview Market Context Flow Alignment V13 Runs

## 2026-06-21

### RED

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_market_context_historical_analog_can_reuse_visible_sector_snapshot \
  tests/test_service_contracts.py::OverviewMarketIntelligenceServiceContractTests::test_overview_breadth_heatmap_summary_keeps_full_canonical_sector_map \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_explains_similarity_before_statistics \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_prioritizes_matrix_and_collapses_stat_tables \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context -q
```

Outcome: failed as expected before implementation. Failures covered the missing `group_leadership_snapshot` contract, 10-sector / capped sector map behavior, and old guide-heavy historical analog copy.

### Focused GREEN

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_market_context_historical_analog_can_reuse_visible_sector_snapshot \
  tests/test_service_contracts.py::OverviewMarketIntelligenceServiceContractTests::test_overview_breadth_heatmap_summary_keeps_full_canonical_sector_map \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_explains_similarity_before_statistics \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_prioritizes_matrix_and_collapses_stat_tables \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot \
  tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_turns_insufficient_data_into_actionable_gap_panel -q
```

Outcome: `7 passed, 3 warnings`.

### Full Contract

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py -q
```

Outcome: `380 passed, 3 warnings`.

### Static Checks

```bash
git diff --check
uv run python -m py_compile app/services/overview_market_intelligence.py app/services/overview_market_context_analog.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/web/overview_dashboard.py
```

Outcome: both passed with no output.

### Live Model Check

```bash
uv run python - <<'PY'
from app.web.overview_dashboard_helpers import load_overview_macro_context_cockpit

model = load_overview_macro_context_cockpit(as_of_date=None, pattern_window='5D')
print("sector_count", len(model["sector_pressure"]["heatmap_rows"]))
print("sector_leader", model["sector_pressure"]["heatmap_rows"][0]["group"])
analog = model["historical_analog"]
print("analog_sector", analog.get("leadership_sector"), analog.get("proxy_etf"))
print("analog_status", analog.get("status"), analog.get("current_as_of"))
print("sample_count", analog.get("sample_count"))
print("macro_present", bool(analog.get("macro_conditioned_analog")))

for window in ["5D", "20D", "MONTHLY"]:
    model = load_overview_macro_context_cockpit(as_of_date=None, pattern_window=window)
    print(window, model["sector_pressure"]["heatmap_rows"][0]["group"], model["historical_analog"].get("leadership_sector"), model["historical_analog"].get("proxy_etf"), model["historical_analog"].get("status"), model["historical_analog"].get("sample_count"))

model = load_overview_macro_context_cockpit(as_of_date="2026-06-18", pattern_window="5D")
print("selected", model["historical_analog"].get("leadership_sector"), model["historical_analog"].get("proxy_etf"), model["historical_analog"].get("status"), model["historical_analog"].get("current_as_of"), model["historical_analog"].get("sample_count"))
PY
```

Outcome:

- latest sector map count: 11.
- latest visible sector leader: `Consumer Cyclical`.
- latest historical analog sector/proxy: `Consumer Cyclical` / `XLY`.
- latest historical analog status: `OK`, sample count 81, current as-of `2026-06-18`.
- pattern window changes kept the same latest sector/proxy and recalculated the sample window: 5D 81 samples, 20D 70 samples, monthly 73 samples.
- selected `2026-06-18` used bounded selected-date sector/proxy `Financials` / `XLF`, status `OK`, effective price basis `2026-06-16`, sample count 80.

### Browser QA

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Playwright QA on `http://localhost:8525` confirmed:

- Sector pressure map renders 11 equal sector tiles.
- Latest historical analog follows the visible `Consumer Cyclical` sector with proxy `XLY` and no longer falls back to stale `Basic Materials`.
- Default historical analog does not render `먼저 볼 점`, `주의할 점`, or `시장 배경 요약`.
- Macro comparison renders only after the broad analog has usable sample rows; the final QA state had sample count 81 and showed the compact comparison.
- QA screenshot: `overview-market-context-flow-alignment-v13-qa.png` (generated artifact, not staged).
