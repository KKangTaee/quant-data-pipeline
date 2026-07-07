# Events Calendar Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use inline TDD and verification for each phase. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Events calendar easier to read by clarifying the selected month, daily counts, date detail, and weekly density meaning.

**Architecture:** Python continues to own DB reads and structured event payloads. React owns display, local filtering, month navigation, selected-date interaction, and density labeling. No provider fetch, trading signal, validation gate, monitoring signal, or automatic action is added.

**Tech Stack:** Python service contracts, Streamlit custom component wrapper, React/Vite/TypeScript, CSS, Browser QA.

---

### Task 1: Month Recognition

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx`
- Modify: `app/web/streamlit_components/events_workbench/src/style.css`

- [ ] Add a failing React source contract that expects month navigation controls, a Korean month title, selected-month summary text, and stronger out-of-month styling.
- [ ] Implement month title formatting, previous/next month buttons, selected-month event/date counts, and clearer muted out-of-month cells.
- [ ] Run focused contract tests, TypeScript/Vite build, and diff check.
- [ ] Commit only source/test/task-doc files.

### Task 2: Date Detail Interaction

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx`
- Modify: `app/web/streamlit_components/events_workbench/src/style.css`

- [ ] Add a failing React source contract for selected-date state, clickable calendar cells, a fixed date-detail panel, and richer tooltip/detail fields.
- [ ] Implement selected-date state, clickable day cells, keyboard accessible button semantics, detail cards with event title/status/source metadata, and concise hover tooltip.
- [ ] Run focused contract tests, TypeScript/Vite build, and diff check.
- [ ] Commit only source/test/task-doc files.

### Task 3: Weekly Density Meaning

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/events.py`
- Modify: `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx`
- Modify: `app/web/streamlit_components/events_workbench/src/style.css`

- [ ] Add failing service/React contracts for `week_end`, Korean range labels, and density explanation copy.
- [ ] Add `week_end` and display labels to weekly density payload, then render `7/27-8/2` style ranges with `총 N건` and a legend explaining the bars are weekly totals.
- [ ] Run focused service and React contracts, py_compile, TypeScript/Vite build, Browser QA screenshot, and diff check.
- [ ] Update task STATUS/RUNS and commit only source/test/task-doc files.
