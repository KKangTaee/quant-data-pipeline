# Economic Cycle Asset State Role Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 자산별 확인 포인트의 공통 경제 배경을 Evidence와 같은 역할별 문구로 표시해 현재 실물 수준과 1·2개월 전망 영향을 혼동 없이 읽게 한다.

**Architecture:** Python의 `_economic_state()`는 기존 factor 값과 direction enum을 유지하면서 역할별 요약 문장만 생성한다. React는 기존 `resolveEvidencePresentation()`을 재사용하는 `resolveEconomicStatePresentation()`을 두어 자산 카드 배지가 Evidence와 같은 상태 문구와 tone을 사용하게 한다. payload 구조, 계산식, 임계값과 자산 경로는 변경하지 않는다.

**Tech Stack:** Python 3, pytest, React, TypeScript, CSS, Vite, Streamlit custom component

## Global Constraints

- 제목은 `사이클 판단의 공통 경제 배경`으로 표시한다.
- 실물 factor는 `기준 이상 / 기준 이하 / 기준 부근`, 금융·선행 여건은 `전망 지원 / 전망 부담 / 영향 중립`, 물가·정책 압력은 `전망 부담 / 부담 완화 / 영향 중립`을 사용한다.
- 요약은 `현재 수준`과 `전망 여건`을 분리한다.
- factor score, expanding robust scale, `±0.15` 임계값, direction enum, 국면 확률과 자산별 경로 계산은 변경하지 않는다.
- 자료 부족은 숨기지 않고 `자료 부족`으로 표시한다.
- unrelated untracked 파일과 사용자 변경은 stage하거나 수정하지 않는다.

---

### Task 1: 역할별 공통 경제 배경 요약

**Files:**
- Modify: `tests/test_economic_cycle_service.py`
- Modify: `finance/economic_cycle_asset_pathways.py:399-452`

**Interfaces:**
- Consumes: `_economic_state(evidence: Sequence[Mapping[str, object]]) -> dict[str, object]`
- Produces: 기존 `summary` 문자열에 `현재 수준:`과 `전망 여건:` 역할별 문장, 기존 `observations[*].direction` enum 보존

- [ ] **Step 1: 역할별 요약을 요구하는 실패 테스트 작성**

`test_market_implications_separate_observed_state_from_asset_pathways()`에 아래 기대값을 추가하고 이전 `약화` narrative 기대값을 새 요약으로 교체한다.

```python
    summary = gold["economic_state"]["summary"]
    assert summary == (
        "현재 수준: 생산·소비 활동과 고용·소득은 자기 과거 기준 이하입니다. "
        "전망 여건: 금융·선행 여건은 전망을 지원합니다. "
        "물가·정책 압력은 전망에 부담을 줍니다."
    )
    assert [row["direction"] for row in gold["economic_state"]["observations"]] == [
        "WEAKENING",
        "WEAKENING",
        "STRENGTHENING",
        "STRENGTHENING",
    ]
    assert summary in gold["narrative"]
```

`test_market_implications_do_not_invent_reasons_when_factor_coverage_is_low()`에는 결측이 역할 안에 남는지 확인한다.

```python
    summary = gold["economic_state"]["summary"]
    assert "현재 수준:" in summary
    assert "전망 여건:" in summary
    assert "자료가 부족합니다" in summary
```

- [ ] **Step 2: 테스트가 이전 공통 강화/약화 요약 때문에 실패하는지 확인**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_economic_cycle_service.py::test_market_implications_separate_observed_state_from_asset_pathways \
  tests/test_economic_cycle_service.py::test_market_implications_do_not_invent_reasons_when_factor_coverage_is_low -q
```

Expected: 새 `현재 수준:` 요약 assertion이 실패하고 기존 direction enum assertion은 통과한다.

- [ ] **Step 3: `_economic_state()`에 역할별 summary builder 구현**

`finance/economic_cycle_asset_pathways.py`에 다음 작은 helper를 추가한다.

```python
def _join_korean_labels(labels: Sequence[str]) -> str:
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return f"{', '.join(labels[:-1])}과 {labels[-1]}"


def _current_level_summary(observations: Sequence[Mapping[str, object]]) -> str:
    phrases = {
        "STRENGTHENING": "자기 과거 기준 이상입니다",
        "WEAKENING": "자기 과거 기준 이하입니다",
        "NEUTRAL": "자기 과거 기준 부근입니다",
        "UNAVAILABLE": "자료가 부족합니다",
    }
    clauses = []
    for direction in ("WEAKENING", "STRENGTHENING", "NEUTRAL", "UNAVAILABLE"):
        labels = [str(row["label"]) for row in observations if row["direction"] == direction]
        if labels:
            clauses.append(f"{_join_korean_labels(labels)}은 {phrases[direction]}.")
    return " ".join(clauses)


