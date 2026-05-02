# Phase 3 DB Sample Entrypoints

## 목적
이 문서는 기존 전략 샘플 함수와 별도로,
DB 기반 검증을 위해 추가한 `*_from_db` entrypoint를 정리한다.

---

## 추가된 함수

- `get_equal_weight_from_db(...)`
- `get_gtaa3_from_db(...)`
- `get_risk_parity_trend_from_db(...)`
- `get_dual_momentum_from_db(...)`
- `portfolio_sample_from_db(...)`

---

## 기본 원칙

- 기존 `get_*` 함수는 그대로 유지한다
- 새 `get_*_from_db` 함수는 DB에 적재된 OHLCV를 사용한다
- 내부적으로는 `BacktestEngine.load_ohlcv_from_db(...)`를 사용한다

---

## 사용 전 전제

DB 기반 함수는 사용 전에
해당 심볼의 OHLCV가 MySQL에 적재되어 있어야 한다.

즉:
- 먼저 수집
- 그 다음 `*_from_db` 호출

---

## 결론

Phase 3부터는
기존 외부 조회 전략 함수와
DB 기반 전략 함수를 병행 운영한다.
