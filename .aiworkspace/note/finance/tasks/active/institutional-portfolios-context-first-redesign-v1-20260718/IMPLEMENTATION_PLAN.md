# Institutional Portfolios Context-First Redesign V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Institutional Portfolios를 선택 기관의 맥락이 먼저 보이는 화면으로 재구성하고, 모든 13F 보유 row를 검색·필터·정렬·페이지 탐색 가능하게 하며, 이전 분기·mapping·가격 coverage 의미를 정확히 분리한다.

**Architecture:** Python service가 `institutional_portfolios_workbench_v2` read model과 정확한 context/coverage/comparison 계약을 만들고, React workbench는 그 payload 전체를 로컬 상태로 탐색한다. Streamlit은 manager/security/price/popularity의 명시적 event만 소비하며 React 검색·필터·페이지 상태는 보관하지 않는다.

**Tech Stack:** Python 3.12, pandas, unittest/pytest, Streamlit, React 18, TypeScript, Vite, CSS.

## Global Constraints

- 첫 화면의 주인공은 manager directory가 아니라 `선택 기관의 포트폴리오 맥락 이해`다.
- React payload schema는 정확히 `institutional_portfolios_workbench_v2`다.
- 전체 보유 기본 page size는 정확히 `50`이며 `rows.slice(0, 80)` 같은 silent hard cut을 남기지 않는다.
- holdings search target은 ticker, issuer name, CUSIP이고 sort는 weight descending, reported value descending, issuer ascending을 지원한다.
- `comparison_available=False`이면 user-facing change groups/items를 노출하지 않는다.
- mapping count coverage, mapped reported-value weight coverage, performance coverage를 서로 다른 값으로 표현한다.
- ticker 미연결 row도 issuer/CUSIP identity로 보이며 가격 수집 action을 제공하지 않는다.
- React direct security search는 Enter 또는 명시 버튼에서만 Streamlit event를 보낸다.
- SEC/provider fetch를 render 중 추가하지 않고 refresh는 secondary action으로 유지한다.
- allocation donut과 custom price chart의 line/candle, daily/weekly/monthly, volume/navigator 기능은 유지한다.
- 추천, 현재 매수/매도 의도, live approval, broker action, 운영 run/job 진단 panel을 추가하지 않는다.
- 420px에서 page-level horizontal overflow가 없어야 한다.

---

### Task 1: V2 Context, Coverage, Comparison Read Model

**Files:**
- Modify: `tests/test_institutional_portfolios.py`
- Modify: `app/services/institutional_portfolios.py`

**Interfaces:**
- Consumes: `build_institutional_workbench_payload(model, managers, interest_model, popularity_model, ...) -> dict[str, Any]`의 기존 호출 계약.
- Produces: payload keys `context_summary`, `coverage`, `holdings_explorer`, `security_search`; 기존 `holdings_table`, `hero`, `portfolio_performance`, `interest`, `popularity`는 compatibility를 위해 유지한다.

- [ ] **Step 1: V2 schema와 993-row full explorer를 요구하는 실패 테스트를 작성한다**

```python
def test_workbench_v2_keeps_all_holdings_for_client_side_explorer(self) -> None:
    holdings = pd.DataFrame([
        {
            "issuer_name": f"Issuer {index:04d}",
            "cusip": f"{index:09d}",
            "reported_value": 1_000 - index,
            "shares_or_principal_amount": 10,
        }
        for index in range(993)
    ])
    model = build_institutional_portfolio_model(_filing_frame(), holdings)
    payload = build_institutional_workbench_payload(model)
    self.assertEqual(payload["schema_version"], "institutional_portfolios_workbench_v2")
    self.assertEqual(payload["holdings_explorer"]["default_page_size"], 50)
    self.assertEqual(len(payload["holdings_explorer"]["rows"]), 993)
    self.assertEqual(payload["coverage"]["holding_count_total"], 993)
```

