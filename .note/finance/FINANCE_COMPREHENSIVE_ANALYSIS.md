# Finance Comprehensive Analysis

## 문서 목적
이 문서는 아래 기존 문서들을 종합한 `finance` 패키지의 상세 분석 문서다.

- `finance/docs/FINANCE_PACKAGE_ANALYSIS.md`
- `finance/docs/FINANCE_DB_DATA_AUDIT.md`
- 현재 워크스페이스의 실제 코드

이 문서는 이후 대화에서 `finance` 패키지의 현재 상태를 이해하는 기준 문서로 사용하기 위한 것이다.

- 범위 포함: `finance` 패키지 전체
- 범위 제외: `financial_advisor`
- 기준 시점: 2026-03-11

---

## 1. 전체 요약

현재 `finance` 패키지는 하나의 단일 라이브러리라기보다 아래 두 축이 함께 들어 있는 초기 단계 퀀트 리서치 시스템에 가깝다.

1. 데이터 인프라 축
   - NYSE 유니버스 수집
   - 자산 메타데이터 수집
   - 가격/재무/팩터 DB 적재
   - 상세 재무제표 라벨/값 수집
2. 전략 리서치 축
   - 시계열 전처리
   - 전략 시뮬레이션
   - 성과 분석 및 시각화

즉, 이 패키지는 "데이터 수집기"와 "백테스트 프레임워크"가 같은 패키지 안에 공존하는 구조다.

---

## 2. 기존 문서와 이번 종합 문서의 관계

### `FINANCE_PACKAGE_ANALYSIS.md`가 다루는 것
- 패키지 레이어 구조
- 각 스크립트의 역할
- 전략/엔진/변환 흐름

### `FINANCE_DB_DATA_AUDIT.md`가 다루는 것
- 어떤 DB와 테이블이 생성되는지
- 어떤 데이터가 실제로 수집/적재되는지
- 퀀트 관점에서 어떤 데이터가 추가로 필요한지

### 이번 문서가 추가로 다루는 것
- 코드 기준으로 재검증한 실제 구조
- 패키지의 중심 인터페이스와 실행 순서
- 데이터 흐름과 DB 흐름의 연결 구조
- 현재 설계의 강점, 리스크, 구조적 갭
- 향후 리팩터링과 확장 우선순위

---

## 3. 패키지의 실질적 아키텍처

현재 구조를 가장 자연스럽게 표현하면 아래와 같다.

```text
외부 데이터 소스
  - yfinance
  - NYSE 웹페이지
  - EDGAR

      |
      v

Data Collection / Persistence
  - finance/data/*
  - MySQL

      |
      v

Loader / Runtime Read Path
  - finance/loaders/*

      |
      v

Research / Backtest Processing
  - finance/transform.py
  - finance/engine.py
  - finance/strategy.py

      |
      v

Analysis / Presentation
  - finance/performance.py
  - finance/display.py
  - finance/visualize.py
```

이 구조는 레이어 분리가 완전히 나쁘지 않다. 다만 중요한 점은 현재 **데이터 적재 파이프라인과 전략 파이프라인이 부분적으로만 연결돼 있다**는 것이다.

예를 들어:

- 가격/재무/팩터는 DB 적재 경로가 존재한다.
- 그리고 이제 `finance/loaders/*`와 `*_from_db` 샘플 entrypoint를 통해 DB 기반 실행 경로도 생겼다.
- 최근에는 DB 기반 sample 경로가 direct path와 같은 indicator warmup 순서를 따르도록 보강되었다.

즉, 예전보다 통합은 많이 진행됐지만 아직 모든 전략과 모든 입력이 loader 계층으로 완전히 이행된 상태는 아니다.

---

## 4. 상위 디렉터리 기준 파일 역할

## 4-1. 핵심 실행 계층

### `finance/loaders/*`
Phase 3에서 추가된 조회 계층이다.

