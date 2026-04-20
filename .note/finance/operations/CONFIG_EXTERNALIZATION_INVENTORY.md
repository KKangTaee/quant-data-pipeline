# Config Externalization Inventory

## 목적
이 문서는 PHASE2의 `설정 외부화 준비`를 위해
현재 코드에 하드코딩되어 있는 운영 관련 상수들을 inventory 형태로 정리한 문서다.

목표는 다음과 같다.

- 어떤 값들이 현재 코드 안에 박혀 있는지 식별
- 외부화 가치가 높은 항목과 낮은 항목을 구분
- 이후 `config/finance_web_app.toml` 같은 설정 파일 도입의 입력 자료로 사용

---

## 분류 기준

### 높은 우선순위
- 환경별로 달라질 가능성이 큼
- 운영자가 자주 바꾸고 싶어할 가능성이 큼
- 코드 수정 없이 바꾸는 것이 실질적으로 유리함

### 중간 우선순위
- 바꿀 가능성은 있으나 자주 바꾸지는 않음
- 한 번 정해두면 장기간 유지할 수 있음

### 낮은 우선순위
- 도메인 규칙이나 스키마 정의에 가까움
- 외부화보다 코드 상수로 유지하는 편이 더 명확함

---

## 1. 웹 앱 운영 기본값

출처:
- `app/web/streamlit_app.py`

### 항목

- `SYMBOL_PRESETS`
  - 현재값:
    - `Big Tech`
    - `Core ETFs`
    - `Dividend ETFs`
    - `Custom`
  - 우선순위:
    - 높음
  - 이유:
    - 운영자 취향이나 전략 유니버스에 따라 자주 바뀔 수 있음

- `PERIOD_PRESETS`
  - 현재값:
    - `1d`, `7d`, `1mo`, `3mo`, `6mo`, `1y`, `5y`, `10y`, `15y`
  - 우선순위:
    - 중간
  - 이유:
    - 완전히 자주 바꾸지는 않지만, 운영 기준 기간은 조정 가능성이 있음

- `SYMBOL_SOURCE_OPTIONS`
  - 현재값:
    - Manual
    - NYSE Stocks
    - NYSE ETFs
    - NYSE Stocks + ETFs
    - Profile Filtered Stocks
    - Profile Filtered ETFs
    - Profile Filtered Stocks + ETFs
  - 우선순위:
    - 낮음
  - 이유:
    - 거의 기능 정의에 가까워서 빈번히 바뀌지는 않을 가능성이 큼

- large run warning threshold
  - 현재값:
    - `warn_threshold = 200`
  - 우선순위:
    - 높음
  - 이유:
    - 운영 규모에 따라 쉽게 달라질 수 있음

- progress 표시 threshold
  - 현재값:
    - symbol count `>= 100`일 때 progress bar 표시
  - 우선순위:
    - 높음
  - 이유:
    - 사용자 체감과 성능 상황에 따라 조정 가능성이 큼

- Operational Pipeline 기본값
  - Daily Market Update:
    - source = `NYSE Stocks`
    - period = `1mo`
    - interval = `1d`
  - Weekly Fundamental Refresh:
    - source = `NYSE Stocks`
    - freq = `quarterly`
  - Extended Statement Refresh:
    - source = `Profile Filtered Stocks`
    - period type = `annual`
    - periods = `8`
  - Metadata Refresh:
    - kinds = `stock`, `etf`
  - 우선순위:
    - 높음
  - 이유:
    - 운영 전략에 따라 달라질 수 있는 대표적인 기본값들임

---

## 2. DB 접속 정보

출처:
- `app/jobs/symbol_sources.py`
- `app/jobs/preflight_checks.py`
- `finance/data/*.py`
- `finance/sample.py`
- `finance/data/nyse_db.py`

### 항목

- host
  - 현재값:
    - `localhost`
- user
  - 현재값:
    - `root`
- password
  - 현재값:
    - `1234`
- port
  - 현재값:
    - `3306`

우선순위:
- 매우 높음

이유:
- 환경별로 반드시 달라질 수 있음
- 보안 측면에서도 코드 하드코딩이 좋지 않음
- 가장 먼저 외부화해야 할 후보

---

