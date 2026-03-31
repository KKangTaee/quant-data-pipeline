# Phase 9 Real-Money Validation Direction

## 목적

- 현재 strict coverage preset과 diagnostics tooling을
  실전 투자 판단 기준에서 어떻게 해석해야 하는지 고정한다.
- 무엇을 지금 바로 product-like surface로 확장해도 되는지,
  무엇은 그 전에 point-in-time validation을 먼저 거쳐야 하는지
  우선순위를 분명히 한다.

## 핵심 용어 설명

이 문서에서 반복해서 쓰는 표현들은 아래 뜻으로 읽는 것이 맞다.

### 1. universe contract

여기서 `universe contract`는
**“이 backtest가 어떤 종목 집합을, 어떤 기준 시점으로, 어떤 규칙에 따라 후보로 삼는가”**
를 뜻한다.

쉽게 말하면 아래 세 가지를 묶은 약속이다.

1. 어떤 종목이 모집군에 들어오는가
2. 그 모집군이 run 전체에서 고정되는가, 리밸런싱 날짜마다 바뀌는가
3. 상장 / 상폐 / 심볼 변경 / coverage 부족을 어떻게 처리하는가

예:

- `managed static research universe`
  - 현재 시점 기준 managed preset을 먼저 고정해 두고
  - 각 리밸런싱 날짜마다 usable한 종목만 남기는 계약
- `historical dynamic PIT universe`
  - 각 리밸런싱 날짜마다 그 시점 기준 membership를 다시 계산하는 계약

즉 `universe contract`는 단순히 “100개를 쓴다”가 아니라,
**그 100개를 어떤 방식으로 정의했는가**를 말한다.

### 2. survivorship / universe drift

#### survivorship

여기서 `survivorship`는
과거 백테스트를 돌릴 때
**지금까지 살아남은 종목들만 기준으로 과거를 보는 왜곡**
을 뜻한다.

예:

- 2026년 기준으로 남아 있는 top-1000만 들고
  2016년 백테스트를 돌리면
- 중간에 상폐되었거나 밀려난 종목이 빠질 수 있다

그러면 실제 과거 투자 환경보다
더 좋은 결과가 나올 위험이 있다.

#### universe drift

`universe drift`는
시간이 지나면서 모집군 자체가 바뀌는 현상을 뜻한다.

예:

- 어떤 종목은 2018년엔 top-1000이 아니었지만 2024년엔 top-1000이 될 수 있다
- 반대로 어떤 종목은 예전엔 핵심 대형주였지만 나중엔 탈락할 수 있다

실전에서는 이 drift가 자연스럽게 존재하므로,
진짜 실전형 검증은 이 변화를 가능한 한 point-in-time으로 반영해야 한다.

### 3. diagnostics bucket / eligible / review_needed / excluded

`diagnostics bucket`은
coverage gap이나 source 이상을
**같은 원인 그룹끼리 묶어놓은 진단 분류**
를 뜻한다.

예:

- `raw_present_shadow_missing`
- `source_present_raw_missing`
- `source_empty_or_symbol_issue`
- `foreign_or_nonstandard_form_structure`

이 bucket에 대해 정책적으로 아래 상태를 붙인다.

- `eligible`
  - 현재 strict universe에 포함 가능한 상태
  - 필요하면 rebuild 같은 운영 조치 후 계속 사용
- `review_needed`
  - 자동 포함/제외를 아직 확정하지 않고
  - targeted recollection 또는 정책 판단이 더 필요한 상태
- `excluded`
  - 현재 strict canonical preset에서는 제외하는 상태

즉 `diagnostics bucket -> policy state` 연결은
“이 진단 결과를 운영과 preset governance에서 어떻게 취급할 것인가”
를 고정하는 작업이다.

### 4. foreign / non-standard form issuer

이 표현은
미국 일반 issuer가 흔히 쓰는 `10-Q`, `10-K` 중심 경로가 아니라,
다른 filing 구조로 공시하는 issuer를 뜻한다.

예:

- `20-F`
- `6-K`
- `40-F`

이런 심볼은 source에 데이터가 있더라도,
현재 strict statement path가 기대하는 filing 구조와 다를 수 있다.

즉 이 문맥에서 말하는
`foreign / non-standard form issuer 기본 처리 규칙 고정`
은:

- 이런 issuer를 지금 strict preset에 기본 포함할지
- 일단 제외하고 later support workstream으로 미룰지

를 정책으로 결정한다는 뜻이다.

### 5. portfolio productization

`portfolio productization`은
전략 결과를 단순 연구 화면이 아니라
**실제 사용자 워크플로우로 묶는 제품화 작업**
을 뜻한다.

예:

- saved portfolio
- compare-to-portfolio
- weighted portfolio builder
- portfolio 결과 저장 / 재실행 / drilldown
- richer exposure / contribution / attribution readout

즉 productization은
“백테스트 엔진의 contract를 더 정확하게 만드는 일”이 아니라,
**이미 있는 전략/결과를 사용자가 더 편하게 쓰게 만드는 일**
에 가깝다.

이 문서에서 productization을 뒤로 미루자는 뜻은,
지금은 UX 확장보다
**실전형 universe contract를 먼저 엄격하게 만드는 것이 우선**
이라는 의미다.

## 현재 상태에 대한 해석

현재 strict annual / quarterly family는
다음 두 층으로 나뉜다.

