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
