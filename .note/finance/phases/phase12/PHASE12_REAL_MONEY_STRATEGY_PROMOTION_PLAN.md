# Phase 12 Real-Money Strategy Promotion Plan

## 목적

- 현재 구현된 전략군을
  “실행은 가능함” 수준에서
  **실전 투자 판단에 쓸 수 있는 계약** 수준으로 끌어올린다.
- prototype / research-only / public-candidate 전략을 다시 구분하고,
  어떤 전략부터 production-grade로 승격할지 우선순위를 고정한다.

쉬운 뜻:

- 이 phase는
  새 전략을 많이 추가하는 phase가 아니다.
- 대신
  “지금 이미 있는 전략 중에서,
  무엇을 실제 투자 판단에 더 가깝게 쓸 수 있게 만들 것인가”
  를 정하고 보강하는 phase다.
- 즉 목표는
  **전략 수를 늘리는 것보다,
  현재 전략을 더 믿고 해석할 수 있게 만드는 것**
  이다.

## 이번 phase의 핵심 질문

1. 어떤 전략군을 현재 시점에서 실전형 후보로 볼 수 있는가
2. 어떤 전략군은 여전히 research-only로 남겨야 하는가
3. 실전형 승격을 위해 공통으로 필요한 계약은 무엇인가
4. 어떤 전략군부터 먼저 production hardening을 해야 하는가

쉬운 뜻:

- 지금 이 문서는
  “뭘 먼저 고칠지”
  “뭘 아직 올리면 안 되는지”
  “실전형이라고 부르려면 최소한 무엇이 있어야 하는지”
  를 정하는 문서다.

## 결론적으로 이번 phase에서 하려는 일

이번 phase는
새로운 전략을 많이 추가하는 phase가 아니라,
**기존 전략군을 실전형 계약으로 승격시키는 phase**
로 잡는다.

즉 초점은 다음과 같다.

- strategy audit
- production contract 정의
- candidate strategy promotion order 고정
- 공통 hardening 항목 구현
- strategy별 real-money checklist 정리

용어 쉽게 보기:

- `strategy audit`
  - 현재 전략들을 다시 점검하고 분류하는 작업
- `production contract`
  - “이 전략을 어디까지 믿고 쓸 수 있는가”에 대한 공통 기준
- `promotion`
  - 단순히 UI에서 더 잘 보이게 하는 것이 아니라,
    실전형 전략 후보로 한 단계 올리는 것
- `hardening`
  - 결과를 더 현실적으로 읽을 수 있게 규칙과 안전장치를 추가하는 것

## 용어 정리

이 문서에서 반복되는 표현을 먼저 짧게 맞춰두면,
뒤의 chapter와 우선순위를 읽기 쉬워진다.

### `prototype`

- 아이디어와 데이터 경로는 열려 있지만,
  아직 실전 판단 기준으로 보기엔 검증과 계약이 부족한 상태다.

### `research-only`

- 연구와 탐색에는 쓰지만,
  실제 투자 판단의 근거로는 아직 쓰지 않는 상태다.

### `public-candidate`

- 완전히 research-only는 아니고,
  더 넓게 노출하거나 일반 사용 경로에 둘 수 있는 후보 상태를 뜻한다.
- 다만 여기서도 곧바로 실전 투자용이라는 뜻은 아니다.

### `production-grade`

- 기능이 돌아가는 수준을 넘어서,
  규칙, 해석, 위험, 제약조건이 함께 정리된 더 단단한 상태를 뜻한다.

### `promotion`

- 전략을 한 단계 더 높은 신뢰도의 상태로 올리는 작업이다.
- 단순히 UI에 더 잘 보이게 하는 것이 아니라,
  더 엄격한 계약과 해석 기준을 붙이는 과정이다.

### `hardening`

- 전략을 더 현실적으로 쓰기 위해
  필터, 비용 가정, 가드레일, 진단 정보를 보강하는 작업이다.

### `candidate`

- 이번 phase에서 먼저 키워볼 가치가 있는 우선 후보를 뜻한다.
- “이미 완성”이라는 의미는 아니다.

### `strategy family`

- 성격이 비슷한 전략 묶음을 뜻한다.
- 예:
  - ETF rotation 전략군
  - strict annual family
  - quarterly prototype family

### `baseline`

- 성능 비교의 기준선으로 쓰는 전략을 뜻한다.
- 실전 승격 우선순위와는 별개로,
  다른 전략이 정말 의미 있는지 비교할 때 필요하다.