def _forecast_context_summary(observations: Sequence[Mapping[str, object]]) -> str:
    by_factor = {str(row["factor"]): row for row in observations}
    phrase_by_factor = {
        "financial_leading_score": {
            "STRENGTHENING": "전망을 지원합니다",
            "WEAKENING": "전망에 부담을 줍니다",
            "NEUTRAL": "전망 영향이 중립적입니다",
            "UNAVAILABLE": "자료가 부족합니다",
        },
        "inflation_policy_score": {
            "STRENGTHENING": "전망에 부담을 줍니다",
            "WEAKENING": "전망 부담을 완화합니다",
            "NEUTRAL": "전망 영향이 중립적입니다",
            "UNAVAILABLE": "자료가 부족합니다",
        },
    }
    clauses = []
    for factor in ("financial_leading_score", "inflation_policy_score"):
        row = by_factor[factor]
        direction = str(row["direction"])
        clauses.append(f"{row['label']}은 {phrase_by_factor[factor][direction]}.")
    return " ".join(clauses)
```

`_economic_state()`의 기존 direction 기반 summary 조립을 아래로 교체한다.

```python
    current_rows = [
        row for row in observations
        if row["factor"] in {"activity_score", "labor_income_score"}
    ]
    forecast_rows = [
        row for row in observations
        if row["factor"] in {"financial_leading_score", "inflation_policy_score"}
    ]
    summary = (
        f"현재 수준: {_current_level_summary(current_rows)} "
        f"전망 여건: {_forecast_context_summary(forecast_rows)}"
    )
```

- [ ] **Step 4: 역할별 요약 테스트 통과 확인**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_economic_cycle_service.py::test_market_implications_separate_observed_state_from_asset_pathways \
  tests/test_economic_cycle_service.py::test_market_implications_do_not_invent_reasons_when_factor_coverage_is_low -q
```

Expected: `2 passed`.

- [ ] **Step 5: Task 1 커밋**

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_service.py
git commit -m "자산별 공통 경제 배경 요약 정리"
```

---

### Task 2: React 역할별 배지와 제목 통일

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:294-299,598-610`
- Modify generated build: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: `EconomicState["observations"][number]`, 기존 `resolveEvidencePresentation(item: Evidence)`
- Produces: `resolveEconomicStatePresentation(observation) -> Pick<EvidencePresentation, "statusLabel" | "tone">`

- [ ] **Step 1: 새 제목과 역할별 배지를 요구하는 source contract 실패 테스트 작성**

`test_cycle_component_contains_cycle_map_ribbon_and_asset_context()`와 `test_economic_cycle_asset_ui_uses_observation_sections_without_left_rails()`의 기존 `관측된 경제 상태` 기대값을 `사이클 판단의 공통 경제 배경`으로 교체하고 다음 token을 추가한다.

```python
        "resolveEconomicStatePresentation",
        'STRENGTHENING: "강화"',
        'WEAKENING: "약화"',
        'statusLabel: "자료 부족"',
        "resolveEvidencePresentation",
```

또한 공통 방향을 직접 렌더링하지 않는지 확인한다.

```python
    assert "관측된 경제 상태" not in source
    assert "ECONOMIC_DIRECTION_LABEL[observation.direction]" not in source
```

- [ ] **Step 2: source contract가 누락된 helper와 새 제목 때문에 실패하는지 확인**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_market_context_economic_cycle.py::test_cycle_component_contains_cycle_map_ribbon_and_asset_context \
  tests/test_market_context_economic_cycle.py::test_economic_cycle_asset_ui_uses_observation_sections_without_left_rails -q
```

Expected: 새 제목 또는 `resolveEconomicStatePresentation` token assertion이 실패한다.

- [ ] **Step 3: EconomicState direction을 기존 Evidence 표현으로 연결**

`EconomicCycleWorkbench.tsx`의 기존 `ECONOMIC_DIRECTION_LABEL`을 다음 변환표와 helper로 교체한다.

```tsx
const ECONOMIC_TO_EVIDENCE_DIRECTION: Record<
  Exclude<EconomicState["observations"][number]["direction"], "UNAVAILABLE">,
  Evidence["direction"]
