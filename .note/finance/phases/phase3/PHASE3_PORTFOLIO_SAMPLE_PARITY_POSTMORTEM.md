# Phase 3 Portfolio Sample Parity Postmortem

## 목적
이 문서는
`portfolio_sample(...)`와 `portfolio_sample_from_db(...)`가
처음에는 서로 다른 결과를 냈다가,
최종적으로 동일한 결과를 내게 된 과정을
비교 중심으로 정리하기 위한 회고 문서다.

참조 문서:
- `.note/finance/phases/phase3/PHASE3_DB_SAMPLE_ALIGNMENT_VALIDATION.md`

---

## 문제 요약

초기 상태에서는
동일한 전략 샘플을 실행했을 때:

- direct path:
  - `portfolio_sample(...)`
- DB-backed path:
  - `portfolio_sample_from_db(...)`

결과가 서로 달랐다.

이 차이는 단순 오차 수준이 아니라,
- 시작일 지연
- 최종 수익률 차이
- Sharpe Ratio / MDD 차이

까지 포함하는 수준이었다.

---

## 당시 관찰된 결과 차이

검증 기준:
- `start='2016-01-01'`

### 1. `portfolio_sample(...)`

- `Equal Weight`
  - Start Date: `2016-01-29`
  - End Date: `2026-03-20`
  - End Balance: `30188.4`
- `GTAA`
  - Start Date: `2016-01-29`
  - End Date: `2026-03-20`
  - End Balance: `22589.1`
- `Risk Parity`
  - Start Date: `2016-01-29`
  - End Date: `2026-03-20`
  - End Balance: `15880.0`
- `Dual Momentum`
  - Start Date: `2016-01-29`
  - End Date: `2026-03-20`
  - End Balance: `24600.7`

### 2. `portfolio_sample_from_db(...)`

- `Equal Weight`
  - Start Date: `2016-01-29`
  - End Date: `2026-03-20`
  - End Balance: `36408.9`
- `GTAA`
  - Start Date: `2017-10-31`
  - End Date: `2026-03-20`
  - End Balance: `19960.9`
- `Risk Parity`
  - Start Date: `2016-10-31`
  - End Date: `2026-03-20`
  - End Balance: `15676.0`
- `Dual Momentum`
  - Start Date: `2017-10-31`
  - End Date: `2026-03-20`
  - End Balance: `21433.0`

즉 당시에는:
- `GTAA`, `Risk Parity`, `Dual Momentum`는 시작일 자체가 밀렸고
- `Equal Weight`는 시작일은 같아도 수익률이 과도하게 높게 나왔다

---

## 무엇이 문제였나

문제는 1개가 아니라 2개가 겹쳐 있었다.

### 1. DB-backed runtime의 warmup 순서가 direct path와 달랐다

초기 DB-backed sample 함수는:

1. `start` 이후 데이터만 먼저 DB에서 읽음
2. 그 다음 `MA200`, `12MReturn` 같은 지표 생성
3. 바로 전략 실행

반면 direct path는:

1. 더 긴 기간을 먼저 불러옴
2. 지표 생성
3. 마지막에 `slice(start=...)`

이 차이 때문에:
- `GTAA`
- `Risk Parity`
- `Dual Momentum`

전략은 warmup이 부족했고,
그 결과 시작일이 뒤로 밀렸다.

### 2. `nyse_price_history`의 과거 OHLCV가 mixed-state였다

초기 DB 상태에서는 일부 자산의 과거 row가:

- `close = raw Close`

가 아니라,

- `close ~= Adj Close`

처럼 들어가 있었다.

또한:
- `adj_close`는 비어 있는 row가 많았다
- 일부 자산은 상장 전 blank row도 섞여 있었다
- explicit `end` 사용 시 마지막 거래일이 누락되기도 했다

이 영향으로:
- `Equal Weight` 같은 단순 전략도
- direct path 대비 DB path의 성과가 크게 달랐다

---

## 실제로 바뀐 것

### 1. runtime 순서 보정

수정 파일:
- `finance/engine.py`
- `finance/sample.py`

수정 내용:
- `BacktestEngine.load_ohlcv_from_db(...)`에 `history_start` 추가
- DB-backed sample 함수들이 warmup용 과거 이력을 먼저 읽고
  마지막에 `slice(start=..., end=...)`를 적용하도록 변경

이 수정으로 해결된 것:
- `GTAA` 시작일 지연
- `Risk Parity` 시작일 지연
- `Dual Momentum` 시작일 지연

### 2. canonical OHLCV refresh 경로 보강

수정 파일:
- `finance/data/data.py`

수정 내용:
- blank price row 적재 방지
- 요청 구간 delete + reinsert 지원
- `end`를 inclusive semantics로 보정
- sample 전략 유니버스 전체 OHLCV 재적재

이 수정으로 해결된 것:
- mixed-state `close`
- 비어 있는 `adj_close`
- 마지막 거래일 누락
- 상장 전 blank row 잔존

---

## 수정 후 최종 상태

최종 검증 기준:
- `start='2016-01-01'`
- `end='2026-03-20'`

### `portfolio_sample(...)`

- `Equal Weight`
  - End Balance: `30188.4`
- `GTAA`
  - End Balance: `22589.1`
- `Risk Parity`
  - End Balance: `15880.0`
- `Dual Momentum`
  - End Balance: `24600.7`

### `portfolio_sample_from_db(...)`

- `Equal Weight`
  - End Balance: `30188.4`
- `GTAA`
  - End Balance: `22589.1`
- `Risk Parity`
  - End Balance: `15880.0`
- `Dual Momentum`
  - End Balance: `24600.7`

최종 검증 결과:
- 시작일 동일
- 마지막 날짜 동일
- row 수 동일
- `Total Balance` 시계열 동일
- 성과 요약 지표 동일

---

## 비교 관점에서 본 핵심 변화

### 이전
- direct path와 DB path가 서로 다른 시스템처럼 동작
- DB path는 warmup 부족
- DB price history는 canonical하지 않음
- 같은 전략이어도 결과 신뢰가 어려움

### 현재
- direct path와 DB-backed path가 같은 결과를 재현
- DB loader 기반 전략 경로가 신뢰 가능한 수준으로 정렬됨
- sample 전략 검증에 DB 경로를 사용해도 direct path와 parity 확인 가능

---

## 결론

이 이슈의 본질은
“DB 경로가 틀렸다”가 아니라,

1. runtime 순서가 direct path와 달랐고
2. historical OHLCV가 canonical하지 않았던 것

이었다.

지금은 두 문제를 모두 해결했기 때문에,
`portfolio_sample(...)`와 `portfolio_sample_from_db(...)`는
동일한 전략 결과를 반환하는 상태로 본다.
