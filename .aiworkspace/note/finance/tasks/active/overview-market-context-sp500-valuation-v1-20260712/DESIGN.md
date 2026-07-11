# Overview Market Context S&P 500 Valuation V1 Design

Status: Pending Written-Spec Review
Last Updated: 2026-07-12

## Decision Summary

`Workspace > Overview > Market Context`를 S&P 500 가치평가 전용 surface로 교체한다. 기존 마지막 거래일 정보, 시장 브리프, Top Mover, Breadth, 섹터 압력 지도, 이벤트 타임라인, sentiment summary, 자료 보강 패널은 더 이상 이 탭에서 렌더링하지 않는다.

새 화면은 React 기반으로 다음 두 그래프를 제공한다.

1. `최근 5년 멀티플 구간`: 실제 가격과 실제 TTM EPS로 계산한 월별 후행 PER의 상대적 위치
2. `FOMC 예상 실적 기반 S&P 500 지수 시나리오`: 현재 TTM 실제 EPS에 FOMC SEP 성장 시나리오를 적용한 예상 EPS와 SPX/SPY band

## Alternatives Considered

### A. Public-Source Hybrid — Selected

- Shiller monthly price/earnings
- S&P Index Earnings actual as-reported EPS
- Federal Reserve FOMC SEP accessible materials
- DB-backed SPX/SPY prices

장점은 공개 근거와 계산 투명성이다. 한계는 Shiller monthly earnings interpolation, S&P workbook automation 제약, analyst consensus 부재다.

### B. Licensed Forward Consensus — Deferred

- LSEG I/B/E/S or FactSet historical forward EPS/PER

forward valuation 정의가 가장 일관되지만 별도 라이선스가 필요하다. V1에 포함하지 않는다.

### C. Internal EDGAR Index EPS Reconstruction — Rejected

현재 EDGAR rows만으로 공식 index EPS를 재구성하려면 historical constituents, float-adjusted shares, official divisor, corporate-action handling이 추가로 필요하다. V1의 정확도와 범위를 벗어난다.

## Data Definitions

### EPS Basis

- 공통 EPS 기준은 `As-Reported`다.
- `TTM actual EPS`는 발표가 완료된 최근 네 분기의 실제 index EPS 합계다.
- `NTM macro-implied EPS`는 TTM actual EPS에 FOMC 기반 성장률을 적용한 자체 시나리오다.
- actual, estimate, mixed를 저장과 UI에서 구분한다.
- mixed EPS는 `TTM actual`로 표시하지 않는다.

### Monthly Trailing PER

```text
monthly_trailing_pe = monthly_spx_level / monthly_ttm_actual_eps
```

Shiller의 monthly `P`와 `E`를 V1 descriptive series로 사용할 수 있다. 이 `E`는 quarterly four-quarter total을 월별 보간한 연구 series이므로 historical timing backtest/PIT proof로 승격하지 않는다.

### Five-Year Multiple Distribution

- 공식 window: 최근 60개 완결 월
- sensitivity window: 최근 36개 완결 월
- 유효 조건: price > 0, EPS > 0, PER > 0

```text
log_pe = ln(monthly_trailing_pe)
mu = mean(log_pe_60m)
sigma = sample_std(log_pe_60m)
multiple(k) = exp(mu + k * sigma)
current_z = (ln(current_trailing_pe) - mu) / sigma
```

판정:

- `z <= -1`: 최근 5년 대비 낮은 구간
- `-1 < z < 1`: 중립 범위
- `z >= 1`: 최근 5년 대비 높은 구간
- `z >= 2`: 극단적으로 높은 구간

표준편차 band는 독립 표본 기반 신뢰구간이 아니라 autocorrelated monthly series의 descriptive relative zone이다.

3년 결과는 기본 화면에 별도 selector로 추가하지 않는다. 3년과 5년 판정 bucket이 다르면 `기간에 따라 해석이 달라짐` sensitivity note를 표시한다.

### FOMC Growth Scenarios

FOMC 금리 점 자체가 아니라 SEP table의 다음 값을 사용한다.

- Change in real GDP
- PCE inflation
- Median
- Central Tendency lower/upper

```text
nominal_growth = (1 + real_gdp_pct / 100) * (1 + pce_pct / 100) - 1
projected_eps = current_ttm_actual_eps * (1 + nominal_growth)
```

- conservative: central tendency lower endpoints
- baseline: medians
- optimistic: central tendency upper endpoints

GDP/PCE central tendency endpoints의 조합은 participant joint distribution이나 confidence interval이 아니라 sensitivity scenario다.

### Index Scenario Band

```text
lower_spx = conservative_eps * five_year_minus_1sigma_multiple
center_spx = baseline_eps * five_year_mean_multiple
upper_spx = optimistic_eps * five_year_plus_1sigma_multiple
gap_to_center_pct = current_spx / center_spx - 1
implied_macro_pe = current_spx / baseline_eps
```

후행 PER 분포를 NTM macro-implied EPS에 적용하므로 이 결과는 `공식 적정가`나 forward-PER confidence band가 아니다. UI에서는 `예상 실적 기반 지수 시나리오`로 부른다.