> = {
  STRENGTHENING: "강화",
  WEAKENING: "약화",
  NEUTRAL: "중립",
};

function resolveEconomicStatePresentation(
  observation: EconomicState["observations"][number],
): Pick<EvidencePresentation, "statusLabel" | "tone"> {
  if (observation.direction === "UNAVAILABLE") {
    return { statusLabel: "자료 부족", tone: "neutral" };
  }
  const group = observation.factor === "activity_score" || observation.factor === "labor_income_score"
    ? "real_economy"
    : "forecast_context";
  return resolveEvidencePresentation({
    factor: observation.factor,
    group,
    direction: ECONOMIC_TO_EVIDENCE_DIRECTION[observation.direction],
  });
}
```

`EconomicStateBlock`은 역할별 표시값을 사용하도록 교체한다.

```tsx
function EconomicStateBlock({ state }: { state: EconomicState }) {
  return (
    <section className="economic-state-block">
      <h5>사이클 판단의 공통 경제 배경</h5>
      <p>{state.summary}</p>
      <div className="economic-observations">
        {state.observations.map((observation) => {
          const presentation = resolveEconomicStatePresentation(observation);
          return (
            <span
              key={observation.factor}
              className={`evidence-tone-${presentation.tone}`}
            >
              {observation.label} · {presentation.statusLabel}
            </span>
          );
        })}
      </div>
    </section>
  );
}
```

- [ ] **Step 4: source contract와 focused regression 통과 확인**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_market_context_economic_cycle.py \
  tests/test_economic_cycle_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
```

Expected: 전체 테스트 통과, Vite production build exit 0, static assets 갱신.

- [ ] **Step 5: Task 2 커밋**

```bash
git add \
  app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx \
  app/web/streamlit_components/economic_cycle_workbench/component_static \
  tests/test_market_context_economic_cycle.py
git commit -m "자산별 공통 경제 배경 배지 통일"
```

---

### Task 3: 실제 화면 QA와 문서 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-evidence-role-copy-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-evidence-role-copy-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-evidence-role-copy-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-evidence-role-copy-v1-20260719/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated QA screenshots under `/tmp/codex-browser-qa/` only

**Interfaces:**
- Consumes: Task 1 역할별 summary, Task 2 역할별 asset-card badge
- Produces: desktop/420px QA evidence와 durable task/root handoff

- [ ] **Step 1: Streamlit 실행 및 desktop QA**

Run:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py \
  --server.port 8501 \
  --server.headless true \
  --server.runOnSave false \
  --server.fileWatcherType none
```

Browser에서 `시장 맥락 > 경제 사이클 > 자산별 확인 포인트`를 열고 다음을 확인한다.

```text
사이클 판단의 공통 경제 배경
현재 수준:
전망 여건:
생산·소비 활동 · 기준 이하
고용·소득 · 기준 이하
금융·선행 여건 · 전망 지원
물가·정책 압력 · 전망 부담
```

Expected: 위 문구가 같은 카드 안에서 일관되게 표시되고 이전 `관측된 경제 상태`, 공통 `강화/약화` 배지가 없다.

- [ ] **Step 2: 420px 반응형 QA**

Viewport를 `420x900`으로 바꾸고 다음을 확인한다.

```text
outer scrollWidth == outer clientWidth
component scrollWidth == component clientWidth
latest reload console error count == 0
```

Expected: 텍스트 겹침과 가로 overflow가 없고 배지가 의미 단위로 wrap된다. desktop과 mobile screenshot을 `/tmp/codex-browser-qa/`에 저장한다.

- [ ] **Step 3: 최종 자동 검증**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_market_context_economic_cycle.py \
  tests/test_economic_cycle_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git diff --check
```

Expected: 모든 focused test 통과, Vite build exit 0, `git diff --check` exit 0.

- [ ] **Step 4: task와 root handoff 문서 갱신**

아래 사실만 기록한다.

```text
- 전체 후속 roadmap 3/3 완료
- 자산 카드의 경제 배경과 Evidence가 같은 역할별 문구를 사용
- direction enum, 모델, 임계값, 확률, 자산 경로는 변경하지 않음
- focused test/build/desktop/420px QA 결과와 screenshot 경로
```

- [ ] **Step 5: 문서 closeout 커밋**

```bash
git add \
  .aiworkspace/note/finance/tasks/active/overview-economic-cycle-evidence-role-copy-v1-20260719 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "자산별 공통 경제 배경 QA 마무리"
```

QA screenshot과 unrelated untracked 파일은 commit하지 않는다.