- [ ] **Step 2: 새 테스트가 기존 v1/필드 부재로 실패하는지 확인한다**

Run: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfolioReadModelTests::test_workbench_v2_keeps_all_holdings_for_client_side_explorer`

Expected: FAIL because schema is v1 and `holdings_explorer`/`coverage` do not exist.

- [ ] **Step 3: 비교 불가 gate와 coverage 분리를 요구하는 실패 테스트를 작성한다**

```python
def test_workbench_v2_suppresses_change_items_without_previous_filing(self) -> None:
    model = build_institutional_portfolio_model(_filing_frame(), _holding_frame())
    payload = build_institutional_workbench_payload(model)
    self.assertFalse(payload["change_board"]["comparison_available"])
    self.assertEqual(payload["change_board"]["groups"], {})
    self.assertEqual(payload["context_summary"]["comparison_state"], "unavailable")
    self.assertEqual(payload["coverage"]["holding_count_total"], 2)
    self.assertEqual(payload["coverage"]["holding_count_mapped"], 1)
    self.assertEqual(payload["coverage"]["holding_count_unmapped"], 1)
    self.assertIn("mapped_weight_pct", payload["coverage"])
    self.assertIn("performance_covered_weight_pct", payload["coverage"])
```

- [ ] **Step 4: context/coverage/explorer/security helpers와 v2 payload를 최소 구현한다**

```python
def _build_coverage(holding_rows: list[dict[str, Any]], performance_model: dict[str, Any]) -> dict[str, Any]:
    total = len(holding_rows)
    mapped = [row for row in holding_rows if row.get("mapping_status") == "mapped" and row.get("symbol")]
    ambiguous = [row for row in holding_rows if row.get("mapping_status") == "ambiguous"]
    mapped_weight_pct = sum(_num(row.get("weight_pct")) for row in mapped)
    performance_weight_pct = _num(performance_model.get("covered_weight_pct"))
    return {
        "holding_count_total": total,
        "holding_count_mapped": len(mapped),
        "holding_count_unmapped": total - len(mapped) - len(ambiguous),
        "holding_count_ambiguous": len(ambiguous),
        "mapped_weight_pct": mapped_weight_pct,
        "mapped_weight_label": _pct_label(mapped_weight_pct),
        "performance_covered_weight_pct": performance_weight_pct,
        "performance_covered_weight_label": _pct_label(performance_weight_pct),
    }
```

`context_summary`는 manager headline, top5 concentration, largest mapped sector, mapping coverage, comparison readiness로 deterministic Korean summary를 만든다. `holdings_explorer.rows`는 prepared holdings 전체를 참조하고 `default_page_size=50`, filters/sorts metadata를 포함한다. `security_search`는 current query, state, explicit submit event id `security_search`를 제공한다.

- [ ] **Step 5: focused read-model tests를 통과시킨다**

Run: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py -k 'workbench or coverage or previous_filing'`

Expected: PASS.

- [ ] **Step 6: Task 1 변경을 커밋한다**

```bash
git add app/services/institutional_portfolios.py tests/test_institutional_portfolios.py
git commit -m "기관 포트폴리오 v2 맥락 모델 추가"
```

### Task 2: Context-First React IA And Complete Holdings Explorer

**Files:**
- Modify: `tests/test_institutional_portfolios.py`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
- Modify only if event adapter requires it: `app/web/institutional_portfolios.py`

**Interfaces:**
- Consumes: Task 1의 `WorkbenchPayload` v2 fields and existing Streamlit interaction object `{id, nonce, ...}`.
- Produces: `security_search` event `{id: "security_search", query, nonce}`; mapped holding drilldown reuses `holding_drilldown`; unmapped identity selection remains local and never emits price collection.

- [ ] **Step 1: source contract 실패 테스트를 작성한다**

