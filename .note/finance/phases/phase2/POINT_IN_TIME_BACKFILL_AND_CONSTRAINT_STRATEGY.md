# Point-In-Time Backfill And Constraint Strategy

## 목적
이 문서는 `nyse_financial_statement_values`가 legacy rows와 new raw rows가 섞인 mixed-state인 상황에서,
어떻게 backfill과 stricter DB constraint로 넘어갈지 단계적으로 정리한다.

전제:
- new raw path는 `accession_no`, `unit`, `available_at`를 갖는 방향으로 안정화 중
- 기존 legacy rows 대부분은 이 필드들이 비어 있음
- 따라서 즉시 전 테이블에 `NOT NULL` / stricter unique rule을 강제하는 것은 위험하다

---

## 1. 현재 상태

2026-03-18 기준 확인 결과:
- `nyse_financial_statement_values` 총 303,054 rows
- `accession_no` 누락 302,712 rows
- `unit` 누락 302,712 rows
- accession-bearing new raw rows는 342 rows, 2개 심볼 수준

즉 현재 테이블은:
- legacy inferred rows
- new raw EDGAR rows

가 함께 존재하는 mixed-state다.

---

## 2. 기본 전략

핵심 원칙은 다음 3개다.

1. new raw path 품질을 먼저 고정한다
2. legacy rows는 strict PIT source로 즉시 간주하지 않는다
3. DB-level strict constraint는 backfill coverage가 충분해진 뒤 적용한다

즉 순서는:
- guard
- backfill
- loader filtering
- strict constraint

이다.

---

## 3. 단계별 권장 순서

## Step 1. new raw path guard 유지

현재 상태:
- `_available_at_from_dates(...)` 보수화 완료
- `accession_no` / `unit` 없는 raw value row skip 완료

목표:
- 앞으로 새로 적재되는 row는 strict identity 후보로 누적되게 만든다

---

## Step 2. legacy rows를 strict PIT 대상에서 분리

권장 규칙:
- loader 또는 downstream query가 strict PIT snapshot을 만들 때는
  아래 조건을 우선 사용한다

예시 필터:
- `accession_no IS NOT NULL`
- `accession_no <> ''`
- `unit IS NOT NULL`
- `unit <> ''`
- `available_at IS NOT NULL`

의미:
- mixed-state 전체 테이블 중에서
  new raw path row만 strict PIT 후보로 사용

장점:
- backfill 전에도 부분적으로 strict PIT snapshot 실험 가능

단점:
- coverage가 아직 낮다
- 전체 universe 전략에는 부족할 수 있다

---

## Step 3. backfill 운영 범위 결정

권장 순서:

1. 우선 research universe부터 backfill
   - 예: 핵심 대형주 / 실제 전략 유니버스

2. 그 다음 profile-filtered stocks

3. 마지막으로 broader universe

이유:
- 전체 유니버스 재적재는 시간이 크다
- strict PIT 연구가 필요한 핵심 종목부터 coverage를 늘리는 편이 낫다

---

## Step 4. backfill 방식

가능한 방식은 두 가지다.

### 옵션 A. in-place upsert backfill
- 기존 테이블에 새 raw path로 다시 적재
- 동일 row는 upsert
- new raw identity row는 accession 기준으로 누적

장점:
- 구현 단순
- 현재 코드 재사용 가능

단점:
- legacy rows가 그대로 남아 mixed-state가 지속됨

### 옵션 B. clean rebuild table
- 새 strict table 또는 truncate/rebuild 방식으로 다시 적재

장점:
- schema purity가 높다
- strict PIT source로 명확하다

단점:
- 운영 비용이 크다
- 다운타임/전환 계획이 필요하다

현재 프로젝트 기준 추천:
- 단기: 옵션 A
- 중기: strict용 clean rebuild 또는 shadow table 검토

---

## Step 5. DB-level strict constraint 적용 시점

아래 중 하나가 만족될 때 적용 검토:

1. 전략 유니버스 대부분이 new raw path로 backfill 완료
2. strict PIT용 별도 테이블/뷰를 도입
3. legacy rows를 분리/폐기할 운영 계획 확정

그 전에는:
- ingestion guard
- loader filtering
- selective backfill

조합으로 운영하는 것이 안전하다

---

## 4. 추천 실무안

현재 프로젝트에 가장 맞는 현실적 순서:

1. new raw path guard 유지
2. loader 설계 시 strict PIT 모드에서는 accession-bearing rows만 사용
3. research universe부터 backfill
4. coverage가 충분해지면 strict table 또는 stricter schema 전환 검토

즉 지금 당장 해야 할 일은:
- 전 테이블 강제 migration이 아니라
- strict loader가 mixed-state를 구분해서 읽도록 설계하는 것

---

## 5. 다음 구현 연결

이 전략 다음의 자연스러운 작업:

1. labels 역할 경계 문서화
2. strict PIT loader query 조건 초안 작성
3. backfill 대상 universe 우선순위 정하기
4. 필요 시 backfill 실행 wrapper 설계