역할:
- DB 적재 데이터 조회
- loader 계약 기준 입력 정규화
- broad research loader와 strict PIT loader 분리의 기반 제공
- 기존 전략 계층과 DB 사이의 read path 담당

현재 구현된 것:
- `load_universe`
- `load_price_history`
- `load_price_matrix`
- `load_fundamentals`
- `load_fundamental_snapshot`
- `load_factors`
- `load_factor_snapshot`
- `load_factor_matrix`
- `load_statement_values`
- `load_statement_labels`
- `load_statement_snapshot_strict`
- runtime adapter 계열

### `finance/engine.py`
`BacktestEngine`이 패키지의 전략 실행 중심 인터페이스다.

역할:
- 티커 집합과 기간 옵션을 받는다.
- OHLCV 로드
- 전처리 함수 체이닝
- 전략 실행
- 표시용 반올림

현재 사용 패턴은 아래와 같다.

```python
engine = (
    BacktestEngine(tickers, period=..., option=...)
    .load_ohlcv()
    .add_ma(...)
    .filter_by_period()
    .align_dates()
    .slice(...)
    .run(strategy)
    .round_columns()
)
```

의미:
- 기존 외부 직접조회 기반 실행과
  DB 기반 loader 실행을 같은 체이닝 인터페이스 안에서 관리한다.
- `load_ohlcv_from_db(...)`는 `history_start`를 받아
  지표 warmup용 과거 이력을 먼저 읽고 마지막에 실제 start/end를 자르는 흐름도 지원한다.
- `engine.py`는 계산 엔진 자체라기보다 orchestration wrapper다.
- 실질 계산은 대부분 `data.py`, `transform.py`, `strategy.py`에 있다.

### `finance/strategy.py`
전략 로직이 모여 있는 핵심 파일이다.

현재 구현 전략:
- `equal_weight`
- `gtaa3`
- `risk_parity_trend`
- `dual_momentum`

특징:
- 모든 전략이 event-driven 주문 엔진보다는 "시점별 포트폴리오 상태 계산" 방식이다.
- 결과는 체결 로그가 아니라 시점별 상태 테이블이다.
- 각 전략 결과 스키마가 완전히 통일되지는 않았다.

### `finance/transform.py`
순수 전처리 함수 집합이다.

가장 중요한 점:
- 입력 형태를 `{ticker: DataFrame}`로 통일하고 있다.
- 전략 이전 단계에서 데이터 길이를 줄이는 함수가 여러 개 있다.

예:
- `add_ma`: 가장 긴 이동평균이 없는 초반 구간 제거
- `add_interval_returns`: 가장 긴 구간 수익률이 없는 초반 구간 제거
- `align_dfs_by_date_intersection`: 모든 티커 공통 날짜만 유지

이 때문에 실제 전략 입력 데이터는 원본보다 훨씬 짧아질 수 있다.

### `finance/performance.py`
성과 요약 계층이다.

핵심 함수:
- `portfolio_performance_summary`
- `make_monthly_weighted_portfolio`

중요한 가정:
- 입력 DataFrame에 최소한 `Date`, `Total Balance`, `Total Return`이 있어야 한다.

### `finance/display.py`
결과를 보기 좋게 만드는 후처리 계층이다.

특징:
- list 컬럼과 ndarray 컬럼까지 반올림 가능
- 현재 전략 결과 포맷과 잘 맞게 설계돼 있다

### `finance/visualize.py`
Matplotlib 시각화 계층이다.

특징:
- 리서치/노트북 사용을 염두에 둔 단순한 플로팅 함수
- macOS 한글 폰트 설정이 코드에 포함됨

### `finance/sample.py`
예제 파일이지만 실질적으로는 수동 통합 테스트 역할도 한다.

함수군:
- 전략 실행 샘플
- DB 기반 전략 실행 샘플 (`*_from_db`)
- 자산 프로필 적재 샘플
- fundamentals/factors 적재 샘플

즉, 사용 예제이면서 현재 프로젝트의 "실행 가이드" 역할도 같이 한다.

