# Practical Validation Level2 Decision Workspace V1 Design

## 이걸 하는 이유?

Final Review는 2026-07-16 개편으로 `이 포트폴리오를 계속 추적할 가치가 있는가?`라는 질문을 중심으로 저장된 행동 근거, 실제 강점과 약점, 포트폴리오 성격, Monitoring 변화 조건, 최종 판단을 하나의 화면에서 읽게 되었다.

반면 Practical Validation은 closure / Gate 계약이 강화됐음에도 사용자 화면은 여전히 다음 문제를 가진다.

- 후보 source, 프로필, replay, module, category, raw audit, provider action이 서로 다른 Streamlit container와 React iframe에 나뉜다.
- `REVIEW`가 측정된 주의, evidence 품질 제한, 자동으로 없앨 수 없는 한계, Final Review 판단 입력, 개발 필요 항목을 충분히 구분하지 못한다.
- `통과`와 `Final Review 판단에 반영할 한계 6건`을 함께 보여주지만 무엇이 해결됐고 무엇이 다음 단계로 넘어가는지 바로 읽히지 않는다.
- 실행 가능한 action이 0건이어도 데이터 action board와 empty group이 노출된다.
- PASS category도 `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치`를 반복해 결과보다 운영 설명이 길다.
- Level2는 흰색 각진 panel과 별도 iframe을 사용하고 Final Review는 blue-gray palette, rounded surface, soft shadow, compact typography의 one-shell을 사용한다.
- 문서는 Practical Validation을 4-flow와 5-flow로 다르게 설명하고, 실제 page는 저장 action을 Flow 3에 포함한 4개 visible flow를 렌더링한다.

현재 문제는 검증 엔진이 동작하지 않는 장애가 아니다. focused service / boundary 회귀 66개는 통과한다. 문제는 정상 contract를 사용자가 읽고 행동할 수 있는 제품 언어와 한 화면 흐름으로 투영하지 못한 것이다.

## Approved Product Goal

Practical Validation의 중심 질문을 다음으로 고정한다.

> 이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?

사용자는 한 화면에서 다음을 끝낼 수 있어야 한다.

1. 어떤 후보와 검증 기준을 사용하는지 확인한다.
2. 최신 저장 데이터 기준으로 replay를 실행한다.
3. 검증된 사실, 지금 해결할 일, 개발이 필요한 일, Final Review로 넘길 한계와 판단 입력을 구분한다.
4. 현재 결과를 기록하거나 저장 후 Final Review로 이동한다.

완료 기준은 raw `PASS` 개수나 `REVIEW` 0개가 아니다.

- current Final Review eligible 후보의 unresolved actionable / critical engineering / missing contract가 0이다.
- 사용자는 Level2에서 해야 할 일과 Final Review로 넘길 일을 혼동하지 않는다.
- 하나의 root issue는 first-read, action, Gate에서 한 번만 보인다.
- 실행 handler가 없는 항목에는 CTA가 없다.
- React는 presentation과 intent만 담당하고 Python이 source selection, profile, replay, classification, applicability, Gate, collection, persistence를 소유한다.

## 2026-07-16 Approved Correction Amendment

초기 one-shell 구현을 실제 화면에서 확인한 결과, 시각 구조뿐 아니라 stage
ownership과 재검증 상호작용에 추가 보정이 필요하다는 사용자 승인을 받았다.
이 amendment는 아래 항목에서 기존 delivery / completion 조건을 대체한다.

### Candidate And Validation Policy Separation

Step 1은 하나의 선택 grid가 아니라 두 개의 명확한 의사결정으로 나눈다.

1. `1A. 검증할 후보 선택`
2. 선택 후보의 유형 / 기간 / 구성 요약
3. `1B. 어떤 관점으로 검증할까요?`
4. 검증 프로필 선택

검증 프로필은 포트폴리오 설계안이 아니라 Level2 판정 정책이다. 후보와 같은
카드 문법을 사용하지 않으며, 선택된 항목은 `disabled` opacity가 아니라
active selection으로 표시한다. `selection_source` 같은 내부 fallback 문자열은
first-read에서 노출하지 않고 `혼합 포트폴리오`, `단일 전략 실행` 같은 Python
소유 표시 이름을 제공한다.

### Fragment-Scoped Revalidation

