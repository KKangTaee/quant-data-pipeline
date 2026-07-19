# Backtest Analysis Level1 Decision Workspace V1 Design

## 이걸 하는 이유?

Practical Validation Level2와 Final Review Level3는 사용자가 단계의 질문을 읽고,
현재 상태와 다음 행동을 한 화면에서 판단하는 decision workspace로 개편됐다.
반면 Level1 Backtest Analysis는 실행 기능이 충분히 존재하지만 다음 문제가 남아
있다.

- 단일 전략과 Portfolio Mix가 하나의 radio 아래에서 전혀 다른 긴 form을 공유한다.
- 기술 설정, 실행 결과, Data Trust, factor readiness, 정책 신호, Level2 handoff가
  여러 Streamlit panel과 tab에 흩어져 있다.
- 전략을 실행한 결과와 Level2 후보로 등록한 결과의 경계가 first-read에서 분명하지
  않다.
- 선택한 전략명이 상단 문맥과 제목을 바꾸면서 사용자가 현재 단계와 작업 대상을
  혼동할 수 있다.
- 일반 사용자 설명과 내부 field / 함수 경로 / status가 같은 시각적 위계에 놓인다.
- 실행 또는 Streamlit rerun 중 입력과 상단 문맥이 사라지는 것처럼 보일 수 있다.
- `Risk-On Momentum 5D`는 구현이 완성되지 않은 개발 단계 전략이지만 일반 운영
  전략과 같은 목록에서 보일 수 있다.
- 저장된 Mix, Run History, Level2 후보 registry는 서로 다른 persistence contract를
  가지지만 하나의 재진입 의미로 읽힐 수 있다.

현재 문제는 전략 계산 엔진을 새로 만드는 일이 아니다. 기존 단일 전략 실행,
Portfolio Mix 실행, 성과 계산, Run History, saved setup, Level2 handoff 기능을
보존하면서 사용자가 후보를 만들고 해석하고 명시적으로 넘기는 제품 흐름으로
투영하지 못한 것이 핵심이다.

## Approved Product Goal

Level1의 중심 질문을 다음으로 고정한다.

> 이 전략 또는 전략 조합을 실행 가능한 후보로 만들고, Level2 검증 대상으로 보낼 근거가 있는가?

사용자는 한 workspace에서 다음을 끝낼 수 있어야 한다.

1. 단일 전략 또는 Portfolio Mix 중 만들 후보 유형을 선택한다.
2. 목적과 핵심 설정을 이해하고 필요한 값만 입력한다.
3. 결과를 성과 순위가 아니라 후보 준비 상태와 근거 순서로 해석한다.
4. 실행 결과, reusable setup, Level2 후보 등록을 구분해 저장한다.

Level1은 실제 투자 적합성을 최종 판단하지 않는다. 높은 수익률만으로 좋은 후보라고
판정하지 않으며, Level2 검증을 시작할 수 있는 실행·데이터·계약 준비 상태까지만
책임진다.

## Approved Scope And Decisions

### Product Scope

- 단일 전략과 Portfolio Mix를 모두 이번 개편 범위에 포함한다.
- 일반 사용자와 숙련 사용자를 함께 지원한다.
- 기본 화면은 설명과 핵심 설정 중심으로 간결하게 유지한다.
- 기존 세부 설정과 근거는 관련 문맥의 progressive disclosure에서 보존한다.
- 전략 runtime, finance DB schema, Level2 / Level3 의미 계약은 기본적으로 바꾸지
  않는다.

### Approved UX Decisions

| 영역 | 승인 결정 |
|---|---|
| 첫 진입 | 단일 전략 후보 / Portfolio Mix 목적 분기 |
| 재진입 | 마지막 workspace와 입력 복원, 상단 `후보 유형 변경` 제공 |
| 단일 전략 | S1 세로 4단계 one-shell |
| Portfolio Mix | M1 역할·비중 중심 세로 4단계 one-shell |
| 결과 | R1 판단 요약 우선 |
| 후보 등록 | 성공 실행과 분리된 명시적 저장 / Level2 이동 |
| 고급 설정 | G1 관련 기본 설정 아래의 문맥형 disclosure |
| 전략 탐색 | C1 목적별 전략 그룹 |
| 저장 Mix | P1 Mix Step 1 안에서 불러오기 |
| 구현 구조 | T2 pure read model + React one-shell + Python fallback |

### Development Strategy Classification

`Risk-On Momentum 5D`는 연구용으로 재분류하거나 삭제하지 않는다. 현재 구현은
보존하고 `개발 중 전략`으로 분리한다.

- 실행을 지원할 수 있는 범위는 유지한다.
- downstream contract가 완성되기 전에는 Level2 후보 저장을 차단한다.
- first-read에는 사용자용 미완성 사유를 표시한다.
- raw handler / contract detail은 상세 개발자 근거에만 둔다.
- 후속 task에서 정식 운영 전략 승격 여부를 검토한다.

## Considered Implementation Approaches

### T1. UI Rearrangement Only

기존 Streamlit 상태와 분류 로직을 유지하고 보이는 순서와 CSS만 바꾼다.

- 장점: 구현량이 작다.
- 단점: rerun reset, 중복 상태 계산, raw contract 노출, React / Python 판단 drift가
  남는다.
- 결정: 채택하지 않는다.

### T2. Level1 Read Model + One-Shell

Python pure service가 후보 상태, 전략 분류, 결과 해석, Level2 handoff Gate를
projection으로 만들고 React와 Python fallback은 같은 projection을 표시한다.

- 장점: 기존 전략 runtime을 보존하면서 Level2 / Level3와 같은 ownership contract를
  만든다.
- 장점: 화면 전체 reset처럼 보이는 현상을 stable context / mutable result 경계로
  교정할 수 있다.
- 장점: raw runtime status와 사용자 설명을 분리할 수 있다.
- 단점: 새 service, component, adapter, compatibility tests가 필요하다.
- 결정: 채택한다.

### T3. Full Level1 Runtime Rewrite

전략 실행, 상태, 저장, UI를 모두 새 workflow로 교체한다.

- 장점: 장기 구조를 가장 크게 단순화할 수 있다.
- 단점: 전략 runtime과 persistence 회귀 위험이 크고 현재 제품 목표보다 범위가 넓다.
- 결정: 채택하지 않는다.

## Target User Flow

### Stable Entry And Context

상단 제목은 선택 전략에 따라 바뀌지 않는다.

```text
Backtest Analysis · Level1
이 전략 또는 조합을 Level2 검증 후보로 만들 수 있는가?
```

선택한 전략이나 Mix는 제목 아래 `현재 작업` summary에 둔다. 재진입 시 마지막
workspace와 입력을 복원하며 summary에서 `후보 유형 변경`을 제공한다.

첫 진입은 두 가지 목적만 보여준다.

```text
단일 전략 후보
Portfolio Mix
```

saved Mix는 세 번째 후보 유형이 아니다. Portfolio Mix Step 1에서 `새 Mix 만들기 /
저장된 Mix 불러오기`로 전환한다.

### Single Strategy Four Steps

1. `전략과 목적`
   - 팩터 기반 종목 선정
   - 모멘텀·전술 자산배분
   - 분산·기본 포트폴리오
   - 개발 중 전략
2. `핵심 설정`
   - 기본 설정 우선
   - Universe 상세
   - Factor·보유 규칙
   - 비용·Guardrail
3. `실행과 해석`
   - 후보 준비 상태
   - 핵심 성과
   - 데이터·실행 근거와 남은 Level1 행동
   - 상세 근거
4. `저장하고 Level2 전송`
   - current 결과와 handoff Gate 확인
   - 명시적 후보 저장

완료된 상위 단계는 사라지지 않고 compact summary가 된다.

초기 운영 전략 매핑은 아래를 기준으로 한다. 이 분류는 React에 hard-code하지 않고
Python strategy metadata에서 projection한다.

| 목적 그룹 | 초기 전략 |
|---|---|
| 팩터 기반 종목 선정 | Quality + Value, Quality, Value |
| 모멘텀·전술 자산배분 | GTAA, Global Relative Strength, Dual Momentum |
| 분산·기본 포트폴리오 | Risk Parity Trend, Equal Weight |
| 개발 중 전략 | Risk-On Momentum 5D |

Strict Annual / Quarterly 같은 동일 전략의 실행 variant는 별도 전략 카드로
중복시키지 않고 해당 전략을 고른 뒤 Step 2 설정에서 선택한다.

### Portfolio Mix Four Steps

1. `구성 전략`
   - 새 Mix 만들기
   - 저장된 Mix 불러오기
2. `역할과 비중`
   - Core / Growth / Defense 같은 역할
   - 총 비중, 중복, alignment
3. `Mix 실행과 해석`
4. `저장하고 Level2 전송`

단일 전략과 같은 학습 구조를 사용하되 역할·비중·alignment는 Mix에서만 책임진다.

## Truth And Persistence Contract

### Explicit Candidate Registration

성공 실행은 Level2 후보 등록과 동일하지 않다.

| 사용자 행동 | 저장 위치 / 의미 |
|---|---|
| 실행 성공 | Run History에 실행 결과 기록 |
| Mix 저장 | reusable saved setup 저장 |
| 후보로 저장하고 Level2로 이동 | Level2 candidate registry 등록 |

Level2 후보 등록은 current 성공 결과와 current 설정 fingerprint가 일치하고,
handoff Gate가 `ready`이며, 실제 persistence handler가 있을 때만 가능하다.

### No Fabricated Actions

- callable handler가 없는 action은 CTA로 투영하지 않는다.
- 개발이 필요한 contract에는 가짜 `지금 해결` 버튼을 제공하지 않는다.
- UI는 raw status만 보고 actionability를 추론하지 않는다.
- development 전략은 명시적 maturity contract로 Level2 handoff를 차단한다.

### Root Issue Deduplication

같은 root cause에서 파생된 warning, data readiness, handoff blocker는 first-read와
count에서 한 번만 반영한다. 파생 evidence는 상세 disclosure에 보존한다.

## Level1 Decision Workspace Read Model

새 pure service를 추가한다.

```text
app/services/backtest_analysis_decision_workspace.py
```

service는 UI framework나 Streamlit session에 의존하지 않고 기존 runtime result,
history, saved setup, strategy metadata, handler registry를 입력으로 받아 immutable
projection을 반환한다.

### Python Ownership

- 목적별 전략 그룹과 표시 순서
- `production / development` maturity
- 전략별 applicable settings와 disclosure groups
- 단일 전략 / Mix 실행 가능 여부
- result freshness와 configuration fingerprint
- 사용자용 결과 요약과 기술 근거 분리
- Data Trust / factor readiness / 기존 handoff contract 해석
- Level2 후보 저장 Gate와 차단 이유
- root issue deduplication
- handler availability와 action contract
- Run History / saved Mix / candidate registry 의미 구분

### UI Ownership

- 후보 유형, 전략, Mix 선택 intent
- 설정값 편집 intent
- 실행, 저장, Level2 이동 intent
- disclosure open / close
- Python projection 렌더링

React는 raw runtime status를 사용자 상태로 분류하거나 Level2 Gate를 계산하지
않는다.

### Top-Level Projection Axes

하나의 거대한 status를 사용하지 않고 독립 상태 축으로 나눈다.

```text
workspace_phase:
  selecting | configuring | running | result | error

result_freshness:
  none | current | stale

handoff_state:
  unavailable | blocked | ready | saved

strategy_maturity:
  production | development
```

projection은 최소한 다음 top-level identity를 제공한다.

```text
workspace_id
workspace_kind
configuration_fingerprint
run_result_id
candidate_source_id
```

존재하지 않는 identity는 빈 문자열이 아니라 explicit `null`로 표현한다.

## Stable Render And Intent Boundary

실행 intent가 발생해도 상단 context와 완료된 입력 단계는 유지한다.

- 상단 hero와 `현재 작업`은 stable surface다.
- Step 1 / Step 2는 실행 중 compact summary로 유지한다.
- Step 3 / Step 4는 mutable result surface다.
- 기존 current 결과가 있으면 삭제하지 않고 `새 설정으로 실행 중`으로 표시한다.
- 실행 성공 뒤 current projection으로 교체한다.
- 실행 실패 뒤 입력과 이전 성공 결과를 보존한다.
- 실제 page route 이동만 app-level navigation을 사용한다.

Streamlit의 script rerun 자체를 없애는 것이 목표가 아니다. 사용자에게 보이는
workspace identity와 stable projection을 rerun 전후에 유지하는 것이 계약이다.

### Physical Render Boundary

시각적으로는 하나의 workspace지만 실행 lifecycle은 같은 frontend bundle의 두
surface mode로 나눈다.

```text
context surface:
  hero + current work + Step 1 + Step 2
  fragment 밖의 stable mount

result surface:
  Step 3 + Step 4
  fragment 안의 mutable mount
```

`context` surface는 후보 유형 / 전략 / 설정 intent만 반환하고, `result` surface는
실행 / 저장 / Level2 이동 intent만 반환한다. 실행 결과 갱신 때문에 result fragment가
rerun되어도 context iframe을 다시 mount하지 않는다. 두 surface는 같은 design token과
read model version을 사용해 사용자에게는 하나의 shell로 보인다.

## Result Interpretation Contract

Level1 first-read는 다음 세 가지 결론만 제공한다.

1. `Level2 검증 후보로 보낼 수 있음`
2. `Level1에서 먼저 해결할 항목이 있음`
3. `개발 중이므로 현재 전송할 수 없음`

첫 화면 정보 순서는 아래와 같다.

1. 판단 요약과 최대 3개 root-dedup 핵심 이유
2. 핵심 성과
3. 데이터와 실행 근거
4. Level1에서 남은 행동
5. 상세 근거

높은 성과는 handoff Gate를 자동 통과시키지 않는다.

### User Explanation

내부 field, status, 함수 경로는 first-read 설명으로 사용하지 않는다.

```text
result_df.Total Balance
-> 비용 반영 후 누적 성과를 계산했습니다

db_write=False
-> 이번 실행은 저장소를 변경하지 않는 읽기 전용 검증입니다

factor_readiness=partial
-> 일부 종목은 필요한 팩터 데이터가 부족합니다

handler_missing
-> 이 전략은 Level2 후보 저장 기능이 아직 연결되지 않았습니다
```

raw field / traceback / callable path는 `상세 근거 > 개발자 정보` disclosure에만
둔다.

## Error And Recovery Contract

오류는 해결 ownership에 따라 구분한다.

| error kind | 의미 | 기본 행동 |
|---|---|---|
| `configuration_required` | 입력 부족 또는 불일치 | 관련 Step 2로 이동 |
| `data_required` | 기존 수집·적재 경로로 준비 가능 | 실제 연결 action만 제공 |
| `execution_failed` | runtime 실행 실패 | 입력·이전 결과 보존 후 재실행 |
| `contract_missing` | 구현 연결 필요 | 개발 필요 설명, CTA 없음 |
| `stale_result` | 설정 변경 뒤 미실행 | 현재 설정으로 다시 실행 |

설정이 바뀌면 과거 결과를 지우지 않고 `stale`로 표시한다. 사용자는 비교를 위해
과거 결과를 볼 수 있지만 다시 실행하기 전에는 Level2 후보로 저장할 수 없다.

## One-Shell And Fallback

새 component 경계는 다음을 기본으로 한다.

```text
app/web/components/backtest_analysis_decision_workspace/
```

- React는 presentation과 intent만 담당한다.
- Python adapter가 intent를 검증하고 기존 runtime / persistence handler를 호출한다.
- React를 사용할 수 없을 때 같은 read model을 사용하는 Python fallback을 제공한다.
- fallback도 같은 정보 순서와 Gate 문장을 사용한다.
- 기존 상세 chart / table / technical metadata는 삭제하지 않고 상세 근거로 연결한다.

## Responsive And Accessibility Contract

### Desktop

- 목적 그룹과 요약 surface는 최대 2열을 사용한다.
- 4단계는 세로 진행 흐름을 유지한다.
- 데이터 밀도가 높은 원본 table은 상세 disclosure에 둔다.

### 760px And Below

- 모든 단계와 카드는 1열이다.
- 전략·Mix 목록은 가로 scroll 대신 세로 목록을 사용한다.
- 긴 전략명과 한국어 설명은 자연스럽게 줄바꿈한다.
- 핵심 table row는 summary card로 바꾸고 원본 표는 disclosure에 둔다.
- 실행·저장 CTA는 본문 너비 전체를 사용한다.
- horizontal overflow는 0이어야 한다.

React component는 `ResizeObserver`로 content height를 Streamlit에 동기화한다.
선택, loading, stale, error 상태는 색상뿐 아니라 label과 보조 문장으로도 표현하고,
키보드 focus를 제공한다.

## Expected File Ownership

구현 전 최종 PLAN에서 실제 call graph를 다시 확인하되 기본 소유 경계는 다음과 같다.

### New

- `app/services/backtest_analysis_decision_workspace.py`
- `app/web/components/backtest_analysis_decision_workspace/`
- focused service / component contract tests

### Existing Adapters To Review

- `app/web/backtest_analysis.py`
- `app/web/backtest_single_strategy.py`
- `app/web/backtest_result_display.py`
- `app/web/backtest_compare/page.py`
- `app/web/pages/backtest.py`

기존 strategy simulation, transform, engine, performance 모듈은 read model이 소비하는
source이며 이번 개편의 재설계 대상이 아니다.

## Development Roadmap

### 1차: Level1 Truth / Handoff Contract

- 현재 실행, 저장, history, handoff call graph 재확인
- production / development 전략 분류
- fingerprint / freshness / handler truth contract
- Level2 Gate와 root issue dedup
- RED -> GREEN tests

### 2차: Level1 Decision Workspace Read Model

- pure service
- common single / Mix projection
- 사용자 설명과 error normalization
- Python fallback projection
- RED -> GREEN tests

