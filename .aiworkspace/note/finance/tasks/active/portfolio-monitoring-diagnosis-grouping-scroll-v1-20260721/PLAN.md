# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 반복되는 상관·낙폭 진단을 유형별 한 카드로 요약하면서 개별 근거를 보존하고, desktop 진단 열이 560px 이후 내부 스크롤되게 한다.

**Architecture:** Python diagnosis projection이 raw fact와 별도로 stable display group을 만들고 priority, subject identity, summary를 소유한다. React는 additive group contract를 표시하고 legacy payload는 one-member group으로 정규화한다. CSS는 desktop diagnosis list만 높이를 제한하고 mobile에서는 page scroll로 되돌린다.

**Tech Stack:** Python dataclasses/unittest, React 18, TypeScript, Vitest, CSS, Vite, Streamlit custom component, Playwright Browser QA.

## Global Constraints

- `correlation_cluster`와 `current_drawdown`만 V1 family grouping한다.
- threshold, severity, confidence, exposure/behavior 계산은 바꾸지 않는다.
- raw `weaknesses`, `all_rows`, diagnosis history snapshot은 fact 단위를 보존한다.
- workspace 변경은 additive contract만 허용한다.
- desktop `> 760px` list max height는 `560px`; mobile `<= 760px`는 `max-height: none`, `overflow: visible`이다.
- DB schema, registry, saved JSONL, live approval, broker/order 기능을 만들지 않는다.

---

### Task 1: Python diagnosis display group projection

**Files:**
- Modify: `app/services/portfolio_monitoring/diagnosis.py:45-230,270-326`
- Test: `tests/test_portfolio_monitoring_diagnosis.py:153-205`

**Interfaces:**
- Produces: `DiagnosisDisplayGroup(group_id, family, section, representative, summary_fact, member_count, members)`
- Produces: `DiagnosisProjection.display_groups: tuple[DiagnosisDisplayGroup, ...]`
- Adds: `DiagnosisFact.subject_ids: tuple[str, ...] = ()`
- Adds: `DiagnosisFact.primary_metric: float | None = None`

- [x] **Step 1: Write failing correlation grouping test**

Construct three correlation facts with `subject_ids`, `primary_metric`, and different affected weights. Assert one correlation display group, three members, three preserved raw weaknesses/all_rows, max `0.98` in `summary_fact`, and only one correlation representative in `top_three`.

```python
groups = [group for group in projection.display_groups if group.family == "correlation_cluster"]
self.assertEqual(len(groups), 1)
self.assertEqual(groups[0].member_count, 3)
self.assertEqual(len(projection.weaknesses), 3)
self.assertEqual(len(projection.all_rows), 3)
self.assertIn("0.98", groups[0].summary_fact)
```

- [x] **Step 2: Write failing drawdown grouping test**

Construct two `current_drawdown` facts and one unrelated weakness. Assert one drawdown group with two members, the most negative drawdown in `summary_fact`, and distinct families in `top_three`.

- [x] **Step 3: Run RED tests**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_diagnosis.PortfolioMonitoringDiagnosisTests.test_projection_groups_correlation_pairs_without_dropping_raw_rows \
  tests.test_portfolio_monitoring_diagnosis.PortfolioMonitoringDiagnosisTests.test_projection_groups_drawdown_items_for_first_read -v
```

Expected: FAIL because fact metadata and `display_groups` do not exist.

- [x] **Step 4: Implement compatible metadata and group projection**

Add default fields to `DiagnosisFact` and this dataclass:

```python
@dataclass(frozen=True)
class DiagnosisDisplayGroup:
    group_id: str
    family: str
    section: str
    representative: DiagnosisFact
    summary_fact: str
    member_count: int
    members: tuple[DiagnosisFact, ...]