```python
def test_workbench_v2_has_complete_holdings_explorer_and_explicit_security_search(self) -> None:
    component_source = _component_source()
    self.assertIn('schema_version: "institutional_portfolios_workbench_v2"', component_source)
    self.assertNotIn("rows.slice(0, 80)", component_source)
    self.assertIn("HOLDINGS_PAGE_SIZE = 50", component_source)
    self.assertIn('id: "security_search"', component_source)
    self.assertIn("holdingSearch", component_source)
    self.assertIn("mappingFilter", component_source)
    self.assertIn("holdingSort", component_source)
    self.assertIn("visibleHoldings", component_source)
    self.assertIn("INSTITUTIONAL PORTFOLIO CONTEXT", component_source)
```

- [ ] **Step 2: source contract가 기존 v1/slice/search 부재로 실패하는지 확인한다**

Run: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_workbench_v2_has_complete_holdings_explorer_and_explicit_security_search`

Expected: FAIL.

- [ ] **Step 3: payload type과 local explorer/search state를 구현한다**

```tsx
const HOLDINGS_PAGE_SIZE = 50;
type HoldingSort = "weight_desc" | "value_desc" | "issuer_asc";
type MappingFilter = "all" | "mapped" | "unresolved";

const [holdingSearch, setHoldingSearch] = useState("");
const [mappingFilter, setMappingFilter] = useState<MappingFilter>("all");
const [sectorFilter, setSectorFilter] = useState("all");
const [holdingSort, setHoldingSort] = useState<HoldingSort>("weight_desc");
const [holdingPage, setHoldingPage] = useState(1);
const [securitySearch, setSecuritySearch] = useState(payload.security_search.current_query || "");
```

`visibleHoldings`는 `payload.holdings_explorer.rows` 전체에 ticker/issuer/CUSIP case-insensitive search, mapping/sector filter, stable sort를 적용하고 마지막에 `(page-1)*50`부터 50개만 slice한다. search/filter/sort 변경 시 page를 1로 돌린다.

- [ ] **Step 4: Overview 계열 context hero와 reading order를 구현한다**

```tsx
<div className="ip-context-hero__eyebrow">INSTITUTIONAL PORTFOLIO CONTEXT</div>
<h2>{payload.context_summary.headline}</h2>
<p>{payload.context_summary.summary}</p>
```

manager favorites/search는 compact switcher로 낮추고, hero 오른쪽 basis에 report period, filing date, snapshot, SEC link를 둔다. portfolio context 순서는 allocation/concentration → comparable change board → coverage/sector → supporting hypothetical performance로 바꾼다. 기존 donut과 chart component는 삭제하거나 단순화하지 않는다.

- [ ] **Step 5: holdings explorer UI와 unmapped semantics를 구현한다**

```tsx
const start = filteredHoldings.length ? (holdingPage - 1) * HOLDINGS_PAGE_SIZE + 1 : 0;
const end = Math.min(holdingPage * HOLDINGS_PAGE_SIZE, filteredHoldings.length);
<strong>{start.toLocaleString()}–{end.toLocaleString()} / {filteredHoldings.length.toLocaleString()}</strong>
```

row는 mapped면 ticker, issuer, weight, value, sector를 보여주고 drilldown event를 보낸다. unresolved면 issuer/CUSIP을 primary로 보여주고 `ticker 연결 전` 또는 `mapping 확인 필요` badge를 표시하며 local identity notice만 연다.

- [ ] **Step 6: explicit security search를 구현하고 Streamlit event boundary를 보존한다**

```tsx
const submitSecuritySearch = () => {
  const query = securitySearch.trim();
  if (!query) return;
  Streamlit.setComponentValue({id: "security_search", query, nonce: Date.now().toString()});
};
```

form submit/검색 버튼만 위 handler를 호출한다. `app/web/institutional_portfolios.py`의 `_consume_workbench_event` branch는 `security_search` query를 기존 selected security session key에 저장하고 rerun한다. 입력 change에서는 event를 보내지 않는다.

- [ ] **Step 7: responsive CSS를 구현한다**

```css
@media (max-width: 420px) {
  .ip-context-hero__grid { grid-template-columns: minmax(0, 1fr); }
  .ip-holdings-toolbar { grid-template-columns: minmax(0, 1fr); }
  .ip-holding-row { grid-template-columns: minmax(0, 1fr) auto; }
  .ip-primary-tabs, .ip-secondary-tabs, .ip-manager-favorites { overflow-x: auto; }
}
```

page root와 모든 grid child에 `min-width: 0`, `max-width: 100%`를 적용해 420px page-level overflow를 막는다.

- [ ] **Step 8: source contract와 React build를 통과시킨다**

Run: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py -k 'workbench or event or selected_security'`

