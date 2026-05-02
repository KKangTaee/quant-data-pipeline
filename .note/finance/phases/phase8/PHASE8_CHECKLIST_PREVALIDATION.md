# Phase 8 Checklist Prevalidation

## 목적

- 사용자가 Phase 7과 함께 나중에 batch review를 할 수 있도록,
  assistant가 Phase 8 checklist를 먼저 자동 점검한 결과를 남긴다.

## 실행 일시

- `2026-03-28`

## 요약

- checklist 기준 자동 점검 가능한 항목은 모두 통과했다.
- Streamlit bare-mode 경고는 있었지만,
  history prefill helper까지 포함한 핵심 로직은 실제로 동작했다.
- 아직 남아 있는 것은 브라우저에서 직접 보는 최종 manual UX 확인뿐이다.

## 항목별 결과

### 1. Single Strategy - Quarterly Value

- 결과:
  - `PASS`
- 확인 내용:
  - form source에 `Price Freshness Preflight` 연결 확인
  - form source에 `Statement Shadow Coverage Preview` 연결 확인
  - runtime 실행 성공
  - selection history build 성공
- preset test:
  - `US Statement Coverage 100`
  - `End Balance = 140,853.2`
  - `selection_rows = 123`

### 2. Single Strategy - Quarterly Quality + Value

- 결과:
  - `PASS`
- 확인 내용:
  - form source에 `Price Freshness Preflight` 연결 확인
  - form source에 `Statement Shadow Coverage Preview` 연결 확인
  - runtime 실행 성공
  - selection history build 성공
  - meta에 `quality_factors`, `value_factors` 모두 남음
- preset test:
  - `US Statement Coverage 100`
  - `End Balance = 187,769.4`
  - `selection_rows = 123`

### 3. Single Strategy - Manual Small Universe

- 결과:
  - `PASS`
- test universe:
  - `AAPL,MSFT,GOOG`
- 결과:
  - quality quarterly:
    - `first_active = 2016-01-29`
  - value quarterly:
    - `first_active = 2017-05-31`
  - quality+value quarterly:
    - `first_active = 2017-05-31`
- 해석:
  - early period가 완전히 영구 flat 상태는 아니다
  - value / quality+value quarterly는 small manual universe에서 늦게 시작하며,
    warning도 그 내용을 설명한다

### 4. Compare - Quarterly Family Exposure

- 결과:
  - `PASS`
- 확인 내용:
  - quarterly family 3종이 compare option에 포함됨
  - 각 전략 expander block source 존재 확인

### 5. Compare Execution

- 결과:
  - `PASS`
- 확인 내용:
  - quarterly value compare runner 성공
  - quarterly quality+value compare runner 성공
  - selection history build 성공
- sample compare outputs:
  - quarterly value compare:
    - `End Balance = 526,109.0`
  - quarterly quality+value compare:
    - `End Balance = 187,769.4`

### 6. History / Prefill

- 결과:
  - `PASS`
- 확인 내용:
  - temp history file 기준 append / load 성공
  - stored record에서 history payload rebuild 성공
  - `Load Into Form` helper도 bare-mode 기준 `True` 반환

### 7. Meta / Context

- 결과:
  - `PASS`
- 확인 내용:
  - quarterly meta keys 확인:
    - `factor_freq = quarterly`
    - `snapshot_mode = strict_statement_quarterly`
    - `snapshot_source = shadow_factors`
  - overlay meta keys 확인:
    - `trend_filter_enabled`
    - `trend_filter_window`
    - `market_regime_enabled`
    - `market_regime_window`
    - `market_regime_benchmark`

### 8. Expected Semantics

- 결과:
  - `PASS`
- 확인 내용:
  - default preset:
    - `US Statement Coverage 100`
  - warnings:
    - `Research-only quarterly value prototype ...`
    - `Research-only quarterly multi-factor prototype ...`
  - 즉 quarterly family가 현재도 `research-only`로 읽히는 semantics 유지

## 주의

- 이번 점검은 주로 runtime / helper / source wiring 기준 자동 점검이다.
- 실제 브라우저에서
  - 화면 배치
  - 탭 전환 UX
  - expander readability
  - caption readability
  는 사용자가 나중에 manual checklist로 확인하는 것이 최종 기준이다.