```

Add helpers `_display_family()`, `_display_group_key()`, `_display_summary()`, `_build_display_groups()`. Only correlation/drawdown collapse by family. Use current severity/affected-weight/persistence/confidence priority for representative and group order. Correlation summary uses maximum `primary_metric` and affected weight; drawdown summary uses minimum `primary_metric`. Build groups after current strength/weakness/data-gap separation and derive `top_three` from weakness group representatives. Keep `all_rows` unchanged.

- [x] **Step 5: Populate structured metadata**

Extend `_fact()` with optional metadata. Pass `(item_id,)` and `drawdown` for current drawdown; `(left, right)` and `correlation` for correlation cluster. Other rules retain defaults.

- [x] **Step 6: Run GREEN diagnosis tests**

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_diagnosis -v
```

Expected: all diagnosis tests PASS.

- [x] **Step 7: Commit Task 1**

```bash
git add app/services/portfolio_monitoring/diagnosis.py tests/test_portfolio_monitoring_diagnosis.py
git commit -m "기능: 포트폴리오 진단 표시 그룹 추가"
```

---

### Task 2: Workspace and TypeScript compatibility contract

**Files:**
- Modify: `app/services/portfolio_monitoring/read_model.py:720-730`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts:170-220`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts:450-460`
- Test: `tests/test_portfolio_monitoring_read_model.py:390-430`
- Test: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts:353-390`

**Interfaces:**
- Consumes: `DiagnosisProjection.display_groups`
- Produces: workspace `diagnosis.display_groups`, TypeScript `DiagnosisDisplayGroup`, grouped `buildDiagnosisSections()`

- [x] **Step 1: Write failing serialization test**

Build a workspace with three correlation facts and assert one serialized correlation group with `member_count == 3`, while `all_rows` remains three rows.

- [x] **Step 2: Write failing grouped/legacy Vitest**

Assert a server group remains one weakness group. Omit `display_groups` in a legacy fixture and assert each old row becomes a one-member group in its original section.

```typescript
expect(buildDiagnosisSections(grouped).weaknesses).toHaveLength(1);
expect(buildDiagnosisSections(legacy).weaknesses[0].member_count).toBe(1);
```

- [x] **Step 3: Run RED contract tests**

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_read_model.PortfolioMonitoringReadModelTests.test_workspace_serializes_diagnosis_display_groups -v
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test -- --run src/workbenchState.test.ts
```

Expected: Python and Vitest FAIL for missing group contract.

- [x] **Step 4: Serialize and type additive groups**

Serialize `[asdict(group) for group in diagnosis.display_groups]`. Add optional `subject_ids`/`primary_metric` to `DiagnosisRow` and define:

```typescript
export type DiagnosisDisplayGroup = {
  group_id: string;
  family: string;
  section: "strength" | "weakness" | "data_gap";
  representative: DiagnosisRow;
  summary_fact: string;
  member_count: number;
  members: DiagnosisRow[];
};
```

Make `DiagnosisProjection.display_groups` optional for legacy payloads.

- [x] **Step 5: Normalize sections with legacy fallback**

Add `legacyDiagnosisGroup(row, section)`. Use server groups when present; otherwise wrap strengths/weaknesses/data_gaps. `now` is the first three non-low weakness groups. Preserve `evidence: diagnosis.all_rows`.

- [x] **Step 6: Run GREEN contract tests**

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_read_model -v
npm test -- --run src/workbenchState.test.ts
npm run typecheck
```

Expected: all commands PASS.

- [x] **Step 7: Commit Task 2**

```bash
git add app/services/portfolio_monitoring/read_model.py tests/test_portfolio_monitoring_read_model.py \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts
git commit -m "기능: 진단 그룹 workspace 계약 연결"
```

---

### Task 3: Group card rendering and bounded lanes

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx:480-510,715-730`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css:103-125,370-385`
- Modify: `tests/test_portfolio_monitoring_component.py:115-140`
- Build: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`

**Interfaces:**
- Consumes: group arrays and `activeGroup.item_rows` label map
- Produces: accessible group cards and desktop-only bounded lists

- [x] **Step 1: Write failing CSS/source contract test**

Assert `.pm-diagnosis-list`, `max-height: 560px`, `overflow-y: auto`, `scrollbar-gutter: stable`, and mobile reset `max-height: none; overflow: visible` exist.