### 3차: Single Strategy One-Shell

- purpose-grouped strategy selection
- contextual advanced settings
- stable execution surface
- decision-first result
- explicit candidate registration
- React / fallback tests and production build

### 4차: Portfolio Mix One-Shell

- new / saved Mix entry
- role, weight, alignment
- reusable setup / candidate persistence separation
- Mix result and handoff
- React / fallback tests and production build

### 5차: Runtime QA / Docs / Closeout

- focused service / handoff / boundary / visual contract tests
- existing runtime regression tests
- React production build
- target `py_compile`
- `git diff --check`
- desktop / 760px Browser QA
- canonical finance docs, active task, root handoff sync
- generated / protected artifact exclusion audit

## Test Strategy

모든 기능과 버그 수정은 RED -> GREEN 순서로 진행한다.

### Service Contract

- development 전략은 실행 가능 범위를 유지하되 Level2 handoff가 blocked다.
- production 전략은 목적 그룹에 한 번만 나타난다.
- 같은 root issue는 first-read와 count에서 한 번만 반영된다.
- 실제 handler가 없는 action은 CTA projection이 없다.
- 설정 fingerprint가 바뀌면 current result는 stale이다.
- stale / failed result는 current 후보 저장이 불가능하다.
- user explanation first-read에는 raw callable path가 없다.

### Persistence Boundary

- 실행 성공만으로 candidate registry를 변경하지 않는다.
- saved Mix는 reusable setup만 변경한다.
- explicit candidate save만 Level2 candidate registry를 변경한다.
- protected registry / history fixture는 테스트 temp path로 대체한다.

### UI Contract

- 선택한 전략이 page title을 바꾸지 않는다.
- running 중 stable context / Step 1 / Step 2가 유지된다.
- React와 fallback의 판단 문장과 action availability가 같다.
- 개발 중 전략에 Level2 CTA가 없다.
- 기본 결과에는 raw field / traceback이 없다.
- 760px에서 single-column과 zero horizontal overflow를 만족한다.
- `ResizeObserver` height sync가 존재한다.

### Runtime Regression

- 지원 단일 전략 execution smoke
- Portfolio Mix execution smoke
- Run History persistence boundary
- saved Mix replay boundary
- Level2 candidate handoff compatibility

## Acceptance Criteria

1. 첫 화면은 단일 전략 후보와 Portfolio Mix 두 목적만 보여준다.
2. 상단 제목은 선택 전략이나 Mix에 따라 바뀌지 않는다.
3. 마지막 workspace와 입력을 복원하고 후보 유형 변경 action을 제공한다.
4. 단일 전략은 세로 4단계 one-shell을 사용한다.
5. Portfolio Mix는 역할·비중 중심 세로 4단계 one-shell을 사용한다.
6. 저장된 Mix는 Portfolio Mix Step 1에서 불러온다.
7. 전략은 목적별 그룹으로 탐색한다.
8. `Risk-On Momentum 5D`는 개발 중 전략으로 분리되고 Level2 전송이 차단된다.
9. 고급 설정은 관련 기본 설정 아래 disclosure에 남는다.
10. 결과는 판단 요약, 핵심 성과, 데이터·실행 근거, 남은 행동, 상세 근거 순서다.
11. 높은 성과만으로 Level2 Gate를 통과하지 않는다.
12. 실행 성공은 Run History만 기록하며 후보를 자동 등록하지 않는다.
13. saved Mix와 candidate registry persistence가 분리된다.
14. explicit 후보 저장만 Level2 candidate registry를 변경한다.
15. Python pure service가 분류, freshness, explanation, Gate를 소유한다.
16. React는 raw status 분류나 Gate 계산을 하지 않는다.
17. React와 Python fallback은 같은 read model을 사용한다.
18. callable handler가 없는 CTA는 렌더링하지 않는다.
19. 동일 root issue는 first-read와 count에서 한 번만 나타난다.
20. 설정 변경은 결과를 삭제하지 않고 stale로 표시한다.
21. stale 결과는 다시 실행하기 전 Level2 후보 저장이 불가능하다.
22. 실행 중 stable context와 완료된 상위 단계가 유지된다.
23. 실패 시 입력과 이전 성공 결과가 보존된다.
24. raw field, 함수 경로, traceback은 기본 결과 화면에 노출되지 않는다.
25. desktop은 목적 그룹과 요약에 최대 2열을 사용한다.
26. 760px 이하는 1열이며 horizontal overflow가 없다.
27. React component는 ResizeObserver height sync를 사용한다.
28. 기존 전략 runtime과 Level2 / Level3 contract를 재설계하지 않는다.
29. 관련 기능은 RED -> GREEN 테스트로 구현한다.
30. desktop / 760px Browser QA와 fresh completion verification을 통과한다.
31. registry, run history, saved JSONL, generated QA artifact, `.superpowers/`는 명시
    요청 없이 stage / commit하지 않는다.
32. 실행 결과 갱신은 mutable result surface만 다시 mount하며 stable context surface를
    유지한다.

## Out Of Scope

- 신규 전략 연구 또는 전략 성능 개선
- `Risk-On Momentum 5D` downstream contract 완성
- strategy runtime 재설계
- DB schema 재설계
- Level2 / Final Review route 재설계
- historical universe / delisting 신규 provider
- broker order, live approval, account sync, auto rebalance
- registry / run history / saved JSONL 정리 또는 재작성

## 6차 Corrective Design: Single Strategy Settings Workspace

### 이걸 하는 이유?

1~5차는 Level1의 고정 질문, 목적별 전략 선택, stable context, 결과 판단과
명시적 인계를 개편했지만 Single Strategy Step 2는 기존 Streamlit form을 거의
그대로 보존했다. 그 결과 새 React context에서 이미 선택한 Strategy / Variant를
다시 selectbox로 고르게 하고, 영문 기술 문구와 긴 universe 근거가 기본 설정보다
먼저 노출된다. 이는 Acceptance Criteria 4, 9, 22의 사용자 경험을 충분히
만족하지 못한다.

### Current Flow Audit

```text
React purpose catalog
  -> select_strategy intent
  -> Python backtest_strategy_choice session state
  -> render_single_strategy_workspace()
  -> duplicate Strategy / Variant Streamlit selectbox
  -> 13 strategy/variant render functions in 7 files
  -> universe controls outside form
  -> date / primary settings in form
  -> nested strategy / overlay / cost / guardrail expanders
  -> shared _handle_backtest_run(payload, strategy_name)
  -> result fingerprint / Run History / decision surface
```

확인된 구조적 원인은 다음과 같다.

- React와 Python이 같은 `backtest_strategy_choice`를 공유하지만 두 surface가 모두
  strategy picker를 렌더링한다.
- 13개 form은 payload와 validation이 서로 달라 완전한 React editor로 옮기면
  session state / validation / prefill을 이중 구현해야 한다.
- 기존 boundary test는 `Advanced Inputs`가 `전략·보유 규칙`으로 바뀌었는지만
  확인해 실제 hierarchy, 중복 picker, 사용자 문구를 검증하지 못한다.
- Strict factor 7개 variant는 universe readiness와 PIT contract가 길고 기술적이라
  first-read를 압도한다.

### Approaches Considered

#### A. Shared Python Settings Shell — Selected

Python widget, payload, validation, prefill을 유지하면서 공통 Step 2 shell과 section
helper를 추가한다. React는 전략 선택만 소유하고 Streamlit은 선택 전략의 설정만
렌더링한다.

- 장점: runtime / payload / form submit 의미를 유지하고 13개 form을 같은 IA로
  통일할 수 있다.
- 단점: React와 완전히 동일한 card component는 아니며 Streamlit layout 제약이
  남는다.

#### B. Full React Settings Editor

모든 입력을 React에서 편집하고 intent payload로 Python에 전달한다.

- 장점: 가장 강한 visual consistency.
- 단점: 13개 form의 field, validation, prefill, immediate universe selector를
  중복 구현하고 Python-owned intent contract가 과도하게 커진다. 이번 corrective
  범위를 벗어난다.

#### C. Quality + Value Only Cleanup

현재 신고된 Strict Annual form만 재배치한다.

- 장점: 수정량이 가장 작다.
- 단점: 전략을 바꾸면 다시 legacy hierarchy가 나타나 Level1 전체 흐름이
  일관되지 않다.

### Selected User Flow

```text
1. React에서 목적과 전략 선택
2. 선택 전략 compact summary
   - 전략명 / variant / 목적 / 현재 maturity
   - 전략 변경은 위 catalog에서 수행
3. 핵심 실행 설정
   - 기간
   - 핵심 전략 파라미터(Top N, 리밸런싱, 신호 주기 등)
4. 투자 대상 Universe
   - Preset / 직접 입력
   - 현재 선택 수와 대표 ticker
   - PIT / data readiness는 한 줄 상태 요약
   - 기술 계약은 접힌 `Universe 근거`에서 확인
5. 선택·보유 규칙
   - factor, overlay, weighting, defensive rule
6. 비용·위험 기준
   - transaction cost, benchmark, liquidity, guardrail
7. `이 설정으로 백테스트 실행`
8. 기존 decision surface에서 결과 판단 / Level2 인계
```

### UI Contract

- visible Strategy / Variant selectbox를 제거한다. React catalog와 current summary가
  유일한 first-read selection surface다.
- saved history prefill이 strategy를 바꾸는 경우에도 session state를 먼저 갱신한 뒤
  같은 summary와 form을 렌더링한다.
- 모든 13개 form은 `선택 전략 -> 핵심 실행 설정 -> Universe -> 선택·보유 규칙 ->
  비용·위험 기준 -> 실행` 순서를 사용한다.
- desktop primary setting은 최대 2열, 760px 이하는 1열로 읽힌다.
- 영문 technical label은 payload key를 바꾸지 않고 사용자용 한국어 label / help로
  교체한다. 원본 mode / callable / raw contract는 disclosure에만 남긴다.
- long ticker list는 `종목 N개 · 대표 ...` summary로 줄이고 전체 목록은 disclosure에
  둔다.
- readiness는 실행 전 blocker 또는 확인점만 요약하고, 실행 후 실제 Factor
  Readiness가 최종 근거를 소유한다.
- development 전략은 설정과 실행 surface를 유지하되 기존대로 Level2 handoff가
  blocked다.

### Component Boundary

- 새 `app/web/backtest_single_settings_workspace.py`
  - common selected-strategy summary
  - section heading / note / compact ticker summary
  - consistent Korean label dictionary
  - no runtime execution or persistence
- `app/web/backtest_single_strategy.py`
  - duplicate picker 제거
  - session selection validation과 selected summary / strategy dispatch만 소유
- `app/web/backtest_single_forms/*.py`
  - strategy-specific widget와 payload / validation 유지
  - common section helper를 사용해 hierarchy와 copy 정렬
- `app/web/backtest_common.py`
  - existing universe / readiness helper는 data resolution만 유지하고 first-read raw
    copy를 공통 shell에 맞게 compact projection한다.

### State And Error Contract

- 사용자 입력을 받는 widget key와 payload key는 바꾸지 않아 saved history prefill을
  보존한다. 허용값이 하나뿐이던 fixed `timeframe` / `option` selectbox는 동일 payload
  상수로 바꾸는 의도적 예외다.
- form submit 이전 변경값이 Python draft에 반영되지 않는 Streamlit contract는
  유지한다. submit 시 shared runner가 normalized fingerprint를 기록한다.
- validation error는 영어 raw 문장 대신 해당 section 바로 아래의 사용자 설명으로
  표시한다.
- 실행 실패 시 설정과 이전 성공 결과를 보존한다.

### Corrective Acceptance Criteria

1. Single Strategy Step 2에 visible `Strategy` / `Variant` selectbox가 없다.
2. current strategy / variant / purpose / maturity summary가 설정 시작점에 한 번만
   나타난다.
3. 13개 form 모두 같은 5-section ordering을 사용한다.
4. Quality + Value Strict Annual의 first-read에 영문 strategy 설명, raw mode,
   전체 300 ticker preview가 없다.
5. 기본 설정과 universe 선택은 고급 factor / overlay / cost보다 먼저 나타난다.
6. full ticker / PIT / readiness technical evidence는 disclosure에 보존된다.
7. submit label은 `이 설정으로 백테스트 실행` 의미의 한국어 문구다.
8. 사용자 입력 widget key, payload, validation, prefill, execution handler는 호환된다.
   fixed single-value `timeframe` / `option` widget은 동일 payload 상수화 예외다.
9. strategy change / run 중 stable React context와 stale-result contract가 유지된다.
10. desktop / 760px Browser QA에서 section hierarchy와 zero horizontal overflow를
    확인한다.
11. 보호 registry / run history / saved JSONL / generated screenshot / `.superpowers/`는
    stage / commit하지 않는다.

### Corrective Out Of Scope

- strategy runtime / payload schema 재설계
- 모든 설정을 React-controlled form으로 이동
- 신규 preset / provider / universe contract 추가
- Factor Readiness 판정 로직 변경
- Level2 / Level3 route 또는 Gate 변경

## 7차 Corrective Design: Unified React Strategy Settings Workspace

### 이걸 하는 이유?

6차는 13개 renderer의 정보 순서와 문구를 정렬했지만 `Approach A. Shared Python
Settings Shell`을 선택해 native Streamlit widget을 의도적으로 보존했다. 실제 화면을
다시 감사한 결과 Quality + Value는 기존 strict-factor disclosure 덕분에 상대적으로
정돈되어 보였지만 Equal Weight, GTAA와 다른 전략은 같은 React one-shell 안에서
legacy Streamlit form으로 급격히 전환된다. 사용자가 요청한 "전략을 바꿔도 동일한
디자인"을 만족하려면 6차 out-of-scope였던 React-controlled settings를 이번 7차에서
명시적으로 범위 안으로 가져와야 한다.

### Confirmed Root Cause

- active Single Strategy는 9개 user choice와 13개 concrete renderer를 사용한다.
- `app/web/backtest_single_forms/*.py`에만 `st.date_input`, `st.number_input`,
  `st.radio`, `st.selectbox`, `st.multiselect`, `st.text_input`, `st.form`,
  `st.expander` 호출이 최소 167개 남아 있고 shared helper가 추가 widget을 렌더링한다.
- 6차의 `single_settings_section()`은 `st.container(border=True)` wrapper이므로
  Level2 / Level3 React card와 같은 component가 아니다.
- GTAA actual DOM에는 `Score Horizons`, `Promotion Policy Signal`, `Minimum Price`와
  같은 legacy 영문 first-read가 남아 있다.
- variant가 없는 전략의 header는 빈 `variant_badge` 줄 때문에 다음 `<span>`을
  Markdown code block으로 해석해 `<span>운영 전략</span>`을 문자 그대로 노출한다.
- payload / validation / prefill이 전략별 renderer 안에 묶여 있어 CSS patch만으로는
  visual consistency와 contract 단일화를 함께 해결할 수 없다.

### Approaches Reconsidered

#### A. Streamlit CSS Reskin

현재 form을 유지하고 global CSS로 native widget을 더 강하게 꾸민다.

- 장점: 구현량과 runtime 회귀 위험이 가장 작다.
- 단점: browser-native input, Streamlit expander, iframe 밖 React card의 차이가 남고
  theme / Streamlit version에 따라 다시 깨진다.

#### B. React Strategy Detail + Streamlit Settings

전략 설명과 summary만 React로 옮기고 입력은 Streamlit에 둔다.

- 장점: 현재 설정 대상을 명확히 설명할 수 있다.
- 단점: 사용자가 지적한 설정 전환 단절이 그대로라 목표를 만족하지 못한다.

#### C. Schema-Driven React Settings Workspace — Selected

Python이 모든 strategy settings schema, option, default, validation, payload adapter를
소유하고 React는 schema를 동일한 visual system으로 렌더링해 full draft intent만
보낸다.

- 장점: 13개 전략이 같은 detail / settings language를 사용하고 React가 domain
  classification이나 Gate를 계산하지 않는다.
- 단점: field contract를 한 번 명시적으로 추출해야 하므로 구현 범위가 크다.
- 사용자 승인: 2026-07-18, 7차에서 C안을 진행한다.

### Target User Flow

```text
1. 고정 Level1 질문과 목적별 전략 선택 (existing context surface)
2. 선택 전략 설명
   - 무엇을 고르는가
   - 어떻게 보유·교체하는가
   - 운영 가능 상태와 핵심 주의점
3. 동일한 React settings surface
   - 핵심 실행 설정
   - 투자 대상 Universe
   - 선택·보유 규칙
   - 비용·위험 기준
   - 고급 설정과 기술 근거 disclosure
4. 이 설정으로 백테스트 실행
5. 기존 decision surface에서 fresh / stale / blocker / Level2 handoff 판단
```

전략 변경은 위 React catalog 한 곳에서만 한다. settings surface 안에는 다시 strategy
picker를 만들지 않는다. Quality / Value family의 Annual / Quarterly variant는 settings
header의 segmented control로 제공하되 Python allow-list로 검증한다.

### Read Model Contract

새 schema version은 `backtest_single_settings_workspace_v2`다.

```text
workspace
  schema_version
  strategy_choice
  concrete_strategy_key
  draft_key
  profile
    display_name
    purpose_label
    maturity_label
    description
    selection_rule
    holding_rule
    risk_note
  variant
    value
    options[]
  sections[]
    section_id
    title
    description
    fields[]
    disclosures[]
  evidence
    universe_summary
    universe_full_text
    technical_rows[]
  action
    id = run_single_strategy
    label
    enabled
  validation_errors{}
```

field는 `field_id`, `payload_key`, `label`, `control`, `value`, `required`, `help`,
`options`, `min`, `max`, `step`, `advanced`, `visible_when`을 필요한 만큼 가진다.
허용 control은 `date`, `number`, `text`, `single_select`, `multi_select`, `segmented`,
`toggle`로 제한한다. React는 `visible_when`과 supplied option metadata를 표시하는 것만
담당하며 option, maturity, Gate를 자체 분류하지 않는다.

