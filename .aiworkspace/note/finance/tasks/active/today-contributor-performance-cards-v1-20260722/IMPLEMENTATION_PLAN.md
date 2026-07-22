# Today Contributor Performance Cards V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Today 대표 포트폴리오의 기여 상위 2개·하위 2개 종목을 현금흐름 조정 누적 수익률과 포트폴리오 누적 기여금이 분리된 compact card로 표시한다.

**Architecture:** Portfolio Monitoring read model이 exact `as_of_date`의 `flow_adjusted_index - 1`만 additive `total_return`으로 제공한다. Group item row는 공통 `basis_date`, selected-position은 자체 `latest_usable_date`를 전달하고 null/missing exact row는 `None`으로 남긴다. Today service가 이를 contribution과 결합해 JSON-safe contributor row로 투영하며 React primary UI와 Python read-only fallback은 같은 정보 계층, signed contribution과 responsive 규칙을 사용한다. 기존 Portfolio Monitoring 화면, DB, ingestion, 그룹 곡선 계산은 변경하지 않는다.

**Tech Stack:** Python 3, pandas, `Decimal`, Streamlit, React 18, TypeScript, CSS, unittest/pytest, Vitest, Vite

## Global Constraints

- contributor selection은 양수 기여 상위 2개와 음수 기여 하위 2개, 최대 4개를 유지한다.
- 섹션 제목은 `종목별 성과 기여`, 보조 문구는 `기여 상위 2 · 하위 2`로 한다.
- 종목 수익률은 정확한 consumer 기준일의 `flow_adjusted_index - 1`이며 이전·이후 값 또는 `(current_value / initial_capital) - 1`로 fallback하지 않는다.
- contributor row는 `symbol`, `contribution_value`, `total_return`, `tone`을 제공하고 기존 `value`는 한 차례 호환 alias로 유지한다.
- sorting과 `tone`은 `contribution_value` 기준이며 수익률 색상은 `total_return` 부호로 독립 계산한다.
- 수익률이 없으면 `수익률 자료 부족`을 표시하되 기여금은 계속 표시한다.
- contribution은 양수 `+$…`, 음수 `-$…`로 표시하고 일반 포트폴리오 평가액 formatter는 유지한다.
- footer copy는 `종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 YYYY-MM-DD`로 한다.
- card surface는 neutral이며 좌측 상태선과 강한 상태 배경을 사용하지 않는다.
- desktop/760px에서는 contributor 내부 2열, 460px 이하에서는 1열로 표시한다.
- `우선 확인`과 contributor section의 outer 1:1 grid는 유지하고 760px 이하에서 세로로 쌓는다.
- React primary와 Python read-only fallback을 함께 개선한다.
- Portfolio Monitoring 사용자 화면, DB schema, ingestion, provider fetch, position event 계산, 그룹 curve 계산은 변경하지 않는다.
- Browser QA는 1280px, 760px, 420px에서 수행하고 horizontal overflow와 console error를 확인한다.

---

## File Map

- `app/services/portfolio_monitoring/read_model.py`: exact as-of item lane의 현금흐름 조정 누적 수익률을 계산해 `GroupValueResult.item_rows`와 selected-position에 제공한다.
- `tests/test_portfolio_monitoring_read_model.py`: group basis-date future/trailing-null과 selected-position exact-latest 계약을 고정한다.
- `app/services/today.py`: item return과 contribution을 결합하고 상위·하위 selection을 수행한다.
- `tests/test_today_home.py`: Today contributor JSON contract와 Python fallback markup을 검증한다.
- `app/web/streamlit_components/today_workbench/src/types.ts`: React contributor row의 명시적 TypeScript 계약을 정의한다.
- `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`: contributor card 구조, label, 독립 tone, missing return state를 렌더링한다.
- `app/web/streamlit_components/today_workbench/src/presentation.ts`: contribution 전용 `+$…` / `-$…` formatter를 소유한다.
- `app/web/streamlit_components/today_workbench/src/presentation.test.ts`: signed contribution formatter를 단위 검증한다.
- `app/web/streamlit_components/today_workbench/src/style.css`: neutral card grid와 760/460px responsive rules를 정의한다.
- `app/web/today_page.py`: React unavailable 시 같은 두 단위를 보여주는 escaped read-only fallback을 렌더링한다.
- `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/*.md`: 실행 결과, 검증, 위험과 완료 상태를 기록한다.
- `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`: task 경로와 최종 handoff만 3~5줄로 남긴다.

