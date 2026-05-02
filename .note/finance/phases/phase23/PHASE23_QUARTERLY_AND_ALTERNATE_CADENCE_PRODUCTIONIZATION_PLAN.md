# Phase 23 Quarterly And Alternate Cadence Productionization Plan

## 이 문서는 무엇인가

`Phase 23`에서 quarterly / alternate cadence 백테스트 기능을 어떻게 제품 기능으로 끌어올릴지 정리한 계획 문서다.

여기서 말하는 핵심은 투자 후보를 새로 고르는 것이 아니다.
이미 존재하는 quarterly strict family와 cadence 관련 실행 경로를 사용자가 믿고 실행, 비교, 저장, 재실행할 수 있는 기능으로 다듬는 것이다.

## 목적

`Phase 23`의 목적은 세 가지다.

1. 현재 `prototype` 또는 `research-only`에 가까운 quarterly strict family의 상태를 정확히 파악한다.
2. annual strict family에 비해 부족한 입력, 실행, compare, history, report, saved replay 차이를 줄인다.
3. 이후 `Phase 24`에서 새 전략을 붙일 때 cadence별 실행 경로가 흔들리지 않도록 기준을 만든다.

## 쉽게 말하면

지금 annual strict 전략은 비교적 성숙한 길이 있다.
반면 quarterly 전략은 실행은 되지만 아직 "실험용으로 열어둔 기능"에 가깝다.

`Phase 23`은 quarterly 전략을 "버튼은 있는데 설명이 애매한 기능"에서
"사용자가 선택하고, 실행하고, 결과를 다시 불러와도 의미가 유지되는 기능"으로 올리는 단계다.

## 왜 필요한가

앞으로 전략을 제대로 넓히려면 annual만으로는 부족하다.
어떤 전략은 quarterly 재무제표 흐름이 더 자연스럽고,
어떤 전략은 annual과 quarterly를 비교해 봐야 한다.

하지만 quarterly가 계속 prototype 상태라면 문제가 생긴다.

- annual 결과와 quarterly 결과를 같은 수준으로 비교하기 어렵다.
- compare / history / saved replay에서 설정이 정확히 복원되는지 확신하기 어렵다.
- 새 전략을 붙일 때 annual 기준으로만 구현하게 되어 구조가 다시 불균형해진다.
- 사용자는 이 결과가 연구용인지, 제품 기능으로 믿고 써도 되는지 구분하기 어렵다.

## 이 phase가 끝나면 좋은 점

`Phase 23`이 끝나면 다음이 좋아져야 한다.

- quarterly strict family를 UI에서 실행할 때 현재 기능의 의미와 한계가 더 명확해진다.
- annual / quarterly / alternate cadence의 입력 차이가 문서와 UI에서 더 잘 보인다.
- compare, history, load/replay 흐름에서 cadence별 설정이 더 안정적으로 이어진다.
- quarterly 결과를 볼 때 "이건 아직 연구용 경고가 필요한가" 또는 "제품 기능으로 검수 가능한가"를 판단할 수 있다.
- `Phase 24`에서 신규 전략을 구현할 때 cadence 지원 기준을 재사용할 수 있다.

## 이 phase에서 다루는 대상

