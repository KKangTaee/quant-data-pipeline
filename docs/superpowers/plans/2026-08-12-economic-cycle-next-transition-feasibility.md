# Economic Cycle Next-Transition Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 다음 국면 목적지와 전환 임박도 모델을 만들기 전에 PIT 전환 사건 표본이 최소 실험 조건을 충족하는지 재현 가능하게 판정한다.

**Architecture:** Runtime 경제사이클 코드는 그대로 두고, observed-state history를 입력받는 순수 feasibility 모듈을 추가한다. 모듈은 고정 순환 순서를 사용하지 않고 두 번 연속 관측으로 모든 destination 전환 사건을 추출한 뒤, 월별 행이 아닌 독립 사건 수로 gate를 판정한다.

**Tech Stack:** Python 3.12, dataclasses, pandas, pytest, existing economic-cycle PIT loader

## Global Constraints

- 고정 3·6개월 뒤 phase classification을 구현하지 않는다.
- 모든 destination phase를 비교하며 fixed adjacent order를 사용하지 않는다.
- unavailable 월은 confirmation streak를 끊는다.
- 표본 gate 실패 시 model fitting, DB schema, service payload와 React UI를 변경하지 않는다.
- `자산별 확인 포인트` 계산·payload·디자인을 변경하지 않는다.
- 기존 사용자 변경 파일과 generated artifact를 stage하지 않는다.

---

### Task 1: 다음 전환 사건 추출 계약

**Files:**
- Create: `finance/economic_cycle_transition_feasibility.py`
- Create: `tests/test_economic_cycle_transition_feasibility.py`

**Interfaces:**
- Consumes: `Sequence[ObservedStateResult]`
- Produces: `extract_confirmed_transition_events(history, confirmation_releases=2) -> tuple[ConfirmedTransitionEvent, ...]`

- [x] **Step 1: 비인접 전환과 두 번 연속 확인을 검증하는 failing test 작성**

```python
def test_extracts_any_destination_only_after_two_consecutive_releases():
    history = _history("contraction", "expansion", "expansion")
    events = extract_confirmed_transition_events(history)
    assert [(item.from_phase, item.to_phase) for item in events] == [
        ("contraction", "expansion")
    ]
```

- [x] **Step 2: 테스트가 import failure로 RED인지 확인**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_feasibility.py -q`
Expected: FAIL because module/function does not exist.

- [x] **Step 3: 순수 사건 추출 함수 최소 구현**

```python
@dataclass(frozen=True)
class ConfirmedTransitionEvent:
    from_phase: str
    to_phase: str
    candidate_started_at: str
    confirmed_at: str
    releases_to_confirmation: int

def extract_confirmed_transition_events(history, *, confirmation_releases=2):
    anchor = None
    candidate = None
    streak = 0
    events = []
    for item in history:
        state = item.observed_state
        phase = state.get("phase")
        if phase is None or state.get("data_status") == "UNAVAILABLE":
            candidate, streak = None, 0
            continue
        if anchor is None:
            anchor = phase
            continue
        if phase == anchor:
            candidate, streak = None, 0
            continue
        candidate, streak = (
            (candidate, streak + 1) if phase == candidate else (phase, 1)
        )
        if streak == confirmation_releases:
            events.append((anchor, candidate))
            anchor, candidate, streak = candidate, None, 0
    return tuple(events)
```

- [x] **Step 4: candidate reversal, unavailable gap, candidate switch 테스트 추가 후 GREEN 확인**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_feasibility.py -q`
Expected: PASS.

### Task 2: 독립 사건 기반 표본 gate

**Files:**
- Modify: `finance/economic_cycle_transition_feasibility.py`
- Modify: `tests/test_economic_cycle_transition_feasibility.py`

**Interfaces:**
- Consumes: observed-state history and extracted events
- Produces: `evaluate_transition_sample_feasibility(history, gate=DEFAULT_SAMPLE_GATE) -> TransitionFeasibilityReport`

- [x] **Step 1: 월별 행이 많아도 독립 사건이 부족하면 NO_GO인 failing test 작성**

