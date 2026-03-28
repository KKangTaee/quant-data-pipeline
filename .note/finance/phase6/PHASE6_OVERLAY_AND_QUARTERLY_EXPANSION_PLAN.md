# Phase 6 Overlay And Quarterly Expansion Plan

## 목적

- Phase 5 first chapter에서 정리한 strict family baseline과 first overlay를 바탕으로,
  다음 major chapter를 공식적으로 연다.
- 이번 phase의 핵심은
  **second overlay implementation**과
  **quarterly strict family entry planning / first validation**
  을 하나의 research chapter로 묶는 것이다.
- 목표는 strict family를
  더 실전적인 연구 환경으로 확장하면서도,
  quarterly 확장을 무리하게 구현하지 않고
  진입 기준과 validation 경로를 먼저 분명하게 만드는 데 있다.

## Phase 5에서 넘겨받는 현재 상태

Phase 5 종료 시점 기준:
- strict annual family baseline comparative research가 정리되었다
- compare advanced-input parity가 구현되었다
- first overlay(`month-end MA200 trend filter + cash fallback`)가 single / compare / history에 연결되었다
- overlay on/off validation이 문서화되었다
- stale / missing symbol heuristic classification이 붙었다
- selection interpretation이 usable 수준으로 강화되었다
- strict preset semantics는 historical backtest 기준으로 정리되었다
- manual test checklist와 phase closeout 문서가 완료되었다

즉 Phase 6은
strict annual family를 다시 만드는 단계가 아니라,
**overlay layer를 한 단계 더 확장하고, quarterly strict family의 실제 entry path를 여는 단계**
로 보는 것이 맞다.

## 이번 Phase의 정식 방향

Phase 6은 아래 두 축을 함께 다룬다.

1. `Second Overlay Implementation`
2. `Quarterly Strict Family Entry And Validation`

우선순위는 첫 번째가 더 높다.

이유:
- Phase 5에서 first overlay가 이미 연결되었기 때문에,
  이제는 second overlay를 붙여 strict family의 risk-layer 실험을 더 현실적으로 확장할 수 있다.
- quarterly strict family는 가치가 크지만,
  coverage / timing / runtime / freshness 부담이 annual보다 더 크므로
  entry criteria와 validation path를 먼저 명확히 하고 들어가는 편이 안전하다.

## 추천 second overlay

현재 기준 추천 second overlay는 다음과 같다.

- `Market Regime Overlay`

의도:
- 개별 종목의 추세 필터만이 아니라,
  broader market regime을 보고 strict factor exposure를 줄이거나 현금으로 옮기는 layer를 추가한다.

초기 범위:
- benchmark 입력 정의
- regime signal 정의
- cash fallback 규칙 정의
- single / compare / history 노출
- on/off validation 및 interpretation 추가

이번 phase에서는
복잡한 defensive rotation보다
**cash fallback first pass**를 우선한다.

## quarterly strict family 방향

quarterly strict family는 이번 phase에서 아래 수준까지 가는 것을 목표로 한다.

1. entry criteria 고정
2. required data path 정의
3. coverage / freshness / runtime audit
4. 최소 1개 quarterly strict candidate에 대한 first-pass validation

이번 phase에서는
annual strict family와 동등한 완성도를 바로 요구하지 않는다.

즉:
- public default 승격보다
- **research-capable prototype + feasibility proof**
가 더 중요한 목표다.

## 범위 안

### A. second overlay implementation

- benchmark / signal / threshold 정의
- runtime wrapper 연결
- UI parameter exposure
- result meta / selection interpretation 연결
- compare on/off validation

### B. quarterly strict family entry planning

- quarterly statement/factor path 범위 확정
- strict quality / value / quality+value 중 첫 대상 선정
- coverage / freshness / runtime 측정
- research-only candidate first pass 검증

### C. interpretation and guidance sync

- second overlay 설명 보강
- quarterly strict semantics 설명 보강
- compare / history / test checklist 갱신

## 범위 밖

이번 phase에서 아래는 기본 범위 밖으로 둔다.

- automated trading / live execution
- full intramonth event-driven de-risk engine
- quarterly strict family 전체 public-default 승격
- third overlay candidate 구현
- broad 신규 전략군 대규모 추가

## 추천 구현 순서

1. `Market Regime Overlay` requirement 문서 고정
2. benchmark / regime input path 정의
3. overlay runtime first pass 구현
4. single / compare / history UI 연결
5. overlay on/off validation
6. quarterly strict family entry criteria 문서 고정
7. quarterly strict first candidate path 구현 또는 validation harness 구현
8. quarterly coverage / runtime / freshness audit
9. interpretation / docs / checklist sync

## 완료 기준

Phase 6 current chapter는 최소한 아래가 충족되면 closeout-ready로 본다.

- second overlay 1종이 strict family에 실제 연결되어 있음
- single / compare / history에서 second overlay 상태를 읽을 수 있음
- on/off validation 결과가 문서화되어 있음
- quarterly strict family에 대해
  - entry criteria가 고정되어 있고
  - first validation 결과가 남아 있음
- phase-specific manual test checklist가 작성되어 있음

## 현재 상태

- phase direction:
  - `confirmed`
- phase formal opening:
  - `opened`
- current chapter focus:
  - `second overlay first`
  - `quarterly strict entry second`
- current implementation state:
  - `market regime overlay first pass implemented`
  - `strict quarterly prototype first pass implemented`
  - `manual UI validation completed`
  - `closeout completed`