현재 React intent는 Streamlit app rerun을 발생시키고, Python replay 실행 뒤
다시 `st.rerun()`을 호출한다. workspace read model이 intent 소비 전에
만들어지기 때문에 전체 탭이 두 번 재구성되는 것이 화면 reset의 원인이다.

Practical Validation one-shell과 그 결과 영역은 `st.fragment` 안에서 렌더링한다.
후보 / profile / replay / Level2 resolution action은 fragment 범위에서 다시
그리며, 실제 Final Review route 이동만 app 범위 rerun을 사용한다. React는
상단 선택 context를 유지하고 replay가 진행되는 동안 Step 2 이하에만 pending
상태를 표시한다.

### Level2-Owned Caution Contract

`pv_data_caution`과 `pv_practical_caution`은 Practical Validation 소유다. 이
role의 non-PASS module을 generic `accepted_limit`로 변환해 Final Review로
넘기지 않는다.

| resolution_class | 의미 | owner / terminal | Gate |
|---|---|---|---|
| `validated_caution` | 실제 계산 또는 관측 근거가 있고 Level2에서 주의로 결론냄 | Practical Validation / `resolved` | 통과 |
| `resolve_now` | 등록된 Python handler와 재검증으로 닫을 수 있음 | Practical Validation / `open` | 해결 전 차단 |
| `engineering_required` | required evidence, adapter, validator가 없음 | Development / `deferred` | critical 차단 |
| `accepted_limit` | 적용 범위와 구조적 한계 근거가 명시된 비핵심 한계 | Final Review / `open` | handoff |
| `final_decision` | 세금·계좌·최종 선택처럼 사용자 판단이 필요 | Final Review / `open` | handoff |
| `monitoring_transfer` | 선정 후 변화 조건으로 추적 | Monitoring / `open` | handoff |

규칙:

1. `REVIEW`라는 raw status만으로 `validated_caution`을 만들지 않는다.
2. audit row에 실제 계산 / 관측 결과가 있고 `NOT_RUN`, `NEEDS_INPUT`,
   `BLOCKED`가 아니어야 Level2 종결이 가능하다.
3. required validation이 없거나 실행되지 않았으면 `engineering_required`다.
4. `accepted_limit`는 explicit applicability와 evidence가 있는 경우만 사용한다.
5. Level2에서 종결된 `validated_caution`은 Final Review handoff lane이나
   handoff count에 다시 포함하지 않는다.
6. current Final Review eligible은 unresolved actionable, critical engineering,
   missing contract가 모두 0이어야 한다.

### User Explanation Contract

raw `Criteria`, 함수 경로, `key=value` evidence는 first-read 설명이 아니다.
새 pure explanation service가 audit row를 다음 계약으로 변환한다.

```text
display_title
status_label
what_was_checked
result_summary
meaning
next_action
evidence_state
stage_owner
technical_trace
```

사용자 설명은 `무엇을 확인했나 -> 현재 결과 -> 이 의미는 -> 다음 행동` 순서로
읽힌다. raw 기술 정보는 `계산 근거` disclosure 안에만 둔다. 상태 표시는
`충분`, `검증 완료·주의 필요`, `자료 보강 필요`, `아직 검증하지 못함`,
`해당 없음`, `이동 차단`으로 정규화한다.

### Detailed Evidence Information Architecture

`상세 검증 근거`는 모든 category를 긴 목록으로 동시에 펼치지 않는다.

- `데이터·시점`
- `검증 방법`
- `구성·위험`
- `실전 운용`
- `조건부 검증`

각 category는 `충분 / 주의 / 보강` count를 제공하고 한 번에 선택한 category만
표시한다. unresolved item이 있으면 해당 category를 기본 선택한다. action이
0건이면 빈 action board를 렌더링하지 않는다.

## Current Evidence

### Current GRS

최신 저장 GRS validation은 다음 상태다.

- latest replay / period coverage: PASS
- Final Review 이동: 가능
- unresolved actionable: 0
- critical engineering: 0
- missing contract: 0
- accepted limit: 6
- final decision input: 1

그러나 현재 Flow 3은 전체 결과를 `통과`로 표시하고 accepted limit 6건만 보조 count로 보여준다. `tax_account_scope` 같은 final decision input 1건은 같은 first-read summary에서 빠진다.

### Current Visual Contract

`app/web/backtest_practical_validation/components.py`와 두 Practical Validation React component는 `border-radius: 0`, no-shadow, white square surface를 사용한다. `tests/test_backtest_refactor_boundaries.py`도 이 모양을 명시적으로 고정한다.

