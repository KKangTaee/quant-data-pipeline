# OHLCV And Financial Ingestion Review

## 목적
이 문서는 현재 `finance` 패키지에서 아래 두 기능이 어디까지 구현되어 있는지 확인하고, 추가로 필요한 부분을 검토한 결과를 정리한 것이다.

1. OHLCV 데이터를 DB에 수집/저장하는 기능
2. 기업 재무제표를 로드해서 DB에 저장하는 기능

기준은 현재 워크스페이스 코드다.

---

## 결론 요약

짧게 말하면:

- **OHLCV 데이터를 DB에 저장하는 기능은 구현되어 있다.**
- **기업 재무제표를 DB에 저장하는 기능도 구현되어 있다.**
- 다만 둘 다 아직 “기본 적재 기능”은 갖췄지만, 운영 완성도 관점에서는 추가해야 할 부분이 꽤 있다.

즉, 현재 상태는:

- 데이터 적재 함수는 존재함
- DB 스키마도 존재함
- UPSERT도 존재함
- 하지만 운영 파이프라인, point-in-time 정합성, 증분 수집, 검증, DB 기반 전략 연결은 아직 더 보강이 필요함

---

## 1. OHLCV DB 적재 기능 구현 여부

## 구현 여부
구현되어 있다.

핵심 함수:
- `finance/data/data.py`
  - `get_ohlcv(...)`
  - `store_ohlcv_to_mysql(...)`
  - `load_ohlcv_many_mysql(...)`

관련 스키마:
- `finance/data/db/schema.py`
  - `PRICE_SCHEMAS["price_history"]`
  - 테이블명: `finance_price.nyse_price_history`

### 현재 구현된 것

`store_ohlcv_to_mysql(...)`는 아래 기능을 수행한다.

- 입력 심볼 리스트 정리
- yfinance로 OHLCV 다운로드
- 배치 단위 수집
- `nyse_price_history` 테이블 생성
- `INSERT ... ON DUPLICATE KEY UPDATE` 기반 UPSERT
- `open`, `high`, `low`, `close`, `adj_close`, `volume`
- `dividends`, `stock_splits`
- 배치 sleep + jitter

`load_ohlcv_many_mysql(...)`는 아래를 지원한다.

- 심볼 리스트 기준 조회
- `start`, `end`, `timeframe` 필터
- 심볼 단위 정렬된 가격 이력 반환

### 현재 테이블 수준에서 저장되는 데이터

저장 테이블:
- DB: `finance_price`
- 테이블: `nyse_price_history`

주요 컬럼:
- `symbol`
- `timeframe`
- `date`
- `open`
- `high`
- `low`
- `close`
- `adj_close`
- `volume`
- `dividends`
- `stock_splits`

즉, 기본적인 가격 백테스트에 필요한 시계열 원장은 이미 있다.

---

## 2. 재무제표 DB 적재 기능 구현 여부

재무제표는 현재 두 층으로 나뉘어 구현되어 있다.

1. 요약형 재무 스냅샷 적재
2. 상세 재무제표 라벨/값 적재

이 둘은 성격이 다르다.

---

## 2-1. 요약형 재무 스냅샷 적재

## 구현 여부
구현되어 있다.

핵심 함수:
- `finance/data/fundamentals.py`
  - `upsert_fundamentals(...)`

관련 스키마:
- `finance/data/db/schema.py`
  - `FUNDAMENTAL_SCHEMAS["fundamentals"]`
  - 테이블명: `finance_fundamental.nyse_fundamentals`

### 현재 구현된 것

`upsert_fundamentals(...)`는 아래를 수행한다.

- 심볼 리스트 입력
- yfinance 재무제표 로드
- 손익/재무상태표/현금흐름표 결합
- 필수 항목 정규화
- 일부 계정 fallback 계산
- DB 테이블 생성 및 schema sync
- UPSERT 저장
- 배치 처리, retry, logging

### 현재 저장되는 핵심 항목

- `total_revenue`
- `gross_profit`
- `operating_income`
- `ebit`
- `net_income`
- `total_assets`
- `current_assets`
- `total_liabilities`
- `current_liabilities`
- `total_debt`
- `net_assets`
- `operating_cash_flow`
- `free_cash_flow`
- `capital_expenditure`
- `cash_and_equivalents`
- `dividends_paid`
- `shares_outstanding`

즉, “팩터 계산이나 기본 재무 스크리닝에 바로 쓸 수 있는 요약 재무 데이터”는 이미 적재 가능하다.