추가 메모:
- DB 기반 sample 함수들은 indicator warmup이 필요한 전략에 대해
  실제 `start`보다 더 앞선 이력을 먼저 읽고,
  마지막에 `slice(start=...)`를 적용하는 구조로 정리되었다.

---

## 4-2. 데이터 수집 계층

### `finance/data/data.py`
가격 데이터 경계 모듈이다.

핵심 기능:
- `get_ohlcv`
  - yfinance OHLCV를 `{ticker: DataFrame}`로 변환
- `get_fx_rate`
  - 환율 조회
- `store_ohlcv_to_mysql`
  - 가격 데이터 DB 적재
- `load_ohlcv_many_mysql`
  - DB에서 가격 이력 조회

이 파일의 의미:
- 시장 데이터와 시스템 내부 표현 사이의 첫 번째 boundary
- 최근에는 canonical refresh 관점에서:
  - blank OHLCV row를 적재하지 않도록 보강되었고
  - 요청 구간의 기존 row를 지우고 다시 적재하는 경로를 지원하며
  - `end`를 inclusive semantics로 보정해 direct provider path와 DB path의 일관성을 맞추고 있다
- 가격 데이터만 놓고 보면 현재 가장 기본적인 source adapter 역할

### `finance/data/nyse.py`
NYSE 상장 종목 목록 수집기다.

기술 방식:
- Selenium
- BeautifulSoup

산출물:
- `csv/nyse_stock.csv`
- `csv/nyse_etf.csv`

의미:
- 전체 유니버스 구축의 출발점
- 현재는 API 기반이 아니라 웹 크롤링 기반

### `finance/data/nyse_db.py`
NYSE CSV를 DB로 올리는 로더다.

역할:
- CSV 읽기
- 테이블 생성
- UPSERT

즉, `nyse.py`와 짝을 이루는 ETL의 load 단계다.

### `finance/data/asset_profile.py`
심볼별 메타데이터 수집기다.

수집 데이터:
- 이름
- quote type
- exchange
- sector
- industry
- country
- market_cap
- dividend_yield
- payout_ratio
- status
- is_spac

이 파일이 중요한 이유:
- 이후 유니버스 필터링의 기준이 된다.
- `load_symbols_from_asset_profile()`를 통해 종목군을 선별한다.

현재 기본 필터:
- SPAC 제외
- 중국 종목 제외
- delisted 추정 제외

즉, 단순 메타 저장이 아니라 "전략용 유니버스 정제"의 시작점이다.

### `finance/data/fundamentals.py`
재무 스냅샷 정규화 모듈이다.

핵심 목적:
- yfinance 원시 재무제표에서 백테스트용 최소 필수 항목만 안정적으로 추출

특징:
- 계정명이 직접 존재하지 않을 때 fallback 계산 로직이 들어 있다.
- 예:
  - gross profit 보정
  - operating income 보정
  - EBIT 보정
  - shares outstanding 근사치 계산

즉, 단순 수집이 아니라 **정규화와 보정**을 수행한다.

### `finance/data/factors.py`
재무 팩터 계산 모듈이다.

입력:
- `nyse_fundamentals`
- 가격 DB의 종가

핵심 처리:
- `period_end` 기준 직전 거래일 가격 매칭
- market cap 계산
- enterprise value 계산
- valuation/profitability/growth 팩터 계산

이 파일의 의미:
- 이 프로젝트가 단순 가격 백테스트를 넘어 팩터 전략으로 확장될 수 있게 하는 핵심 중간 계층

### `finance/data/financial_statements.py`
상세 재무제표 저장용 모듈이다.

특징:
- EDGAR 사용
- 라벨 메타와 값 테이블을 분리 저장
- 한글 라벨 매핑 지원

의미:
- `fundamentals.py`가 "요약 스냅샷"이라면,
- `financial_statements.py`는 "세부 계정 원장"에 가깝다.

