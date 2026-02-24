# quant-data-pipeline `finance` 패키지 분석

## 1. 패키지 전체 역할 요약
`finance`는 **퀀트 백테스트 파이프라인**을 구성하는 패키지로, 크게 아래 4개 레이어로 동작합니다.

- 데이터 수집/저장 레이어: `finance/data/*`
  - yfinance, EDGAR, NYSE 웹 페이지에서 원천 데이터 수집
  - MySQL 스키마 생성/동기화 및 UPSERT
- 데이터 변환 레이어: `finance/transform.py`
  - 이동평균, 구간 수익률, 기간 필터링, 날짜 정렬 등 순수 변환
- 전략/엔진 레이어: `finance/strategy.py`, `finance/engine.py`
  - 전략 로직(리밸런싱/모멘텀/리스크패리티) 실행
  - 체이닝 방식으로 백테스트 파이프라인 조합
- 성과/표현 레이어: `finance/performance.py`, `finance/display.py`, `finance/visualize.py`
  - CAGR/Sharpe/MDD 요약, 스타일링, 시각화

## 2. 실행 흐름(핵심)
대표적인 실행 흐름은 아래 순서입니다.

1. `BacktestEngine.load_ohlcv()`로 가격 데이터 적재
2. `add_ma()`, `add_interval_returns()`, `filter_by_period()`, `align_dates()` 등 전처리
3. `run(Strategy)`로 전략 실행
4. `round_columns()`, `portfolio_performance_summary()`, `plot_*()`로 결과 확인

`finance/sample.py`가 이 과정을 미리 조합한 사용 예제를 제공합니다.

## 3. 스크립트별 수행 역할

### 3.1 루트(`finance/*.py`)

#### `finance/__init__.py`
- 외부 사용 진입점 역할.
- 전략 클래스(`EqualWeightStrategy`, `GTAA3Strategy`)와 데이터 모듈(`data`, `nyse`)을 re-export.

#### `finance/engine.py`
- `BacktestEngine` 클래스 제공.
- 체이닝 API로 데이터 적재/전처리/전략실행/출력포맷을 연결.
- 내부적으로 `data.get_ohlcv`, `transform.*`, `display.round_columns`를 조합.

#### `finance/strategy.py`
- 전략 핵심 시뮬레이션 로직.
- 함수 전략:
  - `equal_weight`: 균등 비중 + 주기 리밸런싱
  - `gtaa3`: 모멘텀 점수 상위 자산 + MA 필터
  - `risk_parity_trend`: 1/변동성 가중 + MA 트렌드 필터
  - `dual_momentum`: 상대모멘텀 Top N + 절대모멘텀(MA) + 현금/대체자산
- OO 래퍼 전략 클래스:
  - `Strategy`(추상), `EqualWeightStrategy`, `GTAA3Strategy`, `RiskParityTrendStrategy`, `DualMomentumStrategy`

#### `finance/transform.py`
- 순수 데이터 가공 유틸 모음.
- 주요 기능:
  - 이동평균 추가: `add_ma`
  - 월/년 시작·종료 필터: `filter_ohlcv`, `filter_finance_history`
  - 기간 슬라이싱: `slice_ohlcv`
  - 수익률 계산: `add_returns`, `add_interval_returns`
  - 날짜 교집합 정렬: `align_dfs_by_date_intersection`
  - 외부 DF 병합: `merge_dfs_to_df`
  - 컬럼 삭제/스코어링/간격샘플링: `drop_columns`, `add_avg_score`, `select_rows_by_interval_with_ends`

#### `finance/performance.py`
- 백테스트 결과 성과 지표 계산/합성.
- `portfolio_performance_summary`:
  - Start/End balance, CAGR, 연환산 변동성, Sharpe, MDD 계산
- `make_monthly_weighted_portfolio`:
  - 여러 전략 결과를 월 단위 가중 포트폴리오로 결합
  - `union/intersection` 날짜 정책 및 수익률 계산 방식 선택 가능

#### `finance/display.py`
- 표시용 포맷 함수.
- `round_columns`: scalar/list/ndarray 내부 숫자를 안전 반올림
- `style_returns`: 수익률 컬럼 색상/포맷 적용한 pandas Styler 반환

#### `finance/visualize.py`
- Matplotlib 기반 시각화.
- 단일/복수 전략에 대해 Equity Curve, Drawdown, Returns Bar 표시.
- macOS 한글 폰트(`AppleGothic`) 설정 포함.

#### `finance/sample.py`
- 실제 사용 시나리오 템플릿.
- 전략별 샘플 함수:
  - `get_equal_weight`, `get_gtaa3`, `get_risk_parity_trend`, `get_dual_momentum`
- 통합 데모:
  - `portfolio_sample`: 전략 실행 + 그래프 + 성과표
  - `asset_profiles_sample`, `fundamentals_sample`: 메타/재무 데이터 적재 예시

