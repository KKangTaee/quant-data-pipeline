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

## UI 설계

Market Context 진입점은 기존 매크로 cockpit과 자료 보강 영역을 더 이상 불러오거나 렌더링하지 않는다. 새 가치평가 read model만 읽어 React 기반 Streamlit component에 전달한다. 재무 계산은 service가 끝낸 뒤 직렬화된 결과만 React에 전달하며, React는 수식을 다시 계산하지 않는다.

새 화면은 사용자가 위에서 아래로 `현재 멀티플 위치 → 예상 실적 → 예상 실적 기반 지수 구간 → 근거와 한계` 순서로 읽도록 구성한다. 두 그래프는 한 화면에서 위아래로 배치하며, 별도 하위 탭이나 운영 진단 패널을 만들지 않는다.

### 변경 전 UI 트리

```text
Workspace
└── Overview
    └── 시장 맥락
        ├── 시장 맥락 제목 / 마지막 거래일 안내
        ├── 시장 브리프 tape
        │   ├── 자료 상태
        │   ├── Top Mover
        │   ├── Breadth
        │   ├── Macro
        │   └── Next Event
        ├── 섹터 압력 지도
        ├── 이벤트 타임라인
        ├── sentiment 요약
        ├── 근거 / 자료 기준 disclosure
        └── 자료 보강
            ├── refresh reflection
            ├── 실행 가능한 보강 항목
            ├── 전체 / 선택 갱신 버튼
            └── job / rows / status 상세
```

### 변경 후 UI 트리

```text
Workspace
└── Overview
    └── 시장 맥락
        ├── 화면 헤더
        │   ├── 제목: S&P 500 가치평가
        │   ├── 설명: 실제 실적과 FOMC SEP를 이용한 상대 가치평가
        │   └── 기준일 strip
        │       ├── SPX / SPY 가격 기준일
        │       ├── TTM 실제 EPS 완료 분기
        │       └── FOMC SEP 발표일
        ├── 1. 최근 5년 멀티플 구간 [React]
        │   ├── 핵심 수치
        │   │   ├── 현재 후행 PER
        │   │   ├── 5년 중심 멀티플
        │   │   ├── 현재 Z-score
        │   │   └── 현재 구간: 낮음 / 중립 / 높음 / 극단적 높음
        │   ├── 월별 PER 그래프
        │   │   ├── 최근 60개월 후행 PER line
        │   │   ├── -1σ 영역
        │   │   ├── 평균선
        │   │   ├── +1σ 영역
        │   │   ├── +2σ 기준선
        │   │   └── 현재 위치 marker
        │   ├── 기간 민감도 안내
        │   │   └── 3년과 5년 판정이 다를 때만 표시
        │   └── 자료 기준
        │       ├── Shiller 월별 자료
        │       ├── As-Reported EPS
        │       └── descriptive band 한계
        ├── 2. FOMC 예상 실적 기반 지수 시나리오 [React]
        │   ├── 예상 EPS 요약
        │   │   ├── 현재 TTM 실제 EPS
        │   │   ├── 보수 예상 EPS
        │   │   ├── 기준 예상 EPS
        │   │   └── 낙관 예상 EPS
        │   ├── SPX 지수 시나리오 그래프
        │   │   ├── 보수적 하단 band
        │   │   ├── 중앙 지수선
        │   │   ├── 낙관적 상단 band
        │   │   └── 현재 SPX marker
        │   ├── 현재 위치 수치
        │   │   ├── 중앙 지수 대비 괴리율
        │   │   ├── 현재 내재 예상 PER
        │   │   └── 예상 실적 기준 구간
        │   ├── SPY 환산
        │   │   ├── 현재 SPY
        │   │   └── 하단 / 중앙 / 상단 환산 가격
        │   └── 전망 근거
        │       ├── FOMC SEP 대상 연도
        │       ├── 실질 GDP / PCE median
        │       └── Central Tendency는 민감도 범위라는 안내
        └── 공통 한계 disclosure
            ├── 투자 신호 / 공식 적정가가 아님
            ├── FOMC 모형에 포함되지 않은 이익 변수
            ├── trailing multiple과 예상 EPS 결합 한계
            └── 사용한 데이터 출처 / 기준일
```

### 1번 영역: 최근 5년 멀티플 구간

- 상단 요약은 현재 후행 PER, 5년 중심 멀티플, Z-score, 현재 구간을 한 줄로 보여준다.
- 본문 그래프는 월별 PER line과 `-1σ / 평균 / +1σ / +2σ` 기준선 및 배경 구간을 함께 보여준다.
- 현재 위치 marker는 다른 월보다 강하게 표시하되 매수·매도 색상이나 signal 문구를 사용하지 않는다.
- 3년과 5년 판정이 다를 때만 기간 민감도 안내를 그래프 아래 보조 문구로 표시한다.

### 2번 영역: FOMC 예상 실적 기반 지수 시나리오

- 현재 TTM 실제 EPS와 보수·기준·낙관 예상 EPS를 먼저 보여준다.
- SPX 그래프에는 하단·중앙·상단 지수 band와 현재 SPX marker를 표시한다.
- 중앙 지수 대비 괴리율과 현재 내재 예상 PER를 그래프 옆 또는 바로 아래에 배치한다.
- SPY는 가치평가 계산에 사용하지 않고 SPX band의 비율 환산 결과만 보조 수치로 표시한다.
- FOMC SEP 발표일, 대상 연도, GDP/PCE 입력값을 그래프 안이 아니라 근거 영역에 배치한다.

### 반응형 배치

- 데스크톱에서도 두 그래프를 나란히 압축하지 않고 위아래 전체 폭으로 배치한다.
- 핵심 수치는 넓은 화면에서 4열, 좁은 화면에서 2열 또는 1열로 줄어든다.
- 그래프 범례와 기준일은 모바일에서 줄바꿈되며 가로 스크롤에 의존하지 않는다.
- React component가 실패하면 동일 read model을 사용한 간결한 Streamlit fallback을 렌더링한다.

### 화면에서 제거할 기존 내용

- 시장 세션 / 마지막 거래일 브리프
- 시장 브리프 tape
- Top Mover와 Breadth rail
- 섹터 압력 지도
- 이벤트 타임라인
- sentiment 요약
- Market Context refresh reflection / bar / result
- raw job / rows / status 진단

기존 하위 service는 Market Movers, Futures Macro, Sentiment, Events, compatibility test 또는 문서에서 사용하지 않는다는 reference audit가 끝날 때까지 유지한다. 이번 차수에서는 Market Context의 visible render 경로만 제거한다.

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
