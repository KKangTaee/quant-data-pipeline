# Futures Macro Decision UX V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Futures Macro가 활성 선물 세션의 최신 저장 관측을 우선하고, 자료가 없으면 최신 완료 일봉을 명확히 사용하며, 첫 화면에서 실제 1D/5D/20D 변화와 5D 검증 결론만 빠르게 읽히게 한다.

**Architecture:** 장중 collection trigger를 daily finalization probe에서 active trade-date resolver로 분리한다. Python payload는 결정적 family narrative와 정확한 publication copy를 소유하고 React는 compact hero, 결과 카드, 검증 gate를 렌더링한다. DB schema와 검증 임계값은 유지한다.

**Tech Stack:** Python 3.12, pytest, Streamlit, React 18, TypeScript 5.7, Vite 6, MySQL-backed stored futures OHLCV

## Global Constraints

- UI에서 provider를 직접 호출하지 않고 `action -> collector -> DB -> service -> React` 경계를 유지한다.
- 장중 provisional row는 completed snapshot 또는 forecast history에 저장하지 않는다.
- `NO_EDGE` publication threshold와 검증 계산은 변경하지 않는다.
- Futures variant CSS만 조정하고 다른 Research header를 회귀시키지 않는다.
- 사용자 소유 registry, run history, screenshots와 unrelated untracked files를 stage하지 않는다.

---

### Task 1: Active Trade-Date Refresh Routing

**Files:**
- Modify: `tests/test_overview_futures_macro_refresh.py`
- Modify: `app/jobs/overview_actions.py`

**Interfaces:**
- Consumes: `active_futures_session_date(evaluation_time: datetime) -> str | None`
- Produces: `run_overview_futures_daily_ohlcv(...)["details"]["intraday_refresh"]` with active session date and one bounded 5m collection

- [x] **Step 1: Write the failing Sunday-evening routing test**

Add a test whose `evaluation_time` is `2026-08-17 01:15 UTC` (Sunday 21:15 ET), whose daily
probe returns `future_session_not_eligible`, and assert collection calls are exactly
`[("1y", "1d"), ("2d", "5m")]`, `session_date == "2026-08-17"`, and the finalizer receives the
same 5m result.

- [x] **Step 2: Pin the inactive-session test to a deterministic closed time**

Change `test_no_pending_session_skips_five_minute_collection` to use Saturday
`2026-08-15 16:00 UTC` and keep its expectation that only daily collection runs.

- [x] **Step 3: Run RED**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_refresh.py::test_evening_active_trade_date_collects_intraday_when_daily_probe_is_not_eligible `

Expected: FAIL because current code only collects 5m when `session_state.status == "pending"`.

- [x] **Step 4: Implement the minimal routing change**

Import `active_futures_session_date` from `app.services.futures_macro_intraday`, calculate
`active_session_date = active_futures_session_date(evaluated_at)`, collect `2d/5m` whenever it is
not `None`, and use that date in `intraday_refresh`. Keep `session_probe` solely as finalization
evidence and preserve one-time reuse by `finalization_runner`.

- [x] **Step 5: Run GREEN**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_refresh.py `

Expected: all refresh/finalization tests pass.

### Task 2: Result-Only Short-Horizon Narrative

**Files:**
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `app/web/overview/futures_macro_helpers.py`

**Interfaces:**
- Produces: `_pattern_one_day_change_summary(rows) -> str`
- Produces: `_pattern_core_alignment_summary(rows) -> str`
- Produces: `_pattern_background_relationship_summary(rows) -> str`
- Produces: observation cards containing `key`, `title`, and `summary` only

- [x] **Step 1: Write failing narrative tests**

Assert the 1D card reports new/continuing/reversing family changes, the 5D card reports
aligned/mixed/single-axis/no-edge state, and the 20D card includes both continuation and reversal
when both are present. Assert every observation card omits `detail`.

- [x] **Step 2: Run RED**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_short_horizon.py::test_observation_cards_report_changes_without_instruction_copy `

Expected: FAIL because cards still contain instructional `detail` and 1D is only a phrase list.

- [x] **Step 3: Implement deterministic summaries**

Classify material 1D/5D pairs as new, reversed, or continuing; normalize core family polarity for
5D risk-supportive versus defensive alignment; and retain both aligned and reversed family names in
the 20D relationship. Replace confirmation copy ending in `확인합니다` with result statements.

- [x] **Step 4: Remove redundant payload detail**

Stop adding `detail` to `observation_cards`. Leave calculation scope in the decision payload for
the methodology disclosure and leave backend `change_conditions` available to other evidence
consumers.

- [x] **Step 5: Run GREEN**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_short_horizon.py `

Expected: all short-horizon payload tests pass.

### Task 3: Truthful Five-Day Validation Contract

**Files:**
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/ForecastValidationGate.tsx`

**Interfaces:**
- Produces: `NO_EDGE` title `검증 완료 · 향후 5거래일 예측 우위 없음`
- Produces: dynamic detail containing independent episodes, chronological evaluations, and baseline comparison

- [x] **Step 1: Write the failing publication-copy test**

For the 120-episode/325-evaluation fixture, assert `NO_EDGE` says validation is complete and the
detail includes both counts and that model error did not beat the baseline. Keep separate assertions
for `PROVISIONAL` and `UNAVAILABLE`.

- [x] **Step 2: Run RED**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_short_horizon.py::test_no_edge_copy_is_a_completed_negative_validation_result `

