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