이 모듈이 있으면 장기적으로 커스텀 팩터를 훨씬 풍부하게 만들 수 있다.

### `finance/data/data_format.py`
실행 모듈이 아니라 참조성 문서 모듈이다.

역할:
- yfinance `ticker.info` 구조 예시 정리

실질 의미:
- 스키마 설계나 필드 탐색에 도움을 주는 reference file

---

## 4-3. DB 계층

### `finance/data/db/mysql.py`
아주 얇은 MySQL 래퍼다.

제공 기능:
- `execute`
- `executemany`
- `query`
- `use_db`
- `close`

의미:
- ORM이 아니라 직접 SQL 중심 운영
- 구조가 단순해 현재 단계에서는 이해하기 쉽다

### `finance/data/db/schema.py`
스키마 정의와 자동 동기화의 중심이다.

중요 기능:
- `NYSE_SCHEMAS`
- `PRICE_SCHEMAS`
- `FUNDAMENTAL_SCHEMAS`
- `sync_table_schema`

`sync_table_schema`의 의미:
- 코드에 새 컬럼이 추가되면 기존 테이블에 자동으로 컬럼을 더한다
- 초기 단계 프로젝트에서 스키마 진화를 쉽게 만들어 준다

한계:
- 컬럼 추가 중심이지, 컬럼 변경/삭제/인덱스 재설계까지 안전하게 다루는 정식 migration 시스템은 아니다

---

## 5. 현재 데이터 흐름

## 5-1. 유니버스 구축 흐름

```text
NYSE 웹페이지
  -> load_nyse_listings()
  -> csv/nyse_stock.csv, csv/nyse_etf.csv
  -> load_nyse_csv_to_mysql()
  -> finance_meta.nyse_stock / finance_meta.nyse_etf
  -> collect_and_store_asset_profiles()
  -> finance_meta.nyse_asset_profile
```

의미:
- 유니버스 데이터는 "크롤링 -> CSV -> DB -> 프로파일 보강" 순서다.

## 5-2. 가격 데이터 흐름

```text
yfinance
  -> get_ohlcv()
  -> 백테스트 직접 사용

또는

yfinance
  -> store_ohlcv_to_mysql()
  -> finance_price.nyse_price_history
  -> load_ohlcv_many_mysql()
```

의미:
- 가격은 "직접 사용 경로"와 "DB 적재 경로"가 둘 다 존재한다.
- 이 이중 경로는 유연하지만, 장기적으로는 소스 일관성 문제를 만들 수 있다.

## 5-3. 재무/팩터 흐름

```text
yfinance statements
  -> upsert_fundamentals()
  -> finance_fundamental.nyse_fundamentals
  -> upsert_factors()
  -> finance_fundamental.nyse_factors
```

중요 포인트:
- 팩터 계산은 fundamentals가 먼저 채워져 있어야 한다.
- 가격 DB도 준비돼 있어야 한다.

즉, `nyse_factors`는 독립 수집 테이블이 아니라 파생 테이블이다.

## 5-4. 상세 재무제표 흐름

```text
EDGAR
  -> get_fundamental()
  -> _iter_label_rows()
  -> _iter_value_rows()
  -> upsert_financial_statements()
  -> labels / values 테이블
```

의미:
- detailed statement 계층은 향후 커스텀 팩터 엔진의 원재료가 될 수 있다.

---

## 6. DB 구조 요약

## 6-1. DB 목록

- `finance_meta`
- `finance_price`
- `finance_fundamental`

## 6-2. 테이블 목록

### `finance_meta`
- `nyse_stock`
- `nyse_etf`
- `nyse_asset_profile`

### `finance_price`
- `nyse_price_history`

### `finance_fundamental`
- `nyse_fundamentals`
- `nyse_factors`
- `nyse_financial_statement_filings`
- `nyse_financial_statement_values`
- `nyse_financial_statement_labels`

---

## 7. 테이블별 역할과 데이터 성격

### `nyse_stock`, `nyse_etf`
역할:
- 전체 유니버스의 출발점