### Python Ownership

- 새 pure service `app/services/backtest_single_settings_workspace.py`
  - 13개 concrete strategy schema coverage
  - submitted draft field allow-list / type / range / option validation
  - strategy / variant별 payload projection
  - 사용자 설명과 field-level error projection
- `app/web/backtest_single_settings_workspace.py`
  - current session / prefill / preset / DB-backed universe option adapter
  - component render와 intent consume
  - React unavailable 시 같은 read model을 쓰는 generic Streamlit fallback
- `app/web/backtest_single_strategy.py`
  - selected strategy / variant 검증
  - primary React settings route와 fallback route
  - result stale preservation
- `app/web/backtest_single_runner.py`
  - 기존 `_handle_backtest_run(payload, strategy_name)` 실행, normalized draft,
    fingerprint, Run History owner를 유지한다.

기존 `app/web/backtest_single_forms/*.py`의 payload 의미와 validation은 pure service로
추출한다. migration 동안 fallback adapter가 같은 schema와 payload projector를
사용하게 해 React와 Python form이 서로 다른 계약을 갖지 않게 한다.

### React Ownership

기존 `backtest_analysis_decision_workspace` bundle에 `settings` surface를 추가한다.

- selected profile과 plain-text badge render
- variant segmented control intent
- section / field / disclosure render
- local draft editing과 field-level error display
- submit 중 pending / duplicate-submit prevention
- `run_single_strategy` intent emit
- 760px one-column layout와 ResizeObserver height sync

React는 raw payload를 handler에 직접 전달하지 않는다. `{strategy_choice, variant,
values}` draft를 intent로 보내며 Python이 current selection과 대조하고 validate한 뒤
payload를 생성한다.

### Intent And Execution Contract

허용 settings action은 다음 두 개뿐이다.

- `select_strategy_variant`
  - current family의 supplied option만 허용
  - Python session variant를 갱신하고 새 schema를 투영
- `run_single_strategy`
  - current strategy / variant와 intent identity가 일치해야 함
  - unknown field, hidden field injection, out-of-range number, invalid option을 거부
  - validation 통과 후에만 existing `_handle_backtest_run()` 호출

실행 성공은 Run History만 기록한다. Level2 candidate source는 기존 decision surface의
명시적 `save_and_move` intent만 만든다.

### State And Rerun Contract

- fixed context surface는 settings 변경과 실행 중 유지한다.
- React local draft는 `draft_key = strategy + variant + prefill revision`으로 구분한다.
- ordinary field edit는 component local state만 바꾸며 Streamlit rerun을 만들지 않는다.
- variant 변경과 submit만 Python intent를 발생시킨다.
- submit 즉시 button을 pending으로 잠그고 Python callback이 intent를 한 번만 소비한다.
- 실행 실패 시 submitted draft와 이전 성공 result를 보존하고 field / section error를
  settings surface에 표시한다.
- 전략 또는 variant 변경 시 이전 성공 result는 삭제하지 않고 `stale`로 유지한다.
- history prefill은 Python이 schema value로 투영하며 사용자는 다시 실행해야 fresh가
  된다.

### Visual Contract

- 모든 전략은 같은 profile card, 4개 primary section, disclosure, CTA를 사용한다.
- profile badge는 HTML string injection이 아니라 React text node로 렌더링한다.
- first-read label은 한국어이며 `Score Horizons`, `Promotion Policy Signal`, raw mode,
  callable path는 보이지 않는다.
- 기술 key가 필요하면 `고급 설정과 기술 근거` disclosure의 secondary text로 둔다.
- desktop primary fields는 최대 2열, wide multi-select / universe / disclosure는 full
  width다.
- 760px 이하는 모든 field가 1열이고 page / iframe horizontal overflow는 0이다.
- field 수가 많은 Risk-On은 같은 section contract를 유지하되 advanced filter / exit /
  diagnostics group을 기본 접힘으로 둔다.
- action이 가능한 전략은 동일한 full-width `이 설정으로 백테스트 실행` CTA를 가진다.

### Fallback Contract

React build가 없거나 component render가 실패하면 Python generic fallback이 같은 schema,
same defaults, same validation, same payload projector를 사용한다. fallback은 기능 보존용
Streamlit UI이며 primary product surface가 아니다. legacy strategy-specific form은 payload
parity가 확보된 뒤 active route에서 제거한다.

### Error Contract

- field error는 해당 field 바로 아래의 사용자 설명으로 표시한다.
- cross-field error는 해당 section 위에 표시한다.
- data/runtime failure는 settings를 지우지 않고 existing decision error surface와 함께
  표시한다.
- raw traceback, callable path, internal exception class는 first-read에 노출하지 않는다.
- unknown action / field / option은 조용히 무시하지 않고 Python validation result로
  차단하되 registry / run history write를 만들지 않는다.

### Test Contract

- pure schema test가 9개 strategy choice와 13개 concrete variant를 정확히 한 번씩
  포함하는지 확인한다.
- 모든 field id / payload key / option / default / range와 section ordering을 검증한다.
- 대표 payload parity fixture로 Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum,
  Risk-On, Quality, Value, Quality + Value annual / quarterly를 검증한다.
- invalid strategy / variant / unknown field / hidden field / invalid option / range error가
  handler 호출 전에 차단되는지 검증한다.
- intent consume test가 callable handler가 있을 때만 run action을 실행하는지 확인한다.
- React source / build test가 all-strategy schema renderer, plain-text badge, pending,
  responsive CSS, ResizeObserver를 확인한다.
- fallback test가 같은 read model과 payload projector를 쓰는지 확인한다.
- Browser QA에서 9개 catalog choice와 13개 variant의 profile / section / CTA를 확인하고
  Equal Weight, GTAA, Quality + Value Annual을 실제 실행한다.

### 7차 Acceptance Criteria

1. 9개 strategy choice와 13개 concrete renderer가 primary React settings surface를 쓴다.
2. primary Single Strategy path에 strategy-specific native Streamlit form이 보이지 않는다.
3. 전략을 바꿔도 profile / 4-section / disclosure / CTA hierarchy가 동일하다.
4. `<span>운영 전략</span>` 또는 다른 raw HTML text가 노출되지 않는다.
5. GTAA / Equal Weight / GRS first-read에 legacy 영문 heading과 diagnostic prose가 없다.
6. 모든 기존 execution payload 의미, validation, prefill, handler, fingerprint가 호환된다.
7. React는 maturity, Gate, handler availability, Level2 eligibility를 계산하지 않는다.
8. unknown / invalid intent는 실행과 persistence 전에 Python에서 차단된다.
9. 실행 실패와 strategy change에서 draft와 이전 result 보존 계약이 유지된다.
10. React unavailable fallback은 같은 schema / payload projector로 실행 가능하다.
11. actual Equal Weight / GTAA / Quality + Value Annual 실행이 성공한다.
12. desktop / 760px에서 iframe height sync와 horizontal overflow 0을 확인한다.
13. protected registry / run history / saved JSONL / `.superpowers/` / screenshot은 stage나
    commit하지 않는다.

### 7차 Out Of Scope

- strategy algorithm / performance / factor formula 변경
- 신규 strategy / preset / provider / historical universe 추가
- Portfolio Mix settings React migration
- DB schema / ingestion / strategy runtime 재설계
- Level2 / Final Review route와 Gate 재설계
- broker order, live approval, account sync, auto rebalance
- protected JSONL과 generated artifact 정리 또는 rewrite

## 8차 Corrective Design: Modifier-Free Multi-Select Controls

### 이걸 하는 이유?

7차 schema-driven React editor는 Python의 배열 값을 정확히 보존하지만
`multi_select`를 browser-native `<select multiple>`로 렌더링한다. 이 control은 macOS에서
추가 선택 시 Command, Windows/Linux에서 Ctrl modifier를 요구하고 선택된 option이
스크롤 밖에 있으면 현재 상태도 보이지 않는다. 실제 Quality 화면은 기본값 5개가 이미
선택됐는데도 한 번에 하나만 선택되는 것처럼 읽힌다. GTAA 상대강도 계산 기간과 방어
자산도 같은 renderer를 사용하므로 공통 control을 modifier-free interaction으로 바꾼다.

### Confirmed Root Cause And Scope

- Python schema와 payload는 이미 `list` 타입, 중복 금지, option allow-list를 지원한다.
- React `SettingsFieldControl`의 `case "multi_select"`만 native select와
  `selectedOptions` event에 의존한다.
- compact option은 Quality/Value 지표 14개 이하와 GTAA 계산 기간 4개다.
- large option은 직접 입력 종목과 방어 자산 1,031개다.
- 따라서 strategy별 schema나 runner를 고치는 문제가 아니라 공통 React control의
  interaction과 presentation 문제다.

### Approaches

#### A. Native Multi-Select + 사용법 안내

- 장점: 구현이 가장 작다.
- 단점: modifier key 의존, 모바일 조작, 선택 상태 가시성 문제가 그대로 남는다.

#### B. 모든 옵션을 펼친 Checkbox Grid

- 장점: 클릭마다 독립 toggle이 되어 동작이 명확하다.
- 단점: 1,031개 ticker field에서 화면 높이와 탐색 부담이 과도하다.

#### C. Option Count 기반 Adaptive Multi-Select — Selected

- option 20개 이하는 compact checkbox-card grid로 표시한다.
- option 21개 이상은 검색 가능한 checkbox list와 selected chip shelf로 표시한다.
- 사용자는 modifier key 없이 각 항목을 클릭해 기존 선택을 유지한 채 추가/제거한다.
- 사용자 승인: 2026-07-18.

### Interaction Contract

#### Compact Mode

- Quality/Value 지표와 GTAA 계산 기간을 checkbox-card grid로 렌더링한다.
- 각 option은 `aria-pressed`와 selected style을 가지며 클릭은 해당 값만 toggle한다.
- `전체 선택`은 supplied option 전체를 catalog 순서로 선택한다.
- `선택 해제`는 빈 배열을 만들며 required validation은 실행 시 기존 Python error로
  안내한다.
- 선택 수와 앞 5개 label을 control 아래에서 항상 확인할 수 있다.

#### Search Mode

- 직접 입력 종목과 방어 자산은 검색 input, selected chip shelf, bounded checkbox result
  list로 구성한다.
- 검색은 option label/value의 case-insensitive substring match이며 domain 분류를 하지 않는다.
- checkbox row click과 selected chip의 제거 button은 같은 toggle helper를 사용한다.
- `검색 결과 전체 선택`은 현재 filter 결과만 catalog 순서로 추가하고 기존 선택을
  유지한다. `선택 해제`는 전체 current selection을 비운다.
- 검색어가 없으면 첫 100개 option만 보여주고 나머지 수를 안내해 1,031개 DOM node를
  한 번에 만들지 않는다. 이미 선택된 값은 검색 결과 밖이어도 chip shelf에서 보인다.

### State And Data Contract

- control input/output은 기존과 동일한 `unknown[]` draft array다.
- toggle은 supplied option value만 허용하고 `String(value)` identity로 비교한다.
- 새 selection은 schema option 순서로 정규화해 fingerprint와 payload가 클릭 순서에
  따라 달라지지 않게 한다.
- ordinary selection edit는 React local state만 갱신하고 Streamlit rerun을 만들지 않는다.
- submit 시 기존 `{strategy_choice, variant, values}` intent를 그대로 사용한다.
- Python visible branch, unknown option, required, type, duplicate validation과 exact payload
  projector는 변경하지 않는다.

### Visual And Accessibility Contract

- compact grid는 desktop에서 available width에 맞춰 자동 열을 만들고 760px에서 최소
  2열까지 자연스럽게 줄바꿈한다.
- selected/unselected는 배경색만이 아니라 border, check mark, `aria-pressed`로 구분한다.
- search result list는 최대 높이를 두고 내부 세로 scroll만 허용하며 가로 overflow는 0이다.
- search input, checkbox row, chip remove button은 keyboard focus와 visible focus outline을
  가진다.
- field label, required badge, help, validation error, selection summary의 현재 계층은
  유지한다.

### Error And Safety Contract

- 0개 선택, invalid option, unknown field는 기존 Python validator가 실행 전에 차단한다.
- search result bulk selection도 schema option 이외의 값을 만들 수 없다.
- selection edit는 Run History, registry, saved JSONL을 쓰지 않는다.
- 실행 실패 시 draft와 이전 성공 result를 보존하는 7차 계약을 유지한다.

### Files And Ownership

- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
  - adaptive mode, toggle/order helper, search state, selected chip과 bulk action render
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
  - compact grid, checkbox row, chip shelf, search list, 760px/focus styles
- Modify `tests/test_backtest_refactor_boundaries.py`
  - native `<select multiple>` 제거, adaptive threshold/search/toggle/bulk/responsive source contract
- Modify active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
  - RED/GREEN, Browser QA, closeout evidence

Python schema, settings adapter, runner, strategy runtime과 persistence contract는 이 8차에서
변경하지 않는다.

### Test And QA Contract

- RED source/visual contract가 native `<select multiple>`를 거부하고 compact/search mode,
  modifier-free toggle, catalog-order normalization, bulk action, selected chip을 요구한다.
- React production build와 existing focused Python/settings/boundary tests를 통과한다.
- Browser desktop QA에서 Quality 기본 5개에 두 지표를 modifier 없이 순서대로 추가하고
  count가 6, 7로 늘어나는지 확인한다.
- GTAA 계산 기간에서도 두 항목을 modifier 없이 독립 toggle하고 selection summary와
  submitted draft가 배열을 유지하는지 확인한다.
- large defensive asset field에서 검색, 단일 추가, chip 제거, 검색 결과 전체 선택과
  bounded list를 확인한다.
- 760px에서 compact grid, search input, chip shelf, CTA와 iframe의 horizontal overflow가
  0인지 확인한다.

### 8차 Acceptance Criteria

1. 모든 `multi_select` field는 modifier key 없이 기존 선택을 유지하며 항목을 추가한다.
2. compact field는 checkbox-card grid, large field는 search + checkbox list + chip shelf를 쓴다.
3. Quality/Value와 GTAA에서 선택 수와 선택 항목을 항상 확인할 수 있다.
4. large option field는 초기 1,031개 row를 전부 DOM에 만들지 않는다.
5. React intent와 Python schema/validation/payload/runner 계약은 변경되지 않는다.
6. required field 0개 선택과 invalid option은 실행 전에 Python에서 차단된다.
7. desktop / 760px horizontal overflow는 0이고 keyboard/focus contract를 유지한다.
8. focused tests, React build, target py_compile, diff-check를 통과한다.
9. protected JSONL, `.superpowers/`, generated screenshot은 stage/commit하지 않는다.

### 8차 Out Of Scope

- factor 의미, weighting, score horizon 계산 변경
- 신규 factor/ticker option 또는 preset 추가
- Python fallback `st.multiselect` redesign
- Portfolio Mix settings migration
- strategy runtime, DB, ingestion, Level2/3 Gate 변경

## 9차 Corrective Design: Deterministic Preset Application

### 이걸 하는 이유?

8차까지의 React 설정 editor는 preset 이름과 universe 종목은 정확히 연결하지만, preset을
바꿔도 보유 수, 신호 주기, 선택 지표, 방어 규칙, 비용 기준이 이전 draft 값으로 남는다.
특히 `GTAA SPY Low-MDD Style Top-2 ADV20`은 legacy 계약에 `top=2`, `interval=4`,
`1M/6M`, `IEF/TLT`, `ADV20=20M`이 명시돼 있는데 current React에서는 preset 이름만
바뀌고 기본 `top=3`, `interval=1`, `1M/3M/6M/12M`이 유지된다. 사용자는 preset을
완결된 시작 설정으로 이해하므로, universe와 규칙이 서로 다른 후보를 실수로 실행할 수 있다.

### Confirmed Audit

- Equal Weight 3개, GRS 2개, Risk Parity 1개, Dual Momentum 1개 preset은 현재 universe
  members만 정의한다.
- GTAA 9개 preset 중 `GTAA SPY Low-MDD Style Top-2 ADV20`만
  `GTAA_PRESET_PARAMETER_DEFAULTS`에 machine-readable override가 있다.
- GTAA U3 / U1 / U5 / Low-MDD Top-3는 legacy 설명에 검증된 `top`, `interval`, score
  horizon과 일부 trend / risk contract가 남아 있지만 현재 runtime option에는 전달되지 않는다.
- Quality broad 1개와 strict managed preset은 universe members와 target size를 소유하고,
  factor / overlay / risk 값은 strategy·variant 기본값을 사용한다.
- Risk-On Momentum 5D의 `top1000` / `top2000` / `sp500`은 universe mode이지 named preset이
  아니므로 이번 preset application 대상이 아니다.
- legacy GTAA native form은 preset별 parameter defaults를 session state에 적용하지만,
  current schema runtime context에는 preset members와 strict target size만 있고 parameter
  profile은 없다.
- React `setFieldValue()`는 field 하나만 갱신하며 preset change를 별도 intent나 declarative
  patch로 해석하지 않는다.

### Approaches

#### A. Existing Explicit Override만 복원

- 장점: 가장 작은 회귀 수정이며 이미 machine-readable인 GTAA 1개 계약만 복원한다.
- 단점: 다른 preset은 여전히 universe만 바뀌어 사용자 기대와 화면 의미가 일치하지 않는다.

#### B. React에 Strategy별 Preset 조건문 추가

- 장점: 화면 반응을 빠르게 구현할 수 있다.
- 단점: React가 전략 의미와 기본값을 소유해 Python fallback / payload / legacy와 drift한다.

#### C. Python-owned Base Profile + Evidence-backed Override — Selected