---

## 2-2. 상세 재무제표 적재

## 구현 여부
구현되어 있다.

핵심 함수:
- `finance/data/financial_statements.py`
  - `get_fundamental(...)`
  - `upsert_financial_statements(...)`

관련 스키마:
- `FUNDAMENTAL_SCHEMAS["financial_statement_values"]`
- `FUNDAMENTAL_SCHEMAS["financial_statement_labels"]`

저장 테이블:
- `finance_fundamental.nyse_financial_statement_values`
- `finance_fundamental.nyse_financial_statement_labels`

### 현재 구현된 것

`upsert_financial_statements(...)`는 아래를 수행한다.

- EDGAR 기반 재무제표 로드
- wide 형식 재무제표를 long 형식 rows로 변환
- 라벨 메타와 실제 값 분리 저장
- `filing_date`, `accepted_at` 저장
- 배치 처리, retry, logging
- 실패 심볼 리스트 반환

### 현재 저장되는 데이터 의미

`nyse_financial_statement_values`
- 실제 재무제표 값 저장
- 라벨 단위 long format

`nyse_financial_statement_labels`
- 라벨명
- 한글 라벨
- statement type
- confidence
- 관리용 메타

즉, 이 프로젝트는 단순히 “요약 재무값”만이 아니라, 상세 재무 계정 수준까지 저장할 수 있는 구조를 이미 갖고 있다.

---

## 3. 관련 추가 구현 상태

## 3-1. 팩터 적재

이건 질문의 직접 대상은 아니지만 현재 구조를 이해하려면 중요하다.

핵심 함수:
- `finance/data/factors.py`
  - `upsert_factors(...)`

현재 구현:
- `nyse_fundamentals`를 읽음
- `nyse_price_history`에서 가격을 불러옴
- `period_end` 기준 직전 거래일 가격을 asof로 붙임
- valuation/profitability/growth 계열 팩터 계산
- `finance_fundamental.nyse_factors`에 저장

즉, 현재 구조는 이미:

1. 가격 적재
2. 재무 적재
3. 팩터 계산 적재

까지 이어지는 형태다.

---

## 3-2. 샘플 연결 상태

`finance/sample.py`를 보면:

- `fundamentals_sample(...)`는 존재한다
- 이 함수는:
  - `load_symbols_from_asset_profile("stock", on_filter=True)`
  - `upsert_fundamentals(...)`
  - `upsert_factors(...)`

를 실행한다.

즉, 요약형 재무 스냅샷과 팩터 적재에는 샘플 경로가 있다.

반면:
- `upsert_financial_statements(...)`를 직접 호출하는 샘플 함수는 현재 없다

즉, 상세 재무제표 적재는 구현돼 있지만, 프로젝트 사용 흐름상 노출은 덜 된 상태다.

---

## 4. 현재 구현이 “완료”라고 보기 어려운 이유

기능 존재 여부로는 구현되어 있다.

하지만 운영이나 연구 인프라 관점에서는 아래가 아직 부족하다.

---

## 4-1. OHLCV 적재 쪽 추가 필요 사항

### A. `end` 파라미터 처리 개선
`store_ohlcv_to_mysql(...)`는 시그니처에 `end`가 있지만, 실제 `get_ohlcv(...)`는 `end`를 받지 않는다.

즉:
- 인터페이스는 `start/end`를 암시하지만
- 실제 구현은 `start` 중심이다

이 부분은 보완이 필요하다.

### B. 증분 수집 전략 부재
현재는 “마지막 저장 날짜 이후만 추가 적재”하는 전용 로직이 없다.

추가되면 좋은 것:
- 심볼별 최근 저장 일자 조회
- 최근 N일만 재수집
- 누락 구간만 보충

### C. DB 기반 백테스트 연결 부족
가격 적재 함수는 있지만, 전략 샘플은 대부분 `yfinance` 직로딩을 사용한다.

즉:
- 저장은 가능
- 하지만 전략 실행의 기본 입력은 아직 DB로 통일되지 않음

### D. 데이터 품질 점검 부재
추가되면 좋은 것:
- 중복 date 검증
- 비정상 volume/price 검증
- 배당/분할 반영 확인
- 심볼별 적재 범위 요약

---

## 4-2. 재무제표 적재 쪽 추가 필요 사항

### A. point-in-time 사용 규칙 정리 필요
요약형 `upsert_fundamentals(...)`는 기본적으로 `period_end` 중심이다.

