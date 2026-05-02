# Phase 3 Strict Statement Loader Scope

## 목적
이 문서는 Phase 3에서 구현할
strict detailed financial statement loader의
보수적 범위를 먼저 고정하기 위한 정책 문서다.

관련 문서:
- `.note/finance/phases/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phases/phase3/PHASE3_LOADER_NAMING_POLICY.md`
- `.note/finance/phases/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`

---

## 1. 기본 결론

Phase 3의 strict statement loader는
`nyse_financial_statement_values`를
point-in-time snapshot source로 읽는
보수적 loader로 정의한다.

초기 구현 범위:
- values 테이블 중심
- snapshot read 중심
- `available_at <= as_of_date` 필수
- accession-bearing row만 허용

즉, Phase 3의 strict loader는
"연구용으로 넓게 읽는 loader"가 아니라
"백테스트 snapshot에서 미래 정보 유입을 최대한 줄이는 loader"
로 본다.

---

## 2. 대상 함수 범위

우선 strict statement loader 범위에 포함되는 함수:

- `load_statement_snapshot_strict(...)`
  - 특정 `as_of_date` 기준 최신 사용 가능 snapshot을 반환

후속 후보:
- `load_statement_values_strict(...)`
  - strict 필터가 적용된 statement history 조회

이번 챕터에서 먼저 고정하는 핵심은:
- snapshot strict loader 정책

이유:
- 백테스트에서 가장 먼저 필요한 것은
  시점별 snapshot 조회이기 때문
- full strict history loader는
  snapshot 규칙이 확정된 뒤 확장해도 늦지 않음

---

## 3. strict loader가 반드시 적용할 필터

strict statement snapshot loader는
최소한 아래 조건을 항상 포함해야 한다.

1. `accession_no IS NOT NULL`
2. `accession_no <> ''`
3. `unit IS NOT NULL`
4. `unit <> ''`
5. `available_at IS NOT NULL`
6. `available_at <= as_of_date`

의미:
- legacy row 제외
- raw identity가 불완전한 row 제외
- 실제 시장 사용 가능 시점이 없는 row 제외
- `period_end`가 아니라 availability 기준으로 snapshot 선택

---

## 4. strict snapshot selection 규칙

strict loader는
"해당 시점에 실제로 사용 가능했던 row 중 가장 최신"
을 선택해야 한다.

정렬 우선순위:
1. `available_at DESC`
2. `period_end DESC`
3. `accession_no DESC`

이 규칙은 다음을 의미한다.
- `period_end`만 최신이라고 채택하지 않는다
- 더 늦게 공시된 동일/수정 filing이 있으면
  availability가 우선한다

---

## 5. strict loader의 반환 단위

Phase 3의 strict statement loader는
기본적으로 raw values row를 반환한다.

즉:
- source of truth는 `nyse_financial_statement_values`
- `nyse_financial_statement_labels`는 strict source가 아님

labels 테이블의 역할:
- summary lookup
- operator review
- concept 설명 보조

따라서 strict loader는
labels 테이블에 의존하지 않고 동작해야 한다.

---

## 6. strict loader가 1차에 보장하는 것

Phase 3의 1차 strict statement loader가 보장하려는 것은 아래까지다.

1. 상세 재무제표 row를 values 테이블에서 읽는다
2. identity-complete row만 사용한다
3. `available_at <= as_of_date` 기준으로 snapshot을 선택한다
4. symbol / statement_type / concept / unit 기준 latest available row를 선택한다

---

## 7. strict loader가 1차에 보장하지 않는 것

아래 항목은 이번 범위에 포함하지 않는다.

1. 전체 유니버스에 대한 충분한 backfill 보장
2. 모든 issuer에 대한 완전한 장기 역사 coverage 보장
3. labels 테이블을 통한 semantic merge 보장
4. statement row를 factor-ready wide table로 즉시 변환하는 것
5. full portfolio-scale batch optimization

즉, Phase 3 strict loader는
"정확성을 우선한 첫 실행 경로"를 확보하는 것이 목적이다.

---

## 8. broad loader와의 차이

strict loader:
- snapshot 우선
- availability 필터 필수
- accession-bearing row만 허용
- 백테스트 입력용

broad loader:
- 연구/탐색 목적
- 필요 시 wider read 허용
- coverage 우선
- strict PIT를 보장하지 않음

따라서 같은 statement 계열이라도:
- `load_statement_values(...)`
  - broad research loader
- `load_statement_snapshot_strict(...)`
  - strict PIT snapshot loader

로 역할을 분리한다.

---

## 9. 초기 구현 입력 범위

Phase 3 첫 strict statement loader는
아래 입력 조합을 우선 지원하는 것이 적절하다.

- `symbols`
- `as_of_date`
- `freq`
- `statement_type`
- optional `concepts`

우선 제외:
- universe_source 기반 대규모 batch snapshot
- portfolio-wide pivot output

즉 1차는
"특정 symbol 집합에 대한 strict snapshot"
을 먼저 안정적으로 지원한다.

---

## 10. 구현 기준 요약

Phase 3 strict statement loader의 구현 기준:

1. 함수 이름은 `load_statement_snapshot_strict(...)`
2. source는 `nyse_financial_statement_values`
3. strict filter는 항상 강제
4. snapshot selection은 `available_at` 기준
5. labels는 보조 정보일 뿐 strict source가 아님
6. 1차는 symbol-based snapshot path를 먼저 구현

---

## 결론

Phase 3에서 구현할 strict statement loader는
coverage보다 point-in-time 안전성을 우선하는
보수적 snapshot loader로 정의한다.

즉 이 loader는
상세 재무제표를 넓게 탐색하는 용도가 아니라,
향후 DB-backed backtest runtime에서
미래 정보 유입을 줄인 snapshot source로 쓰기 위한 첫 구현이다.
