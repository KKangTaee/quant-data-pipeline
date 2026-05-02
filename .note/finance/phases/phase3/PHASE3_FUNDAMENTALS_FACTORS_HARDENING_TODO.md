# Phase 3 Fundamentals / Factors Hardening TODO

## 목적
이 문서는 `nyse_fundamentals`, `nyse_factors` 테이블과
해당 수집/계산 파이프라인을 재점검하고 보강하기 위한 실행 보드다.

핵심 목표:
- 요약 재무 / 파생 팩터 테이블의 역할을 분명히 한다
- 백테스트용으로 더 유효한 필드와 메타를 확보한다
- raw ledger와 summary/derived layer의 경계를 명확히 한다

---

## 현재 판단

현재 기준 판단:

- `nyse_fundamentals`
  - 제거 대상이 아니라 유지 대상
  - 다만 raw truth가 아니라 **broad coverage summary layer**로 재정의가 필요
- `nyse_factors`
  - 제거 대상이 아니라 유지 대상
  - 다만 strict PIT factor store가 아니라 **broad research derived layer**로 정의해야 함
- strict point-in-time 원장은
  - `nyse_financial_statement_filings`
  - `nyse_financial_statement_values`
  - `nyse_financial_statement_labels`
  가 담당

즉 방향은:

```text
raw ledger:
  filings / values / labels

summary layer:
  nyse_fundamentals

derived factor layer:
  nyse_factors
```

---

## 큰 TODO 보드

### A. Current-State Review
상태:
- `completed`

세부 작업:
- `[completed]` 현재 fundamentals/factors schema 점검
  - `schema.py` 기준 컬럼과 uniqueness 확인
- `[completed]` 수집/계산 코드 점검
  - `fundamentals.py`, `factors.py` 로직과 fallback 확인
- `[completed]` DB 실제 분포 점검
  - row 수, coverage, null 분포, sample row 확인

핵심 관찰:
- `nyse_fundamentals` / `nyse_factors`는 둘 다 broad coverage는 좋지만 timing 의미가 약함
- 일부 blank/weak summary row가 들어갈 수 있음
- 현재 factor set은 price-only 전략 이후의 factor 전략을 위해서는 아직 얇은 편
- detailed statement raw ledger는 현재 coverage가 2개 symbol 수준이라 전체 대체는 아직 불가

---

### B. Role and Direction Fix
상태:
- `completed`

세부 작업:
- `[completed]` 두 테이블의 역할을 raw ledger와 분리해서 명시
  - summary / derived research layer로 방향 고정
- `[completed]` 필요한 메타 컬럼 방향 확정
  - source mode / timing basis / derivation source / price attachment metadata
- `[completed]` 장기 방향 문서화
  - 향후 statement-led normalized summary로 이행 가능성 명시

완료 기준:
- `nyse_fundamentals`, `nyse_factors`가 “무엇을 저장하는지 / 무엇을 저장하지 않는지”가 분명해야 함

---

### C. Fundamentals Schema / Ingestion Hardening
상태:
- `completed`

세부 작업:
- `[completed]` blank summary row 제거
  - 모든 핵심 재무값이 비어 있는 row는 적재하지 않음
- `[completed]` 핵심 회계 필드 보강
  - factor 계산에 필요한 base field 추가 여부 확정
- `[completed]` fallback source 추적 메타 보강
  - direct / derived / inferred source 구분 가능하게 정리
- `[completed]` timing/source 메타 추가
  - broad coverage / period-end summary 성격을 테이블에 반영

완료 기준:
- `nyse_fundamentals`가 더 풍부한 summary layer가 되고,
  downstream factor 계산의 입력으로 의미가 더 분명해야 함

---

### D. Factors Schema / Calculation Hardening
상태:
- `completed`

세부 작업:
- `[completed]` price attachment metadata 추가
  - price date / match gap / timing basis 정리
- `[completed]` factor set 확장
  - valuation / quality / safety / growth 관점에서 핵심 팩터 추가
- `[completed]` existing factor formula 재검토
  - 현재 계산식과 분모/부호/결측 처리 재검토
- `[completed]` broad research mode 명시
  - strict PIT factor가 아님을 코드/테이블 의미에 반영

완료 기준:
- `nyse_factors`가 향후 factor 전략 실험에 쓸 수 있는 수준의 폭과 메타를 가져야 함

---

### E. Validation / Backfill Guidance
상태:
- `completed`

세부 작업:
- `[completed]` 샘플 심볼 재수집 및 재계산 검증
  - annual / quarterly 샘플 확인
- `[completed]` null 분포와 새 컬럼 채움 상태 확인
  - 기존 대비 개선 확인
- `[completed]` full-universe backfill 지침 정리
  - 지금 즉시 전체 재수집이 필요한지, 후속 운영 작업으로 둘지 정리
- `[completed]` full-universe 재수집 / 재계산 실행 여부 결정
  - 현재는 즉시 full backfill을 하지 않고, 후속 운영 작업으로 defer

완료 기준:
- 코드 수정 후 sample validation이 끝나고,
  운영상 어떤 backfill이 필요한지 문서로 남아 있어야 함

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `없음`
