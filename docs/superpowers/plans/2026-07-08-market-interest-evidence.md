# Market Interest Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a conservative Market Movers selected-symbol `시장 관심 근거` investigation layer without creating recommendations, scores, buy/sell signals, article bodies, report bodies, filing bodies, or live institutional-intent claims.

**Architecture:** Add a Streamlit-free `app/services/overview/market_interest.py` read model that classifies source leads as official durable candidates, session-only/public leads, or external research destinations. Wire it into the existing selected-symbol Market Movers fragment in `app/web/overview/market_movers_helpers.py`, keeping all lookup actions user-triggered and session-scoped. Keep SEC 13F as an official durable design/deferred source in V1; do not add DB schema until CUSIP-symbol mapping and ingestion scope are approved.

**Tech Stack:** Python 3.11, pandas, Streamlit, existing Market Movers React component bridge, unittest service-contract tests, existing finance documentation workspace.

---

### Task 1: Task Docs And Design Guardrails

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/PLAN.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/NOTES.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/RISKS.md`

- [ ] **Step 1: Record the approved 0차~4차 scope**

Write task docs that state:

```text
0차: docs/research/code boundary read complete.
1차: add UI/UX design for Market Movers selected-symbol market-interest panel.
2차: implement safe MVP with selected symbol only, user-triggered, session-only/non-durable public leads.
3차: document SEC 13F official durable path and CUSIP-symbol mapping blocker; no DB schema in V1.
4차: add conservative summary labels only: 관심 근거 있음, 원문 확인 필요, 지연 자료, 데이터 없음, 미구축.
```

- [ ] **Step 2: Keep 13F scope explicit**

State in `RISKS.md`:

```text
13F is delayed quarterly data, can be submitted up to 45 days after quarter-end, does not reveal shorts, derivatives, hedges, complete fund intent, or real-time trading. CUSIP-symbol mapping is required before durable 13F lookup.
```

### Task 2: RED Tests For Market Interest Read Model

**Files:**
- Modify: `tests/test_service_contracts.py`
- Create later: `app/services/overview/market_interest.py`

- [ ] **Step 1: Write failing service contract tests**

Add tests after the existing Why It Moved tests:

```python
def test_market_interest_read_model_classifies_public_sources_without_recommendation(self) -> None:
    from app.services.overview.market_interest import build_market_interest_read_model

    model = build_market_interest_read_model(
        mover={"Symbol": "NET", "Name": "Cloudflare Inc", "Rank": 1},
        metadata=None,
    )

    self.assertEqual(model["schema_version"], "market_interest_evidence_v1")
    self.assertEqual(model["status"], "NOT_REQUESTED")
    self.assertEqual(model["symbol"], "NET")
    policies = {row["Source"]: row["Policy"] for row in model["original_links"].to_dict("records")}
    self.assertEqual(policies["SEC Form 13F Data Sets"], "official_durable_candidate")
    self.assertEqual(policies["Briefing.com Upgrades / Downgrades"], "external_research_link")
    self.assertIn("45일", " ".join(model["institutional_caveats"]))
    self.assertNotIn("매수", model["boundary_note"])
    self.assertNotIn("score", model["boundary_note"].lower())
```

```python
def test_market_interest_summary_uses_conservative_statuses_from_existing_metadata(self) -> None:
    from app.services.overview.market_interest import build_market_interest_read_model

    metadata = {
        "status": "OK",
        "news": pd.DataFrame([{"Title": "NET news", "Source": "Desk", "Published At": "2026-07-08", "URL": "https://example.com/news"}]),
        "korean_news": pd.DataFrame([], columns=["Title", "Source", "Published At", "Snippet", "URL"]),
        "sec_filings": pd.DataFrame([{"Form": "8-K", "Filing Date": "2026-07-07", "Title": "Current report", "URL": "https://www.sec.gov/Archives/example"}]),
    }
    model = build_market_interest_read_model(
        mover={"Symbol": "NET", "Name": "Cloudflare Inc"},
        metadata=metadata,
    )

    summary = {item["id"]: item for item in model["summary_items"]}
    self.assertEqual(summary["analyst_interest"]["state"], "원문 확인 필요")
    self.assertEqual(summary["news_sec"]["state"], "관심 근거 있음")
    self.assertEqual(summary["institutional_context"]["state"], "지연 자료")
    self.assertEqual(summary["original_links"]["state"], "원문 확인")
    self.assertEqual(summary["news_sec"]["detail"], "뉴스 1건 · SEC 1건")
    self.assertFalse(any("buy" in str(item).lower() for item in model["summary_items"]))