직접 다루는 대상:

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`
- quarterly strict family의 single strategy 실행 UI
- quarterly strict family의 compare / history / load-into-form / saved replay 흐름
- quarterly factor timing과 point-in-time 해석 문구
- annual strict family와 quarterly strict family의 입력 contract 차이

직접 다루지 않는 대상:

- 새로운 투자 후보 선발
- portfolio weight 최적화
- live trading 또는 실제 주문 연동
- quarterly 결과를 곧바로 real-money candidate로 승격하는 판단
- `Phase 24`에서 다룰 신규 strategy family 구현

## 현재 구현 우선순위

1. 현재 quarterly 기능 상태를 먼저 재고로 잡는다.
   - 쉽게 말하면: 이미 되는 것과 아직 prototype인 것을 표로 나눈다.
   - 왜 먼저 하는가: 바로 코드부터 바꾸면 어떤 차이를 메워야 하는지 흐려진다.
   - 기대 효과: 구현 범위가 투자 분석이 아니라 제품 기능 개선으로 고정된다.

2. quarterly UI와 문구를 제품 기능 기준으로 정리한다.
   - 쉽게 말하면: 사용자가 "이 버튼을 누르면 무엇이 실행되는지" 바로 알 수 있게 한다.
   - 왜 필요한가: quarterly는 현재 prototype 문구와 실제 실행 가능성이 섞여 있어 오해가 쉽다.
   - 기대 효과: manual QA에서 확인할 항목이 더 명확해진다.

3. compare / history / saved replay 복원 흐름을 확인한다.
   - 쉽게 말하면: quarterly 결과를 다시 열거나 compare로 불러왔을 때 같은 설정으로 이어지는지 본다.
   - 왜 필요한가: 제품 기능은 한 번 실행되는 것보다 다시 재현되는 것이 중요하다.
   - 기대 효과: quarterly 결과를 나중에 다시 검토할 수 있다.

4. representative smoke validation을 남긴다.
   - 쉽게 말하면: 대표 입력 몇 개로 실제 실행이 깨지지 않는지 확인한다.
   - 왜 필요한가: Phase 23은 broad investment search가 아니라 기능 검증 phase이기 때문이다.
   - 기대 효과: Phase 24로 넘어가기 전에 cadence lane이 최소한의 신뢰 기준을 가진다.

## 이 문서에서 자주 쓰는 용어

- `Cadence`
  - 리밸런싱과 factor 계산 주기를 뜻한다.
  - 여기서는 annual, quarterly, 그리고 이후 추가될 수 있는 다른 실행 주기를 묶어 부르는 말이다.
- `Productionization`
  - 이미 돌아가는 prototype 기능을 사용자가 반복해서 쓸 수 있는 제품 기능으로 다듬는 작업이다.
- `Strict Quarterly Prototype`
  - quarterly 재무제표 기반으로 실행되는 strict family이지만, 아직 annual strict만큼 입력 contract와 검증 surface가 완성되지 않은 상태를 뜻한다.
- `Alternate Cadence`
  - annual / quarterly 외에 월간, 반기, 다른 리밸런싱 주기처럼 나중에 확장될 수 있는 cadence를 뜻한다.
- `Representative Smoke Validation`
  - 모든 조합을 깊게 최적화하는 것이 아니라, 대표 조합으로 기능이 깨지지 않는지 확인하는 가벼운 검증이다.

## 이번 phase의 운영 원칙

- 기본 방향은 개발이다. 투자 분석이나 최종 후보 선정이 아니다.
- quarterly 결과가 좋아 보여도 자동으로 promotion하거나 real-money candidate로 해석하지 않는다.
- 깊은 백테스트 탐색보다 먼저 UI, payload, history, replay의 재현성을 본다.
- annual strict와 완전히 똑같이 만들기보다, 왜 다른지 설명 가능한 상태를 목표로 한다.
- 사용자가 특정 quarterly 결과 분석을 따로 요청하면 그때는 `사용자 요청 분석`으로 분리해 기록한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: quarterly productionization frame 정의

- 무엇을 바꾸는가:
  - 현재 quarterly strict family가 어디까지 구현되어 있고 어디가 prototype인지 문서로 고정한다.
- 왜 필요한가:
  - Phase 23의 작업 범위가 투자 분석으로 흐르지 않게 하기 위해서다.
- 끝나면 좋은 점:
  - 다음 코드 수정이 "무엇을 제품 기능으로 올리는가"에 맞춰진다.

### 두 번째 작업: quarterly UI와 입력 설명 정리

- 무엇을 바꾸는가:
  - single strategy UI에서 quarterly 이름, 설명, warning, advanced input 흐름을 정리한다.
- 왜 필요한가:
  - 현재 사용자는 quarterly가 연구용인지, 제품 기능인지, 어떤 값이 중요한지 빠르게 이해하기 어렵다.
- 끝나면 좋은 점:
  - manual QA에서 확인할 화면과 문구가 분명해진다.

### 세 번째 작업: compare / history / saved replay 연결 확인

- 무엇을 바꾸는가:
  - quarterly 실행 결과가 compare, history, load-into-form, saved replay에서 같은 의미로 복원되는지 확인하고 필요한 부분을 보강한다.
- 왜 필요한가:
  - 재현되지 않는 결과는 제품 기능으로 쓰기 어렵다.
- 끝나면 좋은 점:
  - quarterly 결과를 저장하고 나중에 다시 검토할 수 있다.

### 네 번째 작업: representative validation과 checklist 작성

- 무엇을 바꾸는가:
  - 대표 실행 조합과 확인 문서를 남기고, 사용자가 직접 검수할 checklist를 정리한다.
- 왜 필요한가:
  - Phase 23은 완전한 투자 최적화가 아니라 기능 검수 phase이므로, 무엇을 통과해야 하는지 분명해야 한다.
- 끝나면 좋은 점:
  - Phase 24에서 새 전략을 붙이기 전 cadence 기능의 최소 신뢰 기준이 생긴다.

## 다음에 확인할 것

- 현재 quarterly strict family가 실제로 어떤 runner와 UI 경로를 쓰는지 확인한다.
- annual strict에는 있지만 quarterly에는 없는 입력 contract를 목록화한다.
- 그 차이가 반드시 구현해야 할 차이인지, 문구로 설명하면 되는 차이인지 분리한다.
- compare / history / saved replay에서 quarterly 설정이 빠지는지 확인한다.

## 한 줄 정리

`Phase 23`은 quarterly / alternate cadence를 투자 분석 대상으로 확장하는 phase가 아니라, 다음 전략 확장을 위해 백테스트 제품 기능으로 끌어올리는 phase다.