---

### Task 1: Portfolio Monitoring Item Return Contract

**Files:**
- Modify: `app/services/portfolio_monitoring/read_model.py`
- Test: `tests/test_portfolio_monitoring_read_model.py`

**Interfaces:**
- Consumes: `ItemValueLane.curve: pandas.DataFrame`, `_normalized_lane_curve(lane)`, `flow_adjusted_index`
- Produces: `_lane_total_return(lane: ItemValueLane | None, as_of_date: date) -> Decimal | None`; item row field `total_return: Decimal | None`

- [ ] **Step 1: Write failing tests for exact basis-date and selected-position latest returns**

Add these tests to `PortfolioMonitoringReadModelTests`:

```python
def test_item_rows_require_valid_flow_adjusted_index_on_group_basis_date(self) -> None:
    read_model = _load_read_model()
    item = _item(
        "item-amd",
        requested=date(2026, 7, 1),
        effective=date(2026, 7, 1),
        capital="1000",
        funding_mode="fixed_shares",
        input_shares=10,
    )
    lane = _position_lane(item)
    lane.curve.loc[lane.curve.index[-1], "flow_adjusted_index"] = None

    result = read_model.align_group_value_lanes(
        [item], {item.monitoring_item_id: lane}
    )

    self.assertIsNone(result.item_rows[0]["total_return"])

def test_item_rows_do_not_fabricate_total_return_without_flow_adjusted_index(self) -> None:
    read_model = _load_read_model()
    item = _item(
        "item-amd",
        requested=date(2026, 7, 1),
        effective=date(2026, 7, 1),
        capital="1000",
    )
    lane = _lane(
        item,
        [("2026-07-01", 1000), ("2026-07-02", 1200)],
    )

    result = read_model.align_group_value_lanes(
        [item], {item.monitoring_item_id: lane}
    )

    self.assertIsNone(result.item_rows[0]["total_return"])
```

The first test intentionally blanks the exact group basis-date index and expects `None`. Add `test_item_rows_do_not_use_observation_after_group_basis_date` to prove a future lane observation is excluded, a valid-latest selected-position assertion expecting `Decimal("-0.00154")`, and `test_selected_position_requires_valid_index_on_its_latest_usable_date` expecting `None` for a trailing-null latest row.

- [ ] **Step 2: Run the focused exact-date tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_item_rows_require_valid_flow_adjusted_index_on_group_basis_date \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_item_rows_do_not_use_observation_after_group_basis_date \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_selected_position_requires_valid_index_on_its_latest_usable_date \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_item_rows_do_not_fabricate_total_return_without_flow_adjusted_index \
  -q
```

Expected for the final-review correction: exact-null/future/trailing-null assertions fail because the prior helper reuses an older or newer non-null value.

- [ ] **Step 3: Add the minimal lane return helper**

Add next to `_normalized_lane_curve` in `app/services/portfolio_monitoring/read_model.py`:

```python
def _lane_total_return(
    lane: ItemValueLane | None,
    as_of_date: date,
) -> Decimal | None:
    """Return the cash-flow-adjusted item return observed on one exact date."""

    if lane is None:
        return None
    frame = _normalized_lane_curve(lane)
    if frame.empty or "flow_adjusted_index" not in frame:
        return None
    exact = frame.loc[frame["date"] == pd.Timestamp(as_of_date)]
    if exact.empty:
        return None
    value = exact.iloc[-1]["flow_adjusted_index"]
    if pd.isna(value):
        return None
    return _money(value) - Decimal("1")
