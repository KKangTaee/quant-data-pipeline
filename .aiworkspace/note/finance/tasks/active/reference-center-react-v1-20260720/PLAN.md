# Reference Center React V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan.

**Goal:** `Guides`와 `Glossary`를 검색 중심 단일 React `Reference Center`로 통합하고, 현재 제품 surface와 stable item ID만 안내하는 읽기 전용 도움말 흐름을 제공한다.

**Architecture:** Streamlit-free Python catalog가 `reference_center_v1` payload와 drift report를 만들고, React component가 검색·필터·상세 상태를 로컬에서 처리한다. Python page shell은 initial deep link와 `navigate_to_surface` intent만 검증하고 기존 Streamlit page target 또는 Backtest panel route로 이동한다.

**Tech Stack:** Python 3.12, Streamlit multipage navigation, React 18, TypeScript 5.7, Vite 6, Vitest 4, Python `unittest`.

## Global Constraints

- Reference는 읽기 전용이다. DB, provider, registry, saved setup, session workflow를 쓰지 않는다.
- 로그 관리, run history, failure artifact, raw registry, row/job diagnostic panel을 추가하지 않는다.
- 사용자 catalog는 `.aiworkspace/note/finance/docs/GLOSSARY.md`를 runtime에 자동 파싱하지 않는다.
- 상단 navigation에는 `/reference` 하나만 남긴다. `/guides`, `/glossary`는 새 화면 검증 후 제거한다.
- React는 검색, filter, item 선택, drawer/sheet open/close를 local state로 처리한다.
- Python으로 넘어오는 event는 `navigate_to_surface` 하나뿐이며 destination을 allowlist로 재검증한다.
- 기존 `app/web/reference_guides.py`, `app/services/reference_guides_catalog.py`, `app/services/reference_glossary_catalog.py`는 새 경로와 tests가 GREEN이 된 뒤 제거한다.
- 내부 durable 문서 `GLOSSARY.md`, registry, saved setup, 과거 task/research 기록은 보존한다.
- 현재 worktree의 unrelated untracked PNG와 `.superpowers/`는 stage하거나 수정하지 않는다.

## Exact File Map

| 책임 | 파일 |
| --- | --- |
| canonical catalog, payload, drift guard | `app/services/reference_center.py` |
| Reference page shell, deep link, navigation intent | `app/web/reference_center.py` |
| Streamlit custom component bridge | `app/web/reference_center_react_component.py` |
| React contracts | `app/web/streamlit_components/reference_center_workbench/src/contracts.ts` |
| React ranking/filter | `app/web/streamlit_components/reference_center_workbench/src/search.ts` |
| React application | `app/web/streamlit_components/reference_center_workbench/src/ReferenceCenterWorkbench.tsx` |
| responsive presentation | `app/web/streamlit_components/reference_center_workbench/src/style.css` |
| component entry/build | `app/web/streamlit_components/reference_center_workbench/{index.html,package.json,package-lock.json,tsconfig.json,vite.config.ts,src/main.tsx,component_static/}` |
| single top navigation | `app/web/streamlit_app.py` |
| stable contextual help IDs | `app/services/reference_contextual_help.py`, `app/web/reference_contextual_help.py` |
| contextual help call sites | `app/web/overview/page.py`, `app/web/institutional_portfolios.py`, `app/web/ingestion/page.py`, `app/web/backtest_analysis.py`, `app/web/backtest_practical_validation/page.py`, `app/web/backtest_final_review/page.py`, `app/web/final_selected_portfolio_dashboard.py` |
| Python contracts | `tests/test_reference_center.py`, `tests/test_reference_center_component.py`, `tests/test_reference_contextual_help.py` |
| task evidence | `.aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720/{STATUS.md,NOTES.md,RUNS.md,RISKS.md}` |
| durable alignment | `.aiworkspace/note/finance/docs/{INDEX.md,ROADMAP.md,PROJECT_MAP.md}`, root handoff logs |

## Stable Contracts

### Catalog IDs

The catalog must include exactly these six journey IDs:

```python
REQUIRED_JOURNEY_IDS = {
    "journey.market_understanding",
    "journey.institutional_portfolios",
    "journey.data_preparation",
    "journey.candidate_creation",
    "journey.validation_decision",
    "journey.monitoring",
}
```

The first release must also include these current concept and playbook IDs:

```python
REQUIRED_REFERENCE_ITEM_IDS = {
    "feature.market_context",
    "feature.market_movers",
    "feature.futures_macro",
    "feature.sentiment",
    "feature.events",
    "feature.economic_cycle",
    "status.not_run",
    "status.review",
    "status.blocked",
    "concept.data_trust",
    "concept.provider_coverage",
    "concept.selected_route_gate",
    "concept.saved_portfolio",
    "concept.monitoring_scenario",
    "playbook.ingestion_data_missing",
    "playbook.practical_validation_not_run",
    "playbook.final_review_candidate_missing",
    "playbook.monitoring_scenario_stale",
}
```

### Destinations

```python
REFERENCE_DESTINATIONS = {
    "overview",
    "institutional_portfolios",
    "ingestion",
    "backtest_analysis",
    "practical_validation",
    "final_review",
    "portfolio_monitoring",
}
```

Backtest destination mapping:

```python
BACKTEST_DESTINATION_PANELS = {
    "backtest_analysis": "Backtest Analysis",
    "practical_validation": "Practical Validation",
    "final_review": "Final Review",
}
```

### Payload and Event

```typescript
export type ReferenceKind = "journey" | "concept" | "playbook";
export type ReferenceScope = "all" | ReferenceKind;

export type ReferenceItem = {
  id: string;
  kind: ReferenceKind;
  category: string;
  title: string;
  summary: string;
  aliases: string[];
  keywords: string[];
  related_surfaces: string[];
  meaning: string;
  impact: string;
  next_action: string;
  related_item_ids: string[];
  destination: string | null;
  search_text: string;
};

export type ReferenceCenterPayload = {
  schema_version: "reference_center_v1";
  component: "ReferenceCenterWorkbench";
  filters: Array<{ id: ReferenceScope; label: string }>;
  journeys: string[];
  items: ReferenceItem[];
  initial_item_id: string | null;
  invalid_initial_item: boolean;
  empty_state: {
    title: string;
    description: string;
    suggestions: string[];
  };
};

export type ReferenceCenterEvent = {
  id: "navigate_to_surface";
  destination: string;
  item_id: string;
  nonce: string;
};
```

---

## Task 1: Build the canonical Streamlit-free catalog and drift guard

**Files:**

- Create: `app/services/reference_center.py`
- Create: `tests/test_reference_center.py`

### Step 1: Write the failing catalog boundary tests

Create `tests/test_reference_center.py` with tests that:

- remove `streamlit` from `sys.modules`, import the service, and assert it stays absent;
- assert `schema_version == "reference_center_v1"` and component name;
- assert the journey ID set equals `REQUIRED_JOURNEY_IDS`;
- assert all required concept/playbook IDs exist;
- assert IDs are unique and `kind` is one of `journey`, `concept`, `playbook`;
- assert every item has non-empty `category`, `title`, `summary`, `meaning`, `impact`, `next_action`;
- assert all `related_item_ids` resolve;
- assert every non-null destination is allowlisted;
- assert the drift report contains no missing current surfaces, forbidden labels, duplicate IDs, invalid relations, or invalid destinations;
- assert no user-visible field contains any of these case-insensitive forbidden labels:

```python
FORBIDDEN_USER_LABELS = {
    "Futures Monitor",
    "Macro Thermometer",
    "Candidate Review",
    "Portfolio Proposal",
    "Selected Portfolio Dashboard",
    "Main Worktree",
    "Sub Worktree",
    "Fixture",
}
```

Use `unittest.TestCase` classes throughout the Python test files so the installed runner discovers every test. The defensive lookup test is:

```python
class ReferenceCenterCatalogContractTests(unittest.TestCase):
    def test_reference_item_lookup_is_defensive_and_validates_initial_item(self) -> None:
        item = get_reference_item("status.not_run")
        self.assertIsNotNone(item)
        assert item is not None
        item["title"] = "mutated"
        fresh_item = get_reference_item("status.not_run")
        assert fresh_item is not None
        self.assertEqual(fresh_item["title"], "NOT_RUN")
        self.assertEqual(validate_initial_reference_item("status.not_run"), "status.not_run")
        self.assertIsNone(validate_initial_reference_item("unknown"))
```

### Step 2: Run the test and confirm RED

Run:

```bash
.venv/bin/python -m unittest tests/test_reference_center.py
```

Expected: test import fails with `ModuleNotFoundError: app.services.reference_center`.

### Step 3: Implement the catalog API

Create these public functions in `app/services/reference_center.py` with the exact annotations shown: `get_reference_center_items() -> list[dict[str, Any]]`, `get_reference_item(item_id: str) -> dict[str, Any] | None`, `validate_initial_reference_item(item_id: object) -> str | None`, `validate_reference_destination(destination: object) -> str | None`, `build_reference_center_payload(initial_item_id: object = None) -> dict[str, Any]`, and `build_reference_center_drift_report() -> dict[str, Any]`.

