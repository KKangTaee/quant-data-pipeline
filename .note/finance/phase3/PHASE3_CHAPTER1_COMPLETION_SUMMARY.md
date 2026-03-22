# Phase 3 Chapter 1 Completion Summary

## 목적
이 문서는 Phase 3의 첫 구현 챕터를 마감 정리하기 위한 요약 문서다.

상위 계획 문서:
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`

참조 TODO 보드:
- `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase3/PHASE3_LOADER_IMPLEMENTATION_TODO.md`

---

## 챕터 목표

이번 챕터에서 완료하려고 했던 핵심 목표는 다음과 같았다.

1. loader 구현 범위를 확정한다
2. strict vs broad loader 정책을 고정한다
3. 첫 loader 세트를 실제 코드로 구현한다
4. DB loader를 기존 전략 runtime과 연결한다
5. 최소 1개 전략의 DB 기반 실행 경로를 검증한다

---

## 완료된 결과

### 1. Loader 정책과 범위를 고정했다
- `finance/loaders/*` 패키지 구조를 확정했다
- broad research loader와 strict PIT loader의 차이를 문서와 코드 양쪽에서 고정했다
- loader naming 규칙, helper 범위, 첫 구현 순서를 문서화했다

### 2. 첫 loader 세트를 실제 코드로 구현했다
- `finance/loaders/universe.py`
- `finance/loaders/price.py`
- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `finance/loaders/financial_statements.py`
- `finance/loaders/runtime_adapter.py`

구현된 대표 공개 함수:
- `load_universe(...)`
- `load_price_history(...)`
- `load_price_matrix(...)`
- `load_fundamentals(...)`
- `load_fundamental_snapshot(...)`
- `load_factors(...)`
- `load_factor_snapshot(...)`
- `load_factor_matrix(...)`
- `load_statement_values(...)`
- `load_statement_labels(...)`
- `load_statement_snapshot_strict(...)`

### 3. DB-backed runtime 경로를 열었다
- `BacktestEngine.load_ohlcv_from_db(...)`를 추가했다
- `finance/sample.py`에 `*_from_db` 샘플 함수를 추가했다
- 기존 외부 직접조회 기반 샘플은 그대로 유지했다

대표 추가 함수:
- `get_equal_weight_from_db(...)`
- `get_gtaa3_from_db(...)`
- `get_risk_parity_trend_from_db(...)`
- `get_dual_momentum_from_db(...)`
- `portfolio_sample_from_db(...)`

### 4. 첫 DB-backed 전략 검증을 완료했다
- `EqualWeightStrategy`를 첫 검증 전략으로 사용했다
- `DB -> loader -> runtime adapter -> strategy` 경로를 실제로 통과시켰다
- `AAPL`, `MSFT`, `GOOG` 기준 검증과
  `VIG`, `SCHD`, `DGRO`, `GLD` ETF 기준 검증을 모두 완료했다

### 5. OHLCV ingestion을 stock + ETF 공통 경로로 보강했다
- `finance_price.nyse_price_history`를 stock + ETF 공통 가격 원장으로 유지하기로 결정했다
- Daily Market Update가 stock + ETF 혼합 유니버스를 더 쉽게 수집하도록 보강했다
- ETF OHLCV가 실제로 DB에 적재되고 DB-backed sample path에서 사용되는 것까지 확인했다

---

## 이번 챕터의 주요 결정

### 단일 가격 fact table 유지
- `stock`과 `etf`는 가격 구조가 동일하므로
  `finance_price.nyse_price_history` 하나에 함께 저장하는 방향을 유지한다

### strict / broad 구분 기준
- strict loader는 시간 해석과 point-in-time 안전성 기준이 더 엄격하다
- broad loader는 연구용으로 더 넓게 읽지만, broken legacy row를 다시 허용하지는 않는다

### sample 함수 운영 원칙
- 기존 `get_*` 함수는 외부 직접조회 기반 예시로 유지한다
- DB 기반 검증은 별도 `*_from_db` 함수로 분리한다

---

## 검증 요약

이번 챕터에서 확인한 대표 검증:
- loader smoke validation
- DB-backed `EqualWeightStrategy` 실행
- ETF OHLCV 적재 후 DB-backed ETF equal-weight 실행
- broad fundamentals / factors loader 조회
- broad / strict statement loader 조회

관련 검증 문서:
- `.note/finance/phase3/PHASE3_FIRST_DB_BACKED_RUNTIME_VALIDATION.md`
- `.note/finance/phase3/PHASE3_OHLCV_INGESTION_VALIDATION.md`
- `.note/finance/phase3/PHASE3_STATEMENT_LOADER_VALIDATION.md`

---

## 아직 남아 있는 것

이번 챕터는 loader와 최소 runtime path를 여는 데 집중했다.
아직 남아 있는 다음 단계는 다음과 같다.

1. runtime generalization
   - sample helper 수준을 넘어 engine / runtime 쪽 공통 경로를 더 정리
2. loader 사용 전략 확장
   - price-only 전략 외에 fundamentals / factors 기반 전략 연결 준비
3. UI handoff 준비
   - Phase 4에서 호출 가능한 runtime entrypoint 구조 정리
4. 성능/운영 최적화 후속
   - 더 깊은 yfinance 대량 수집 최적화는 후속 트랙으로 유지

---

## 현재 판단

Phase 3는 아직 전체 완료는 아니다.

하지만 이번 첫 챕터를 통해:
- loader read-path
- DB-backed sample path
- broad / strict statement path
- stock + ETF 공통 OHLCV 적재 경로

까지 확보했기 때문에,
이제부터는 “기초 구현 준비 단계”가 아니라
“runtime 일반화와 Phase 4 handoff 준비 단계”로 넘어간다고 보는 것이 맞다.