Final Review는 `app/web/components/final_review_investment_report/frontend/src/style.css`에서 다음 visual hierarchy를 사용한다.

- outer workspace: 20px radius
- primary decision / chart surface: 17px radius
- compact summary / control: 14px radius
- ink: `#152033`
- blue-gray line / muted palette
- soft shadow: `0 10px 30px rgba(33, 53, 72, .055)`
- 760px에서 single-column responsive layout

따라서 현재 차이는 브라우저나 일부 CSS 누락이 아니라 오래된 Level2 product contract다.

## Considered Approaches

### A. Style-Only Correction

현재 Flow 1~4와 두 React component를 유지하고 radius, shadow, color token만 Final Review와 맞춘다.

- 장점: 변경량과 회귀 위험이 작다.
- 단점: REVIEW 의미 혼합, 빈 action board, 중복 category card, 4/5-flow drift, 다음 행동 불명확성이 그대로 남는다.
- 결정: 채택하지 않는다.

### B. Hybrid One-Shell Decision Workspace

Python이 현재 source / profile / replay / closure / category / action / Gate를 하나의 read model로 만들고 React가 4단계 workspace를 표시하며 intent만 반환한다. advanced profile, raw evidence, source JSON 같은 검산용 상세는 Streamlit disclosure와 fallback에 남긴다.

- 장점: Level3 시각 언어와 질문 중심 흐름을 맞추면서 기존 Python 실행·저장 경계를 보존한다.
- 장점: 현재 두 React iframe을 하나로 합치고 empty action surface를 제거할 수 있다.
- 장점: full React form migration 없이 source/profile/replay intent를 한 shell에서 연결할 수 있다.
- 단점: 새 Python projection과 React component, intent dispatcher, compatibility fallback이 필요하다.
- 결정: 채택한다.

### C. Full React Migration

후보 상세, custom profile 질문, replay mode, provider collection, raw evidence table까지 전부 React로 옮긴다.

- 장점: 시각적 일관성이 가장 높다.
- 단점: Streamlit session / form / rerun / provider action을 대규모로 다시 연결해야 하며 이번 목표보다 범위가 크다.
- 결정: 채택하지 않는다.

## Target User Flow

visible flow는 아래 4단계로 통일한다.

```text
1. 후보와 검증 기준 확인
2. 최신 데이터 기준 재검증
3. 결과 해석과 해결 구분
4. 저장하고 Final Review로 이동
```

데이터 보강이 필요한 경우만 recovery loop를 연다.

```text
3. 지금 해결할 항목
  -> Python action 실행
  -> current replay 무효화
  -> 2. 최신 데이터 기준 재검증
  -> 새 결과
```

`검증 기준 상세`는 별도 5번째 flow가 아니다. Step 3의 progressive disclosure이며 first-read 결론을 검산하는 위치다.

## Finding Semantics

기존 raw status와 closure resolution class를 대체하지 않고, 사용자 표시용 `finding_kind`를 Python projection에서 추가한다.

| finding_kind | 의미 | first-read 위치 | Gate |
|---|---|---|---|
| `verified` | 기준을 충족하거나 재현된 사실 | `검증된 내용` | 통과 |
| `measured_caution` | observation과 comparator / threshold가 있는 주의 | `주의해서 볼 결과` | policy에 따라 통과 또는 차단 |
| `validated_caution` | 실제 evidence가 있고 Level2에서 종결한 주의 | `Level2 검증 주의` | 통과 |
| `resolve_now` | 현재 Python handler와 재검증으로 닫을 수 있음 | `지금 해야 할 일` | 해결 전 차단 |
| `engineering_required` | runtime / provider / adapter / validator 개발 필요 | `개발 후 재검토` | critical이면 차단 |
| `accepted_limit` | 자동으로 없앨 수 없는 비핵심 한계 | `Final Review로 넘길 것` | 명시적 허용 |
| `final_decision` | 계좌·세금·선택 사유처럼 사람이 결정 | `Final Review로 넘길 것` | handoff input |
| `monitoring_transfer` | 선정 뒤 변화 조건으로 추적 | `Final Review로 넘길 것` | handoff input |
| `not_applicable` | 후보 특성에 적용되지 않음 | 상세 disclosure | Gate 제외 |

규칙:

1. non-PASS root issue는 `evidence_closure.issues`의 `resolution_class`, `criticality`, `gate_effect`, `actionable_now`, `action_id`, `terminal_state`를 우선 사용한다.
2. PASS / READY module 또는 evidence row는 `verified`로 투영한다.
3. explicit observation과 comparator / threshold가 있고 blocker가 아닌 경우만 `measured_caution`을 만든다.
4. module label이나 raw `REVIEW`만으로 `accepted_limit`, `validated_caution`,
   `resolve_now`를 추정하지 않는다.
5. 동일 `root_issue_id`는 lane과 count에서 한 번만 반영하고 derived checks는 disclosure에 보존한다.

## Applicability And Truth Corrections

### Single-Component Construction

단일 전략 후보의 component weight 100%는 mix concentration이나 underlying holdings concentration의 증거가 아니다.

- single component에서 mix 전용 concentration row는 `NOT_APPLICABLE`로 낮춘다.
- ETF / fund look-through가 있는 경우 underlying holdings concentration은 별도 measured evidence로 유지한다.
- weighted mix의 component concentration은 기존 conditional core를 유지한다.

### Provider Evidence

provider module 전체를 generic `근거 부족`으로 표시하지 않는다.

- coverage가 충분하고 liquidity/capacity source만 proxy이면 실제 관측 근거가
  있는 Level2 `validated_caution`으로 종결한다. 적용 범위와 구조적 한계
  근거가 별도로 명시된 경우에만 `accepted_limit`를 사용한다.
- ETF-like 후보의 required holdings / exposure / operability gap은 실제 Python collection handler가 있을 때만 `resolve_now`다.
- non-ETF source에는 provider freshness를 core blocker로 승격하지 않는다.

### Validation Method Strength

walk-forward window, OOS holdout, regime split처럼 실제 계산된 evidence가 있으면 그 값을 먼저 표시한다.

- 일부 방법론이 없다는 이유로 전체 method strength를 `근거 없음`으로 축약하지 않는다.
- 계산된 evidence와 없는 evidence를 분리한다.
- 계산된 method evidence의 취약 결과는 `validated_caution`으로 종결한다.
- required method evidence가 누락되거나 `NOT_RUN`이면 profile과 무관하게
  engineering gap으로 분류하고, conditional method만 profile applicability를
  적용한다.

### Static / Dynamic Universe

- static manual universe의 사후 선택 가능성은 accepted limit로 설명할 수 있다.
- dynamic historical universe의 PIT membership / delisting 근거 부족은 `engineering_required + critical` blocker다.
- 두 경우 모두 generic data action으로 합치지 않는다.

## Python Read Model

새 pure service를 추가한다.

```text
app/services/backtest_practical_validation_decision_workspace.py
```

primary interface:

```python
def build_practical_validation_decision_workspace(
    *,
    source: dict[str, Any],
    validation_profile: dict[str, Any],
    replay_result: dict[str, Any] | None,
    validation_result: dict[str, Any] | None,
    source_options: list[dict[str, Any]],
) -> dict[str, Any]:
    ...
```

schema:

```text
schema_version = practical_validation_decision_workspace_v1
state
header
candidate_selector
profile
replay
verdict
summary
verified_findings[]
measured_cautions[]
resolution_lanes
category_disclosures[]
actions
boundaries
```

### state

| state | 의미 |
|---|---|
| `source_required` | 선택 가능한 source가 없음 |
| `replay_required` | source/profile은 준비됐지만 current-session replay가 없음 |
| `resolution_required` | resolve_now 또는 critical engineering blocker가 있음 |
| `ready_with_handoff` | action blocker는 없고 accepted limit / final decision / monitoring transfer가 있음 |
| `ready` | action blocker와 handoff limitation이 없음 |

### summary

first-read count는 raw module count가 아니라 사용자 행동 기준이다.

```text
verified_count
measured_caution_count
resolve_now_count
engineering_blocker_count
accepted_limit_count
final_decision_count
monitoring_transfer_count
```

current GRS는 Level2-owned caution 보정 전에는 다음처럼 읽혔다.

```text
Final Review 이동 가능
지금 해결 0
개발 차단 0
인수할 한계 6
최종 판단 1
```

보정 후에는 실제 계산 / 관측된 Practical Validation caution을
`validated_caution`으로 종결하고, explicit accepted limit와 Final Review
decision input만 handoff count에 남긴다. 정확한 count는 current append-only
row를 새 contract로 read-only 재투영해 QA 시 기록한다.

