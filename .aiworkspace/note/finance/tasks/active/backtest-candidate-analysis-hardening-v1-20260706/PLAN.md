# Backtest Candidate Analysis Hardening V1 Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use inline execution with TDD and verification before each commit. Steps use checkbox syntax for tracking.

**Goal:** Backtest 후보분석에서 stale result, 불완전한 Data Trust handoff, Quality/Value preset ambiguity, Price Freshness Preflight prototype UI, and price-refresh stale-result UX를 1차부터 4차까지 순차적으로 고친다.

**Architecture:** Backtest Analysis remains the source creation surface. Data collection stays in `app/services/backtest_price_refresh.py` and existing ingestion jobs. UI changes stay in `app/web/*` and optional React components under `app/web/components/*`; service/gate decisions remain Streamlit-free where possible.

**Tech Stack:** Python 3.12, Streamlit, unittest, TypeScript React Streamlit custom components.

---

## Files

- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/backtest_result_display.py`
- Modify: `app/services/backtest_handoff_readiness.py`
- Modify: `app/web/backtest_common.py`
- Modify: `app/services/backtest_price_refresh.py`
- Create: `app/web/components/backtest_price_freshness_preflight/`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

## 1차: Stale Result / Data Trust Gate Safety

- [ ] Write failing tests for result staleness helper and `price_freshness.status` missing gate block.
- [ ] Verify the tests fail before implementation.
- [ ] Add a small result-display guard so selected strategy mismatch hides the previous bundle and asks for rerun.
- [ ] Treat missing / limited Data Trust as entry blocker for Practical Validation handoff.
- [ ] Run focused Python tests, compile affected modules, and `git diff --check`.
- [ ] Commit only 1차 files.

## 2차: Quality / Value Preset Basis

- [ ] Write failing tests for preset metadata and fallback/duplicate wider preset status.
- [ ] Verify the tests fail before implementation.
- [ ] Add preset metadata/read model helpers around existing `QUALITY_STRICT_PRESETS`.
- [ ] Render user-facing preset basis, actual count, fallback/staged state, and dynamic PIT scope note without changing strategy engine behavior.
- [ ] Run focused tests and compile affected modules.
- [ ] Commit only 2차 files.

## 3차: Price Freshness Preflight React Surface

- [ ] Write failing tests for preflight view model fields consumed by React.
- [ ] Verify the tests fail before implementation.
- [ ] Create `backtest_price_freshness_preflight` component following existing Streamlit custom component patterns.
- [ ] Replace the prototype Streamlit metric block with the React surface and keep Streamlit fallback.
- [ ] Run Python tests, component `npm run build`, compile, and browser QA if the app starts.
- [ ] Commit only 3차 files.

## 4차: Price Refresh Post-Run Stale UX

- [ ] Write failing tests for refresh result requiring a backtest rerun after DB update.
- [ ] Verify the tests fail before implementation.
- [ ] Mark the last result bundle as stale after a successful or partial price refresh and show a rerun-required state instead of implying updated performance.
- [ ] Keep refresh action DB-only; do not auto-run backtest, source registration, or 2차 handoff.
- [ ] Run focused tests, compile, UI/browser QA, and `git diff --check`.
- [ ] Commit only 4차 files.

## Done Criteria

- Strategy changes no longer show previous strategy results as current.
- Data Trust `자료 제한`, missing status, warning, error, excluded tickers, or malformed price rows block the 2차 검증 send button.
- Quality/Value preset basis is explicit and does not imply S&P latest 100 membership.
- Price Freshness Preflight renders through a product-style React surface with fallback.
- Price update completion clearly says the DB changed and the current result must be rerun.
- Durable docs explain the changed Backtest UI flow.
