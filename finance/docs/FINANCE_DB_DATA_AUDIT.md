# finance DB 수집 데이터 조사

## 조사 범위
- 코드 기준 범위: `finance/data/*`, `finance/data/db/schema.py`, `finance/sample.py`
- 목적: 현재 `finance` 기능으로 실제 수집/적재되는 DB/테이블과 데이터 성격을 파악하고, 퀀트 백테스트 관점에서 추가 필요 데이터를 제안

---

## 1. 수집되는 DB와 테이블, 그리고 데이터 내용

## 1-1. `finance_meta`

### `nyse_stock`
- 용도: NYSE 상장 주식 목록(마스터 유니버스)
- 적재 경로:
  - `finance/data/nyse.py::load_nyse_listings(kind="stock")` -> CSV 생성
  - `finance/data/nyse_db.py::load_nyse_csv_to_mysql(kind="stock")` -> DB UPSERT
- 주요 데이터:
  - `symbol`, `name`, `url`, `created_at`

### `nyse_etf`
- 용도: NYSE 상장 ETF 목록(마스터 유니버스)
- 적재 경로:
  - `load_nyse_listings(kind="etf")` -> CSV
  - `load_nyse_csv_to_mysql(kind="etf")` -> DB UPSERT
- 주요 데이터:
  - `symbol`, `name`, `url`, `created_at`

### `nyse_asset_profile`
- 용도: 종목 메타/필터 정보(퀀트 유니버스 정제용)
- 적재 경로:
  - `finance/data/asset_profile.py::collect_and_store_asset_profiles()`
  - 내부에서 `nyse_stock`, `nyse_etf`를 읽어 yfinance 프로파일 조회 후 UPSERT
- 주요 데이터:
  - 식별: `symbol`, `kind(stock|etf)`
  - 분류: `quote_type`, `exchange`, `sector`, `industry`, `country`
  - 기초 팩터: `market_cap`, `dividend_yield`, `payout_ratio`
  - 운영 상태: `status(active/delisted/not_found/error)`, `is_spac`, `error_msg`, `last_collected_at`, `delisted_at`
- 활용 포인트:
  - `load_symbols_from_asset_profile()`에서 SPAC/중국/상폐 추정 종목 제외 필터로 사용

---

## 1-2. `finance_price`

### `nyse_price_history`
- 용도: OHLCV + 배당/분할 가격 히스토리(백테스트 핵심 시계열)
- 적재 경로:
  - `finance/data/data.py::store_ohlcv_to_mysql()`
- 조회 경로:
  - `finance/data/data.py::load_ohlcv_many_mysql()`
- 주요 데이터:
  - 키: `symbol`, `timeframe(1d/1wk/1mo)`, `date`
  - 가격: `open`, `high`, `low`, `close`, `adj_close`, `volume`
  - 기업행위: `dividends`, `stock_splits`
  - 운영: `updated_at`
- 참고:
  - 현재 테이블 구조에는 거래소 캘린더/세션 정보(휴장, 반장 등)는 없음

---

## 1-3. `finance_fundamental`

### `nyse_fundamentals`
- 용도: yfinance 재무제표에서 추린 필수 재무 스냅샷
- 적재 경로:
  - `finance/data/fundamentals.py::upsert_fundamentals()`
- 주요 데이터:
  - 키: `symbol`, `freq(annual|quarterly)`, `period_end`
  - 손익: `total_revenue`, `gross_profit`, `operating_income`, `ebit`, `net_income`
  - 재무상태: `total_assets`, `current_assets`, `total_liabilities`, `current_liabilities`, `total_debt`, `net_assets`
  - 현금흐름: `operating_cash_flow`, `free_cash_flow`, `capital_expenditure`, `cash_and_equivalents`
  - 기타: `dividends_paid`, `shares_outstanding`, `currency`, `source`, `last_collected_at`, `error_msg`

### `nyse_factors`
- 용도: fundamentals + price 결합으로 계산한 팩터 저장
- 적재 경로:
  - `finance/data/factors.py::upsert_factors()`
  - `period_end` 기준으로 직전 거래일 가격(asof) 매칭 후 계산
- 주요 데이터:
  - valuation: `psr`, `por`, `ev_ebit`, `per`, `pbr`, `pcr`, `pfcr`
  - quality/profitability: `gpa`, `roe`, `roa`, `asset_turnover`
  - safety/liquidity: `current_ratio`, `debt_ratio`, `liquidation_value`
  - growth: `op_income_growth`, `asset_growth`, `debt_growth`, `shares_growth`
  - base: `price`, `market_cap`, `enterprise_value`
  - 운영: `last_calculated_at`, `error_msg`

### `nyse_financial_statement_values`
- 용도: EDGAR 재무제표 라벨별 실제 수치(long format)
- 적재 경로:
  - `finance/data/financial_statements.py::upsert_financial_statements()`
- 주요 데이터:
  - 키: `symbol`, `freq`, `period_end`, `statement_type`, `label`
  - 값: `value`
  - 운영: `source`, `last_collected_at`, `error_msg`
- 특징:
  - 매우 세부적인 계정과목까지 저장 가능해 커스텀 팩터 확장성이 큼