## 3. 배치/재시도/슬립 관련 ingest 파라미터

출처:
- `finance/data/data.py`
- `finance/data/fundamentals.py`
- `finance/data/financial_statements.py`
- `finance/data/asset_profile.py`
- `finance/data/nyse.py`

### OHLCV
- `chunk_size = 50`
- `sleep = 0.4`

### fundamentals
- `chunk_size = 25`
- `sleep = 0.6`

### financial_statements
- `chunk_size = 20`
- `sleep = 0.8`
- `max_retry = 3`

### asset_profile
- `chunk_size = 50`
- `sleep = 0.4`
- `max_retry = 3`

### nyse 수집
- `sleep = 1.5`

우선순위:
- 높음

이유:
- 공급자 응답 상태, rate limit, 운영 시간대에 따라 조정할 가능성이 큼
- 실제 운영 안정성에 직접 영향

---

## 4. 주기/기간 기본값

출처:
- `app/jobs/ingestion_jobs.py`
- `app/web/streamlit_app.py`
- `finance/data/*.py`

### 항목
- 기본 `freq = annual`
- 기본 `period = annual`
- 기본 `interval = 1d`
- 기본 `period = 1y`
- financial statement `periods = 4`

우선순위:
- 중간

이유:
- 일부는 운영 기본값으로 의미가 크지만
- 일부는 함수 시그니처의 안전한 fallback 역할이기도 함

---

## 5. UI/표시 관련 상수

출처:
- `app/web/streamlit_app.py`

### 항목
- `Recent Logs` file limit
  - 현재값:
    - 최근 5개
- `Failure CSV` file limit
  - 현재값:
    - 최근 5개
- `load_run_history(limit=30)` 같은 표시 개수
- `recent_results` 세션 보관 개수
  - 현재값:
    - 10개

우선순위:
- 중간

이유:
- UI 사용성에 따라 바뀔 수 있으나 핵심 운영 로직보다는 덜 중요함

---

## 6. 낮은 우선순위 또는 외부화 비권장

### 항목
- DB schema의 enum 값
  - 예: `1d`, `1wk`, `1mo`, `annual`, `quarterly`
- pipeline/job 이름 문자열
- write-target mapping 자체의 개념 구조

이유:
- 이 값들은 설정이라기보다 시스템 정의에 가까움
- 외부화하면 오히려 코드 이해도가 떨어질 수 있음

---

## 우선 외부화 추천 순서

1. DB 접속 정보
2. 운영 파이프라인 기본값
3. large-run / progress threshold
4. batch / sleep / retry 파라미터
5. symbol presets
6. UI 표시 개수

---

## 외부화 우선순위 분류

### 즉시 외부화 대상

- DB 접속 정보
  - 이유:
    - 환경 의존성이 가장 크고 보안 이슈도 직접적임

- 운영 파이프라인 기본값
  - 이유:
    - 현재 가장 자주 바뀔 가능성이 큰 운영값
    - daily/weekly/extended 기본 동작을 코드 수정 없이 조정할 수 있어야 함

- large-run / progress threshold
  - 이유:
    - 사용성 조정이 자주 필요할 수 있음
    - 운영 규모가 바뀌면 빠르게 튜닝하고 싶어질 가능성이 큼

### 다음 단계 외부화 대상

- batch / sleep / retry 파라미터
  - 이유:
    - 실제 운영 안정성과 rate limit 대응에 중요하지만
    - 먼저 UI/운영 기본값 외부화가 끝난 뒤 묶어도 됨

- symbol presets
  - 이유:
    - 운영 편의성에는 중요하지만
    - 시스템 동작 자체보다는 사용자 편의 영역에 가까움

### 나중 단계 외부화 대상

- UI 표시 개수
  - 이유:
    - 운영 핵심보다는 화면 편의성 문제

- period/freq 함수 fallback 기본값 일부
  - 이유:
    - 일부는 설정이라기보다 함수 시그니처의 안전한 기본값 역할이 큼

### 외부화 비권장 또는 보류

- schema enum 값
- job/pipeline 이름 문자열
- write-target 구조 정의

이유:
- 설정이라기보다 시스템 정의에 가까움
- 외부화해도 운영 가치보다 복잡성 증가 가능성이 큼

---