- 모든 named preset은 해당 strategy·variant의 공식 기본값으로 완결된 base profile을 가진다.
- 검증된 별도 parameter evidence가 있는 preset만 base profile 위에 override를 적용한다.
- React와 Python fallback은 Python이 제공한 field-value patch를 기계적으로 적용하며 전략별
  숫자나 분류를 계산하지 않는다.
- 사용자 승인: 2026-07-18.

### Preset Profile Contract

Python pure service는 preset별로 다음 JSON-ready model을 만든다.

```text
preset_profiles[preset_name] = {
  application_kind: strategy_default | validated_override,
  source_label: 사용자 설명,
  values: {field_id: value}
}
```

- `values`는 current workspace schema에 실제 존재하는 field만 포함한다.
- 모든 preset은 universe `preset_name`과 preset-owned execution / selection / holding / risk
  field를 deterministic하게 다시 설정한다.
- `start`, `end`처럼 검증 기간 자체를 정하는 값은 preset-owned가 아니므로 보존한다.
- `universe_mode`는 preset 선택 시 `preset`으로 유지하고 manual ticker draft는 삭제하지 않아
  사용자가 직접 입력 모드로 돌아갈 때 기존 입력을 복구할 수 있게 한다.
- strategy / variant base profile은 schema field default에서 만들고, 별도 override가 없는
  universe preset도 같은 strategy 기본 규칙 전체를 적용한다.
- override에 없는 field는 이전 draft 값을 유지하지 않고 base profile 값으로 돌아간다. 이를
  통해 A preset에서 수정된 값이 B preset에 누출되지 않게 한다.

### Evidence-backed GTAA Overrides

- `GTAA Universe (U3 Commodity Candidate Base)`:
  `top=2`, `interval=3`, score horizon `1/3/6`; 나머지는 GTAA base profile.
- `GTAA Universe (U1 Offensive Candidate Base)`:
  `top=2`, `interval=3`, score horizon `1/3/6/12`; 나머지는 GTAA base profile.
- `GTAA Universe (U5 Smallcap Value Candidate Base)`:
  `top=3`, `interval=3`, score horizon `1/3/6/12`; 나머지는 GTAA base profile.
- `GTAA SPY Low-MDD Style Top-3`:
  `top=3`, `interval=3`, score horizon `1/6`, `trend_filter_window=250`,
  `risk_off_mode=cash_only`, `benchmark_ticker=SPY`; 나머지는 GTAA base profile.
- `GTAA SPY Low-MDD Style Top-2 ADV20`:
  existing `GTAA_PRESET_PARAMETER_DEFAULTS` 전체를 authoritative override로 사용한다.
- 다른 GTAA preset은 근거 없는 tuning을 만들지 않고 GTAA base profile을 사용한다.

문서 설명만으로 값을 추론하지 않는다. 위 값은 이미 legacy preset note 또는
`GTAA_PRESET_PARAMETER_DEFAULTS`에 명시된 contract만 machine-readable map으로 승격한다.

### State Precedence And Interaction

초기 workspace build precedence는 다음 순서를 따른다.

1. strategy / variant schema defaults
2. selected preset base profile과 validated override
3. saved replay / prefill / stored draft의 explicit values

따라서 저장된 실행을 불러올 때는 당시 explicit payload가 보존되고, 사용자가 화면에서 다른
preset을 직접 선택한 순간에만 새 preset profile이 current draft에 적용된다.

- `preset_name` change: 해당 preset profile 전체를 merge한다.
- `manual_tickers -> preset` change: 현재 선택된 preset profile을 적용한다.
- preset 적용 후 ordinary field edit: 사용자가 자유롭게 override하며 rerun 없이 local draft에
  남긴다.
- 다른 preset change: 새 base + override로 preset-owned field를 다시 초기화한다.
- 같은 preset을 유지한 ordinary rerender / validation error: 값을 다시 덮어쓰지 않는다.

### UI Feedback Contract

- preset field 아래에 마지막 적용 결과를 한 줄로 표시한다.
- `strategy_default`: `전략 기본 규칙을 적용했습니다.`
- `validated_override`: `검증된 프리셋 설정을 적용했습니다.`
- 별도 modal이나 confirmation step은 만들지 않는다. select change 자체가 명시적 적용 행동이다.
- 사용자가 이후 값을 수정해도 `preset_name`은 유지한다. preset은 immutable lock이 아니라
  시작 profile이므로 custom edit를 허용한다.
- React는 `application_kind`를 계산하지 않고 Python model의 label과 values만 사용한다.

### Error And Safety Contract

- Python은 preset profile의 field id가 current schema에 없거나 option / range / type 계약을
  위반하면 workspace build test에서 실패하게 한다.
- forged intent에 preset profile 적용을 신뢰하지 않고 submit 시 기존 Python validation과
  payload projection을 다시 실행한다.
- preset change 자체는 runner, Run History, registry, saved JSONL을 호출하지 않는다.
- validation error, 실행 실패, stale result 보존은 기존 Level1 계약을 유지한다.

### Files And Ownership

- Modify `app/web/backtest_common.py`
  - legacy note에 이미 명시된 GTAA evidence-backed overrides를 canonical parameter map으로 승격
- Modify `app/services/backtest_single_settings_workspace.py`
  - pure preset profile builder, schema-safe patch, read-model contract와 initial precedence
