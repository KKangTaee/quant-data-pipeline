# Overview Market Context Turnaround Stage Semantics Fix V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AAPL의 stored `USD per share` diluted EPS를 전환분석이 정확히 읽게 하고, 6개 rail에서 전환 신호·이미 양수·PER 적용 가능·영업 개선폭 미달을 구분한다.

**Architecture:** Existing `nyse_financial_statement_values` reader의 duration unit allowlist만 보정하고 schema/writer는 건드리지 않는다. Backend milestone status와 threshold는 보존하되 operating evidence를 보강하고, React에서 `ESTABLISHED`를 UI-local display state로 파생해 transition `MET`과 구분한다.

**Tech Stack:** Python 3.12, pandas, MySQL-backed finance loaders, unittest, React 18, TypeScript, Vite, Streamlit component.

## Global Constraints

- 6개 rail과 independent milestone 계약을 유지하고 앞 단계를 자동 pass하지 않는다.
- operating +1.0%p, two-positive TTM OCF, earnings-turn, four-positive TTM EPS/PER thresholds를 변경하지 않는다.
- source table, schema, collector, UPSERT, provider, 자동 수집을 변경하지 않는다.
- 검색·기업 선택·PER/전환 전환은 DB-only다.
- `ESTABLISHED`는 UI-local display state이며 backend milestone status는 `MET/NOT_MET/UNKNOWN`을 유지한다.
- PER 상대 고평가/저평가 position은 operating/readiness rail과 독립이다.
- 새 run/job/row 진단 panel을 추가하지 않는다.
- unrelated untracked `researches/active/2026-07-market-interest-free-source-benchmark/`는 stage/commit하지 않는다.

---

### Task 1: EPS reader와 operating evidence 계약

**Files:**
- Modify: `tests/test_us_stock_turnaround.py`
- Modify: `finance/loaders/us_stock_turnaround.py:17`
- Modify: `finance/data/us_stock_turnaround.py:778-840`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md`

**Interfaces:**
- Preserves: `load_us_stock_turnaround_inputs(symbol, *, as_of_date=None, visible_quarters=20, query_fn=None) -> dict[str, Any]`.
- Extends: `OPERATING_IMPROVEMENT.evidence` with `current_operating_margin_pct`, `latest_operating_margin_yoy_delta_pp`, and `recent_operating_improvement_count`.
- Preserves: all milestone status names, headline priority, thresholds, and JSON shape outside added evidence keys.

- [x] **Step 1: Write a failing public-loader EPS unit test**

Add to `TurnaroundLoaderTests`:

```python
def test_loader_reads_canonical_usd_per_share_eps_rows(self) -> None:
    from finance.loaders.us_stock_turnaround import load_us_stock_turnaround_inputs

    def query(database: str, sql: str, params: tuple[object, ...]):
        if "FROM nyse_symbol_lifecycle" in sql:
            return [{"symbol": "AAPL", "name": "Apple Inc.", "related_cik": 320193, "exchange": "NASDAQ", "quote_type": "EQUITY", "profile_status": "active", "country": "United States", "source": "sec_company_tickers_exchange"}]
        if "source_period_type = 'duration'" in sql:
            return _metric_facts("diluted_eps", [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7], symbol="AAPL") if "USD per share" in params else []
        return []

    result = load_us_stock_turnaround_inputs("AAPL", as_of_date="2026-07-16", query_fn=query)
    available = [row for row in result["series"]["timeline"] if row.get("status") == "AVAILABLE"]

    self.assertTrue(available)
    self.assertAlmostEqual(available[-1]["ttm_eps"], 6.2)
    self.assertNotIn("diluted_eps", result["coverage"]["missing_concepts"])
```

- [x] **Step 2: Run the loader test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround.TurnaroundLoaderTests.test_loader_reads_canonical_usd_per_share_eps_rows -v
```

Expected: FAIL at `self.assertTrue(available)` because duration query params omit `USD per share`.

- [x] **Step 3: Add the canonical EPS unit**

Change the constant to:

```python
_DURATION_UNITS = ("USD", "USD per share", "USD/share", "USD/shares", "shares")
```

- [x] **Step 4: Run the loader test and confirm GREEN**

Run the Step 2 command.

Expected: PASS with latest TTM EPS `6.2` and no diluted-EPS coverage gap.

- [x] **Step 5: Write a failing operating-evidence test**

Add to `TurnaroundMilestoneAndRiskTests`:

```python
def test_profitable_but_below_threshold_operating_margin_exposes_context(self) -> None:
    from finance.data.us_stock_turnaround import classify_turnaround_milestones

    timeline = _analysis_timeline(ttm_eps=[4.0] * 8)
    margins = [31.1, 31.3, 31.5, 31.75, 31.81, 31.87, 31.97, 32.38]
    deltas = [None, None, None, None, 0.99, 0.83, 0.59, 0.63]
    for row, margin, delta in zip(timeline, margins, deltas):
        row["ttm_operating_margin_pct"] = margin
        row["operating_margin_yoy_delta_pp"] = delta

    evidence = classify_turnaround_milestones(
        {"timeline": timeline},
        per_status="READY",
    )["milestones"]["OPERATING_IMPROVEMENT"]["evidence"]

    self.assertFalse(evidence["operating_margin_improvement"])
    self.assertEqual(evidence["current_operating_margin_pct"], 32.38)
    self.assertEqual(evidence["latest_operating_margin_yoy_delta_pp"], 0.63)
    self.assertEqual(evidence["recent_operating_improvement_count"], 0)
```

- [x] **Step 6: Run the evidence test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround.TurnaroundMilestoneAndRiskTests.test_profitable_but_below_threshold_operating_margin_exposes_context -v
```

Expected: ERROR/FAIL with missing `current_operating_margin_pct` evidence key.

- [x] **Step 7: Expose exact evidence without changing the threshold**

Before `operating_improvement`, calculate:

```python
recent_operating_improvement_count = sum(delta >= 1.0 for delta in operating_deltas)
latest_operating_margin_yoy_delta_pp = latest.get("operating_margin_yoy_delta_pp")
```

Use `recent_operating_improvement_count >= 2` in the existing boolean and add to the milestone evidence:

```python
current_operating_margin_pct=operating_margin,
latest_operating_margin_yoy_delta_pp=latest_operating_margin_yoy_delta_pp,
recent_operating_improvement_count=recent_operating_improvement_count,
```

- [x] **Step 8: Run 1차 regressions**

Run:

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation
.venv/bin/python -m py_compile finance/loaders/us_stock_turnaround.py finance/data/us_stock_turnaround.py
git diff --check
```

Expected: all selected tests PASS; compile and diff check exit 0.

- [x] **Step 9: Record and commit 1차**

Update task `RUNS.md` with RED/GREEN commands and `STATUS.md` to 1/3 complete, then:

```bash
git add finance/loaders/us_stock_turnaround.py finance/data/us_stock_turnaround.py tests/test_us_stock_turnaround.py .aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/RUNS.md .aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md
git commit -m "전환분석 EPS와 영업 근거 경계 보정"
```

---

### Task 2: 6요소 rail semantic display

**Files:**
- Modify: `tests/test_market_context_valuation.py`
- Modify: `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx:121-142`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css:226-239`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md`

**Interfaces:**
- Consumes: existing milestone status/evidence plus Task 1 operating evidence.
- Produces: UI-local display state `"MET" | "ESTABLISHED" | "NOT_MET" | "UNKNOWN"`.
- Preserves: backend payload and Streamlit event behavior.

- [x] **Step 1: Write failing React source-contract tests**

Add to `MarketContextValuationTests`:

```python
def test_turnaround_rail_distinguishes_transition_from_established_state(self) -> None:
    source = Path("app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx").read_text()
    for token in (
        'type MilestoneDisplayState = "MET" | "ESTABLISHED" | "NOT_MET" | "UNKNOWN"',
        "매출 성장 / GP 개선",
        "영업 수익성 개선",
        "OCF 양수 지속",
        "FCF 양수",
        "EPS 양전 신호",
        "TTM EPS 양수",
        "PER 적용 가능",
        "이미 양수",
        "흑자 · 개선폭 미달",
        "분석 가능",
    ):
        self.assertIn(token, source)
    self.assertNotIn('label: "영업손실 축소"', source)
    self.assertNotIn('label: "PER READY"', source)

def test_turnaround_established_state_has_distinct_non_failure_style(self) -> None:
    style = Path("app/web/streamlit_components/market_context_valuation/src/style.css").read_text()
    for token in (".milestone-established", ".milestone-established > span", ".milestone-established strong"):
        self.assertIn(token, style)
```

