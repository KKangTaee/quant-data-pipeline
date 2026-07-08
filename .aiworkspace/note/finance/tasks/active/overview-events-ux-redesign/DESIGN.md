# Design

## 2026-07-07 Events React Workbench Continuation

### 이걸 하는 이유?

`Workspace > Overview > Events`는 FOMC, macro release, earnings estimate 일정을 이미 DB에서 읽지만, 현재 화면은 `Next Event`, row count, source lane, Macro Week Lane, `Agenda / Calendar / Quality / Raw`가 기능 단위로 분리되어 있다. 사용자는 "오늘 / 이번 주 / 30일 안에 무엇을 봐야 하는가", "공식 일정과 provider estimate가 어떻게 다른가", "stale 또는 not confirmed 일정은 무엇인가"를 첫 화면에서 바로 읽기 어렵다.

이번 React 전환은 Events를 validation gate, 매수/매도 신호, monitoring signal, 자동 action으로 바꾸지 않는다. Events는 시장 배경과 조사 단서이며, 일정 밀도와 자료 상태 근거를 확인하는 context surface다.

### Current Flow

현재 Events 탭 흐름은 다음 순서다.

```text
render_events_header
-> render_event_refresh_toolbar
-> load_event_snapshot_context
-> render_event_refresh_results
-> render_events_overview_lanes
-> empty state
-> filter_event_calendar_rows
-> render_event_detail_tabs
```

실제 Streamlit UI 대부분은 `app/web/overview/events_helpers.py`가 소유한다. `app/web/overview/events.py`는 tab entrypoint만 담당하고, `app/web/overview/components/events.py`는 macro week lane, summary strip, source lane, warning strip, agenda sections HTML renderer를 가진다.

### Current Read Model Contract

`app/services/overview/events.py`는 현재 다음 계약을 제공한다.

- `build_market_events_snapshot()`
  - DB table: `finance_meta.market_event_calendar`
  - output: `rows` DataFrame, `coverage`, `warnings`, `date_window`, `status`
  - derived fields: `Days Until`, `Window`, `Importance`, `Focus`, `Source Type`, `Validation`, `Freshness`, `Quality Action`, `Event Status`, `Age Days`
  - coverage fields: event count, official / estimate count, estimate-only / cross-checked / not-confirmed / stale estimate count, this-week / next-30D / recent / upcoming counts
- `build_overview_macro_week_lane()`
  - recent major + upcoming near-term lane
  - clusters: FOMC, CPI, PPI, Employment, GDP, Earnings
  - status can become `REVIEW` from stale / estimate-only / not-confirmed rows
  - boundary note already states context-only behavior

The current service does not yet provide a React-ready workbench payload with hero brief, grouped lanes, trust review, calendar density, or lower evidence tabs.

### Current UI Weaknesses

- The first screen reads like operational status: next row, stored rows, review count, source mini cards.
- Refresh collection and UI reload are not separated as two user concepts.
- Macro Week Lane, Agenda, Calendar, Quality, and Raw are useful, but the reading order is split across multiple peer sections.
- Calendar grid shows events, but hover/detail data for stale/review counts and event density is not available.
- `Quality` is technically correct but product copy should read as "자료 신뢰 / 추정 일정 확인".
- Earnings provider estimates need a stronger distinction from official FOMC / macro schedules.
- Raw evidence should stay available but should not compete with the brief / lane / trust sections.

### Proposed Ownership Boundary

Python remains the owner of interpretation and side effects.

- `app/services/overview/events.py`
  - add a service-owned `events_workbench` payload builder.
  - owns all new user-facing interpretation copy and derived structures.
  - keeps rows / coverage / warnings compatible with existing callers.
- `app/web/overview/events_helpers.py`
  - adds only payload adapter glue, React event handling, fallback dispatch, and current refresh action calls.
  - does not invent new interpretation copy beyond existing button/action labels.
- `app/web/overview/events_react_component.py`
  - wraps the Streamlit custom component and build availability check.
- `app/web/streamlit_components/events_workbench/`
  - owns React rendering, filters/toggles, tabs, hover tooltips, calendar / density interaction.
  - sends action ids to Python; does not read DB, fetch providers, or create signals.