성격:
- 마스터 심볼 목록
- 상대적으로 정적 데이터

### `nyse_asset_profile`
역할:
- 유니버스 필터링
- 섹터/산업/국가 기반 분류
- 운영 상태 추적

성격:
- 반정적 메타데이터
- 정제된 심볼 집합 생성에 직접 사용됨

### `nyse_price_history`
역할:
- 가격 기반 백테스트의 핵심 원장

성격:
- 시계열 원천 데이터
- OHLCV + 배당 + 분할 포함
- stock과 ETF를 함께 저장하는 공용 price fact table
- 자산 종류 구분은 별도 meta 테이블(`nyse_stock`, `nyse_etf`, `nyse_asset_profile`)에서 해석

### `nyse_fundamentals`
역할:
- 핵심 재무 스냅샷 저장

성격:
- 요약형 재무 테이블
- 백테스트용 최소 필수 지표 중심

### `nyse_factors`
역할:
- 파생 팩터 저장

성격:
- 계산 결과 테이블
- 전략 입력 후보 테이블

### `nyse_financial_statement_filings`
역할:
- filing 단위 공시 메타 저장

성격:
- human-inspectable filing ledger
- `accession_no`, `filing_date`, `accepted_at`, `available_at`, `report_date` 중심

### `nyse_financial_statement_values`
역할:
- filing / concept / period 단위 상세 재무 계정 저장

성격:
- long-format raw fact ledger
- 실제 `period_end`와 공시 가능 시점을 함께 보존
- strict raw ledger 방향으로 정리 중
- `accession_no`, `unit`, `available_at`를 갖는 row를 PIT-friendly raw row로 우선 취급
- 확장형 팩터 생성에 적합

### `nyse_financial_statement_labels`
역할:
- 재무 계정 concept 요약 메타 저장

성격:
- operator-facing summary 계층
- `symbol + statement_type + concept + as_of` 기준의 concept summary
- strict loader의 source of truth가 아니라 UI/해석 보조 계층

---

## 8. 현재 전략 레이어의 성격

현재 전략들은 전반적으로 ETF/자산배분형 전략에 더 가깝다.

샘플 기준:
- 배당 ETF 묶음
- 글로벌 자산배분
- 듀얼 모멘텀
- 리스크 패리티

즉, 개별 종목 selection 엔진보다는 "소수 자산군 로테이션/배분" 성격이 강하다.

이건 데이터 인프라가 향하는 방향과 약간 차이가 있다.

왜냐하면 데이터 인프라는:
- NYSE 전체 유니버스
- 주식 프로파일
- 재무/팩터
- 상세 재무제표

까지 수집하고 있어서, 장기적으로는 **주식 단면(cross-sectional) 팩터 전략** 쪽으로 확장할 준비가 되어 있기 때문이다.

즉, 현재 상태는 다음과 같이 볼 수 있다.

- 전략: ETF 중심 리서치
- 데이터: 주식 팩터 연구까지 고려한 인프라

이 구조는 나쁘지 않지만, 두 축의 연결은 아직 초기 단계다.

---

## 9. 강점 분석

## 9-1. 역할 분리가 비교적 명확하다
- 수집
- 변환
- 전략
- 성과/표현

의 층이 분명하다.

특히 `transform.py`와 `strategy.py`가 분리되어 있어 전략 실험이 쉬운 편이다.

## 9-2. DB 적재 계층이 이미 꽤 실용적이다
- UPSERT 기반
- 스키마 자동 동기화
- 배치 처리
- 재시도
- 로그 파일 저장

초기 프로젝트치고는 운영 감각이 들어가 있다.

## 9-3. 재무 데이터 계층이 단순하지 않다
- fundamentals 요약 계층
- detailed financial statements 계층
- factors 파생 계층

의 3단 구조가 있다.

이건 향후 팩터 연구에 유리하다.