- [x] **Step 2: Run the new source tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation.MarketContextValuationTests.test_turnaround_rail_distinguishes_transition_from_established_state tests.test_market_context_valuation.MarketContextValuationTests.test_turnaround_established_state_has_distinct_non_failure_style -v
```

Expected: FAIL because `ESTABLISHED`, new copy, and style are absent.

- [x] **Step 3: Add typed semantic state and label maps**

Add above `MilestoneRail`:

```tsx
type MilestoneDisplayState = "MET" | "ESTABLISHED" | "NOT_MET" | "UNKNOWN";
type MilestoneDisplayItem = { key: string; label: string; status: MilestoneDisplayState; detail: string };

const milestoneHeadlineLabels: Record<string, string> = {
  PER_READY: "PER 적용 가능",
  PER_CANDIDATE: "PER 후보",
  EARNINGS_TURN: "EPS 양전 신호",
  CASH_FLOW_TURN: "현금흐름 전환",
  OPERATING_IMPROVEMENT: "영업 개선",
  LOSS_BASELINE: "손실 기준",
  UNCONFIRMED: "근거 확인 중",
};

const analysisStatusLabels: Record<string, string> = {
  READY: "분석 가능",
  PARTIAL: "근거 일부",
  BLOCKED: "분석 전",
};
```

- [x] **Step 4: Build six display items without backend auto-pass**

Inside `MilestoneRail`, derive:

```tsx
const earnings = milestones.EARNINGS_TURN || {};
const perCandidate = milestones.PER_CANDIDATE || {};
const perReady = milestones.PER_READY || {};
const currentOperatingMargin = operatingEvidence.current_operating_margin_pct;
const currentTtmEps = earnings.evidence?.current_ttm_eps;
const operatingEstablished = finite(currentOperatingMargin) && currentOperatingMargin > 0 && !operatingEvidence.operating_margin_improvement;
const epsEstablished = perCandidate.status === "MET" || perReady.status === "MET" || (finite(currentTtmEps) && currentTtmEps > 0);
const unresolved = (status?: string): MilestoneDisplayState => status === "UNKNOWN" || status === "UNCONFIRMED" ? "UNKNOWN" : "NOT_MET";
```

Replace `items` with six `MilestoneDisplayItem` rows using these exact labels/details:

```tsx
const items: MilestoneDisplayItem[] = [
  { key: "REVENUE_GP", label: "매출 성장 / GP 개선", status: operatingEvidence.revenue_direction || operatingEvidence.gross_margin_improvement ? "MET" : unresolved(operating.status), detail: operatingEvidence.revenue_direction || operatingEvidence.gross_margin_improvement ? "확인" : "아직 미확인" },
  { key: "OPERATING_IMPROVEMENT", label: "영업 수익성 개선", status: operatingEvidence.operating_margin_improvement ? "MET" : operatingEstablished ? "ESTABLISHED" : unresolved(operating.status), detail: operatingEvidence.operating_margin_improvement ? "개선 확인" : operatingEstablished ? "흑자 · 개선폭 미달" : "아직 미확인" },
  { key: "CASH_FLOW_TURN", label: "OCF 양수 지속", status: cash.status === "MET" ? "MET" : unresolved(cash.status), detail: cash.status === "MET" ? "확인" : "아직 미확인" },
  { key: "FCF_TURN", label: "FCF 양수", status: cashEvidence.fcf_confirmed ? "MET" : unresolved(cash.status), detail: cashEvidence.fcf_confirmed ? "확인" : "아직 미확인" },
  { key: "EARNINGS_TURN", label: epsEstablished ? "TTM EPS 양수" : "EPS 양전 신호", status: earnings.status === "MET" ? "MET" : epsEstablished ? "ESTABLISHED" : unresolved(earnings.status), detail: earnings.status === "MET" ? "전환 확인" : epsEstablished ? "이미 양수" : "아직 미확인" },
  { key: "PER_READY", label: "PER 적용 가능", status: perReady.status === "MET" ? "MET" : unresolved(perReady.status), detail: perReady.status === "MET" ? "적용 가능" : "아직 미확인" },
];
```

Render `ESTABLISHED` with `milestone-established`, a `●` icon, and the item-specific `detail`. Render UNKNOWN as `? / 근거 부족` and keep `MET` as `✓`.

- [x] **Step 5: Render Korean headline and analysis status**

Use:

```tsx
const headlineLabel = milestoneHeadlineLabels[headline] || headline.replaceAll("_", " ");
const analysisStatus = model?.status || "BLOCKED";
```

Render `headlineLabel` and `analysisStatusLabels[analysisStatus] || analysisStatus` while preserving the existing status CSS class.

- [x] **Step 6: Add established styles**

Add:

```css
.milestone-established { border-color: #c8d9e6; background: #f2f7fb; }
.milestone-established > span { color: #fff; background: #567f9b; }
.milestone-established strong { color: #315a73; }
```

- [x] **Step 7: Run 2차 regressions and production build**

Run:

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation tests.test_us_stock_turnaround tests.test_us_stock_valuation
npm run build
git diff --check
```

Working directory for `npm run build`: `app/web/streamlit_components/market_context_valuation`.

Expected: selected tests PASS; Vite exits 0; new hashed assets are produced; diff check exits 0.

- [x] **Step 8: Record and commit 2차**

Update task `RUNS.md` and `STATUS.md` to 2/3 complete, then:

```bash
git add app/web/streamlit_components/market_context_valuation/src app/web/streamlit_components/market_context_valuation/component_static tests/test_market_context_valuation.py .aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/RUNS.md .aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md
git commit -m "전환단계 기성 흑자 상태 표현 개선"
```

---

### Task 3: Actual AAPL, transition-company Browser QA, and closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` only if durable reader meaning needs clarification
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Verifies: actual DB-only AAPL PER/turnaround EPS equality and six display semantics.
- Verifies: one negative-EPS transition company preserves early-turn/missing states without established auto-pass.
- Produces: one Browser QA screenshot outside git.

- [x] **Step 1: Verify actual AAPL read model**

Run a read-only script using `build_market_context_valuation_read_model(selected_symbol="AAPL")` and assert/record:

```python
per_eps = stock["earnings_scenario"]["current_ttm_eps"]
turn = stock["turnaround_analysis"]
latest = [row for row in turn["series"]["timeline"] if row.get("status") == "AVAILABLE"][-1]
assert turn["milestones"]["headline"] == "PER_READY"
assert turn["milestones"]["milestones"]["PER_READY"]["status"] == "MET"
assert abs(float(latest["ttm_eps"]) - float(per_eps)) < 1e-9
```

Expected: both TTM EPS values are `7.90` with current stored data.

- [x] **Step 2: Verify one negative-EPS actual symbol read-only**

Read RIVN first, with LCID fallback only if RIVN lacks current evidence. Confirm `PER_READY` is not auto-passed and the selected symbol remains recommended to turnaround analysis. Do not run a provider collection action.

- [x] **Step 3: Run focused and repository regression checks**

Run:

```bash
.venv/bin/python -m unittest tests.test_nyse_calendar tests.test_us_stock_freshness tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation
.venv/bin/python -m py_compile finance/loaders/us_stock_turnaround.py finance/data/us_stock_turnaround.py app/services/overview/us_stock_turnaround.py app/services/overview/market_context_valuation.py
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Expected: all focused tests PASS. Record every repository-wide failure/error by exact test id and distinguish existing Streamlit isolation/other-area contracts from task regressions.

- [x] **Step 4: Perform actual Browser QA at desktop and 420px**

Verify AAPL:

- headline `PER 적용 가능`, badge `분석 가능`;
- `영업 수익성 개선 / 흑자 · 개선폭 미달` is neutral established, not failure;
- `TTM EPS 양수 / 이미 양수` and `PER 적용 가능 / 적용 가능` are visible;
- PER tab still shows the same current relative valuation position.

Verify RIVN or LCID:

- transition/negative-EPS state does not become `이미 양수`;
- six slots remain independent and do not auto-pass;
- analysis selector produces no provider action.

For both widths confirm horizontal overflow 0 and new browser console errors 0. Save one representative screenshot under `/Users/taeho/.codex/visualizations/2026/07/15/019f65a4-445f-79b2-8e17-0e3b374b88b3/` and do not stage it.

- [x] **Step 5: Synchronize durable docs**

Use `finance-doc-sync`. Set task status to 3/3 complete, clear active task pointers, register this as latest completed task, and record the canonical EPS-unit reader boundary plus UI-local established semantics at the smallest durable doc set.

- [x] **Step 6: Run final verification and audit scope**

Run fresh:

```bash
.venv/bin/python -m unittest tests.test_nyse_calendar tests.test_us_stock_freshness tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation
npm run build
git diff --check
git status --short
```

Expected: focused tests and build PASS, no whitespace error, only intended closeout docs plus preserved unrelated research folder remain.

- [x] **Step 7: Commit 3차 closeout**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716 .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md .aiworkspace/note/finance/tasks/active/README.md .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "전환단계 의미 보정 QA와 문서 정렬"
```