- Existing Streamlit sections remain fallback when `component_static/index.html` is missing.

### Proposed React Payload Shape

Schema candidate: `events_react_workbench_v1`.

```text
payload
  schema_version
  component
  boundary_note
  action_boundary = python_dispatch_only
  command
    title
    detail
    actions: refresh_fomc, refresh_earnings, refresh_macro, reload
  brief
    title = 다가오는 시장 이벤트 브리프
    next_event
    counts: today, this_week, next_30d
    official_vs_estimate
    freshness_summary
    stale_estimate_summary
    boundary_copy
  event_groups
    recent_major
    today
    this_week
    next_30d
    later
  trust_review
    estimate_stale
    estimate_only
    not_confirmed
    conflict
    official_rows
    refresh_reasons
  calendar
    month_days
    event_type_counts
    stale_count
    review_count
    primary_titles
  density
    weekly_buckets
    stacked_counts_by_type
    review_count
    stale_count
  evidence
    agenda_rows
    calendar_rows
    trust_rows
    raw_rows
    raw_columns
```

React may filter and toggle already-provided structures, but it should not create new explanatory conclusions from raw values.

### Phased Roadmap

2026-07-07 추가 리서치 후, Events 작업은 단순 React 전환이 아니라 market event calendar 제품화 흐름으로 확장한다. 아래 확장 로드맵이 현재 기준이다.

#### 1차: 현재 구조 분석 / React 전환 범위

- 완료: current flow, read-model contract, UI weakness, React ownership boundary를 정리했다.
- Not included: code implementation, UI QA, commit.

#### 2차: 이벤트 taxonomy / schema / read-model contract

- Purpose: 후속 P0 수집 확장을 받기 위해 `market_event_calendar`와 `build_market_events_snapshot()`의 표준 분류 언어를 먼저 고정한다.
- Fields: `event_family`, `event_subtype`, `event_time_label`, `event_datetime_utc`, `universe_scope`, `source_authority`.
- Read model: `market_events_snapshot_v2`, `Event Family`, `Event Subtype`, `Universe Scope`, `Source Authority`, `Event Time`, `Event Datetime UTC`, and coverage count maps.
- Completion: focused RED/GREEN contract tests, schema/upsert/read-model compatibility, data docs alignment.
- Not included: new external collectors, React scaffold, Browser QA.

#### 3차: 공식 macro / fixed-income calendar 수집 확장

- Purpose: CPI / PPI / Employment / GDP only 상태를 넘어 PCE, retail, durable goods, housing, ISM PMI, Treasury auctions/refunding 같은 P0 official calendar를 확장한다.
- Files: `finance/data/market_intelligence.py`, `app/jobs/ingestion_jobs.py`, `app/jobs/overview_actions.py`, service tests.
- Completion: official rows carry taxonomy fields and source URLs; ingestion job result reports partial source failures without UI direct fetch.

#### 4차: 실적 universe 확장

- Purpose: latest movers 중심 earnings를 S&P 500 / Nasdaq-100 / portfolio / watchlist / major-cap coverage로 확장한다.
- Key rule: future earnings dates remain `provider_estimate` unless issuer/official source confirms them.
- Completion: universe-scoped earnings collection, stale/not-confirmed/cross-checked source states, bounded batching.

#### 5차: 시장 구조 이벤트 추가

- Purpose: NYSE/Nasdaq holidays, early closes, options expiration/OPEX, and index rebalance calendar rows를 추가한다.
- Completion: market-structure rows use `event_family=market_structure`, `universe_scope=all_us`, and official/source evidence URLs.

#### 6차: workbench payload builder

- Purpose: React가 렌더링만 할 수 있도록 service-owned `events_workbench_v1` payload를 만든다.
- Scope: hero brief, event groups, trust review, calendar day buckets, density buckets, lower evidence.

#### 7차: React scaffold / fallback

- Purpose: `events_react_component.py` and `events_workbench/*` scaffold를 추가한다.
- Completion: React build가 없으면 기존 Streamlit UI fallback.

#### 8차: 핵심 brief / freshness / refresh UX

