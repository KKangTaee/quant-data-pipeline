# Phase 3 Broad Statement Loader Policy

## 목적
이 문서는 Phase 3에서 구현할
broad detailed financial statement loader의
허용 범위를 고정하기 위한 정책 문서다.

관련 문서:
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phase3/PHASE3_LOADER_NAMING_POLICY.md`
- `.note/finance/phase3/PHASE3_STRICT_STATEMENT_LOADER_SCOPE.md`

---

## 1. 기본 결론

Phase 3의 broad statement loader는
strict PIT loader보다 넓게 읽을 수 있는
research-oriented loader로 정의한다.

하지만 broad loader라고 해서
초기 mixed-state나 identity-broken row를
다시 허용하는 것은 아니다.

즉 broadness의 의미는:
- 더 넓은 조회 목적
- 더 느슨한 time semantics
- 더 넓은 출력 형태

이지,
- 불완전한 raw identity 허용
- point-in-time에 부적합한 broken row 복귀

를 뜻하지는 않는다.

---

## 2. broad loader의 핵심 역할

Phase 3의 broad statement loader는
다음 목적에 우선 사용된다.

1. 연구용 historical statement inspection
2. concept-level exploratory analysis
3. custom factor prototype 계산용 원천 조회
4. wide / pivot 형태의 실험용 데이터 가공

즉 broad loader는
"정확한 backtest snapshot"보다
"연구와 탐색을 위한 유연한 조회"
에 초점을 둔다.

---

## 3. broad loader가 strict loader와 다른 점

strict loader:
- `available_at <= as_of_date` 필수
- snapshot selection 필수
- 백테스트 입력용

broad loader:
- `as_of_date` 없이 history read 가능
- `period_end` 중심 range 조회 가능
- latest-by-period-end 같은 research-friendly read 허용
- strict PIT를 보장하지 않음

즉 broad loader는
time semantics를 느슨하게 가져가되,
raw row identity 자체는 무너뜨리지 않는다.

---

## 4. broad loader가 허용하는 조회 패턴

Phase 3 broad statement loader는
아래 조회를 허용한다.

1. `period_end` 기준 historical range 조회
2. symbol 집합 기준 raw values 조회
3. optional `statement_type`, `concepts`, `units` 필터
4. research용 pivot / wide reshape 전제의 row 반환
5. 필요 시 labels summary join 또는 lookup 보조

예상 함수:
- `load_statement_values(...)`
- `load_statement_history(...)` 또는 내부 helper

---

## 5. broad loader도 유지해야 하는 최소 제약

broad loader라도
아래 제약은 유지하는 것이 맞다.

1. source는 `nyse_financial_statement_values`
2. `accession_no`, `unit`, `available_at`가 있는 현재 strict schema를 전제로 한다
3. labels 테이블은 보조 정보로만 쓴다
4. row identity는 `(symbol, freq, accession_no, statement_type, concept, period_end, unit)`를 따른다

즉 broad loader는
schema cleanup 이전의 legacy mixed-state를
지원 대상으로 삼지 않는다.

---

## 6. mixed-state / legacy row 정책

이번 Phase 3 정책에서는
상세 재무제표 broad loader가
legacy mixed-state row를 허용하지 않는 것으로 고정한다.

이유:
1. Phase 2에서 values table을 strict raw ledger로 재정의했다
2. 로컬 DB도 이미 reset/rebuild 되었다
3. broadness를 위해 broken row를 다시 허용할 이유가 없다
4. broad/strict 차이는 availability semantics와 output shape로도 충분히 구분된다

정리:
- strict와 broad의 차이:
  - "깨진 row를 읽느냐"가 아니라
  - "PIT 보장을 강제하느냐"다

---

## 7. labels 테이블 사용 범위

`nyse_financial_statement_labels`는 broad loader에서만
선택적으로 보조 사용 가능하다.

허용 범위:
- concept 설명 보조
- operator-facing display label
- summary UI lookup

비허용 범위:
- strict source-of-truth 대체
- values row identity 대체
- PIT snapshot selection 기준

---

## 8. broad loader의 1차 입력 범위

Phase 3 broad loader는
아래 입력 조합을 우선 지원하는 것이 적절하다.

- `symbols`
- `start`
- `end`
- `freq`
- optional `statement_type`
- optional `concepts`
- optional `units`

strict loader와 달리:
- `as_of_date`는 선택적이거나 불필요할 수 있다

---

## 9. broad loader가 1차에 보장하지 않는 것

아래는 broad loader의 1차 범위 밖이다.

1. strict PIT safety
2. portfolio-ready aligned panel output
3. automatic factor normalization
4. universe-wide heavy optimization
5. semantic taxonomy 완성

즉 broad loader는
연구용 raw access layer이며,
전략 실행 직전의 최종 panel builder는 아니다.

---

## 10. 구현 기준 요약

Phase 3 broad statement loader의 구현 기준:

1. 기본 이름은 `load_statement_values(...)`
2. source는 `nyse_financial_statement_values`
3. strict PIT filter는 기본 강제가 아님
4. `period_end` 중심 history read를 허용
5. labels는 optional helper
6. broken legacy row는 허용하지 않음

---

## 결론

Phase 3의 broad statement loader는
strict PIT loader보다 넓은 연구용 조회를 허용하지만,
Phase 2에서 정리한 stricter raw ledger 기준은 유지한다.

즉 broad loader의 넓음은
identity 완화가 아니라
조회 목적과 시간 해석의 완화에서 나온다.
