# Institutional Holdings Metric Clarity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make quarter-review contribution, 13F popularity value, and source limitations immediately understandable without changing collection, ranking, or performance calculations.

**Architecture:** Python services remain authoritative for contribution selection, popularity semantics, and localized disclosure payloads. React formats percentage points and renders explicit labels in the existing content-first workbench; SEC ingestion caveats, DB schema, refresh flow, the contribution formula, and popularity sort priority remain unchanged.

**Tech Stack:** Python 3, pandas, pytest, React 18, TypeScript 5, CSS, Vitest, Vite, Streamlit custom component, Browser QA.

## Global Constraints

- Keep `contribution_pct = weight_pct * return_pct / 100.0` unchanged.
- Display stock return as `%` and portfolio return contribution as `%p`.
- `수익 기여 상위` contains only `contribution_pct > 0`; `손실 기여 상위` contains only `contribution_pct < 0`; zero appears in neither list.
- Popularity ranking remains holder-count descending, with total reported value only as the secondary tie-breaker.
- Popularity value means same-quarter 13F reported holding value aggregate in US dollars; it is not market cap, volume, or current holding value.
- Preserve the manual `기관 보유 랭킹 불러오기` flow and explicit 13F refresh boundary.
- Keep raw English SEC caveats for ingestion/internal records, but do not render the duplicate English chip list.
- Do not change provider access, refresh cadence, DB schema, stored prices, CUSIP mapping, recommendation, order, or trading boundaries.
- Do not stage generated screenshots, `.superpowers/`, run history, registry changes, or unrelated user files.

---

## File Structure

- Modify `app/services/institutional_quarter_review.py`: select positive contributors and negative detractors by sign while preserving calculation.
- Modify `app/services/institutional_portfolios.py`: add dollar-labeled popularity semantics and localized 13F disclosure payload.
- Modify `tests/test_institutional_quarter_review.py`: lock formula, sign filtering, order, and zero exclusion.
- Modify `tests/test_institutional_portfolios.py`: lock popularity labels, localization, and React source contracts.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts`: provide a signed percentage-point formatter.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts`: test `%p` formatting.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/QuarterReviewPanel.tsx`: render explanation, three metrics, empty states, and `%p` values.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`: label popularity metrics and render one Korean disclosure.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`: style the new rows and responsive behavior.
- Regenerate `app/web/streamlit_components/institutional_portfolios_workbench/component_static/`: tracked production bundle.
- Create `.aiworkspace/note/finance/tasks/active/institutional-holdings-metric-clarity-v1-20260817/`: execution record.
- Modify `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md` only if the verified semantic flow is absent.
- Modify `.aiworkspace/note/finance/tasks/active/README.md`: current/completed task pointer.

---

### Task 1: Lock Contribution and Popularity Semantics in Python

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/institutional-holdings-metric-clarity-v1-20260817/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `tests/test_institutional_quarter_review.py`
- Modify: `tests/test_institutional_portfolios.py`
- Modify: `app/services/institutional_quarter_review.py:155-245`
- Modify: `app/services/institutional_portfolios.py:22-29,312-322,1443-1480,1678-1686`

**Interfaces:**
- Consumes: `build_institutional_price_proxy(...)`, `build_institutional_popularity_model(...)`, and `build_institutional_workbench_payload(...)`.
- Produces: sign-filtered `top_contributors` and `top_detractors`; `reported_value_label: str`; localized `source_caveats.title`, `summary`, and three `items`.

- [ ] **Step 1: Open the active finance task record**

Create the six task files before code changes. `PLAN.md` points to the approved design and this
implementation plan, `DESIGN.md` summarizes the three approved UI changes, and `STATUS.md` starts as:

```markdown
State: active
Current Step: 1/3 의미 계약 고정
```

Record the unchanged data boundaries and pre-2023 absolute-value comparison risk in `RISKS.md`.
Add the task as the current active product task in the active task README.

- [ ] **Step 2: Write the failing sign-separation test**

Append to `tests/test_institutional_quarter_review.py`:

```python
def test_price_proxy_separates_positive_and_negative_contributors_and_omits_zero() -> None:
    from app.services.institutional_quarter_review import build_institutional_price_proxy

    holdings = pd.DataFrame([
        {"cusip": "POS000001", "holding_symbol": "POS", "title_of_class": "COM", "amount_type": "SH", "reported_value": 50},
        {"cusip": "NEG000001", "holding_symbol": "NEG", "title_of_class": "COM", "amount_type": "SH", "reported_value": 30},
        {"cusip": "ZERO00001", "holding_symbol": "ZERO", "title_of_class": "COM", "amount_type": "SH", "reported_value": 20},
    ])
    prices = pd.DataFrame([
        {"symbol": "POS", "date": "2026-03-31", "adj_close": 100},
        {"symbol": "POS", "date": "2026-06-30", "adj_close": 120},
        {"symbol": "NEG", "date": "2026-03-31", "adj_close": 100},
        {"symbol": "NEG", "date": "2026-06-30", "adj_close": 90},
        {"symbol": "ZERO", "date": "2026-03-31", "adj_close": 100},
        {"symbol": "ZERO", "date": "2026-06-30", "adj_close": 100},
    ])

    proxy = build_institutional_price_proxy(
        holdings, prices,
        start_date="2026-03-31", end_date="2026-06-30",
        proxy_id="quarter_holdings_proxy",
    )

    assert next(row for row in proxy["rows"] if row["holding_symbol"] == "POS")["contribution_pct"] == 10.0
    assert [row["holding_symbol"] for row in proxy["top_contributors"]] == ["POS"]
    assert [row["holding_symbol"] for row in proxy["top_detractors"]] == ["NEG"]
