# Final Review Decision Workspace Design

Status: Approved by user for implementation planning
Last Updated: 2026-07-16

## One-Line Recommendation

Final Review를 validation contract inspector에서 `이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가`에 답하는 React-first Decision Workspace로 재설계한다.

## Why This Direction

현재 Gate, root dedup, terminal state, append-only persistence 계약은 안전하다. 문제는 이 계약의 중간 상태를 총평, 점수, closure, 저장 전 질문, Monitoring guide, 상세 탭으로 모두 노출해 사용자가 포트폴리오보다 workflow schema를 읽게 만든다는 점이다.

새 설계는 correctness 계약을 버리지 않는다. Python이 저장된 evidence를 Final Review 전용 decision projection으로 압축하고, React는 그 projection을 한 가지 질문과 한 가지 판단 흐름으로 표현한다.

## Product Decision

Primary question:

> 이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가?

Final Review가 끝내는 일:

- 후보의 투자 thesis와 가장 큰 trade-off를 이해한다.
- 성과 경로, 손실 행동, 구성/실행 현실성을 직접 관측값으로 확인한다.
- 계속 추적할 조건을 2~4개의 Monitoring trigger로 확정한다.
- 계속 추적, 관찰 후 재검토, 제외, Level2 재검토 중 하나를 이유와 함께 저장한다.

Final Review가 하지 않는 일:

- live investment approval, broker order, account sync, auto rebalance
- current market timing 또는 account-specific allocation 결정
- provider fetch, replay, DB ingestion, Level2 validation 실행
- historical universe / delisting 신규 provider 보강

## Chosen Approach

선택안은 `Decision Brief + Evidence Disclosure`다.

승인한 A안은 이 정보 순서와 함께 `Workspace > Overview > 시장 맥락`의 visual language를 채택한다. React workbench는 blue-gray palette, rounded panel, soft shadow, compact type hierarchy를 사용하고, 각진 green editorial report나 12-column magazine layout으로 해석하지 않는다.

검토한 대안:

- 3단계 wizard: 순서는 분명하지만 근거를 앞뒤로 다시 보기 어렵고 양식 작성처럼 느껴진다.
- 현재 report 축소: 구현 부담은 작지만 strength/weakness 의미와 Streamlit/React 이중 구조가 남는다.

Decision Brief는 다음 순서를 고정한다.

1. 추적 가치 결론
2. 포트폴리오 행동 근거
3. 진짜 강점과 약점
4. Monitoring 변화 조건
5. 최종 판단과 사유
6. 접힌 evidence confidence / accepted limits / provenance

## Content Semantics

### Verdict And Thesis

- verdict는 `계속 추적할 가치 있음`, `관찰 후 재검토`, `추적 가치 낮음`, `Level2 재검토 필요` 중 하나다.
- thesis는 strongest observation과 largest trade-off를 한 문단에 함께 담는다.
- Gate pass, readiness, registry count는 thesis의 강점이 될 수 없다.

### Portfolio Behavior Board

주 visual:

- 동일 기간, 동일 frequency의 cumulative net performance와 benchmark
- underwater drawdown과 recovery path

보조 observation:

- concentration / maximum component weight
- turnover
- modeled cost
- liquidity freshness 또는 capacity evidence
- stress / regime observation

chart series가 없으면 빈 illustrative chart를 만들거나 lane을 조용히 숨기지 않는다. 해당 위치에 `미측정` 상태와 누락 이유를 표시하고 disclosure에 source gap을 남긴다.

### Strengths And Weaknesses

strength/weakness item은 다음 필드를 가진다.

- `root_issue_id` 또는 stable observation id
- `title`
- `interpretation`
- `measured_value`
- `threshold_or_comparator`
- `evidence_refs`
- `as_of`

생성 규칙:

- high score, Gate pass, readiness row를 strength로 사용하지 않는다.
- critical gap, must-review label을 portfolio weakness로 그대로 바꾸지 않는다.
- 같은 observation은 strength, weakness, trigger 중 한 primary role만 가진다.
- 관측값 없이 서술형 장단점을 생성하지 않는다.

### Portfolio Trait Map

성격 지도는 보조 visual이다.

- axis는 집중 위험, 낙폭 압력, 회전 부담, 비용 부담, 국면 의존처럼 관측 가능한 exposure/pressure를 표현한다.
- 바깥쪽은 더 좋다는 뜻이 아니다.
- measured observation과 interpretation threshold가 모두 있을 때만 normalization한다.
- `trait_map.axes`는 모든 승인 axis의 `status`를 전달한다. 누락 axis는 `normalized_value=null`, `status=unmeasured`이며 React는 polygon을 해당 axis까지 연결하지 않는다.
- composite score, average score, ranking을 만들지 않는다.

### Score Policy

- overall investment score를 제거한다.
- `투자 매력도 / 근거 신뢰도 / Monitoring 준비도` headline score 3종을 제거한다.
- evidence confidence 하나만 secondary metadata로 허용한다.
- evidence confidence는 결론의 신뢰도를 설명할 뿐 strength, weakness, trait axis, route를 직접 결정하지 않는다.

### Monitoring Conditions

- 본문에는 실제 저장되는 trigger 2~4개만 표시한다.
- 각 trigger는 observation, threshold, cadence, re-review action을 가진다.
- 일반적인 10개 pattern guide와 다음 실험 아이디어는 본문에서 제거한다.
- 아직 Level2 실행이 필요한 항목은 Monitoring condition처럼 포장하지 않는다.

### Disclosure

접힌 disclosure에만 표시한다.