```

Add the field inside the item row comprehension:

```python
"total_return": _lane_total_return(
    valid_lanes.get(item.monitoring_item_id),
    basis_date,
),
```

Replace `_project_selected_position`'s duplicated last-row return block with:

```python
total_return = _lane_total_return(lane, lane.latest_usable_date)
```

This preserves the selected-position latest-date contract while making both consumers use one exact-date helper with different owning dates.

- [ ] **Step 4: Run focused and read-model regressions**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_read_model.py -q
```

Expected: all tests pass, including the two new item-row tests.

- [ ] **Step 5: Commit the additive contract**

```bash
git add app/services/portfolio_monitoring/read_model.py tests/test_portfolio_monitoring_read_model.py
git commit -m "기능: 종목별 현금흐름 조정 수익률 제공"
```

---

### Task 2: Today Contributor Projection Contract

**Files:**
- Modify: `app/services/today.py`
- Test: `tests/test_today_home.py`

**Interfaces:**
- Consumes: Portfolio Monitoring item rows with `monitoring_item_id`, `source_ref`, `total_return`; metrics `contribution_by_item`
- Produces: contributor row `{symbol: str, contribution_value: float, value: float, total_return: float | None, tone: "positive" | "negative"}`

- [ ] **Step 1: Extend the complete fixture with item returns**

Change the fixture rows in `tests/test_today_home.py`:

```python
"item_rows": [
    {
        "monitoring_item_id": "nvda",
        "source_ref": "NVDA",
        "total_return": Decimal("0.42"),
    },
    {
        "monitoring_item_id": "tlt",
        "source_ref": "TLT",
        "total_return": Decimal("-0.08"),
    },
],
```

- [ ] **Step 2: Write failing contributor contract tests**

Extend `test_complete_inputs_build_market_and_representative_portfolio`:

```python
self.assertEqual(
    model["portfolio"]["contributors"][0],
    {
        "symbol": "NVDA",
        "contribution_value": 240.0,
        "value": 240.0,
        "total_return": 0.42,
        "tone": "positive",
    },
)
self.assertEqual(
    model["portfolio"]["contributors"][-1],
    {
        "symbol": "TLT",
        "contribution_value": -40.0,
        "value": -40.0,
        "total_return": -0.08,
        "tone": "negative",
    },
)
```

Add a missing-return test:

```python
def test_contributor_keeps_contribution_when_item_return_is_missing(self) -> None:
    inputs = self._complete_inputs()
    inputs["portfolio"]["active_group"]["item_rows"][0]["total_return"] = None

    model = self._builder()(**inputs)

    contributor = model["portfolio"]["contributors"][0]
    self.assertEqual(contributor["symbol"], "NVDA")
    self.assertEqual(contributor["contribution_value"], 240.0)
    self.assertIsNone(contributor["total_return"])
```

- [ ] **Step 3: Run Today projection tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_today_home.py::TodayHomeReadModelTests::test_complete_inputs_build_market_and_representative_portfolio \
  tests/test_today_home.py::TodayHomeReadModelTests::test_contributor_keeps_contribution_when_item_return_is_missing \
  -q
```

Expected: failure because contributor rows still expose only `{symbol, value, tone}`.

- [ ] **Step 4: Join item returns into the contributor projection**

Replace the `symbols` mapping with an item metadata mapping in `app/services/today.py`:

```python
items_by_id = {
    str(row.get("monitoring_item_id") or ""): {
        "symbol": _text(row.get("source_ref")),
        "total_return": _safe_float(row.get("total_return")),
    }
    for row in item_rows
}
```

Build contribution rows with explicit semantics:

```python
contribution_rows = []
for item_id, raw_value in raw_contributions.items():
    contribution_value = _safe_float(raw_value)
    if contribution_value in (None, 0.0):
        continue
    item = items_by_id.get(str(item_id), {})
    contribution_rows.append(
        {
            "symbol": _text(item.get("symbol"), str(item_id)),
            "contribution_value": contribution_value,
            "value": contribution_value,
            "total_return": _safe_float(item.get("total_return")),
            "tone": "positive" if contribution_value > 0 else "negative",
        }
    )
