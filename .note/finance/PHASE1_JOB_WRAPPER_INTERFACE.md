# Phase 1 Job Wrapper Interface

## 목적
이 문서는 1차 내부 웹 앱이 호출할 job wrapper 계층의 인터페이스를 정의하기 위한 문서다.

목표:
- 웹 UI가 `finance/data/*`의 low-level 함수에 직접 의존하지 않게 만들기
- 수집 작업의 입력/출력 형식을 통일하기
- 이후 실행 이력 저장, 실패 요약, 자동화로 확장하기 쉽게 만들기

---

## 왜 job wrapper가 필요한가

현재 프로젝트에는 이미 수집 함수가 존재한다.

예:
- `store_ohlcv_to_mysql(...)`
- `upsert_fundamentals(...)`
- `upsert_factors(...)`

하지만 이 함수들을 웹 UI에서 직접 호출하면 문제가 생긴다.

예:
- 함수별 파라미터 형식이 제각각일 수 있음
- 반환값 형식이 통일되지 않음
- 예외 처리 위치가 분산됨
- UI에서 실패/성공 표시가 복잡해짐

따라서 UI와 수집 함수 사이에 얇은 실행 계층이 필요하다.

---

## 1차 wrapper 대상

1차에서는 아래 세 개만 감싼다.

### 1. OHLCV 수집
원본 함수:
- `finance.data.data.store_ohlcv_to_mysql(...)`

wrapper 이름 제안:
- `run_collect_ohlcv(...)`

### 2. fundamentals 수집
원본 함수:
- `finance.data.fundamentals.upsert_fundamentals(...)`

wrapper 이름 제안:
- `run_collect_fundamentals(...)`

### 3. factors 계산
원본 함수:
- `finance.data.factors.upsert_factors(...)`

wrapper 이름 제안:
- `run_calculate_factors(...)`

---

## wrapper 설계 원칙

### 1. UI 친화적이어야 한다
UI는 wrapper에 단순한 입력을 전달하고, 통일된 결과를 받아야 한다.

### 2. 기존 수집 함수를 재사용해야 한다
wrapper는 새 수집 로직을 만들지 않는다.

### 3. 예외를 직접 흘려보내지 않고 결과 객체로 정리해야 한다
즉, 가능하면:
- 성공
- 부분 성공
- 실패

를 구조적으로 반환해야 한다.

### 4. 향후 실행 이력 저장과 연결 가능해야 한다
즉, 결과에는 시작/종료 시각과 메시지가 들어가는 것이 좋다.

---

## 권장 파일 구조

1차에서는 단순하게 시작하는 것이 좋다.

권장 구조:

```text
app/
  jobs/
    ingestion_jobs.py
```

또는 더 단순하게:

```text
admin/
  jobs.py
```

내 추천:
- 처음에는 `app/jobs/ingestion_jobs.py`

이유:
- 이후 UI와 job 코드를 분리하기 쉽다
- 확장 시 `backtest_jobs.py` 등을 자연스럽게 추가 가능하다

---

## 공통 입력 규칙

UI에서 wrapper로 전달하는 입력은 아래 원칙을 따른다.

### 1. 가능한 단순한 타입 사용
- `list[str]`
- `str`
- `int`
- `float`
- `None`

### 2. UI 문자열 입력은 wrapper에서 정리 가능해야 한다

예:
- `"AAPL,MSFT,GOOG"` -> `["AAPL", "MSFT", "GOOG"]`

즉, wrapper 앞단 또는 wrapper 내부에 입력 정리 함수가 있어도 된다.

### 3. 파라미터는 너무 많이 열지 않는다

1차에서 노출할 기본 파라미터만 허용:
- symbols
- period
- interval
- freq
- start
- end

---

## 공통 출력 규칙

모든 wrapper는 아래 구조를 목표로 한다.

```python
{
    "job_name": str,
    "status": "success" | "partial_success" | "failed",
    "started_at": str,
    "finished_at": str,
    "duration_sec": float,
    "rows_written": int | None,
    "symbols_requested": int | None,
    "symbols_processed": int | None,
    "failed_symbols": list[str],
    "message": str,
    "details": dict,
}
```

