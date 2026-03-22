# Phase 3 Price-Only Runtime Pattern

## 목적
이 문서는 price-only 전략 sample 함수들이 direct path와 DB-backed path에서
어떤 공통 runtime 시작 패턴을 쓰는지 정리한다.

---

## 배경

Phase 3 초반에는 각 sample 함수가 아래 초기화 흐름을 개별적으로 가지고 있었다.

- `BacktestEngine(...)` 생성
- direct path면 `.load_ohlcv()`
- DB path면 `.load_ohlcv_from_db(...)`
- 필요 시 `history_start` 계산

이 패턴은 `Equal Weight`, `GTAA`, `Risk Parity`, `Dual Momentum`에 반복되어 있었다.

---

## 현재 정리된 방식

`finance/sample.py`는 `_build_price_only_engine(...)` helper를 통해
price-only 전략의 공통 runtime 시작 경로를 관리한다.

역할:
- direct path와 DB path의 차이를 한 곳에 모음
- DB-backed path의 warmup history 진입 규칙을 한 곳에서 관리
- 각 전략 sample 함수는 전략별 전처리와 전략 실행 로직에 더 집중

---

## helper 책임

`_build_price_only_engine(...)`는 다음을 담당한다.

- `tickers`, `option`, `period` 기준 `BacktestEngine` 생성
- direct path:
  - `.load_ohlcv()`
- DB-backed path:
  - `history_buffer_years`가 있으면 `history_start` 계산
  - `.load_ohlcv_from_db(start=..., end=..., timeframe=..., history_start=...)`

즉 helper는 **runtime 시작 경로**만 통합하고,
전략별 후속 체인은 각 함수에서 유지한다.

---

## 적용 대상

현재 이 패턴을 쓰는 함수:

- `get_equal_weight(...)`
- `get_equal_weight_from_db(...)`
- `get_gtaa3(...)`
- `get_gtaa3_from_db(...)`
- `get_risk_parity_trend(...)`
- `get_risk_parity_trend_from_db(...)`
- `get_dual_momentum(...)`
- `get_dual_momentum_from_db(...)`

---

## 기대 효과

- sample 함수 간 중복 감소
- direct / DB-backed 경로 차이 관리 지점 단일화
- Phase 4 UI handoff 전에 price-only 전략 공통 runtime 규칙을 더 명확히 유지

---

## 한계

- 이 helper는 price-only 전략 기준이다
- fundamentals / factors / statement loader를 쓰는 전략은 별도 runtime 패턴이 필요할 수 있다
- 따라서 이후 factor/fundamental 전략 확장 시 같은 helper를 그대로 재사용하기보다,
  별도 data-contract helper 계층으로 확장할지 다시 판단해야 한다
