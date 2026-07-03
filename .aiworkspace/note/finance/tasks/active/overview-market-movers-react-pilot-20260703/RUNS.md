# Runs

## Phase 0 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_pilot_contract_defines_payload_and_actions`
  - Result: failed as expected with missing `build_market_movers_react_workbench_payload` import.
- GREEN: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_pilot_contract_defines_payload_and_actions`
  - Result: passed.
- `uv run python -m py_compile app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## Phase 1 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_component_scaffold_keeps_streamlit_fallback`
  - Result: failed as expected with missing `app.web.overview.market_movers_react_component`.
- GREEN: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_component_scaffold_keeps_streamlit_fallback`
  - Result: passed.
- `uv run python -m py_compile app/web/overview/market_movers_react_component.py app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## Phase 2 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_display_pilot_wraps_unified_summary_with_fallback`
  - Result: failed as expected before the helper routed the summary through `render_market_movers_react_workbench`.
- RED: same focused test after adding React render contract checks.
  - Result: failed as expected before `MarketMoversWorkbench.tsx` rendered the summary grid and actions.
- RED: same focused test after adding Vite relative asset contract.
  - Result: failed as expected before `vite.config.ts` set `base: "./"`.
- GREEN: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_pilot_contract_defines_payload_and_actions tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_component_scaffold_keeps_streamlit_fallback tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_display_pilot_wraps_unified_summary_with_fallback`
  - Result: passed.
- `uv run python -m py_compile app/web/overview/market_movers_helpers.py app/web/overview/market_movers_react_component.py`
  - Result: passed.
- `npm install`
  - Result: passed; created `package-lock.json`, 0 vulnerabilities.
- `npm run build`
  - Result: passed; generated `component_static/index.html`, `component_static/assets/index-ChyCXN4Q.css`, and `component_static/assets/index-BighDM1T.js`.
- `git diff --check`
  - Result: passed.
- Browser QA: Streamlit on `http://localhost:8531`, Overview > Market Movers.
  - Result: initially failed with a module MIME error because Vite emitted absolute `/assets/...` URLs.
  - Fix: set Vite `base: "./"` and rebuilt.
  - Retest result: passed; iframe width 1174, height 274, `rootChildren: 1`, text included `변동 종목`, `Universe`, `Returnable`, `Missing`, `일중 스냅샷 갱신`, `유니버스 갱신`, and `화면 새로고침`.
  - Screenshot: `.aiworkspace/note/finance/tasks/active/overview-market-movers-react-pilot-20260703/browser-qa-market-movers-react-phase2.png` (generated/local artifact; not staged).

## Phase 3 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_event_bridge_dispatches_existing_actions_once tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_component_emits_action_events`
  - Result: failed as expected before `_dispatch_market_movers_react_event` and `Streamlit.setComponentValue` existed.
- GREEN: same focused command.
  - Result: passed.
- `npm run build`
  - Result: passed; generated `component_static/index.html`, `component_static/assets/index-CqmWYMqX.css`, and `component_static/assets/index-C3BFdUbT.js`.
- `uv run python -m py_compile app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA: Streamlit on `http://localhost:8531`, Overview > Market Movers.
  - Result: passed; clicked only the React iframe `화면 새로고침` action, saw `Last DB snapshot reload request`, iframe remained 1174x274 and non-empty, console errors were empty.
  - Screenshot: `.aiworkspace/note/finance/tasks/active/overview-market-movers-react-pilot-20260703/browser-qa-market-movers-react-phase3.png` (generated/local artifact; not staged).

## Phase 4 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_action_strip_replaces_legacy_buttons_when_rendered`
  - Result: failed as expected before the React-rendered path guarded the legacy refresh bar.
- GREEN: same focused command.
  - Result: passed.
- `uv run python -m py_compile app/web/overview/market_movers_helpers.py`
  - Result: passed.
- Browser QA: Streamlit on `http://localhost:8531`, Overview > Market Movers.
  - Result: passed; parent Streamlit buttons matching `일중 스냅샷 갱신`, `유니버스 갱신`, and `화면 새로고침` were `[]`, iframe still included those action labels, console errors were empty.
  - Screenshot: `.aiworkspace/note/finance/tasks/active/overview-market-movers-react-pilot-20260703/browser-qa-market-movers-react-phase4.png` (generated/local artifact; not staged).

## Phase 5 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_controls_remain_streamlit_owned_for_pilot`
  - Result: failed as expected with missing `control_ownership`.
- GREEN: same focused command.
  - Result: passed.
- `npm run build`
  - Result: passed; generated `component_static/index.html`, `component_static/assets/index-CqmWYMqX.css`, and `component_static/assets/index-BXFIdWF2.js`.
- Browser QA: Streamlit on `http://localhost:8531`, Overview > Market Movers.
  - Result: passed; iframe rendered `data-control-mode="streamlit_owned"`, schema `market_movers_react_workbench_v1`, width 1174, height 274, and no console errors.
  - Screenshot: `.aiworkspace/note/finance/tasks/active/overview-market-movers-react-pilot-20260703/browser-qa-market-movers-react-phase5.png` (generated/local artifact; not staged).