## 9-4. 전략 API가 간단하다
`BacktestEngine(...).<transform>().run(strategy)` 패턴은 이해하기 쉽다.

즉, 새로운 전략을 붙이기도 나쁘지 않다.

---

## 10. 현재 구조의 핵심 한계

## 10-1. DB 기반 데이터 파이프라인과 전략 파이프라인이 분리돼 있다
현재 전략 샘플은 대부분 DB가 아닌 `yfinance` 직로딩을 사용한다.

영향:
- 재현성 저하
- 데이터 버전 관리 어려움
- 동일 전략이라도 실행 시점에 따라 데이터 차이 가능

장기적으로는 아래 중 하나로 정리해야 한다.

1. 백테스트 입력을 DB 기준으로 통일
2. 또는 실험용/운영용 경로를 명시적으로 분리

## 10-2. 포인트인타임 공시 시점 통제가 아직 약하다
`nyse_fundamentals`는 기본적으로 `period_end` 중심이다.

문제:
- 백테스트에서 실제 공시 이전 시점에 해당 재무값을 사용하면 룩어헤드 바이어스가 생긴다.

상세 재무제표 쪽은 2026-03-18 기준으로
- `nyse_financial_statement_filings`
- `nyse_financial_statement_values`
- `nyse_financial_statement_labels`

에 `filing_date`, `accepted_at`, `available_at`, `accession_no`, `report_date`를 저장한다.

즉 raw ledger 차원에서는 point-in-time 기반 snapshot을 만들 수 있는 기반이 생겼다.
다만 현재 한계는 여전히 남아 있다.

- 전략/팩터 계층이 이 availability 규칙을 아직 직접 재사용하지 않는다
- `nyse_fundamentals`, `nyse_factors`는 여전히 별도 강화가 필요하다
- quarterly raw ledger는 provider truth를 보존하는 방향이라 Q4를 DB에서 합성하지 않는다
- `nyse_financial_statement_values`는 strict raw ledger 방향으로 재정의되었고,
  old mixed-state row를 PIT source로 곧바로 신뢰하지 않는 방향으로 정리됐다

즉, 실전형 팩터 백테스트로 가려면 이 부분이 매우 중요하다.

## 10-3. 생존편향 제어가 충분하지 않다
현재는 `status`와 일부 휴리스틱 필터가 있지만:
- listing_date
- delisting_date
- symbol change history
- corporate action identity history

가 별도 시계열 테이블로 정리돼 있지 않다.

즉, 현재 유니버스 필터는 유용하지만 완전한 point-in-time universe는 아니다.

## 10-4. 거래비용 모델이 없다
전략 계산은 사실상 frictionless market을 가정한다.

없는 것:
- 수수료
- 슬리피지
- bid/ask spread proxy
- 거래량 제약

ETF 전략에서는 영향이 덜할 수 있지만, 개별 종목 팩터 전략으로 가면 필수다.

## 10-5. 설정값이 코드에 하드코딩돼 있다
여러 모듈에서 아래 기본값이 반복된다.

- host=`localhost`
- user=`root`
- password=`1234`

영향:
- 보안 취약
- 환경 분리 어려움
- 테스트/운영 전환 불편

## 10-6. 패키지 인터페이스가 아직 정리 중이다
- `finance/__init__.py`는 일부만 re-export한다.
- `finance/data`에는 `__init__.py`가 없다.
- public API가 아직 안정적으로 정해진 느낌은 아니다.

즉, 내부 구조는 보이지만 외부 사용 계약은 아직 약하다.

## 10-7. 전략 결과 스키마가 완전히 표준화돼 있지 않다
예:
- 어떤 전략은 `Ticker`
- 어떤 전략은 `End Ticker`, `Next Ticker`
- 어떤 전략은 `Cash`, `Next Weight`

이 차이는 사람이 보기엔 문제없지만, 공통 리포팅/저장/비교 시스템을 만들 때 비용이 생긴다.

---

## 11. 데이터 품질 관점 분석

