# Runs

- 2026-05-30: `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py tests/test_service_contracts.py` - PASS.
- 2026-05-30: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` - PASS, 12 tests.
- 2026-05-30: `uv run python -m unittest tests.test_service_contracts` - PASS, 73 tests.
- 2026-05-30: `git diff --check` - PASS.
- 2026-05-30: Browser smoke at `http://localhost:8501` Events tab - PASS; source lane, summary strip, `Agenda / Calendar / Quality / Raw`, calendar grid, quality view, no leaked HTML, console errors 0.
- 2026-05-30: Browser smoke rerun after source-lane filter adjustment - PASS; Events tab rendered, source lane and summary strip present, short refresh labels present, no leaked HTML, console errors 0.
- 2026-05-30: `uv run python -m py_compile app/web/overview_dashboard.py` - PASS.
- 2026-05-30: Browser smoke at 1000px viewport - PASS; Type and Window render as selectboxes, refresh buttons remain visible, no segmented option wrapping, console errors 0.
- 2026-05-30: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` - PASS, 12 tests.
- 2026-05-30: `git diff --check` - PASS.
- 2026-05-30: `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py` - PASS.
- 2026-05-30: Browser smoke at 1300px and 1000px viewports - PASS; top summary, source lane metrics, calendar topbar, legend, event count badges rendered; no leaked HTML, no horizontal overflow, console errors 0.
- 2026-05-30: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests` - PASS, 12 tests.
- 2026-05-30: `git diff --check` - PASS.
