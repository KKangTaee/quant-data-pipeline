# Market Movers Sector React Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `섹터 / 시장 확산 맥락` and its detail table from Streamlit HTML / `st.expander` into the existing Market Movers React custom component.

**Architecture:** Reuse the existing `market_movers_workbench` Streamlit custom component and add a new `MarketMoversSectorBreadth` payload branch. Python remains the owner of the DB snapshot, sector breadth read model, and table serialization; React owns rendering, the 4-column lane layout, left-to-right bars, and the detail drawer. The legacy HTML renderer remains as a fallback when the built React bundle is unavailable.

**Tech Stack:** Python Streamlit helper layer, existing React / Vite custom component, service contract unittest, browser QA.

---

### Task 1: Contract And Payload

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/market_movers_helpers.py`

- [ ] **Step 1: Write the failing test**

Add a contract that calls `build_market_movers_sector_breadth_react_payload(source_model)` and verifies:

```python
payload["schema_version"] == "market_movers_sector_breadth_react_v1"
payload["component"] == "MarketMoversSectorBreadth"
payload["map"]["lanes"][1]["tone"] == "danger"
payload["map"]["lanes"][1]["bar_width_pct"] == 50
payload["detail_table"]["visible"] is True
payload["detail_table"]["default_open"] is False
payload["detail_table"]["columns"] == ["Sector", "Return %", "Advancers", "Decliners"]
payload["detail_table"]["rows"][0]["Sector"] == "Technology"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_react_payload_includes_map_and_detail_table
```

Expected: FAIL because `build_market_movers_sector_breadth_react_payload` does not exist.

- [ ] **Step 3: Write minimal implementation**

Add `build_market_movers_sector_breadth_react_payload(model)` that wraps `build_market_movers_sector_map_model(model)` and serializes `table_rows` using `_market_mover_sector_breadth_table(model).to_dict(orient="records")`.

- [ ] **Step 4: Run test to verify it passes**

Run the same focused unittest. Expected: PASS.

### Task 2: Render Boundary

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/market_movers_react_component.py`
- Modify: `app/web/overview/market_movers_helpers.py`

- [ ] **Step 1: Write the failing test**

Add a contract that verifies:

```python
"render_market_movers_sector_breadth_react" in wrapper_source
"_render_market_movers_sector_breadth_react(" in helper_source
"with st.expander(\"섹터 breadth 상세 표\"" not in render_body
"render_sector_breadth_market_map(" in fallback_body
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_sector_breadth_uses_react_with_html_fallback
```

Expected: FAIL because the sector context still renders HTML plus Streamlit expander directly.

- [ ] **Step 3: Write minimal implementation**

Add wrapper `render_market_movers_sector_breadth_react(payload, key=...)`. In `_render_market_movers_sector_breadth_context`, build the payload and call the React wrapper first. If it returns `None`, render the existing HTML map plus `st.expander` fallback.

- [ ] **Step 4: Run test to verify it passes**

Run the same focused unittest. Expected: PASS.

### Task 3: React Component And CSS

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/style.css`

- [ ] **Step 1: Write the failing test**

Extend source-contract assertions so React contains:

```text
MarketMoversSectorBreadth
payload.component === "MarketMoversSectorBreadth"
className="mm-sector-breadth"
className="mm-sector-breadth__detail"
grid-template-columns: repeat(4, minmax(0, 1fr));
.mm-sector-breadth__bar
```

- [ ] **Step 2: Run test to verify it fails**

Run the focused React source contract. Expected: FAIL because the branch and CSS do not exist.

- [ ] **Step 3: Write minimal implementation**

Add TypeScript types and a `MarketMoversSectorBreadth` renderer. It renders header, rail, three stats, lane grid, boundary note, and a `<details>` detail table. Bar color uses `toneColor(lane.tone)` and width uses `lane.bar_width_pct`; negative lanes still start from the left.

- [ ] **Step 4: Run test to verify it passes**

Run the focused React source contract. Expected: PASS.

### Task 4: Build, QA, Docs, Commit

**Files:**
- Modify: `app/web/streamlit_components/market_movers_workbench/component_static/*`
- Modify: this task's `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`

- [ ] Run focused unittests for payload/render/React contracts.
- [ ] Run broader `OverviewMarketIntelligenceServiceContractTests`.
- [ ] Run `npm run build` in `app/web/streamlit_components/market_movers_workbench`.
- [ ] Run `py_compile` for changed Python files and tests.
- [ ] Run `git diff --check`.
- [ ] Start Streamlit, verify in browser that the sector map is inside the React iframe, renders 4 columns, negative bars are red left-to-right, and the detail drawer exists inside the same component.
- [ ] Stage only source, tests, built component static assets, and task docs. Do not stage run history, `.DS_Store`, or local screenshots.
- [ ] Commit with a Korean message.