Run: `npm run build --prefix app/web/streamlit_components/institutional_portfolios_workbench`

Expected: both PASS.

- [ ] **Step 9: Task 2 변경을 커밋한다**

```bash
git add app/web/institutional_portfolios.py app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx app/web/streamlit_components/institutional_portfolios_workbench/src/style.css tests/test_institutional_portfolios.py
git commit -m "기관 포트폴리오 맥락 우선 탐색 UI 구현"
```

### Task 3: Actual Data QA, Browser QA, And Durable Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RISKS.md`
- Modify as routed by `finance-doc-sync`: `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`, `.aiworkspace/note/finance/docs/PROJECT_MAP.md`, `.aiworkspace/note/finance/docs/ROADMAP.md`, root handoff logs and current task manifest.

**Interfaces:**
- Consumes: completed v2 implementation and local MySQL snapshot.
- Produces: verified commands, one generated Browser QA screenshot outside git staging, explicit deferred mapping/history risks, durable flow documentation.

- [ ] **Step 1: 전체 focused suite와 static checks를 실행한다**

Run: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py`

Run: `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py`

Run: `npm run build --prefix app/web/streamlit_components/institutional_portfolios_workbench`

Run: `git diff --check`

Expected: all PASS, no whitespace errors.

- [ ] **Step 2: actual DB smoke를 수행한다**

Python smoke에서 Berkshire, Bridgewater, Duquesne를 `load_institutional_portfolio_model` → `build_institutional_workbench_payload`로 통과시키고 아래를 assert한다.

```python
assert payload["coverage"]["holding_count_total"] == len(payload["holdings_explorer"]["rows"])
assert payload["holdings_explorer"]["default_page_size"] == 50
assert not payload["change_board"]["groups"] if not payload["change_board"]["comparison_available"] else True
```

Bridgewater는 total이 80보다 큰지 확인해 silent truncation regression을 실제 데이터로 닫는다.

- [ ] **Step 3: desktop과 420px Browser QA를 수행한다**

Streamlit을 별도 port에서 시작하고 Institutional Portfolios로 이동한다. desktop에서 context hero → 전체 보유 → 검색/필터/다음 page → mapped 종목 상세를 확인한다. 420px에서 hero 1-column, tab/filters 사용 가능, page-level horizontal overflow 없음, unresolved row identity와 비활성 가격 action을 확인한다. 최종 desktop 또는 mobile 상태 screenshot 1장을 생성하되 stage하지 않는다.

- [ ] **Step 4: `finance-doc-sync` matrix에 따라 task/durable/root 문서를 정렬한다**

`STATUS.md`에는 3차 구현/QA 완료와 4차 보정 상태를, `RUNS.md`에는 명령과 결과를, `RISKS.md`에는 historical filing 부재와 mapping coverage를 기록한다. durable flow에는 v2 payload, 50-row client pagination, explicit security search, change gate를 반영한다.

- [ ] **Step 5: 문서와 구현 최종 상태를 커밋한다**

```bash
git add .aiworkspace/note/finance app/services/institutional_portfolios.py app/web/institutional_portfolios.py app/web/streamlit_components/institutional_portfolios_workbench/src tests/test_institutional_portfolios.py
git commit -m "기관 포트폴리오 맥락 우선 개편 검증 및 문서화"
```