문제:
- 실제 공시 이전 시점에 이 값을 전략에 쓰면 look-ahead bias 위험이 있다

상세 재무제표 쪽은 `filing_date`, `accepted_at`를 저장하지만,
현재 이 정보가 factors/backtest 파이프라인에 강하게 연결되어 있진 않다.

### B. 상세 재무제표 샘플/운영 진입점 부족
`upsert_financial_statements(...)`는 구현돼 있지만:
- `sample.py`에 직접 샘플이 없음
- 일반 사용 흐름에서 상대적으로 덜 드러남

즉, 구현은 됐지만 운영 루트는 약하다.

### C. 라벨 표준화 고도화 필요
상세 재무제표는 라벨 단위라 강력하지만,
기업별/기간별 라벨 변형이 존재할 수 있다.

추가되면 좋은 것:
- 핵심 라벨 canonical mapping
- statement_type별 라벨 관리 전략
- factor 생성 시 라벨 우선순위 규칙 강화

### D. 재무 적재 검증 리포트 부재
추가되면 좋은 것:
- 심볼별 최근 적재 성공 여부
- 빈 statements 비율
- 주요 계정 coverage
- annual/quarterly coverage 차이

---

## 4-3. 공통적으로 추가되면 좋은 부분

### A. orchestration 계층
현재는 함수는 있지만, “전체 적재 작업을 어떤 순서로 돌릴지”를 관리하는 명시적 job 레이어가 약하다.

예:
- universe sync
- asset profile sync
- OHLCV sync
- fundamentals sync
- financial statements sync
- factors sync

를 하나의 파이프라인으로 묶는 운영 루틴이 아직 명확하지 않다.

### B. 설정 관리
여러 함수에 아래 기본값이 반복된다.

- `host="localhost"`
- `user="root"`
- `password="1234"`

이건 추후 환경 분리와 배포에 불리하다.

### C. 테스트/검증 자동화
현재 샘플 함수는 있지만, 자동 검증 체계는 약하다.

추가되면 좋은 것:
- 테이블 생성 smoke test
- ingestion dry-run test
- factor 계산 검증 test
- point-in-time rule check

### D. 운영 요약 리포트
적재 후 결과를 한 번에 확인할 수 있는 요약이 있으면 좋다.

예:
- 몇 개 심볼 성공
- 몇 개 실패
- 어떤 테이블에 몇 행 업데이트
- 최근 적재 시각

---

## 5. 현재 기준 판단

사용자의 현재 이해:

> OHLCV 데이터를 DB에 수집하는 기능과, 각 기업들의 재무제표를 로드해서 DB에 저장하는 기능은 구현되어 있는가?

이 질문에 대한 답은:

### 맞다

더 정확히 말하면:

- OHLCV 적재: 구현되어 있음
- 요약형 재무 스냅샷 적재: 구현되어 있음
- 상세 재무제표 적재: 구현되어 있음
- 팩터 적재: 구현되어 있음

다만 아래는 아직 “추가 보강 필요” 상태다.

- 증분 적재 전략
- point-in-time 정합성 강화
- DB 기반 백테스트 연결
- 운영 오케스트레이션
- 데이터 품질 검증
- 테스트 자동화

---

## 6. 지금 시점에서 추천하는 다음 우선순위

실제로 다음 작업을 정한다면 아래 순서를 권장한다.

### 1순위
OHLCV 적재 경로를 운영 가능하게 보강

구체적으로:
- `end` 파라미터 정리
- 증분 적재 로직 추가
- 적재 결과 요약 리포트 추가

### 2순위
재무 적재의 point-in-time 기준 정리

구체적으로:
- 어떤 테이블이 `period_end` 기준인지
- 어떤 테이블이 `filing_date`/`accepted_at` 기준인지
- 팩터/전략에서 어떤 기준을 사용할지 명확화

### 3순위
DB 기반 리서치 입력 경로 추가

구체적으로:
- 백테스트가 yfinance 직로딩뿐 아니라 DB 로딩도 쉽게 쓰도록 경로 추가

### 4순위
상세 재무제표 적재 샘플 및 검증 루틴 추가

---

## 7. 최종 한 줄 결론

현재 프로젝트는 이미 “가격 적재”와 “재무제표 적재” 기능을 갖추고 있다.

하지만 지금 필요한 다음 단계는 “새 적재 기능을 만드는 것”보다는,
"이미 있는 적재 기능을 운영 가능하고 연구 친화적으로 연결하는 것"에 더 가깝다.
