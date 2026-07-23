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

## 2026-07-23 Market Calendar Coverage Correction

### Approved Outcome

사용자는 earnings 수집을 `주요 대형주·보유/관심종목 daily + S&P 500 periodic full sweep` 혼합 방식으로 바꾸고, React 화면은 `A · 브리프 + 캘린더` 구조로 개편하는 안을 승인했다.

이번 개편은 Events를 운영 job dashboard로 만들지 않는다. 첫 화면의 제품 가치는 사용자가 오늘과 이번 주의 중요 일정을 한국시간으로 파악하고, 공식 일정과 변경 가능한 실적 추정을 구분하는 것이다. Coverage와 실패 상태는 누락 가능성을 설명하는 보조 근거로만 사용한다.

### Verified Current Problems

- Overview의 수동·자동 earnings 경로는 `symbol_source="latest_movers"`, `top_movers_limit=20`을 사용한다.
- `latest_movers`는 최신 S&P 500 intraday snapshot을 `return_pct DESC`로 정렬한 상승 종목 목록이다.
- 2026-07-21 최신 snapshot에서 GOOG / GOOGL은 음의 수익률이어서 top 20에서 제외됐고, `market_event_calendar`에도 Alphabet 행이 없었다.
- 같은 날짜 범위로 GOOG / GOOGL을 직접 provider에 조회하면 2026-07-23 earnings event가 반환됐다. Provider parser가 아니라 symbol selection contract가 직접 원인이다.
- 저장된 FOMC 일정 자체는 공식 Fed 일정과 일치하지만, UI의 전역 `LIMIT 200` 때문에 earnings 행이 많을 때 먼 미래 FOMC가 화면 payload에서 밀려난다.
- 2026년 미국 휴장 / 조기폐장 행은 공식 일정과 일치하지만, 공개된 2027년 공식 일정은 DB에 없다.
- React local filter는 rail과 calendar 일부만 바꾸고 hero / trust / density의 합계를 일관되게 다시 계산하지 않는다.
- 다음 일정은 중요도 판단 없이 정렬된 첫 행을 사용하고, 모든 earnings가 `Medium`으로 표시된다.
- earnings는 미국 거래일만 있고 장전 / 장후, 실제 UTC datetime, 한국시간 표시일이 없어 자정처럼 오해될 수 있다.

### Collection Alternatives

1. S&P 500 전체 daily
   - 장점: 단순하고 매일 완전성을 목표로 할 수 있다.
   - 단점: 현재 provider adapter가 종목별 순차 조회이므로 매일 약 500회 호출과 큰 실패 범위를 만든다.
2. Movers + fixed core list
   - 장점: 호출량이 작다.
   - 단점: fixed list의 자의성이 남고 중요한 기업 누락 문제를 근본적으로 해소하지 못한다.
3. Priority daily + sharded S&P 500 sweep
   - 장점: 사용자에게 중요한 종목을 매일 확인하면서 전체 universe 완전성을 주기적으로 복구한다.
   - 단점: cold start 직후에는 full coverage가 아니므로 coverage checkpoint가 필요하다.

승인된 안은 3번이다.

### Earnings Coverage Contract

#### Daily Priority Set

`build_priority_earnings_symbols()`는 아래 source를 합집합으로 만들고 symbol 기준으로 중복 제거한다.

1. 최신 `nyse_asset_profile.market_cap` 기준 미국 주식 상위 100종목
2. 명시적으로 연결된 보유 포트폴리오 종목
3. 명시적으로 연결된 관심종목
4. `market_event_calendar`에 active 상태로 저장된 45일 이내 earnings 종목

포트폴리오나 관심종목 source가 비어 있으면 해당 source만 건너뛰며 전체 수집 실패로 취급하지 않는다. 관련 없는 saved registry를 추측해서 포트폴리오로 사용하지 않는다.

#### S&P 500 Full Sweep

