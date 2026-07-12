# Overview Market Context S&P 500 Valuation V1 Design

Status: Implemented through V1.2
Last Updated: 2026-07-12

## V1.2 Implemented Amendment

- Graph 1 keeps the 60-month official / 36-month sensitivity contract and displays symmetric `-2σ/-1σ/center/+1σ/+2σ` anchors. React SVG owns hover state only; Python owns every multiple value.
- Graph 2 keeps the current EPS/SPX ruler and adds a 12-month reconstructed history using stored SEP release vintages, observation-year targets, and rolling 60-month log(PER) anchors.
- A SEP released during a month becomes effective for the next monthly point. The latest EOD point uses the latest release available by its exact as-of date.
- Shiller price-only months after the latest EPS publication remain stored. The history carries the last positive TTM EPS forward and exposes its `eps_basis_date` instead of implying that a new EPS was published.
- The history is labeled `과거 시점 재구성 시나리오`, not a strict PIT backtest, because Shiller EPS is not a preserved release-vintage series.

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

---

## V1.1 Data Activation Follow-up — 2026-07-12

### 이걸 하는 이유?

V1 live QA에서 `sp500_monthly_valuation` 1,863행과 SPX/SPY EOD가 저장됐는데도 S&P actual EPS가 없으면 그래프 1까지 `60개월 실제 PER 이력이 필요합니다`로 차단됐다. 그래프 2는 S&P Index Earnings importer는 있지만 공식 XLSX 자동 요청이 403으로 차단되어 기본 환경에서 `sp500_index_earnings`가 비어 있었다. 사용자가 실제 화면에서 두 그래프를 읽으려면 그래프 1 의존성을 분리하고, 그래프 2에 명시적 source hierarchy와 공식 파일 등록 흐름이 필요하다.

### 승인된 접근

완전 자동 403 우회, scraper, headless-browser impersonation은 구현하지 않는다. 대신 다음 두 경로를 결합한다.

1. 자동 무료 경로: Shiller 월별 자료에서 최신 60개월 PER와 최신 완료 분기 TTM EPS 대체 기준을 읽는다.
2. 공식 우선 경로: 사용자가 공식 Index Earnings XLSX를 브라우저로 내려받아 등록하면 S&P actual As-Reported quarter를 release vintage로 저장하고 즉시 우선 사용한다.

### 그래프 1 독립 계산

- 그래프 1은 `sp500_monthly_valuation`만 필요로 한다.
- 공식 60개월 window와 36개월 민감도는 마지막 유효 월별 `trailing_pe`로 계산한다.
- current marker는 마지막 Shiller 관측월의 `trailing_pe`다.
- `sp500_index_earnings`, current TTM actual EPS, SPX EOD 누락 때문에 그래프 1을 차단하지 않는다.
- source basis는 `Shiller 월별 보간 TTM EPS`와 최신 관측월을 표시한다.

### 그래프 2 EPS Source Hierarchy

```text
1순위: S&P Index Earnings
  quarterly + as_reported + actual
  latest distinct 4 quarters
  -> source_quality = official_actual

2순위: Shiller latest completed-quarter E
  month in 03 / 06 / 09 / 12
  positive trailing_eps
  -> source_quality = interpolated_ttm_proxy
```

- 1순위가 READY면 기존 actual TTM 계산을 사용한다.
- 1순위가 없거나 4분기 미만이면 2순위를 명시적으로 선택한다.
- Shiller fallback은 `실제 EPS`로 표기하지 않고 `Shiller TTM 대체 기준`으로 표시한다.
- read model은 `eps_source`, `eps_source_quality`, `eps_basis_date`, `fallback_reason`을 React에 전달한다.
- S&P official actual이 새로 저장되면 별도 migration 없이 다음 read에서 자동 승격한다.

### 공식 XLSX 등록 흐름

