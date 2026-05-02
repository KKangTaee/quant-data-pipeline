# Point-In-Time Schema Review And Patch Plan

## 목적
이 문서는 2026-03-18 기준으로 반영된
EDGAR 상세 재무제표 point-in-time 관련 코드 변경을 검토한 뒤,
바로 이어서 수정해야 할 항목을 우선순위와 패치 순서 기준으로 정리한다.

검토 대상:
- `finance/data/financial_statements.py`
- `finance/data/db/schema.py`
- 관련 문서/노트

---

## 결론 요약

현재 변경은 방향이 맞다.

특히 좋아진 점:
- `nyse_financial_statement_filings`를 추가해 filing-level 메타를 별도 저장
- `nyse_financial_statement_values`에
  - `period_end`
  - `filing_date`
  - `accepted_at`
  - `available_at`
  - `accession_no`
  를 보존
- wide statement DataFrame 기반의 추정형 적재에서
  raw EDGAR fact + filing metadata 기반 적재로 이동

하지만 아직 strict point-in-time이라고 보기에는 이르다.

즉시 봐야 할 핵심 위험은 3개다.

1. `available_at` fallback이 너무 이르다
2. values unique key가 nullable 컬럼을 포함한다
3. labels 요약 테이블이 concept-level 구분을 잃을 수 있다

---

## 1. 우선순위별 리뷰 결과

## 1-1. P1 - `available_at` fallback 보수성 부족

대상:
- `finance/data/financial_statements.py`
- `_available_at_from_dates(...)`

현재 동작:
- `accepted_at`이 있으면 그것을 사용
- 없으면 `filing_date 00:00:00`을 사용

문제:
- filing이 실제로 장 마감 후 제출되었거나
- filing_date만 있고 acceptance time이 없는 경우에도
- 그날 자정부터 사용 가능했던 것처럼 저장된다

이건 snapshot loader가 `available_at <= as_of_date`를 그대로 쓰기 시작할 때
하루 단위 미래 정보 오염을 만들 수 있다.

예시:
- `filing_date = 2025-10-31`
- 실제 acceptance는 장 마감 이후였을 수 있음
- 그런데 DB에는 `2025-10-31 00:00:00`으로 저장되면
- 2025-10-31 장중 전략에도 이미 사용 가능했던 것처럼 보일 수 있다

판단:
- strict PIT 기준에서는 위험
- 가장 먼저 손봐야 한다

권장 수정:
- `accepted_at`이 있으면 그대로 사용
- `accepted_at`이 없고 `filing_date`만 있으면 보수적 fallback 사용

추천 fallback 후보:
1. `filing_date 23:59:59`
2. 다음 거래일 00:00:00

현재 프로젝트 기준 추천:
- 우선 1차는 `filing_date 23:59:59`
- 이후 거래일 캘린더를 붙일 수 있으면 다음 거래일 기준으로 강화

이유:
- 구현이 단순하다
- `filing_date 00:00:00`보다 명백히 보수적이다
- strict trade calendar 도입 전 임시 규칙으로 충분히 의미가 있다

---

## 1-2. P1 - values unique key가 nullable 컬럼을 포함

대상:
- `finance/data/db/schema.py`
- `nyse_financial_statement_values.uk_fin`

현재 key:
- `(symbol, freq, accession_no, statement_type, concept, period_end, unit)`

문제:
- `accession_no`가 `NULL`일 수 있음
- `unit`도 `NULL`일 수 있음
- MySQL unique index는 `NULL` 값을 동일 row로 강하게 막지 못할 수 있다

즉:
- 동일 row를 다시 적재해도
- key 일부가 `NULL`이면 duplicate insert가 날 가능성이 있다

point-in-time raw ledger에서는
idempotent write가 매우 중요하므로 이건 단순 품질 문제가 아니라
운영 안정성과 데이터 정합성 문제다.

판단:
- `available_at` fallback과 같은 우선순위로 즉시 수정해야 한다

권장 수정 방향:

### 옵션 A. key 컬럼을 `NOT NULL`로 강제
- `accession_no`는 없는 row를 적재하지 않음
- `unit`은 없으면 `'UNKNOWN'` 같은 정규화 문자열 사용

장점:
- DB uniqueness가 명확해짐
- loader 설계가 단순해짐

단점:
- provider 결측 row를 일부 버릴 수 있음

### 옵션 B. 수집 단계에서 stable fallback key 생성
- `accession_no`가 없으면 concept/period/report/form 기반 synthetic key 생성
- `unit`이 없으면 normalized sentinel 문자열로 대체

장점:
- row 보존율이 높다

단점:
- synthetic key 설계가 섬세해야 한다
- 실제 provider identity와 혼동될 수 있다

현재 프로젝트 기준 추천:
- `accession_no`가 없으면 row skip 여부를 먼저 실제 샘플로 확인
- 대부분 accession이 존재한다면 `accession_no NOT NULL` 쪽이 더 좋다
- `unit`은 `NULL` 대신 sentinel 정규화가 현실적이다

즉 1차 추천안:
1. `accession_no` completeness 확인
2. 실사용상 거의 항상 존재하면 `NOT NULL` 전환
3. `unit`은 정규화된 문자열로 강제

---

## 1-3. P2 - labels 요약 테이블의 semantic collision 가능성

대상:
- `finance/data/financial_statements.py`
- `_iter_label_rows_from_values(...)`
- `finance/data/db/schema.py`
- `nyse_financial_statement_labels`

현재 구조:
- dedupe key: `(symbol, label, as_of)`
- PK도 `(symbol, label, as_of)`