### category_disclosures

기존 `visible_criteria_detail_groups`를 버리지 않는다. 새 read model은 category별로 다음만 first-level disclosure에 제공한다.

```text
category_id
title
question
outcome
verified_items[]
root_issue_ids[]
technical_rows[]
```

PASS category에는 `추가 조치 없음` card를 만들지 않는다. verified item과 technical rows만 접힌 상세에 둔다.

## React Workspace

새 component path를 사용한다.

```text
app/web/components/practical_validation_decision_workspace/
```

기존 `practical_validation_fix_queue`와 `practical_validation_data_action_board`는 active render path에서 제거하되, migration 기간 동안 import compatibility와 Streamlit fallback 검증을 위해 즉시 삭제하지 않는다.

React reading order:

1. 질문 중심 header
2. candidate / profile / replay basis
3. verdict hero
4. `검증된 내용`
5. `지금 해야 할 일`
6. `Final Review로 넘길 것`
7. save / move action
8. category / source / technical disclosure 안내

visual token은 Final Review Decision Workspace를 따른다.

- 20 / 17 / 14px radius hierarchy
- `#152033` ink
- blue-gray line / muted palette
- green / orange / red는 outcome 의미에만 사용
- soft shadow
- 760px single-column
- 긴 root id / source id / evidence text는 wrap 또는 disclosure로 낮춤

React가 반환할 수 있는 intent:

```text
select_source
select_profile_preset
run_replay
run_resolution_action
save_audit_only
save_and_move
```

intent 공통 필드:

```text
action
intent_id
selection_source_id
validation_result_id
```

`run_resolution_action`은 추가로 `root_issue_id`, `action_id`를 보낸다.

React는 다음을 하지 않는다.

- raw status를 finding_kind로 분류
- root dedup
- applicability 계산
- handler 존재 여부 추정
- Gate 계산
- provider / DB fetch
- replay
- registry append

## Python Intent Handling

`app/web/backtest_practical_validation/page.py`가 intent를 소비한다.

- `select_source`: source id가 현재 option에 있는지 확인하고 session source를 변경한 뒤 replay state를 지운다.
- `select_profile_preset`: 허용된 preset인지 확인하고 Python profile state를 변경한다.
- `run_replay`: 기존 `_render_actual_replay_panel`의 실행 service 경계를 재사용한다.
- `run_resolution_action`: current workspace의 동일 root issue / action id인지 재확인하고 `has_action_handler(action_id)`와 Python dispatcher를 통과한 경우만 실행한다.
- `save_audit_only` / `save_and_move`: 기존 `_consume_practical_validation_next_stage_action`과 current-session replay guard를 유지한다.

custom profile 질문과 advanced replay mode는 첫 구현에서 Streamlit disclosure로 유지한다. 기본 workspace는 preset과 latest replay를 primary path로 사용한다.

## Streamlit Fallback And Detailed Evidence

React build가 없거나 payload error가 있으면 Python fallback이 같은 순서와 같은 count를 표시한다.

fallback도 다음 원칙을 지킨다.

- raw module inventory를 first-read에 표시하지 않는다.
- action 0건이면 action board를 렌더링하지 않는다.
- accepted limit와 final decision count를 분리한다.
- technical detail은 expander 안에 둔다.

Flow 1의 source curve / selection history / raw source table과 기존 Flow 4 evidence tabs는 `상세 검증 근거` disclosure 아래로 이동한다.

## Error Handling

- validation result에 closure가 없으면 current result를 다시 build하고, required closure contract가 여전히 없으면 `missing_contract` blocker로 표시한다.
- `actionable_now=true`인데 handler가 없으면 `engineering_required` contract error로 바꾸고 CTA를 만들지 않는다.
- React intent의 source id / validation id / root issue id가 current workspace와 다르면 무시하고 사용자에게 stale action 안내를 표시한다.
- resolution action 성공 또는 부분 실패 뒤에는 current replay를 항상 초기화한다.
- replay가 끝나지 않았으면 result / save section을 ready로 표시하지 않는다.
- current source의 최신 validation이 blocking이면 과거 eligible row로 fallback하지 않는다.

## File Ownership