```

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_classifies_public_sources_without_recommendation tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_summary_uses_conservative_statuses_from_existing_metadata
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.overview.market_interest'`.

### Task 3: GREEN Market Interest Service

**Files:**
- Create: `app/services/overview/market_interest.py`
- Modify: `app/services/overview/__init__.py` only if local package exports require it; current code usually imports modules directly.

- [ ] **Step 1: Implement source policy and read model**

Create `app/services/overview/market_interest.py` with:

```python
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import pandas as pd

MARKET_INTEREST_LINK_COLUMNS = ["Source", "Lane", "Policy", "Evidence", "Caveat", "URL"]
MARKET_INTEREST_STATUS_LABELS = {"NOT_REQUESTED", "READY"}


def _clean_text(value: Any, *, upper: bool = False) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if not text:
        return None
    return text.upper() if upper else text


def _rows_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=MARKET_INTEREST_LINK_COLUMNS)


def _stockanalysis_forecast_url(symbol: str) -> str:
    return f"https://stockanalysis.com/stocks/{symbol.lower()}/forecast/"


def _google_search_url(query: str) -> str:
    return "https://www.google.com/search?q=" + quote_plus(query)


def build_market_interest_original_links(*, symbol: str, name: str | None = None) -> pd.DataFrame:
    normalized_symbol = _clean_text(symbol, upper=True) or ""
    normalized_name = _clean_text(name) or normalized_symbol
    if not normalized_symbol:
        return _rows_frame([])
    analyst_query = f"{normalized_symbol} {normalized_name} analyst upgrade downgrade price target"
    institution_query = f"{normalized_symbol} {normalized_name} 13F institutional holdings"
    return _rows_frame(
        [
            {
                "Source": "StockAnalysis Forecast",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Forecast / analyst page destination",
                "Caveat": "Commercial-data-backed public page; no durable storage in V1.",
                "URL": _stockanalysis_forecast_url(normalized_symbol),
            },
            {
                "Source": "Briefing.com Upgrades / Downgrades",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Daily analyst action calendar destination",
                "Caveat": "Public lead only; storage and scraping are not approved.",
                "URL": "https://www.briefing.com/calendars/updown?Filter=All",
            },
            {
                "Source": "MarketBeat Ratings",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Ratings / target-change destination",
                "Caveat": "Freemium aggregator; use as outbound reference first.",
                "URL": "https://www.marketbeat.com/ratings/",
            },
            {
                "Source": "Yahoo Finance Analysis",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Quote analysis page destination",
                "Caveat": "Dynamic public page; no article/report body collection.",
                "URL": f"https://finance.yahoo.com/quote/{quote_plus(normalized_symbol)}/analysis/",
            },
            {
                "Source": "SEC Company Search",
                "Lane": "뉴스/공시 촉매",
                "Policy": "official_session_lookup",
                "Evidence": "Official company filing search destination",
                "Caveat": "Metadata and source links only unless a separate SEC digest scope is approved.",
                "URL": "https://www.sec.gov/edgar/search/#/q=" + quote_plus(f"{normalized_symbol} 8-K 10-Q 10-K"),
            },
            {
                "Source": "SEC Form 13F Data Sets",
                "Lane": "기관 보유 배경",
                "Policy": "official_durable_candidate",
                "Evidence": "Official quarterly 13F flattened datasets",
                "Caveat": "Requires CUSIP-symbol mapping before selected-symbol durable lookup.",
                "URL": "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets",
            },
            {
                "Source": "SEC 13F FAQ",
                "Lane": "기관 보유 배경",
                "Policy": "official_reference",
                "Evidence": "Official 13F reporting caveats",
                "Caveat": "Use to explain delayed quarterly filing scope.",
                "URL": "https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f",
            },
            {
                "Source": "WhaleWisdom",
                "Lane": "기관 보유 배경",
                "Policy": "external_research_link",
                "Evidence": "13F aggregator destination",
                "Caveat": "Freemium aggregator; SEC remains the durable source candidate.",
                "URL": _google_search_url(f"site:whalewisdom.com {institution_query}"),
            },
            {
                "Source": "Google Analyst Search",
                "Lane": "원문 확인",
                "Policy": "external_research_link",
                "Evidence": "General web search for analyst actions",
                "Caveat": "Search launch point only; no automatic cause judgment.",
                "URL": _google_search_url(analyst_query),
            },
        ]
    )


def _count_rows(value: Any) -> int:
    if isinstance(value, pd.DataFrame):
        return int(len(value.index))
    if isinstance(value, list):
        return int(len(value))
    return 0


def build_market_interest_read_model(*, mover: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    row = dict(mover or {})
    normalized_symbol = _clean_text(row.get("Symbol") or row.get("symbol"), upper=True)
    name = _clean_text(row.get("Name") or row.get("name")) or normalized_symbol or ""
    links = build_market_interest_original_links(symbol=normalized_symbol or "", name=name)
    payload = dict(metadata or {})
    news_count = _count_rows(payload.get("news")) + _count_rows(payload.get("korean_news"))
    sec_count = _count_rows(payload.get("sec_filings"))
    news_sec_state = "관심 근거 있음" if news_count or sec_count else "원문 확인 필요"
    news_sec_detail = f"뉴스 {news_count}건 · SEC {sec_count}건"
    status = "READY" if payload and str(payload.get("status") or "").upper() != "NOT_REQUESTED" else "NOT_REQUESTED"
    summary_items = [
        {
            "id": "analyst_interest",
            "label": "애널리스트 관심",
            "state": "원문 확인 필요",
            "detail": "업그레이드/다운그레이드와 목표가 변경은 외부 원문 링크에서 확인합니다.",
            "tone": "neutral",
        },
        {
            "id": "news_sec",
            "label": "뉴스/공시 촉매",
            "state": news_sec_state,
            "detail": news_sec_detail,
            "tone": "success" if news_count or sec_count else "neutral",
        },
        {
            "id": "institutional_context",
            "label": "기관 보유 배경",
            "state": "지연 자료",
            "detail": "13F는 분기 지연 공시이며 V1은 원문/공식 출처 확인 경로만 제공합니다.",
            "tone": "warning",
        },
        {
            "id": "original_links",
            "label": "원문 확인",
            "state": "원문 확인",
            "detail": f"{len(links.index)}개 출처 링크",
            "tone": "neutral",
        },
    ]
    return {
        "schema_version": "market_interest_evidence_v1",
        "status": status,
        "symbol": normalized_symbol,
        "name": name,
        "summary_items": summary_items,
        "original_links": links,
        "institutional_caveats": [
            "13F는 분기 공시 기반 지연 자료이며 분기 종료 후 최대 45일 늦게 제출될 수 있습니다.",
            "13F는 숏 포지션, 파생, 헤지, 실시간 거래 의도, 전체 포트폴리오 맥락을 완전히 보여주지 않습니다.",
            "선택 종목 기준 공식 DB 조회에는 CUSIP-symbol mapping과 quarter comparison 설계가 필요합니다.",
        ],
        "source_policy_note": (
            "Official SEC sources can become durable data only after schema and mapping approval; "
            "public analyst aggregators stay external links or session-only metadata in V1."
        ),
        "boundary_note": (
            "시장 관심 근거는 조사 보조 정보입니다. 추천, 점수화, 매매 신호, "
            "자동 catalyst 판정, live trading, broker order, auto rebalance와 연결하지 않습니다."
        ),
    }


__all__ = [
    "MARKET_INTEREST_LINK_COLUMNS",
    "build_market_interest_original_links",
    "build_market_interest_read_model",
]
```

