# Turnaround 공시 기반 분기 산출·표시 Implementation Plan

Status: Approved Implementation Plan
Last Updated: 2026-07-16

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 동등한 SEC concept family의 확정 공시값으로 누락된 Q4를 안전하게 산출하고, 산출 분기와 이를 포함한 TTM 지표를 전환분석 UI에서 직접 공시값과 구분한다.

**Architecture:** 기존 `Ingestion -> DB -> Loader -> pure calculator -> Service -> React` 경계는 유지한다. exact-concept 해석 이후 guarded family fallback을 적용하고, quarterly series가 구조화 provenance를 전달하며, React는 source-quarter marker와 active inspector에서만 중립적인 설명을 표시한다.

**Tech Stack:** Python 3, pandas, unittest, React 18, TypeScript, SVG, CSS, Vite.

## Global Constraints

- authoritative specification은 같은 task의 `DESIGN.md`다.
- 현재 linked `codex/sub-dev` worktree에서 inline으로 실행하며 새 worktree나 subagent를 만들지 않는다.
- unrelated untracked `researches/active/2026-07-market-interest-free-source-benchmark/`는 수정·stage·commit하지 않는다.
- direct Q4가 있으면 항상 우선한다.
- explicit `TURNAROUND_CONCEPT_FAMILIES` 밖의 concept는 결합하지 않는다.
- symbol, fiscal year, unit, primary period, PIT cutoff가 맞지 않으면 결측을 유지한다.
- forecast, interpolation, taxonomy 문자열 유사도 매칭, schema/provider/collector 변경을 만들지 않는다.
- 사용자 문구는 `추정`이 아니라 `공시 기반 산출`로 통일한다.
- screenshot, run history, temp artifact는 commit하지 않는다.

## Goal

SEC 공시의 동등한 concept 계열에서 FY와 Q1~Q3가 서로 다른 taxonomy 이름을 사용해도, 엄격한 회계·기간 조건을 만족하면 Q4를 공시 기반으로 산출한다. 산출된 분기와 이를 포함한 TTM 지표는 화면에서 직접 공시값과 구분한다.

## 이걸 하는 이유?

Moderna 2023년 매출은 Q1/Q2의 `Revenues`와 Q3/FY의 `RevenueFromContractWithCustomerExcludingAssessedTax`로 concept 이름이 바뀐다. 현재 resolver는 exact concept별로만 FY 차감을 수행하여 실제 공시 숫자가 모두 있어도 2023-Q4 매출을 만들지 못하고, 그 한 분기 때문에 네 개 TTM 구간이 끊긴다. 그래프의 결측 보존 원칙은 유지하면서, 동일 의미로 명시된 concept family 안의 확정 공시값을 안전하게 사용할 필요가 있다.

## Scope

- `resolve_discrete_quarters`의 동등 concept-family Q4 fallback
- derived-quarter 및 TTM 포함 여부의 구조화 provenance
- 전환분석 차트와 inspector의 `공시 기반 산출` 표기
- MRNA 회귀 테스트, 기존 exact-concept/결측/PIT 회귀 테스트
- 실제 DB와 desktop/420px Browser QA

## Out Of Scope

- 결측값 보간 또는 forecast
- 임의 taxonomy concept 자동 유사도 매칭
- schema, collector, provider, DB row 변경
- 직접 공시값을 산출값으로 대체
- universe-wide backfill 또는 진단 job panel

## Roadmap

1. MRNA 회귀 fixture와 안전 조건을 RED 테스트로 고정한다.
2. 동등 concept-family Q4 산출과 provenance를 구현한다.
3. 차트/inspector에 중립적인 산출 표기를 추가한다.
4. focused regression, actual DB, Browser QA와 문서 정렬을 수행한다.

## Stop Condition

- 직접 Q4가 없고 FY/Q1/Q2/Q3가 모두 primary filing facts이며 symbol, fiscal year, unit, concept family가 맞을 때만 Q4가 산출된다.
- 산출값의 `available_at`은 모든 operand가 이용 가능해진 날짜보다 빠르지 않다.
- MRNA 2023-Q4 매출 `2.811B`, 원가 `0.929B`, GP `1.882B`, 영업이익 `0.006B`가 재현된다.
- 산출 분기와 해당 분기를 포함한 TTM 표시가 직접 공시와 구분된다.
- 안전 조건이 맞지 않으면 기존 결측과 끊긴 선을 유지한다.

## File Ownership Map

