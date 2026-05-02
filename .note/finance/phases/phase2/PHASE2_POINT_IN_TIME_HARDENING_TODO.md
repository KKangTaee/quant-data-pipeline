# Phase 2 Point-In-Time Hardening TODO

## 목적
이 문서는 PHASE2의 다음 챕터로,
상세 재무제표 point-in-time 후속 패치를 실제 코드 수준에서 진행하기 위한 작업 보드다.

이번 챕터의 목표:

1. detailed financial statement raw ledger를 strict PIT에 더 가깝게 보강
2. values 테이블의 row identity를 더 안정적으로 만든다
3. labels / values / loader의 역할 경계를 명확히 한다

상위 참고 문서:
- `.note/finance/phases/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`
- `.note/finance/phases/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`
- `.note/finance/phases/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`

---

## 큰 TODO 보드

### A. `available_at` fallback 보수화
상태:
- `completed`

세부 작업:
- `[completed]` fallback 정책 확정
  - acceptance time이 없을 때 `filing_date 00:00:00` 대신 보수적 시점을 쓰도록 기준 확정
- `[completed]` `_available_at_from_dates(...)` 수정
  - filing date만 있을 때 더 늦은 시점으로 저장되도록 실제 코드 반영
- `[completed]` 로컬 검증
  - 샘플 입력 기준으로 새 fallback 값이 기대대로 나오는지 확인
- `[completed]` 관련 문서/로그 반영
  - 어떤 fallback 규칙을 채택했는지 durable note에 남김

완료 기준:
- acceptance time이 없는 filing이 더 이상 당일 자정부터 사용 가능했던 것처럼 저장되지 않아야 함

---

### B. values row identity 안정화
상태:
- `completed`

세부 작업:
- `[completed]` `accession_no` / `unit` 결측 현황 점검
  - 실제 DB에서 nullable key 컬럼이 얼마나 비어 있는지 파악
- `[completed]` raw identity 정책 확정
  - accession 기반 strict identity로 갈지, fallback key를 둘지 결정
- `[completed]` ingestion-side identity guard 패치
  - 새 raw path에서 `accession_no` / `unit` 없는 row를 PIT ledger에 넣지 않도록 보호
- `[completed]` 중복/재적재 검증
  - 같은 입력을 다시 적재해도 중복 row가 생기지 않는지 확인
- `[completed]` legacy row backfill / DB-level strict constraint 전략 확정
  - 기존 mixed-state rows를 어떻게 재수집/정리한 뒤 stricter schema로 갈지 결정

완료 기준:
- `nyse_financial_statement_values`가 재적재에도 안정적인 raw ledger로 동작해야 함

현재 결론 메모:
- legacy mixed-state 문제를 확인한 뒤, local DB에서는 labels/values 테이블을 드롭 후 strict schema로 재생성함
- 현재 로컬 DB 기준으로는 legacy rows를 제거한 새 schema 상태에서 다시 시작한 상태
- 대표 raw source 샘플(`AAPL`, `MSFT`, `JPM`)에서는 statement facts의 `accession` / `unit` 누락이 0건으로 확인됨
- 따라서 ingestion guard와 stricter DB constraint를 함께 유지해도 되는 상태가 됨
- strict PIT loader는 당분간 accession-bearing rows만 사용하는 방향으로 설계하는 것이 권장됨

---

### C. labels 역할 경계 확정
상태:
- `completed`

세부 작업:
- `[completed]` labels 테이블을 summary layer로 명시
  - labels는 operator-facing 요약 계층이라는 점 문서화
- `[completed]` loader가 values 중심으로 동작하도록 기준 정리
  - future loader가 labels를 semantic source of truth로 쓰지 않도록 기준 고정
- `[completed]` labels key 확장 적용
  - label 중심 PK를 concept 중심 summary PK로 재정의
- `[completed]` strict PIT loader query 조건 초안 작성
  - `available_at`, `accession_no`, `unit` 기준으로 strict snapshot query 패턴을 정리
- `[completed]` 로컬 DB 재생성 및 샘플 재적재 확인
  - labels/values 테이블을 strict schema로 재생성하고 `AAPL`, `MSFT` 연간 샘플 적재 성공 확인

완료 기준:
- labels / values / loader 역할이 헷갈리지 않게 문서화되어 있어야 함

---

## 현재 추천 다음 작업 순서

1. research-universe backfill 범위 확정
2. strict PIT loader 구현 범위 확정
3. broad vs strict loader naming 규칙 확정
4. 필요 시 loader 실제 구현 시작

---

## 현재 작업 중 항목

현재 `in_progress`:
- 없음

바로 다음 체크 대상:
- research-universe backfill 범위 확정

---

## 현재 진척도

- 이번 챕터:
  - 약 `100%`

판단 근거:
- patch plan과 우선순위는 정리 완료
- 첫 번째 즉시 수정 항목은 구현과 검증까지 완료
- values table mixed-state 현황과 raw identity 정책도 정리 완료
- 새 raw path에 대한 identity guard와 재적재 검증까지 완료
- labels/values의 local strict-schema 재생성과 샘플 재적재까지 완료
- future strict loader 기준 문서도 초안 수준까지 정리 완료