```python
def test_sample_gate_counts_independent_events_not_repeated_monthly_origins():
    report = evaluate_transition_sample_feasibility(_long_single_episode_history())
    assert report.status == "NO_GO_DATA"
    assert "INSUFFICIENT_TRANSITION_EVENTS" in report.reason_codes
```

- [x] **Step 2: RED 확인**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_feasibility.py -q`
Expected: FAIL because evaluator does not exist.

- [x] **Step 3: literal gate와 report 구현**

```python
DEFAULT_SAMPLE_GATE = TransitionSampleGate(
    minimum_usable_origins=180,
    minimum_events=48,
    minimum_events_per_destination=8,
    minimum_events_per_origin=8,
    holdout_fraction=0.25,
    minimum_holdout_events=12,
    minimum_holdout_events_per_destination=2,
)
```

Report에는 usable 기간, phase별 월 수, 전체 사건, origin/destination/route별 사건,
chronological holdout support와 reason code를 포함한다.

- [x] **Step 4: 모든 gate 충족 fixture와 class/holdout 부족 fixture를 각각 검증**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_feasibility.py -q`
Expected: PASS.

### Task 3: 실제 PIT 데이터 feasibility 실행

**Files:**
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/CURRENT_PROJECT_AUDIT.md`
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/RECOMMENDATION.md`
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/RISKS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-next-transition-feasibility-v1-20260812/RUNS.md`

**Interfaces:**
- Consumes: `EconomicCyclePipelineLoader.prime_panel(2026-07-31)` and `build_observed_state_history(panel)`
- Produces: actual-data `TransitionFeasibilityReport`

- [x] **Step 1: 기존 PIT loader로 1959-01~2026-07 panel 재구성**

Run: `.venv/bin/python` audit command recorded in task `RUNS.md`.
Expected: 811 monthly origins with unavailable periods retained.

- [x] **Step 2: feasibility evaluator 실행과 결과 기록**

Expected current evidence: usable origins 148, confirmed events 32, destination support recovery 7 / expansion 9 / slowdown 5 / contraction 11; status `NO_GO_DATA`.

- [x] **Step 3: model/UI stop decision과 해결 가능한 데이터 공백을 research 문서에 기록**

공식 후보는 Philadelphia Fed RTDSM monthly vintage와 ADS real-time vintages다. 신규
provider ingestion은 별도 사용자 승인 범위로 분리한다.

### Task 4: 검증과 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-next-transition-feasibility-v1-20260812/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-next-transition-feasibility-v1-20260812/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-next-transition-feasibility-v1-20260812/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`

**Interfaces:**
- Consumes: focused test and actual-data report
- Produces: closed feasibility decision and next approval boundary

- [x] **Step 1: focused regression 실행**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_feasibility.py tests/test_economic_cycle_observed_state_v1.py tests/test_economic_cycle_observed_state_acceptance.py -q`
Expected: PASS.

- [x] **Step 2: 정적 검증 실행**

Run: `.venv/bin/python -m py_compile finance/economic_cycle_transition_feasibility.py`
Expected: exit 0.

Run: `git diff --check`
Expected: exit 0.

- [x] **Step 3: task 상태를 complete로 닫고 다음 결정을 RTDSM/ADS data expansion으로 기록**

Browser QA는 production UI를 변경하지 않았으므로 수행하지 않는다.

- [x] **Step 4: 경제사이클 관련 파일만 stage하고 coherent commit 생성**

```bash
git add finance/economic_cycle_transition_feasibility.py \
  tests/test_economic_cycle_transition_feasibility.py \
  docs/superpowers/specs/2026-08-11-economic-cycle-forecast-feasibility-design.md \
  docs/superpowers/plans/2026-08-12-economic-cycle-next-transition-feasibility.md \
  .aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit \
  .aiworkspace/note/finance/tasks/active/economic-cycle-next-transition-feasibility-v1-20260812 \
  .aiworkspace/note/finance/docs/ROADMAP.md
git commit -m "검증: 경제사이클 다음 전환 표본 gate 확정"
```
