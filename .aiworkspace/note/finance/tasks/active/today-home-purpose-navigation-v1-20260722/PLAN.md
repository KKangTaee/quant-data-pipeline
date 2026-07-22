# Today Home + Purpose Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 상세 화면을 보존하면서 DB-backed `Today` 기본 진입 화면과 `Research / Portfolio / Data / Help` 목적형 상위 navigation을 구현한다.

**Architecture:** `app/services/today.py`가 기존 Overview·Portfolio Monitoring 결과를 compact read-only payload로 투영한다. `app/web/today_page.py`는 기존 Overview visual token을 재사용해 B안의 `시장 브리프 → 대표 포트폴리오 → 다음 확인` 순서를 렌더링하고, `app/web/streamlit_app.py`는 기존 URL path를 유지한 채 Today를 기본 page로 등록한다.

**Tech Stack:** Python 3.11, Streamlit multipage navigation, existing MySQL-backed Overview/Portfolio Monitoring loaders, unittest/pytest, HTML/CSS/SVG presentation.

## Global Constraints

- 기존 `/overview`, `/institutional-portfolios`, `/ingestion`, `/backtest`, `/selected-portfolio-dashboard`, `/reference` URL path와 내부 화면을 유지한다.
- 신규 기본 page 등록 key는 `today`이며 Streamlit `default=True` 규칙에 따라 실제 canonical browser path는 `/`다.
- Today 진입만으로 provider/FRED/SEC fetch, ingestion job, registry write, monitoring log write를 실행하지 않는다.
- 시장 context는 매매 신호·공식 적정가·확정 예측·validation gate로 표현하지 않는다.
- 대표 포트폴리오는 기존 default group과 동일한 DB-backed read model을 사용한다.
- generated QA artifact와 registry/saved/run-history 변경은 커밋하지 않는다.

---

### Task 1: Pure Today read model

**Files:**
- Create: `app/services/today.py`
- Create: `tests/test_today_home.py`

**Interfaces:**
- Consumes: `economic_cycle`, `sp500`, `futures_macro`, `sentiment`, `events`, `portfolio` mapping과 `generated_at`.
- Produces: `build_today_read_model(...) -> dict[str, object]` with `header`, `market`, `portfolio`, `actions`, `boundaries`.

- [x] **Step 1: Write failing projection tests**

```python
model = build_today_read_model(
    economic_cycle=cycle_fixture,
    sp500=sp500_fixture,
    futures_macro=futures_fixture,
    sentiment=sentiment_fixture,
    events=event_fixture,
    portfolio=portfolio_fixture,
    generated_at=datetime(2026, 7, 22, 9, 0),
)
self.assertEqual(model["schema_version"], "today_home_v1")
self.assertEqual(model["portfolio"]["name"], "Core")
self.assertAlmostEqual(model["portfolio"]["metrics"]["day_return"], 0.02)
self.assertFalse(model["boundaries"]["provider_fetch"])
```

- [x] **Step 2: Run RED test**

Run: `.venv/bin/python -m pytest tests/test_today_home.py -q`

Expected: FAIL because `app.services.today` does not exist.

- [x] **Step 3: Implement minimal pure projection**

Implement these concrete helpers and the public builder:

```python
def build_today_read_model(*, economic_cycle, sp500, futures_macro,
                           sentiment, events, portfolio, generated_at=None) -> dict[str, object]: ...
def _project_market_evidence(...) -> list[dict[str, object]]: ...
def _project_portfolio(workspace: object) -> dict[str, object]: ...
def _daily_return(curve: object) -> float | None: ...
```

The builder returns `READY`, `PARTIAL`, or `UNAVAILABLE` without converting missing evidence into a positive conclusion. Portfolio output returns `EMPTY` rather than fabricated zero returns when no active item exists.

- [x] **Step 4: Run GREEN test**

Run: `.venv/bin/python -m pytest tests/test_today_home.py -q`

Expected: PASS.

### Task 2: Today B presentation and existing-loader adapter