## 다음 단계 제안

이 inventory 기준으로 다음 작업은 아래 순서가 적절하다.

1. `C-2 외부화 우선순위 분류`
2. `C-3 설정 파일 경로 확정`
3. `C-4 설정 파일 포맷 초안 작성`
4. 이후 `config/finance_web_app.toml` 도입

---

## 설정 파일 경로 결정

### 확정 경로
- `config/finance_web_app.toml`

### 결정 이유
- 프로젝트 루트 기준에서 찾기 쉽다
- 웹 앱 운영 설정이라는 목적이 파일명에 직접 드러난다
- 나중에 `config/finance_data_pipeline.toml`, `config/backtest.toml` 같은 식으로 확장하기 쉽다
- `.note/finance`는 기록/문서 영역이고, 실제 런타임 설정은 코드와 같은 레벨의 `config/` 아래에 두는 편이 역할이 명확하다

### 현재 판단
- 1차 설정 파일은 하나로 시작한다
- 웹 앱과 운영 파이프라인 기본값을 먼저 이 파일에 넣는다
- DB 접속 정보도 같은 파일에 둘 수 있지만,
  장기적으로는 환경변수 분리를 검토할 수 있다

### 후속 작업 연결
- 다음 단계:
  - `C-4 설정 파일 포맷 초안 작성`
- 이후:
  - 실제 `config/finance_web_app.toml` 파일 생성

---

## 설정 파일 포맷 초안

### 선택 포맷
- `TOML`

### 선택 이유
- 사람 읽기 쉬움
- 섹션 구조가 명확함
- Python에서 다루기 쉬움
- 운영 설정 파일 용도로 JSON보다 덜 답답하고, YAML보다 단순한 편

### 초안 구조

```toml
[database]
host = "localhost"
user = "root"
password = "1234"
port = 3306

[ui.thresholds]
large_run_warning = 200
progress_display = 100

[ui.history]
recent_results_limit = 10
persistent_history_limit = 30
recent_logs_limit = 5
failure_csv_limit = 5

[presets.symbols]
big_tech = "AAPL,MSFT,GOOG"
core_etfs = "SPY,QQQ,TLT,GLD"
dividend_etfs = "VIG,SCHD,DGRO,GLD"

[operational.daily_market_update]
default_source = "NYSE Stocks"
default_period = "1mo"
default_interval = "1d"

[operational.weekly_fundamental_refresh]
default_source = "NYSE Stocks"
default_freq = "quarterly"

[operational.extended_statement_refresh]
default_source = "Profile Filtered Stocks"
default_period_type = "annual"
default_periods = 8

[operational.metadata_refresh]
default_kinds = ["stock", "etf"]

[ingestion.ohlcv]
chunk_size = 50
sleep = 0.4

[ingestion.fundamentals]
chunk_size = 25
sleep = 0.6

[ingestion.financial_statements]
chunk_size = 20
sleep = 0.8
max_retry = 3

[ingestion.asset_profile]
chunk_size = 50
sleep = 0.4
max_retry = 3
```

### 1차 포함 권장 섹션

- `[database]`
  - 가장 먼저 외부화 가치가 큰 영역

- `[ui.thresholds]`
  - large-run / progress threshold를 바로 옮기기 좋음

- `[presets.symbols]`
  - preset 변경을 코드 수정 없이 하게 만들기 좋음

- `[operational.*]`
  - 운영 파이프라인 기본값 외부화의 핵심

### 1차에서는 보류 가능 섹션

- `[ui.history]`
  - 중요도는 있지만, 1차 설정 파일 도입 후 다음에 옮겨도 됨

- `[ingestion.*]`
  - 유용하지만 먼저 UI/운영값부터 바꾸는 편이 우선순위상 더 자연스러움

### 구현 순서 제안

1. `database`
2. `ui.thresholds`
3. `presets.symbols`
4. `operational.*`
5. 필요 시 `ingestion.*`

### 다음 실제 구현 연결

다음 구현 단계에서는 아래 중 하나로 바로 이어질 수 있다.

1. 실제 `config/finance_web_app.toml` 생성
2. TOML 로더 모듈 추가
3. 웹 앱의 일부 하드코딩 상수를 새 설정 파일에서 읽도록 연결