---

### 3.2 데이터 수집/적재(`finance/data/*.py`)

#### `finance/data/data.py`
- 가격/환율 데이터 경계 모듈.
- `get_ohlcv`: yfinance OHLCV를 `{ticker: DataFrame}` 형태로 변환
- `get_fx_rate`: 환율 시계열 조회
- `store_ohlcv_to_mysql`: 가격 데이터 MySQL UPSERT
- `load_ohlcv_many_mysql`: 심볼 다건 가격 데이터 조회

#### `finance/data/nyse.py`
- Selenium + BeautifulSoup로 NYSE 상장목록 크롤링.
- `load_nyse_listings(kind=stock|etf)`:
  - 페이지네이션 반복 수집
  - CSV(`csv/nyse_{kind}.csv`) 저장

#### `finance/data/nyse_db.py`
- `nyse_stock`/`nyse_etf` CSV를 MySQL로 적재.
- `load_nyse_csv_to_mysql`: 테이블 생성 후 UPSERT

#### `finance/data/asset_profile.py`
- yfinance 기반 자산 프로파일 수집(주식/ETF).
- 핵심:
  - 상태 판단(`active/delisted/not_found/error`)
  - SPAC 휴리스틱 판별
  - 프로파일 UPSERT
- `collect_and_store_asset_profiles`: 배치 수집 + 실패 CSV 기록
- `load_symbols_from_asset_profile`: 필터링된 심볼 목록 조회

#### `finance/data/fundamentals.py`
- yfinance 재무제표를 백테스트용 필수 항목으로 정규화.
- gross profit, operating income, EBIT, shares outstanding 등 결측 보정 로직 내장.
- `upsert_fundamentals`: 배치/재시도/로그 기반으로 `nyse_fundamentals` UPSERT.

#### `finance/data/factors.py`
- fundamentals + 가격 데이터를 결합해 팩터 계산.
- 주요 처리:
  - period_end 시점 종가 asof 매칭
  - market cap / enterprise value 계산
  - 밸류·퀄리티·성장 팩터(PSR, PER, PBR, ROE, 성장률 등) 산출
- `upsert_factors`: `nyse_factors` UPSERT 및 오류 로깅

#### `finance/data/financial_statements.py`
- EDGAR(`edgar` 라이브러리) 기반 재무제표 상세 라벨/값 수집.
- 기능:
  - `get_fundamental`: 손익/재무상태/현금흐름 결합 DF 생성
  - 라벨 한글 매핑(`financial_term_kor_map`) 제공
  - wide → long 변환 후 labels/values 테이블 분리 저장
- `upsert_financial_statements`: 배치/재시도/로그 처리 포함

#### `finance/data/data_format.py`
- yfinance `ticker.info` 표준 필드 예시(ETF/주식) 레퍼런스 사전.
- 수집 로직 실행 모듈이 아니라, **데이터 포맷 문서화/참조용 상수 모듈** 성격.

---

### 3.3 DB 유틸(`finance/data/db/*.py`)

#### `finance/data/db/mysql.py`
- `MySQLClient` 래퍼.
- `execute`, `executemany`, `query`, `use_db`, `close` 제공.

#### `finance/data/db/schema.py`
- 스키마 정의/동기화 중심 모듈.
- 기능:
  - `NYSE_SCHEMAS`, `PRICE_SCHEMAS`, `FUNDAMENTAL_SCHEMAS` 정의
  - `sync_table_schema`: 테이블 컬럼 누락 자동 `ALTER TABLE ADD COLUMN`

#### `finance/data/db/__init__.py`
- 현재 내용 없음(패키지 마커 파일).

## 4. 구조적 관찰 포인트
- 장점:
  - 수집(`data`), 변환(`transform`), 전략(`strategy`), 출력(`display/visualize`)의 역할 분리가 명확함.
  - DB 적재 계층이 UPSERT + 스키마 동기화를 갖춰 운영 친화적.
- 주의 포인트:
  - 일부 함수/모듈에 하드코딩된 DB 접속정보(`root/1234`, `localhost`)가 존재.
  - `data_format.py`는 매우 큰 레퍼런스 상수 파일이라 런타임 의존 최소화가 필요.
  - `sample.py`는 데모 성격이 강해 운영 코드와 분리 관리가 바람직.

## 5. 결론
이 패키지는 **"데이터 수집 → 정규화/전처리 → 전략 백테스트 → 성과/시각화"** 전체를 한 번에 수행하는 소형 퀀트 리서치 프레임워크입니다. 특히 `BacktestEngine` + `Strategy` 조합이 핵심 실행 인터페이스이며, `finance/data` 하위는 이를 위한 데이터 인프라(수집/DB/팩터 계산)를 담당합니다.
