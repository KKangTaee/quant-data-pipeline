# Economic Cycle Asset Dedup Typography Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 금·달러 카드의 공통 경제 배경 중복을 제거하고 자산 고유 해석을 분리하며 `자산별 확인 포인트` 전체 글자를 기존보다 `1px` 크게 만든다.

**Architecture:** `finance/economic_cycle_asset_pathways.py`가 공통 `economic_state`와 금·달러 자산 고유 `summary/current_interpretation`을 분리한다. `finance/economic_cycle_interpretation.py`는 명시 summary를 보존하고 React는 새 필드를 우선하되 legacy narrative fallback을 유지한다. Typography는 Economic Cycle React의 자산별 section class 아래에만 제한한다.

**Tech Stack:** Python 3.12, pytest, TypeScript, React, CSS, Vite, Streamlit component

## Global Constraints

- 공통 `economic_state` 계산, 네 factor 방향, publication gate, 가격·경로 산식은 변경하지 않는다.
- 금·달러 summary/current interpretation에는 `현재 수준:`과 `전망 여건:`을 넣지 않는다.
- 가격 기간은 기존 5/21/63거래일을 유지하고 가격 원인·수익률·매매 신호를 만들지 않는다.
- `자산별 확인 포인트` section의 모든 표시 글자만 기존보다 정확히 `1px` 키운다.
- legacy payload의 `narrative` fallback과 기존 DB-only render 경계를 유지한다.
- generated component build는 갱신하되 Browser QA screenshot과 run history는 commit하지 않는다.
- 기존 unrelated registry, run history, QA artifact는 stage하거나 수정하지 않는다.

---

### Task 1: 금·달러 공통 배경과 자산 고유 해석 분리

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py:539-570, 1146-1235`
- Modify: `finance/economic_cycle_interpretation.py:492-530`
- Test: `tests/test_economic_cycle_asset_pathways.py:507-580`

**Interfaces:**
- Consumes: 기존 `economic_state: Mapping[str, object]`, `pathways: Sequence[Mapping[str, object]]`, `price_context: Mapping[str, object]`
- Produces: 금·달러 context의 `summary: str`, `current_interpretation: list[str]`, compatibility `narrative: str`
- Preserves: `economic_state`, `pathways`, `price_context`, `coverage`, `unmeasured_pathways`

- [ ] **Step 1: 금·달러 의미 분리 회귀 테스트를 작성한다**

`tests/test_economic_cycle_asset_pathways.py`의 기존 gold/dollar fixture를 재사용해 다음 테스트를 추가한다.

```python
def test_gold_and_dollar_keep_common_economic_state_out_of_asset_copy() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    contexts = pathways.build_asset_pathway_contexts(
        evidence=_economic_evidence(),
        market_rows=_macro_history(
            {
                "DFII10": "UP",
                "DGS2": "UP",
                "DGS10": "UP",
                "VIXCLS": "DOWN",
                "BAA10Y": "DOWN",
            }
        ),
        price_rows=_price_history({"GC=F": "DOWN", "DX-Y.NYB": "UP"}),
        reference_date="2026-07-17",
    )

    common_summary = contexts["gold"]["economic_state"]["summary"]
    for asset_group in ("gold", "dollar"):
        context = contexts[asset_group]
        assert common_summary not in context["summary"]
        assert common_summary not in context["narrative"]
        assert all(
            common_summary not in row
            for row in context["current_interpretation"]
        )
        assert "현재 수준:" not in context["summary"]
        assert "전망 여건:" not in context["summary"]
        assert context["current_interpretation"]
        assert context["summary"] != " ".join(context["current_interpretation"])
```

기존 `test_commodities_keep_wti_copper_and_gold_separate` 끝에 원자재 내부 금도 명시
필드를 재사용하는지 확인하는 assertion을 추가한다.

```python
assert assets["gold"]["summary"] == contexts["gold"]["summary"]
assert (
    assets["gold"]["current_interpretation"]
    == contexts["gold"]["current_interpretation"]
)
assert (
    contexts["gold"]["economic_state"]["summary"]
    not in assets["gold"]["narrative"]
)
```

- [ ] **Step 2: 새 테스트가 현재 중복 때문에 실패하는지 확인한다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_economic_cycle_asset_pathways.py \
  -k 'gold_and_dollar_keep_common or commodities_keep_wti'
```