- [ ] **Step 2: Run GREEN**

Run the same two tests. Expected: PASS.

### Task 4: RED Tests For UI Wiring

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify later: `app/web/overview/market_movers_helpers.py`

- [ ] **Step 1: Write failing UI contract tests**

Add tests:

```python
def test_market_movers_selected_investigation_adds_market_interest_action_and_tab(self) -> None:
    source = Path("app/web/overview/market_movers_helpers.py").read_text(encoding="utf-8")

    self.assertIn("build_market_interest_read_model", source)
    self.assertIn("시장 관심 근거 확인", source)
    self.assertIn('"시장 관심"', source)
    self.assertIn("애널리스트 관심", source)
    self.assertIn("기관 보유 배경", source)
    self.assertIn("13F는 분기 공시 기반 지연 자료", source)
    self.assertNotIn("기관이 지금 사고", source)
    self.assertNotIn("매수 신호", source)
```

```python
@patch("app.web.overview.market_movers_helpers.st")
def test_market_mover_market_interest_react_event_sets_session_state_without_provider_fetch(self, mock_st: MagicMock) -> None:
    from app.web.overview.market_movers_helpers import _dispatch_market_mover_investigation_react_event

    mock_st.session_state = {}
    metadata = {}
    result = _dispatch_market_mover_investigation_react_event(
        {"event": {"id": "fetch_market_interest", "nonce": 456}},
        symbol="NET",
        identity={"Name": "Cloudflare Inc"},
        metadata_key="overview_market_mover_metadata__NET",
        metadata=metadata,
        refresh_target={"enabled": False},
    )

    self.assertEqual(result, metadata)
    self.assertIn("overview_market_mover_metadata__NET__market_interest", mock_st.session_state)
    self.assertEqual(mock_st.session_state["overview_market_mover_metadata__NET__market_interest"]["symbol"], "NET")
    mock_st.rerun.assert_called_once()
```

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_selected_investigation_adds_market_interest_action_and_tab tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_market_interest_react_event_sets_session_state_without_provider_fetch
```

Expected: FAIL because the helper has no market-interest import/action/tab.

### Task 5: GREEN UI Wiring

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`

