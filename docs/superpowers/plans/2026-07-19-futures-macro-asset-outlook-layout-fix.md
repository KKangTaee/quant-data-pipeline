# Futures Macro Asset Outlook Layout Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move shared 5D / 20D publication statuses to the asset section heading and restore readable two-column asset outlook rows.

**Architecture:** `AssetPathwaysSection` derives the two horizon statuses once from the first pathway because every pathway inherits the same horizon-level publication status. A section-level status rail owns those badges; each card keeps only its pathway-specific direction. CSS gives the rail responsive wrapping and the card rows two columns with non-breaking direction text.

**Tech Stack:** React 18, TypeScript, CSS, Python `unittest` source contracts, Vite, Streamlit custom component, Browser QA.

## Global Constraints

- Keep the visible status token `PROVISIONAL`; do not translate or promote it.
- Keep the asset direction threshold at `±0.25` standardized median movement.
- Do not change the probability model, path model, validation gates, Python payload, DB schema, provider, ingestion, or materialization.
- Preserve current observation badges and future `five_day_status` / `twenty_day_status` payload fields.
- Preserve unrelated untracked research and `.superpowers/` content.

---

## File Structure

- Modify `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`: move shared future statuses from each card to one section-level rail.
- Modify `app/web/streamlit_components/futures_macro_workbench/src/style.css`: style the section rail and reduce each future row to a readable two-column grid.
- Modify `tests/test_service_contracts.py`: lock status ownership and non-breaking layout source contracts.
- Rebuild `app/web/streamlit_components/futures_macro_workbench/component_static/`: publish the approved React/CSS change.
- Update `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/{STATUS,RUNS}.md`: record root cause, unchanged semantics, tests, and Browser QA.

### Task 1: Section-Owned Outlook Status And Readable Card Rows

**Files:**
- Modify: `tests/test_service_contracts.py:8344-8363`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx:4-40`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css:270-284,315-340`

**Interfaces:**
- Consumes: `AssetPathwayPayload[]`, including `outlook.five_day_status`, `outlook.twenty_day_status`, `outlook.five_day`, and `outlook.twenty_day`.
- Produces: one `.fm-workbench__asset-status-rail` with horizon-level status badges and card rows containing only period plus pathway direction.

- [ ] **Step 1: Write the failing source contract**

Extend `test_futures_macro_react_separates_observation_and_outlook_statuses` with:

```python
        style = (root / "style.css").read_text(encoding="utf-8")
        self.assertIn('className="fm-workbench__asset-status-rail"', assets)
        self.assertIn("5D 전체 전망 ·", assets)
        self.assertIn("20D 전체 전망 ·", assets)
        self.assertIn("pathways[0]?.outlook.five_day_status", assets)
        self.assertIn("pathways[0]?.outlook.twenty_day_status", assets)
        self.assertNotIn("item.outlook.five_day_status", assets)
        self.assertNotIn("item.outlook.twenty_day_status", assets)
        self.assertIn(".fm-workbench__asset-status-rail", style)
        self.assertIn("grid-template-columns: auto minmax(0, 1fr)", style)
        self.assertIn("white-space: nowrap", style)
```

Keep the existing checks for `five_day_status`, `twenty_day_status`, observation labels, and absence of the legacy card-wide `estimate_status`.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
.venv/bin/python -m unittest -v tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses
```

Expected: FAIL because `.fm-workbench__asset-status-rail` and `pathways[0]?.outlook.*_status` do not exist and the card still references `item.outlook.*_status`.

- [ ] **Step 3: Implement section-level status ownership**

At the top of `AssetPathwaysSection`, derive the shared horizon statuses:

```tsx
  const fiveDayStatus = pathways[0]?.outlook.five_day_status;
  const twentyDayStatus = pathways[0]?.outlook.twenty_day_status;
```

Replace the heading's right-side `<small>` with:

```tsx
        <div className="fm-workbench__asset-heading-meta">
          <small>전체 체제의 보조 근거</small>
          {(fiveDayStatus || twentyDayStatus) && (
            <div className="fm-workbench__asset-status-rail" aria-label="전체 전망 상태">
              {fiveDayStatus && (
                <b className={`estimate-${fiveDayStatus.toLowerCase()}`}>
                  5D 전체 전망 · {fiveDayStatus}
                </b>
              )}
              {twentyDayStatus && (
                <b className={`estimate-${twentyDayStatus.toLowerCase()}`}>
                  20D 전체 전망 · {twentyDayStatus}
                </b>
              )}
            </div>
          )}
        </div>
```

Remove both per-card `<b>` elements so each outlook row is exactly:

```tsx
              <span>
                <small>다음 5D</small>
                <strong>{item.outlook.five_day}</strong>
              </span>