Expected: FAIL. 현재 gold/dollar `summary`가 없거나 common economic summary를 포함하고 `current_interpretation`이 비어 있어야 한다.

- [ ] **Step 3: 자산 고유 summary와 interpretation helper를 구현한다**

`finance/economic_cycle_asset_pathways.py`에서 `_pathway_narrative()`가 common state를 직접
결합하지 않도록 다음 helper를 구현한다.

```python
def _price_direction_summary(
    asset_group: str,
    price_context: Mapping[str, object],
) -> str:
    price_label = {
        "RISING": "상승",
        "FALLING": "하락",
        "MIXED": "기간별 혼재",
        "NEUTRAL": "중립",
        "UNAVAILABLE": "확인 불가",
    }.get(str(price_context.get("status")), "확인 불가")
    subject = "달러지수" if asset_group == "dollar" else "금 가격"
    return f"실제 {subject}의 1개월·3개월 방향은 {price_label}입니다."


def _pathway_overall_label(
    pathways: Sequence[Mapping[str, object]],
) -> str:
    statuses = [
        str(row.get("status") or "UNAVAILABLE")
        for row in pathways
        if str(row.get("status") or "UNAVAILABLE") != "UNAVAILABLE"
    ]
    unavailable = any(
        str(row.get("status") or "UNAVAILABLE") == "UNAVAILABLE"
        for row in pathways
    )
    if not statuses:
        return "자료가 부족합니다"
    if set(statuses) == {"SUPPORTS_RISE"}:
        return (
            "상승 쪽으로 모이지만 일부 자료가 부족합니다"
            if unavailable
            else "상승 쪽으로 모입니다"
        )
    elif set(statuses) == {"SUPPORTS_FALL"}:
        return (
            "하락 쪽으로 모이지만 일부 자료가 부족합니다"
            if unavailable
            else "하락 쪽으로 모입니다"
        )
    return (
        "혼재하고 일부 자료가 부족합니다"
        if unavailable
        else "혼재합니다"
    )


def _pathway_summary(
    *,
    asset_group: str,
    pathways: Sequence[Mapping[str, object]],
    price_context: Mapping[str, object],
) -> str:
    asset_label = "달러" if asset_group == "dollar" else "금"
    pathway_state = _pathway_overall_label(pathways)
    price_state = _price_direction_summary(asset_group, price_context)
    return f"{asset_label}의 측정 경로는 {pathway_state}. {price_state}"


def _pathway_current_interpretation(
    *,
    asset_group: str,
    pathways: Sequence[Mapping[str, object]],
    price_context: Mapping[str, object],
) -> list[str]:
    rising = [
        str(row["label"])
        for row in pathways
        if row["status"] == "SUPPORTS_RISE"
    ]
    falling = [
        str(row["label"])
        for row in pathways
        if row["status"] == "SUPPORTS_FALL"
    ]
    mixed = [
        str(row["label"])
        for row in pathways
        if row["status"] in {"MIXED", "NEUTRAL"}
    ]
    unavailable = [
        str(row["label"])
        for row in pathways
        if row["status"] == "UNAVAILABLE"
    ]
    rows: list[str] = []
    if rising:
        rows.append(f"측정된 {', '.join(rising)}는 상승 요인으로 나타납니다.")
    if falling:
        rows.append(f"측정된 {', '.join(falling)}는 하락 요인으로 나타납니다.")
    if mixed:
        rows.append(f"{', '.join(mixed)}는 방향이 뚜렷하지 않습니다.")
    if unavailable:
        rows.append(f"{', '.join(unavailable)}는 자료가 부족합니다.")
    rows.append(_price_direction_summary(asset_group, price_context))
    if asset_group == "dollar":
        rows.append(
            "해외 상대금리가 아직 없어 달러의 국가 간 금리 차이는 판정하지 않습니다."
        )
    rows.append(
        "측정된 경로를 나눈 설명이며 가격 원인을 확정하지 않습니다."
    )
    return rows
```

summary는 경로 전체 상태와 실제 가격 상태를 한 문장으로 축약하고, interpretation은
구체 경로 label과 자료 한계를 별도 항목으로 보존한다.

context 조립은 다음 계약을 따른다.

