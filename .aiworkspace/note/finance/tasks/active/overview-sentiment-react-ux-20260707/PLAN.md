# Overview Sentiment React UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task in the current `codex/sub-dev` worktree. Do not create a new branch for this task.

**Goal:** Improve `Workspace > Overview > Sentiment` into a React-backed, summary-first market sentiment reading surface while keeping DB reads, refresh actions, and interpretation in Python services.

**Architecture:** Python continues to own `finance/data/sentiment.py`, `finance/loaders/sentiment.py`, `app/services/overview/sentiment.py`, and Overview refresh actions. `app/web/overview/sentiment_helpers.py` will adapt the existing snapshot into a serializable React payload, dispatch React events back to Python, and keep Streamlit fallback/raw evidence sections. React will render display and lightweight interaction only.

**Tech Stack:** Streamlit custom component, React/Vite/TypeScript, Pandas/Altair fallback charts, existing Overview service/read-model tests.

---

## 이걸 하는 이유?

현재 Sentiment 탭은 `analysis`, `driver_groups`, `component_explanations`, `next_checks`, `rows`, `component_rows`, `history_rows`를 이미 갖고 있지만 Streamlit 카드/탭으로 분산되어 있다. 사용자는 먼저 "현재 시장 심리가 어떤 상태인지", "무엇이 그 상태를 만들었는지", "데이터가 최신인지", "다음에 무엇을 확인해야 하는지"를 읽어야 한다. 이번 작업은 원천 데이터와 해석 소유권을 바꾸지 않고, 화면 구조를 판단 흐름 중심으로 바꾸는 React 프로토타입이다.

## Boundaries

- 새 브랜치를 만들지 않는다.
- React는 새 해석 문구를 만들지 않는다.
- 모든 판단/문구는 `app/services/overview/sentiment.py`의 `analysis`, `driver_groups`, `component_explanations`, `next_checks`, `rows`, `component_rows`, `history_rows` 기반으로만 렌더링한다.
- `시장 심리 갱신`은 `app/jobs/overview_actions.py` facade를 통해서만 실행한다.
- UI render 중 CNN/AAII/provider를 직접 fetch하지 않는다.
- Sentiment는 시장 배경 / 조사 단서이며 validation gate, 매수/매도 신호, monitoring signal, broker order, auto rebalance가 아니다.
- generated artifact, run_history, QA screenshot, `.DS_Store`는 명시 요청 없이는 stage/commit하지 않는다.

## Files

- Modify: `app/web/overview/sentiment.py`
- Modify: `app/web/overview/sentiment_helpers.py`
- Create: `app/web/overview/sentiment_react_component.py`
- Create: `app/web/streamlit_components/sentiment_workbench/`
- Modify: `tests/test_service_contracts.py`
- Update during closeout: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Update during closeout: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Update during closeout: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Update during closeout: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Update during closeout: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

## Roadmap

### 1차: Contract / Payload Design

Purpose: Freeze the React boundary before UI implementation.

Scope:
- Add active task records.
- Add tests for a serializable `sentiment_react_workbench_v1` payload.
- Add minimal Python adapter helpers in `sentiment_helpers.py` without replacing the current UI.

QA:
- Focused tests for the payload.
- `py_compile` for Sentiment modules.
- `git diff --check`.

Commit:
- Korean commit message for phase 1 only.

### 2차: React Component Scaffold

Purpose: Create the custom component shell and fallback path.

Scope:
- Add `sentiment_react_component.py`.
- Add Vite/React component scaffold under `app/web/streamlit_components/sentiment_workbench/`.
- Wire the Sentiment tab to render React when built, otherwise keep existing Streamlit display.

QA:
- `npm install` only if package lock is absent or stale.
- `npm run build`.
- Focused Python tests and `py_compile`.
- Browser QA if the component can render.

Commit:
- Korean commit message for phase 2 only.

### 3차: Summary / Freshness UI

Purpose: Make the first screen answer current state and data freshness.

Scope:
- React command strip for refresh vs reload distinction.
- Core summary hero: phase/headline/summary.
- Metric cards for CNN Fear & Greed, AAII bearish, bull-bear spread, data confidence.
- Freshness chips from existing rows/coverage only.

QA:
- Payload contract tests.
- React build.
- Browser QA screenshot.

Commit:
- Korean commit message for phase 3 only.

### 4차: Drivers / AAII / Next Checks UI

Purpose: Show what created the sentiment state and how CNN/AAII agree or diverge.

Scope:
- Driver groups as greed/fear/neutral lanes.
- CNN component visual chart based on `component_rows` and `driver_groups`.
- AAII comparison panel based on existing `analysis_steps` / `coverage`.
- Next checks as context-only follow-up cards.

QA:
- Payload/component contract tests.
- React build.
- Browser QA screenshot.

Commit:
- Korean commit message for phase 4 only.

### 5차: Evidence / Graphs / Docs Closeout

Purpose: Move raw evidence below the reading flow and close durable documentation.

Scope:
- Improve history graph placement and component chart as lower evidence.
- Keep raw tables available but not dominant.
- Update durable docs/runbook/root logs.
- Final QA and screenshot.

QA:
- Focused tests.
- `py_compile`.
- React build.
- `git diff --check`.
- Browser QA screenshot.
- `git status --short` stage review excluding generated artifacts.

Commit:
- Korean commit message for phase 5 only.

## Phase 1 Detailed Steps

- [ ] Write a failing test that imports `build_sentiment_react_workbench_payload` and asserts schema, action boundary, core metrics, driver lanes, next checks, and chart series are derived from a sample snapshot.
- [ ] Run the focused test and confirm it fails because the adapter does not exist.
- [ ] Implement the minimal adapter in `app/web/overview/sentiment_helpers.py`.
- [ ] Run the focused test and confirm it passes.
- [ ] Run phase 1 QA commands.
- [ ] Update task `STATUS.md` and `RUNS.md`.
- [ ] Stage only phase 1 source/docs files.
- [ ] Commit phase 1.
