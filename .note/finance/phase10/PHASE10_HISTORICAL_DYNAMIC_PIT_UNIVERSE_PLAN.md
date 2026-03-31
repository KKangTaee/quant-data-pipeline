# Phase 10 Historical Dynamic PIT Universe Plan

## 목적

- current strict preset의 `managed static research universe` 계약을 넘어서
  **historical rebalance-date 기준 universe membership**를 복원하는 mode를 만든다.
- 실전 투자용 최종 검증에 가까운 backtest contract를 확보한다.

## 왜 이 phase가 필요한가

현재 strict annual / quarterly family는

- diagnostics
- operator tooling
- coverage policy
- promotion gate

까지는 정리되어 있다.

하지만 universe membership 자체는
여전히 current managed preset를 기준으로 잡고,
run 안에서 availability filtering만 적용하는 구조다.

이 방식은 연구와 operator validation에는 유용하지만,
실전 투자용 final validation contract로는 부족하다.

즉 다음 단계는
UI productization보다 먼저
**historical dynamic PIT universe를 구현하는 것**
이 더 중요하다.

## 이번 phase의 핵심 질문

1. rebalance date별 universe membership를 어떤 source에서 복원할 것인가
2. market-cap / listing status / delisting / symbol mapping을 어떤 단위로 관리할 것인가
3. annual strict family를 먼저 dynamic mode에 연결할지, quarterly까지 같이 열지
4. current static preset mode와 dynamic PIT mode를 UI / runtime에서 어떻게 구분할 것인가

## 권장 기본안

### 1. first implementation target은 annual strict family

처음부터 quarterly까지 같이 열기보다,
먼저 `strict annual family`를 dynamic universe mode에 연결하는 편이 안전하다.

이유:

- annual family가 현재 가장 안정적인 strategy surface
- quarterly는 아직 research-only 계약
- dynamic PIT의 핵심 검증은 universe contract부터 확실히 잡는 것이므로,
  먼저 annual에서 contract를 검증하는 것이 효율적이다

### 2. current static mode는 유지한다

dynamic PIT mode를 만든다고 해서
current static preset를 바꾸지는 않는다.

즉:

- current mode = 빠른 연구 / operator-friendly / managed static research universe
- new mode = 실전형 검증용 historical dynamic PIT universe

으로 분리한다.

### 3. universe membership는 rebalance snapshot 단위로 관리한다

핵심 기준일은
일봉 매일이 아니라
**rebalance date snapshot**
으로 시작하는 것이 현실적이다.

즉 first pass는:

- 매 rebalance date 기준
  - active listing
  - usable price
  - point-in-time market-cap ranking
를 기준으로 top-N을 구성하는 방향이 적절하다.

## 범위 안

### A. dynamic universe contract 정의

- rebalance-date membership semantics
- listing / delisting / symbol continuity contract
- current static preset과의 차이 명시

### B. point-in-time universe source design

- historical market-cap reconstruction에 필요한 source 정의
- listing / delisting / symbol mapping source 정의
- missing historical metadata fallback rule 정의

### C. runtime integration first pass

- annual strict family dynamic mode first pass
- static vs dynamic mode 분리
- compare-ready 최소 contract 정의

### D. validation and interpretation

- static vs dynamic annual comparison
- universe drift / candidate drift readout
- PIT mode 결과 설명 문구

## 범위 밖

- live trading
- intraday PIT universe
- full monthly index constituent licensing replacement
- quarterly family full public promotion
- portfolio productization

## 추천 구현 순서

1. dynamic PIT universe contract 문서화
2. historical membership / market-cap source inventory
3. annual strict dynamic mode runtime first pass
4. static vs dynamic comparison report
5. UI mode exposure / diagnostics / docs sync
6. checklist / closeout

함께 볼 reference 문서:

- `PHASE10_PIT_SOURCE_AND_SCHEMA_GAP_ANALYSIS.md`
- `PHASE10_DYNAMIC_PIT_FIRST_PASS_IMPLEMENTATION_ORDER.md`
- `PHASE10_CURRENT_CHAPTER_TODO.md`
- `PHASE10_TEST_CHECKLIST.md`

## 완료 기준

- annual strict family가 `historical dynamic PIT universe` mode로 실행 가능하다
- current static mode와 dynamic mode의 차이가 문서와 UI에 분명히 드러난다
- static vs dynamic 결과 차이를 검토할 수 있다
- 이후 quarterly / portfolio productization으로 넘어갈 기준이 생긴다

## 권고

이 phase는
새로운 전략을 더 추가하는 phase가 아니라,
현재 전략 결과를 **실전 투자에 더 가까운 계약에서 다시 검증하는 phase**
로 보는 것이 맞다.