### `nyse_financial_statement_labels`
- 용도: 라벨 메타(한글 라벨 포함) 및 라벨 관리
- 적재 경로:
  - `upsert_financial_statements()`에서 values와 함께 UPSERT
- 주요 데이터:
  - 키: `symbol`, `label`, `as_of`
  - 메타: `label_kr`, `statement_type`, `confidence`
  - 운영컬럼: `enabled`, `priority`, `condition_json`, `last_updated_at`

---

## 1-4. 현재 수집 체인의 구조 요약
1. NYSE 목록 수집: `nyse_stock`/`nyse_etf`
2. 프로파일 강화: `nyse_asset_profile`
3. 가격 수집: `nyse_price_history`
4. 재무 스냅샷 수집: `nyse_fundamentals`
5. 팩터 계산: `nyse_factors`
6. 상세 재무 라벨/값: `nyse_financial_statement_labels`, `nyse_financial_statement_values`

즉, 현재 구조는 **유니버스-가격-기초재무-팩터**까지는 이미 갖춘 상태입니다.

---

## 2. 퀀트 백테스트를 위해 추가로 필요한 데이터(권장)
현재 저장 데이터만으로도 기본 백테스트는 가능하지만, 실전형/기관형 검증에는 아래 데이터가 추가로 필요합니다.

## 2-1. 우선순위 높음 (먼저 보강 권장)

### A. 포인트인타임(Point-in-Time) 재무 공시 시점
- 필요 이유:
  - 현재 `period_end` 중심이라 실제 시장 공개일(보고서 제출일) 지연이 반영되지 않으면 룩어헤드 바이어스 위험
- 추가 제안 컬럼/테이블:
  - `filing_date`, `accepted_datetime`, `report_type(10-K/10-Q)`
  - restatement 구분 플래그

### B. 생존편향 방지용 상장/상폐 히스토리
- 필요 이유:
  - 현재 `status`는 추정값이고 시계열 이력(상장일/상폐일/티커변경)이 약함
- 추가 제안:
  - `listing_date`, `delisting_date`, `delisting_reason`, `old_symbol/new_symbol`
  - 심볼 변경 매핑 테이블

### C. 벤치마크/무위험금리 시계열
- 필요 이유:
  - 전략 성과 해석(알파, 정보비율, 초과수익) 필수
- 추가 제안:
  - 벤치마크 가격(`SPY`, `QQQ`, `ACWI` 등)
  - 무위험금리(`3M T-Bill`, SOFR)

### D. 거래비용/슬리피지 모델용 마이크로 구조 데이터
- 필요 이유:
  - 현재 백테스트는 사실상 마찰비용 0 가정
- 추가 제안:
  - 일별/월별 스프레드 대용치, ADV(평균거래대금), 수수료 모델 파라미터

## 2-2. 우선순위 중간 (전략 확장 시 권장)

### E. 섹터/산업 분류의 시점 이력
- 필요 이유:
  - 섹터 로테이션, 중립화, 리밸런싱 제약에 필요
- 추가 제안:
  - `symbol-sector` 변경 이력 테이블(`effective_from`, `effective_to`)

### F. 인덱스 편입 이력
- 필요 이유:
  - S&P500/Nasdaq100 편입 기반 유니버스 전략 검증
- 추가 제안:
  - `index_membership_history(symbol, index_name, in_date, out_date)`

### G. 배당 이벤트 상세
- 필요 이유:
  - 현재 `dividends` 총액은 있으나 ex-date/pay-date 기반 전략에는 부족
- 추가 제안:
  - `ex_dividend_date`, `record_date`, `pay_date`, `dividend_type`

### H. ETF 추가 메타
- 필요 이유:
  - ETF 로테이션/리스크 통제에 추적오차, 보수율, AUM 흐름 중요
- 추가 제안:
  - `expense_ratio`, `aum`, `tracking_error`, `holdings_turnover`

## 2-3. 우선순위 낮음 (고급 전략용)

### I. 애널리스트 추정치/서프라이즈
- 필요 이유:
  - 기대치 대비 실적 서프라이즈, 리비전 팩터 전략

### J. 공매도/대차 데이터
- 필요 이유:
  - short interest, borrow fee 기반 수급/리스크 신호

### K. 옵션 내재변동성/스큐
- 필요 이유:
  - 변동성 리스크 프리미엄, 테일리스크 필터 전략

---

## 3. 현재 스키마 대비 갭 분석 (요약)

- 이미 강한 영역:
  - 가격(OHLCV+배당/분할), 재무 스냅샷, 다수 팩터, 상세 재무 라벨
- 부족한 영역:
  - 시점 일치(공시일), 생존편향 제어, 거래비용 모델, 벤치마크/무위험금리
- 실무 우선 순서 제안:
  1. 공시일/상장상폐 이력 추가
  2. 벤치마크/무위험금리 저장
  3. 거래비용 근사용 데이터 추가
  4. 섹터/인덱스 membership 시계열 보강

---

## 4. 파일 정리(요청사항 반영)
- Markdown 보관 폴더 생성: `finance/docs`
- 기존 문서 이동:
  - `finance/FINANCE_PACKAGE_ANALYSIS.md` -> `finance/docs/FINANCE_PACKAGE_ANALYSIS.md`
- 신규 조사 문서 생성:
  - `finance/docs/FINANCE_DB_DATA_AUDIT.md`