```

Change positive/negative filtering and sorting to the explicit field:

```python
positives = sorted(
    (row for row in contribution_rows if row["contribution_value"] > 0),
    key=lambda row: row["contribution_value"],
    reverse=True,
)[:2]
negatives = sorted(
    (row for row in contribution_rows if row["contribution_value"] < 0),
    key=lambda row: row["contribution_value"],
)[:2]
```

- [ ] **Step 5: Run the full Today service regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
```

Expected: all Today read-model and renderer tests pass before the UI contract is changed in Task 3.

- [ ] **Step 6: Commit the Today contract**

```bash
git add app/services/today.py tests/test_today_home.py
git commit -m "기능: Today 종목 성과 기여 계약 확장"
```

---

### Task 3: React Primary And Python Fallback Contributor Cards

**Files:**
- Modify: `app/web/streamlit_components/today_workbench/src/types.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/style.css`
- Modify: `app/web/today_page.py`
- Test: `tests/test_today_home.py`
- Generated by build: `app/web/streamlit_components/today_workbench/component_static/**`

**Interfaces:**
- Consumes: Task 2 contributor row and `portfolio.basis_date`
- Produces: two-column neutral contributor card grid, independent return/contribution tones, `+$…` / `-$…`, missing-return copy, responsive fallback parity

- [ ] **Step 1: Update the fallback fixture to the explicit contract**

Change the fallback test contributor in `tests/test_today_home.py`:

```python
"contributors": [
    {
        "symbol": "NVDA",
        "contribution_value": 240.0,
        "value": 240.0,
        "total_return": 0.42,
        "tone": "positive",
    }
],
```

- [ ] **Step 2: Write failing renderer/source contract assertions**

Replace the old `누적 기여` assertion in `test_today_html_preserves_b_layout_order_and_escapes_market_copy` with:

```python
self.assertIn("종목별 성과 기여", html)
self.assertIn("기여 상위 2 · 하위 2", html)
self.assertIn("종목 누적 수익률", html)
self.assertIn("+42.00%", html)
self.assertIn("포트폴리오 누적 기여", html)
self.assertIn("+$240", html)
self.assertIn("입출금 영향을 조정한 누적 성과", html)
```

Add a missing-return fallback test:

```python
def test_today_fallback_labels_missing_item_return_without_hiding_contribution(self) -> None:
    module = importlib.import_module("app.web.today_page")
    model = {
        "header": {},
        "market": {"evidence": [], "watch_items": []},
        "portfolio": {
            "status": "READY",
            "basis_date": "2026-07-21",
            "metrics": {},
            "curve": [],
            "contributors": [
                {
                    "symbol": "AMD",
                    "contribution_value": 11915.0,
                    "value": 11915.0,
                    "total_return": None,
                    "tone": "positive",
                },
                {
                    "symbol": "TEM",
                    "contribution_value": -401.0,
                    "value": -401.0,
                    "total_return": None,
                    "tone": "negative",
                },
            ],
            "review_items": [],
        },
    }

    html = module.build_today_html(model)

    self.assertIn("수익률 자료 부족", html)
    self.assertIn("+$11,915", html)
    self.assertIn("-$401", html)
```

Extend the source contract test with:

```python
react_source = Path(
    "app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx"
).read_text(encoding="utf-8")
css_source = Path(
    "app/web/streamlit_components/today_workbench/src/style.css"
).read_text(encoding="utf-8")
types_source = Path(
    "app/web/streamlit_components/today_workbench/src/types.ts"
).read_text(encoding="utf-8")

self.assertIn("종목별 성과 기여", react_source)
self.assertIn("기여 상위 2 · 하위 2", react_source)
self.assertIn("수익률 자료 부족", react_source)
self.assertIn("signedMoneyText(row.contribution_value)", react_source)
self.assertIn("contribution_value", types_source)
self.assertIn("total_return", types_source)
self.assertIn(".today-contributor-grid", css_source)
self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", css_source)
```