| 책임 | 파일 |
|---|---|
| finding projection / user flow read model | 새 `app/services/backtest_practical_validation_decision_workspace.py` |
| root closure / action handler truth | `app/services/backtest_evidence_closure.py` |
| construction / provider / method applicability | `app/services/backtest_construction_risk_audit.py`, `app/services/backtest_practical_validation_modules.py`, `app/services/backtest_validation_efficacy.py`, `app/services/backtest_data_coverage_audit.py` |
| legacy workspace compatibility / technical groups | `app/services/backtest_practical_validation_workspace.py` |
| page state / replay / collection / save intent | `app/web/backtest_practical_validation/page.py` |
| Streamlit fallback | `app/web/backtest_practical_validation/workspace_panel.py`, `components.py` |
| Level2 one-shell presentation | 새 `app/web/components/practical_validation_decision_workspace/` |
| focused service contract | 새 `tests/test_backtest_practical_validation_decision_workspace.py` |
| page / UI boundary | `tests/test_backtest_refactor_boundaries.py` |
| existing cross-stage regression | `tests/test_backtest_evidence_closure.py`, relevant `tests/test_service_contracts.py` classes |

`app/services/backtest_practical_validation_decision_workspace.py`는 closure와 legacy workspace를 소비한다. audit / module producer가 새 read model을 import하지 않도록 단방향 의존성을 유지한다.

## Delivery Slices

아래 기존 1~4차는 initial one-shell 구현 이력이다. 사용자 실화면 확인 후
승인된 correction delivery는 `PLAN.md`의 Task 5~9가 소유하며, 기존 4차
closeout보다 우선한다.

### 1차: Validation Truth / Finding Contract

- finding_kind projection 기준
- single-component construction applicability
- provider evidence copy / severity
- method evidence actual / missing 분리
- root issue dedup and current GRS fixture

완료 조건:

- current GRS가 `지금 해결 0 / 개발 차단 0 / 인수 한계 6 / 최종 판단 1`로 투영된다.
- single component 100%가 underlying concentration weakness로 표시되지 않는다.
- handler 없는 item은 CTA를 만들지 않는다.

### 2차: Level2 Decision Workspace Read Model

- 새 pure service와 state machine
- candidate / profile / replay basis
- verdict / verified / resolution / handoff lanes
- category disclosure projection
- save / move action contract

완료 조건:

- replay 전, resolution 필요, handoff 포함 ready, clean ready 상태가 fixture로 분리된다.
- action 0건이면 action lane이 hidden이다.
- closure final decision item이 accepted limit와 별도 count로 보인다.

### 3차: One-Shell UI / Intent Integration

- new React component
- Final Review visual token 적용
- source / preset / replay / resolution / save intent bridge
- old Fix Queue / Data Action Board active render 제거
- Streamlit fallback / advanced disclosure 유지

완료 조건:

- desktop과 760px에서 4단계 흐름이 한 shell로 읽힌다.
- Python-only classification / action / save boundary test가 통과한다.
- separate empty action iframe이 나타나지 않는다.

### 4차: QA / Docs / Closeout

- current GRS runtime fixture / Browser QA
- focused service / closure / boundary regression
- React production build
- target py_compile
- `git diff --check`
- 4/5-flow 문서 drift 수정
- active task / root handoff sync

완료 조건:

- desktop / 760px에서 overflow와 clipped copy가 없다.
- replay / action / save guard는 기존 contract를 유지한다.
- protected registry, run history, saved JSONL, generated screenshot을 commit하지 않는다.

## Non-Goals

- historical universe / delisting provider 신규 도입
- DB schema 변경
- strategy runtime 또는 backtest calculation 재설계
- Final Review 판단 route 변경
- Final Review에서 provider fetch / replay 실행
- live approval, broker order, account sync, auto rebalance
- 기존 registry / saved JSONL row rewrite 또는 삭제
- 모든 raw evidence table의 React migration

## Acceptance Criteria

