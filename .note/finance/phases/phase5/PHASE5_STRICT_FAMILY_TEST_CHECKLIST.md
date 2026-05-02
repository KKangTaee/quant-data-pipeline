# Phase 5 Strict Family Test Checklist

## 목적

- Phase 5에서 추가된 strict family UI / runtime / interpretation / overlay 기능을
  사용자가 순서대로 점검할 수 있게 정리한다.

대상 전략:
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

---

## 1. Single Strategy Smoke Test

### 1-1. Quality Strict

- 위치:
  - `Backtest -> Single Strategy -> Quality Snapshot (Strict Annual)`
- 설정:
  - `Preset = US Statement Coverage 100`
- 확인 항목:
  - 실행이 성공한다
  - `Price Freshness Preflight`가 보인다
  - `Selection History` 탭이 보인다
  - `Selection History -> Interpretation` 탭이 보인다
  - `Interpretation Summary`가 보인다
  - `Overlay Rejection Frequency`가 비어 있지 않거나, 비어 있을 경우 적절한 안내 문구가 보인다

### 1-2. Value Strict

- 위치:
  - `Backtest -> Single Strategy -> Value Snapshot (Strict Annual)`
- 설정:
  - `Preset = US Statement Coverage 1000`
- 확인 항목:
  - 실행이 성공한다
  - 더 이상 selection-history 렌더링 에러가 없다
  - `Selection History -> History / Interpretation / Selection Frequency` 3개 탭이 모두 보인다
  - `Cash Share`가 자연스럽게 보인다

### 1-3. Quality + Value Strict

- 위치:
  - `Backtest -> Single Strategy -> Quality + Value Snapshot (Strict Annual)`
- 설정:
  - `Preset = US Statement Coverage 300`
- 확인 항목:
  - 실행이 성공한다
  - quality / value factor가 둘 다 반영된다
  - `Selection History -> Interpretation` 탭이 정상 동작한다

---

## 2. Overlay On/Off Test

### 2-1. Quality Strict Overlay

- 전략:
  - `Quality Snapshot (Strict Annual)`
- 실행:
  - overlay `off` 1회
  - overlay `on`, `window = 200` 1회
- 확인 항목:
  - 두 실행 모두 성공한다
  - 결과 비교가 가능하다:
    - `End Balance`
    - `CAGR`
    - `Sharpe`
    - `Maximum Drawdown`
  - `Selection History`에서 아래 흐름이 읽힌다:
    - `Raw Selected Tickers`
    - `Overlay Rejected Tickers`
    - `Selected Tickers`

### 2-2. Value Strict Overlay

- 전략:
  - `Value Snapshot (Strict Annual)`
- 실행:
  - overlay `off` 1회
  - overlay `on`, `window = 200` 1회
- 확인 항목:
  - `Interpretation Summary`에서 아래 값이 자연스럽다:
    - `Overlay Rejections`
    - `Cash-Only Rebalances`
    - `Avg Cash Share`

### 2-3. Quality + Value Strict Overlay

- 전략:
  - `Quality + Value Snapshot (Strict Annual)`
- 실행:
  - overlay `off` 1회
  - overlay `on`, `window = 200` 1회
- 확인 항목:
  - mixed strategy에서도 same UI가 자연스럽게 보인다
  - `Selection History`와 `Interpretation`이 정상 동작한다

---

## 3. Preflight / Freshness Test

- strict 전략 아무거나 선택
- 실행 전 확인:
  - `Price Freshness Preflight`가 보인다

### 3-1. Preflight Details

- `Preflight Details`를 연다
- 확인 항목:
  - `Heuristic Reason Summary`가 보인다
  - `Stale / Missing Classification`이 보인다

### 3-2. Freshness UX

- stale가 없을 때:
  - 과한 경고 없이 깔끔하게 보인다
- stale가 있을 때:
  - 원인 라벨이 보인다
  - 설명이 현재 동작과 크게 어긋나지 않는다

---

## 4. Compare Test

- 위치:
  - `Backtest -> Compare & Portfolio Builder`
- 선택 전략:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`

### 4-1. Advanced Inputs

- 확인 항목:
  - 각 전략별 preset 입력이 따로 보인다
  - 각 전략별 factor set 수정이 가능하다
  - 각 전략별 overlay on/off 수정이 가능하다
  - 각 전략별 trend-filter window 수정이 가능하다

### 4-2. Compare Execution

- 실행 후 확인 항목:
  - compare 결과가 정상 표시된다
  - `Focused Strategy` drilldown이 정상 동작한다
  - 전략별 설정 차이가 실제 결과에 반영된다

---

## 5. History Test

- 위치:
  - `Backtest -> History`

### 5-1. Shared History Surface

- 확인 항목:
  - `Persistent Backtest History`가 보인다
  - `History Drilldown`이 보인다

### 5-2. Save / Load / Rerun

- single run 하나 실행 후 확인:
  - history에 저장된다
- compare run 하나 실행 후 확인:
  - history에 저장된다
- history에서 확인:
  - `Load Into Form`이 동작한다
  - `Run Again`이 동작한다

---

## 6. UI / Copy Test

- strict preset 아래 historical-backtest 설명 캡션이 보인다
- `Price Freshness Preflight` 옆 툴팁이 보인다
- `Trend Filter Overlay` 옆 툴팁이 보인다
- 설명 문구가 현재 실제 동작과 맞는다

---

## 권장 테스트 순서

1. `Quality Snapshot (Strict Annual)` single smoke
2. `Value Snapshot (Strict Annual)` single smoke
3. `Quality + Value Snapshot (Strict Annual)` single smoke
4. overlay on/off 비교
5. preflight / stale classification 확인
6. compare strict-family 확인
7. history 저장 / reload / rerun 확인

---

## 메모

- 현재 strict preset은 `historical backtest` semantics를 따른다.
- 즉 run-level preset universe는 고정이고,
  실제 후보 제외는 각 rebalance date에서
  price / factor availability 기준으로 자연스럽게 발생한다.
- `Price Freshness Preflight`는 경고/진단 레이어이며,
  run-level universe replacement 용도는 아니다.