- [ ] **Step 3: Run renderer tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_today_home.py::TodayHomePageContractTests::test_today_html_preserves_b_layout_order_and_escapes_market_copy \
  tests/test_today_home.py::TodayHomePageContractTests::test_today_fallback_labels_missing_item_return_without_hiding_contribution \
  tests/test_today_home.py::TodayHomePageContractTests::test_today_page_reuses_overview_visual_tokens_and_read_only_loaders \
  -q
```

Expected: new card-copy and source assertions fail against the existing chip UI.

- [ ] **Step 4: Make the TypeScript contributor contract explicit**

Replace the contributor type in `src/types.ts`:

```typescript
contributors: Array<{
  symbol: string;
  contribution_value: number;
  value?: number;
  total_return: number | null;
  tone: "positive" | "negative";
}>;
```

Add the formatter unit assertion in `src/presentation.test.ts`, then export the implementation from `src/presentation.ts`:

```typescript
expect(signedMoneyText?.(11915)).toBe("+$11,915");
expect(signedMoneyText?.(-401)).toBe("-$401");

export function signedMoneyText(value: number | null): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const magnitude = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Math.abs(value));
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}${magnitude}`;
}
```

- [ ] **Step 5: Render React contributor cards with independent tones**

In `TodayWorkbench.tsx`, import `signedMoneyText`, derive the return tone inside the map and replace the chip section with:

```tsx
<section className="today-contributor-section">
  <header className="today-detail-heading">
    <span>종목별 성과 기여</span>
    <small>기여 상위 2 · 하위 2</small>
  </header>
  <div className="today-contributor-grid">
    {payload.portfolio.contributors.length
      ? payload.portfolio.contributors.map((row) => {
        const returnTone = row.total_return == null
          ? "is-unavailable"
          : row.total_return < 0 ? "is-negative" : "is-positive";
        const contributionTone = row.tone === "negative"
          ? "is-negative"
          : "is-positive";
        return (
          <article
            className="today-contributor-card"
            key={`${row.symbol}-${row.contribution_value}`}
          >
            <strong className="today-contributor-symbol">{row.symbol}</strong>
            <span className="today-contributor-return-label">종목 누적 수익률</span>
            <b className={`today-contributor-return ${returnTone}`}>
              {row.total_return == null
                ? "수익률 자료 부족"
                : percentText(row.total_return)}
            </b>
            <footer>
              <span>포트폴리오 누적 기여</span>
              <strong className={contributionTone}>
                {signedMoneyText(row.contribution_value)}
              </strong>
            </footer>
          </article>
        );
      })
      : <small>기여 계산 자료가 없습니다.</small>}
  </div>
  <small className="today-contributor-note">
    종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 {payload.portfolio.basis_date ?? "-"}
  </small>
</section>
```

Leave the adjacent `우선 확인` section intact.

- [ ] **Step 6: Add neutral card and responsive CSS**

Replace `.today-contributors` chip rules with:

```css
.today-detail-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.today-detail-heading > span {
  color: #708293;
  font-size: 11px;
  font-weight: 850;
}
.today-detail-heading small,
.today-contributor-note {
  color: #82909b;
  font-size: 10px;
}
.today-contributor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.today-contributor-card {
  display: grid;
  min-width: 0;
  gap: 4px;
  padding: 11px 12px;
  border: 1px solid #e1e8ed;
  border-radius: 11px;
  background: #fff;
}
.today-contributor-symbol {
  color: #29445a;
  font-size: 11px;
}
.today-contributor-return-label {
  color: #82909b;
  font-size: 10px;
}
.today-contributor-return {
  color: #29445a;
  font-size: 15px;
}
.today-contributor-return.is-unavailable {
  color: #7b8995;
  font-size: 11px;
}
.today-contributor-card footer {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  margin-top: 5px;
  padding-top: 7px;
  border-top: 1px solid #edf1f4;
}
.today-contributor-card footer span {
  color: #718493;
  font-size: 10px;
}
.today-contributor-card footer strong {
  font-size: 11px;
  white-space: nowrap;
}
.today-contributor-note {
  line-height: 1.45;
}
```

