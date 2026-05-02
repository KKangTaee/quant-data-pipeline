# Phase 6 Completion Summary

## 목적

- Phase 6에서 진행한
  - `Market Regime Overlay`
  - `Quality Snapshot (Strict Quarterly Prototype)`
  workstream을 closeout 관점에서 정리한다.
- 다음 phase를 열기 전에,
  현재 strict family가 어디까지 구현/검증되었는지 한 번에 확인할 수 있게 한다.

## Phase 6에서 완료된 것

### 1. second overlay first pass 구현

Phase 6의 second overlay는 아래로 고정되었다.
- `Market Regime Overlay`

현재 first-pass semantics:
- benchmark의 `Close`와 `MA(window)`를 month-end rebalance 시점에 비교
- `Close < MA(window)`이면 그 rebalance에서 strict factor 후보 전체를 현금으로 둠
- intramonth trigger는 아직 없고, rebalance-date only semantics를 유지

기본값:
- benchmark:
  - `SPY`
- window:
  - `200`

즉 현재는
**시장 전체의 장기 추세가 무너지면 strict factor 포트폴리오 전체를 현금으로 전환하는 상위 방어 레이어**
가 추가된 상태다.

### 2. strict annual family에 regime overlay 연결

아래 3개 전략은 이제 모두 market regime overlay를 지원한다.
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

지원 surface:
- single strategy
- compare
- history
- selection interpretation

즉 overlay가 단순 strategy 내부 로직이 아니라,
UI / 결과 / 기록 / 해석까지 이어진 연구 기능으로 정리되었다.

### 3. quarterly strict family 첫 진입 경로 구현

Phase 6에서는 새 single-only research strategy가 추가되었다.
- `Quality Snapshot (Strict Quarterly Prototype)`

현재 의미:
- public default 전략이 아님
- compare public set에도 아직 포함되지 않음
- quarterly strict family feasibility를 보기 위한 research-only prototype

이 경로도 first pass 기준으로는
- trend filter overlay
- market regime overlay
- selection history
- interpretation
을 annual strict family와 같은 패턴으로 지원한다.

### 4. history / compare / prefill UX 보강

Phase 6 manual validation 과정에서 아래 UX/기록 경로도 함께 보강되었다.

- compare strict annual family advanced inputs를 전략별로 읽기 쉬운 block/expander 구조로 정리
- overlay enable이 꺼져 있어도
  - regime window
  - regime benchmark
  를 미리 수정 가능하게 정리
- single-strategy `Load Into Form` 오류 수정
- compare history drilldown에
  - per-strategy summary row
  - strategy-level override / market regime context
  노출

즉 Phase 6는 전략만 추가한 것이 아니라,
**manual validation과 history 해석까지 usable한 수준으로 같이 다듬은 phase**
였다.

### 5. manual test checklist 작성 및 검증

Phase 6 closeout 기준 manual validation 문서는 아래다.
- `PHASE6_TEST_CHECKLIST.md`

이 체크리스트를 통해
- annual strict family overlay on/off
- quarterly prototype single path
- compare annual strict family input path
- history / prefill / tooltip
을 점검했다.

## 핵심 결과

### strict annual family는 second overlay까지 연구 가능한 상태가 되었다

Phase 5에서는 first overlay까지 붙은 상태였다면,
Phase 6에서는 market-wide overlay까지 올라가면서
strict annual family가
**개별 종목 추세 + 시장 전체 regime**
를 함께 실험할 수 있는 전략군이 되었다.

### quarterly strict family는 “구현 가능성”은 열렸지만 아직 research-only다

manual validation 기준으로 quarterly prototype은
요청한 start date보다 실제 active period가 늦게 시작될 수 있었다.

즉 지금 상태는:
- quarterly strict family가 완전히 막혀 있는 것은 아님
- 하지만 아직 public candidate로 올릴 정도의 coverage / history depth는 부족

따라서 Phase 6 종료 판단은:
- annual strict family overlay expansion:
  - `completed`
- quarterly strict family first entry / validation:
  - `completed`
- quarterly public promotion:
  - `not_ready`

## 아직 남겨둔 것

아래는 Phase 6 미완료가 아니라,
다음 phase 후보로 넘긴 항목이다.

- quarterly statement shadow coverage 확장
- statement API payload와 실제 timing field 재확인
- `available_at` / filing timing 기반 PIT ledger 재정비
- quarterly strict family의 longer-history 검증
- quarterly public candidate 승격 여부 판단

## Phase 6 종료 판단

현재 기준으로는:
- Phase 6 planned first pass:
  - `completed`
- manual validation and UX fix pass:
  - `completed`
- next-phase kickoff readiness:
  - `ready`

즉 지금은
**Phase 6를 closeout하고, quarterly coverage와 statement PIT hardening을 중심으로 다음 phase를 여는 것이 자연스러운 시점**
이다.
