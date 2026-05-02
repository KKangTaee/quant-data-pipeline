# Backtest Loader Input Contract

## 목적
이 문서는 PHASE2의 loader 계층 구현 전에,
price / fundamentals / factors / detailed financial statements / universe loader가
공통적으로 따를 입력 계약을 정의한다.

핵심 원칙:
- 전략 코드와 UI는 개별 테이블 구조 대신 loader 입력 계약만 안다
- 같은 의미의 입력은 loader 종류가 달라도 최대한 같은 이름과 해석 규칙을 쓴다
- `nyse_financial_statement_labels`, `nyse_financial_statement_values`는
  장기 이력과 세부 계정 확보를 위한 first-class raw ledger로 취급한다

---

## 1. 공통 설계 원칙

### 1-1. 입력 해석 우선순위
심볼 대상 결정은 아래 순서를 따른다.

1. `symbols`가 명시되면 그것을 최우선 사용
2. `symbols`가 없고 `universe_source`가 있으면 source를 해석해 심볼 집합을 로드
3. 둘 다 없으면 loader는 예외를 발생시키거나 명시적 validation error를 반환

즉, `symbols`는 explicit override다.

### 1-2. loader는 raw SQL 노출을 숨긴다
전략, 웹 UI, 백테스트 실행기는
- DB명
- 테이블명
- SQL 조건식
을 직접 알지 않아야 한다.

이 정보는 loader 내부 구현에만 남긴다.

### 1-3. 날짜 입력은 문자열 또는 datetime 허용
공개 함수는 우선 아래 둘을 허용하는 방향으로 설계한다.

- ISO 문자열: `YYYY-MM-DD`
- `pd.Timestamp` 또는 `datetime`

loader 내부에서는 최종적으로 `pd.Timestamp`로 정규화한다.

### 1-4. 반환 전 입력 정규화 helper를 둔다
실제 구현 시 아래 helper를 별도 공통 함수로 둔다.

- `resolve_loader_symbols(...)`
- `normalize_date_range(...)`
- `normalize_loader_freq(...)`
- `normalize_timeframe(...)`

---

## 2. 공통 입력 필드 계약

### 2-1. `symbols`

의미:
- 명시적으로 지정한 심볼 목록

형태:
- `list[str]`
- 또는 UI/CLI 입력에서 온 문자열은 helper에서 `list[str]`로 변환

규칙:
- 공백 제거
- 대문자 정규화
- 중복 제거
- 빈 값 제거
- 명백히 잘못된 ticker 형식은 validation 단계에서 제외 또는 예외 처리

비고:
- `symbols`가 있으면 `universe_source`보다 우선한다

### 2-2. `universe_source`

의미:
- 사전 정의된 심볼 유니버스 소스

예상 enum:
- `manual`
- `nyse_stocks`
- `nyse_etfs`
- `nyse_stocks_etfs`
- `profile_filtered_stocks`
- `profile_filtered_etfs`
- `profile_filtered_stocks_etfs`

규칙:
- `manual`은 loader 공통 계약에서는 기본 source가 아니다
- `manual`은 주로 UI 계층에서 `symbols` 직접 입력과 연결된다
- loader 계층에서는 `symbols is None`일 때만 `universe_source`를 해석한다

### 2-3. `start`, `end`

의미:
- 시계열 범위 필터

형태:
- `start: str | datetime | None`
- `end: str | datetime | None`

규칙:
- 둘 다 있으면 inclusive range로 해석
- `start`만 있으면 `>= start`
- `end`만 있으면 `<= end`
- 둘 다 없으면 loader별 기본 범위를 사용하거나 전체 범위를 허용

주의:
- price loader에서는 `date`
- fundamentals / factors / statements에서는 기본적으로 `period_end`
기준 필터로 해석한다

### 2-4. `as_of_date`

의미:
- 특정 시점 기준 snapshot 조회

형태:
- `str | datetime`

규칙:
- `as_of_date`가 있으면 loader는 시계열 전체가 아니라 snapshot 조회로 해석
- snapshot은 기본적으로 `period_end <= as_of_date`인 최신 row를 반환한다
- point-in-time에서 실제 공시 가능 시점 반영은 D-4에서 별도 강화한다

비고:
- `start/end`와 동시에 쓰지 않는 것을 기본 규칙으로 한다
- 같이 들어오면 `as_of_date`가 우선하는 것이 아니라 validation error로 처리하는 쪽이 안전하다

### 2-5. `freq`

의미:
- 회계/팩터 주기

예상 값:
- `annual`
- `quarterly`

적용 대상:
- fundamentals loader
- factor loader
- detailed financial statement loader

규칙:
- price loader는 `freq` 대신 `timeframe`을 쓴다
- statement loader에서 `freq`는 저장 주기와 period type이 충돌하지 않도록 같은 의미로 유지한다

### 2-6. `timeframe`

의미:
- 가격 데이터 주기

예상 값:
- `1d`
- `1wk`
- `1mo`

적용 대상:
- price loader 전용

규칙:
- OHLCV loader에서만 사용
- fundamentals / factors / statements에는 사용하지 않는다

### 2-7. `field`

의미:
- price matrix에서 어떤 가격 필드를 pivot할지 결정

예상 값:
- `open`
- `high`
- `low`
- `close`
- `adj_close`
- `volume`