- `finance_meta.market_universe_member`의 최신 active S&P 500 구성종목을 사용한다.
- 약 100종목씩 5개 shard로 순환한다.
- 각 자동 실행은 daily priority set과 아직 완료되지 않은 다음 shard를 처리한다.
- 구성종목 수가 500과 다르면 실제 expected count에 맞춰 shard 수와 마지막 shard 크기를 계산한다.
- cycle cursor와 실패 목록을 DB checkpoint에 저장한다.
- provider 실패가 없는 정상 cycle은 5회 이내 완료한다. 실패가 있으면 base shard cursor는 한 바퀴를 마쳐도 coverage를 `partial`로 유지하고 retry queue가 비워진 뒤에만 `complete`로 전환한다.
- 실패 종목은 다음 실행의 priority retry queue에 포함한다.
- 구성종목 snapshot이 바뀌면 새 cycle을 시작하되, 이미 저장된 미래 일정은 즉시 삭제하지 않는다.

`latest_movers`는 earnings 기본 보장 범위에서 제거한다. 필요하면 별도 조사 source로 남길 수 있지만 Overview 기본 수집의 성공 기준에는 포함하지 않는다.

#### Coverage Checkpoint

새 `finance_meta.market_event_collection_coverage` 테이블은 event row와 분리된 수집 완전성 상태를 보존한다.

```text
coverage_key
event_family
universe_scope
window_start / window_end
expected_items / covered_items / failed_items
cursor_offset / batch_size
coverage_status = pending | partial | complete | stale | error
cycle_started_at / cycle_completed_at
last_attempted_at / last_success_at
details_json
created_at / updated_at
```

필수 coverage key는 `earnings:priority_daily`, `earnings:sp500_cycle`, `fomc:<year>`, `market_holiday:<year>`다. 이 테이블은 raw job 결과를 첫 화면에 보여주기 위한 것이 아니라, 수집하지 않은 종목을 "일정 없음"으로 오인하지 않기 위한 read-model 근거다.

`covered_items`는 provider가 정상 응답해 `event_found` 또는 `checked_no_event`로 판정된 항목 수다. `failed_items`는 covered에 포함하지 않는다. `complete`는 `covered_items == expected_items`이고 retry queue가 비었을 때만 사용할 수 있다.

### Issuer Identity And Display Deduplication

- raw earnings event는 ticker별 evidence를 보존한다.
- event row에 nullable `issuer_key`와 `issuer_name`을 추가한다.
- 우선 issuer key는 `nyse_symbol_lifecycle`의 SEC `related_cik`를 사용해 `sec_cik:<CIK>`로 만든다.
- SEC identity가 없으면 `symbol:<SYMBOL>`로 fallback하고 임의의 회사명 유사도 결합은 하지 않는다.
- service는 `(issuer_key, event_date, event_subtype)`로 display group을 만든다.
- display group은 대표 회사명, `symbols`, 가장 강한 source authority, 가장 최근 collected-at을 가진다.
- 따라서 GOOG / GOOGL raw row는 남지만 React는 `Alphabet · GOOG/GOOGL` 한 일정만 렌더한다.

### Date And Time Contract

Earnings는 아래 값을 구분한다.

- `event_date`: 미국 거래 세션 기준 발표일
- `event_datetime_utc`: provider가 실제 시각을 제공할 때만 저장
- `event_time_label`: `before_market`, `after_market`, `time_confirmed`, `time_unknown`
- `display_date_kst` / `display_time_kst`: service에서 exact UTC datetime 또는 장전 / 장후 session label을 근거로 계산할 수 있을 때만 채운다.

Exact datetime이 있으면 Asia/Seoul로 정확히 변환한다. Exact datetime 없이 `before_market` / `after_market`만 있으면 미국 세션 기준의 한국 날짜를 `예정`으로 표시한다. 시간 label도 없으면 `display_date_kst`와 `display_time_kst`를 비우고, calendar는 미국 `event_date`에 잠정 배치하면서 `미국 기준 · 한국시간 미확인`을 명시한다. 어떤 경우에도 임의의 자정을 만들지 않는다.

### FOMC And US Market Holiday Contract

