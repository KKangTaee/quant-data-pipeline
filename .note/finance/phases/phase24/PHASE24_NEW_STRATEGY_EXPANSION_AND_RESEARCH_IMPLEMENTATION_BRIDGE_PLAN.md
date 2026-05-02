# Phase 24 New Strategy Expansion And Research Implementation Bridge Plan

## 이 문서는 무엇인가

`Phase 24`에서 새 전략을 어떻게 finance 백테스트 제품 안으로 추가할지 정리한 계획 문서다.

여기서 핵심은 새 전략의 투자 성과를 바로 판단하는 것이 아니다.
`quant-research`에 있는 전략 문서를 실제 `quant-data-pipeline` 구현으로 옮길 때,
어떤 기준으로 고르고, 어디까지 UI / runtime / compare / history에 붙여야 하는지 표준 경로를 만드는 것이다.

## 목적

1. 새 전략 후보를 아무거나 고르지 않고, 현재 데이터와 백테스트 구조에 맞는 후보부터 고른다.
2. `research note -> finance runtime -> UI -> compare/history/replay`로 이어지는 구현 기준을 만든다.
3. 첫 신규 전략 family를 제품 안에 붙이는 최소 구현 단위를 실행한다.

## 쉽게 말하면

지금까지는 Value / Quality / Quality + Value와 cadence 정리에 집중했다.
이제는 프로그램이 “새로운 전략을 계속 추가할 수 있는 구조”인지 확인할 차례다.

다만 성과 좋은 전략을 찾는 단계가 아니라,
새 전략을 넣을 때마다 같은 방식으로 실행하고 비교하고 다시 열 수 있게 만드는 단계다.

## 왜 필요한가

- 새 전략을 매번 임시 코드로 붙이면 UI, report, history, compare 연결이 계속 달라진다.
- `quant-research`에 전략 문서가 많아도, 구현 기준이 없으면 실제 제품 기능으로 이어지기 어렵다.
- 새 전략을 붙이는 표준 경로가 생기면 이후 전략 라이브러리 확장이 훨씬 덜 흔들린다.

## 이 phase가 끝나면 좋은 점

- 어떤 research note가 구현 후보인지 더 쉽게 판단할 수 있다.
- 첫 신규 전략 family가 single / compare / history 흐름에 들어온다.
- 이후 전략을 추가할 때 따라 할 수 있는 구현 템플릿이 생긴다.
- 투자 분석과 제품 개발 검증이 섞이지 않게 된다.

## 이 phase에서 다루는 대상

직접 다루는 대상:

- `quant-research/.note/research/strategies/`에 있는 전략 문서
- price-only ETF 전략처럼 현재 DB loader로 구현 가능한 전략 후보
- finance strategy / sample / runtime / web UI / catalog 연결 경로
- compare / history / saved replay 최소 연결 기준
- Phase 24 manual checklist와 smoke validation report

직접 다루지 않는 대상:

- 옵션, 이벤트드리븐, M&A, 선물 직접 복제처럼 별도 데이터 엔지니어링이 큰 전략의 본격 구현
- 새 전략의 real-money promotion 판단
- live trading 또는 실제 주문 연동
- quarterly real-money contract / guardrails parity 구현

## 현재 구현 우선순위

1. research-to-implementation 기준을 먼저 고정한다.
   - 쉽게 말하면: 어떤 전략을 지금 구현할 수 있고, 어떤 전략은 나중에 해야 하는지 나눈다.
   - 왜 먼저 하는가: 후보 선정 기준 없이 구현하면 Phase 24가 또 투자 분석처럼 흐를 수 있다.
   - 기대 효과: 첫 구현 후보를 납득 가능한 기준으로 고를 수 있다.

2. 첫 신규 전략 후보를 선정한다.
   - 쉽게 말하면: 지금 codebase에 가장 안전하게 붙일 수 있는 전략을 하나 고른다.
   - 왜 필요한가: Phase 24는 표준 경로를 실제 코드로 한 번 통과시켜야 의미가 있다.
   - 기대 효과: 새 전략 추가 workflow의 병목이 빨리 드러난다.

3. 첫 신규 전략 family를 최소 제품 경로에 붙인다.
   - 쉽게 말하면: single 실행, compare, history, replay까지 최소한으로 이어지게 한다.
   - 왜 필요한가: single 실행만 되면 “제품 전략”이라고 부르기 어렵다.
   - 기대 효과: 이후 새 전략 추가의 구현 템플릿이 된다.