- evidence confidence 근거
- Level2에서 인수한 non-critical limits
- root issue provenance와 technical path
- score/policy compatibility note가 필요한 경우의 legacy detail

eligible 후보에서 0개인 unresolved item을 빈 카드로 렌더링하지 않는다.

## Python Contract

새 pure service:

`app/services/backtest_final_review_decision_brief.py`

책임:

- stored validation과 investability/evidence closure adapter 입력 정규화
- eligibility 확인
- behavior observations와 chart series projection
- verdict, thesis, strength, weakness, trait axes, monitoring conditions 생성
- canonical decision route와 disclosure 생성
- root/observation dedup

초기 schema:

```text
decision_brief_v1
  candidate
  eligibility
  verdict
  evidence_confidence
  behavior_board
    cumulative_series
    benchmark_series
    underwater_series
    execution_observations
  trait_map
  strengths
  weaknesses
  monitoring_conditions
  decision_action
  disclosures
  capabilities
```

`app/services/backtest_evidence_read_model.py`는 기존 registry/payload compatibility adapter와 공통 evidence source 역할을 유지하되, 새 화면의 narrative/strength/weakness/layout projection은 새 service로 이동한다.

## React And Streamlit Ownership

Streamlit:

- navigation
- compact page heading
- Python payload orchestration
- React component unavailable 시 동일 Decision Brief의 최소 fallback

React:

- 후보 선택 intent
- verdict와 evidence presentation
- chart와 trait map rendering
- route/reason intent
- save result presentation

React는 Gate, classification, normalization, dedup, score, persistence를 계산하지 않는다.

React component는 다음 목적 단위로 분리한다.

- `CandidateSelector`
- `VerdictHero`
- `BehaviorBoard`
- `PortfolioTraitMap`
- `StrengthWeaknessSection`
- `MonitoringConditions`
- `EvidenceDisclosure`
- `DecisionAction`

## Data Flow

```text
stored Practical Validation result
  -> Python eligibility Gate
  -> decision_brief_v1 builder
  -> React Decision Workspace
  -> user candidate/route/reason intent
  -> Python current-session and save guard
  -> append-only Final Review decision row
  -> optional Portfolio Monitoring handoff
```

Final Review 안에서 provider fetch, replay, DB ingestion, validation save를 실행하지 않는다.

## Decision Route Compatibility

| UI label | Canonical route | Persistence effect |
| --- | --- | --- |
| 계속 추적 | `SELECT_FOR_PRACTICAL_PORTFOLIO` | Final Review row + allowed 경우 Monitoring handoff |
| 관찰 후 재검토 | `HOLD_FOR_MORE_PAPER_TRACKING` | Final Review non-select row |
| 추적 대상에서 제외 | `REJECT_FOR_PRACTICAL_USE` | Final Review rejected row |
| Level2로 돌려보내기 | `RE_REVIEW_REQUIRED` | Final Review re-review row, Level2 handoff 안내 |

기존 registry row, route, status display를 재작성하지 않는다.

## Error And Missing-Data Behavior

- unresolved actionable / critical engineering / missing contract는 기존 Gate가 React payload 생성 전에 차단한다.
- optional observation이 없으면 fabricated chart, normalized trait value, strength/weakness를 만들지 않는다. chart lane과 trait axis는 명시적인 `미측정` 상태로 남긴다.
- accepted non-critical limitation은 evidence confidence와 disclosure에만 반영한다.
- stale candidate id, payload mismatch, duplicate decision id는 Python save gate에서 차단하고 후보 재열기를 안내한다.
- React build가 없으면 과거 긴 report를 되살리지 않고 같은 Decision Brief의 compact Streamlit fallback을 사용한다.
- component rendering 실패는 registry write를 유발하지 않는다.

## Implementation Sequence

### 1차. Decision Brief Contract

- pure service와 schema
- eligibility / route / dedup contract
- RED -> GREEN service tests

### 2차. Portfolio Behavior Projection

- cumulative / benchmark / underwater series
- execution observations
- trait map
- evidence-backed strength/weakness and triggers
- current GRS regression fixture

### 3차. React Decision Workspace

- React-first candidate-to-decision flow
- Streamlit Decision Desk와 old report section 제거
- compact fallback
- responsive UI와 interaction contract tests

### 4차. Persistence, QA, Docs

- route label compatibility와 save guard
- Monitoring handoff regression
- focused Python tests, GRS runtime tests
- React production build, target py_compile, git diff --check
- desktop/narrow Browser QA
- finance docs, research, active task/handoff sync

## Verification Contract

- current eligible 후보의 unresolved actionable / critical engineering / missing contract는 0이다.
- overall investment score와 3종 headline score가 새 report에 없다.
- strength/weakness item은 direct evidence reference를 가진다.
- 같은 root issue 또는 measured observation을 중복 반영하지 않는다.
- missing observation은 fabricated chart나 0점 axis가 되지 않는다.
- Level2 해결 action과 provider/replay CTA가 Final Review 본문에 없다.
- 후보 선택부터 save intent까지 하나의 React visual hierarchy로 보인다.
- 기존 canonical route와 append-only registry contract가 유지된다.
- generated visual companion, Browser QA screenshot, run history, registry user rows는 commit하지 않는다.

## Final Recommendation

이 설계는 기존 evidence closure correctness를 유지하면서 Final Review의 사용자 질문을 다시 중심에 둔다. 구현은 UI부터 줄이는 방식이 아니라 Python decision projection을 먼저 만들고, 그 contract 위에 React workbench를 올리는 순서로 진행해야 한다.