- FOMC는 Federal Reserve 공식 calendar 기준으로 현재 연도와 공개된 차기 연도를 수집한다.
- 휴장 / 조기폐장은 NYSE / Nasdaq 공식 calendar 기준으로 공개된 향후 연도를 수집한다.
- 공식 source parse가 일부 실패하면 성공한 다른 연도 / source는 저장하되 기존 정상 공식 행을 삭제하지 않는다.
- coverage checkpoint의 expected / covered count로 연도별 완전성을 검사한다.
- 서비스 조회는 먼저 날짜 범위와 event family를 적용한다. 전역 `LIMIT 200`으로 모든 family를 한꺼번에 자르지 않는다.
- earnings 행 수가 늘어도 FOMC와 휴장 / 조기폐장이 payload에서 사라지지 않아야 한다.

### Data Flow And Ownership

```text
Overview automation / manual refresh
-> earnings coverage orchestrator
   -> priority symbol composer
   -> S&P 500 shard checkpoint
   -> provider adapters
   -> issuer identity enrichment
   -> market_event_calendar upsert
   -> coverage checkpoint update
-> date-window / family-aware DB loader
-> app.services.overview.events interpretation
-> Events React workbench rendering
```

- `finance/data/market_intelligence.py`: symbol composition, shard orchestration, issuer enrichment, event / coverage persistence
- `finance/data/db/schema.py`: event identity columns and coverage table
- `app/jobs/overview_actions.py`: manual facade
- `app/jobs/overview_automation.py`: daily priority + next-shard cadence
- `app/services/overview/events.py`: importance ranking, KST presentation, issuer grouping, consistent filtered payload
- `app/web/overview_dashboard_helpers.py`: date-window / family-aware loader boundary
- `app/web/overview/events_helpers.py`: React payload adapter and Python action dispatch only
- `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx`: display and local selection state only

UI와 service는 provider를 직접 호출하지 않는다. React는 raw row에서 중요도를 새로 계산하지 않고 service-owned payload를 렌더한다.

### A · Brief + Calendar UX

#### First Screen

상단은 아래 세 질문에 답한다.

1. 오늘 / 이번 주에 중요한 일정은 무엇인가?
2. 한국시간으로 언제인가?
3. 공식 일정인가, 변경 가능한 추정 일정인가?

Hero는 `가장 중요한 다음 일정`, `이번 주 핵심 일정`, `다음 FOMC`만 보여준다. 다음 일정은 DB 첫 행이 아니라 아래 우선순위의 명시적 sort key로 고른다.

1. 날짜 근접도: 오늘, 이번 calendar week, 30일 이내, 이후
2. 사용자 관련성: FOMC, 보유 / 관심종목 earnings, 주요 대형주 earnings, 공식 휴장·조기폐장, 그 외 일정
3. source authority와 실제 / 예정 시각
4. title

이 순서 때문에 오늘의 Alphabet 실적이 몇 주 뒤 FOMC나 휴장일에 가려지지 않는다. 과거 stale row와 superseded row는 next event가 될 수 없다.

기존 다중 command band는 제거하고 `일정 갱신`을 보조 action으로 내린다. Refresh 결과의 run / row / status 값은 collapsed evidence에만 둔다.

#### Main Calendar

- 왼쪽: 월간 7열 calendar
- 오른쪽: 선택 날짜의 중요 일정 전체
- 하단: 현재 필터와 동일한 weekly density
- 필터: `전체`, `FOMC`, `실적`, `휴장·조기폐장`

필터는 hero counts, calendar day counts, selected-date details, density totals / segments, trust summary에 동일하게 적용한다. 하나의 filtered display model을 만든 뒤 모든 UI section이 이를 공유한다.

#### Event Card

Event card는 다음 순서로 읽힌다.

```text
Alphabet 실적
GOOG · GOOGL
7월 23일 KST · 장후 또는 시간 미확인
주요 대형주 일일 확인 · 제공자 추정
```

`Medium` 같은 일괄 중요도는 제거한다. 대신 `핵심`, `보유·관심`, `일반`과 선정 근거를 표시한다. 상세 근거에는 미국 거래일, source authority, 마지막 확인 시각, source URL을 둔다.

#### Trust And Evidence