### 상태 해석
- `success`
  - 작업이 정상 완료됨
- `partial_success`
  - 일부는 성공, 일부는 실패
- `failed`
  - 전체 작업이 실패하거나 의미 있는 결과를 만들지 못함

---

## 1차 wrapper별 입력/출력 제안

## 1. `run_collect_ohlcv(...)`

### 입력 제안
- `symbols: list[str]`
- `start: str | None = None`
- `end: str | None = None`
- `period: str = "1y"`
- `interval: str = "1d"`

### 내부 수행
- 입력 심볼 정리
- `store_ohlcv_to_mysql(...)` 호출
- 반환된 적재 행 수를 `rows_written`에 반영

### 주의
- 현재 low-level 함수는 `end` 처리가 완전하지 않으므로,
  결과 메시지에 이 제약을 명시하거나 1차에서는 `end` 입력을 숨기는 것도 가능하다.

### 출력 메시지 예시
- `"OHLCV collection completed"`
- `"OHLCV collection completed with limited date-range handling"`

---

## 2. `run_collect_fundamentals(...)`

### 입력 제안
- `symbols: list[str]`
- `freq: str = "annual"`

### 내부 수행
- `upsert_fundamentals(...)` 호출
- 적재 건수 반환

### 출력 메시지 예시
- `"Fundamentals ingestion completed"`

---

## 3. `run_calculate_factors(...)`

### 입력 제안
- `symbols: list[str] | None = None`
- `freq: str | None = None`
- `start: str | None = None`
- `end: str | None = None`

### 내부 수행
- `upsert_factors(...)` 호출
- 적재 건수 반환

### 출력 메시지 예시
- `"Factor calculation completed"`

---

## 공통 helper 필요 항목

1차 wrapper 구현 전에 아래 helper를 같이 만들면 좋다.

### 1. `parse_symbols(...)`
입력:
- 문자열 또는 리스트

출력:
- 정제된 `list[str]`

기능:
- 공백 제거
- 빈 값 제거
- 중복 제거

### 2. `now_str()` 또는 datetime helper
기능:
- 시작/종료 시각 기록

### 3. `build_job_result(...)`
기능:
- 공통 결과 dict 생성

이 helper가 있으면 wrapper 간 중복이 크게 줄어든다.

---

## 예외 처리 원칙

### 1. wrapper 레벨에서 잡는다
UI에서 traceback를 직접 다루지 않게 한다.

### 2. 결과 객체에 메시지를 넣는다
예:
- `"Database connection failed"`
- `"No symbols provided"`
- `"Factor calculation returned zero rows"`

### 3. 가능한 경우 partial success를 남긴다
단, low-level 함수가 심볼별 실패 목록을 주지 않는 경우는 한계가 있다.

즉, 1차는 완전한 부분 성공 추적보다:
- 실패 시 메시지
- 성공 시 처리 건수

에 집중해도 괜찮다.

---

## 1차 구현 단순화 제안

처음부터 너무 많은 공통 구조를 만들 필요는 없다.

1차는 아래 정도면 충분하다.

- wrapper 함수 3개
- helper 2~3개
- 결과 dict 통일

즉, 작은 abstraction으로 시작한다.

---

## 검증 기준

이 단계가 완료되려면 아래를 만족해야 한다.

1. Python 코드에서 wrapper 3개를 직접 호출할 수 있다.
2. wrapper 3개가 모두 같은 형식의 결과를 반환한다.
3. 실패 시 예외 대신 결과 객체로 상태를 전달한다.
4. UI가 wrapper 결과만으로 상태를 표시할 수 있다.

---

## 다음 단계

이 문서 기준으로 다음 구현 단계는 아래다.

1. 공통 결과 포맷 helper 설계 확정
2. 실제 job wrapper 코드 작성
3. Streamlit 앱 골격에 연결

---

## 현재 결정사항

확정:
- 1차 wrapper 대상은 OHLCV / fundamentals / factors
- wrapper는 UI와 low-level ingestion 함수 사이의 얇은 계층
- 결과는 통일된 dict 구조로 반환

보류:
- dataclass 사용 여부
- 실행 이력을 파일에 남길지 DB에 남길지