```python
summary = _pathway_summary(
    asset_group=asset_group,
    pathways=pathways,
    price_context=price_context,
)
current_interpretation = _pathway_current_interpretation(
    asset_group=asset_group,
    pathways=pathways,
    price_context=price_context,
)
contexts[asset_group].update(
    {
        "summary": summary,
        "current_interpretation": current_interpretation,
        "narrative": " ".join(current_interpretation),
    }
)
```

`build_commodities_context()`의 gold child는 standalone gold context의
`summary/current_interpretation/narrative`를 그대로 복사한다. common `economic_state`
문장을 다시 합치지 않는다.

```python
gold_summary = str(gold_context.get("summary") or "")
gold_narrative = str(gold_context.get("narrative") or gold_summary)
gold_interpretation = [
    str(row)
    for row in gold_context.get("current_interpretation") or []
    if str(row).strip()
]
gold.update(
    {
        "summary": gold_summary or gold_narrative,
        "current_interpretation": (
            gold_interpretation
            if gold_interpretation
            else [gold_narrative]
            if gold_narrative
            else []
        ),
        "narrative": gold_narrative,
    }
)
```

`finance/economic_cycle_interpretation.py`의 read-model adapter는 context가 제공한
summary를 보존한다.

```python
summary = str(item.get("summary") or narrative)
item.update(
    {
        "summary": summary,
        "context": narrative,
        "is_directional_forecast": False,
    }
)
```

- [ ] **Step 4: 금·달러·원자재 focused 테스트를 통과시킨다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_economic_cycle_asset_pathways.py \
  -k 'gold or dollar or commodities'
```

Expected: all selected tests PASS.

- [ ] **Step 5: 실제 DB read model에서 공통 배경 중복이 payload에서 제거됐는지 확인한다**

Run:

```bash
.venv/bin/python - <<'PY'
from app.runtime_env import load_project_local_env
from app.services.overview.economic_cycle import build_economic_cycle_read_model

load_project_local_env()
model = build_economic_cycle_read_model(freshness_date="2026-07-25")
for item in model["market_implications"]:
    if item["asset_group"] not in {"gold", "dollar"}:
        continue
    common = item["economic_state"]["summary"]
    assert common not in item["summary"]
    assert common not in item["narrative"]
    assert all(common not in row for row in item["current_interpretation"])
    print(item["asset_group"], item["summary"])
PY
```

Expected: gold/dollar summary만 출력되고 assertion error가 없다. provider fetch나 DB write가 발생하지 않는다.

- [ ] **Step 6: Task 1을 커밋한다**

```bash
git add \
  finance/economic_cycle_asset_pathways.py \
  finance/economic_cycle_interpretation.py \
  tests/test_economic_cycle_asset_pathways.py
git commit -m "기능: 경제사이클 금·달러 해석 중복 제거"
```

---

### Task 2: React 표시 우선순위와 자산별 typography 적용

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:1015-1065, 1306-1312`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css:263-347`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/component_static/`
- Test: `tests/test_market_context_economic_cycle.py:470-505`

**Interfaces:**
- Consumes: Task 1의 `MarketImplication.summary`, `CommodityAsset.summary`, `current_interpretation`, `narrative`, `economic_state`
- Produces: existing `.market-implications` scoped UI, summary-first display, legacy narrative fallback
- Preserves: 기존 `EconomicStateBlock`, `AssetObservationBody`, responsive grid와 component event contract

- [ ] **Step 1: React 의미 우선순위와 typography source contract 테스트를 작성한다**

`tests/test_market_context_economic_cycle.py`에 다음 검증을 추가한다.

```python
def test_economic_cycle_asset_section_prefers_explicit_copy_and_scopes_larger_type() -> None:
    component = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/"
        "EconomicCycleWorkbench.tsx"
    ).read_text()
    style = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    assert 'className="market-implications"' in component
    assert "item.summary || item.narrative || item.context" in component
    assert "asset.summary || asset.narrative" in component
    assert (
        "item.current_interpretation?.length "
        "? item.current_interpretation "
        ": [item.narrative || item.summary || item.context]"
    ) in component
    for rule in (
        ".market-implications .section-heading > div > span { font-size: 11px; }",
        ".market-implications .section-heading h3 { font-size: 19px; }",
        ".market-implications .section-heading > small { font-size: 11px; }",
        ".market-implications .implication-summary { font-size: 12px; }",
        ".market-implications .economic-state-block p { font-size: 11px; }",
        ".market-implications .observation-block li { font-size: 10px; }",
        ".market-implications .series-primary-metrics > * { font-size: 9px; }",
        ".market-implications .price-return-grid strong { font-size: 11px; }",
    ):
        assert rule in style
```