적용 대상:
- `load_price_matrix(...)`

### 2-8. `factor_names`

의미:
- factor snapshot 또는 factor matrix에서 가져올 factor 목록

형태:
- `list[str]`

예상 값 예시:
- `per`
- `pbr`
- `psr`
- `ev_ebit`
- `roe`
- `roa`
- `gpa`

### 2-9. `statement_type`

의미:
- 상세 재무제표 데이터에서 어떤 statement group을 볼지 지정

예상 값 예시:
- `income_statement`
- `balance_sheet`
- `cash_flow`

비고:
- 실제 raw ledger의 label 체계와 mapping 규칙은 구현 단계에서 고정해야 한다
- 1차 loader에서는 optional filter로만 취급한다

---

## 3. loader별 입력 계약

## 3-1. Universe Loader

핵심 입력:
- `source`
- 선택적 filter: `kind`, `sector`, `country`, `limit`

규칙:
- Universe loader는 `symbols`를 직접 받지 않는다
- 대신 source 기반으로 심볼 리스트를 생성한다
- 결과는 `list[str]` 정규화 반환이 기본이다

---

## 3-2. Price Loader

핵심 입력:
- `symbols` 또는 `universe_source`
- `start`, `end`
- `timeframe`
- 선택적으로 `field`

규칙:
- 최종적으로는 resolved symbol list를 기반으로 조회
- `start/end`는 `finance_price.nyse_price_history.date` 기준으로 필터
- `load_price_history(...)`는 long-form 반환
- `load_price_matrix(...)`는 `index=date`, `columns=symbol`

권장 기본값:
- `timeframe="1d"`

---

## 3-3. Fundamentals Loader

핵심 입력:
- `symbols` 또는 `universe_source`
- `freq`
- `start`, `end` 또는 `as_of_date`

규칙:
- 시계열 조회는 `period_end` 기준
- snapshot 조회는 `as_of_date` 기준 latest available row 반환
- `freq`는 반드시 `annual` 또는 `quarterly`

권장 기본값:
- `freq="annual"`

---

## 3-4. Factor Loader

핵심 입력:
- `symbols` 또는 `universe_source`
- `freq`
- `start`, `end` 또는 `as_of_date`
- 선택적으로 `factor_names`

규칙:
- fundamentals loader와 최대한 같은 계약을 따른다
- snapshot은 cross-sectional factor table 반환
- matrix loader는 factor 1개 기준 pivot 또는 multi-index 여부를 별도 결정해야 한다

권장 기본값:
- `freq="annual"`

---

## 3-5. Detailed Financial Statement Loader

핵심 입력:
- `symbols` 또는 `universe_source`
- `freq`
- `start`, `end` 또는 `as_of_date`
- `statement_type`

역할:
- yfinance summary tables보다 더 긴 과거 이력을 확보
- 세부 account-level 데이터를 기반으로 custom factor를 재구성
- 장기 백테스트와 재무 원장 추적에 사용

역할 구분:
- `nyse_financial_statement_values`
  - detailed statement loader의 raw source of truth
- `nyse_financial_statement_labels`
  - operator-facing summary / label lookup 보조 계층
  - semantic identity의 최종 기준으로 사용하지 않는다

규칙:
- 기본 필터 축은 `symbol`, `freq`, `period_end`
- `labels` loader와 `values` loader를 분리하되,
  전략/UI에는 가능하면 `pivot` 또는 `snapshot` helper를 제공한다
- `statement_type`은 optional filter다
- strict snapshot / point-in-time loader는 `values` 중심으로 설계한다

권장 기본값:
- `freq="annual"`

---

## 4. 충돌 규칙

### 4-1. `symbols`와 `universe_source`가 동시에 들어온 경우
- `symbols`를 우선 사용
- `universe_source`는 metadata로만 기록 가능
- 실제 조회 대상은 `symbols`

### 4-2. `start/end`와 `as_of_date`가 동시에 들어온 경우
- 허용하지 않는다
- validation error 처리

### 4-3. `freq`와 price `timeframe` 혼용
- 허용하지 않는다
- price loader는 `timeframe`
- fundamentals / factors / statements는 `freq`

---

## 5. 1차 구현 권장 범위

우선 구현:
1. `load_universe(...)`
2. `load_price_history(...)`
3. `load_price_matrix(...)`
4. `load_fundamentals(...)`
5. `load_factors(...)`
6. `load_statement_values(...)`

그 다음 구현:
1. `load_fundamental_snapshot(...)`
2. `load_factor_snapshot(...)`
3. `load_statement_pivot(...)`
4. `load_statement_snapshot(...)`

이유:
- 1차 백테스트와 전략 UI는 먼저 시계열/테이블 로드가 중요
- snapshot / point-in-time loader는 D-4에서 기준을 더 강화한 뒤 구현하는 것이 안전

---

## 6. 구현 전 체크리스트

- `symbols`와 `universe_source` 해석 helper를 공통화했는가
- `start/end`와 `as_of_date`의 충돌을 막았는가
- `freq`와 `timeframe`을 loader별로 분리했는가
- detailed financial statement loader를 보조가 아닌 핵심 원장으로 취급했는가
- loader가 table name과 SQL 세부사항을 외부에 노출하지 않는가