```

- [ ] **Step 3: Write failing popularity and disclosure assertions**

Extend `test_popularity_model_ranks_stocks_by_report_period_holder_count`:

```python
self.assertEqual(model["rows"][0]["reported_value_label"], "$8.0M")
self.assertIn("보유 기관 수", model["subtitle"])
self.assertIn("시가총액", model["caveat"])
self.assertIn("거래량", model["caveat"])
```

Extend the existing workbench payload test:

```python
self.assertEqual(payload["source_caveats"]["title"], "13F 자료 해석 시 주의")
self.assertEqual(payload["source_caveats"]["summary"], "지연 공시 · 실시간 매매 신호 아님")
self.assertEqual(len(payload["source_caveats"]["items"]), 3)
self.assertTrue(all("13F holdings are not" not in item for item in payload["source_caveats"]["items"]))
```

- [ ] **Step 4: Run tests and verify the expected failures**

```bash
.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -k "separates_positive or popularity_model_ranks or source_caveats" -q
```

Expected: FAIL because positive/zero rows can enter detractors, `reported_value_label` is absent, and disclosure metadata is absent.

- [ ] **Step 5: Implement sign-specific lists without changing math**

In `build_institutional_price_proxy`, derive and return:

```python
positive_rows = [row for row in rows if row["contribution_pct"] > 0]
negative_rows = [row for row in rows if row["contribution_pct"] < 0]

"top_contributors": sorted(positive_rows, key=lambda row: row["contribution_pct"], reverse=True)[:5],
"top_detractors": sorted(negative_rows, key=lambda row: row["contribution_pct"])[:5],
```

- [ ] **Step 6: Add the dollar formatter and localized disclosure read model**

Beside `_money_label` add:

```python
def _usd_reported_value_label(value: Any) -> str:
    if value is None:
        return "보고가액 확인 불가"
    try:
        if pd.isna(value):
            return "보고가액 확인 불가"
    except TypeError:
        pass
    return f"${_money_label(value)}"
```

Add a user-facing constant without changing `SEC_13F_SOURCE_CAVEATS`:

```python
INSTITUTIONAL_PORTFOLIO_DISCLOSURE_KO = {
    "title": "13F 자료 해석 시 주의",
    "summary": "지연 공시 · 실시간 매매 신호 아님",
    "items": [
        "분기 종료 후 최대 45일 뒤 공개되는 지연 자료이며 실시간 매매 신호가 아닙니다.",
        "공매도, 현금, 일부 파생상품, 헤지, 수수료와 분기 중 매매는 반영되지 않습니다.",
        "수정 신고, 비공개 처리, 원천 추출과 CUSIP-symbol 연결 상태에 따라 표시 내용이 달라질 수 있습니다.",
    ],
}
```

Add to each popularity row:

```python
"reported_value_label": _usd_reported_value_label(row.get("total_reported_value")),
```

Use exact copy:

```python
"subtitle": "보유 기관 수가 많은 종목 순이며, 기관 수가 같으면 13F 보고 보유가액 합계를 비교합니다.",
"caveat": "보고 보유가액 합계는 해당 분기의 지연된 13F 보고값이며 시가총액, 거래량 또는 현재 보유액이 아닙니다.",
```

Project disclosure as:

```python
"source_caveats": {"visible": True, **INSTITUTIONAL_PORTFOLIO_DISCLOSURE_KO},
```

- [ ] **Step 7: Run focused service tests**

```bash
.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q
```

Expected: all selected suites pass.

- [ ] **Step 8: Commit the semantic read model and active task shell**

```bash
git add app/services/institutional_quarter_review.py app/services/institutional_portfolios.py tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py .aiworkspace/note/finance/tasks/active/institutional-holdings-metric-clarity-v1-20260817 .aiworkspace/note/finance/tasks/active/README.md
git commit -m "개선: 기관 보유 지표 의미 계약 명확화"
```

---

### Task 2: Render Contribution as Weight, Return, and Percentage Points

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/QuarterReviewPanel.tsx:45-112,183-218`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css:3234-3245,3536-3540`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**
- Consumes: `ProxyRow.weight_pct`, `return_pct`, `contribution_pct`, and sign-filtered lists from Task 1.
- Produces: `signedPercentagePointLabel(value) -> string`; explanation and three-metric rows; no inline English quarter-review caveat.

- [ ] **Step 1: Write a failing formatter test**

In `workbenchState.test.ts`:

```ts
import { signedPercentagePointLabel } from "./workbenchState";