- [ ] **Step 2: 새 source contract가 아직 class/override가 없어 실패하는지 확인한다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_market_context_economic_cycle.py \
  -k 'asset_section_prefers_explicit_copy'
```

Expected: FAIL with missing scoped font rule or explicit-copy priority.

- [ ] **Step 3: React가 명시 summary/current interpretation을 우선하게 한다**

`CommodityAsset` type에 `summary?: string;`을 추가한다.

`MarketImplicationCard`에서 다음 우선순위를 사용한다.

```tsx
const summary = item.summary || item.narrative || item.context;
const interpretation = item.current_interpretation?.length
  ? item.current_interpretation
  : [item.narrative || item.summary || item.context];
```

상단 문장은 `summary`를 표시한다.

```tsx
<p className="implication-summary">{summary}</p>
```

원자재 내부 금 카드도 explicit summary를 우선한다.

```tsx
<p>{asset.summary || asset.narrative}</p>
```

자산별 section의 기존 전용 scope class를 유지한다.

```tsx
<section className="market-implications">
```

legacy payload가 summary/current interpretation을 제공하지 않아도 기존 narrative fallback이
유지돼야 한다.

- [ ] **Step 4: 자산별 section의 모든 표시 글자에 `+1px` scoped override를 추가한다**

`style.css`의 asset block 뒤에 기존 `.market-implications` scope로 다음 값을 추가한다.

```css
.market-implications .section-heading > div > span { font-size: 11px; }
.market-implications .section-heading h3 { font-size: 19px; }
.market-implications .section-heading > small { font-size: 11px; }
.market-implications .implication-card > header span { font-size: 11px; }
.market-implications .implication-card > header strong { font-size: 15px; }
.market-implications .implication-overall > span { font-size: 9px !important; }
.market-implications .implication-summary { font-size: 12px; }
.market-implications .coverage-status { font-size: 10px; }
.market-implications .economic-state-block h5,
.market-implications .pathway-group h5,
.market-implications .price-pathway h5,
.market-implications .unmeasured-pathways h5,
.market-implications .unconnected-pathway-note h5,
.market-implications .observation-block > h5 { font-size: 11px; }
.market-implications .economic-state-block p { font-size: 11px; }
.market-implications .economic-observations span { font-size: 9px; }
.market-implications .movement-unit-note { font-size: 9px; }
.market-implications .observation-block li { font-size: 10px; }
.market-implications .movement-item > header { font-size: 10px; }
.market-implications .observed-pathways-block .pathway-item > p { font-size: 10px; }
.market-implications .commodity-asset-card > header strong { font-size: 13px; }
.market-implications .commodity-asset-card > p { font-size: 10px; }
.market-implications .pathway-item > header strong { font-size: 12px; }
.market-implications .pathway-item > header span { font-size: 9px; }
.market-implications .pathway-empty { font-size: 10px; }
.market-implications .series-primary-metrics > * { font-size: 9px; }
.market-implications .pathway-hover-details { font-size: 9px; }
.market-implications .pathway-details { font-size: 9px; }
.market-implications .price-status { font-size: 9px; }
.market-implications .price-return-grid span { font-size: 9px; }
.market-implications .price-return-grid strong { font-size: 11px; }
.market-implications .implication-basis { font-size: 9px; }
.market-implications .unmeasured-pathways span { font-size: 9px; }
.market-implications .unconnected-pathway-note p { font-size: 11px; }
```

기존 base rule, padding, gap, grid, line-height는 변경하지 않는다. mobile의
`.pathway-details`도 위 scoped override가 cascade에서 적용되는지 production build와
Browser QA로 확인한다.

- [ ] **Step 5: React source contract와 기존 Economic Cycle UI regression을 통과시킨다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_market_context_economic_cycle.py
```

Expected: all tests PASS.

- [ ] **Step 6: production component bundle을 재생성한다**

Run:

```bash
cd app/web/streamlit_components/economic_cycle_workbench
npm run build
```

Expected: Vite exits 0 and `component_static/index.html` references the newly generated hashed JS/CSS assets.

- [ ] **Step 7: Task 2를 커밋한다**