Implement a private `REFERENCE_CENTER_ITEMS` list using the IDs in **Stable Contracts**. Each item must use current labels and contain user-facing Korean copy. Construct `search_text` as normalized concatenation of title, aliases, keywords, summary, meaning, impact, next action, and related surfaces. Use `deepcopy` on every public return value.

The payload constructor must retain invalid-link evidence without passing an invalid ID to React:

```python
normalized_initial = str(initial_item_id or "").strip()
valid_initial = validate_initial_reference_item(normalized_initial)
return {
    "schema_version": "reference_center_v1",
    "component": "ReferenceCenterWorkbench",
    "filters": deepcopy(REFERENCE_FILTERS),
    "journeys": sorted(REQUIRED_JOURNEY_IDS),
    "items": get_reference_center_items(),
    "initial_item_id": valid_initial,
    "invalid_initial_item": bool(normalized_initial and valid_initial is None),
    "empty_state": deepcopy(REFERENCE_EMPTY_STATE),
}
```

The drift report status must be `PASS` only when every issue list is empty.

### Step 4: Run focused tests and confirm GREEN

Run:

```bash
.venv/bin/python -m unittest tests/test_reference_center.py
```

Expected: all tests pass.

### Step 5: Commit the catalog unit

```bash
git add app/services/reference_center.py tests/test_reference_center.py
git commit -m "기능: Reference Center 카탈로그 계약 추가"
```

---

## Task 2: Define the page-shell deep-link and navigation contract

**Files:**

- Create: `app/web/reference_center.py`
- Modify: `tests/test_reference_center.py`

### Step 1: Write failing pure routing tests

Add tests for the pure helpers `normalize_reference_event(value: object) -> dict[str, str] | None` and `resolve_reference_navigation(destination: object) -> dict[str, str] | None` before importing Streamlit rendering.

Required assertions:

```python
assert normalize_reference_event(None) is None
assert normalize_reference_event({"event": {"id": "search", "destination": "overview"}}) is None
assert normalize_reference_event({"event": {"id": "navigate_to_surface", "destination": "raw_registry", "item_id": "x"}}) is None
assert normalize_reference_event({
    "event": {
        "id": "navigate_to_surface",
        "destination": "final_review",
        "item_id": "journey.validation_decision",
        "nonce": "n-1",
    }
}) == {
    "id": "navigate_to_surface",
    "destination": "final_review",
    "item_id": "journey.validation_decision",
    "nonce": "n-1",
}
assert resolve_reference_navigation("final_review") == {
    "page_target_key": "backtest",
    "panel": "Final Review",
}
assert resolve_reference_navigation("portfolio_monitoring") == {
    "page_target_key": "portfolio_monitoring",
    "panel": "",
}
```

### Step 2: Run the tests and confirm RED

Run:

```bash
.venv/bin/python -m unittest tests/test_reference_center.py
```

Expected: imports fail because the helpers are absent.

### Step 3: Implement routing without product mutation

`app/web/reference_center.py` must expose `normalize_reference_event(value: object) -> dict[str, str] | None`, `resolve_reference_navigation(destination: object) -> dict[str, str] | None`, `configure_reference_center_page_targets(page_targets: dict[str, object]) -> None`, and `render_reference_center_page() -> None`.

Keep a module-local `_REFERENCE_PAGE_TARGETS`. Allow only keys `overview`, `institutional_portfolios`, `ingestion`, `backtest`, `portfolio_monitoring`. For Backtest destinations call `request_backtest_panel(panel)` before `st.switch_page(backtest_page)`. For all other allowed destinations call only `st.switch_page(target)`.

Read the initial item once per render:

```python
initial_item = st.query_params.get("item")
payload = build_reference_center_payload(initial_item)
```

Do not mutate query parameters after the React component opens another detail. If `invalid_initial_item` is true, render a compact warning above the component.

At this task stage, import `render_reference_center_workbench` behind the page function so the pure routing tests remain importable before the component bridge exists.

### Step 4: Run focused tests and compile

```bash
.venv/bin/python -m unittest tests/test_reference_center.py
.venv/bin/python -m py_compile app/services/reference_center.py app/web/reference_center.py
```

Expected: both commands pass.

### Step 5: Commit the page contract

```bash
git add app/web/reference_center.py tests/test_reference_center.py
git commit -m "기능: Reference 이동 intent 계약 추가"
```

---

## Task 3: Scaffold the React workbench and implement ranked local search

**Files:**