- [x] **Step 2: Run RED component test**

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component.PortfolioMonitoringComponentTests.test_diagnosis_lists_are_bounded_only_on_desktop -v
```

Expected: FAIL because the wrapper/CSS contract does not exist.

- [x] **Step 3: Implement group-aware presentation**

Add `diagnosisSubject(row, labels)` and `diagnosisHeadline(group)`. Multiple correlation members use `함께 움직이는 조합 N개가 확인되었습니다.`; multiple drawdown members use `낙폭 재확인 종목 N개가 확인되었습니다.`; one-member groups keep representative meaning. `DiagnosisGroupCard` shows representative severity/confidence, headline, summary, subject label, and all member evidence inside one disclosure.

- [x] **Step 4: Add counts and scroll wrappers**

Each section uses a heading with display group count and a focusable `.pm-diagnosis-list` with an accessible label. Build `monitoring_item_id -> source_ref` from `activeGroup.item_rows`; missing ids display `추적 항목`.

- [x] **Step 5: Add desktop/mobile CSS**

```css
.pm-diagnosis-list {
  display: grid;
  align-content: start;
  gap: 8px;
  max-height: 560px;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-gutter: stable;
}
```

Under `@media (max-width: 760px)` reset with `max-height: none; overflow: visible; padding-right: 0; scrollbar-gutter: auto`.

- [x] **Step 6: Run GREEN UI checks and build**

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component -v
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test -- --run
npm run typecheck
npm run build
```

Expected: all tests/typecheck/build PASS and canonical hashed asset updates.

- [x] **Step 7: Commit Task 3**

```bash
git add tests/test_portfolio_monitoring_component.py \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css \
  app/web/streamlit_components/portfolio_monitoring_workbench/component_static
git commit -m "개선: 포트폴리오 진단 그룹과 스크롤 화면 적용"
```

---

### Task 4: Regression, Browser QA, and documentation closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Verifies unchanged raw policy facts and grouped desktop/mobile UX

- [x] **Step 1: Run full automation**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -q
.venv/bin/python -m py_compile app/services/portfolio_monitoring/diagnosis.py \
  app/services/portfolio_monitoring/read_model.py app/web/final_selected_portfolio_dashboard.py \
  app/web/portfolio_monitoring_react_component.py
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test -- --run
npm run typecheck
npm run build
```

Expected: tests PASS and build/compile exit 0.

- [x] **Step 2: Run isolated Browser QA**

Use a temporary Streamlit fixture, not production writes. Desktop verifies three correlation members become one group, two drawdowns become one group, disclosure retains subjects/values, diagnosis list `scrollHeight > clientHeight`, `clientHeight <= 560`, keyboard focus works, and console errors are zero. At 420px verify one-column layout, `overflowY=visible`, `maxHeight=none`, page scroll, and zero horizontal overflow. Save `portfolio-monitoring-diagnosis-grouping-scroll-qa.png` but do not stage it.

- [x] **Step 3: Synchronize docs**

Record raw fact preservation, family-grouped display, desktop 560px boundary, mobile page scroll, exact test counts, and Browser QA evidence. Any unverified gap stays in `RISKS.md`.

- [x] **Step 4: Run final hygiene**

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_docs -q
git diff --check
git status --short
```

Expected: docs tests PASS, diff clean, only intended files plus pre-existing untracked artifacts.

- [x] **Step 5: Commit Task 4**

```bash
git add .aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md \
  .aiworkspace/note/finance/tasks/active/portfolio-monitoring-diagnosis-grouping-scroll-v1-20260721 \
  .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: 포트폴리오 진단 그룹화와 QA 정리"
```

## Plan Self-Review

- Spec coverage: family grouping, raw preservation, subject identity, summary, top-three dedup, legacy fallback, desktop scroll, mobile reset, QA, docs가 Tasks 1-4에 연결된다.
- Placeholder scan: 미정 값이나 추상적 테스트 지시가 없다.
- Type consistency: Python/TypeScript group fields는 `group_id`, `family`, `section`, `representative`, `summary_fact`, `member_count`, `members`로 일치한다.
