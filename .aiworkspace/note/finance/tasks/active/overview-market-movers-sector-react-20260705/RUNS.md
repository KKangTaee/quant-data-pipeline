# Overview Market Movers Sector React Migration Runs

## 2026-07-05

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_react_payload_includes_map_and_detail_table tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_uses_react_with_html_fallback tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_react_component_renders_map_and_detail_drawer
```

Result: RED first. The payload function, React wrapper, render boundary, and `MarketMoversSectorBreadth` branch did not exist.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_react_payload_includes_map_and_detail_table tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_uses_react_with_html_fallback tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_react_component_renders_map_and_detail_drawer
```

Result: GREEN after implementation (`3 OK`).

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
npm run build
```

Result: passed (`109 OK`), and Vite built `component_static/index.html`, `component_static/assets/index-CAw_1dqV.css`, and `component_static/assets/index-B6gQcnVP.js`.

```bash
.venv/bin/python -m py_compile app/web/overview/market_movers_helpers.py app/web/overview/market_movers_react_component.py tests/test_service_contracts.py
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
git diff --check
```

Result: passed (`249 OK` for the combined unittest command).

Browser QA: Streamlit on `http://localhost:8509`, Overview > Market Movers. Verified one `.mm-sector-breadth` React component, 11 `.mm-sector-breadth__lane` nodes, one `.mm-sector-breadth__detail` drawer, zero main-page `.ov-sector-breadth-map` nodes, 3 `.mm-sector-breadth__lane--negative` lanes, first negative style `--mm-sector-lane-tone: #dc2626; --mm-sector-lane-bar: 7%;`, and detail drawer opening to 12 table rows including the header. Screenshot captured at `market-movers-sector-react-qa.png` (generated/local artifact; not staged).