Expected: FAIL on the old `예측력 확인 안 됨` copy.

- [x] **Step 3: Implement status-specific detail**

Build `NO_EDGE`, `VERIFIED`, `PROVISIONAL`, and `UNAVAILABLE` detail after episode/evaluation values
are read. Do not change any publication status calculation.

- [x] **Step 4: Compact the React metrics**

Render validation date, independent episodes, chronological evaluations, and
`model_brier - baseline_brier` as `기본 대비 Brier`. Positive delta must be labeled worse because
lower Brier is better; null inputs render `-`.

- [x] **Step 5: Run focused Python and TypeScript build**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_short_horizon.py `

Then run:
` npm run build ` in `app/web/streamlit_components/futures_macro_workbench`.

Expected: pytest passes and Vite exits 0.

### Task 4: Compact Header And Explicit Latest-Available Fallback

**Files:**
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx`
- Modify: `app/web/streamlit_components/market_research_header/style.css`

**Interfaces:**
- Produces: `HeroPayload.fallback_reason?: string | null`
- Produces: Futures facts `현재 데이터`, `현재 기준`, `검증 기준`, `관측 범위`

- [x] **Step 1: Write failing hero/fallback contract tests**

Assert completed fallback exposes `fallback_reason`, the Futures header uses only two evidence meta
items, and source contains a `새 장중 관측이 없어` notice path.

- [x] **Step 2: Run RED**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_short_horizon.py::test_completed_fallback_exposes_latest_available_reason `

Expected: FAIL because `fallback_reason` is not part of the hero payload.

- [x] **Step 3: Implement compact hero payload and rendering**

Pass `fallback_reason` into the hero. Format intraday ET observation time for `현재 기준`; otherwise
use the completed date. Remove command detail from meta and cap evidence at two. Show the fallback
notice only when an active session was attempted but eligible current bars were unavailable.

- [x] **Step 4: Add Futures-only CSS variant**

Set the Futures grid to top alignment, compact padding/gaps, and 2x2 facts. Add explicit 760px and
480px Futures overrides so shared responsive rules remain intact.

- [x] **Step 5: Run focused tests and build**

Run the short-horizon pytest file and the component `npm run build`; both must exit 0.

### Task 5: Remove Next Check And Move Scope To Methodology

**Files:**
- Delete: `app/web/streamlit_components/futures_macro_workbench/src/CalculationScopeSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/ShortHorizonDecisionSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MethodDisclosure.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_futures_macro_v2_integration.py`

**Interfaces:**
- Consumes: `ShortHorizonDecisionPayload.calculation_scope`
- Produces: `MethodDisclosure` prop `scope: CalculationScope`
- Produces: payload schema `futures_macro_react_workbench_v6`

- [x] **Step 1: Write failing source-contract tests**

Assert `CalculationScopeSection` is absent from the root render/imports, the short-horizon source
does not render `observation_windows` or `card.detail`, and `MethodDisclosure` receives
`calculation_scope`.

- [x] **Step 2: Run RED**

Run the named short-horizon source-contract tests and confirm they fail on the existing primary
Next Check section.

- [x] **Step 3: Implement the UI hierarchy**

Remove the redundant reading guide and instructional detail, delete the Next Check component, pass
scope into MethodDisclosure, and render one compact methodology scope note. Remove obsolete CSS.

- [x] **Step 4: Bump the internal payload schema**

Change Python and TypeScript schema literals from v5 to v6 and update focused integration/service
contract expectations.

- [x] **Step 5: Run GREEN and build**

Run:
` .venv/bin/python -m pytest -q tests/test_overview_futures_macro_short_horizon.py tests/test_futures_macro_v2_integration.py `

Run the changed Futures Macro nodes in `tests/test_service_contracts.py`, then run `npm run build`.

Expected: all selected tests pass and the production bundle is rebuilt.

### Task 6: Verification, Browser QA, And Documentation Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/futures-macro-decision-ux-v2-20260817/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/futures-macro-decision-ux-v2-20260817/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/futures-macro-decision-ux-v2-20260817/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/futures-macro-decision-ux-v2-20260817/RISKS.md`
- Review: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Review: `.aiworkspace/note/finance/docs/data/README.md`

**Interfaces:**
- Produces: task closeout evidence and one untracked QA screenshot

- [x] **Step 1: Run full focused regression**

Run the refresh, intraday, short-horizon, snapshot, pattern validation, and v2 integration suites.
Run `py_compile` for changed Python modules, `npm run build`, and `git diff --check`.

- [x] **Step 2: Verify actual stored-data behavior**

Read the current materialized snapshot and intraday observation without mutating forecast history.
Confirm the displayed current/completed dates and `NO_EDGE` evidence are consistent.

- [x] **Step 3: Perform Browser QA**

Open Futures Macro, run the approved latest-data action if safe, and verify desktop plus narrow
layout, no console errors, no horizontal overflow, compact hero, result-only cards, accurate gate,
and absent Next Check. Save one screenshot outside staged files.

- [x] **Step 4: Sync task and durable docs**

Record exact commands/results. Update canonical docs only if implemented ownership/data semantics
changed; otherwise record `canonical doc change 없음` because this task refines existing workflow
and UI contracts without changing table meaning.

- [x] **Step 5: Review and commit**

Review the scoped diff against DESIGN.md, address Critical/Important findings, stage only task-owned
files, and create a Korean coherent feature commit.