- Modify `app/web/backtest_single_settings_workspace.py`
  - canonical parameter map runtime injection과 Python fallback preset application
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts`
  - preset profile / application feedback read-model type
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
  - generic preset patch reducer, preset-mode transition, feedback render
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
  - compact feedback copy style와 760px contract
- Modify focused service / boundary tests and active task documents
  - RED/GREEN, Browser QA, closeout evidence

### TDD And QA Contract

- RED service tests는 모든 named preset에 complete profile이 있고 current schema field만 포함하는지
  확인한다.
- RED GTAA tests는 U3 / U1 / U5 / Top-3 / Top-2 ADV20이 문서화된 override를 투영하고,
  ordinary GTAA preset은 base profile로 이전 값 누출을 제거하는지 확인한다.
- RED strict-factor tests는 preset change가 factor / overlay / risk base 값을 복원하되 start/end와
  explicit prefill은 보존하는지 확인한다.
- RED frontend boundary tests는 generic preset patch, manual-to-preset application,
  `strategy_default` / `validated_override` feedback과 React-side strategy conditions 부재를 요구한다.
- GREEN 후 focused settings / boundary / service contract tests, React production build,
  target py_compile, `git diff --check`를 실행한다.
- Browser desktop QA는 Equal Weight, GTAA base, GTAA U3, GTAA Top-2 ADV20, Quality + Value Annual의
  preset change와 사용자 edit 후 재선택을 확인한다.
- 760px QA는 feedback, settings grid, multi-select, CTA와 iframe horizontal overflow 0을 확인한다.

### 9차 Acceptance Criteria

1. 모든 named preset 선택은 strategy / variant base profile 전체를 deterministic하게 적용한다.
2. evidence-backed GTAA preset은 문서화된 override를 정확히 적용한다.
3. preset이 바뀌면 이전 preset이나 사용자 수정의 preset-owned 값이 누출되지 않는다.
4. 검증 시작일 / 종료일과 manual ticker draft는 preset 변경으로 소실되지 않는다.
5. 저장 replay / prefill의 explicit values는 initial preset profile보다 우선한다.
6. preset 적용 뒤 사용자는 개별 값을 수정할 수 있고 같은 preset rerender가 이를 덮어쓰지 않는다.
7. React는 전략별 preset 숫자, validation, payload 또는 Gate를 계산하지 않는다.
8. Python fallback은 같은 preset profile과 적용 semantics를 사용한다.
9. focused tests, React build, py_compile, diff-check와 desktop / 760px Browser QA를 통과한다.
10. protected JSONL, `.superpowers/`, generated screenshot은 stage/commit하지 않는다.

### 9차 Out Of Scope

- 근거 없는 strategy tuning 또는 신규 preset 추가
- factor formula, strategy algorithm, DB / ingestion / historical universe 변경
- preset을 immutable saved setup으로 바꾸는 기능
- Portfolio Mix preset / role / weight redesign
- Level2 / Final Review route와 Gate 변경
- broker order, live approval, account sync, auto rebalance

## 10차 Corrective Design: Result Evidence And Level2 Handoff Workspace

### 이걸 하는 이유?

현재 Level1은 실행 버튼 아래에 실행 전에도 Step 3 판단 surface를 노출하고, 실제 결과는
`상세 근거` expander 안에서 탭·표·차트·raw meta가 서로 다른 언어와 정밀도로 분산된다.
또한 benchmark, ETF 운용 가능성, 유동성, rolling / split / OOS처럼 Level2가 실제로
검증해야 할 질문 일부가 Level1 blocker로 읽혀, “Level1에서 실행 가능한 결과를 만들었는가”와
“Level2에서 실전 검증을 통과했는가”가 섞여 있다.

10차의 목적은 결과를 더 많이 노출하는 것이 아니라 다음 사용자 흐름을 한 화면에서 명확히
끝내는 것이다.

1. 방금 실행한 설정과 결과가 서로 일치하는지 확인한다.
2. 성과와 위험, 현재 보유와 최신 신호 기준 목표 구성을 이해한다.
3. Level1에서 고쳐야 하는 기술 문제와 Level2에서 검증할 질문을 구분한다.
4. 기술적으로 재현 가능한 결과만 Practical Validation으로 인계한다.

### Confirmed Current Audit

- `app/web/backtest_result_display.py`는 약 4,500줄이며 expander 10개, `st.tabs` 호출 5개,
  dataframe 44개, chart 4개, metric 79개를 직접 조립한다.
- `_render_last_run()`은 result bundle 존재 여부를 확인하기 전에
  `render_backtest_analysis_decision_surface(workspace)`를 호출하므로 실행 전에도 Step 3가
  나타난다.
- 실제 상세 결과는 `st.expander("상세 근거")` 아래 Summary, Equity Curve, Balance Extremes,
  Period Extremes, strategy-specific selection / universe / policy / swing, Result Table, Meta로
  분산된다.
- 같은 연환산 수익률이 decision surface에서는 `0.249`, 상세 header에서는 `24.9%`처럼
  서로 다른 표기로 중복된다.
- current readiness builder가 실행 계약과 practical-validation 질문을 한 verdict에 섞어
  benchmark / ETF / liquidity / rolling 근거 부족을 Level1 blocker처럼 투영한다.
- result rows에는 `End Ticker`, `Next Ticker`, `Next Weight` 또는 `Next Balance`,
  `Added Ticker`, `Removed Ticker`, `Cash`, `Rebalancing` 계열 정보가 이미 있어 별도
  broker/account integration 없이도 backtest-simulated current / target snapshot을 만들 수 있다.
- `_render_real_money_details_legacy()`는 current primary route에서 사용되지 않는 대형 legacy
  renderer다. 참조와 contract test로 미사용을 증명한 뒤에만 제거할 수 있다.

### Considered Approaches

#### A. 판단 흐름형 단일 Result Workspace — Selected

- KPI, 통합 차트, 보유·목표 구성, 인계 상태, 검증 질문, 사용자 표, 기술 부록을 한 흐름으로 둔다.
- 장점: 사용자가 결과 이해부터 다음 행동까지 한 번에 끝내며 Level2/3와 같은 시각 언어를 쓴다.
- 단점: 기존 상세 renderer를 pure read model과 presentation으로 분해해야 한다.

#### B. 기존 탭을 React로 시각 교체

- 장점: legacy section 순서를 비교적 쉽게 보존한다.
- 단점: 결과 이해가 탭 탐색에 계속 의존하고 stage ownership 혼합을 해결하지 못한다.

#### C. KPI와 차트만 상단으로 이동

- 장점: 변경 범위가 가장 작다.
- 단점: holdings, Level2 question, raw table hierarchy가 그대로 남아 실사용 흐름이 완성되지 않는다.

사용자 승인: 2026-07-18. 10차는 A를 기준으로 한다.

### Product Question And Stage Ownership

Level1의 질문은 다음 하나로 고정한다.

> 이 설정으로 유효하고 재현 가능한 백테스트 결과를 만들었으며 Practical Validation에
> 인계할 수 있는가?

Level1은 전략의 투자 적합성을 최종 판정하지 않는다. Level1에서 인계를 막는 조건은 다음뿐이다.

- 아직 실행하지 않음
- 최근 실행 실패
- current settings fingerprint와 result fingerprint 불일치
- result identity 또는 core result contract 손상 / 누락
- development strategy이거나 callable Level2 handoff handler 부재

다음 항목은 Level1 blocker가 아니라 Level2 validation question이다.

- benchmark 비교와 drawdown 해석
- rolling / split / OOS / regime 검증
- 거래비용, turnover, slippage 현실성
- 유동성, ETF AUM / spread, 실제 운용 가능성
- concentration, overlap, 구성 위험
- 최신 데이터 replay와 source completeness
- 방법론 또는 evidence adapter 개발 필요성

따라서 current `build_next_step_readiness_evaluation()`의 혼합 verdict는 구현 시 다음 두
projection으로 분리한다.

1. `technical_handoff_readiness`: Level1이 소유하는 실행·동일성·계약·handler 상태
2. `level2_validation_questions`: Level2가 검증할 질문과 현재 보유 evidence

Level2는 이 질문을 받아 최신 데이터로 검증하고, unresolved actionable / critical engineering /
missing contract가 남지 않을 때만 Final Review eligibility를 만든다. Level1이 practical
validation signal을 미리 PASS/FAIL로 판정하지 않는다.

### User-Facing Handoff States

Level1 결과 workspace는 pass/fail 대신 다음 상태를 사용한다.

- `Level2 인계 가능`: fresh success, core contract valid, callable handoff handler 존재
- `재실행 필요`: 설정이 바뀌어 보존된 결과가 reference-only이거나 이전 실행 이후 새 실행 실패
- `결과 준비 필요`: 미실행, 첫 실행 실패, core result contract 불완전
- `인계 기능 미지원`: development strategy 또는 callable handler 부재

`재실행 필요`와 `결과 준비 필요`는 전략의 성과가 나쁘다는 뜻이 아니다. technical handoff가
아직 준비되지 않았다는 뜻으로만 설명한다.

### Result Lifecycle And Atomic Refresh

#### Initial State

- 실행 전에는 Step 3/result/decision area를 렌더링하지 않는다.
- 설정 workspace와 `이 설정으로 백테스트 실행` action까지만 보인다.

#### First Run

- 실행 중에는 action 아래에 진행 상태만 보인다.
- 아직 성공한 result가 없으므로 빈 KPI, 빈 chart, 빈 action board를 만들지 않는다.
- 성공하면 complete read model을 한 번에 표시한다.
- 실패하면 설정 영역 가까이에 이해 가능한 error와 retry action만 표시한다.

#### Settings Changed After Success

- 이전 성공 결과는 `이전 설정 결과 · 참고용`으로 보존한다.
- result fingerprint와 current settings fingerprint 차이를 명시한다.
- stale result에서는 Level2 handoff action을 잠근다.

#### Rerun

- 이전 성공 결과를 유지한 채 `새 설정으로 실행 중` 상태를 덧씌운다.
- rerun 성공 시 같은 result workspace surface의 KPI, chart, holdings, tables, evidence,
  handoff state를 새 `run_result_id` 기준으로 atomic replace한다. 기존 validation registry row를
  덮어쓰지 않는다.
- rerun 실패 시 이전 결과를 reference로 유지하고 error를 표시한다. 실패 draft는 이전 결과를
  fresh로 만들지 않으며 Level2 handoff는 계속 잠긴다.

### Result Workspace Information Architecture

결과 화면의 first-read 순서는 다음으로 고정한다.

1. **성과 요약**
   - 검증 기간, 누적/연환산 수익률, 최대 낙폭, 위험 대비 수익, 변동성
   - 값은 Python이 사용자 표시 단위로 formatting하고 React는 raw decimal을 변환하지 않는다.
2. **전략과 기준의 흐름**
   - net strategy와 benchmark를 같은 SVG chart에 표시한다.
   - high / low / maximum drawdown marker와 기간을 함께 제공한다.
   - benchmark가 없으면 strategy-only chart를 그리고 benchmark 검증을 Level2 질문으로 남긴다.
3. **현재 보유와 최신 신호 기준 목표 구성**
   - backtest-simulated current allocation과 latest available signal target을 나란히 비교한다.
   - broker account나 실제 주문으로 오해하지 않도록 정의와 기준일을 함께 표시한다.
4. **Level2 인계 상태와 검증 질문**
   - Level1 technical handoff 상태를 먼저 설명한다.
   - Level2에서 확인할 질문은 목적별 lane으로 분리한다.
5. **목적별 검증 근거**
   - 성과·위험, 선택·보유, 실행 현실성, 데이터 신뢰 4개 group을 사용한다.
6. **사용자용 결과 표**
   - 성과 시계열과 보유 변화 표를 읽기 쉬운 column contract로 제공한다.
7. **기술 부록**
   - raw `result_df`, raw meta, history compatibility detail만 disclosure 안에 둔다.

상단 first-read에는 raw job/status/row count를 주인공으로 올리지 않는다. 진단값은 사용자가
문제를 이해하거나 재현할 때 필요한 보조 근거로만 기술 부록에 둔다.

### Pure Read Model Contract

새 pure service를 추가한다.

```text
app/services/backtest_analysis_result_workspace.py
```

Python은 다음 JSON-ready contract를 완성해 React와 fallback에 동일하게 전달한다.

```text
result_workspace = {
  lifecycle: {
    state,
    is_stale,
    is_running,
    result_fingerprint,
    current_settings_fingerprint,
    display_label,
    error,
  },
  identity: {
    run_result_id,
    candidate_source_id,
    validation_result_id,
    strategy_name,
    variant_name,
    run_at,
    period_label,
  },
  performance_summary: [...],
  chart: {
    strategy_series,
    benchmark_series,
    markers,
    benchmark_missing_reason,
  },
  holdings: {
    as_of,
    current_allocation,
    target_allocation,
    additions,
    removals,
    cash,
    status,
    explanation,
  },
  technical_handoff_readiness: {
    state,
    reasons,
    can_handoff,
    action,
  },
  level2_validation_questions: [...],
  evidence_groups: [...],
  performance_rows: [...],
  holding_change_rows: [...],
  technical_appendix: {
    row_count,
    columns,
    prepared_rows,
    meta_rows,
  },
}
```

- `run_result_id`는 Level1 실행 결과의 필수 identity다.
- `candidate_source_id`와 `validation_result_id`는 handoff 전에는 비어 있을 수 있다.
  Level2 source 등록 성공 후에는 `validation_result_id`를 top-level handoff identity로 반환해
  Practical Validation의 read model, action, history를 같은 record에 연결한다.
- 새 rerun은 새 `run_result_id`를 만들며 append-only validation registry row를 in-place
  overwrite하지 않는다. 동일 source/profile 재사용 여부는 기존 Level2 registration contract가
  결정한다.
- React는 raw status를 분류하거나 Gate, percentage, allocation weight를 계산하지 않는다.
- read model builder는 strategy-specific raw column 차이를 흡수하고 unsupported evidence에는
  빈 추정값 대신 explicit unavailable reason을 준다.
- `technical_appendix`도 DataFrame 객체가 아니라 JSON-ready rows와 metadata만 가진다.
  user table은 stable column contract와 bounded page를 쓰고, full raw DataFrame/history export가
  필요하면 Python adapter가 기존 compatibility disclosure에서 별도로 연결한다.
- 동일 read model을 React unavailable fallback이 사용해 상태, count, 문구, action semantics가
  달라지지 않게 한다.

### Holdings And Target Allocation Contract

#### Meaning

- `현재 보유`: 마지막 valuation row 기준 backtest-simulated allocation이다.
- `목표 구성`: 마지막 valid signal/rebalance row 기준 latest available signal target이다.
- 둘 다 실제 broker account, 투자 추천, 주문 지시가 아니다.

#### Source Priority

- current tickers: latest valuation row의 `End Ticker`와 end balance/weight 계열
- target tickers: last valid signal/rebalance row의 `Next Ticker`
- target weight: explicit `Next Weight` 우선
- explicit weight가 없고 `Next Balance / total` contract가 성립할 때만 Python이 weight를 계산
- 계산 근거가 불충분하면 weight를 만들지 않고 `비중 근거 없음`으로 표시

#### Edge Cases

- latest row가 rebalance row가 아니면 미래 신호를 만들지 않고
  `다음 리밸런싱까지 현재 구성 유지`로 표시한다.
- cash-only 결과는 empty state가 아니라 `현금 100%`로 표시한다.
- holdings column이 없으면 strategy 결과 계약의 부재 이유를 명시한다.
- Portfolio Mix는 component allocation을 먼저 표시한다. component별 target evidence가 있을 때만
  underlying ticker contribution을 aggregate하며, 일부만 있으면 partial evidence로 표시한다.

### Chart And User Table Contract

새 chart dependency를 추가하지 않는다. Level3 Final Review의
`DecisionBriefCharts.tsx`와 같은 SVG visual language를 재사용한다.

- strategy series는 비용 반영 net curve를 우선한다.
- benchmark series는 같은 시작점을 기준으로 비교 가능하게 정규화한 projection을 Python이 준다.
- chart는 tooltip/legend에서 사용자 표시 단위를 사용하고 raw dataframe column name을 노출하지 않는다.
- high / low / maximum drawdown marker는 계산 근거와 날짜가 있을 때만 표시한다.

사용자용 성과 표 column은 다음으로 제한한다.

- 날짜
- 잔고
- 기간 수익률
- 낙폭
- 보유 수
- turnover
- 비용

보유 변화 표 column은 다음으로 제한한다.

- 날짜
- 상태
- 현재 보유
- 목표 구성
- 편입
- 제외
- 현금

strategy-specific raw column과 full `result_df`는 기술 부록에서만 제공한다.

### Evidence Group Contract

- **성과·위험**: 기간 수익, drawdown, 회복, benchmark 차이
- **선택·보유**: 보유 구성, 변경 이력, 집중도, 선택 빈도
- **실행 현실성**: turnover, transaction cost, liquidity, ETF operability
- **데이터 신뢰**: 계산 기준일, coverage, universe/source, dynamic universe/factor readiness

strategy-specific evidence는 새 top-level tab을 늘리지 않고 위 group의 detail slot에 둔다.

- factor / GTAA / swing selection history → 선택·보유
- dynamic universe / factor readiness → 데이터 신뢰
- policy signal / swing execution log → 선택·보유 또는 실행 현실성

실행 현실성이나 데이터 신뢰 evidence가 부족하더라도 core result contract가 유효하면 Level1
result는 보인다. 부족한 근거는 Level2 질문으로 승격한다.

### React And Python Rendering Boundary

새 component를 추가한다.

```text
app/web/components/backtest_analysis_result_workspace/
```

- React는 read model presentation과 `handoff_to_level2`, disclosure, table pagination 같은 intent만
  담당한다.
- React는 raw status classification, stale 판단, Gate, handler existence, benchmark normalization,
  holdings weight 계산을 하지 않는다.
- `ResizeObserver`로 iframe height를 동기화하고 760px 이하에서 KPI, holdings comparison,
  question lane, table을 단일 열로 전환한다.
- action이 0개면 빈 action board를 렌더링하지 않는다.

`app/web/backtest_result_display.py`는 다음 책임만 남긴다.

- runtime result/meta를 pure service input으로 adapter
- component mount와 validated intent dispatch
- same-read-model Python fallback
- raw technical appendix와 history/replay compatibility 연결

미사용 legacy renderer는 `rg` 참조 검사와 boundary test가 primary/runtime consumer 0개임을
증명한 뒤 별도 implementation unit에서 제거한다.

### Empty, Partial And Error States

- no run: result workspace 자체를 숨긴다.
- first run in progress: 실행 action 아래 progress만 표시한다.
- previous result + rerun: 이전 result를 유지하고 running overlay를 표시한다.
- first run failure: 설정 영역에 error와 retry만 표시한다.
- rerun failure: 이전 result를 reference로 보존하고 error를 표시하며 handoff를 잠근다.
- missing benchmark: strategy-only chart + Level2 benchmark question
- missing holdings: unavailable reason, fake ticker/weight 없음
- missing weights: supported balance contract가 있을 때만 Python derive
- stale result: 모든 first-read 영역에 reference marker를 일관되게 표시
- development strategy: 결과 열람 허용, Level2 handoff는 `인계 기능 미지원`

### Planned Implementation Roadmap

#### 1차. Result Truth / Read Model

- 실행 전 result 숨김과 lifecycle state를 RED로 고정한다.
- Level1 technical handoff blocker와 Level2 validation question을 분리한다.
- performance, chart, current/target holdings, evidence, user tables pure read model을 구현한다.
- 완료 조건: strategy family matrix와 Portfolio Mix가 같은 contract를 만들고 pure tests가 통과한다.

#### 2차. Result Workspace UI

- 새 React result component를 구현한다.
- KPI → chart → holdings → handoff/questions → evidence → tables 순서를 적용한다.
- 완료 조건: React는 presentation/intent만 소유하고 production build와 boundary tests가 통과한다.

#### 3차. Lifecycle / Fallback / Legacy Cleanup

- `_render_last_run()`의 unconditional pre-run Step 3 mount를 제거한다.
- stale/running/success/failure atomic lifecycle과 same-read-model fallback을 연결한다.
- 증명된 미사용 legacy renderer만 제거한다.
- 완료 조건: 이전 성공 보존, rerun atomic replace, error 보존, fallback parity tests가 통과한다.

#### 4차. Runtime QA / Docs / Closeout

- 대표 전략 family 전체와 Portfolio Mix를 실제 실행한다.
- desktop / 760px Browser QA, React build, py_compile, focused/full tests, diff-check를 새로 실행한다.
- canonical finance docs와 active task/root handoff log를 동기화한다.
- 완료 조건: 보호 파일 0 stage/commit, QA evidence와 distinct Korean commits가 남는다.

### TDD And QA Contract

- 모든 feature/bugfix는 RED → GREEN 순서로 진행한다.
- pure unit test는 no-run / fresh / stale / running / first-failure / rerun-failure 상태를 고정한다.
- holdings test는 single ticker, multiple ticker, cash-only, non-rebalance latest row, missing weight,
  partial Portfolio Mix evidence를 포함한다.
- Gate test는 practical-validation signal이 Level1 blocker에 포함되지 않음을 확인한다.
- Level2 question test는 benchmark, ETF, liquidity, rolling/OOS, cost evidence 부족을 보존한다.
- React boundary test는 raw classification, allocation calculation, Gate calculation 부재와
  same-read-model fallback parity를 확인한다.
- representative runtime matrix는 Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum,
  strict factor variants, Portfolio Mix를 포함한다.
- Browser desktop / 760px에서 pre-run Step 3 부재, stale → running → fresh, error preserves old,
  chart, holdings, user tables, Level2 question lane, horizontal overflow 0을 확인한다.
- fresh React production build, target py_compile, focused/full Python tests, `git diff --check`,
  protected-path staged audit를 완료 전 다시 실행한다.

### 10차 Acceptance Criteria

1. 실행 전에는 결과/판단/상세 근거 영역이 보이지 않는다.
2. 설정 변경 후 이전 결과는 참고용으로 보존되고 Level2 handoff는 잠긴다.
3. rerun 중 이전 결과가 사라지지 않으며 성공 시 같은 workspace가 atomic refresh된다.
4. rerun 실패 시 이전 결과와 오류를 함께 보여주고 handoff를 잠근다.
5. Level1 blocker는 실행·fingerprint·core contract·callable handler로 제한된다.
6. benchmark/ETF/liquidity/rolling/OOS/cost 질문은 Level2 validation question으로 분리된다.
7. current holdings와 latest-signal target은 사용자 의미, 기준일, source contract와 함께 표시된다.
8. 사용자가 읽는 KPI/chart/table에는 raw decimal과 raw code column을 그대로 노출하지 않는다.
9. strategy-specific evidence는 4개 목적 group 안에서 같은 visual contract를 사용한다.
10. React unavailable fallback은 동일 read model과 action semantics를 사용한다.
11. desktop / 760px에서 result workflow와 table/chart가 horizontal overflow 없이 동작한다.
12. focused/full tests, React build, py_compile, diff-check와 protected-path audit를 통과한다.

### 10차 Out Of Scope

- broker account holdings, order, live approval, account sync, auto rebalance
- strategy algorithm, factor formula, engine 또는 DB schema 재설계
- 신규 benchmark / historical universe / delisting provider 개발
- Practical Validation 또는 Final Review route 자체 재설계
- Level2 practical-validation 계산을 Level1에서 선실행하는 기능
- raw run/job/status 중심 운영 진단 dashboard

## 11차 Result Interpretation And Schedule Polish

### Why This Corrective Exists

10차 Result Workspace는 결과 계층과 Level1/Level2 소유권을 정리했지만 실제 Browser 사용에서
다음 해석 공백이 남았다.

- `전략과 기준의 흐름` X축에 날짜 label이 없어 기간 안의 위치를 바로 읽기 어렵다.
- 첫 시점 100의 의미는 맞지만 `100 -> 124.9`가 누적 `+24.9%`라는 설명이 충분하지 않다.
- SVG point의 native title은 hover 위치를 비교하기 어렵고 마우스가 떠난 뒤의 명확한 상태도 없다.
- 범례가 `기준지수`라고만 표시되어 실제 SPY 또는 다른 comparator를 알 수 없다.
- current/target holdings는 보이지만 마지막 신호, 실제 rebalance, cadence와 다음 예상 window가 없다.
- `기술 부록`이 raw column과 metadata key/value를 그대로 보여 일반 사용자가 의미를 알기 어렵다.

이 corrective의 목표는 새 분석 기능을 추가하는 것이 아니라 이미 계산된 결과를 시간, 비교 기준,
운용 일정과 계산 근거의 언어로 정확하게 읽게 만드는 것이다.

### Approved Decisions

- architecture는 Python read model + React presentation인 B안을 유지한다.
- 투자금 입력, 달러 환산, 고정 10,000달러 참고값은 추가하지 않는다.
- chart는 첫 공통 시점 100의 normalized index를 유지하고 누적 수익률과의 관계를 설명한다.
- 다음 rebalance는 근거가 있을 때만 month/quarter/year window로 보여주며 exact trading date를
  추측하지 않는다.
- raw metadata는 첫 disclosure에 노출하지 않고 사용자 설명과 원본 추적 정보를 분리한다.

### Chart Read Model Contract

Python은 React가 날짜, 수익률 또는 Benchmark 의미를 추론하지 않도록 다음 projection을 제공한다.

```text
chart: {
  normalized_base: 100,
  normalized_explanation,
  strategy_label,
  benchmark: {
    available,
    label,
    ticker,
    contract_label,
    missing_reason,
  },
  strategy_series,
  benchmark_series,
  timeline_dates,
  desktop_x_ticks: [{date, label}],
  compact_x_ticks: [{date, label}],
  hover_rows: [{
    date,
    strategy_value,
    strategy_value_label,
    strategy_return,
    strategy_return_label,
    benchmark_value,
    benchmark_value_label,
    benchmark_return,
    benchmark_return_label,
  }],
  markers,
}
```

- desktop tick은 시작/종료를 포함해 최대 6개, 760px tick은 시작/중간/종료 최대 3개다.
- tick 날짜는 실제 chart timeline에서 고르며 존재하지 않는 날짜를 만들지 않는다.
- strategy와 Benchmark의 SVG x좌표는 각 series index가 아니라 같은 `timeline_dates` date index를
  사용한다. sparse Benchmark는 실제 관측 date에만 point/path segment를 만들고 날짜 위치를 당기지 않는다.
- normalized return은 `value / 100 - 1`이고 Python이 숫자와 표시 label을 함께 제공한다.
- legend는 `전략 · <strategy label>`과 `기준 · <benchmark label>`을 표시한다.
- direct ticker comparator는 ticker를 표시한다. candidate equal-weight 같은 contract comparator는
  Python이 제공한 contract label을 표시한다. 둘 다 없으면 `기준 없음`을 만들지 않고 missing reason을
  chart 아래에 표시한다.

React SVG는 pointer 위치에서 가장 가까운 `timeline_dates` / `hover_rows` 날짜 하나를 선택한다. hover 중에만 vertical
crosshair와 floating tooltip을 렌더링하고 pointer leave에서 제거한다. tooltip은 날짜, 전략 normalized
index / 누적 수익률, available Benchmark normalized index / 누적 수익률만 표시한다. raw balance와
DataFrame column 이름은 표시하지 않는다. keyboard focus 사용자는 각 point의 accessible title/label을
계속 사용할 수 있다.

### Holdings Schedule Contract

`holdings`에 다음 schedule projection을 추가한다.

```text
schedule: {
  valuation_as_of,
  latest_signal_as_of,
  last_rebalance_as_of,
  cadence_label,
  next_window_label,
  next_window_status,
  explanation,
}
```

Source priority는 다음과 같다.

1. `valuation_as_of`: latest result row의 Date
2. `latest_signal_as_of`: target allocation을 만든 last valid signal row의 Date
3. `last_rebalance_as_of`: `Rebalancing=true`인 마지막 result row의 Date
4. cadence: explicit `rebalance_interval`, `interval`, `rebalance_freq` metadata
5. next window: last rebalance와 explicit cadence가 모두 있을 때만 계산

integer month interval은 마지막 rebalance month에서 N개월 뒤를, explicit monthly/quarterly/annual은
각각 1/3/12개월 뒤를 next window로 계산하고 exact trading day 대신 `YYYY-MM 월말 예상`으로 표시한다.
그 외 frequency는 irregular로 취급한다. irregular,
signal-only, missing cadence, partial Mix는 `다음 일정 확인 필요`를 표시한다. 시장 휴일이나 다음 영업일을
추측하지 않는다.

holdings 첫 줄에는 현재 평가 기준일, 최신 신호일, 마지막 리밸런싱일, 주기, 다음 예상 window를 compact
schedule strip으로 표시한다. 목표 구성 설명은 다음 의미를 유지한다.

> 최신 신호 기준 목표입니다. 다음 리밸런싱 전까지 현재 구성을 유지하며, 새 신호가 동일하면 목표
> 구성도 유지됩니다.

이 정보는 backtest simulation schedule이며 broker 주문, live rebalance 또는 account instruction이 아니다.

### Calculation And Data Basis Contract

visible label `기술 부록`은 `계산 및 데이터 기준`으로 바꾼다. first disclosure는 Python이 만든 사용자용
section만 표시한다.

- **계산 기준**: 실행 방식, 비용 반영, 실제 결과 기간, 결과 행 수
- **데이터 기준**: universe, 가격 기준일/최신성, Benchmark, factor 준비 상태
- **결과 추적**: run result id, configuration fingerprint, lifecycle 상태

각 row는 `label`, `value_label`, `explanation`, `status`를 가지며 raw key를 사용자 label로 사용하지 않는다.
알려진 metadata가 없으면 설명을 지어내지 않고 `확인 가능한 근거 없음`으로 표시한다.

원본 result columns, bounded prepared rows, raw meta는 secondary `원본 필드 보기` disclosure에만 둔다.
React는 raw value를 JSON string으로 first layer에 렌더링하지 않는다. Python fallback도 같은 section 순서와
label을 사용한다. 원본은 개발/감사용이며 사용자 판단의 first-read가 아니다.

### Component And Ownership Changes

- `app/services/backtest_analysis_result_workspace.py`
  - x tick, normalized return, Benchmark identity, hover row, schedule, appendix section 계산 소유
- `app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts`
  - read model exact type 확장
- `ResultWorkspaceChart.tsx`
  - date axis, pointer-only tooltip/crosshair, actual Benchmark legend 표시
- `BacktestAnalysisResultWorkspace.tsx`
  - schedule strip과 `계산 및 데이터 기준` disclosure 표시
- `style.css`
  - tooltip, crosshair, responsive date label/schedule/appendix layout 소유
- `app/web/backtest_analysis_result_workspace_panel.py`
  - same-read-model fallback parity

React는 Benchmark 분류, next schedule 계산, normalized return 계산, metadata meaning mapping을 소유하지
않는다. chart pointer의 nearest-row 선택과 desktop/compact tick 선택만 presentation behavior다.

### Error And Partial States

- strategy curve만 있으면 날짜/hover를 그대로 제공하고 Benchmark missing reason을 표시한다.
- sparse Benchmark는 common-date hover row에만 값이 있고 없는 날짜는 tooltip에서 `-`로 표시한다.
- cadence가 없거나 irregular이면 next window를 만들지 않는다.
- latest signal 또는 last rebalance가 없으면 각각 `확인 가능한 기록 없음`으로 표시한다.
- cash-only와 holdings unavailable도 schedule evidence가 있으면 schedule strip은 유지한다.
- stale result는 schedule, chart, appendix 전체에 기존 reference-only lifecycle을 그대로 적용한다.

### TDD And Browser QA Contract

- RED: desktop/compact x tick, normalized explanation/return, Benchmark ticker/contract/missing case
- RED: hover row common-date/sparse Benchmark projection
- RED: monthly cadence, missing cadence, irregular signal, non-rebalance latest, cash-only, partial Mix schedule
- RED: user appendix sections, raw disclosure separation, unknown metadata omission
- GREEN 뒤 focused result/decision/boundary tests와 full service baseline을 다시 실행한다.
- React production build와 target `py_compile`, `git diff --check`를 실행한다.
- desktop Browser QA에서 x dates, actual Benchmark, pointer enter/move/leave tooltip, schedule와 appendix를 확인한다.
- 760px에서 3개 x tick, tooltip viewport containment, schedule wrap, appendix overflow 0과 ResizeObserver를 확인한다.
- registry, run history, saved JSONL, `.superpowers/`, screenshots와 run artifacts는 stage/commit하지 않는다.

### 11차 Acceptance Criteria

1. chart X축은 실제 날짜를 desktop 최대 6개, 760px 최대 3개 표시한다.
2. normalized 100과 누적 수익률 관계가 사용자 문장으로 설명된다.
3. pointer hover 중에만 날짜/전략/Benchmark 값과 crosshair가 나타난다.
4. legend에 실제 Benchmark ticker 또는 comparator contract label이 표시된다.
5. holdings는 평가일, 최신 신호일, 마지막 rebalance, cadence와 next expected window를 구분한다.
6. 근거 없는 exact rebalance date를 만들지 않는다.
7. `계산 및 데이터 기준` first layer는 raw key/JSON 대신 한국어 의미와 설명을 표시한다.
8. raw columns/meta는 secondary disclosure에만 남는다.
9. React와 Python fallback이 같은 read model 의미를 표시한다.
10. desktop/760px Browser QA, focused tests, builds, compile, diff-check와 protected-path audit를 완료한다.

### 11차 Out Of Scope

- 투자금 입력, 달러 환산, 고정 10,000달러 reference value
- chart zoom/pan/range selector 또는 신규 chart dependency
- broker holdings/order, tax, minimum lot, live/auto rebalance
- market holiday 기반 exact next trading date provider
- strategy algorithm, runtime calculation, DB schema 또는 Level2/Final Review route 재설계

## 12차 Current Selection And Factor Presentation Corrective

### Why This Corrective Exists

11차까지 Level1 설정과 결과 워크스페이스를 React one-shell로 정리했지만 실제 Browser 사용에서
다음 세 회귀가 남았다.

- 전략 또는 설정을 변경해 이전 결과가 stale이 되면 설정 화면 바로 아래에 Streamlit `st.info`,
  `st.warning`, raw refresh job `st.dataframe`이 먼저 나타난다. 이전 결과 보존은 의도된 계약이지만
  이 레거시 운영 표면은 사용자 결과 흐름과 충돌한다.
- `목적과 핵심 설정`의 단일 전략 configuration summary가 현재 선택이 아니라 이전
  `backtest_current_draft_payload`를 읽는다. Quality + Value를 선택해도 이전 GTAA의
  `strategy_key`, `timeframe`, `option`, promotion threshold가 현재 선택의 설정처럼 보인다.
- strict factor multi-select가 payload 원본 key를 visible label로 사용해 `net_margin`,
  `operating_income_yield` 같은 코드 키가 노출되고 긴 항목은 desktop에서도 잘린다.

이 corrective의 목표는 이전 실행 결과를 참고용으로 보존한다는 lifecycle 계약은 유지하면서
현재 선택, 이전 실행, 사용자 표시명, 원본 기술 근거의 소유 경계를 분리하는 것이다.

### Approved Decisions

- B안인 Python-owned user presentation contract를 적용한다.
- 전략 또는 설정 변경 시 이전 성공 결과는 삭제하지 않고 참고용으로 보존한다.
- 단일 전략 context의 raw configuration summary는 제거한다. 현재 선택은 전략 catalog와 바로 아래
  settings editor가 소유하며 이전 draft payload를 현재 설정처럼 재표시하지 않는다.
- stale / price refresh 안내는 Result Workspace의 lifecycle 안내 하나로 통합한다. 설정과 결과 사이의
  Streamlit 안내와 raw refresh job table은 제거한다.
- factor payload value는 기존 원본 key를 유지하되 visible label은 `한국어 의미 + 표준 약어`를 사용한다.
  일반적 약어가 없는 항목은 한국어 의미만 표시한다.
- raw factor key와 refresh job detail은 first-read가 아니라 secondary technical evidence에서만 확인한다.

### Current Selection Contract

Single Strategy context surface는 다음만 표시한다.

1. Level1 질문과 Single Strategy / Portfolio Mix 진입 선택
2. 목적별 전략 catalog와 현재 선택 표시
3. 바로 이어지는 현재 선택 전용 settings editor

`configuration_summary`는 Single Strategy context에 렌더링하지 않는다. 현재 설정값은 settings read
model이 소유하고, 실행된 값은 Result Workspace의 계산 및 데이터 기준이 소유한다. 따라서 아직 실행하지
않은 current draft와 이전 run payload를 하나의 summary에서 섞지 않는다.

Portfolio Mix는 component와 weight를 한눈에 확인해야 하므로 구성 요약을 유지할 수 있지만 raw key/value
dictionary를 그대로 표시하지 않는다. Python이 만든 사용자 label/value row만 React가 표현한다.

전략 catalog에서 다른 전략을 선택해도 이전 `backtest_current_draft_payload`와 성공 결과는 감사와 참고를
위해 session에 보존할 수 있다. 단, read model은 payload의 `strategy_key`가 현재 선택의 concrete strategy와
일치하지 않으면 current configuration으로 투영하지 않는다.

### Stale Result Lifecycle Contract

전략, variant 또는 설정 변경 후 이전 결과는 다음 의미로 유지한다.

```text
current settings
  -> fingerprint mismatch
  -> previous successful result remains visible
  -> result lifecycle = stale / reference_only
  -> Level2 handoff disabled
  -> rerun success atomically replaces result
