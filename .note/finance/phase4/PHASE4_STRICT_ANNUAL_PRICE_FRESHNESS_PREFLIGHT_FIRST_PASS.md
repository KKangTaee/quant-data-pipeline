# Phase 4 Strict Annual Price Freshness Preflight First Pass

## 목적
- `Quality Snapshot (Strict Annual)`과 `Value Snapshot (Strict Annual)` 실행 전에
  large-universe price freshness 상태를 먼저 보여준다.
- 실행 후에만 원인을 추적하는 것이 아니라,
  실행 전에 stale symbol / latest-date spread를 확인하게 한다.

## 구현 범위

### 1. Loader
- `finance/loaders/price.py`
  - `load_price_freshness_summary(...)` 추가
  - full price history를 읽지 않고
    symbol별 `MAX(Date)`와 row count만 집계하는 preflight용 loader다.

### 2. Runtime helper
- `app/web/runtime/backtest.py`
  - `inspect_strict_annual_price_freshness(...)` 추가
  - strict annual universe 기준으로:
    - requested count
    - covered count
    - common latest date
    - newest latest date
    - spread days
    - stale symbol count
    - missing symbol count
  를 계산한다.
- strict annual quality / value wrapper는 이 결과를:
  - 실행 전 warning 생성
  - 결과 bundle `meta["price_freshness"]`
  에 같이 남긴다.

### 3. UI
- `app/web/pages/backtest.py`
  - strict annual single-strategy form 두 곳에
    `Price Freshness Preflight` 섹션 추가:
    - `Quality Snapshot (Strict Annual)`
    - `Value Snapshot (Strict Annual)`
  - 현재 선택된 universe와 end date 기준으로
    common latest / newest latest / spread를 바로 보여준다.
  - stale or missing symbol이 있으면
    `Preflight Details`에서 샘플 심볼 목록을 보여준다.

## 현재 동작
- 모두 정렬되어 있으면:
  - green success
  - 예: `All 300 selected symbols have price data through 2026-03-20.`
- 최신 날짜가 갈려 있으면:
  - yellow warning
  - selected end보다 뒤처진 symbol count
  - universe 내부 latest-date spread
  - first stale / missing symbols
  를 보여준다.

## 운영 의미
- strict annual wide-universe preset에서
  duplicated final-month row가 보이면
  selection logic만 의심하지 말고
  먼저 price freshness preflight를 확인하게 된다.
- 이 check는 `Daily Market Update` 실행 여부를 판단하는
  lightweight operator signal 역할을 한다.

## 검증
- `python3 -m py_compile`
  - `finance/loaders/price.py`
  - `finance/loaders/__init__.py`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/__init__.py`
  - `app/web/pages/backtest.py`
  통과
- runtime helper check:
  - `US Statement Coverage 300`
  - `end=2026-03-20`
  - status: `ok`
  - `common_latest_date = 2026-03-20`
  - `spread_days = 0`

## 의미
- strict annual family는 이제
  - statement shadow factor fast path
  - selection history
  - large-universe union-calendar fix
  - price freshness preflight
  까지 갖춘 상태다.