```bash
git add \
  app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/style.css \
  app/web/streamlit_components/economic_cycle_workbench/component_static \
  tests/test_market_context_economic_cycle.py
git commit -m "디자인: 경제사이클 자산 카드 가독성 개선"
```

---

### Task 3: Actual Browser QA와 finance closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-asset-dedup-typography-v1-20260725/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-asset-dedup-typography-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-asset-dedup-typography-v1-20260725/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-asset-dedup-typography-v1-20260725/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-asset-dedup-typography-v1-20260725/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, do not commit: `economic-cycle-asset-dedup-typography-v1-qa.png`

**Interfaces:**
- Consumes: Task 1 payload contract와 Task 2 production bundle
- Produces: actual desktop/420px evidence, task `2/2차` closeout, durable ownership/status alignment
- Preserves: registry JSONL, run history, existing QA artifacts

- [ ] **Step 1: focused Python·React·compile·diff 검증을 새로 실행한다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_economic_cycle_asset_pathways.py \
  tests/test_market_context_economic_cycle.py \
  tests/test_economic_cycle_service.py
.venv/bin/python -m py_compile \
  finance/economic_cycle_asset_pathways.py \
  finance/economic_cycle_interpretation.py \
  app/services/overview/economic_cycle.py
git diff --check
```

Expected: focused tests and compile exit 0; `git diff --check` has no output.

- [ ] **Step 2: isolated Streamlit app을 실행하고 desktop actual 화면을 확인한다**

Run:

```bash
uv run streamlit run app/web/streamlit_app.py \
  --server.port 8518 \
  --server.headless true
```

Browser QA:

- `/overview`의 `시장 환경 > 경제 사이클`로 이동한다.
- 금·달러 각각 `현재 수준:`과 `전망 여건:` 문장이 `사이클 판단의 공통 경제 배경`
  블록에서 한 번만 보이는지 확인한다.
- 상단 요약은 자산 고유 경로·가격만, `현재 해석`은 상세 항목과 자료 한계만 표시하는지
  확인한다.
- `자산별 확인 포인트` section의 computed font sizes가 이전 값보다 `1px` 큰지 대표
  heading/body/badge/metric selector로 확인한다.
- desktop에서 카드 높이, 줄바꿈, tooltip, 가로 overflow와 console warning/error를
  확인한다.

- [ ] **Step 3: 420px responsive QA와 screenshot을 남긴다**

Viewport를 `420x900`으로 바꾸고 다음을 확인한다.

- section/card `scrollWidth <= clientWidth`
- 금·달러 summary와 common background가 잘리지 않는다.
- 가격 3열과 series metric이 카드 폭 안에 유지된다.
- mobile `세부 데이터` disclosure 글자가 `+1px` 적용되고 펼침 내용이 겹치지 않는다.
- console warning/error가 0이다.

desktop 또는 중복 제거가 가장 잘 보이는 viewport에서
`economic-cycle-asset-dedup-typography-v1-qa.png`를 생성하되 commit하지 않는다.

- [ ] **Step 4: active task와 durable finance 문서를 실제 결과로 동기화한다**

`finance-doc-sync`와 `finance-runbook-maintainer` routing을 적용한다.

- `PLAN.md`, `STATUS.md`: `2/2차`, tests/build/Browser QA actual 결과
- `NOTES.md`: common state와 asset-specific copy 역할
- `RUNS.md`: 명령, pass count, build, viewport/overflow/console 결과
- `RISKS.md`: 남은 범위와 resolved risk
- `PROJECT_MAP.md`: gold/dollar summary/current interpretation ownership
- `INDEX.md`, `ROADMAP.md`: latest completed Economic Cycle UX task
- root logs: 작업 단위당 3~5줄 handoff
- 운영 절차가 변하지 않았으면 runbook 본문은 수정하지 않는다.

- [ ] **Step 5: stage 대상을 제한하고 closeout 문서를 커밋한다**

```bash
git add \
  .aiworkspace/note/finance/tasks/active/market-research-economic-cycle-asset-dedup-typography-v1-20260725 \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "문서: 경제사이클 자산 카드 정리 기록"
```

Expected: registry, run history, `.superpowers/`, existing/new QA images가 staged paths에 없다.

- [ ] **Step 6: 최종 상태를 확인한다**

Run:

```bash
git status --short
git log --oneline -5
```

Expected: 이 task 소유 파일은 commit됐고 기존 unrelated dirty/generated files만 남는다.