## 11-1. 가격 데이터
좋은 점:
- OHLCV 외에 배당과 주식분할도 저장함
- stock과 ETF를 동일 price ledger에 넣어 mixed-asset backtest에 바로 연결 가능
- 최근 hardening으로 Daily Market Update가 stock + ETF 공통 수집을 전제로 동작하도록 정리됨
- yfinance batch fetch 경로가 병렬 배치 fetch + retry 기반으로 개선됨

주의점:
- 거래소 세션 정보 없음
- 조정 가격 활용 규칙이 백테스트 전반에서 통일되어 있진 않음
- 현재 전략은 주로 `Close`를 사용함
- 대규모 전 유니버스 refresh는 여전히 외부 provider 속도에 영향을 크게 받음

즉, total return 정확도와 corporate action 처리 정책을 더 명확히 할 필요가 있다.

## 11-2. 프로파일 데이터
좋은 점:
- 유니버스 필터링에 실용적

주의점:
- `status`는 추정치다
- `is_spac`도 휴리스틱이다
- sector/industry/country도 provider 품질에 의존한다

즉, 유용하지만 절대적 ground truth로 보기엔 위험하다.

## 11-3. fundamentals 데이터
좋은 점:
- 백테스트용 최소 항목이 잘 정리돼 있다
- 결측 보정 로직이 있다

주의점:
- 보정값은 근사치다
- shares outstanding도 일부 경우 추정
- source가 yfinance라 계정명/coverage 일관성이 완벽하지 않을 수 있다

즉, 실용성은 높지만 accounting-grade precision은 아니다.

## 11-4. detailed financial statements 데이터
좋은 점:
- filing / concept 단위 세부 정보가 저장된다
- actual `period_end`를 raw fact 기준으로 저장한다
- `filing_date`, `accepted_at`, `available_at`, `accession_no`, `form_type`를 함께 저장한다
- filing 메타를 사람이 직접 확인할 수 있도록 `nyse_financial_statement_filings`가 별도로 존재한다

주의점:
- 라벨 표준화 문제
- 기업별/기간별 라벨 변형
- 같은 개념이 다른 라벨로 나타날 가능성
- provider의 `fiscal_year` / `fiscal_period`는 비교열 fact에서 filing 컨텍스트일 수 있어서,
  row 정체성은 `period_end`와 `accession_no`를 우선 기준으로 봐야 한다
- quarterly 저장은 raw truth 우선이라 10-Q의 비교 balance-sheet row와 10-K 기반 FY row가 함께 보일 수 있고,
  DB 저장 단계에서 synthetic Q4를 만들지 않는다
- `nyse_financial_statement_labels`는 convenience summary로 보는 것이 맞고,
  실제 strict loader는 `values`를 중심으로 읽어야 한다

즉, powerful하지만 정교한 semantic normalization이 뒤따라야 한다.

## 11-5. factors 데이터
좋은 점:
- valuation/profitability/growth를 폭넓게 포함한다

주의점:
- `period_end` 기준 asof 가격 매칭은 유용하지만,
  실제 공시 시점 기반으로는 아닐 수 있다
- point-in-time strictness는 아직 부족하다

---

## 12. 현재 기준으로 가장 중요한 함수들

## 12-1. 데이터 적재
- `finance.data.nyse.load_nyse_listings`
- `finance.data.nyse_db.load_nyse_csv_to_mysql`
- `finance.data.asset_profile.collect_and_store_asset_profiles`
- `finance.data.fundamentals.upsert_fundamentals`
- `finance.data.factors.upsert_factors`
- `finance.data.financial_statements.upsert_financial_statements`

## 12-2. 전략 실행
- `finance.data.data.get_ohlcv`
- `finance.engine.BacktestEngine`
- `finance.strategy.EqualWeightStrategy`
- `finance.strategy.GTAA3Strategy`
- `finance.strategy.RiskParityTrendStrategy`
- `finance.strategy.DualMomentumStrategy`

