# Phase 7 Supplementary Polish Pass

## 목적

- Phase 7 first pass 이후 남아 있던 실사용성 gap을 줄인다.
- quarterly strict prototype를 직접 테스트할 때 헷갈리기 쉬운 UI/diagnostic 부분을 보강한다.

## 이번 보강 범위

### 1. weekend / holiday-aware price freshness preflight

문제:

- strict preflight는 selected end를 그대로 stale 기준으로 사용했다.
- 예를 들어 `2026-03-28`처럼 비거래일을 end로 주면,
  실제 최신 거래일이 `2026-03-27`이어도 whole-universe stale처럼 보일 수 있었다.

수정:

- `finance/loaders/price.py`
  - `load_latest_market_date(...)` 추가
- `app/web/runtime/backtest.py`
  - selected end 이전의 실제 마지막 market session을 찾아
    `effective trading end`로 freshness를 판단하도록 변경

효과:

- selected end가 비거래일일 때 불필요한 stale warning이 줄어든다.
- preflight message / details에
  - `Selected End`
  - `Effective Trading End`
  가 함께 남는다.

검증:

- `US Statement Coverage 100`
- selected end `2026-03-28`
- result:
  - `effective trading end = 2026-03-27`
  - `stale_count = 0`

### 2. quarterly statement shadow coverage preview

문제:

- quarterly prototype가 실제로 어느 시점부터 shadow coverage를 갖는지
  UI에서 바로 읽기 어려웠다.

수정:

- `app/web/pages/backtest.py`
  - `Statement Shadow Coverage Preview` 추가

현재 표시 항목:

- `Requested`
- `Covered`
- `Earliest Period`
- `Latest Period`
- `Median Rows / Symbol`

효과:

- quarterly prototype가 왜 특정 구간부터 열리는지
  raw statement ledger가 아니라 rebuilt statement shadow 기준으로 바로 읽을 수 있다.

### 3. quarterly prototype UI wording refresh

수정:

- quarterly prototype 안내 문구를 Phase 7 기준으로 갱신
- `US Statement Coverage 100` 기본 preset은
  now `2016` 부근부터 다시 열리지만
  다른 universe / manual tickers는 coverage에 따라 더 늦을 수 있다는 점을 명시

### 4. Statement PIT Inspection UI card

문제:

- Phase 7 checklist의 핵심 검증 항목 일부가
  Python / notebook snippet 실행을 전제로 하고 있었다.

수정:

- `app/web/streamlit_app.py`
  - `Ingestion` 탭에 `Statement PIT Inspection` card 추가

현재 UI에서 바로 볼 수 있는 것:

- DB `Coverage Summary`
- DB `Timing Audit`
- EDGAR `Source Payload Inspection`

효과:

- quarterly / annual statement PIT 상태를 확인할 때
  notebook을 꼭 열지 않아도 된다
- later user validation이 훨씬 가벼워진다

## 코드 변경 파일

- `finance/loaders/price.py`
- `finance/loaders/__init__.py`
- `app/web/runtime/backtest.py`
- `app/web/pages/backtest.py`
- `app/web/streamlit_app.py`

## 의미

이번 패치는 quarterly PIT foundation 자체를 다시 바꾼 것은 아니다.
대신,

- non-trading-day freshness false warning을 줄이고
- quarterly shadow coverage 상태를 UI에서 읽기 쉽게 만들고
- prototype semantics를 더 직접적으로 설명하고
- statement PIT inspection을 UI에서 바로 수행할 수 있게 한

하는 실사용성 보강 패스라고 보는 것이 맞다.
