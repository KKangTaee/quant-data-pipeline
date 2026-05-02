# Phase 3 Repeatable DB-Backed Smoke Scenarios

## 목적
이 문서는 Phase 3 이후 DB-backed runtime 경로를 빠르게 재검증하기 위한
반복 가능한 smoke scenario 세트를 고정한다.

핵심 목표:
- 코드 변경 후 최소 검증 절차를 짧게 반복 가능하게 만들기
- direct path / DB-backed path / loader path / ingestion path를 각각 대표하는 시나리오를 유지하기

---

## 공통 원칙

- 가능한 한 작은 symbol set을 사용한다
- 너무 오래 걸리는 full-universe 검증은 smoke scenario에 넣지 않는다
- 각 scenario는 무엇을 검증하는지 명확해야 한다
- “성공”의 기준은 숫자 자체보다 경로가 정상적으로 이어지는지에 둔다
- parity가 필요한 경우에는 direct path와 DB-backed path가 동일해야 한다

---

## Scenario 1. Minimal DB-Backed Price Strategy

목적:
- 가장 작은 DB-backed runtime 경로 검증

검증 경로:
- `finance_price.nyse_price_history`
- `load_price_strategy_dfs(...)`
- `BacktestEngine.load_ohlcv_from_db(...)`
- `EqualWeightStrategy`

입력:
- `symbols = ['AAPL', 'MSFT', 'GOOG']`
- `start = '2024-01-01'`
- `end = '2024-12-31'`
- `timeframe = '1d'`
- `rebalance_interval = 21`

실행 예시:

```python
from finance.sample import get_equal_weight_from_db

df = get_equal_weight_from_db(
    tickers=['AAPL', 'MSFT', 'GOOG'],
    start='2024-01-01',
    end='2024-12-31',
    interval=21,
)
```

확인 포인트:
- 예외 없이 실행
- 결과 DataFrame 생성
- `Date`, `Total Balance`, `Total Return` 존재

---

## Scenario 2. ETF Ingestion + DB Runtime

목적:
- ETF OHLCV 적재와 DB-backed strategy path가 같이 동작하는지 확인

검증 경로:
- `Daily Market Update` 또는 `run_collect_ohlcv(...)`
- `finance_price.nyse_price_history`
- `get_equal_weight_from_db(...)`

입력:
- `symbols = ['VIG', 'SCHD', 'DGRO', 'GLD']`
- 수집 구간: `1y`, `1d`
- 전략 구간: `2025-01-01 ~ 2026-03-22`

확인 포인트:
- ETF row가 `nyse_price_history`에 저장됨
- DB-backed Equal Weight가 예외 없이 실행됨

비고:
- stock + ETF 단일 price table 방향 검증용

---

## Scenario 3. Direct vs DB Portfolio Parity

목적:
- canonicalized DB path가 legacy direct-fetch sample과 동일한 결과를 내는지 확인

검증 경로:
- `portfolio_sample(...)`
- `portfolio_sample_from_db(...)`

입력:
- `start = '2016-01-01'`
- `end = '2026-03-20'`

대상 전략:
- Equal Weight
- GTAA
- Risk Parity
- Dual Momentum

확인 포인트:
- 시작일 동일
- 마지막 날짜 동일
- row 수 동일
- `Total Balance` 시계열 동일

비고:
- runtime order + canonical OHLCV refresh가 모두 유지되는지 보는 가장 중요한 회귀 시나리오

---

## Scenario 4. Broad Loader Smoke

목적:
- Phase 3에서 만든 read-path loader들이 여전히 정상 동작하는지 확인

대상:
- `load_fundamentals(...)`
- `load_fundamental_snapshot(...)`
- `load_factors(...)`
- `load_factor_snapshot(...)`
- `load_statement_values(...)`
- `load_statement_snapshot_strict(...)`

입력 예시:
- `symbols = ['AAPL', 'MSFT']`
- annual 기준
- 최근 3~4개 period 범위

확인 포인트:
- DataFrame이 비어 있지 않음
- snapshot이 symbol당 1행 형태를 유지
- strict statement snapshot이 `available_at <= as_of_date` 의미를 유지

---

## Scenario 5. Fundamentals / Factors Hardening Sample

목적:
- 최근 hardening된 summary/derived layer가 정상 동작하는지 확인

대상:
- `upsert_fundamentals(...)`
- `upsert_factors(...)`

입력:
- `symbols = ['AAPL', 'MSFT']`
- `freq = 'annual'`
- `freq = 'quarterly'`

확인 포인트:
- `nyse_fundamentals`에 blank summary row가 남지 않음
- 새 base field / source metadata가 저장됨
- `nyse_factors`에 새 factor / price metadata가 저장됨

비고:
- full-universe backfill이 아니라 sample validation용

---

## 권장 실행 순서

일반적인 코드 변경 후 최소 순서:

1. Scenario 1
2. Scenario 3

OHLCV 수집/DB 경로 변경 후:

1. Scenario 2
2. Scenario 3

fundamentals/factors 관련 변경 후:

1. Scenario 5
2. Scenario 4

---

## smoke scenario와 full validation의 차이

smoke scenario는:
- 경로가 살아 있는지
- 주요 계약이 깨지지 않았는지
- 최소 대표 사례에서 오류가 없는지

만 보는 단계다.

full validation은:
- 더 큰 universe
- 더 긴 기간
- 더 많은 전략
- 운영 성능 / coverage / null 분포

까지 포함한다.

즉 smoke scenario는 회귀 방지용 최소 세트로 유지하는 것이 맞다.

---

## 현재 결론

Phase 3 이후 반복적으로 가장 중요하게 볼 시나리오는 아래 3개다.

1. `Minimal DB-Backed Price Strategy`
2. `Direct vs DB Portfolio Parity`
3. `Fundamentals / Factors Hardening Sample`

이 3개가 통과하면,
price runtime / DB-backed sample path / summary/derived research layer가
기본적으로 살아 있다고 봐도 된다.