describe("signedPercentagePointLabel", () => {
  it("formats contribution as signed percentage points", () => {
    expect(signedPercentagePointLabel(2)).toBe("+2.00%p");
    expect(signedPercentagePointLabel(-1.25)).toBe("-1.25%p");
    expect(signedPercentagePointLabel(0)).toBe("0.00%p");
    expect(signedPercentagePointLabel(null)).toBe("-");
  });
});
```

- [ ] **Step 2: Add failing React source-contract assertions**

Extend the existing quarter-review source test:

```python
self.assertIn("포트폴리오 수익 기여 = 이전 보고 비중 × 종목 수익률", quarter_review_source)
self.assertIn("이전 보고 비중", quarter_review_source)
self.assertIn("종목 수익률", quarter_review_source)
self.assertIn("포트폴리오 기여", quarter_review_source)
self.assertIn("수익 기여 상위", quarter_review_source)
self.assertIn("손실 기여 상위", quarter_review_source)
self.assertIn("수익 기여 종목이 없습니다.", quarter_review_source)
self.assertIn("손실 기여 종목이 없습니다.", quarter_review_source)
self.assertIn("수익 기여(%p)", quarter_review_source)
self.assertNotIn('<p className="ip-note">{review.caveat}</p>', quarter_review_source)
```

- [ ] **Step 3: Run tests and verify failure**

```bash
cd app/web/streamlit_components/institutional_portfolios_workbench && npm test -- src/workbenchState.test.ts
cd ../../../..
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "canonical_research_destination_navigation" -q
```

Expected: formatter and new labels are missing.

- [ ] **Step 4: Implement the formatter**

In `workbenchState.ts`:

```ts
export function signedPercentagePointLabel(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "-";
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toFixed(2)}%p`;
}
```

- [ ] **Step 5: Replace the contribution list presentation**

Import the formatter. Make `ContributionList` accept `emptyText` and render:

```tsx
<div className="ip-review-contribution-item" key={`${title}-${row.cusip}`}>
  <span><strong>{row.holding_symbol || row.cusip}</strong><small>{row.issuer_name}</small></span>
  <dl>
    <div><dt>이전 보고 비중</dt><dd>{numberLabel(row.weight_pct)}%</dd></div>
    <div><dt>종목 수익률</dt><dd>{percentLabel(row.return_pct)}</dd></div>
    <div><dt>포트폴리오 기여</dt><dd>{signedPercentagePointLabel(row.contribution_pct)}</dd></div>
  </dl>
</div>
```

Render once above the lists:

```tsx
<div className="ip-review-contribution-guide">
  <strong>포트폴리오 수익 기여 = 이전 보고 비중 × 종목 수익률</strong>
  <span>예: 비중 20% × 수익률 +10% = 포트폴리오 수익률 +2.0%p 기여</span>
</div>
```

Use `수익 기여 상위` / `수익 기여 종목이 없습니다.` and
`손실 기여 상위` / `손실 기여 종목이 없습니다.`. Change the table heading to
`수익 기여(%p)`, use the formatter in its cells, and remove `review.caveat` rendering.

- [ ] **Step 6: Style the guide and three-metric rows**

Add:

```css
.ip-review-contribution-guide { grid-column: 1 / -1; padding: 12px 14px; border: 1px solid #dce6ef; border-radius: 10px; background: #f7fafc; }
.ip-review-contribution-guide strong, .ip-review-contribution-guide span { display: block; }
.ip-review-contribution-guide span { margin-top: 4px; color: #66788c; font-size: 12px; }
.ip-review-contribution-item { padding: 10px 0; border-bottom: 1px solid #e8eef4; }
.ip-review-contribution-item dl { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 8px 0 0; }
.ip-review-contribution-item dt { color: #7c8b9d; font-size: 10px; }
.ip-review-contribution-item dd { margin: 2px 0 0; color: #315674; font-size: 12px; font-weight: 800; }
```

At the existing mobile breakpoint, switch the metric `dl` to one column if it would overflow.

- [ ] **Step 7: Run React and source tests**

```bash
cd app/web/streamlit_components/institutional_portfolios_workbench && npm test && npm run typecheck
cd ../../../..
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "canonical_research_destination_navigation" -q
```

Expected: all commands pass.

- [ ] **Step 8: Commit the contribution presentation**

```bash
git add app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts app/web/streamlit_components/institutional_portfolios_workbench/src/QuarterReviewPanel.tsx app/web/streamlit_components/institutional_portfolios_workbench/src/style.css tests/test_institutional_portfolios.py
git commit -m "개선: 분기 리뷰 수익 기여 표시 명확화"
```

---

### Task 3: Label Popularity Value and Consolidate the Korean Disclosure

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx:134-155,316-333,938-982,1758-1768`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css:880-940,1894-1912,1970-2030`
- Modify: `tests/test_institutional_portfolios.py`
- Regenerate: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/`

**Interfaces:**
- Consumes: `reported_value_label` and localized `source_caveats` from Task 1.
- Produces: labeled popularity metrics and one default-collapsed disclosure; no `.ip-caveats` chip list.

- [ ] **Step 1: Write failing UI source-contract assertions**

```python
self.assertIn("13F 보고 보유가액 합계", component_source)
self.assertIn("보유 기관", component_source)
self.assertIn('className="ip-source-disclosure"', component_source)
self.assertIn("payload.source_caveats.title", component_source)
self.assertIn("payload.source_caveats.summary", component_source)
self.assertNotIn('className="ip-caveats"', component_source)
self.assertNotIn("items.slice(0, 5)", component_source)
self.assertIn(".ip-source-disclosure", style_source)
self.assertNotIn(".ip-caveats span", style_source)
```

- [ ] **Step 2: Run the source test and verify failure**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "canonical_research_destination_navigation" -q
```

Expected: unlabeled `value_label` and chip styles still exist.

- [ ] **Step 3: Extend TypeScript payload types**

Add `reported_value_label: string` to `PopularityRow`. Change `source_caveats` to:

```ts
source_caveats: {
  visible: boolean;
  title: string;
  summary: string;
  items: string[];
};
```

- [ ] **Step 4: Render explicit popularity metrics**

Replace anonymous trailing values with:

```tsx
<span className="ip-popularity-metric"><small>보유 기관</small><em>{row.holder_count_label}개</em></span>
<span className="ip-popularity-metric"><small>13F 보고 보유가액 합계</small><em>{row.reported_value_label}</em></span>
```

Keep manual load and drilldown behavior unchanged.

- [ ] **Step 5: Replace caveat chips with one disclosure**

```tsx
{payload.source_caveats.visible ? (
  <details className="ip-source-disclosure">
    <summary><span>{payload.source_caveats.title}</span><small>{payload.source_caveats.summary}</small></summary>
    <ul>{payload.source_caveats.items.map((item) => <li key={item}>{item}</li>)}</ul>
  </details>
) : null}
```

Do not add `open`; it must be collapsed initially.

- [ ] **Step 6: Style the metrics and disclosure**

```css
.ip-popularity-metric { display: grid; gap: 2px; min-width: 140px; }
.ip-popularity-metric small { color: #7c8b9d; font-size: 10px; }
.ip-popularity-metric em { color: #315674; font-style: normal; font-weight: 800; }
.ip-source-disclosure { border: 1px solid #dce6ef; border-radius: 10px; background: #f8fafc; }
.ip-source-disclosure summary { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 14px; cursor: pointer; }
.ip-source-disclosure summary span { color: #334155; font-weight: 800; }
.ip-source-disclosure summary small { color: #64748b; }
.ip-source-disclosure ul { margin: 0; padding: 0 32px 14px; color: #64748b; font-size: 12px; }
```