### `universe semantics`

- 이 전략이 어떤 종목/ETF 묶음을 대상으로 삼는지에 대한 의미와 규칙이다.
- 쉽게 말하면
  “무엇을 후보로 놓고 전략이 출발하는가”
  를 정하는 개념이다.

### `dynamic PIT`

- 과거 각 시점 기준으로 universe나 입력 데이터를 다시 계산해보는 실전형 검증 방식이다.
- static research mode보다 실전에 더 가까운 검증 계약으로 본다.

### `hold`

- 이번 phase에서 억지로 승격하지 않고,
  현재 상태를 유지하면서 다음 조건을 기다리는 뜻이다.

### `checklist`

- 구현이 끝난 뒤
  “정말 우리가 의도한 계약대로 동작하는지”
  를 사람이 검수하기 위한 확인표다.

## 현재 전략군에 대한 기본 분류

이 분류가 왜 필요한가:

- 지금까지는 전략을
  “실행된다 / 안 된다”
  기준으로 많이 봤다.
- 그런데 실전 투자 목적이라면
  그보다 더 중요한 건
  “이 전략을 지금 어느 정도까지 믿어도 되는가”
  이다.
- 그래서 이번 phase에서는 전략을
  **실전 우선 후보 / 기준선 / 연구용 보류**
  로 다시 나눈다.

### A. 실전형 우선 후보

- `GTAA`
- `Dual Momentum`
- `Risk Parity Trend`
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

이 전략들은
현재 프로젝트 기준으로
실전형 hardening을 적용할 가치가 가장 크다.

쉬운 뜻:

- 이 그룹은
  “지금 당장 실전에 넣어도 된다”는 뜻은 아니다.
- 대신
  **이번 phase에서 가장 먼저 보강할 가치가 큰 전략들**
  이라는 뜻이다.

이유:

- ETF rotation / allocation 계열은 universe semantics가 비교적 단순하다
- strict annual family는 이미 dynamic PIT contract first/second pass를 갖췄다

용어 쉽게 보기:

- `universe semantics`
  - 이 전략이 어떤 종목 묶음을 대상으로 삼는지에 대한 의미/규칙
- `dynamic PIT contract`
  - 과거 각 시점 기준으로 universe를 다시 계산해보는 실전형 검증 계약

### B. baseline / 참고용

- `Equal Weight`
- `Quality Snapshot` broad research path

이 경로들은
연구/비교 기준선으로는 유용하지만,
현재 우선순위 기준으로는 production promotion target이 아니다.

쉬운 뜻:

- 이 전략들은 “쓸모없다”는 뜻이 아니다.
- 대신
  **비교 기준선이나 연구 보조용으로는 좋지만,
  이번 phase의 실전 승격 우선순위는 아니다**
  라는 뜻이다.

### C. research-only 유지

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

이 quarterly family는
현재도 명시적으로 prototype / research-only contract로 읽는 것이 맞다.
이번 phase에서는
**실전형 승격 대상이 아니라 보류 대상**
으로 둔다.

쉬운 뜻:

- 이 전략들은 이번 phase에서 버리는 것이 아니다.
- 다만
  **지금 당장 실전형으로 올리기엔 아직 이르다**
  고 보는 것이다.
- 즉
  연구는 계속할 수 있지만,
  promotion 우선순위에서는 뒤로 둔다.

## 실전형 전략 공통 계약

아래 항목이 있어야
“실전에 더 가까운 백테스트”라고 부를 수 있다.

쉬운 뜻:

- 여기서 말하는 `공통 계약`은
  특정 전략 하나의 세부 공식이 아니라,
  **실전형 전략이라면 공통으로 갖춰야 하는 기본 조건**
  을 뜻한다.
- 예를 들어
  universe를 어떻게 봤는지,
  거래 비용을 무시했는지,
  실제로 매매 가능한 대상을 골랐는지 같은 것들이다.

### 1. universe / data contract 명시

- fixed ETF set인지
- managed static preset인지
- historical dynamic PIT universe인지
- point-in-time 한계가 어디까지인지

### 2. investability filter

- 최소 가격
- 최소 거래대금 또는 최소 유동성 proxy
- listing-age / continuity 조건
- delisted / stale / profile issue 처리 규칙

### 3. turnover / cost contract

- 리밸런싱 시 비용 가정
- slippage / commission / spread first-pass model
- turnover summary 표준 노출

### 4. portfolio guardrail

- 최대 종목 수
- 단일 종목 비중
- cash handling
- overlay / regime 적용 시 행동 규칙