## 12-3. 성과 요약
- `finance.performance.portfolio_performance_summary`
- `finance.performance.make_monthly_weighted_portfolio`
- `finance.visualize.plot_equity_curves`

---

## 13. 지금 당장 이해해야 하는 핵심 사실

### 사실 1
이 프로젝트는 아직 "전략 백테스트 엔진"보다 "연구용 퀀트 워크벤치"에 더 가깝다.

### 사실 2
데이터 계층은 장기적으로 주식 팩터 전략을 할 준비가 꽤 되어 있다.

### 사실 3
하지만 현재 샘플 전략은 대부분 ETF 자산배분형이다.

### 사실 4
DB 적재 계층은 실제 운영용 파이프라인처럼 보이지만, 전략 계층과 완전 통합되진 않았다.

### 사실 5
향후 고도화에서 가장 중요한 축은 아래 셋이다.

1. point-in-time 데이터 정합성
2. DB 기반 전략 입력 통일
3. 전략 결과 스키마 표준화

---

## 14. 향후 리팩터링 우선순위 제안

## 14-1. 1순위
백테스트 입력 데이터 소스를 통일한다.

권장 방향:
- 실험용: yfinance 직로딩
- 운영용: DB 로딩

둘을 명시적으로 분리하거나, 가능하면 DB 기준으로 수렴시키는 것이 좋다.

## 14-2. 2순위
공시 시점 기반 팩터 파이프라인을 만든다.

필요한 연결:
- `financial_statements.py`의 `filing_date`, `accepted_at`, `available_at`
- `factors.py`의 계산 기준 시점
- 백테스트 리밸런싱 시점

## 14-3. 3순위
전략 결과 공통 스키마를 정의한다.

예:
- `Date`
- `Holdings`
- `Weights`
- `Cash`
- `Total Balance`
- `Total Return`
- `Rebalancing`

## 14-4. 4순위
설정 관리 계층을 만든다.

대상:
- DB 연결
- batch size
- sleep
- retry
- 로그 경로

## 14-5. 5순위
리서치용 샘플과 운영 파이프라인을 분리한다.

예:
- `sample.py`는 examples로 이동
- ingestion jobs는 별도 jobs/module화

---

## 15. 퀀트 관점에서 추가되면 좋은 데이터

이미 기존 감사 문서에서 제안된 항목을 현재 코드 맥락으로 다시 정리하면 아래가 핵심이다.

## 15-1. 매우 중요
- filing/accepted 시점 기반 point-in-time 재무 데이터
- listing/delisting/symbol change history
- benchmark 및 risk-free rate 시계열
- 거래비용 근사용 유동성 데이터

## 15-2. 중요
- 섹터/산업 분류 이력
- index membership history
- 배당 이벤트 상세 이력
- ETF 전용 메타 확장

## 15-3. 고급 확장
- analyst estimates / surprise
- short interest / borrow fee
- options implied volatility

---

## 16. 현재 패키지를 한 문장으로 정의하면

현재 `finance` 패키지는:

"NYSE 유니버스, 가격, 재무, 팩터 데이터를 수집·저장하면서 동시에 ETF/자산배분형 전략을 빠르게 연구할 수 있게 만든 초기 단계 퀀트 리서치 패키지"

라고 정의하는 것이 가장 정확하다.

---

## 17. 이후 대화에서 이 문서를 어떻게 사용할지

이후 `finance` 관련 질문에서는 이 문서를 기준으로 아래 순서로 이해하면 된다.

1. 지금 묻는 내용이 데이터 적재 문제인지 전략 문제인지 먼저 구분
2. 데이터 적재면 어느 DB/테이블에 해당하는지 확인
3. 전략 문제면 `engine -> transform -> strategy -> performance` 순서로 본다
4. 팩터 문제면 `fundamentals -> factors -> point-in-time 이슈`를 같이 본다

즉, 이 문서는 단순 설명 문서가 아니라 이후 분석과 설계 대화의 기준 좌표다.
