# Phase 8 Price Stale Diagnosis First Pass

## 목적

`Price Freshness Preflight`가 yellow일 때,

- 이 심볼이 정말 상폐/심볼변경 쪽인지
- provider가 최신 데이터를 안 주는지
- 아니면 DB만 뒤처진 것인지

를 한 번 더 좁혀볼 수 있는 **read-only diagnosis flow**를 추가한다.

핵심 원칙은:

- `stale warning`
- `read-only diagnosis`
- `explicit retry payload`

를 분리하는 것이다.

즉, 원인 파악과 재수집을 한 버튼에 섞지 않고,
먼저 분류를 본 뒤 필요한 경우만 `Daily Market Update`로 이어지게 한다.

---

## 구현 내용

위치:

- `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`

입력:

- `Diagnosis Symbols`
- `Diagnosis End Date`

고정 진단 규칙:

- daily (`1d`) latest-date 기준
- provider probe windows:
  - `5d`
  - `1mo`
  - `3mo`

진단에 사용하는 데이터:

1. DB latest price date
   - `finance_price.nyse_price_history`
2. provider probe
   - `yfinance` read-only 재조회
3. asset profile status
   - `finance_meta.nyse_asset_profile`

---

## 결과 해석

이 카드는 각 심볼에 대해 아래를 합쳐서 보여준다.

- `DB Latest`
- `Provider Latest`
- `Probe Status`
- `Profile Status`
- `Diagnosis`
- `Recommended Action`

first-pass diagnosis labels:

- `up_to_date_in_db`
  - DB가 이미 effective trading end까지 최신
- `local_ingestion_gap`
  - provider는 effective trading end까지 주는데 DB만 뒤처짐
- `local_ingestion_gap_partial`
  - provider는 DB보다 newer row를 주지만 아직 market end까지는 덜 옴
- `provider_source_gap`
  - provider도 DB보다 더 최신 row를 못 줌
- `provider_source_gap_or_symbol_issue`
  - provider probe가 no-data에 가깝고 symbol status도 애매함
- `likely_delisted_or_symbol_changed`
  - asset profile 기준 상폐/심볼 변경 가능성이 높음
- `asset_profile_error`
  - asset profile 상태 자체가 에러
- `rate_limited_during_probe`
  - provider probe가 rate limit에 걸려 확정 보류
- `inconclusive`
  - 근거가 섞여 있어 확정이 어려움

---

## 활용 방법

### 1. backtest에서 yellow preflight 확인

- strict annual / quarterly preflight가 yellow이면
- stale symbol list를 확인한다.

### 2. diagnosis card로 이동

- `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`
- stale symbol을 붙여넣고 실행

### 3. diagnosis 기준으로 액션 선택

- `local_ingestion_gap`
  - `Daily Market Update` 대상
- `provider_source_gap`
  - provider 자체가 최신 row를 안 주는 상태
  - 즉시 재수집보다 retry later / symbol inspection 쪽이 맞음
- `likely_delisted_or_symbol_changed`
  - 상폐/심볼변경 가능성을 먼저 봄
- `asset_profile_error`
  - `Metadata Refresh` 후 재확인
- `rate_limited_during_probe`
  - 진단 자체를 나중에 다시 실행

### 4. explicit retry payload 사용

카드 하단의
`Suggested Daily Market Update Payload`
는 `local_ingestion_gap` 계열 심볼만 대상으로 만든다.

즉,
- provider에 최신 row가 있다는 근거가 있을 때만
- targeted `Daily Market Update` payload를 제안한다.

---

## 왜 이 구조가 좋은가

이전에는 사용자가 yellow preflight를 보고도

- 진짜 상폐인지
- source gap인지
- DB만 덜 들어온 건지

를 구분하기 어려웠다.

이번 first pass는 이를 다음처럼 분리한다.

- preflight:
  - 경고/탐지
- diagnosis:
  - 원인 좁히기
- daily refresh payload:
  - 실제 retry 후보만 제시

즉 operator 입장에서
“무조건 다시 돌린다”가 아니라
“무엇 때문에 stale인지 먼저 보고, 그다음 필요한 것만 refresh한다”
는 구조로 바뀌었다.

---

## 테스트 포인트

1. `Price Stale Diagnosis` 카드가 `Manual Jobs / Inspection`에 보이는지
2. `AAPL` 같은 정상 심볼에서 `up_to_date_in_db`가 나오는지
3. stale 심볼에서
   - `DB Latest`
   - `Provider Latest`
   - `Diagnosis`
   - `Recommended Action`
   가 보이는지
4. provider probe details가 `5d / 1mo / 3mo`별로 보이는지
5. `local_ingestion_gap`이 하나라도 있을 때만
   `Suggested Daily Market Update Payload`가 나오는지

---

## 현재 한계

- first pass는 `yfinance` 재조회 기반이라
  provider 자체가 불안정하면 결과가 `rate_limited_during_probe` 또는 `inconclusive`로 남을 수 있다.
- `provider_source_gap`과 `likely_delisted_or_symbol_changed`는 여전히 heuristic 성격이 있다.
- asset profile refresh는 현재 targeted symbol refresh가 아니라
  broader `Metadata Refresh` 경로와 연결된다.

따라서 이 카드는
**상폐 확정기**가 아니라
**실무형 원인 분리 도우미**로 보는 것이 맞다.