Market Context React 본문 아래 secondary Streamlit expander에 `S&P 공식 EPS 연결`을 둔다. 이는 job/status 진단 패널이 아니라 그래프 2의 누락 입력을 해결하는 bounded data action이다.

```text
S&P 공식 Index Earnings 링크 열기
  -> 사용자가 브라우저에서 XLSX 다운로드
  -> Market Context 파일 uploader에 등록
  -> workbook sheet/header 탐색
  -> quarterly date / As-Reported EPS 후보 preview
  -> 사용자가 source release date와 마지막 actual quarter 확인
  -> actual/estimate 상태 명시
  -> finance_meta.sp500_index_earnings vintage UPSERT
  -> cache clear / rerun
  -> official_actual source로 자동 승격
```

- XLS/XLSX 원본은 registry나 repo에 저장하지 않고 메모리에서 파싱한다.
- sheet/header는 첫 30행에서 date, As-Reported, Operating 관련 header를 탐색한다.
- 상태가 workbook cell에 명시돼 있으면 이를 사용한다.
- 상태가 명시되지 않으면 행 위치나 색상으로 추론하지 않고 사용자가 선택한 `마지막 actual quarter`를 cutoff로 적용한다.
- release date는 workbook 안에서 신뢰할 수 있게 파싱되면 제안값으로 보여주되 사용자가 확인한다.
- preview가 quarterly date와 As-Reported EPS를 찾지 못하면 DB write 없이 구체적 오류를 표시한다.

### UI 변경

- 그래프 1 blocked copy는 월별 이력이 실제로 60개 미만일 때만 노출한다.
- 그래프 2 상단의 `현재 TTM EPS` label은 source에 따라 `S&P actual TTM EPS` 또는 `Shiller TTM 대체 기준`으로 바뀐다.
- source-quality badge는 `공식 actual`과 `보간 대체 기준`을 구분한다.
- fallback 상태에서도 FOMC EPS/SPX scenario는 계산하되 limitation에 공식 actual 미연결을 표시한다.
- uploader expander는 secondary action이며 두 그래프보다 먼저 나오지 않는다.

### Error Handling

- Shiller 60개월 미만: 그래프 1만 `INSUFFICIENT_HISTORY`.
- S&P 4분기 미만 + Shiller completed-quarter EPS 없음: 그래프 2만 `BLOCKED`.
- official XLSX header 미탐지: preview 단계에서 차단, DB write 없음.
- actual cutoff가 candidate 범위 밖: validation error, DB write 없음.
- official import 뒤에도 4 distinct actual quarters 미만: official incomplete evidence를 보존하되 graph 2는 Shiller fallback 유지.
- SEP stale, SPX/SPY date mismatch 방어는 V1 계약을 유지한다.

### Test Design

- S&P EPS가 비어 있어도 60개월 Shiller graph 1이 READY인지 검증.
- latest completed-quarter Shiller EPS loader와 source-quality payload 검증.
- official 4-quarter evidence가 Shiller fallback보다 우선하는지 검증.
- generic workbook header discovery, preview, user-confirmed cutoff, no-write error tests.
- import 후 cache clear/rerun contract와 React source label contract 검증.
- Browser QA에서 초기 fallback 상태와 official fixture import 후 승격 상태를 각각 확인한다.

### Out Of Scope

- 403 회피용 cookie forging, proxy, scraper, headless browser download.
- S&P 라이선스/SFTP 계약 구현.
- EDGAR constituent EPS 재구성과 index divisor 복제.
- fallback을 official actual 또는 애널리스트 consensus로 표현하는 행위.

## V1.1 Final Implementation Contract — 2026-07-12

### 왜 기존 설계를 좁히는가?

후속 source 조사 뒤 사용자는 S&P official Index Earnings를 현재 기능의 필수 입력에서 제외하고, DB에 공식 actual EPS가 없으면 Shiller 최신 TTM EPS로 자동 계산을 계속하도록 확정했다. 따라서 위 `공식 XLSX 등록 흐름`은 선택적 미래 확장으로만 남기며 이번 구현에는 uploader, download helper, job/status panel을 추가하지 않는다.