- [ ] **Step 1: Import the market-interest read model**

Add:

```python
from app.services.overview.market_interest import build_market_interest_read_model
```

- [ ] **Step 2: Add session key helper**

Add near `_market_mover_statement_refresh_session_key`:

```python
def _market_mover_market_interest_session_key(metadata_key: str) -> str:
    return f"{metadata_key}__market_interest"
```

- [ ] **Step 3: Add action**

Update `_market_mover_investigation_react_actions` so its default actions are:

```python
[
    {"id": "fetch_news_metadata", "label": "뉴스 메타데이터 조회", "kind": "secondary"},
    {"id": "fetch_sec_metadata", "label": "SEC 공시 메타데이터 조회", "kind": "secondary"},
    {"id": "fetch_market_interest", "label": "시장 관심 근거 확인", "kind": "secondary"},
]
```

- [ ] **Step 4: Dispatch action without provider fetch**

Update `_dispatch_market_mover_investigation_react_event`:

```python
if action_id not in {"fetch_news_metadata", "fetch_sec_metadata", "fetch_market_interest", "refresh_statement"}:
    return metadata
...
if action_id == "fetch_market_interest":
    interest_key = _market_mover_market_interest_session_key(metadata_key)
    st.session_state[interest_key] = build_market_interest_read_model(
        mover={"Symbol": symbol, "Name": identity.get("Name")},
        metadata=metadata,
    )
    st.rerun()
    return metadata
```

- [ ] **Step 5: Add fallback button**

In `_render_market_mover_investigation_actions`, add one more button column and wire:

```python
if action_cols[2].button("시장 관심 근거 확인", ...):
    interest_key = _market_mover_market_interest_session_key(metadata_key)
    st.session_state[interest_key] = build_market_interest_read_model(
        mover={"Symbol": symbol, "Name": identity.get("Name")},
        metadata=metadata,
    )
```