Add under the existing 460px media query:

```css
.today-contributor-grid { grid-template-columns: 1fr; }
```

Do not collapse the inner contributor grid at 760px; only the outer `.today-portfolio-detail-grid` stacks there.

- [ ] **Step 7: Build escaped Python fallback cards**

In `app/web/today_page.py`, replace the contributor chip builder with card markup using `contribution_value` first and the temporary `value` alias only as a fallback:

```python
def _signed_money(value: Any) -> str:
    try:
        numeric = float(value)
        sign = "+" if numeric > 0 else "-" if numeric < 0 else ""
        return f"{sign}${abs(numeric):,.0f}"
    except (TypeError, ValueError):
        return "—"

contributor_cards: list[str] = []
for row in contributors:
    contribution = row.get("contribution_value", row.get("value"))
    total_return = row.get("total_return")
    return_html = (
        f'<strong class="today-contributor-return {_value_tone(total_return)}">'
        f'{escape(_percent(total_return))}</strong>'
        if total_return is not None
        else '<strong class="today-contributor-return is-unavailable">수익률 자료 부족</strong>'
    )
    contributor_cards.append(
        '<article class="today-contributor-card">'
        f'<div class="today-contributor-symbol">{escape(str(row.get("symbol") or "-"))}</div>'
        '<div class="today-contributor-return-label">종목 누적 수익률</div>'
        f'{return_html}'
        '<div class="today-contributor-footer">'
        '<span>포트폴리오 누적 기여</span>'
        f'<strong class="{_value_tone(contribution)}">{escape(_signed_money(contribution))}</strong>'
        '</div>'
        '</article>'
    )
contributor_html = (
    "".join(contributor_cards)
    or '<div class="today-event-detail">기여 계산 자료가 없습니다.</div>'
)
```

Render it in a dedicated detail section:

```html
<div class="today-detail-heading">
  <span class="today-panel-meta">종목별 성과 기여</span>
  <span class="today-panel-meta">기여 상위 2 · 하위 2</span>
</div>
<div class="today-contributor-grid">{contributor_html}</div>
<div class="today-contributor-note">
  종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 {escape(str(portfolio.get('basis_date') or '-'))}
</div>
```

Mirror the React neutral card CSS in `_today_css()` and add the same 460px one-column rule. Reuse existing overview tokens (`--ov-mi-*`) for border, text, muted text, and surface colors.

- [ ] **Step 8: Run Python tests and frontend checks**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
npm test -- --run
npm run typecheck
npm run build
```

Run the npm commands from:

```text
app/web/streamlit_components/today_workbench
```

Expected: Python tests pass, Vitest passes, TypeScript reports no errors, Vite writes an updated `build/` bundle.

- [ ] **Step 9: Commit primary and fallback UI together**

```bash
git add \
  app/web/today_page.py \
  app/web/streamlit_components/today_workbench/src/types.ts \
  app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx \
  app/web/streamlit_components/today_workbench/src/style.css \
  app/web/streamlit_components/today_workbench/build \
  tests/test_today_home.py
git commit -m "기능: Today 종목별 성과 기여 카드 구현"
```

---

### Task 4: Regression, Browser QA, And Durable Handoff

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/DESIGN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722/RISKS.md`
- Modify if durable contract changed: `.aiworkspace/note/finance/docs/flows/TODAY_HOME.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated QA screenshot outside the commit: `today-contributor-performance-cards-v1-browser-qa.png`

**Interfaces:**
- Consumes: completed Python and React implementation from Tasks 1–3
- Produces: verified 4/4 roadmap status, actual viewport evidence, clean durable handoff

- [ ] **Step 1: Run the scoped Python regression suite**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_today_home.py \
  tests/test_portfolio_monitoring_read_model.py \
  tests/test_portfolio_monitoring_page.py \
  -q
```

Expected: all scoped tests pass with no failure or error.

