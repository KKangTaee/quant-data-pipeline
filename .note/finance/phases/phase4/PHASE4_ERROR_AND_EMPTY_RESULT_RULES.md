# Phase 4 Error And Empty Result Rules

## 목적
이 문서는 Phase 4 첫 백테스트 UI에서
입력 오류, 데이터 부재, 일반 실행 오류를 어떻게 구분해 보여줄지 정리한다.

현재 범위:
- `Equal Weight`
- DB-backed
- single-strategy first pass

---

## 현재 분류

현재 first-pass UI는 오류를 아래 3종으로 구분한다.

### 1. Input Error

예:
- `start > end`
- ticker가 비어 있음

현재 처리:
- runtime에서는 `BacktestInputError`
- UI에서는 warning 스타일로 표시

의도:
- 사용자가 직접 바로 고칠 수 있는 문제라는 점을 분명히 한다

### 2. Data Error

예:
- 요청 구간에 MySQL price history가 없음
- 요청 ticker 중 일부가 DB에 없음

현재 처리:
- runtime에서는 `BacktestDataError`
- UI에서는 error 스타일로 표시
- ingestion 재실행 힌트를 같이 보여준다

의도:
- 실행 로직 버그가 아니라 데이터 준비 상태 문제라는 점을 분명히 한다

### 3. System Error

예:
- 예기치 않은 runtime 예외
- 코드 버그
- wrapper 내부 미처리 오류

현재 처리:
- UI에서는 generic execution failed 메시지로 표시

의도:
- first pass에서는 과도한 내부 stack 정보를 바로 노출하지 않는다

---

## 현재 구현 위치

- runtime 분류:
  - `app/web/runtime/backtest.py`
- UI 표시:
  - `app/web/pages/backtest.py`

현재 공개 예외:
- `BacktestInputError`
- `BacktestDataError`

---

## 현재 first-pass 규칙

### Input validation 규칙
- ticker가 최소 1개 이상이어야 한다
- `start_date <= end_date`

### Data validation 규칙
- 요청 ticker/date range/timeframe 기준으로
  DB OHLCV row가 최소한 존재해야 한다
- requested ticker가 모두 조회 결과에 포함되어야 한다

### Result validation 규칙
- `result_df`가 비어 있으면 허용하지 않는다
- 최소 컬럼:
  - `Date`
  - `Total Balance`
  - `Total Return`

---

## 현재 UI 표시 규칙

### Input Error
- warning block

### Data Error
- error block
- ingestion 재실행 힌트 표시

### Success
- 기존 last bundle 표시
- summary / chart / table / meta 표시

---

## 다음 확장 후보

현재 이후에 고려할 수 있는 것:

1. missing ticker를 별도 bullet list로 표시
2. DB range preview 추가
3. empty result 전용 illustration/card
4. error history 저장

---

## 결론

Phase 4 first pass는 지금 아래 기준으로 고정한다.

- 입력 문제는 warning
- 데이터 준비 문제는 data error
- 예기치 않은 문제는 system error
- 성공 시에는 기존 result bundle 표시