- `finance/data/us_stock_turnaround.py`: mixed-concept Q4 fallback, metric provenance, TTM derived-input propagation.
- `tests/test_us_stock_turnaround.py`: MRNA fixture, safety guards, provenance/TTM regressions.
- `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx`: typed provenance, source marker, badge, formula, TTM notice.
- `app/web/streamlit_components/market_context_valuation/src/style.css`: neutral marker/badge/formula styles and mobile wrapping.
- `tests/test_market_context_valuation.py`: React source contract and service passthrough regression.
- `app/services/overview/us_stock_turnaround.py`: 수정하지 않고 existing recursive JSON-safe passthrough만 검증한다.

---

### Task 1: Mixed-concept Q4 family fallback

**Files:**
- Modify: `tests/test_us_stock_turnaround.py`
- Modify: `finance/data/us_stock_turnaround.py:180-290`
- Modify: task `RUNS.md`, `STATUS.md`

**Interfaces:**
- Consumes: `resolve_discrete_quarters(... concepts, units, as_of_date)`와 existing exact-concept candidates.
- Produces: guarded family가 완전할 때 기존 resolved-row schema의 Q4 하나.
- Preserves: direct-quarter priority, primary-period filter, PIT cutoff, honest missingness.

- [x] **Step 1: Write the MRNA-like failing test**

`TurnaroundQuarterResolverTests`에 다음 핵심 fixture를 추가한다.

```python
old = "us-gaap:Revenues"
current = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
rows = [
    _fact(value=1_862_000_000.0, period_start="2023-01-01", period_end="2023-03-31", available_at="2023-05-04", fiscal_year=2023, fiscal_quarter=1, concept=old, symbol="MRNA"),
    _fact(value=344_000_000.0, period_start="2023-04-01", period_end="2023-06-30", available_at="2023-08-03", fiscal_year=2023, fiscal_quarter=2, concept=old, symbol="MRNA"),
    _fact(value=1_831_000_000.0, period_start="2023-07-01", period_end="2023-09-30", available_at="2023-11-03", fiscal_year=2023, fiscal_quarter=3, concept=current, symbol="MRNA"),
    _fact(value=6_848_000_000.0, period_start="2023-01-01", period_end="2023-12-31", available_at="2024-02-23", fiscal_year=2023, fiscal_quarter=None, period_type="FY", concept=current, symbol="MRNA", accession_no="2023-FY"),
]
resolved = resolve_discrete_quarters(
    rows, metric="revenue", concepts=(current, old), units=("USD",), as_of_date="2024-03-01",
)
q4 = next(row for row in resolved if row["fiscal_quarter"] == 4)
self.assertEqual(q4["value"], 2_811_000_000.0)
self.assertEqual(q4["available_at"], "2024-02-23")
self.assertEqual(q4["derivation"], "fy_minus_q1_q2_q3")
self.assertEqual({item["concept"] for item in q4["provenance"]["operands"]}, {old, current})
```

- [x] **Step 2: Verify RED**

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround.TurnaroundQuarterResolverTests.test_resolver_derives_q4_across_allowlisted_revenue_concepts -v
```

Expected: `next(...)` ERROR because no exact concept group owns FY plus Q1/Q2/Q3.

- [x] **Step 3: Implement minimal guarded fallback**

기존 exact selection 뒤 normalized FY rows를 `(symbol, fiscal_year, normalized unit)`로 묶는다. Q4가 없고 selected Q1/Q2/Q3가 모두 같은 unit이면 priority가 가장 높은 FY row를 골라 다음 계산을 수행한다.

```python
q_values = [float(row["value"]) for row in quarter_rows]
logical_operands = [fiscal_year_row] + [_resolved_as_operand(row) for row in quarter_rows]
selected[q4_key] = _resolved_row(
    fiscal_year_row,
    metric=metric,
    fiscal_quarter=4,
    value=fiscal_year_row["value_number"] - sum(q_values),
    available_at=max([fiscal_year_row["available_at_ts"]] + [pd.Timestamp(row["available_at"]) for row in quarter_rows]),
    derivation="fy_minus_q1_q2_q3",
    operands=logical_operands,
)
```

- [x] **Step 4: Add guard regressions**

allowlist 밖 concept가 operand가 되지 않음, direct Q4가 FY subtraction보다 우선함, FY filing이 `as_of_date` 이후면 Q4가 생기지 않음을 각각 assert한다.

- [x] **Step 5: Verify GREEN and commit**

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround.TurnaroundQuarterResolverTests -v
.venv/bin/python -m unittest tests.test_us_stock_turnaround -v
.venv/bin/python -m py_compile finance/data/us_stock_turnaround.py
git diff --check
```

Update task evidence and commit `전환분석 동등 공시 concept Q4 산출 보정`.

---

### Task 2: Quarter and TTM provenance contract

