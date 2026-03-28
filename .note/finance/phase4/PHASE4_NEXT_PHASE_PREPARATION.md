# Phase 4 Next Phase Preparation

## 목적

- Phase 4 종료 이후 어떤 workstream이 가장 자연스럽게 이어지는지 정리한다.
- 새 major phase를 바로 여는 대신,
  다음 phase 후보와 준비 포인트를 명시해 둔다.

## 현재 출발점

Phase 4 종료 시점 기준으로:
- unified Backtest UI가 존재한다
- public runtime wrapper family가 정리되었다
- strict annual family가 public candidate까지 올라왔다
- annual coverage preset/operator 흐름이 생겼다
- strict annual managed preset은 `100/300/500/1000`까지 열렸지만,
  current DB 기준 공식 public default는 여전히 `300`으로 유지된다
- `Coverage 1000`은 real top-1000 staged preset으로 usable하지만,
  closeout refresh 이후에도 stale symbol `4`개와 `49d` freshness spread가 남아 있어
  public default로는 올리지 않는다
- `Value Snapshot (Strict Annual)`은 closeout 보강 이후
  `2016-01-29`부터 active하게 동작하는 real strict-value path가 되었다
- strict annual multi-factor first candidate도 추가되었다

즉 다음 phase는
UI를 새로 여는 것보다
**strategy library / comparative research / stricter factor family 확장**
쪽이 더 자연스럽다.

## 다음 phase 후보

### 후보 1. Strategy Library And Comparative Research

가장 자연스러운 후보다.

핵심 작업:
- strict quality / strict value 비교 리포트 고도화
- strict quality / strict value / strict quality+value 비교
- strict multi-factor 후보
- strategy family별 canonical preset
- comparative research read path 정리

### 후보 2. Annual Coverage Expansion And Operations

운영 중심 phase로도 갈 수 있다.

핵심 작업:
- wider annual coverage 반복 run
- shadow rebuild 운영 루틴
- missing issuer scope 정리
- operator runbook 정리
- `US Statement Coverage 500/1000`의 staged operator path를
  언제 public default 후보로 올릴지 판단

### 후보 3. User-Defined Portfolio Construction Expansion

장기 제품 관점 후보다.

핵심 작업:
- strategy blending UX 강화
- custom portfolio inputs
- saved portfolio definition
- portfolio rerun / compare

## 추천

현재 구현 상태 기준으로는
다음 phase 후보를 아래 순서로 보는 것이 맞다.

1. `Strategy Library And Comparative Research`
2. `Annual Coverage Expansion And Operations`
3. `User-Defined Portfolio Construction Expansion`

이유:
- strict annual family가 막 usable candidate가 되었기 때문에
  바로 다음 가치는 strategy-family 확장과 비교 연구 쪽에서 가장 크게 나온다.
- 다만 current DB audit 기준으로 wider preset coverage가 아직 얕아서,
  `Annual Coverage Expansion And Operations` 후보의 우선순위도 이전보다 높아졌다.

## next-phase kickoff 전에 확인할 것

- strict annual family의 official role을 그대로 유지할지
- broad vs strict public 기본값을 더 다듬을지
- `Quality -> Value -> Multi-Factor` 순으로 갈지
- 더 넓은 annual coverage run을 먼저 추가로 돌릴지
- `US Statement Coverage 500/1000`을 current DB audit 기준 staged preset으로 둘지
  혹은 별도 managed universe를 새로 정의할지

## 현재 상태

- Phase 4 closeout:
  - `completed`
- next-phase candidate 정리:
  - `completed`
- next-phase formal opening:
  - `completed`

## 후속 결정

이후 사용자 확인을 거쳐,
다음 phase 방향은 아래처럼 고정되었다.

- next phase:
  - `Strategy Library And Comparative Research + Risk Overlay`

관련 문서:
- `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`
- `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase5/PHASE5_PRACTICAL_INVESTMENT_READINESS_POLICY.md`

추가로 사용자 요청 기준 carry-over 항목도 같이 반영되었다.
- compare 화면에서 strict factor 전략의 advanced-input parity 보강
- strict factor family의 quarterly expansion candidate 검토
