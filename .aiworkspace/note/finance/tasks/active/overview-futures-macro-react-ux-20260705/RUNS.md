# Overview Futures Macro React UX Runs

## 2026-07-05

```bash
.venv/bin/python - <<'PY'
from time import perf_counter
from app.services.futures_macro_thermometer import clear_overview_futures_macro_snapshot_cache, load_overview_futures_macro_snapshot

for include_validation in (False, True):
    clear_overview_futures_macro_snapshot_cache()
    t0 = perf_counter()
    snapshot = load_overview_futures_macro_snapshot(include_validation=include_validation, cache_ttl_seconds=0)
    dt = perf_counter() - t0
    coverage = snapshot.get("coverage") or {}
    validation = snapshot.get("validation") or {}
    print({
        "include_validation": include_validation,
        "seconds": round(dt, 3),
        "status": snapshot.get("status"),
        "daily_raw_rows": coverage.get("raw_rows"),
        "daily_symbols": coverage.get("symbol_count"),
        "validation_status": validation.get("status"),
        "validation_dates": (validation.get("coverage") or {}).get("validation_dates"),
    })
PY
```

Result: `include_validation=False` loaded in about 0.21s; `include_validation=True` loaded in about 7.59s with 1,221 validation dates.

### Phase 1 RED / GREEN

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_primary_tab_modules_own_tab_orchestration \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_tab_exposes_daily_refresh_and_cache_reload \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_symbol_extraction_accepts_snapshot_dataframe \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_routes_futures_macro_as_primary_tab
```

RED result: failed because the old tab contract still expected `detail_expanded=True`, the validation action CSS was absent, and `_futures_selected_symbols()` raised pandas DataFrame truth-value ambiguity.

GREEN result: passed after updating the contract, adding validation action CSS, and extracting symbols from the `Symbol` column when the snapshot symbol payload is a DataFrame.

### Phase 1 Focused QA

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests
.venv/bin/python -m py_compile app/web/overview/futures_macro.py app/web/overview/futures_macro_helpers.py app/web/overview/components/common.py app/services/futures_macro_thermometer.py app/services/futures_macro_validation.py tests/test_service_contracts.py
git diff --check
```

Result: Overview contract class passed 141 tests. `py_compile` and `git diff --check` passed.

### Phase 1 Timing Smoke

```bash
.venv/bin/python - <<'PY'
from time import perf_counter
from app.services.futures_macro_thermometer import clear_overview_futures_macro_snapshot_cache, load_overview_futures_macro_snapshot
from app.services.futures_macro_validation import build_futures_macro_validation_snapshot, build_interpretation_confidence

clear_overview_futures_macro_snapshot_cache()
t0 = perf_counter()
snapshot = load_overview_futures_macro_snapshot(include_validation=False, cache_ttl_seconds=0)
fast_dt = perf_counter() - t0
symbols_frame = snapshot.get("symbols")
symbols = list(dict.fromkeys(str(symbol) for symbol in symbols_frame["Symbol"].dropna().tolist()))
t1 = perf_counter()
validation = build_futures_macro_validation_snapshot(symbols=symbols, current_snapshot=snapshot)
confidence = build_interpretation_confidence(snapshot, validation)
print(round(fast_dt, 3), round(perf_counter() - t1, 3), validation.get("status"), confidence.get("label"))
PY
```

Result: fast snapshot `0.216s`, no validation payload in the fast snapshot, on-demand validation `7.613s`, validation `OK`, confidence `Low Confidence`, validation dates `1,221`.

### Phase 1 Browser QA

```bash
.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8517 --server.address 127.0.0.1 --server.headless true
```

Result: Browser QA confirmed Futures Macro tab shows `대기 · 탭 첫 진입은 현재 매크로만 빠르게 읽고...`, `과거 점검 불러오기` loads timestamped validation with 1,221 PIT dates, and `다시 읽기` clears the loaded session validation back to `대기`.

Screenshot: `browser-qa-futures-macro-phase1.png` in this task folder. It is a generated QA artifact and should remain uncommitted unless explicitly requested.

### Phase 2 RED / GREEN

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_workbench_payload_keeps_python_action_boundary \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_component_scaffold_keeps_streamlit_fallback
```

RED result: initially failed because the React source did not contain the explicit positive `payload.component === "FuturesMacroWorkbench"` guard expected by the scaffold contract.

GREEN result: passed after making the identity guard explicit.

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_component_scaffold_keeps_streamlit_fallback
```

RED result: failed after adding the `index.html` expectation because the Vite entry file was absent. `npm run build` also failed with `Could not resolve entry module "index.html"`.

GREEN result: passed after adding `app/web/streamlit_components/futures_macro_workbench/index.html`; `npm run build` then produced `component_static/index.html`, CSS, and JS assets.

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_event_payload_accepts_nested_and_direct_shapes
```

RED result: failed for direct event shape. GREEN result: passed after matching the existing Market Movers React bridge behavior and accepting nested or direct event payloads.

### Phase 2 Focused QA

```bash
cd app/web/streamlit_components/futures_macro_workbench
npm install
npm run build
```

Result: install audited 108 packages with 0 vulnerabilities. Build passed with 170 transformed modules and wrote `component_static/index.html`, `assets/index-VxsTOpyz.css`, and `assets/index-DCU9uHUo.js`.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests
.venv/bin/python -m py_compile app/web/overview/futures_macro.py app/web/overview/futures_macro_helpers.py app/web/overview/futures_macro_react_component.py app/web/overview/components/common.py tests/test_service_contracts.py
git diff --check
```