### 5. validation surface

- benchmark 비교
- max drawdown / rolling underperformance
- turnover / rebalance summary
- strategy별 왜 이 결과가 났는지 읽을 수 있는 해석 surface

## 추천 구현 우선순위

이 순서를 먼저 정하는 이유:

- 실전형 승격은 생각보다 손볼 축이 많다.
- 그래서
  “무엇부터 손댈지”를 먼저 고정하지 않으면
  문서만 많아지고 실제 승격은 느려질 수 있다.
- 이번 phase는
  **가장 방어적이고 실무적인 순서**
  로 가는 것이 중요하다.

### Chapter 1. Strategy Production Audit Matrix

목표:

- current strategy family를
  - production candidate
  - baseline only
  - research-only
  로 다시 분류한다.

쉬운 뜻:

- 먼저 전략들을
  “이번에 키울 것 / 기준선으로 둘 것 / 아직 보류할 것”
  으로 나누는 단계다.

### Chapter 2. Real-Money Promotion Contract

목표:

- 실전형 승격에 필요한 공통 계약을 문서로 먼저 고정한다.

핵심 항목:

- investability
- turnover/cost
- benchmark/risk readout
- real-money caution wording

쉬운 뜻:

- 실전형으로 부르려면 최소한 어떤 설명과 규칙이 있어야 하는지
  공통 틀을 먼저 고정하는 단계다.

### Chapter 3. ETF Strategy Hardening

대상:

- `GTAA`
- `Dual Momentum`
- `Risk Parity Trend`

이유:

- universe semantics가 비교적 단순하고
- 가장 먼저 실전형 contract를 얹기 좋다.

쉬운 뜻:

- ETF 전략은
  종목 universe가 복잡한 개별주 전략보다
  먼저 실전형으로 다듬기 쉽다.
- 그래서 가장 먼저 실제 구현 대상으로 잡는다.

### Chapter 4. Strict Annual Family Promotion

대상:

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

이유:

- dynamic PIT validation contract가 이미 들어와 있다.
- 이제 여기에
  investability / cost / promotion gate를 얹는 단계다.

쉬운 뜻:

- annual strict family는
  이미 실전형 검증 기반이 어느 정도 있다.
- 그래서 ETF 다음 순서로
  “실전형 후보”에 더 가깝게 올리기 좋다.

### Chapter 5. Quarterly Family Hold Rule

목표:

- quarterly prototype family는
  계속 research-only로 유지한다는 규칙을 명확히 하고,
  실전 승격 전제 조건만 남긴다.

쉬운 뜻:

- quarterly 전략을 포기하는 게 아니다.
- 다만 이번 phase에서는
  억지로 실전형으로 밀어 올리지 않고,
  어떤 조건이 채워져야 나중에 올릴 수 있는지만 남긴다.

### Chapter 6. Real-Money Checklist And Handoff

목표:

- later batch QA가 아니라
  **실전형 전략 후보 검수 checklist**
  를 만들 수 있는 상태로 정리한다.

쉬운 뜻:

- 마지막에는
  “이 전략이 실전형 후보로 어느 정도 준비됐는지”
  를 체크할 수 있는 검수 기준을 남긴다는 뜻이다.

## 이번 phase의 권고 방향

가장 실무적인 순서는 다음이다.

1. ETF 전략군 production hardening
2. strict annual family production hardening
3. quarterly family는 hold

쉬운 뜻:

- 이번 phase는
  `ETF 먼저 -> annual strict 다음 -> quarterly는 보류`
  순서로 가는 것이 가장 무리 없는 방향이라는 뜻이다.

이 순서가 좋은 이유:

- fixed ETF 전략은 universe ambiguity가 적다
- strict annual family는 dynamic PIT를 이미 확보했다
- quarterly family는 아직 prototype contract를 벗어나지 않았다

## 이번 phase에서 하지 않을 것

- quarterly family를 무리하게 실전형으로 승격
- product/workflow polish를 최우선으로 재개
- new strategy family를 대량 추가

이번 phase는
**기존 전략을 실전에 가까운 수준으로 만드는 것**
이 우선이다.

왜 이렇게 제한하는가:

- 지금 가장 중요한 건
  “전략을 더 많이 만드는 것”이 아니라
  “지금 있는 전략 중 무엇을 실제 투자 판단에 더 가까운 상태로 올릴 것인가”
  이다.
- 그래서 이번 phase는 일부러 범위를 좁게 잡는다.