SPY 환산:

```text
target_spy = current_spy * target_spx / current_spx
```

모든 가치평가 계산은 SPX로 하고 SPY는 동일 기준일의 비율 환산 결과로만 표시한다.

## Source And Persistence Architecture

```text
Shiller / S&P Index Earnings / Federal Reserve SEP / SPX-SPY EOD
  -> finance/data/sp500_valuation.py
  -> finance/data/db/schema.py
  -> finance/loaders/sp500_valuation.py
  -> app/services/overview/sp500_valuation.py
  -> app/web/overview React surface
```

Planned storage contracts:

1. Monthly valuation observation
   - observation month, SPX level, EPS, PER, CAPE, source, quality, collected_at
2. Index earnings snapshot
   - period, basis, actual/estimate/mixed, EPS, source release date, source identity
3. FOMC SEP projection vintage
   - release date, target year, variable, statistic, lower/median/upper, source URL

New releases append new vintage rows. They do not overwrite prior projection releases.

S&P workbook automatic access may be unavailable. The collector boundary must support a deterministic uploaded/local source file path without adding direct UI fetch to Market Context. Manual source ingestion is an accepted V1 fallback; a typed EPS number without source identity is not canonical production input.

## Refresh Cadence

- SPX/SPY: trading-day EOD
- Shiller: monthly
- S&P Index Earnings: source file update / earnings update cadence
- FOMC SEP: new projection release, normally March/June/September/December

FOMC discovery starts from the official calendar/projection material links and must not hard-code a single historical anchor fragment. Failed refresh retains the latest successful vintage and marks freshness explicitly.

## Service Boundaries

`app/services/overview/sp500_valuation.py` owns Streamlit-free behavior:

- source-row normalization
- actual/mixed eligibility
- monthly PER construction
- 60m/36m distribution
- FOMC scenario calculation
- SPX/SPY alignment and conversion
- classification copy keys
- freshness, insufficiency, and limitation evidence

The service returns one serializable read model for React. React does not recompute financial formulas.

## UI Design

The Market Context entrypoint stops loading/rendering the old macro cockpit and refresh bar. It loads only the new valuation read model and renders a React Streamlit component with a Streamlit fallback for component failure.

### Surface 1: Five-Year Multiple Regime

- current trailing PER, 5y geometric-center multiple, Z-score, bucket
- monthly PER line
- -1 sigma / mean / +1 sigma / +2 sigma reference lines and zones
- source/basis date
- conditional 3y-vs-5y sensitivity note

### Surface 2: Earnings And Index Scenario

- current TTM actual EPS
- conservative/baseline/optimistic macro-implied EPS
- SPX scenario band and current SPX marker
- center gap percentage and implied macro P/E
- SPY equivalent band as secondary values
- FOMC SEP release date and target year

### Removed Visible Content

- market-session/last-trading-day brief
- market brief tape
- Top Mover and Breadth rail
- sector pressure map
- events timeline
- sentiment summary
- Market Context refresh reflection/bar/result
- raw job/row/status diagnostics

The underlying old services are retained until a later reference audit proves they are unused by Market Movers, Futures Macro, Sentiment, Events, compatibility tests, or docs.

## Error Handling

- fewer than 60 valid months: no official 5y classification; explain insufficiency
- 48–59 valid months: optional limited-history state, no full confidence copy
- non-positive EPS/PER: exclude from distribution; block current multiple if current EPS is invalid
- mixed/estimate current EPS: do not label actual; block actual-only scenario unless an explicitly labeled estimate mode is later approved
- missing/latest SEP parse failure: retain latest successful vintage and show its release date/staleness
- SPX/SPY date mismatch: do not calculate SPY equivalent
- React component failure: render a compact Streamlit fallback with the same read model and no remote fetch

## Test Design

### Data And Parser Tests

- Shiller workbook normalization fixture
- S&P EPS actual/estimate/mixed classification fixture
- FOMC accessible HTML parser fixture for median and central tendency
- new-vintage append/upsert identity

### Calculation Tests

- TTM/PE eligibility
- log mean/sample standard deviation and sigma multiples
- 60m official window and 36m sensitivity window
- FOMC compounding formula
- scenario band and SPY conversion
- insufficiency, non-positive EPS, stale/misaligned state

### UI And Contract Tests

- old Market Context render calls absent
- new React component receives the service read model
- React chart zones, labels, and disclosures render
- Python fallback renders when component is unavailable

### Verification

- targeted pytest
- Python compile
- React test/build
- `git diff --check`
- Streamlit Browser QA
- one generated QA screenshot, not committed unless requested

## Documentation And Commit Strategy

Coherent commits:

1. approved design/task record
2. source contracts and persistence
3. five-year multiple engine
4. FOMC earnings/index scenario engine
5. React Market Context replacement
6. QA hardening and durable docs alignment

Generated artifacts, registry JSONL, saved JSONL, run history, existing user screenshots, and unrelated Market Movers work remain uncommitted.