- Create: `app/web/streamlit_components/reference_center_workbench/index.html`
- Create: `app/web/streamlit_components/reference_center_workbench/package.json`
- Create: `app/web/streamlit_components/reference_center_workbench/package-lock.json`
- Create: `app/web/streamlit_components/reference_center_workbench/tsconfig.json`
- Create: `app/web/streamlit_components/reference_center_workbench/vite.config.ts`
- Create: `app/web/streamlit_components/reference_center_workbench/src/contracts.ts`
- Create: `app/web/streamlit_components/reference_center_workbench/src/search.ts`
- Create: `app/web/streamlit_components/reference_center_workbench/src/search.test.ts`

### Step 1: Copy only the repository-standard toolchain shape

Use `institutional_portfolios_workbench` as the version baseline. Set the new package name to `reference-center-workbench-component` and scripts to:

```json
{
  "dev": "vite --host 0.0.0.0",
  "build": "vite build --outDir component_static",
  "test": "vitest run",
  "typecheck": "tsc --noEmit"
}
```

Run `npm install` inside the new component directory to produce the lock file. Do not add `node_modules` to Git.

### Step 2: Write failing ranking/filter tests

In `src/search.test.ts`, build four fixed items that distinguish exact title, alias prefix, keyword, and summary matches. Assert:

- empty query preserves catalog order;
- exact normalized title ranks before alias prefix;
- alias prefix ranks before keyword, keyword before summary-only;
- multi-token query requires every token;
- `journey`, `concept`, and `playbook` filters exclude other kinds;
- whitespace and case are normalized;
- no match returns an empty list.

Use this function signature:

```typescript
export function searchReferenceItems(
  items: ReferenceItem[],
  query: string,
  scope: ReferenceScope,
): ReferenceItem[];
```

### Step 3: Run Vitest and confirm RED

```bash
cd app/web/streamlit_components/reference_center_workbench
npm test
```

Expected: the test fails because `searchReferenceItems` has not been implemented.

### Step 4: Implement deterministic ranking

Normalize with `toLocaleLowerCase().trim()` and split on whitespace. Discard an item unless all tokens are included in its `search_text`. Score each token using the highest matching field:

```typescript
const SCORE = {
  exactTitleOrAlias: 400,
  titleOrAliasPrefix: 300,
  keyword: 200,
  summaryOrBody: 100,
} as const;
```

Preserve the original catalog order as the final tie-breaker. Never send a search event to Streamlit.

### Step 5: Run tests and typecheck

```bash
npm test
npm run typecheck
```

Expected: Vitest and TypeScript both pass.

### Step 6: Commit the React contract/search unit

```bash
git add app/web/streamlit_components/reference_center_workbench/index.html \
  app/web/streamlit_components/reference_center_workbench/package.json \
  app/web/streamlit_components/reference_center_workbench/package-lock.json \
  app/web/streamlit_components/reference_center_workbench/tsconfig.json \
  app/web/streamlit_components/reference_center_workbench/vite.config.ts \
  app/web/streamlit_components/reference_center_workbench/src/contracts.ts \
  app/web/streamlit_components/reference_center_workbench/src/search.ts \
  app/web/streamlit_components/reference_center_workbench/src/search.test.ts
git commit -m "기능: Reference React 검색 모델 추가"
```

---

## Task 4: Build the search-first React interface and responsive detail sheet

**Files:**

- Create: `app/web/streamlit_components/reference_center_workbench/src/ReferenceCenterWorkbench.tsx`
- Create: `app/web/streamlit_components/reference_center_workbench/src/ReferenceCenterWorkbench.test.tsx`
- Create: `app/web/streamlit_components/reference_center_workbench/src/style.css`
- Create: `app/web/streamlit_components/reference_center_workbench/src/main.tsx`
- Modify: `app/web/streamlit_components/reference_center_workbench/package.json`
- Modify: `app/web/streamlit_components/reference_center_workbench/package-lock.json`
- Modify: `app/web/streamlit_components/reference_center_workbench/vite.config.ts`

### Step 1: Add the component test dependencies

Add `jsdom`, `@testing-library/react`, and `@testing-library/user-event` as development dependencies. Configure Vitest with `environment: "jsdom"` for `*.test.tsx`.

### Step 2: Write failing behavior tests

Export the unwrapped `ReferenceCenterWorkbench` function for tests and use `withStreamlitConnection` only for the default export. Render the unwrapped component with a fixed payload and mock `Streamlit.setComponentValue`. Test:

- search input is the first interactive control;
- all four scope filter labels render: `전체`, `사용 흐름`, `상태·용어`, `문제 해결`;
- the six journey cards render when query is empty;
- typing narrows the result list without invoking `setComponentValue`;
- selecting a result opens its detail and displays meaning, surface, impact, next action, related items;
- clicking a related item replaces the open detail locally;
- `initial_item_id` opens its detail on first render;
- invalid initial item shows the changed/removed notice and remains on home;
- close button returns to the search/list view;
- valid `화면으로 이동` emits exactly one `navigate_to_surface` event;
- missing payload and empty item list render distinct unavailable states.

### Step 3: Run tests and confirm RED

```bash
cd app/web/streamlit_components/reference_center_workbench
npm test
```

Expected: component tests fail because the UI is absent.

### Step 4: Implement the component structure

Use this top-level state only:

```typescript
const [query, setQuery] = useState("");
const [scope, setScope] = useState<ReferenceScope>("all");
const [selectedItemId, setSelectedItemId] = useState<string | null>(payload.initial_item_id);
```

Render in this order:

1. compact title/purpose;
2. search input;
3. four scope chips;
4. six journey cards when query is empty;
5. result list;
6. overlay and detail panel when an item is selected.

The detail order is fixed: `뜻/목적`, `어디서 보이나`, `영향`, `다음 행동`, `관련 항목`, destination button. Add semantic labels and a focusable close button. Set component ready on mount and synchronize frame height after payload, result, and selection changes.

Only destination clicks emit:

```typescript
Streamlit.setComponentValue({
  event: {
    id: "navigate_to_surface",
    destination: selectedItem.destination,
    item_id: selectedItem.id,
    nonce: `${Date.now()}-${Math.random()}`,
  },
});
```

### Step 5: Implement responsive CSS

Use CSS custom properties scoped under `.reference-center`. Required behavior:

- desktop drawer is fixed to the component's right edge, width `min(460px, 44vw)`;
- overlay covers the workbench area and closes only by explicit click or close button;
- at `@media (max-width: 520px)` the panel uses full component width, bottom-sheet positioning, `max-height: 88vh`, and internal scrolling;
- journey grid collapses from 3 columns to 2 at 900px and 1 at 520px;
- no horizontal overflow at 420px;
- visible focus style for search, filter chips, cards, results, links, and close button.

### Step 6: Run React verification

```bash
npm test
npm run typecheck
npm run build
```

Expected: tests, typecheck, and production build pass; `component_static/index.html` exists.

### Step 7: Commit the workbench UI

```bash
git add app/web/streamlit_components/reference_center_workbench/package.json \
  app/web/streamlit_components/reference_center_workbench/package-lock.json \
  app/web/streamlit_components/reference_center_workbench/vite.config.ts \
  app/web/streamlit_components/reference_center_workbench/src \
  app/web/streamlit_components/reference_center_workbench/component_static
git commit -m "기능: Reference 검색 중심 React 화면 구현"
```

---

## Task 5: Add the Streamlit component bridge and compact failure state

**Files:**

- Create: `app/web/reference_center_react_component.py`
- Create: `tests/test_reference_center_component.py`
- Modify: `app/web/reference_center.py`

### Step 1: Write failing bridge tests

Mirror the existing institutional component boundary without importing its product logic. Test:

- availability is false in an empty temp directory and true when `index.html` exists;
- `_json_safe_payload` converts `datetime`, `date`, `Decimal`, pandas timestamps, `NaN`, `inf`, Series, and DataFrame;
- `render_reference_center_workbench` returns `None` when the build is unavailable;
- dict component values are preserved and non-dict values return `None`;
- component name is `reference_center_workbench` and build directory ends in `component_static`.

### Step 2: Run tests and confirm RED

```bash
.venv/bin/python -m unittest tests/test_reference_center_component.py
```

Expected: import fails because the bridge does not exist.

### Step 3: Implement the bridge

Expose these constants and the two annotated functions described immediately below:

```python
REFERENCE_CENTER_REACT_COMPONENT_NAME = "reference_center_workbench"
REFERENCE_CENTER_REACT_COMPONENT_ROOT = Path(__file__).resolve().parent / "streamlit_components" / "reference_center_workbench"
REFERENCE_CENTER_REACT_BUILD_DIR = REFERENCE_CENTER_REACT_COMPONENT_ROOT / "component_static"
```

The functions are `reference_center_react_component_available(build_dir: Path | None = None) -> bool` and `render_reference_center_workbench(payload: dict[str, Any], *, key: str = "reference_center_workbench") -> dict[str, Any] | None`.

Declare only when `component_static/index.html` exists. Call the component with JSON-safe payload and `default={"event": None}`.

### Step 4: Wire the page shell

In `render_reference_center_page`, check availability first. When missing, render only:

```python
st.error("Reference 화면을 불러오지 못했습니다. 배포된 React build를 확인해 주세요.")
st.caption("검색과 도움말 콘텐츠는 변경되지 않았습니다. 화면을 새로고침한 뒤 다시 시도해 주세요.")
```

Do not call the legacy Guide or Glossary renderers. Normalize the returned event, validate it, then route it once.

### Step 5: Run Python and React verification

```bash
.venv/bin/python -m unittest tests/test_reference_center.py tests/test_reference_center_component.py
.venv/bin/python -m py_compile app/web/reference_center.py app/web/reference_center_react_component.py
cd app/web/streamlit_components/reference_center_workbench
npm test
npm run typecheck
npm run build
```

Expected: all commands pass.

### Step 6: Commit the bridge

```bash
git add app/web/reference_center.py app/web/reference_center_react_component.py \
  tests/test_reference_center_component.py \
  app/web/streamlit_components/reference_center_workbench/component_static
git commit -m "기능: Reference React Streamlit 브리지 연결"
```

---

## Task 6: Replace the split navigation with one Reference page

**Files:**

- Modify: `app/web/streamlit_app.py`
- Modify: `tests/test_reference_center.py`

### Step 1: Write the failing shell contract test

Read `app/web/streamlit_app.py` as source and assert:

```python
assert 'title="Reference"' in source
assert 'url_path="reference"' in source
assert 'title="Guides"' not in source
assert 'url_path="guides"' not in source
assert 'title="Glossary"' not in source
assert 'url_path="glossary"' not in source
assert "render_reference_guides_page" not in source
assert "load_glossary_sections_from_markdown" not in source
assert "_render_runtime_build_indicator" not in reference_page_source
```

Also assert `configure_reference_center_page_targets` receives all five page target keys.

### Step 2: Run the shell contract and confirm RED

```bash
.venv/bin/python -m unittest tests/test_reference_center.py
```

Expected: old Guides/Glossary assertions fail.

### Step 3: Update Streamlit page registration

Remove pandas and glossary imports that are used only by the old page. Remove `_load_glossary_sections`, `_load_reference_concepts`, `_format_concept_rows`, `_render_guides_page`, and `_render_glossary_page`.

Register:

```python
reference_page = st.Page(
    render_reference_center_page,
    title="Reference",
    icon="📚",
    url_path="reference",
)
```

Configure page targets:

```python
configure_reference_center_page_targets({
    "overview": overview_page,
    "institutional_portfolios": institutional_portfolios_page,
    "ingestion": ingestion_page,
    "backtest": backtest_page,
    "portfolio_monitoring": selected_portfolio_dashboard_page,
})
```

Use `"Reference": [reference_page]` in `st.navigation`. Keep `_render_runtime_build_indicator` only where Overview or other existing surfaces already use it; never render it inside Reference.

### Step 4: Run focused regression

```bash
.venv/bin/python -m unittest tests/test_reference_center.py tests/test_reference_center_component.py
.venv/bin/python -m py_compile app/web/streamlit_app.py
```

Expected: all commands pass.

### Step 5: Commit navigation integration

```bash
git add app/web/streamlit_app.py tests/test_reference_center.py
git commit -m "기능: Reference 단일 내비게이션 전환"
```

---

## Task 7: Convert contextual help to stable item deep links and expand coverage

**Files:**

- Modify: `app/services/reference_contextual_help.py`
- Modify: `app/web/reference_contextual_help.py`
- Modify: `tests/test_reference_contextual_help.py`
- Modify: `app/web/overview/page.py`
- Modify: `app/web/institutional_portfolios.py`
- Modify: `app/web/ingestion/page.py`
- Modify: `app/web/backtest_analysis.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/web/final_selected_portfolio_dashboard.py`

### Step 1: Rewrite tests to the new link contract and confirm RED

Replace the `/guides`/`/glossary` expectations with:

- required surface keys are exactly or a superset of `overview`, `institutional_portfolios`, `ingestion`, `backtest_analysis`, `practical_validation`, `final_review`, `portfolio_monitoring`;
- every link has `target == "/reference"` and an existing `item_id`;
- drift report has empty `missing_reference_item_ids`, `invalid_links`, and duplicate keys;
- renderer maps `/reference` to a single `reference` page target and calls `st.page_link(page_target, label=label, query_params={"item": item_id})`;
- all seven owner renderers contain their matching `render_reference_contextual_help("<surface_key>"` call.

### Step 2: Run contextual tests and confirm RED

```bash
.venv/bin/python -m unittest tests/test_reference_contextual_help.py
```