1. 사용자가 첫 화면에서 Final Review 이동 가능 여부와 이유를 한 문장으로 이해한다.
2. `통과`라는 문구가 accepted limit / final decision handoff를 숨기지 않는다.
3. 지금 해결, 개발 후 재검토, 인수할 한계, 최종 판단 입력이 서로 다른 lane으로 보인다.
4. current Final Review eligible 후보의 unresolved actionable / critical engineering / missing contract가 0임을 표시한다.
5. action handler가 없는 issue에 CTA가 없다.
6. 동일 root issue는 first-read와 action count에서 한 번만 보인다.
7. single component / ETF-like / weighted mix / static universe / dynamic universe applicability가 구분된다.
8. action이 0건이면 데이터 action surface를 렌더링하지 않는다.
9. React는 intent만 반환하고 Python이 validation / Gate / action / save를 소유한다.
10. Level2가 Final Review와 동일한 visual language를 사용하되 검증과 판단의 stage 역할을 섞지 않는다.
11. 후보 선택과 검증 정책 선택이 별도 subsection으로 읽힌다.
12. 최신 재검증은 상단 context를 유지하고 workspace fragment만 갱신한다.
13. `pv_data_caution` / `pv_practical_caution`은 근거가 있을 때 Level2에서
    종결되고, 근거가 없으면 Final Review가 아니라 engineering blocker가 된다.
14. first-read와 상세 근거에 raw 함수 경로나 해석되지 않은 `key=value`
    문자열이 사용자 설명으로 노출되지 않는다.

## Approved Provider And Final Review Handoff Correction

2026-07-17 사용자 실화면 확인에서 ETF provider 수집 차단과 Final Review
handoff 소비 불일치가 확인됐다. 기존 수집 job과 snapshot schema는 유지하고
provider normalization과 cross-stage read model만 보강한다.

### Provider collection boundary

- COMT, EFA, LQD, TIP의 공식 iShares download는 기존 CSV endpoint가 아니라
  SpreadsheetML 형식의 fund workbook을 반환한다.
- VNQ는 Vanguard 공식 `portfolio-holding/stock.json`을 통해 normalized holdings를
  제공하지만 현재 source discovery와 parser가 없다.
- 새 DB table이나 별도 ingestion job을 만들지 않는다.
- `etf_provider_source_map -> etf_holdings_snapshot -> etf_exposure_snapshot` 경로와
  Practical Validation의 기존 provider collection handler를 재사용한다.
- provider payload parser는 source verification과 collection 양쪽에서 동일 계약을
  사용하고, malformed/empty payload는 verified로 승격하지 않는다.

### Final Review handoff boundary

Level2 closure의 세 handoff class를 Final Review가 root issue 기준으로 직접 소비한다.

- `final_decision`: route 선택 전에 사용자가 선택/보류 사유에 반영할 판단 입력
- `accepted_limit`: Level2에서 근거를 확인하고 인수한 제한으로, Final Review의
  추가 수리 항목이 아니라 confidence disclosure
- `monitoring_transfer`: observation, threshold, cadence, re-review action, evidence
  reference가 모두 있는 경우에만 구조화된 Monitoring 조건

Final Review eligibility가 막힌 동안 Level2에는 이들을 실제 승격으로 표현하지 않고
`검증 통과 후 Final Review에서 확인할 항목`으로 표시한다. eligible validation을
저장한 뒤에는 Final Review 본문에서 `최종 판단 입력 / 인수한 검증 한계 /
Monitoring 조건`으로 분리한다. 동일 root issue는 한 section과 count에 한 번만
반영한다.

### File ownership extension

| 책임 | 파일 |
|---|---|
| iShares SpreadsheetML / Vanguard JSON parser와 source discovery | `finance/data/etf_provider.py` |
| provider parser / discovery / collection regression | `tests/test_service_contracts.py` 또는 focused provider test |
| Final Review handoff projection | `app/services/backtest_final_review_decision_brief.py` |
| Level2 prospective/eligible handoff copy | `app/services/backtest_practical_validation_decision_workspace.py` |
| Final Review React presentation | `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`, `decisionBriefTypes.ts`, `style.css` |
| Python fallback | `app/web/backtest_final_review/page.py` |

### Additional acceptance criteria

15. COMT, EFA, LQD, TIP workbook payload와 VNQ JSON payload가 기존 normalized
    holdings row로 변환된다.
16. source discovery가 iShares workbook과 Vanguard JSON을 verified candidate로
    만들 수 있다.
17. 다섯 종목 수집 뒤 holdings/exposure consumer가 동일 snapshot schema를 읽는다.
18. Final Review 본문에서 final decision, accepted limit, monitoring transfer가 서로
    다른 의미와 행동으로 보인다.
19. 구조화 근거가 부족한 REVIEW는 Final Review handoff로 승격되지 않고 Level2
    engineering blocker로 남는다.
20. blocked workspace는 prospective handoff를 실제 승격처럼 표현하지 않는다.

## 2026-07-17 Approved Atomic Revalidation And Actionable Handoff Correction