- 자료 신뢰 / coverage는 첫 화면의 주인공이 아니라 접힌 보조 section이다.
- 영어 warning을 한국어 행동 문구로 바꾼다.
- raw evidence와 source URL은 하단 상세 근거에서 유지한다.
- coverage incomplete와 실제 no-event를 구분한다.
- 사용자에게 행동이 필요한 경우에만 `확인 필요` 문구를 노출한다.

#### Responsive Behavior

- desktop은 calendar / selected-date detail의 2열 배치를 사용한다.
- 좁은 화면은 calendar 다음에 selected-date detail을 쌓는다.
- filter는 줄바꿈 가능하며 가로 스크롤을 만들지 않는다.
- 선택일 전체 event 목록은 page 전체가 아니라 detail 영역 안에서 읽을 수 있어야 한다.

### Error Handling

- provider 일부 실패: 성공 event만 upsert하고 기존 정상 event는 보존하며 coverage를 `partial`로 기록한다.
- 특정 symbol에 upcoming date가 없음: 해당 symbol을 `checked_no_event`로 coverage에 포함하되 기존 미래 event는 한 번의 missing 응답만으로 supersede하지 않는다.
- 동일 미래 event가 두 번 연속 사라지거나 새 공식 / 교차확인 일정으로 대체될 때만 기존 추정 event를 stale / superseded 처리한다.
- official parser mismatch: 이전 공식 행을 유지하고 해당 연도 coverage를 `error` 또는 `partial`로 기록한다.
- checkpoint persist 실패: cursor를 전진시키지 않아 shard 누락을 방지한다.
- cold start: UI는 "일정 없음" 대신 "S&P 500 전체 확인 진행 중"을 보조 근거에 표시한다.
- source가 비어 있는 portfolio / watchlist: priority set의 다른 source는 정상 실행한다.

### Testing And Completion

#### Collector / DB Contract

- GOOG / GOOGL이 daily priority set에 포함된다.
- provider 실패가 없는 S&P 500 cycle은 5회 이내 완료된다.
- 실패 종목이 있으면 base shard 순회 후에도 `partial`을 유지하고 retry 완료 뒤 `complete`가 된다.
- partial provider failure가 기존 event를 삭제하지 않는다.
- issuer key가 같은 GOOG / GOOGL raw row는 하나의 display group으로 묶인다.
- 45일 이내 기존 earnings symbol이 daily priority set으로 승격된다.
- coverage checkpoint가 expected / covered / failed / cursor를 보존한다.

#### Official Calendar Contract

- 2026 / 2027 FOMC expected count와 저장 count가 일치한다.
- 공개된 2027년 휴장 / 조기폐장 일정이 저장된다.
- earnings 행이 200개를 초과해도 date window 안의 FOMC / holiday는 누락되지 않는다.

#### Service / React Contract

- next event priority가 stale first-row ordering을 사용하지 않는다.
- exact event datetime과 장전 / 장후 label은 KST 표시 계약에 따라 변환되고, 완전한 unknown time은 KST 날짜나 자정으로 추정되지 않는다.
- 모든 filter 대상 section이 동일한 count / event set을 사용한다.
- 영어 warning과 일괄 `Medium` label이 남지 않는다.
- coverage incomplete와 no-event empty state가 구분된다.

#### Final Verification

- focused RED / GREEN contract tests
- relevant broad unit tests
- Python `py_compile`
- Events React `npm run build`
- desktop / mobile Browser QA
- Google 일정, FOMC, 미국 휴장, filter consistency DOM 확인
- QA screenshot 1장 이상 첨부, generated artifact는 commit 제외
- `git diff --check`

### Scope Boundaries

- FOMC / earnings / 미국 휴장·조기폐장 외의 신규 event family 확장은 이번 correction에서 하지 않는다.
- 매수 / 매도 신호, validation gate, broker action, 자동 리밸런싱을 추가하지 않는다.
- issuer 공식 IR 페이지를 전 종목 자동 수집하는 crawler는 이번 범위에 넣지 않는다.
- provider estimate를 공식 확정 일정으로 승격하지 않는다.
- portfolio / watchlist source가 정의되지 않은 경우 unrelated registry를 추측 연결하지 않는다.