- Purpose: 첫 화면을 "다가오는 시장 이벤트 브리프"로 바꾸고 화면 reload vs data refresh를 분리한다.
- Completion: next event, today/week/30D counts, official vs estimate, latest collection, stale estimate boundary.

#### 9차: 이벤트 레일 / 자료 신뢰 / calendar 개선

- Purpose: Recent / Today / This Week / Next 30D / Later reading flow, trust review, calendar hover/density chart를 구현한다.
- Completion: FOMC/Macro/Earnings/Market Structure filters and stale/review tooltip QA.

#### 10차: 최종 QA / docs / commit

- Purpose: 전체 구현 단위를 검증하고 coherent commit으로 닫는다.
- QA: service contract tests, `py_compile`, React build, Browser QA, `git diff --check`.
- Commit policy: generated screenshots, run history, `.DS_Store`, local artifacts, unrelated dirty files 제외.

### Original React Roadmap

#### 1차: Analysis / Scope

- Purpose: current code, read model, UI weakness, React payload range confirmation.
- Files read: `app/web/overview/events.py`, `events_helpers.py`, `components/events.py`, `app/services/overview/events.py`, `overview_dashboard_helpers.py`, `finance/data/market_intelligence.py`, related jobs/schema/tests, and existing React workbench patterns.
- Completion: this design note and task status are updated.
- Not included: code implementation, React scaffold, UI QA, commit.

#### 2차: React Scaffold / Wrapper

- Purpose: add component shell without changing user-facing behavior when unavailable.
- Expected files:
  - create `app/web/overview/events_react_component.py`
  - create `app/web/streamlit_components/events_workbench/*`
  - modify `app/web/overview/events_helpers.py`
- Completion: build availability check works; fallback Streamlit Events UI remains intact.
- QA: `py_compile` wrapper/helper; `npm install` if needed; `npm run build` for events component.

#### 3차: Brief / Freshness / Refresh UX

- Purpose: make the first view answer what to look at next and why refresh may be needed.
- Expected service change: hero brief, freshness summary, source summary, warnings / refresh reasons.
- UI: "다가오는 시장 이벤트 브리프", next event, today / week / 30D counts, official vs estimate, latest collection, stale estimate state, context-only boundary.
- Refresh result stays a secondary expander / companion, not the main surface.
- QA: service contract tests and Browser QA screenshot of Events first screen.

#### 4차: Event Rails / Trust Review

- Purpose: make Recent Major / Today / This Week / Next 30D / Later a single reading flow.
- Expected service change: event groups and trust review rows.
- UI: type badges for FOMC / Macro / Earnings and source-state badges for official / provider estimate / cross-checked / stale / not confirmed.
- Rename user-facing Quality concept to "자료 신뢰 / 추정 일정 확인".
- QA: FOMC, Macro, Earnings filter paths and stale / estimate-only fixture checks.

#### 5차: Calendar / Density / Raw Evidence

- Purpose: show when events are clustered and which dates need source review.
- Expected service change: calendar day buckets and weekly density buckets.
- UI: React month calendar or timeline, hover tooltip with date, event type counts, major titles, stale/review counts, plus stacked weekly density chart.
- Raw / source URL / confidence / collected_at / raw fields remain accessible in lower evidence.
- QA: desktop and mobile Browser QA, tooltip or DOM state check, screenshot verification.

#### 6차: Docs / Final QA / Commit

- Purpose: close the implementation unit coherently.
- Docs: update Overview Market Intelligence runbook and relevant docs for Events React workbench ownership and QA.
- QA: `git diff --check`, Python compile, focused service tests, React build, Browser QA.
- Commit: coherent Korean commit message, excluding generated screenshots, run history, `.DS_Store`, local artifacts, and unrelated dirty files.

### Open Risks

- `events_helpers.py` is already large. The React adapter should be kept small, but deeper decomposition may be needed if event handling and payload adaptation grow.
- Existing tests assert current helper function names and macro week lane order. The React path should preserve those contracts or update tests deliberately.
- `sentiment_workbench` currently has no committed `node_modules`; Events may need `npm install` before build unless dependency reuse is standardized.
- Browser QA screenshots are generated artifacts and must stay uncommitted unless explicitly requested.