```

설정 editor와 Result Workspace 사이에 별도 Streamlit reset notice를 렌더링하지 않는다.
`_render_backtest_rerun_required_notice()`의 warning과 DataFrame도 first-read에서 제거한다. Result Workspace는
Python이 제공한 `result_freshness`, `reference_reason`, `reference_message`를 사용해 상단에 다음과 같은
compact lifecycle strip 하나만 표시한다.

- 설정 변경: `이전 설정 결과 · 참고용`
- 가격 데이터 갱신: `가격 갱신 전 결과 · 참고용`
- 재실행 실패: `이전 성공 결과 유지 · 참고용`

refresh message, saved row count, target end, collection start, ticker count는 사용자 판단의 first-read가
아니다. 값이 필요하면 `계산 및 데이터 기준 > 원본 근거`의 secondary evidence로만 남긴다. raw job/status
dashboard를 새로 만들지 않는다.

### Factor Presentation Contract

Python settings schema의 option은 계산용 `value`와 사용자용 `label`을 분리한다.

```text
{
  value: "roe",
  label: "자기자본이익률 (ROE)"
}
```

대표 label은 다음 원칙을 따른다.

- `roe` -> `자기자본이익률 (ROE)`
- `roa` -> `총자산이익률 (ROA)`
- `net_margin` -> `순이익률`
- `asset_turnover` -> `자산회전율`
- `current_ratio` -> `유동비율`
- `book_to_market` -> `장부가치 대비 시가`
- `earnings_yield` -> `이익수익률`
- `ocf_yield` -> `영업현금흐름 수익률`
- `operating_income_yield` -> `영업이익 수익률`

모든 Quality / Value option에 label을 제공한다. React의 검색은 label과 raw value를 함께 검색할 수 있지만
버튼, 선택 요약, chip에는 label만 표시한다. submit intent에는 기존 value array를 그대로 보내 runner와
저장 payload 계약을 바꾸지 않는다.

compact factor option grid는 desktop과 760px에서 기본 2열을 사용하고 작은 mobile 폭에서 1열로
전환한다. 각 button text는 여러 줄을 허용하고 `min-width: 0`, `overflow-wrap: anywhere`, 충분한
line-height를 적용해 clip 또는 horizontal overflow가 없게 한다.

### Component And Ownership Changes

- `app/services/backtest_single_settings_workspace.py`
  - factor value -> user label map과 option projection 소유
- `app/services/backtest_analysis_decision_workspace.py`
  - Single Strategy context configuration summary suppression 또는 user summary projection 소유
- `app/services/backtest_analysis_result_workspace.py`
  - stale/reference reason과 사용자 lifecycle message projection 소유
- `app/web/backtest_single_strategy.py`
  - 설정과 결과 사이 legacy reset notice 제거
- `app/web/backtest_result_display.py`
  - raw rerun warning/DataFrame first-read 제거, same-read-model result renderer만 호출
- `app/web/components/backtest_analysis_decision_workspace/frontend/`
  - Python label 표시, compact option wrap, raw configuration dictionary 부재
- `app/web/components/backtest_analysis_result_workspace/frontend/`
  - reference-only lifecycle strip 표시
- Python fallback
  - 동일 label, summary suppression, stale lifecycle 의미 유지

React는 strategy key 일치 판정, stale 원인 분류, factor key 번역, Gate 또는 payload 변환을 소유하지
않는다. Python이 value/label, lifecycle state와 user message를 제공하고 React는 presentation과 intent만
담당한다.

### Error And Partial States

- current strategy와 draft payload가 다르면 current context에는 이전 payload summary를 표시하지 않는다.
- result bundle이 없으면 stale/reference 안내도 표시하지 않는다.
- refresh detail이 없더라도 generic `이전 설정 결과 · 참고용`을 표시할 수 있다.
- factor option label map에 알 수 없는 extension key가 들어오면 계산 value는 보존하고 사용자 label은
  안전한 title 형태로 fallback한다. raw snake_case를 그대로 first-read에 노출하지 않는다.
- React component가 없으면 Python fallback도 한국어 factor label과 compact stale 안내를 사용한다.

### TDD And Browser QA Contract

- RED: Quality + Value 선택 중 이전 GTAA draft가 context summary에 노출되지 않는다.
- RED: Single Strategy context에 raw `strategy_key`, `timeframe`, `option`, promotion key가 없다.
- RED: stale result가 보존되지만 Streamlit reset notice와 refresh DataFrame을 렌더링하지 않는다.
- RED: settings change / price refresh / rerun failure reference reason이 one lifecycle message로 투영된다.
- RED: 모든 Quality / Value factor option은 user label과 unchanged raw value를 가진다.
- RED: submitted factor array는 기존 raw key payload와 정확히 같다.
- GREEN 뒤 focused settings / decision / result / boundary tests와 full service baseline을 새로 실행한다.
- React production build, target `py_compile`, `git diff --check`를 실행한다.
- desktop Browser QA에서 Quality + Value 선택, 이전 GTAA result 보존, raw summary/legacy table 부재,
  factor label과 2열 wrap을 확인한다.
- 760px에서 factor option 2열, 작은 label wrap, lifecycle strip, horizontal overflow 0과
  ResizeObserver height를 확인한다.
- registry, run history, saved JSONL, `.superpowers/`, screenshots와 run artifact는 stage/commit하지 않는다.

### 12차 Acceptance Criteria

1. 현재 선택과 이전 draft/result가 같은 설정으로 오인되지 않는다.
2. Quality + Value 선택 화면에 이전 GTAA raw configuration summary가 보이지 않는다.
3. stale 결과는 참고용으로 보존되지만 설정 아래 legacy Streamlit notice/table은 보이지 않는다.
4. reference-only 상태와 재실행 필요성은 Result Workspace lifecycle strip 하나로 이해할 수 있다.
5. factor 선택 화면은 한국어 의미와 표준 약어를 사용하고 raw snake_case를 first-read에 노출하지 않는다.
6. factor payload value와 runner contract는 변경되지 않는다.
7. desktop / 760px에서 긴 factor label clip과 horizontal overflow가 없다.
8. React unavailable fallback도 동일 상태와 label 의미를 유지한다.
9. focused/full tests, React build, py_compile, diff-check와 protected-path audit를 통과한다.

### 12차 Out Of Scope

- factor 계산식, ranking, weighting, universe, strategy runtime 또는 DB schema 변경
- 이전 성공 결과 삭제 또는 run history rewrite
- raw run/job/status 중심 운영 진단 dashboard 추가
- 신규 factor/provider/historical universe 개발
- Level2 Practical Validation 또는 Final Review route 재설계
- broker order, live approval, account sync, tax, auto rebalance

## 13차 Backtest Workflow Top Shell Redesign

### Why This Corrective Exists

Level1~3의 각 workspace는 blue-gray one-shell 시각 언어와 단계별 질문을 갖게 됐지만,
Backtest 페이지 최상단은 초기 Streamlit 구조를 그대로 유지한다.

- 큰 `Backtest` 제목과 긴 설명이 실제 작업 시작점보다 먼저 공간을 차지한다.
- 설명은 현재 3단계 계약과 맞지 않는 `Pre-Live`, `Portfolio Proposal`을 계속 언급한다.
- `후보 선정 흐름` 제목과 별도 설명이 위의 페이지 설명을 다시 반복한다.
- native `st.pills`의 빨간 밑줄은 Level1~3의 blue-gray visual language와 충돌한다.
- 탭 이름만으로는 각 단계에서 사용자가 무엇을 끝내야 하는지 알기 어렵다.

이 corrective는 상단의 두 legacy block을 하나의 React workflow shell로 통합한다.
각 Level 내부의 판단 UI나 Gate를 최상단에서 다시 계산하지 않고, 현재 위치와 단계의 책임만
명확하게 설명한다.

### Approved Visual Direction

사용자는 visual companion의 A안인 `통합 Decision Header + 단계 레일`을 승인했다.

```text
BACKTEST DECISION PIPELINE
후보를 만들고 검증해 최종 투자 판단까지 이어갑니다
각 단계에서 해야 할 일을 분리하고, 검증된 근거만 다음 판단으로 넘깁니다.

현재 단계 · LEVEL 1
후보 분석
전략을 실행하고 비교해 실전 검증 후보를 준비합니다.

[01 후보 분석] [02 실전 검증] [03 최종 검토]
```

기존 `Backtest` title / caption, `후보 선정 흐름` heading / caption, red underline pills는
primary route에서 제거한다. 새 shell 하나가 page identity, current stage context와 stage navigation을
함께 제공하고 바로 아래에 선택된 Level workspace가 이어진다.

### Product Contract

최상단의 질문은 `전체 workflow에서 지금 어디에 있고 무엇을 끝내는가?`다.
각 Level의 판단 결과, blocker count, registry count 또는 eligibility를 다시 요약하지 않는다.

| 단계 | 사용자 label | 현재 단계에서 끝낼 일 |
|---|---|---|
| Level1 | 후보 분석 | 전략을 실행하고 비교해 실전 검증 후보를 준비한다. |
| Level2 | 실전 검증 | 최신 데이터로 검증하고 해결할 일과 넘길 판단을 구분한다. |
| Level3 | 최종 검토 | 검증된 한계와 Monitoring 이관 조건을 바탕으로 최종 판단한다. |

추천 보조 기능은 우측 `현재 단계` context card 하나다. 단계 번호, 사용자 label과 위의 완료 목적만
표시한다. job, saved row, 실패 수, 후보 수 같은 운영 진단값은 표시하지 않는다.

세 단계는 기존과 같이 모두 직접 이동할 수 있다. 최상단 shell은 진행 Gate가 아니며 Level2 entry
또는 Final Review eligibility를 추론하거나 차단하지 않는다. 실제 Gate와 상태는 각 Level의 Python
read model이 소유한다.

### Read Model And Ownership

새 pure service를 추가한다.

```text
app/services/backtest_workflow_shell.py
```

service는 다음 JSON-ready projection을 만든다.

```text
headline
description
active_stage
active_stage_index
active_stage_context:
  level_label
  title
  responsibility
stages[]:
  stage_key
  level_label
  title
  english_title
  responsibility
  is_active