At the mobile breakpoint, allow popularity buttons and disclosure summary to wrap without page overflow.

- [ ] **Step 7: Run tests, typecheck, and production build**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
cd app/web/streamlit_components/institutional_portfolios_workbench && npm test && npm run typecheck && npm run build
cd ../../../..
git diff --check
```

Expected: all commands exit 0 and `component_static/` is updated.

- [ ] **Step 8: Commit UI and bundle**

```bash
git add app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx app/web/streamlit_components/institutional_portfolios_workbench/src/style.css app/web/streamlit_components/institutional_portfolios_workbench/component_static tests/test_institutional_portfolios.py
git commit -m "개선: 기관 보유 랭킹과 13F 안내 한글화"
```

---

### Task 4: Verify the Actual Workflow and Close Out Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-metric-clarity-v1-20260817/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify if needed: `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`
- Generated, do not stage: `institutional-holdings-metric-clarity-v1-qa.png`

**Interfaces:**
- Consumes: verified services, React source, and production bundle.
- Produces: desktop/mobile QA evidence, `State: complete` task record, and durable flow semantics only if absent.

- [ ] **Step 1: Advance the active task record to final QA**

Confirm this roadmap remains in `PLAN.md`:

```markdown
1. 의미 계약 고정 — contribution sign, `%p`, reported-value and disclosure payload
2. 화면 표현 개선 — contribution metrics, popularity labels, Korean disclosure
3. 실제 화면 검증과 문서 정렬 — desktop/mobile QA, regressions, closeout
```

Set `STATUS.md` to `State: active` and `Current Step: 3/3 actual Browser QA and closeout`.
Keep the unchanged data boundaries and pre-2023 absolute-value comparison risk in `RISKS.md`.

- [ ] **Step 2: Run the proportional regression set**

```bash
.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q
cd app/web/streamlit_components/institutional_portfolios_workbench && npm test && npm run typecheck && npm run build
cd ../../../..
.venv/bin/python -m py_compile app/services/institutional_quarter_review.py app/services/institutional_portfolios.py app/web/institutional_portfolios.py
git diff --check
```

Expected: all commands exit 0. Record exact counts/output in `RUNS.md`.

- [ ] **Step 3: Perform Browser QA using the browser-control skill**

Verify:

1. A manager with an available `분기 리뷰` shows the formula guide and three metrics.
2. Stock return uses `%`; portfolio contribution uses `%p`.
3. Positive/negative lists do not borrow opposite-sign rows.
4. `기관 보유 랭킹` retains manual load and shows `보유 기관` plus `13F 보고 보유가액 합계 $...`.
5. Ranking copy says the amount is not market cap or volume.
6. `13F 자료 해석 시 주의` is collapsed initially and expands to exactly three Korean bullets.
7. Desktop and 390px layouts have no overflow or label collision.
8. Browser console error count is zero.
9. Save `institutional-holdings-metric-clarity-v1-qa.png` and do not stage it.

- [ ] **Step 4: Align documentation and close state**

Update the durable flow only if it lacks this meaning:

```text
분기 리뷰 contribution은 이전 보고 비중 × 종목 수익률의 포트폴리오 수익 기여(%p)이며,
기관 보유 랭킹은 보유 기관 수 기준이고 금액은 해당 분기 13F 보고 보유가액 합계다.
```

Set `STATUS.md` to `State: complete`, record roadmap `3/3`, QA evidence, and screenshot.
Record in `NOTES.md` that calculation, ranking priority, refresh, ingestion, DB schema, and trading
boundaries did not change. Move the task pointer in the active README to recent completed.

- [ ] **Step 5: Review and commit only closeout documents**

```bash
git status --short
git diff --check
git diff -- .aiworkspace/note/finance/tasks/active/institutional-holdings-metric-clarity-v1-20260817 .aiworkspace/note/finance/tasks/active/README.md .aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md
git add .aiworkspace/note/finance/tasks/active/institutional-holdings-metric-clarity-v1-20260817 .aiworkspace/note/finance/tasks/active/README.md
```

If the canonical flow changed, add it explicitly, then commit:

```bash
git add .aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md
git commit -m "완료: 기관 보유 지표 해석 UX 개선"
```

- [ ] **Step 6: Final completion check**

```bash
git status --short
git log -5 --oneline
```

Expected: only pre-existing unrelated changes and generated artifacts remain. Report roadmap `3/3`,
exact verification counts, screenshot, changed semantics, unchanged boundaries, and branch integration options.