- [ ] **Step 2: Run syntax, diff, and frontend verification**

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/portfolio_monitoring/read_model.py \
  app/services/today.py \
  app/web/today_page.py
git diff --check
npm test -- --run
npm run typecheck
npm run build
```

Run the npm commands from `app/web/streamlit_components/today_workbench`.

Expected: commands exit 0 and `git diff --check` prints no whitespace errors.

- [ ] **Step 3: Start the local app and perform actual Browser QA**

Start the project with the repository's existing Streamlit runbook command. Open `/` and check these exact states at 1280px, 760px, and 420px:

```text
- title: 종목별 성과 기여
- scope note: 기여 상위 2 · 하위 2
- each available card: symbol / 종목 누적 수익률 / return / 포트폴리오 누적 기여 / signed dollar
- footer: 종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 <portfolio basis date>
- 1280 and 760: contributor cards remain two columns
- 760: contributor section and 우선 확인 stack vertically
- 420: contributor cards become one column
- no horizontal scroll
- no clipped symbol, return, or contribution amount
- no browser console error
```

Save one representative screenshot as `today-contributor-performance-cards-v1-browser-qa.png`. Keep it untracked because QA screenshots are generated artifacts unless the user explicitly asks to commit them.

- [ ] **Step 4: Inspect the final diff for scope and data correctness**

Run:

```bash
git status --short
git diff --stat
git diff -- \
  app/services/portfolio_monitoring/read_model.py \
  app/services/today.py \
  app/web/today_page.py \
  app/web/streamlit_components/today_workbench/src/types.ts \
  app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx \
  app/web/streamlit_components/today_workbench/src/style.css \
  tests/test_portfolio_monitoring_read_model.py \
  tests/test_today_home.py
```

Confirm that no DB, ingestion, provider, registry, saved portfolio, run-history, or Portfolio Monitoring page UI file is included. Confirm unrelated dirty artifacts remain unstaged.

- [ ] **Step 5: Synchronize task and durable documentation**

Update the active task documents with concrete results:

```text
PLAN.md: Status Complete, Roadmap 4/4 complete
DESIGN.md: Status Implemented and Verified
STATUS.md: completed tasks, exact test commands, viewport QA result, screenshot path
NOTES.md: final field contract and why flow_adjusted_index is required
RUNS.md: RED/GREEN commands, frontend build, Browser QA viewports
RISKS.md: resolved risks and any genuine remaining gap only
```

If `.aiworkspace/note/finance/docs/flows/TODAY_HOME.md` exists, update only the durable contributor field/copy contract. Add 3–5 line task pointers to the two root handoff logs rather than copying implementation detail.

- [ ] **Step 6: Commit documentation alignment**

```bash
git add \
  .aiworkspace/note/finance/tasks/active/today-contributor-performance-cards-v1-20260722 \
  .aiworkspace/note/finance/docs/flows/TODAY_HOME.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Today 성과 기여 카드 검증 결과 정리"
```

If `docs/flows/TODAY_HOME.md` does not exist, omit it from `git add`; do not create an unrelated new durable document solely to satisfy this command.

- [ ] **Step 7: Verify the committed state**

Run:

```bash
git status --short
git log -4 --oneline
```

Expected: only previously identified unrelated generated/user files remain dirty, and the implementation appears as coherent task commits after the design commit.

---

## Self-Review Result

- Spec coverage: selection, explicit units, flow-adjusted return, missing-return state, independent tones, footer, React/fallback parity, responsive behavior, browser QA, and out-of-scope boundaries each map to a concrete task.
- Placeholder scan: no `TBD`, deferred implementation, unspecified error handling, or unspecified test step remains.
- Type consistency: Task 1 produces `Decimal | None`; Task 2 converts it to `float | None`; Task 3 consumes `number | null`. `contribution_value` is the sort/render source and `value` remains only a Python compatibility alias.
- Scope consistency: shared read-model change is additive; Portfolio Monitoring UI, DB, ingestion, provider calls, registries, saved portfolios, and run history are excluded.