```

Python ownership:

- 허용된 stage key와 표시 순서
- current stage 정규화
- stage별 사용자 label, 책임 문장과 active state
- React intent allow-list 검증
- Streamlit session state와 기존 route dispatcher 갱신
- React unavailable fallback

React ownership:

- hero, current-stage card와 stage rail presentation
- stage card click intent
- focus / hover / selected 시각 상태
- responsive layout과 ResizeObserver height sync

React는 raw session state로 stage를 새로 분류하거나 route, Gate, eligibility, completion을 계산하지
않는다. intent는 다음 최소 계약만 사용한다.

```text
{type: "select_stage", stage_key: "Practical Validation"}
```

Python adapter는 `stage_key`가 `BACKTEST_WORKFLOW_PANEL_OPTIONS`에 있을 때만 기존
`request_backtest_panel()` 또는 동등한 route owner를 호출한다. 잘못된 key와 중복 intent는 무시한다.

### Component And Route Boundary

- `app/services/backtest_workflow_shell.py`
  - 단계 catalog, active-stage normalization과 read model 소유
- `app/web/backtest_workflow_shell.py`
  - session adapter, validated intent와 component/fallback mount 소유
- `app/web/backtest_workflow_shell_panel.py`
  - 같은 read model을 사용하는 Python fallback 소유
- `app/web/components/backtest_workflow_shell/`
  - React presentation과 `select_stage` intent 소유
- `app/web/backtest_page.py`
  - native pills selector를 새 shell renderer로 교체하고 기존 stage dispatch 유지
- `app/web/streamlit_app.py`
  - legacy `st.title("Backtest")`와 obsolete caption 제거

기존 `BACKTEST_STAGE_ANALYSIS`, `BACKTEST_STAGE_PRACTICAL_VALIDATION`,
`BACKTEST_STAGE_FINAL_REVIEW`, legacy route normalization과 Level workspace renderer는 바꾸지 않는다.
이 shell은 Level1 전용 component가 아니라 세 Level이 공유하는 page-level navigation이다.

### Responsive And Accessibility Contract

- desktop: hero는 설명 / current-stage card 2열, stage rail은 동일 폭 3열이다.
- 760px: hero는 1열로 줄바꿈하고 stage rail 3열을 유지하되 긴 영어 label이 clip되지 않는다.
- 520px 이하: stage rail은 세로 1열로 전환한다.
- component body와 stage card는 `min-width: 0`, multi-line text와 horizontal overflow 0을 만족한다.
- stage card는 button semantic, keyboard focus, `aria-current="step"`을 제공한다.
- selected는 색만이 아니라 border, `CURRENT` label과 `aria-current`로 구분한다.
- content 높이는 ResizeObserver로 Streamlit iframe에 동기화한다.
- reduced-motion 환경에서는 hover/selection transition을 제거한다.

### Error And Fallback States

- session의 current stage가 허용 목록에 없으면 Level1로 정규화한다.
- active stage metadata가 누락되면 raw key를 노출하지 않고 안전한 사용자 fallback label을 쓴다.
- component가 load되지 않으면 Python fallback이 같은 headline, current responsibility와 3단계 이동을
  제공한다.
- intent 처리 중 rerun이 발생해도 shell 아래의 선택 workspace만 교체하며 별도 loading dashboard나
  빈 action board를 만들지 않는다.
- stage navigation은 persistence를 쓰지 않으므로 registry, Run History와 saved JSONL을 수정하지 않는다.

### TDD And Browser QA Contract

- RED: 3개 stage가 정확히 한 번, 고정 순서로 projection된다.
- RED: unknown current stage는 Level1로 정규화되고 active stage는 하나뿐이다.
- RED: stage responsibility와 사용자 label은 Python projection에 존재한다.
- RED: React source는 route / Gate / raw session 분류를 소유하지 않는다.
- RED: invalid / duplicate intent는 기존 route handler를 호출하지 않는다.
- RED: primary Backtest entry에는 legacy title, obsolete caption, `st.pills`가 없다.
- GREEN 뒤 focused shell / route / boundary tests와 영향 범위 회귀를 새로 실행한다.
- React production build, target `py_compile`, `git diff --check`를 실행한다.
- desktop Browser QA에서 hero 2열, current Level context, 세 stage 이동과 workspace dispatch를 확인한다.
- 760px에서 hero 1열, stage rail 3열, label wrap, iframe height와 horizontal overflow 0을 확인한다.
- screenshots는 generated artifact로 보존하고 commit하지 않는다.

### 13차 Acceptance Criteria

1. 초기 Streamlit `Backtest` title/caption과 별도 `후보 선정 흐름` block이 보이지 않는다.
2. 하나의 blue-gray React shell에서 workflow 목적, 현재 단계 책임과 3단계 이동을 이해할 수 있다.
3. stage 이동 후 hero의 current-stage card와 아래 workspace가 같은 단계로 갱신된다.
4. Python이 stage allow-list, current state와 route dispatch를 계속 소유한다.
5. 최상단은 각 Level의 Gate, blocker, count 또는 투자 판단을 중복 계산하지 않는다.
6. React unavailable fallback도 같은 단계 의미와 이동을 제공한다.
7. desktop / 760px에서 clip과 horizontal overflow가 없고 keyboard / aria-current 계약을 만족한다.
8. focused tests, React build, py_compile, diff-check, Browser QA와 protected-path audit를 통과한다.

### 13차 Out Of Scope

- Level1/2/3 내부 workflow, 판단 Gate, candidate count 또는 registry contract 변경
- stage completion percentage, notification center, job/run/status dashboard 추가
- legacy route 삭제 또는 Practical Validation / Final Review route 재설계
- strategy runtime, DB schema, provider, broker, live approval 또는 auto rebalance 변경

## 14차 Corrective Design: Stage-Local Legacy Title Removal

### Problem And Root Cause

Level1은 page-level workflow shell 아래에서 React Decision Workspace hero가 질문과 설명을 바로
소유한다. 반면 Level2와 Level3는 각각 `render_practical_validation_workspace()`와
`render_final_review_workspace()`가 큰 Streamlit stage title/caption을 먼저 렌더링한 뒤, React hero가
같은 단계 이름과 질문을 다시 보여준다. 따라서 문제는 React 디자인 부족이 아니라 stage-local title
owner가 Level별로 다른 데서 생긴 presentation duplication이다.

### Approved A Structure

모든 단계의 primary reading order를 다음 하나로 통일한다.

```text
Backtest Workflow Top Shell
  -> current stage responsibility / stage navigation
  -> active Level React Decision Workspace hero
  -> active Level body
```

- Level1은 이미 이 구조이므로 바꾸지 않는다.
- Level2의 `### Practical Validation`과 바로 뒤 caption을 primary render path에서 제거한다.
- Level3의 `### Final Review`와 바로 뒤 caption을 primary render path에서 제거한다.
- React hero의 단계별 핵심 질문, 후보 context와 설명은 유지한다.
- 공통 top shell은 stage identity/navigation만 소유하고 Level 내부 question/Gate를 복제하지 않는다.

새 공통 title component를 추가하거나 기존 React hero를 top shell로 끌어올리지 않는다. 그런 방식은
현재 두 계층을 다시 세 계층으로 만들거나 Level별 candidate context를 분리하므로 이 corrective 범위를
넘는다.

### Fallback And Ownership

- Practical Validation Python fallback은 이미 shared read model의 `header.question/detail`을 표시하므로
  React unavailable에서도 질문이 유지된다.
- Final Review Python fallback은 top shell의 current-stage responsibility 뒤에 candidate selector와
  computed verdict headline을 표시한다. static 질문을 다시 추가하지 않고 실제 판단 결과를 첫 내용으로
  유지한다.
- 제거 대상은 presentation-only `st.markdown` / `st.caption` 두 쌍이다. source selection, replay,
  decision brief, handler, route, registry와 persistence는 바꾸지 않는다.

### TDD And QA Contract

- RED source contract는 Level2/3 primary render function에 legacy stage title/caption이 남아 있으면
  실패해야 한다.
- GREEN은 두 renderer에서 중복 pair만 제거하며 React/fallback body와 route dispatch는 그대로 둔다.
- focused workflow/boundary tests, target `py_compile`, `git diff --check`를 실행한다.
- desktop Browser QA에서 Level2와 Level3가 top shell 다음 React hero로 바로 이어지고 중복 title이
  없는지 확인한다.
- 760px에서 제거된 빈 간격, hero clipping과 horizontal overflow가 없는지 확인한다.
- generated screenshots와 protected registry / Run History / saved JSONL / `.superpowers/`는 commit하지
  않는다.

### 14차 Acceptance Criteria

1. Level1/2/3 모두 `공통 workflow shell -> active React hero -> body` 순서를 사용한다.
2. Level2/3의 legacy Streamlit stage title과 설명이 primary DOM에 없다.
3. 각 React hero의 단계별 핵심 질문과 candidate context는 유지된다.
4. React unavailable fallback은 top shell과 기존 fallback content로 단계 의미를 잃지 않는다.
5. route, Gate, replay, registry, save와 Final Review 판단 계약은 변경되지 않는다.
6. desktop/760px Browser QA, focused tests, py_compile, diff-check와 protected-path audit를 통과한다.

### 14차 Out Of Scope

- page-level workflow shell 또는 Level React hero의 재디자인
- Level1/2/3 question copy 재작성
- Final Review read model/schema 변경
- Level2 replay fragment, Level3 persistence 또는 route 재설계
- 신규 공통 header component, progress/count/status dashboard 추가

## 15차 Corrective Design: Portfolio Mix React One-Shell Completion

### 이걸 하는 이유?

Level1의 Portfolio Mix는 4차에서 new / saved 진입, 역할·비중 truth, fingerprint, 저장과 Level2
인계 분리를 연결했지만 실제 편집·실행 surface는 `app/web/backtest_compare/page.py`의 legacy
Streamlit form에 남아 있다. 현재 화면은 다음 세 계층으로 분절된다.

```text
Level1 React context
  -> legacy Streamlit component / weight / saved replay workspace
  -> Level1 React decision
```

이 때문에 Single Strategy에서 이미 해결한 preset 우선 설명, 동일한 React 설정 editor, stable context,
사용자용 label, responsive layout이 Portfolio Mix에는 적용되지 않는다. 저장 Mix가 0건이어도 generic
Level1 판단이 아래에 나타나고, raw JSON / 절대 저장 경로 / 영문 기술 key가 first-read에 노출된다.

이번 corrective는 전략 계산 엔진을 다시 만드는 작업이 아니다. 여러 component의 설정을 기존 Single
Strategy pure schema로 검증하고, 현재 compare runner와 weighted builder를 Python adapter에서 호출하면서
Mix 전체를 하나의 React one-shell로 완성하는 작업이다.

### Confirmed Root Cause

- `app/web/backtest_analysis.py`는 Portfolio Mix에서 React context를 먼저 mount하고 legacy
  `render_compare_portfolio_workspace()`를 fragment로 렌더링한 뒤 React decision을 다시 mount한다.
- `app/web/backtest_compare/page.py`는 약 5,700줄이며 구성 전략, 공통 기간, 13개 concrete variant의
  strategy-specific form, 역할·비중, saved replay, raw detail과 실행 side effect를 함께 소유한다.
- 기존 React projection은 `saved_entry_mode`, role / weight summary와 action availability만 제공하고
  component draft나 settings schema를 소유하지 않는다.
- 7차 Unified React Strategy Settings의 승인 범위에서 `Portfolio Mix settings React migration`이
  명시적으로 제외되어 Single과 Mix의 visual/runtime boundary가 갈라졌다.
- 따라서 최근 stage-title/top-shell 변경의 회귀가 아니라 이전 4차에서 남긴 implementation gap이다.

### Approved Product Direction

채택안은 `A. Portfolio Mix 전체 React 전환`이다.

- 구성 전략 선택, 공통 기준, 구성별 preset / 상세 설정, 역할·비중, 실행 결과, 저장 Mix 재진입과
  최종 action을 하나의 React workspace에서 제공한다.
- Python이 catalog, field schema, validation, component payload, weighted Gate, 실행, persistence와
  intent 검증을 소유한다.
- React는 presentation과 intent만 소유한다.
- component first-read는 preset과 핵심 설정만 보여주며 `세부 설정`을 열 때 Single Strategy와 같은
  full React editor를 표시한다.
- Portfolio Mix에서는 기존 별도 React decision mount를 제거하고 같은 one-shell의 Step 3 / 4가
  결과와 action을 담당한다.
- Single Strategy primary flow는 변경하지 않는다.

CSS reskin이나 settings-only hybrid는 채택하지 않는다. 두 방식은 legacy saved replay, raw detail,
fragment reset과 React / Streamlit split ownership을 남긴다.

### Approved User Flow

#### Step 1. 구성 전략과 공통 기준

- `새 Mix 만들기`와 `저장된 Mix 불러오기`를 같은 Step 1의 mode로 둔다.
- 새 Mix는 최소 2개, 최대 4개 component를 지원한다.
- 목적별 strategy catalog에서 component를 추가하며 같은 concrete strategy 중복은 허용하지 않는다.
- 각 component card는 전략명, variant, preset, maturity, 현재 역할과 compact 설정 요약을 표시한다.
- preset은 먼저 보이고, `세부 설정`을 열 때 해당 component의 full React settings editor가 나타난다.
- component setting schema, preset 자동 적용과 사용자 label은 기존
  `backtest_single_settings_workspace.py`를 재사용한다.
- Mix component detail은 settings-only surface로 투영하며 Single 전용 실행 CTA는 포함하지 않는다.
- start / end / timeframe / option은 Mix 공통 값으로 한 번만 편집한다. component editor는 같은 값을
  중복 노출하지 않는다.
- component를 제거해도 다른 component draft와 공통 설정, 이전 결과는 보존한다.

저장 Mix mode는 name, component summary, 역할, 비중과 저장일을 card shelf로 표시한다.

- `불러와 편집`: 저장 snapshot을 current draft로 복원한다.
- `저장 기준으로 다시 실행`: 저장 snapshot을 복원한 뒤 current component / weighted execution을 실행한다.
- 저장된 값을 단순 선택한 상태만으로 결과나 Level1 판단을 만들지 않는다.
- raw JSON, 절대 파일 경로와 내부 field table은 primary / detail UI에서 제거한다.
- 삭제가 유지될 경우 `저장 Mix 관리` disclosure의 secondary action으로만 둔다.

#### Step 2. 역할과 목표 비중

- component별 역할은 `핵심(Core) / 성장(Growth) / 방어(Defense) / 보조(Satellite)` 사용자 label로
  표시하고 internal value는 기존 `core / growth / defense / satellite`를 보존한다.
- target weight는 component row에서 편집하며 합계 100%를 명시적으로 확인한다.
- date alignment와 common-period coverage를 사용자 문장으로 표시한다.
- 같은 역할 집중이나 높은 단일 비중은 경고할 수 있지만 UI가 비중을 자동 수정하지 않는다.
- 100% 미충족, 0% component, 설정 validation error가 있으면 실행 handler를 호출하지 않는다.

#### Step 3. Mix 실행과 해석

- 실행 전에는 generic 결과 verdict와 빈 metric / action board를 렌더링하지 않는다.
- 실행 중에도 Step 1 / 2와 current draft를 유지한다.
- component별 pending / running / success / error를 해당 component card에 연결한다.
- component 하나가 실패해도 다른 draft와 이전 성공 결과는 삭제하지 않는다.
- component 실행이 모두 성공한 뒤 기존 weighted builder로 Mix bundle을 만든다.
- 설정이 바뀌면 이전 성공 결과는 `참고용 이전 결과`로 남고 current save / Level2 action만 차단한다.
- current 결과는 Mix 성과, component contribution, component allocation, explicit evidence가 있을 때의
  underlying target, Level1 readiness를 기존 result workspace contract와 같은 언어로 표시한다.

#### Step 4. 저장하고 Level2 전송

- current result와 normalized draft fingerprint가 일치할 때만 action을 표시한다.
- `Mix 설정 저장`은 reusable setup만 저장한다.
- `Level2 검증 후보로 등록`은 selection source만 생성한다.
- 두 action은 별도 callable Python handler이며 하나의 action 실패가 다른 persistence를 rollback하지 않는다.
- 저장 Mix를 선택하거나 draft만 복원한 상태에서는 Level2 action을 제공하지 않는다.
- callable action이 0개이면 빈 action board를 렌더링하지 않는다.

### Architecture And Ownership

```text
Backtest Analysis common entry
  -> Portfolio Mix React one-shell
     -> validated intent
        -> Python Portfolio Mix web adapter
           -> pure Portfolio Mix workspace service
           -> existing Single settings service
           -> existing compare runner / weighted builder
           -> existing Run History / saved Mix / Level2 source handlers
```

#### New Pure Service

`app/services/backtest_portfolio_mix_workspace.py`

- Mix draft normalization과 stable component ID
- component strategy / variant / preset projection
- existing Single settings workspace composition
- shared setting, role / weight, total, alignment validation
- current draft fingerprint와 result freshness
- saved Mix user-facing summary projection
- execution / save / Level2 action availability
- root issue deduplication과 user-facing error projection

Pure service는 Streamlit, React, DB fetch, file write와 runner를 import하지 않는다.

#### New Web Adapter

`app/web/backtest_portfolio_mix_workspace.py`

- session draft와 last result/error 보존
- nonce / intent ID dedup과 action allow-list
- component add / remove / variant / settings / role / weight / shared-setting intent 검증
- component settings payload를 기존 compare runner override로 변환
- current compare execution, weighted build와 Run History append
- saved Mix write와 Level2 source handoff의 distinct handler
- React unavailable Python fallback mount

#### New React Component

`app/web/components/backtest_portfolio_mix_workspace/`

- approved four-step one-shell presentation
- preset-first component cards와 on-demand detail editor
- saved Mix shelf, allocation board, result and final actions
- inline validation / component runtime state
- desktop / 760px / narrow responsive layout
- ResizeObserver height sync, keyboard focus, aria state

React는 strategy grouping, concrete runner, validation, fingerprint, Gate, persistence와 retry를 계산하지 않는다.