1. strategy / diagnostics / operator tooling
   - 상당 부분 구현이 정리되어 있음
2. universe semantics / historical point-in-time validation
   - 아직 최종 실전 기준으로는 부족함

특히 현재 `Coverage 100/300/500/1000`은
**historical monthly top-N universe가 아니라, managed static research universe**
로 해석하는 것이 맞다.

즉:

- preset membership 자체는 현재 기준 managed universe를 사용하고
- run 안에서 각 rebalance date마다 usable symbol만 남긴다

이 구조는 연구와 운영 점검에는 유용하지만,
실전 투자용 최종 검증 계약으로는 부족하다.

## 왜 여기서 멈춰서 정책을 고정해야 하나

지금 바로 portfolio productization을 더 밀어도
사용 경험은 좋아질 수 있다.
하지만 실전 투자 기준에서는
다음 질문에 먼저 답이 있어야 한다.

1. 현재 universe contract를 정확히 무엇으로 볼 것인가
2. 예외 심볼(`MRSH`, `AU`)은 어떤 정책으로 취급할 것인가
3. annual / quarterly 결과를 어느 수준까지 신뢰할 것인가
4. survivorship / universe drift를 얼마나 허용할 것인가

이 기준이 없으면
UI는 좋아져도 backtest contract 자체가 흔들릴 수 있다.

## 권장 진행 방향

### 1. Phase 9에서는 policy를 먼저 고정한다

이번 phase에서 먼저 해야 하는 일은 구현 확장보다 아래 결정이다.

- current preset semantics를 `managed static research universe`로 공식 고정
- diagnostics bucket을 `eligible / review_needed / excluded` 정책으로 연결
- foreign / non-standard form issuer 기본 처리 규칙 고정
- annual / quarterly strict family의 승격 조건 고정

이 단계의 목적은:

- “현재 결과를 어디까지 믿을 수 있는가”
- “어떤 심볼은 왜 preset에서 빠져야 하는가”
- “어떤 결과는 아직 research-only인가”

를 문서와 operator flow 기준으로 고정하는 것이다.

### 2. 그 다음 최우선 구현은 Historical Dynamic PIT Universe mode다

실전 투자까지 생각하면,
다음 major engineering priority는
**portfolio productization보다 historical dynamic PIT universe** 쪽이 더 중요하다.

권장 이유:

- current preset membership는 현재 기준 top-N 관리 리스트이므로
  과거 각 월의 실제 top-N membership를 재현하지 않는다
- real-money 검증에서는
  monthly membership drift / listing timing / delisting / universe turnover가
  결과에 직접 영향을 준다
- 이 부분을 해결하지 않고 product surface만 넓히면
  보기 좋은 연구 UI는 되지만,
  실전형 검증 기준으로는 약하다

즉:

- 현재 mode = 빠른 연구 / 운영 / 아이디어 필터링
- future dynamic PIT mode = 실전형 검증 기준

으로 역할을 분리하는 것이 좋다.

### 3. Portfolio productization은 그 다음 단계로 미룬다

`saved portfolio`, `compare-to-portfolio`, `research workflow surface`는
충분히 가치 있는 작업이지만,
실전 투자 목표 기준에서는
dynamic PIT universe보다 먼저 오면 우선순위가 뒤집힌다.

따라서 권고 순서는:

1. Phase 9: policy / governance / promotion gate
2. Next major phase: historical dynamic PIT universe
3. 그 다음: portfolio productization

## annual / quarterly family에 대한 현재 권고

### strict annual family

- 현재는 가장 앞선 candidate
- 다만 여전히 `managed static research universe` 계약 위에 있으므로
  실전 배치 전 최종 검증은 dynamic PIT mode를 거치는 것이 맞다

### strict quarterly family

- 아직 `research-only`
- coverage / form policy / batch QA가 더 정리되어야 함
- public candidate나 실전형 판단 근거로 올리기에는 아직 이름값이 크다

## MRSH / AU 같은 예외 심볼을 보는 방식

이 예외들은 단순 “마지막 날짜에 stale” 문제가 아니라
policy bucket 예시로 보는 것이 더 정확하다.

- `MRSH`
  - `source_empty_or_symbol_issue`
  - symbol/source validity review bucket
- `AU`
  - `foreign_or_nonstandard_form_structure`
  - foreign-form support vs exclusion policy bucket

즉 이 심볼들은
단순 targeted recollection 대상이라기보다,
Phase 9 정책을 고정할 때 대표 예시로 쓰는 편이 맞다.

## 실전 투자 기준의 운영 원칙

현재 프로젝트를 실전형으로 끌고 가려면,
아래 원칙을 유지하는 것이 좋다.

1. 현재 static preset 결과를 최종 실전 근거로 과대해석하지 않는다
2. diagnostics 결과는 operator action뿐 아니라 policy bucket으로 기록한다
3. quarterly는 research-only 계약을 유지한다
4. product surface보다 universe semantics를 먼저 고정한다
5. 실전형 최종 승격은 dynamic PIT universe validation 이후로 미룬다

## 한 줄 결론

내 기준 권고는 명확하다.

- **Phase 9에서는 policy를 고정**
- **그 다음은 dynamic PIT universe 구현**
- **portfolio productization은 그 이후**

즉,
지금 프로젝트를 실전 투자까지 가져가려면
“더 예쁜 product surface”보다
“더 엄격한 universe contract”를 먼저 완성하는 편이 맞다.
