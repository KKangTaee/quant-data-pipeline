# Phase 3 DB Sample Alignment Validation

## 목적
이 문서는 `portfolio_sample(...)`과 `portfolio_sample_from_db(...)`의
결과 차이를 분석하고,
DB-backed sample 경로의 warmup 정렬 수정 결과를 기록하기 위한 검증 문서다.

---

## 문제 요약

같은 명목상 시작 조건(`start='2016-01-01'`)으로 실행해도
직접조회 기반 sample과 DB-backed sample의 결과가 달랐다.

관찰된 차이:
- `GTAA`
- `Risk Parity`
- `Dual Momentum`

에서는 DB-backed sample의 시작일이 direct path보다 늦게 밀렸다.

또한:
- `Equal Weight`

는 시작일은 같았지만 최종 성과가 크게 달랐다.

---

## 원인 분석

### 1. Warmup 부족

DB-backed sample 함수들은 기존에:
- `start` 이후 데이터만 먼저 DB에서 읽고
- 그 다음 `MA200`, `12MReturn` 같은 지표를 계산했다

반면 direct path는:
- 더 긴 기간을 먼저 읽고
- 지표를 계산한 후
- 마지막에 `slice(start=...)`를 적용했다

이 차이 때문에:
- `GTAA`
- `Risk Parity`
- `Dual Momentum`

은 indicator warmup 부족으로 시작일이 뒤로 밀렸다.

### 2. DB price history mixed-state

`finance_price.nyse_price_history`의 오래된 row들 중 일부는
`close`가 raw `Close`가 아니라 사실상 `Adj Close`처럼 저장되어 있었다.

이 영향은 배당형 ETF와 ETF/채권 ETF에서 특히 크게 나타났다.

즉 warmup을 맞춘 후에도:
- direct path
- DB-backed path

의 최종 수익률은 완전히 같아지지 않는다.

---

## 적용한 수정

수정 파일:
- `finance/engine.py`
- `finance/sample.py`
- `finance/data/data.py`

적용 내용:
- `BacktestEngine.load_ohlcv_from_db(...)`에 `history_start` 파라미터 추가
- DB-backed sample 함수에서 warmup용 과거 이력을 먼저 읽고
  마지막에 `.slice(start=..., end=...)`를 적용하도록 정리
- OHLCV 재적재 시:
  - 요청 구간의 기존 row를 지우고 다시 적재할 수 있게 보강
  - 가격이 모두 비어 있는 blank row를 적재하지 않도록 보강
  - `end`를 inclusive semantics로 처리하도록 yfinance 호출을 보정

전략별 warmup 기준:
- `GTAA`: 약 3년
- `Risk Parity`: 약 2년
- `Dual Momentum`: 약 3년

---

## 수정 후 검증 결과

검증 기준:
- `start='2016-01-01'`
- `end='2026-03-20'`

### direct vs db start date

- `Equal Weight`
  - direct: `2016-01-29`
  - db: `2016-01-29`
- `GTAA`
  - direct: `2016-01-29`
  - db: `2016-01-29`
- `Risk Parity`
  - direct: `2016-01-29`
  - db: `2016-01-29`
- `Dual Momentum`
  - direct: `2016-01-29`
  - db: `2016-01-29`

### direct vs db row count

- `Equal Weight`
  - direct: `123`
  - db: `123`
- `GTAA`
  - direct: `62`
  - db: `62`
- `Risk Parity`
  - direct: `123`
  - db: `123`
- `Dual Momentum`
  - direct: `123`
  - db: `123`

1차적으로는 warmup 부족으로 인한
- 시작일 지연
- row 수 감소

문제는 해결됐다.

---

## 2차 canonical rebuild

추가로 sample 전략 유니버스 전체에 대해
`2010-01-01 ~ 2026-03-20` 구간을 canonical refresh로 다시 적재했다.

대상 유니버스:
- `VIG`, `SCHD`, `DGRO`, `GLD`
- `SPY`, `IWD`, `IWM`, `IWN`, `MTUM`, `EFA`, `TLT`, `IEF`, `LQD`, `DBC`, `VNQ`
- `QQQ`, `SOXX`, `BIL`

재적재 후 확인된 상태:
- pre-listing blank row 제거
- `adj_close` 정상 적재
- `close`가 provider raw `Close`와 일치
- 마지막 거래일 `2026-03-20`까지 포함

---

## 최종 검증 결과

최종적으로 아래 4개 sample 경로에 대해 direct path와 DB-backed path가 일치함을 확인했다.

- `Equal Weight`
- `GTAA`
- `Risk Parity`
- `Dual Momentum`

검증 기준:
- `start='2016-01-01'`
- `end='2026-03-20'`

최종 상태:
- 시작일 동일
- 마지막 날짜 동일
- row 수 동일
- `Total Balance` 시계열 동일
- 성과 요약 지표 동일

---

## 결론

이번 수정으로 DB-backed sample path는:
- direct path와 같은 indicator warmup 구조를 따르고
- canonicalized price history를 기준으로 동일한 전략 결과를 재현한다.

즉 이 이슈에 대해서는:
- runtime 순서 문제
- historical OHLCV mixed-state 문제

둘 다 해결된 상태로 본다.