```

and the equivalent 20D row.

- [ ] **Step 4: Implement the minimal responsive CSS**

Replace the current three-column asset outlook and per-card badge rules with:

```css
.fm-workbench__asset-heading-meta { align-items: end; display: grid; gap: 7px; justify-items: end; }
.fm-workbench__asset-heading-meta > small { color: var(--muted); font-size: 0.76rem; line-height: 1.45; text-align: right; }
.fm-workbench__asset-status-rail { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; }
.fm-workbench__asset-status-rail b { background: #fff7e8; border-radius: 999px; color: #9b681a; font-size: 0.55rem; padding: 4px 7px; white-space: nowrap; }
.fm-workbench__asset-status-rail b.estimate-verified { background: #e9f7f1; color: #24795d; }
.fm-workbench__asset-status-rail b.estimate-unavailable { background: #eef2f5; color: #667888; }
.fm-workbench__asset-outlook span { align-items: center; color: var(--muted); display: grid; font-size: 0.66rem; gap: 7px; grid-template-columns: auto minmax(0, 1fr); }
.fm-workbench__asset-outlook small { color: var(--muted); font-size: 0.62rem; white-space: nowrap; }
.fm-workbench__asset-outlook strong { color: #40566a; justify-self: end; white-space: nowrap; }
```

Add inside `@media (max-width: 760px)`:

```css
  .fm-workbench__asset-heading-meta { align-self: stretch; justify-items: start; }
  .fm-workbench__asset-heading-meta > small { text-align: left; }
  .fm-workbench__asset-status-rail { justify-content: flex-start; }
```

- [ ] **Step 5: Run focused GREEN and related payload separation tests**

Run:

```bash
.venv/bin/python -m unittest -v tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons
```

Expected: 2 tests pass.

- [ ] **Step 6: Build the production component**

Run:

```bash
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
```

Expected: Vite exits 0 and emits updated hashed CSS / JS assets under `component_static/assets/`.

- [ ] **Step 7: Commit the independently testable UI fix**

```bash
git add tests/test_service_contracts.py app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx app/web/streamlit_components/futures_macro_workbench/src/style.css app/web/streamlit_components/futures_macro_workbench/component_static
git commit -m "선물 매크로 자산 전망 배치 정리"
```

### Task 2: Actual Browser QA And Durable Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md`

**Interfaces:**
- Consumes: the production custom component built in Task 1 and the current DB-only V4 snapshot.
- Produces: evidence that shared statuses appear once, card directions remain readable, semantics are unchanged, and desktop/mobile layouts do not overflow.

- [ ] **Step 1: Start a fresh sub-dev Streamlit server**

Run on port `8568` with headless Streamlit, hot reload disabled, and no change to other worktree servers.

- [ ] **Step 2: Verify the actual desktop UI**

Using the Browser skill, select `선물 매크로 · Futures Macro` and confirm:

1. Exactly one `5D 전체 전망 · PROVISIONAL` and one `20D 전체 전망 · PROVISIONAL` appear in the asset section.
2. All five card headers show `관측 완료`.
3. Cards contain five 5D and five 20D pathway directions without per-card status badges.
4. `우위 미확인` and `상방 우세` render as whole phrases rather than one character per line.
5. The document and component have no horizontal overflow and browser console errors are zero.

- [ ] **Step 3: Verify 420px responsive behavior and save one QA screenshot**

Set the Browser viewport to `420×900`, verify status-rail wrapping and intact direction phrases, then reset the viewport. Save the desktop screenshot outside the repository at:

```text
/Users/taeho/.codex/visualizations/2026/07/19/futures-macro-asset-outlook-layout/futures-macro-asset-outlook-layout-qa.png
```

- [ ] **Step 4: Update task closeout docs**

Add a dated section to `STATUS.md` and `RUNS.md` recording:

```text
- Root cause: the repeated horizon-level badge consumed the third grid column inside each five-column asset card.
- Fix: 5D / 20D publication status moved to one section-level rail; cards retain only pathway-specific direction.
- Semantics unchanged: PROVISIONAL remains the valid horizon status; ±0.25 direction thresholds and current snapshot values are unchanged.
- Verification: focused RED/GREEN, regression tests, Vite build, desktop / 420px Browser QA, no overflow, zero console errors.
```

- [ ] **Step 5: Run final fresh verification**

Run:

```bash
.venv/bin/python -m unittest -v tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation tests.test_futures_macro_snapshot tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_ribbon_has_visible_regime_legend tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py app/services/futures_macro_snapshot.py
git diff --check
```

Expected: 67 tests pass, Vite exits 0, py_compile exits 0, and `git diff --check` exits 0.

- [ ] **Step 6: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md
git commit -m "선물 매크로 자산 전망 배치 QA 마무리"
```