문제:
- 같은 label이 다른 concept에 매핑될 수 있다
- 같은 label이 statement_type마다 다르게 쓰일 수 있다
- 현재는 최신 row 한 개가 이전 의미를 덮어쓴다

예:
- 동일 `label`
- 다른 `concept`
- 다른 filing / 다른 statement context

raw values는 살아 있어도
labels를 기준 dictionary처럼 쓰면 잘못된 해석이 붙을 수 있다.

판단:
- raw ledger 자체를 깨는 P1 문제는 아님
- 그러나 loader/semantic mapping에 labels를 재사용할 계획이면 미리 역할을 고정해야 한다

가능한 방향:

### 옵션 A. labels를 사람용 요약 테이블로만 유지
- 지금 구조 유지 가능
- 문서에 “semantic source of truth 아님” 명시

### 옵션 B. labels도 concept-level로 강화
- PK 또는 dedupe key에 `statement_type`, `concept` 추가

장점:
- semantic ambiguity 감소

단점:
- 현재 UI/운영자가 보는 label summary가 더 복잡해짐

현재 프로젝트 기준 추천:
- 당장은 옵션 A
- 즉, labels는 operator-facing summary로만 규정
- 실제 loader는 values 중심으로 설계

---

## 2. 권장 수정 순서

### Step 1. `available_at` fallback 수정

목표:
- accepted time이 없는 filing도 지나치게 이른 시점으로 열리지 않게 만든다

권장 패치:
- `_available_at_from_dates(...)`에서
  - `accepted_at` 우선 유지
  - `filing_date` fallback을 `00:00:00`에서 보수적 시점으로 변경

검증:
- 기존 row와 새 row를 샘플 비교
- 같은 filing_date를 가진 row의 `available_at`이 더 늦어졌는지 확인

### Step 2. values key completeness 점검

목표:
- 중복 삽입 가능성을 실제 데이터로 먼저 확인

필요 점검:
- `accession_no IS NULL` row 수
- `unit IS NULL` row 수
- 동일 key 후보 중복 row 존재 여부

검증 SQL 예시:
- `accession_no` null count
- `unit` null count
- nullable key 포함 duplicate 패턴 탐색

2026-03-18 점검 결과:
- `nyse_financial_statement_values` 전체 303,054 rows
- `accession_no` 누락 302,712 rows
- `unit` 누락 302,712 rows
- `accession_no`가 채워진 row는 342건, 2개 심볼에 한정

해석:
- 현재 테이블은 legacy rows와 새 raw-path rows가 섞인 mixed-state다
- 따라서 지금 바로 전 테이블에 `NOT NULL` 제약을 강제하면 기존 데이터와 충돌할 가능성이 높다
- 다음 패치는
  - 새 raw rows에 대한 strict identity 강제
  - 기존 legacy rows의 backfill 또는 rebuild 전략
  를 분리해서 설계해야 한다

### Step 3. key 수정 및 migration 방향 확정

목표:
- values table을 idempotent raw ledger로 안정화

후보:
- `accession_no NOT NULL`
- `unit` sentinel 정규화
- 필요 시 unique key 재생성

현재 추천:
1. 새 raw path는 `accession_no` 없는 row를 기본적으로 strict-PIT 대상에서 제외
2. `unit`은 수집 시점 정규화 sentinel 적용 검토
3. legacy rows는 즉시 strict-PIT row로 취급하지 않고, 재수집/backfill 계획을 별도로 둔다

### Step 4. labels 역할 고정

목표:
- labels를 summary table로만 둘지 semantic dictionary로도 쓸지 확정

현재 추천:
- summary table로 고정
- loader는 values 기반

---

## 3. 구현 방식별 장단점

## 3-1. `available_at` fallback

### `filing_date 23:59:59`
- 장점:
  - 간단
  - 현재 구조에서 바로 적용 가능
- 단점:
  - 실제 acceptance가 장 시작 전인 경우도 지나치게 늦춤

### 다음 거래일 기준
- 장점:
  - 더 보수적
  - 백테스트 안전성은 더 높음
- 단점:
  - 거래일 캘린더/휴장일 처리가 필요

현재 추천:
- 먼저 `23:59:59`
- 나중에 거래일 캘린더 결합

## 3-2. unique key 안정화

### strict raw identity
- accession 기반 row만 허용
- provider truth 중심

장점:
- PIT 원장으로 가장 깔끔

단점:
- 일부 provider edge row를 버릴 수 있음

### synthetic fallback identity
- row 보존율은 높음

장점:
- 누락 데이터 흡수 가능

단점:
- 나중에 loader가 provider truth와 synthetic identity를 구분해야 함

현재 추천:
- raw ledger는 provider truth 우선
- synthetic fallback은 정말 accession 누락이 의미 있게 많을 때만 검토

---

## 4. 다음 실제 코드 작업 제안

다음 코드 수정 묶음은 아래처럼 가는 것이 좋다.

1. `financial_statements.py`
   - `_available_at_from_dates(...)` 보수화

2. DB 데이터 점검
   - `accession_no`, `unit` 결측/중복 조사

3. `schema.py` + ingestion
   - values key 안정화

4. 문서 업데이트
   - strict PIT 아님 / fallback 규칙 명시

---

## 5. 현재 결론

- 이번 변경은 상세 재무제표를 point-in-time 가능한 raw ledger로 끌어올리는 방향으로는 옳다
- 하지만 strict point-in-time이라고 부르기 전에
  - `available_at` fallback
  - nullable unique key
  두 항목은 먼저 정리해야 한다
- labels 테이블은 당분간 summary 용도로 제한하는 것이 안전하다