**Files:**
- Create: `app/web/today_page.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: existing cached Overview loaders and `load_portfolio_monitoring_workspace_for_operations()`.
- Produces: `configure_today_page_targets(mapping)` and `render_today_page()`.

- [x] **Step 1: Write failing renderer/source-boundary tests**

```python
source = Path("app/web/today_page.py").read_text(encoding="utf-8")
self.assertIn("overview_ui_css", source)
self.assertIn("load_portfolio_monitoring_workspace_for_operations", source)
self.assertNotIn("run_overview_", source)
self.assertNotIn("requests.", source)
```

- [x] **Step 2: Run RED test**

Run: `.venv/bin/python -m pytest tests/test_today_home.py -q`

Expected: FAIL because the Today renderer is missing.

- [x] **Step 3: Implement the B presentation**

Render one responsive shell in this order:

```text
오늘의 시장 판단 header + 기준일/freshness
시장 결론 hero
경제·S&P 500·선물 매크로·심리 evidence + 다음 일정
대표 포트폴리오 metrics/curve/기여·주의 항목
시장 근거 / 영향 종목 / 포트폴리오 점검 page links
```

Use Overview blue-gray tokens, 2-column desktop layout, 1-column `max-width: 760px` layout, escaped copy, and the same compact fallback for partial/missing sources.

- [x] **Step 4: Run GREEN test and compile**

Run: `.venv/bin/python -m pytest tests/test_today_home.py -q && .venv/bin/python -m py_compile app/services/today.py app/web/today_page.py`

Expected: PASS and exit 0.

### Task 3: Default route and purpose navigation

**Files:**
- Modify: `app/web/streamlit_app.py`
- Modify: `tests/test_today_home.py`
- Modify: `tests/test_institutional_portfolios.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `render_today_page`, existing `st.Page` objects.
- Produces: top navigation groups `Research`, `Portfolio`, `Data`, `Help` and default `/today`.

- [x] **Step 1: Write failing route contract**

```python
self.assertIn('title="Today"', source)
self.assertIn('url_path="today"', source)
self.assertIn('default=True', today_page_statement)
self.assertIn('"Research": [', source)
self.assertIn('"Portfolio": [', source)
self.assertIn('"Data": [', source)
self.assertIn('"Help": [', source)
```

Also assert every legacy `url_path` remains present.

- [x] **Step 2: Run RED route tests**

Run: `.venv/bin/python -m pytest tests/test_today_home.py tests/test_institutional_portfolios.py -q`

Expected: FAIL on the old `Workspace / Operations / Reference` navigation contract.

- [x] **Step 3: Register Today and regroup existing pages**

Use these page titles without changing their URL paths:

```text
Research: Today, Market Research, Institutional Holdings
Portfolio: Portfolio Lab, Portfolio Monitoring
Data: Data Operations
Help: Reference Center
```

Configure Today page targets after constructing all `st.Page` objects so page links use the existing Page instances.

- [x] **Step 4: Run GREEN route tests**

Run: `.venv/bin/python -m pytest tests/test_today_home.py tests/test_institutional_portfolios.py tests/test_reference_center.py tests/test_reference_contextual_help.py -q`

Expected: PASS.

### Task 4: Actual-data browser QA and durable documentation

**Files:**
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `RUNS.md`, `RISKS.md`

- [x] **Step 1: Run focused and regression verification**

Run: `.venv/bin/python -m pytest tests/test_today_home.py tests/test_institutional_portfolios.py tests/test_reference_center.py tests/test_reference_contextual_help.py tests/test_portfolio_monitoring_page.py -q`

Run: `.venv/bin/python -m py_compile app/services/today.py app/web/today_page.py app/web/streamlit_app.py`

Run: `git diff --check`

Expected: all tests pass, compile exits 0, no whitespace errors.

- [x] **Step 2: Run Browser QA**

Verify actual DB-backed `/today` at desktop, 760px, and 420px; confirm default landing, zero horizontal overflow, no console errors, and continuity of all seven top-level destinations. Capture one screenshot without staging it.

- [x] **Step 3: Sync durable docs and task closeout**

Record the new canonical navigation, Today data flow, verification evidence, remaining limitations, and `4/4차` completion without copying command transcripts into root logs.

- [x] **Step 4: Commit coherent implementation**

Stage only Today implementation/tests/docs and commit with a Korean message. Do not stage `.superpowers`, registry, saved, run-history, or generated QA files.

## Self-Review

- Spec coverage: default landing, B layout, 대표 포트폴리오, partial/empty states, legacy URLs, owner links, no provider fetch are each owned by Tasks 1–3.
- Placeholder scan: no TBD/TODO/implement-later markers are present.
- Type consistency: `build_today_read_model` is the only service entry; web adapter and tests use the same payload keys.