### Implementation Roadmap

1. Data contract: coverage table, issuer identity, date / time fields와 focused tests
2. Collection: daily priority composer, S&P 500 shard checkpoint, official-year completeness
3. Service / React: family-aware loader, consistent filtered display model, A안 화면
4. Verification / docs: DB smoke, broad tests, React build, Browser QA, durable docs, coherent commit

## 2026-07-24 Refresh Completion / FOMC Follow-up

### Approved User Outcome

- 상단 `일정 갱신`은 약 10초 안에 끝나는 공식 일정만 갱신한다.
  - FOMC
  - 공식 매크로 일정
  - 미국 휴장·조기폐장과 시장 구조 일정
- 약 90초 이상 걸릴 수 있는 실적 예상 일정은 하단의 명시적 `실적 예상 일정 갱신`으로 분리한다.
- 기존 `run_overview_event_calendars_refresh_all()`은 자동화와 기존 호출자 호환성을 위해 전체 4-step bundle로 유지한다.
- 완료된 갱신은 React가 `finished_at` 기반 completion token으로 확인해 `갱신 중` 상태를 해제한다.
- FOMC parser가 taxonomy를 source row에 직접 부여하고, 동일 event key UPSERT 재실행으로 기존 NULL taxonomy 행을 보정한다.

### Root Cause Contract

- 공식 FOMC 2026-07-28~29 일정은 DB에 2026-07-29 행으로 저장돼 있었다.
- `_parse_fomc_calendar_events_from_html()`이 `event_family`, `event_subtype`, `universe_scope`, `source_authority`를 만들지 않아 2026/2027 FOMC 16행의 taxonomy가 NULL이었다.
- family-bounded Events loader는 `event_family='central_bank'`만 읽으므로 저장된 FOMC가 workbench와 `다음 FOMC`에서 누락됐다.
- React의 pending reset effect가 변하지 않는 `payload.schema_version`과 `payload.status`만 관찰해, 정상 완료 후에도 버튼이 `갱신 중`으로 남을 수 있었다.
- 마지막 실제 bundle은 102초에 완료됐으며 그중 earnings가 92.091초였다. 긴 동기 실행과 현재 8521 QA 서버 종료는 별개로 다룬다.

### Data / UI Flow

```text
상단 일정 갱신
-> refresh_official
-> FOMC -> Macro -> Market Structure
-> DB 저장
-> session result finished_at 변경
-> Streamlit rerun
-> React completion token 변경
-> pending button 해제

하단 실적 예상 일정 갱신
-> refresh_earnings
-> priority + S&P 500 shard
-> DB 저장
-> 동일 completion token 계약으로 pending 해제
```

### Error And Compatibility Rules

- 공식 일정 중 일부가 `partial_success`여도 성공 row는 보존하고 완료 결과를 화면에 전달한다.
- UI 기본 action을 분리해도 `refresh_all` Python facade와 기존 automation contract는 제거하지 않는다.
- FOMC taxonomy는 parser 단계에서 정규화 전 source row에 명시한다. reader가 NULL을 임의 추론하는 fallback은 추가하지 않는다.
- 화면 첫 영역에는 run/status dashboard를 추가하지 않는다. 기존 접힌 지원 근거만 유지한다.

### Follow-up Acceptance

- parser가 FOMC row에 `central_bank / fomc_meeting / all_us / federal_reserve`를 생성한다.
- FOMC collector 재실행 후 DB의 2026/2027 FOMC taxonomy NULL이 0건이다.
- `events_workbench_v2`의 `views.all.brief.next_fomc`가 2026-07-29 회의를 반환한다.
- 상단 `일정 갱신`은 earnings collector를 호출하지 않는다.
- `실적 예상 일정 갱신`은 기존 hybrid earnings job을 그대로 실행한다.
- completion token 변경 시 primary/secondary pending state가 모두 해제된다.
- focused tests, 관련 broad tests, React build, 실제 DB smoke, Browser QA가 통과한다.