### 선택한 구조

1. `finance/loaders/sp500_valuation.py`가 공식 actual 4분기 TTM과 최신 Shiller TTM EPS를 각각 읽는다.
2. 같은 loader 계층의 resolver가 `official_actual`을 우선하고, 준비되지 않았으면 `interpolated_ttm_proxy`를 선택한다.
3. `app/services/overview/sp500_valuation.py`는 선택된 EPS evidence를 계산에 사용하되, 그래프 1은 EPS resolver와 완전히 독립적으로 최신 Shiller `trailing_pe`를 current marker로 사용한다.
4. React는 `eps_source`, `eps_source_quality`, `eps_basis_date`, `fallback_reason`과 SEP 입력을 그대로 설명하며 source 선택이나 재무 계산을 수행하지 않는다.

Service가 두 DB source를 직접 조회·선택하는 대안은 source policy가 계산 계층으로 새어 나가므로 선택하지 않는다. 공식 EPS가 없을 때 그래프 2를 계속 차단하는 대안은 이번 완료 조건을 만족하지 못한다.

### 그래프 1 계약

- 필요한 입력은 유효한 Shiller 월별 `trailing_pe` 60개뿐이다.
- current PER와 marker는 최신 유효 Shiller 관측월의 `trailing_pe`다.
- 60개월 log(PER) 평균·표본 표준편차가 공식 구간이고, 36개월 결과는 민감도다.
- 최신 SPX, 공식 S&P EPS, SEP가 없어도 그래프 1 status는 독립적으로 `READY`가 될 수 있다.

### 그래프 2 계약

- EPS 우선순위는 `S&P 공식 실제 EPS` 다음 `Robert Shiller TTM EPS`다.
- resolver는 `current_ttm_eps`, `eps_source`, `eps_source_quality`, `eps_basis_date`, `fallback_reason`을 반환한다.
- 최신 SEP target year의 median `Change in real GDP`와 median `PCE inflation`을 사용한다.

```text
expected_eps_growth_pct = real_gdp_pct + pce_inflation_pct
projected_eps = current_ttm_eps * (1 + expected_eps_growth_pct / 100)
lower_spx = projected_eps * five_year_minus_1sigma_multiple
baseline_spx = projected_eps * five_year_mean_multiple
upper_spx = projected_eps * five_year_plus_1sigma_multiple
current_vs_baseline_gap_pct = current_spx / baseline_spx - 1
```

양수 괴리율은 현재 SPX가 기준 시나리오보다 높은 상태, 음수는 낮은 상태다. 이는 애널리스트 컨센서스나 공식 적정가가 아니라 FOMC 거시 지표 기반 자체 시나리오다.

### UI 계약

- 그래프 1과 그래프 2의 readiness/error state를 분리한다.
- EPS 출처 badge, EPS 기준일, SEP 발표일, 적용 GDP, 적용 PCE, 계산 성장률을 그래프 2에 표시한다.
- Shiller fallback이면 `Robert Shiller TTM EPS`와 fallback 이유를 본문에 표시한다.
- EPS/SPX/SEP 기준일이 다르면 숨기지 않고 근거 영역에 표시한다.
- uploader, provider 직접 fetch, 운영 job/status 패널은 추가하지 않는다.

### 검증 계약

- 공식 EPS 0건 + Shiller 60개월 이상이면 그래프 1과 그래프 2가 모두 `READY`여야 한다.
- 공식 actual 4분기가 있으면 Shiller보다 자동 우선해야 한다.
- 실제 DB smoke에서 Shiller 2026-03 EPS, SEP 2026-06-17, SPX 2026-07-10 기준값이 read model에 남아야 한다.
- React source contract, TypeScript/Vite build, focused Python tests, DB-backed smoke, Browser QA를 모두 통과한 뒤 완료로 표시한다.