**Files:**
- Modify: `tests/test_us_stock_turnaround.py`
- Modify: `finance/data/us_stock_turnaround.py:579-710`
- Modify: `tests/test_market_context_valuation.py`
- Modify: task `RUNS.md`, `STATUS.md`

**Interfaces:**
- Consumes: resolved fact의 `derivation`과 `provenance.operands`.
- Produces: `metric_provenance`, `derived_metrics`, `ttm_derived_metrics` on every timeline row.
- Preserves: existing numeric field names, TTM missingness, service schema version.

- [ ] **Step 1: Write failing provenance tests**

MRNA revenue/cost/operating fixture에서 다음 계약을 assert한다.

```python
q4 = next(row for row in result["timeline"] if row["slot_key"] == "2023-Q4")
self.assertEqual(q4["revenue"], 2_811_000_000.0)
self.assertEqual(q4["gross_profit"], 1_882_000_000.0)
self.assertEqual(q4["operating_income"], 6_000_000.0)
self.assertEqual(q4["metric_provenance"]["revenue"]["source_kind"], "FILING_DERIVED")
self.assertEqual(q4["metric_provenance"]["gross_profit"]["rule"], "revenue_minus_cost")
self.assertIn("revenue", q4["derived_metrics"])
self.assertIn("gross_profit", q4["derived_metrics"])
q1_2024 = next(row for row in result["timeline"] if row["slot_key"] == "2024-Q1")
self.assertIn("revenue", q1_2024["ttm_derived_metrics"])
self.assertIn("gross_profit", q1_2024["ttm_derived_metrics"])
```

Direct-only fixture에는 두 derived list가 비어 있음을 별도 assert한다.

- [ ] **Step 2: Verify RED**

새 test method 두 개를 `-v`로 실행한다. Expected: timeline에 provenance keys가 없어 FAIL/ERROR.

- [ ] **Step 3: Propagate per-metric provenance**

각 timeline row를 다음처럼 초기화하고 fact를 읽을 때 채운다.

```python
"metric_provenance": {},
"derived_metrics": [],
```

```python
derivation = str(fact.get("derivation") or "reported_quarter")
source_kind = "REPORTED" if derivation == "reported_quarter" else "FILING_DERIVED"
row["metric_provenance"][metric] = {
    "source_kind": source_kind,
    "rule": derivation,
    "operands": list(dict(fact.get("provenance") or {}).get("operands") or []),
}
if source_kind == "FILING_DERIVED":
    row["derived_metrics"].append(metric)
```

`revenue_minus_cost`에는 revenue/cost resolved facts를 operand로 가진 `FILING_DERIVED` provenance를 기록하고 `gross_profit`을 append한다.

- [ ] **Step 4: Propagate TTM derived inputs**

`index >= 3`에서 `_sum_window`와 동일한 네 row의 `derived_metrics` union을 정렬하여 `ttm_derived_metrics`에 저장한다. 네 input 중 하나가 결측이면 기존 TTM 값은 계속 `None`이며 provenance가 숫자를 대신 만들지 않는다.

- [ ] **Step 5: Verify JSON-safe service passthrough**

`build_us_stock_turnaround_read_model` 결과의 nested provenance가 `json.dumps(model)` 가능한 mapping/list이며 값이 보존됨을 service test로 확인한다. Service production file은 수정하지 않는다.

- [ ] **Step 6: Verify GREEN and commit**

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_market_context_valuation -v
.venv/bin/python -m py_compile finance/data/us_stock_turnaround.py app/services/overview/us_stock_turnaround.py
git diff --check
```

Update task evidence and commit `전환분석 분기 산출 근거 계약 추가`.

---

### Task 3: Neutral marker and inspector disclosure

**Files:**
- Modify: `tests/test_market_context_valuation.py`
- Modify: `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Modify: product `component_static` bundle through `npm run build`
- Modify: task `RUNS.md`, `STATUS.md`

**Interfaces:**
- Consumes: `metric_provenance`, `derived_metrics`, `ttm_derived_metrics`.
- Produces: source-quarter SVG marker, active inspector badge/formula, TTM derived-input notice.
- Preserves: gap segments, pointer selection, 8/12/20 windows, zero axes, existing layout.

- [ ] **Step 1: Write the failing React contract**

```python
def test_turnaround_discloses_filing_derived_quarters_without_calling_them_estimates(self) -> None:
    source = Path("app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx").read_text()
    style = Path("app/web/streamlit_components/market_context_valuation/src/style.css").read_text()
    for token in (
        "metric_provenance?: Record<string, MetricProvenance>",
        "derived_metrics?: string[]",
        "ttm_derived_metrics?: string[]",
        "공시 기반 산출",
        "공시 기반 산출값 포함",
        "turnaround-derived-marker",
        "turnaround-derived-badge",
    ):
        self.assertIn(token, source + style)
    self.assertNotIn("추정값", source)
```