4. representative smoke validation과 checklist를 남긴다.
   - 쉽게 말하면: 모든 조합을 깊게 분석하지 않고, 기능이 깨지지 않는지 대표 케이스로 확인한다.
   - 왜 필요한가: Phase 24는 투자 분석 phase가 아니라 신규 전략 구현 경로 검증 phase다.
   - 기대 효과: Phase 25 pre-live readiness로 넘어가기 전 전략 확장 경로가 남는다.

## 이 문서에서 자주 쓰는 용어

- `Research-to-Implementation Bridge`
  - research note에 적힌 전략 아이디어를 실제 finance 백테스트 코드와 UI로 옮기는 연결 기준이다.
- `Implementation Candidate`
  - 지금 codebase와 데이터로 실제 구현 가능한 전략 후보다.
- `Strategy Family`
  - 사용자가 UI에서 하나의 전략 묶음으로 인식하는 백테스트 family다.
- `Price-Only ETF Strategy`
  - 재무제표, 옵션, 이벤트 데이터 없이 ETF 가격 데이터만으로 먼저 구현 가능한 전략이다.
- `Minimum Product Path`
  - 새 전략이 최소한 single 실행, compare, history, saved replay 흐름까지 연결되는 경로다.

## 이번 phase의 운영 원칙

- 기본 방향은 개발이다. 투자 추천이나 최종 후보 선발이 아니다.
- 첫 구현 후보는 데이터 요구가 단순하고 현재 DB-backed runtime에 붙일 수 있어야 한다.
- 새 전략을 붙일 때 single 실행만 보고 끝내지 않는다. compare / history / replay 연결을 같이 본다.
- 복잡한 데이터가 필요한 전략은 shortlist에는 남기되 첫 구현에서는 제외한다.
- quarterly real-money / guardrail parity는 Phase 24의 주 작업이 아니라 future readiness backlog로 유지한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: research-to-implementation bridge 정의

- 무엇을 바꾸는가:
  - `quant-research` 전략 문서를 구현 후보로 고르는 기준과 첫 후보를 정리한다.
- 왜 필요한가:
  - 새 전략 확장이 투자 분석으로 흐르지 않고 제품 구현 경로로 남기 위해서다.
- 끝나면 좋은 점:
  - “왜 이 전략을 먼저 구현하는가”가 문서와 코드 모두에서 설명된다.

### 두 번째 작업: first new family runtime 구현

- 무엇을 바꾸는가:
  - 첫 신규 전략 family의 simulation / sample / runtime wrapper를 추가한다.
- 왜 필요한가:
  - 문서 기준만으로는 새 전략 확장 workflow를 검증할 수 없다.
- 끝나면 좋은 점:
  - 실제 DB-backed 실행이 가능한 신규 전략이 생긴다.

### 세 번째 작업: UI / compare / history / replay 연결

- 무엇을 바꾸는가:
  - 새 전략을 `Backtest` 화면에서 선택하고, compare에 넣고, history에서 다시 실행할 수 있게 한다.
- 왜 필요한가:
  - 사용자가 실제 제품 기능으로 쓰려면 재진입 경로가 필요하다.
- 끝나면 좋은 점:
  - 이후 신규 전략을 붙일 때 따라 할 수 있는 UI 연결 기준이 생긴다.

### 네 번째 작업: smoke validation과 checklist

- 무엇을 바꾸는가:
  - 대표 실행 결과와 manual QA checklist를 남긴다.
- 왜 필요한가:
  - 새 전략이 제품 안에서 깨지지 않는지 검수해야 한다.
- 끝나면 좋은 점:
  - Phase 24를 닫을 수 있는 검증 기준이 생긴다.

## 다음에 확인할 것

- 첫 구현 후보는 `Global Relative-Strength Allocation With Trend Safety Net`으로 채택했다.
- core strategy / sample helper / runtime wrapper first pass는 완료했고,
  representative DB-backed smoke run까지 통과했다.
- single / compare / history / saved replay에 필요한
  catalog 등록, UI 입력, payload, meta 왕복도 연결했다.
- 다음 확인 대상은 사용자가 `PHASE24_TEST_CHECKLIST.md`로 실제 화면 QA를 완료하는 것이다.

## 한 줄 정리

`Phase 24`는 새 전략의 성과를 바로 고르는 phase가 아니라, research note를 finance 백테스트 제품 기능으로 옮기는 표준 경로를 만드는 phase다.