Expected: old targets and missing owner call sites fail.

### Step 3: Rewrite service rows with stable IDs

Replace `guide_focus` and `glossary_terms` with `reference_item_ids`. Each help row must link to one or two precise items. Required examples:

```python
{"label": "NOT_RUN 의미 확인", "target": "/reference", "item_id": "status.not_run"}
{"label": "기관 보유 해석 흐름", "target": "/reference", "item_id": "journey.institutional_portfolios"}
{"label": "stale 시나리오 해결", "target": "/reference", "item_id": "playbook.monitoring_scenario_stale"}
```

Import `get_reference_center_items`, not the legacy glossary service, for referential integrity.

### Step 4: Update the renderer and page-target setup

Set:

```python
REFERENCE_PAGE_TARGET_KEYS = {"/reference": "reference"}
```

Call:

```python
st.page_link(
    page_target,
    label=label,
    query_params={"item": item_id},
)
```

Render compact `관련 Reference` links before `먼저 확인할 것` and `경계`. Do not re-create separate Guide/Glossary columns.

### Step 5: Add the seven owner call sites

Place contextual help directly after each surface's title or first purpose paragraph so it is discoverable but collapsed by default. For Backtest stages, add it inside each stage renderer rather than the shared shell. Do not add any help box to legacy `Candidate Review` or `Portfolio Proposal` panels.

Update `streamlit_app.py` so contextual help page targets receive `{"reference": reference_page}`.

### Step 6: Run drift, call-site, and compile checks

```bash
.venv/bin/python -m unittest tests/test_reference_center.py tests/test_reference_contextual_help.py
.venv/bin/python -m py_compile \
  app/services/reference_contextual_help.py \
  app/web/reference_contextual_help.py \
  app/web/overview/page.py \
  app/web/institutional_portfolios.py \
  app/web/ingestion/page.py \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_final_review/page.py \
  app/web/final_selected_portfolio_dashboard.py
```

Expected: all commands pass and drift report status is `PASS`.

### Step 7: Commit contextual help integration

```bash
git add app/services/reference_contextual_help.py app/web/reference_contextual_help.py \
  app/web/streamlit_app.py app/web/overview/page.py app/web/institutional_portfolios.py \
  app/web/ingestion/page.py app/web/backtest_analysis.py \
  app/web/backtest_practical_validation/page.py app/web/backtest_final_review/page.py \
  app/web/final_selected_portfolio_dashboard.py tests/test_reference_contextual_help.py
git commit -m "기능: Reference 문맥 도움말 딥링크 통합"
```

---

## Task 8: Remove the verified legacy renderers and stale tests

**Files:**

- Delete: `app/web/reference_guides.py`
- Delete: `app/services/reference_guides_catalog.py`
- Delete: `app/services/reference_glossary_catalog.py`
- Delete: `tests/test_reference_guides_catalog.py`
- Delete: `tests/test_reference_glossary_catalog.py`
- Modify: `tests/test_reference_center.py`

### Step 1: Write the legacy import guard before deletion

Add a source-tree contract that asserts no active `app/**/*.py` imports these legacy modules or functions:

```python
LEGACY_REFERENCE_SYMBOLS = {
    "reference_guides",
    "reference_guides_catalog",
    "reference_glossary_catalog",
    "render_reference_guides_page",
    "load_glossary_sections_from_markdown",
    "search_glossary_sections",
}
```

Exclude only cache/build directories, never active Python files.

### Step 2: Run the guard and confirm RED

```bash
.venv/bin/python -m unittest tests/test_reference_center.py
```

Expected: existing legacy source files/imports are reported.

### Step 3: Delete old active paths

Delete only the files listed above after `rg` confirms no remaining production import. Preserve `.aiworkspace/note/finance/docs/GLOSSARY.md` and research/task history.

### Step 4: Run Reference and import regression

```bash
rg -n "reference_guides|reference_glossary_catalog|/guides|/glossary" app tests
.venv/bin/python -m unittest \
  tests/test_reference_center.py \
  tests/test_reference_center_component.py \
  tests/test_reference_contextual_help.py
.venv/bin/python -m compileall -q app/services app/web
```

Expected: `rg` returns no active matches and the test/compile commands pass. A no-match `rg` exit status is expected.

### Step 5: Commit legacy removal

```bash
git add -u app/web/reference_guides.py \
  app/services/reference_guides_catalog.py \
  app/services/reference_glossary_catalog.py \
  tests/test_reference_guides_catalog.py \
  tests/test_reference_glossary_catalog.py
git add tests/test_reference_center.py
git commit -m "정리: 기존 Guides Glossary 화면 제거"
```