- [ ] **Step 2: Verify RED**

새 test method를 `-v`로 실행한다. Expected: provenance types, copy and styles are absent.

- [ ] **Step 3: Add typed provenance helpers**

`MetricOperand`, `MetricProvenance`와 optional point fields를 추가한다. `derivationFormula`는 known rules만 다음처럼 표현한다.

```text
fy_minus_q1_q2_q3 -> FY 6.85B − Q1 1.86B − Q2 0.34B − Q3 1.83B
h1_minus_q1 -> H1 ... − Q1 ...
nine_months_minus_h1 -> 9M ... − H1 ...
revenue_minus_cost -> 매출 ... − 원가 ...
```

Unknown rule은 badge는 유지하지만 formula를 만들지 않는다.

- [ ] **Step 4: Render source marker and disclosure**

- legend에 `공시 기반 산출`을 추가한다.
- `derived_metrics.length > 0`인 source quarter에 neutral SVG circle과 `<title>`을 추가한다.
- active inspector slot label 옆에 `공시 기반 산출` badge를 표시한다.
- primary derivation은 revenue, gross profit, 나머지 metric 순서로 하나의 formula만 표시한다.
- margin TTM이 revenue/gross-profit/operating-income 산출 input을 포함하면 `TTM 지표에 공시 기반 산출값 포함`을 표시한다.
- Cash chart도 OCF/CapEx source marker와 TTM 포함 notice를 같은 규칙으로 표시한다.

- [ ] **Step 5: Add neutral responsive styles**

`.turnaround-derived-marker`, `.legend-derived`, `.turnaround-derived-heading`, `.turnaround-derived-badge`, `.turnaround-derived-detail`, `.turnaround-derived-note`를 blue-gray neutral palette로 추가하고 420px에서 wrapping되게 한다.

- [ ] **Step 6: Verify GREEN, build and commit**

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation tests.test_us_stock_turnaround -v
cd app/web/streamlit_components/market_context_valuation && npm run build
git diff --check
```

Stage source/tests/styles/product static bundle only and commit `전환분석 공시 기반 산출 표시 추가`.

---

### Task 4: Actual QA, Browser QA and closeout

**Files:**
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: Tasks 1~3 complete source and tests.
- Produces: actual MRNA evidence, QA screenshot, durable handoff, final commit.

- [ ] **Step 1: Verify actual MRNA DB-only values**

Provider call 없이 current read model을 만들고 다음을 기록한다.

```text
2023-Q4 revenue 2.811B / cost 0.929B / GP 1.882B / operating income 0.006B
2023-Q4 revenue and GP source_kind FILING_DERIVED
2024-Q1~Q3 TTM margins finite with derived-input disclosure
```

AAPL direct-data와 RIVN transition model에는 false derived badge가 생기지 않아야 한다.

- [ ] **Step 2: Run final regression**

```bash
.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation -v
.venv/bin/python -m py_compile finance/data/us_stock_turnaround.py app/services/overview/us_stock_turnaround.py
cd app/web/streamlit_components/market_context_valuation && npm run build
git diff --check
git status --short
```

Repository-established broader unittest command도 실행하고 baseline 외 실패는 별도로 기록한다.

- [ ] **Step 3: Perform Browser QA**

Current runbook으로 Finance app을 실행한다. MRNA desktop/420px에서 marker, badge, formula, TTM notice, continuous line, overflow 0, new console error 0을 확인한다. AAPL/RIVN false badge도 확인하고 screenshot 한 장을 staged files 밖에 저장한다.

- [ ] **Step 4: Synchronize docs and verify completion**

`finance-doc-sync`로 implemented behavior와 PIT/provenance 의미를 정렬한다. 모든 docs/static 변경 후 `verification-before-completion` 명령을 fresh-run한다.

- [ ] **Step 5: Commit closeout**

Owned source/tests/docs/static bundle만 stage하고 commit `전환분석 분기 산출 QA와 문서 정렬`.

## Completion Contract

- 전체 roadmap 4/4가 evidence와 함께 완료된다.
- MRNA 단절 원인이 실제 공시 기반 Q4로 복구된다.
- direct/derived provenance가 사용자에게 숨겨지지 않는다.
- guard 실패는 계속 결측이며 line renderer는 임의 보간하지 않는다.
- 후속 concept-family audit은 별도 task다.