#### Existing Boundary

- `app/web/backtest_analysis.py`는 Mix primary route에서 새 workspace를 한 번만 mount하며 generic Mix
  decision surface를 중복 렌더링하지 않는다.
- `app/services/backtest_single_settings_workspace.py`는 component별 schema / preset / validation / payload
  source로 재사용한다. Mix 전용 field catalog를 복제하지 않는다.
- `app/services/backtest_compare_catalog.py`, `backtest_compare_execution.py`,
  `backtest_weighted_portfolio.py`, `backtest_portfolio_mix_readiness.py`의 계산 의미는 유지한다.
- `app/web/backtest_compare/page.py`의 primary legacy renderer는 새 workspace cutover 후 route에서 제거한다.
  새 flow에서 호출되지 않는 form / raw replay / presentation helper는 reference test 뒤 삭제한다.

### Draft And Data Flow

```text
mix_draft:
  draft_id
  source_saved_portfolio_id
  shared:
    start
    end
    timeframe
    option
    date_policy
  components[]:
    component_id
    strategy_choice
    variant
    settings_values
    role
    weight_percent
```

- component ID는 presentation key이며 strategy name을 session key로 직접 사용하지 않는다.
- normalized fingerprint는 shared values와 ordered component identity / variant / effective settings / role /
  weight를 포함한다.
- 각 component는 existing Single pure builder / validator / payload projector를 통과한다.
- Python adapter는 projected payload에서 Mix shared field를 정규화하고 concrete strategy display name과
  compare override를 만든다.
- 모든 component가 성공한 뒤 weighted result를 생성하고 top-level `run_result_id`와 fingerprint를
  component / weighted / handoff contract에 유지한다.
- 실행 성공은 Run History, Mix 저장은 saved setup, Level2 전송은 candidate source라는 기존 분리를
  유지한다.

### Legacy Prototype Data Decision

기존 saved Mix와 run artifact는 prototype test 성격이 강하므로 새 구조를 복잡하게 만드는 migration /
fallback을 구현하지 않는다.

- 신규 React workspace와 신규 saved Mix는 새 schema만 쓴다.
- legacy saved row를 새 draft로 자동 보정하거나 역할·설정을 추론해 primary flow에 승격하지 않는다.
- old raw replay UI와 legacy-only form / helper는 새 flow reference가 없으면 제거할 수 있다.
- 기존 protected JSONL을 구현 과정에서 rewrite / delete / stage / commit하지 않는다.
- 실제 로컬 prototype data 초기화가 필요하면 새 flow 완료 뒤 별도 명시 작업으로 수행한다.
- runtime QA는 legacy record가 아니라 새 UI에서 생성한 Mix로 수행한다.

### Error And Lifecycle Contract

- field validation error는 component detail의 해당 field에 표시하고 runner를 호출하지 않는다.
- component execution error는 해당 card에 연결하며 다른 draft와 이전 결과를 보존한다.
- weighted build error는 component success bundle을 보존한다.
- save failure는 draft / result / Run History를 제거하지 않는다.
- Level2 handoff failure는 saved Mix나 Run History를 rollback하지 않는다.
- current draft 변경은 old result를 stale reference로 만들고 destructive reset하지 않는다.
- 저장 Mix 0건은 empty state와 `새 Mix 만들기` intent만 표시한다.
- development component가 있으면 실행은 허용하되 Mix 전체 Level2 action은 차단한다.
- raw traceback, callable path, absolute save path와 internal key/value table은 사용자 surface에 표시하지 않는다.

### Implementation Roadmap

#### 15-1차: Mix Truth / Read Model

- new pure Mix draft / workspace service
- Single settings schema composition
- component payload / role / weight / fingerprint / saved summary contract
- RED -> GREEN focused tests
- distinct Korean commit

#### 15-2차: New Mix React One-Shell

- new React component and Python adapter
- component catalog, shared settings, preset-first detail editor
- role / weight board, stable execution surface and fallback
- React production build and focused UI tests
- distinct Korean commit

#### 15-3차: Result / Saved Mix / Level2 Integration

- component execution and weighted result
- saved Mix create / select / restore / rerun
- result lifecycle, distinct setup save / candidate handoff
- legacy primary renderer cutover and unreachable helper cleanup
- RED -> GREEN persistence / boundary tests
- distinct Korean commit

#### 15-4차: Runtime QA / Docs / Closeout

- actual GTAA + `Quality + Value` + Equal Weight Mix create / run / save / restore / edit / rerun
- stale reference and component failure preservation QA
- focused tests, React build, target py_compile, diff-check
- desktop / 760px Browser QA and screenshot
- canonical finance docs, active task and root handoff log sync
- protected artifact exclusion audit and closeout commit

### TDD And Browser QA Contract

- RED: 2~4 component constraint, duplicate concrete strategy rejection and stable component ID.
- RED: component schema / preset / validation is composed from the existing Single pure service.
- RED: invalid shared / component / role / weight input never reaches the runner.
- RED: setting changes preserve old result as stale and disable current save / handoff.
- RED: component failure preserves other draft and previous success result.
- RED: save Mix and Level2 handoff use distinct callable handlers.
- RED: saved mode with 0 rows has no verdict / action board / raw path.
- RED: React source does not classify Gate, execute runner or write persistence.
- RED: Mix primary route no longer renders legacy Streamlit form / raw saved replay.
- GREEN 뒤 focused service / intent / boundary / persistence tests를 새로 실행한다.
- React production build, target `py_compile`, `git diff --check`를 수행한다.
- desktop Browser QA에서 3-component new Mix create, detail editor, roles / weights, run, save, restore,
  edit, rerun과 Level2 action boundary를 확인한다.
- 760px에서 single-column wrap, detail editor, saved shelf, result, iframe height와 overflow 0을 확인한다.
- generated screenshots, `.superpowers/`, registry, Run History와 saved JSONL은 commit하지 않는다.

### 15차 Acceptance Criteria

1. Portfolio Mix primary route가 하나의 React four-step workspace를 사용한다.
2. legacy Streamlit component form, saved replay page와 generic duplicate decision mount가 primary DOM에 없다.
3. 2~4개 component를 목적별 catalog에서 추가하고 preset 우선으로 설정할 수 있다.
4. component detail은 기존 Single settings schema / preset / validation을 재사용한다.
5. shared period / execution values는 한 번만 입력하고 모든 component에 Python이 적용한다.
6. roles / weights / total / alignment가 사용자 label로 표시되고 invalid draft는 실행되지 않는다.
7. 실행과 rerun 중 Step 1 / 2와 draft가 사라지지 않는다.
8. 설정 변경과 component failure가 이전 결과를 삭제하지 않는다.
9. 저장 Mix 0건에는 empty state만 있고 generic Level1 verdict가 없다.
10. saved Mix는 같은 shell에서 새 schema draft로 restore / rerun할 수 있다.
11. setup save, Run History와 Level2 candidate source는 서로 다른 persistence action이다.
12. current fingerprint와 result가 일치하고 Gate가 ready일 때만 save / Level2 action이 나타난다.
13. React는 classification, validation, runner, Gate와 persistence를 소유하지 않는다.
14. desktop / 760px에서 visual hierarchy, ResizeObserver, keyboard / aria와 overflow 0을 만족한다.
15. focused tests, production build, py_compile, diff-check, actual Browser QA와 protected-path audit를 통과한다.

### 15차 Out Of Scope

- strategy algorithm, factor formula, performance calculation 또는 DB schema 변경
- 신규 strategy / provider / historical universe 추가
- Level2 / Final Review route와 Gate 의미 재설계
- legacy prototype JSONL migration, rewrite 또는 자동 deletion
- broker order, live approval, account sync, auto rebalance
- Single Strategy primary workflow 재설계

## 2026-07-19 15차 후속: Portfolio Mix Step 3 Result Evidence 보강 설계

### 이걸 하는 이유?

actual GTAA 50% / Equal Weight 50% 실행 결과에서 Step 3은 KPI 네 개만 표시했다. 그러나 weighted
builder는 이미 월별 `result_df`, `chart_df`, component contribution amount/share와 data trust를 계산한다.
새 adapter가 이 bundle을 `summary`와 `period`로만 축약하고 React가 summary grid만 렌더링해 승인된
15차 설계의 `Mix 성과 / component contribution / component allocation / explicit evidence`가 primary
workspace에서 사라졌다. 성공 notice와 current result card도 공통 result stack 간격이 없어 서로 붙어 보인다.

이 후속 범위는 새 계산을 발명하지 않고 이미 계산된 weighted result를 사용자 언어로 투영한다.

### Approved Presentation: B안

Step 3의 기본 화면은 다음 순서로 읽는다.

1. `이 구성으로 Mix 실행` action
2. 실행 성공 / 실패 / stale feedback
3. current 또는 reference result identity와 실제 공통 기간
4. 사용자 단위 KPI
5. 누적 성과 흐름
6. 월별 수익률 변화
7. `구성 기여도·월별 결과·계산 근거` disclosure

기본 화면은 누적 성과와 월별 수익률까지만 펼친다. component 기여도, 월별 결과 표와 계산·데이터
근거는 하나의 secondary disclosure 안에 둬 Step 3이 legacy result tab처럼 길어지지 않게 한다.

### Spacing And Formatting Contract

- 실행 button과 feedback/result 묶음 사이는 18px을 둔다.
- feedback notice와 result card, result card 내부 주요 block 사이는 각각 16px 이상을 둔다.
- CAGR / MDD는 raw decimal `0.096`, `-0.17`이 아니라 `9.60%`, `-17.00%`로 표시한다.
- Sharpe는 소수 둘째 자리, 평가액은 천 단위 구분을 사용한다.
- React는 숫자 의미를 추론하지 않는다. Python read model이 raw value와 formatted label을 함께 제공한다.
- current와 stale/reference는 같은 result evidence 구조를 쓰되 stale에는 `참고용 이전 결과` label을
  표시하고 save / Level2 action을 계속 차단한다.

### Default Charts

#### 누적 성과 흐름

- weighted `chart_df`의 실제 공통 날짜와 `Total Balance`를 첫 유효 시점 100 기준으로 normalize한다.
- desktop은 최대 6개, 760px은 최대 3개의 실제 timeline date tick을 표시한다.
- 별도 benchmark 계약이 없는 weighted Mix에 SPY나 component benchmark를 임의로 합성하지 않는다.
- explicit Mix benchmark가 향후 저장되는 경우에만 같은 chart의 비교 series로 확장할 수 있다.

#### 월별 수익률 변화

- weighted `result_df`의 `Total Return`을 월별 막대로 표시한다.
- 양수와 음수는 같은 zero axis에서 색과 방향으로 구분한다.
- 원본에 없는 월은 chart row를 만들지 않는다. 날짜는 있지만 값이 NaN인 row는 월별 결과 표에
  `계산값 없음`으로 보존하고 chart bar에서는 제외한다. 두 경우 모두 0으로 만들지 않는다.
- 기본 화면은 전체 월별 series를 chart로 보여주고, 정확한 row 값은 disclosure의 월별 결과 표에 둔다.

### Hover And Keyboard Contract

- 누적 성과 chart는 pointer가 chart 안에 있을 때 가장 가까운 실제 날짜 row 하나를 선택한다.
- tooltip은 `날짜 / 기준 100 지수 / 누적 수익률 / 평가액`을 보여준다.
- 월별 수익률 chart는 bar hover에서 `월 / 월 수익률 / 월말 평가액`을 보여준다.
- tooltip과 crosshair/highlight는 pointer leave에서 사라지며 상시 label로 chart를 덮지 않는다.
- chart point와 monthly bar는 keyboard focus로 같은 tooltip 내용을 확인할 수 있어야 한다.
- React는 nearest-row 선택과 tooltip 위치만 소유한다. 날짜, normalized value와 사용자 label은 Python이
  제공하며 React가 raw dataframe column을 분류하거나 percentage 계산을 하지 않는다.

### Secondary Disclosure

`구성 기여도·월별 결과·계산 근거`는 세 묶음을 제공한다.

1. `구성 기여도`
   - 목표 비중, normalized input weight, 종료 시점 contribution amount/share
   - 종료 시점 compact summary table을 먼저 표시
   - contribution series가 있을 때 `기여 금액 / 기여 비중` segmented view로 같은 timeline chart를 표시
2. `월별 결과`
   - 사용자 열 `월 / 월 수익률 / 평가액`
   - raw `Date`, `Total Return`, `Total Balance` key를 first-read label로 노출하지 않음
3. `계산 근거`
   - 공통 시작/종료일, 월별 관측 수, intersection date policy
   - component strategy / role / target weight와 component data trust summary
   - raw meta / absolute path / JSON dump는 노출하지 않음

명시적 holdings / underlying target evidence가 weighted bundle에 없으면 빈 보유표를 만들지 않는다.
component allocation과 contribution은 holdings를 대신하는 데이터로 오인하지 않도록 별도 이름을 쓴다.

### Ownership And Data Flow

```text
weighted bundle
  result_df / chart_df
  component_contribution_amount_df
  component_contribution_share_df
  component_data_trust_rows
  component roles / weights / meta
    -> Python Portfolio Mix result projection
       formatted KPI / actual dates / normalized curve / monthly bars
       contribution / monthly table / calculation basis
         -> Portfolio Mix workspace read model current/reference result
           -> React Step 3 presentation + pointer/focus intent only
```

- `app/services/backtest_portfolio_mix_workspace.py`가 weighted bundle DataFrame을 JSON-safe result
  evidence와 사용자 label로 투영하고 fingerprint/current-stale lifecycle을 유지한다.
- `app/web/backtest_portfolio_mix_workspace.py`는 weighted builder 결과를 pure projection에 전달하고
  session current/reference result를 원자적으로 교체한다.
- `app/web/components/backtest_portfolio_mix_workspace/frontend/src/App.tsx`는 result sections와
  pointer/focus state만 렌더링한다.
- `styles.css`는 result stack 간격, desktop/two-chart와 760px/one-column responsive contract를 소유한다.
- 기존 weighted calculation, run history, saved setup과 Level2 source schema는 변경하지 않는다.

### Error And Empty States

- 실행 전에는 KPI, chart, monthly table과 disclosure를 만들지 않는다.
- weighted result에 chart/monthly row가 없으면 해당 block만 `계산 근거 없음`으로 낮추고 다른 KPI를
  유지한다.
- component/weighted 실행 실패는 이전 성공 result evidence를 reference로 보존한다.
- 무한대와 duplicate date는 Python projection에서 제거/정렬한다. NaN 월별 row는 표에서
  `계산값 없음`으로 보존하고 chart에서는 제외하며, sparse month를 0 또는 PASS로 만들지 않는다.

### Verification Contract

- RED: weighted bundle의 summary/chart/monthly/contribution/data-trust가 JSON-safe result evidence로 투영된다.
- RED: percentage/currency/ratio label과 actual date tick이 Python에서 고정된다.
- RED: missing/NaN/sparse data가 0으로 invent되지 않는다.
- RED: stale reference가 full result evidence를 보존하고 save/Level2 action은 계속 차단된다.
- RED: React source에 두 기본 chart, secondary disclosure, pointer leave와 keyboard focus tooltip이 있다.
- RED: React가 raw dataframe key, percentage 계산, benchmark 추론을 하지 않는다.
- GREEN: focused service/adapter/boundary test, React production build, target `py_compile`, `git diff --check`.
- Browser QA: desktop과 760px에서 result stack 간격, formatted KPI, actual date ticks, 두 chart hover/focus,
  disclosure, stale/reference와 horizontal overflow 0을 확인한다.

### Out Of Scope

- weighted portfolio 계산식, 월별 resampling 또는 component contribution 계산 변경
- 임의 SPY benchmark, blended benchmark 또는 신규 benchmark 설정 UI
- weighted holdings / underlying target을 근거 없이 합성
- chart zoom/pan/range selector와 신규 chart dependency
- saved JSONL / Run History / Level2 source schema migration

## 17차 Portfolio Mix Chart Geometry And Full-Width Layout

### 문제와 원인

- 누적 성과 point는 `PLOT_LEFT`부터 `CHART_WIDTH - PLOT_RIGHT` 사이에 배치되지만 pointer index는
  SVG 전체 렌더 폭을 0~100%로 정규화했다. 119개 row 예시에서 첫 plot point 위 커서는 기존 계산으로
  index 9를 선택해 crosshair와 tooltip 데이터가 커서보다 오른쪽으로 어긋난다.
- desktop에서 누적 성과와 월별 수익률을 1.35:0.9 두 열로 배치해 월별 막대가 전체 결과 폭의 약 40%만
  사용한다. 119개월 막대를 읽기에는 폭과 간격이 부족하다.

### 승인된 설계

- 두 chart card를 desktop과 760px 모두 `누적 성과 -> 월별 수익률` 두 행, 각 전체 폭으로 배치한다.
- pointer의 client X를 먼저 SVG viewBox X로 변환한 뒤 실제 plot 영역
  `(chartX - PLOT_LEFT) / (CHART_WIDTH - PLOT_LEFT - PLOT_RIGHT)`으로 정규화한다.
- crosshair와 tooltip은 선택된 실제 point의 같은 viewBox X를 사용한다. edge tooltip clamp는 card 밖
  clipping 방지를 위해 유지한다.
- Python evidence, weighted 계산, KPI, 저장/Level2 handoff와 chart 높이 상수는 변경하지 않는다.

### 검증 계약

- RED source contract는 plot-aware index helper와 single-column desktop grid 부재로 실패해야 한다.
- GREEN focused test와 React production build를 통과해야 한다.
- actual desktop QA에서 plot 첫/중간/마지막 커서가 같은 위치의 point/date를 선택하고 월별 chart가
  전체 폭을 사용해야 한다. 760px overflow와 ResizeObserver height도 유지한다.
