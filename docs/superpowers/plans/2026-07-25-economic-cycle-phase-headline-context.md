# Economic Cycle Phase Headline Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Status: Complete

**Goal:** Economic Cycle hero가 우세 국면명과 함께 실물경제의 수준·최근 3개월 방향을 바로 설명하게 한다.

**Architecture:** Python read model이 네 국면의 사용자 설명을 소유하고 기존 `headline.summary`에 전달한다. React는 현재 payload 표시 계약을 그대로 유지하므로 UI 구조와 확률·모델·DB 경계는 변경하지 않는다.

**Tech Stack:** Python 3.12, pytest, Streamlit, React/Vite, Browser QA

## Global Constraints

- hero 제목의 짧은 `<국면> 우세` 표기는 유지한다.
- recovery/expansion/slowdown/recession 설명은 승인된 수준·최근 3개월 방향 문구를 사용한다.
- 판단할 수 없는 결과는 기존 제한 문구를 유지한다.
- 확률 카드, 월중 비교, cycle map, ribbon의 짧은 국면명은 변경하지 않는다.
- 모델 feature, probability, snapshot schema, DB, provider 수집은 변경하지 않는다.

---

### Task 1: Phase별 hero 설명을 read model에 연결

**Files:**
- Modify: `app/services/overview/economic_cycle.py:33-47, 525-540`
- Modify: `tests/test_economic_cycle_service.py:80-140`

**Interfaces:**
- Consumes: `current_phase: str | None`
- Produces: `headline.summary: str`
- Preserves: React `payload.headline.summary`, probability/model/storage contracts

- [x] **Step 1: 네 국면의 사용자 설명을 검증하는 실패 테스트를 작성한다**

`tests/test_economic_cycle_service.py`에 다음 parametrized test를 추가한다.

```python
@pytest.mark.parametrize(
    ("phase", "expected"),
    [
        (
            "recovery",
            "생산·소비와 고용·소득 수준은 낮지만 최근 3개월 흐름은 개선 중입니다.",
        ),
        (
            "expansion",
            "생산·소비와 고용·소득 수준이 높고 최근 3개월 흐름도 개선 중입니다.",
        ),
        (
            "slowdown",
            "생산·소비와 고용·소득 수준은 높지만 최근 3개월 흐름은 약화 중입니다.",
        ),
        (
            "recession",
            "생산·소비와 고용·소득 수준이 낮고 최근 3개월 흐름도 약화 중입니다.",
        ),
    ],
)
def test_headline_explains_phase_as_level_and_three_month_momentum(
    phase: str,
    expected: str,
) -> None:
    service = _load_service()
    snapshot = _ready_snapshot()
    horizons = json.loads(str(snapshot["forecast_path_json"]))
    horizons[0].update(
        {
            "dominant_phase": phase,
            "probabilities": _probabilities(phase),
        }
    )
    snapshot["current_phase"] = phase
    snapshot["forecast_path_json"] = json.dumps(horizons)
    snapshot["probabilities_json"] = json.dumps(_probabilities(phase))

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: _history_rows(),
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    assert model["headline"]["summary"] == expected
```

이 테스트는 phase가 맞아도 generic `현재는 … 국면 가능성이 가장 높습니다.`가 다시
노출되는 회귀를 잡는다.

- [x] **Step 2: 새 테스트가 기존 generic summary 때문에 실패하는지 확인한다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_economic_cycle_service.py \
  -k headline_explains_phase
```

Expected: 4 cases FAIL. 실제 값은 기존 generic summary다.

- [x] **Step 3: Python service에 phase별 headline summary mapping을 추가한다**

`PHASE_LABELS` 인접 위치에 다음 상수를 둔다.

```python
PHASE_HEADLINE_SUMMARIES = {
    "recovery": "생산·소비와 고용·소득 수준은 낮지만 최근 3개월 흐름은 개선 중입니다.",
    "expansion": "생산·소비와 고용·소득 수준이 높고 최근 3개월 흐름도 개선 중입니다.",
    "slowdown": "생산·소비와 고용·소득 수준은 높지만 최근 3개월 흐름은 약화 중입니다.",
    "recession": "생산·소비와 고용·소득 수준이 낮고 최근 3개월 흐름도 약화 중입니다.",
}
```

headline summary는 다음 우선순위를 사용한다.

```python
headline_summary = (
    PHASE_HEADLINE_SUMMARIES.get(str(current_phase))
    if current_phase
    else str(current.get("reason") or "현재 국면 판단이 제한적입니다.")
)
```

- [x] **Step 4: 새 테스트와 Economic Cycle service 회귀를 통과시킨다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q tests/test_economic_cycle_service.py
```

Expected: PASS.

- [x] **Step 5: 변경을 커밋한다**

```bash
git add \
  app/services/overview/economic_cycle.py \
  tests/test_economic_cycle_service.py
git commit -m "개선: 경제사이클 국면 의미를 첫 화면에 설명"
```

---

### Task 2: Production build, actual Browser QA, 문서 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generated only: `economic-cycle-phase-headline-context-qa.png`

**Interfaces:**
- Consumes: Task 1의 `headline.summary`
- Produces: desktop/420px visual evidence와 durable handoff
- Preserves: generated artifact와 unrelated dirty files의 unstaged 상태

- [x] **Step 1: focused regression과 production build를 실행한다**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q \
  tests/test_economic_cycle_service.py \
  tests/test_market_context_economic_cycle.py

cd app/web/streamlit_components/economic_cycle_workbench
npm run build
```

Expected: Python PASS, Vite production build PASS.

- [x] **Step 2: actual desktop/420px Browser QA를 실행한다**

`/overview`의 Economic Cycle hero에서 다음을 확인한다.

- 제목은 `회복 우세`
- 설명은 `생산·소비와 고용·소득 수준은 낮지만 최근 3개월 흐름은 개선 중입니다.`
- 확률 카드와 cycle map은 짧은 phase label 유지
- desktop/420px document overflow 0
- console warning/error 0

QA screenshot은 generated
`economic-cycle-phase-headline-context-qa.png`로 저장하고 커밋하지 않는다.

- [x] **Step 3: durable docs에 hero 의미 계약과 QA 결과를 동기화한다**

- `PROJECT_MAP.md`: current hero는 phase의 level×3M momentum 설명을 함께 표시한다고 기록
- `WORK_PROGRESS.md`: 구현·focused/Browser QA 핵심 3~5줄 기록
- `QUESTION_AND_ANALYSIS_LOG.md`: 사용자 질문, 해석, 결정, follow-up 기록

- [x] **Step 4: closeout 검증을 실행한다**

Run:

```bash
.venv/bin/python -m py_compile app/services/overview/economic_cycle.py
.venv/bin/python \
  .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
git diff --check
```

Expected: all commands exit 0.

- [x] **Step 5: closeout 문서를 커밋한다**

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: 경제사이클 국면 설명 개선 기록"
```

## Completion Evidence

- TDD RED: 네 phase 모두 기존 generic summary를 반환해 4 cases FAIL
- TDD GREEN: 신규 mapping 4 cases PASS, Economic Cycle service 28 PASS
- focused regression: service/UI 56 PASS
- React production build: PASS
- actual Browser QA: desktop 한 줄, 420px 두 줄, hero/document overflow 0
- browser console warning/error: 0
- generated screenshot: `economic-cycle-phase-headline-context-qa.png`