Move statement refresh to the next column.

- [ ] **Step 6: Add market-interest tab**

In `_render_market_mover_selected_investigation_fragment`, read:

```python
interest_key = _market_mover_market_interest_session_key(metadata_key)
market_interest_model = st.session_state.get(interest_key)
if not isinstance(market_interest_model, dict):
    market_interest_model = build_market_interest_read_model(
        mover={"Symbol": symbol, "Name": identity.get("Name")},
        metadata=None,
    )
```

Change tabs to:

```python
clue_tabs = st.tabs(["기본 지표", "시장 관심", "뉴스", "SEC 공시", "외부 검색"])
```

Render `시장 관심` with summary items, caveats, and original link table. Use `_market_mover_open_link_frame` and `_market_mover_metadata_column_config` so `열기` remains clickable.

- [ ] **Step 7: Run GREEN**

Run the two UI tests. Expected: PASS.

### Task 6: Focused Regression Tests And Compile

**Files:**
- Test only.

- [ ] **Step 1: Run focused service tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
```

Expected: PASS.

- [ ] **Step 2: Compile changed Python**

Run:

```bash
.venv/bin/python -m py_compile app/services/overview/market_interest.py app/services/overview/why_it_moved.py app/services/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/jobs/overview_actions.py
```

Expected: exit 0.

### Task 7: Documentation Sync

**Files:**
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify task docs under `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/`

- [ ] **Step 1: Update durable docs minimally**

Document:

```text
Market Interest V1 is a selected-symbol investigation helper under Market Movers.
Analyst sources are external/session-only only.
SEC/news metadata reuses existing selected-symbol boundaries.
13F is official durable candidate only; no DB schema in V1 because CUSIP-symbol mapping is unresolved.
No recommendation, score, buy/sell signal, live institutional-intent claim, article/report/filing body storage.
```

- [ ] **Step 2: Update task RUNS with command outcomes**

Record each RED/GREEN command and QA command with short result.

### Task 8: Browser QA

**Files:**
- Generated screenshot only, not staged.

- [ ] **Step 1: Start or reuse Streamlit**

Run the app locally using the repo’s existing Streamlit command if no server is running.

- [ ] **Step 2: Open Market Movers and capture screenshot**

Use browser QA to verify:

```text
Overview > Market Movers loads.
Selected-symbol manual panel has a 시장 관심 action.
시장 관심 tab renders analyst/news/SEC/13F/original link context.
13F caveat is visible.
No buy/sell/signal/score language appears in the new panel.
```

Save screenshot as a local generated artifact and do not stage it.

### Task 9: Final Verification And Commit

**Files:**
- All changed implementation/tests/docs.

- [ ] **Step 1: Run final verification**

Run:

```bash
git diff --check
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py
```

Expected: all exit 0.

- [ ] **Step 2: Review git status and stage only intended files**

Do not stage:

```text
market-movers-*-qa.png
sentiment-graph-*-qa.png
.playwright-mcp/
run_history/
run_artifacts/
registries/
saved/
```

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/superpowers/plans/2026-07-08-market-interest-evidence.md \
  app/services/overview/market_interest.py \
  app/web/overview/market_movers_helpers.py \
  tests/test_service_contracts.py \
  .aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708 \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/data/README.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Market Movers 시장 관심 근거 패널 추가"
```

Expected: commit succeeds.

---

## Self-Review

- Spec coverage: 0차 context was completed before plan. 1차 UI/UX design is captured in Task 1 and implemented in Tasks 4-5. 2차 safe MVP is covered by the selected-symbol, user-triggered, session-only/link-only service and UI. 3차 13F official data design is covered by source policy, caveats, docs, and explicit DB deferral. 4차 conservative summary is covered by `summary_items`.
- Placeholder scan: no `TBD`, `TODO`, or "implement later" instructions remain.
- Type consistency: the service returns `pd.DataFrame` link rows with `MARKET_INTEREST_LINK_COLUMNS`; UI uses existing open-link frame helpers.