사용자 실화면 재검증에서 완료 notice가 나타나는 동안 Level2 one-shell 전체가
사라지고 advanced disclosure만 남는 회귀를 재현했다. 또한 기존 Final Review
handoff는 세 lane을 읽을 수 있게 만들었지만 `accepted_limit`을 사용자가 실제로
인수했는지 또는 Level2로 되돌렸는지를 기록하지 않아, 인계가 설명에서 끝났다.

### Atomic revalidation boundary

custom component의 `Streamlit.setComponentValue()`가 fragment rerun을 시작한 뒤
Python intent consumer가 다시 `st.rerun(scope="fragment")`을 호출한다. 이 두 번째
rerun이 이미 그린 component delta를 중단하고 one-shell iframe을 다시 mount하게
만드는 직접 원인이다.

Practical Validation component wrapper는 Streamlit 1.57의 `on_change` callback을
지원한다. callback은 component key의 current intent를 읽고 source / validation
identity를 Python에서 검증한 뒤 local intent를 projection 전에 소비한다.

- source / profile / replay / Level2 resolution은 callback에서 처리하며 별도
  fragment rerun을 호출하지 않는다.
- widget event가 시작한 한 번의 fragment rerun 본문이 최신 session state로
  workspace model을 만들고 같은 component key에 전달한다.
- Final Review route 이동은 기존 app rerun을 유지한다.
- 성공 notice는 one-shell 밖의 독립 block으로 남겨 component mount 순서를
  흔들지 않고, React Step 2에 완료 상태를 함께 표시한다.
- 후보 / 검증 기준과 기존 Step 3~4 결과는 replay 계산 중에도 유지한다.

### Compact Level2 handoff

Level2 first-read는 Final Review의 세 lane 상세를 반복하지 않는다. eligible
workspace에서는 `Final Review 인계 준비 완료` summary 아래에 root issue별 한 줄
요약만 표시한다.

- `final_decision`: `Final Review에서 결정`
- `accepted_limit`: `한계 인수 판단`
- `monitoring_transfer`: `Monitoring 자동 이관`

각 항목은 Level2에서 확인된 근거의 의미와 다음 stage action만 보여준다. 상세
관측값과 evidence ref는 `상세 검증 근거` 또는 Final Review에서 확인한다. blocked
workspace는 기존처럼 prospective copy를 사용하며 실제 승격으로 표현하지 않는다.

### Actionable Final Review handoff

Final Review는 eligible Level2 handoff를 다음처럼 완료한다.

1. `final_decision`은 최종 route 사유에 반영할 판단 질문으로 표시한다.
2. `accepted_limit`은 root issue마다 `accepted` 또는 `return_to_level2`를 반드시
   선택한다.
3. 하나라도 `return_to_level2`이면 저장 route는 `RE_REVIEW_REQUIRED`여야 한다.
4. `monitoring_transfer`는 observation / threshold / cadence / re-review action /
   evidence reference가 모두 있는 구조화 조건만 자동 이관한다.
5. Final Review React는 입력 intent만 만들고 Python이 expected root set, 중복,
   허용값, route consistency를 검증한다.
6. 검증된 acknowledgement는 append-only final decision row의
   `decision_brief_snapshot.accepted_limit_acknowledgements`에 저장한다.

빈 handoff lane은 렌더링하지 않는다. 기존 route 값, eligibility Gate, append-only
persistence, live-approval 금지 경계는 변경하지 않는다.

### Additional acceptance criteria

21. replay click 뒤 후보 / 검증 기준 / 기존 결과 component가 DOM에서 사라지지 않는다.
22. replay event 한 건은 Python local intent 한 번과 fragment projection 한 번으로
    끝나며 explicit fragment rerun을 추가로 호출하지 않는다.
23. Level2 handoff는 compact summary이며 Final Review 상세 lane을 복제하지 않는다.
24. accepted limit가 있으면 Final Review 저장 전에 모든 root issue의 인수 또는
    Level2 반환 선택이 필요하다.
25. `return_to_level2` acknowledgement는 `RE_REVIEW_REQUIRED` route와만 저장된다.
26. 저장 row는 accepted-limit acknowledgement와 Monitoring condition snapshot을
    보존한다.
27. React 미가용 fallback도 동일한 선택과 Python 검증 계약을 사용한다.
28. desktop / 760px에서 handoff action과 replay pending 상태가 overflow 없이 읽힌다.