Before committing, inspect `git status --short` and unstage any unrelated file if present.

---

## Task 9: Synchronize durable documentation and complete responsive Browser QA

**Files:**

- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720/RISKS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated QA screenshot outside the commit, for example: `reference-center-react-v1-qa.png`

### Step 1: Run the full automated verification before documentation claims

From repository root:

```bash
git diff --check
.venv/bin/python -m unittest \
  tests/test_reference_center.py \
  tests/test_reference_center_component.py \
  tests/test_reference_contextual_help.py
.venv/bin/python -m compileall -q app/services app/web
cd app/web/streamlit_components/reference_center_workbench
npm test
npm run typecheck
npm run build
cd ../../../..
test -f app/web/streamlit_components/reference_center_workbench/component_static/index.html
```

Expected: no diff errors, all Python/React tests pass, compile/typecheck/build pass, and the built index exists.

### Step 2: Start the app for Browser QA

Use an available local port and capture the exact command in `RUNS.md`:

```bash
.venv/bin/streamlit run app/web/streamlit_app.py --server.headless true --server.port 8517
```

Keep the session running only for QA, then stop it cleanly.

### Step 3: Perform the required user-flow QA

At desktop width, 900px, and 420px verify:

1. top navigation contains one `Reference` entry and no Guides/Glossary entry;
2. search is the first interactive control;
3. all six journey cards are reachable;
4. `NOT_RUN` search returns the status item and opens detail;
5. filter changes results without a Streamlit rerun/visible page reset;
6. related item click replaces the detail locally;
7. desktop uses side drawer, 420px uses full-width sheet;
8. explicit close returns to the list;
9. `/reference?item=status.not_run` opens the intended detail;
10. invalid deep link falls back with the changed/removed notice;
11. a valid destination moves to its owning surface;
12. contextual link from an owner surface opens its exact item;
13. browser back from contextual deep link returns to the owner surface;
14. no clipping, overlap, or horizontal overflow exists.

Capture one screenshot showing the desktop Reference search plus open detail. Save it as a generated artifact and do not stage it.

### Step 4: Run a wider regression proportional to navigation risk

Identify navigation/backtest shell tests with `rg --files tests | rg 'streamlit|navigation|backtest_page|workflow_routes'`, then run the relevant files in addition to the focused suite. Record the exact selected files and result in `RUNS.md`. If the repository has no direct multipage shell test, record that gap in `RISKS.md` and rely on Browser QA plus source contract tests.

### Step 5: Synchronize documentation with verified facts only

Use `finance-doc-sync` before editing durable docs. Record:

- `PROJECT_MAP.md`: new service/page/component ownership and removal of old active paths;
- `ROADMAP.md`: Reference Center V1 completed only if every acceptance criterion is verified;
- `INDEX.md`: correct durable links if Reference architecture docs are indexed;
- task `STATUS.md`: roadmap `4/4차` only after Browser QA;
- `RUNS.md`: exact commands, test counts, browser viewport checks, screenshot path;
- `RISKS.md`: only unresolved validation gaps;
- root handoff logs: 3–5 concise lines pointing to the task directory.

Do not copy implementation chatter into root logs.

### Step 6: Final repository checks

```bash
git status --short
git diff --check
git diff --stat
git diff -- .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720
```

Confirm unrelated PNGs and `.superpowers/` remain untracked and unstaged.

### Step 7: Commit documentation closeout

```bash
git add .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/tasks/active/reference-center-react-v1-20260720 \
  .aiworkspace/note/finance/tasks/active/README.md \
  .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md \
  app/web/streamlit_components/reference_center_workbench/component_static
git commit -m "문서: Reference Center 구현 및 QA 결과 정렬"
```

### Step 8: Final completion evidence

Run after the last commit:

```bash
git status --short
git log -9 --oneline
git diff HEAD^ --check
```

Completion may be claimed only when:

- all nine tasks are committed;
- focused Python tests, React tests, typecheck, build, compile, and diff checks pass;
- desktop/900/420 Browser QA is recorded;
- the screenshot exists but is not staged;
- the task status reports overall roadmap `4/4차` and lists no unverified acceptance criterion as complete.

## Execution Checkpoints

After Tasks 1–2, report **1차 catalog/contract 완료** and confirm no navigation changed yet.

After Tasks 3–5, report **2차 React workbench 완료** with test/typecheck/build evidence.

After Tasks 6–7, report **3차 navigation/contextual help 완료** and note that legacy source still exists until Task 8.

After Tasks 8–9, report **4차 legacy removal/docs/QA 완료** with the screenshot and remaining risk, if any.