Result: Overview contract class passed 144 tests. `py_compile` and `git diff --check` passed.

### Phase 2 Snapshot Smoke

```bash
.venv/bin/python - <<'PY'
from app.services.futures_macro_thermometer import load_overview_futures_macro_snapshot
from app.web.overview.futures_macro_helpers import build_futures_macro_react_workbench_payload
from app.web.overview.futures_macro_react_component import futures_macro_react_component_available

macro = load_overview_futures_macro_snapshot(include_validation=False)
payload = build_futures_macro_react_workbench_payload(macro, validation={}, confidence={}, validation_loaded_at="")
print({
    "component_available": futures_macro_react_component_available(),
    "schema": payload["schema_version"],
    "scores": len(payload["scores"]),
    "flow_cards": len(payload["flow"]["cards"]),
    "evidence_sections": len(payload["evidence"]["sections"]),
    "validation_state": payload["validation"]["state"],
})
PY
```

Result: component available `True`, schema `futures_macro_react_workbench_v1`, 6 score chips, 5 flow cards, 4 evidence sections, validation state `대기`.

### Phase 2 Browser QA

```bash
.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8517 --server.headless true
```

Result: Browser QA confirmed the Futures Macro React iframe renders the workbench payload, `Futures Macro actions`, `과거 점검 불러오기`, lazy validation state, score chips, and 1W flow. The in-app Browser automation did not deliver iframe button clicks to the React handler / Python component return path, so click dispatch was not claimed from Browser QA; nested/direct event parsing and dispatch remain covered by unit contract.

Screenshot: `browser-qa-futures-macro-phase2.png` in this task folder. It is a generated QA artifact and should remain uncommitted unless explicitly requested.

### Phase 3 RED / GREEN

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_workbench_payload_keeps_python_action_boundary \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_component_scaffold_keeps_streamlit_fallback \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_thermometer_builds_flow_context_for_1w_and_1m_moves
```

RED result: failed because `flow_context` was absent from the macro read model, the React payload had no `default_period` / `periods`, and the component source had no flow period tab controls.

GREEN result: passed after adding `build_macro_flow_context(...)`, carrying `1W` / `1M` periods through the React payload, and rendering period tabs in the custom component.

### Phase 3 Focused QA

```bash
.venv/bin/python -m py_compile app/services/futures_macro_thermometer.py app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests
```

Result: `py_compile` passed, FuturesMacroThermometer contract class passed 17 tests, and OverviewAutomation contract class passed 144 tests.

```bash
cd app/web/streamlit_components/futures_macro_workbench
npm run build
```

Result: Vite build passed with 170 transformed modules and wrote the checked-in `component_static` bundle.

### Phase 3 Snapshot Smoke

```bash
.venv/bin/python - <<'PY'
from app.web.overview.futures_macro_helpers import build_futures_macro_react_workbench_payload, load_overview_futures_macro_snapshot

macro = load_overview_futures_macro_snapshot(include_validation=False)
payload = build_futures_macro_react_workbench_payload(macro, validation={}, confidence={}, validation_loaded_at="")
flow = payload.get("flow", {})
print({
    "component": payload.get("component"),
    "schema": payload.get("schema_version"),
    "flow_default": flow.get("default_period"),
    "flow_periods": [period.get("key") for period in flow.get("periods", [])],
    "period_titles": [period.get("title") for period in flow.get("periods", [])],
    "cards": len(flow.get("cards") or []),
})
PY
```

Result: component `FuturesMacroWorkbench`, schema `futures_macro_react_workbench_v1`, default `1W`, periods `['1W', '1M']`, titles `['최근 1주 흐름', '최근 1개월 흐름']`, and 5 default flow cards.

### Phase 3 Browser QA Attempt

Result: Streamlit server on port 8501 responded with HTTP 200, but the Codex In-app Browser tab API timed out when listing or reading tabs during Phase 3. No Phase 3 screenshot was captured. Unit contracts, React build, and snapshot smoke verify the 1W / 1M payload and component source, but iframe visual QA remains a final QA follow-up.

### Phase 4 RED / GREEN

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_risk_weakness_with_easing_rates \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_dollar_pressure_risk_off_candidate \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_commodity_weakness_as_demand_slowdown_candidate \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_conflicting_risk_on_and_safe_haven_as_transition \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_keeps_low_signal_mixed_context_distinct
```

RED result: failed against the previous implementation because the new subtype labels and new dollar-pressure / transition branches were absent.

GREEN result: passed after refining `_mixed_macro_context(...)` while keeping the top-level `혼재된 매크로 흐름` scenario.

### Phase 4 Focused QA

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_workbench_payload_keeps_python_action_boundary \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_weak_growth_without_safe_haven_confirmation \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_risk_weakness_with_easing_rates \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_dollar_pressure_risk_off_candidate \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_commodity_weakness_as_demand_slowdown_candidate \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_conflicting_risk_on_and_safe_haven_as_transition \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_keeps_low_signal_mixed_context_distinct \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_mixed_scenario_confidence_does_not_report_directional_hit_sample
```

Result: passed 8 tests.

```bash
.venv/bin/python -m py_compile app/services/futures_macro_thermometer.py tests/test_service_contracts.py
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests
git diff --check
```

Result: `py_compile` passed, FuturesMacroThermometer contract class passed 20 tests, OverviewAutomation contract class passed 144 tests, and `git diff --check` passed. Existing `edgar` deprecation warnings and Streamlit no-runtime cache warnings were present in the broader unittest output.
