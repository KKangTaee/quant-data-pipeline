# Phase 3 Runtime Cleanup Backlog

## 목적
이 문서는 Phase 3 runtime generalization 과정에서 발견됐지만
즉시 처리하지 않고 후속 작업으로 분리한 warning / cleanup / optimization 항목을 모아둔다.

즉:
- 지금 당장 product path를 막지 않는 항목
- 하지만 나중에 다시 봐야 하는 항목

을 한 곳에 모아두는 문서다.

---

## 분류 기준

### 1. resolved during Phase 3
- 한때 경고나 cleanup 후보였지만 이번 Phase에서 이미 해결된 항목

### 2. deferred operational work
- 코드 구조는 정리됐지만, 실제 대규모 운영 실행이 남아 있는 항목

### 3. deferred optimization work
- 기능은 맞지만 성능/운영 효율을 더 끌어올릴 여지가 있는 항목

### 4. deferred architecture work
- 지금 방향은 정리됐지만 다음 Phase에서 더 근본적으로 확장해야 하는 항목

---

## 1. resolved during Phase 3

### A. `SettingWithCopyWarning` in `finance/transform.py`

상태:
- `resolved`

배경:
- `filter_finance_history(...)`에서 grouped result에 바로 값을 넣으면서
  Pandas `SettingWithCopyWarning`이 발생했다

조치:
- grouped slice를 명시적으로 `.copy()`
- dividend sum을 index 기준으로 다시 맞춰 넣도록 수정

현재 판단:
- 더 이상 활성 backlog 항목이 아님

---

### B. DB-backed sample warmup mismatch

상태:
- `resolved`

배경:
- direct path와 DB-backed path의 indicator warmup 순서가 달라
  `portfolio_sample(...)`과 `portfolio_sample_from_db(...)`가 달랐음

조치:
- `history_start` 기반 warmup load 추가
- sample DB path를 direct path와 같은 순서로 정렬

현재 판단:
- 더 이상 활성 backlog 항목이 아님

---

### C. legacy mixed-state OHLCV parity issue

상태:
- `resolved for sample universe`

배경:
- sample 전략 유니버스의 오래된 `nyse_price_history` row가 canonical하지 않아
  direct path와 DB-backed path 결과가 달랐음

조치:
- canonical refresh
- blank row 제거
- inclusive `end` 보정

현재 판단:
- sample universe parity 문제는 해결
- 다만 full-universe 재정비는 별도 운영 항목으로 남음

---

## 2. deferred operational work

### A. full-universe fundamentals/factors backfill

상태:
- `deferred`

배경:
- `nyse_fundamentals`, `nyse_factors`의 의미와 계산식은 새 기준으로 정리됐지만
  전체 universe를 새 기준으로 다시 채우는 작업은 아직 하지 않음

이유:
- yfinance 호출량이 큼
- 운영 시간과 실패 관리가 필요함
- 이번 턴의 목적은 코드/계산 정합성 확보였음

후속 작업:
- full stock universe 기준:
  - `upsert_fundamentals(..., replace_symbol_history=True)`
  - `upsert_factors(..., replace_symbol_history=True)`

---

### B. full-universe OHLCV canonical refresh

상태:
- `deferred`

배경:
- sample 전략 유니버스는 canonical refresh를 통해 parity를 맞췄음
- 하지만 전체 universe의 historical OHLCV를 같은 수준으로 전부 다시 정리한 것은 아님

후속 작업:
- 대규모 universe 기준 canonical refresh 범위와 운영 방식을 따로 정리

---

## 3. deferred optimization work

### A. deeper yfinance large-universe optimization

상태:
- `deferred`

현재 상태:
- 기존보다 속도는 개선됨
  - batch fetch 병렬화
  - sleep 감소
  - retry/backoff

아직 남은 여지:
- 더 큰 유니버스에서 batch sizing 재조정
- symbol partition 전략 세분화
- 캐시/재시도 정책 고도화
- provider fallback 검토

현재 판단:
- 기능 correctness보다 우선순위가 낮아서 후속 최적화 항목으로 둠

---

### B. large-scale operational benchmark

상태:
- `deferred`

배경:
- 현재는 correctness 위주 smoke/sample validation만 완료
- 실제 대규모 운영 시간과 batch별 실패율을 체계적으로 측정하진 않음

후속 작업:
- 운영 benchmark 문서화
- symbol 수 대비 수집 시간 기록

---

## 4. deferred architecture work

### A. strict PIT factor pipeline

상태:
- `deferred`

배경:
- `nyse_factors`는 broad research layer로 정리됨
- strict PIT factor store는 아직 별도 구현 안 됨

후속 방향:
- `nyse_financial_statement_filings`
- `nyse_financial_statement_values`
- `available_at`

기준으로 strict factor build path 설계

---

### B. factor/fundamental runtime connection layer implementation

상태:
- `deferred to next runtime step`

배경:
- 문서상 연결 원칙과 input contract는 정리됨
- 실제 `rebalance-date snapshot connection layer` 구현은 아직 남아 있음

현재 판단:
- 이 항목은 cleanup이라기보다 다음 기능 구현 Phase의 직접 대상

---

### C. Phase 4 UI runtime entrypoint design

상태:
- `deferred to handoff step`

배경:
- validation harness와 runtime contract는 정리 중이지만
  UI가 직접 부를 최소 entrypoint는 아직 고정 전

현재 판단:
- 다음 handoff 작업에서 다루는 것이 맞음

---

## 우선순위 요약

### 높은 우선순위
1. full-universe fundamentals/factors backfill
2. full-universe OHLCV canonical refresh 범위 판단

### 중간 우선순위
3. strict PIT factor pipeline 설계
4. factor/fundamental runtime connection layer 구현

### 낮은 우선순위
5. deeper yfinance optimization
6. large-scale operational benchmark

---

## 결론

Phase 3 현재 기준에서 cleanup backlog의 의미는 분명하다.

- correctness를 막는 핵심 warning은 대부분 정리됨
- 남은 것은 주로:
  - large-scale 운영 재정비
  - deeper optimization
  - 다음 단계 아키텍처 확장

즉 지금 backlog는 “지금 당장 막힌 문제 목록”이 아니라
**다음 단계에서 다시 열어야 할 운영/최적화/아키텍처 후속 목록**이다.
