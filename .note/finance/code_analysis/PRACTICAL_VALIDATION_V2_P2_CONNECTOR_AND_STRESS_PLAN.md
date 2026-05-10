# Practical Validation V2 P2 Connector And Stress Plan

## 목적

이 문서는 Practical Validation V2의 P2 개발 범위를 실행 가능한 개발 계획으로 정리한다.
기존 `PRACTICAL_VALIDATION_V2_REMAINING_IMPLEMENTATION_PLAN.md`가 전체 남은 구현 목록이라면,
이 문서는 그중 P2에 해당하는 provider connector, macro / sentiment connector,
stress interpretation 고도화를 어떤 순서로 개발할지 정한다.

상세 provider / DB / loader 설계는
`PRACTICAL_VALIDATION_V2_PROVIDER_CONNECTOR_PLAN.md`를 기준으로 한다.

## 쉽게 말하면

현재 Practical Validation은 이미 후보 source, 최신 runtime 재검증, curve provenance,
benchmark parity, rolling / stress / baseline / sensitivity 일부 계산을 갖고 있다.

하지만 아직 많은 진단이 아래처럼 proxy에 가깝다.

- ETF 운용성: 가격 / 거래량 proxy
- 자산군 노출: ticker 이름과 known bucket proxy
- macro / sentiment: benchmark 최근 움직임 proxy
- stress: 위기 구간 숫자는 계산하지만 "왜 약했는지" 해석은 약함

P2의 목표는 이 proxy evidence를 더 실제적인 데이터와 해석으로 승격하는 것이다.

```text
현재:
가격 / 거래량 / ticker proxy 중심 진단

P2 이후:
provider snapshot + macro context + stress interpretation 기반 진단
```

## 왜 필요한가

백테스트 성과가 좋아도 실전 후보로 바로 믿기에는 부족한 질문들이 있다.

- ETF 비용과 거래 가능성이 실제 운용에 충분한가?
- ETF 안쪽 holdings가 서로 겹쳐서 실제로는 같은 위험에 몰려 있지 않은가?
- 현재 금리, credit spread, volatility 환경에서 후보의 약점이 다시 드러날 수 있는가?
- 위기 구간에서 숫자가 나빴다면, 그 원인이 자산군, component, benchmark mismatch 중 무엇인가?

P2는 이 질문들을 Final Review에서 사람이 판단할 수 있는 evidence로 만든다.

## 이 P2가 끝나면 좋은 점

- `Operability / Cost / Liquidity`가 단순 proxy가 아니라 provider coverage를 함께 보여준다.
- `Regime / Macro Suitability`와 `Sentiment / Risk-On-Off Overlay`가 market-context snapshot을 읽는다.
- `Stress / Scenario Diagnostics`가 단순 return / MDD 표를 넘어 해석 문장과 review trigger를 제공한다.
- Final Review는 `NOT_RUN`, `REVIEW`, `PASS`의 이유를 더 명확하게 읽을 수 있다.
- Selected Portfolio Dashboard의 사후 monitoring으로 이어질 때 어떤 data gap이 남았는지 추적하기 쉬워진다.

## 현재 기준선

현재 구현 상태는 아래 문서와 코드 기준이다.

| 영역 | 현재 상태 |
|---|---|
| 최신 runtime 재검증 | `전략 재검증 실행` 버튼으로 기존 strategy runtime을 DB 최신 시장일까지 확장 실행 |
| Curve provenance | actual runtime, embedded snapshot, component proxy, DB price proxy 출처를 validation result에 저장 |
| Benchmark parity | 기간, 월별 coverage, frequency 차이를 계산 |
| ETF operability | DB price / volume 기반 60D 평균 거래대금 proxy |
| Asset allocation | ticker bucket proxy |
| Holdings overlap | 아직 없음 |
| Macro / sentiment | benchmark recent return / drawdown / volatility proxy |
| Stress | static stress calendar + curve 기반 return / MDD / benchmark spread |
| Sensitivity | drop-one / weight +5%p 일부, strategy-specific perturbation은 아직 `NOT_RUN` |

현재 DB 기준으로 확인된 데이터 상태:

| 데이터 | 현재 활용 가능성 |
|---|---|
| `finance_price.nyse_price_history` | OHLCV / volume / latest market date / ADV proxy 계산 가능 |
| `finance_meta.nyse_asset_profile` | `total_assets`, `bid`, `ask`, `fund_family`, `status`를 저장할 수 있으나 실제 coverage는 낮음 |
| ETF holdings | 별도 table / loader 없음 |
| Macro series | 별도 table / loader 없음 |
| Sentiment series | 별도 table / loader 없음 |

## P2 범위

### P2-1. Cost / Liquidity / ETF Operability Connector

목표:

- ETF별 비용, 유동성, 거래 가능성 데이터를 provider snapshot으로 읽는다.
- 현재 price / volume proxy와 실제 provider data를 분리해 보여준다.

핵심 evidence:

- expense ratio
- AUM 또는 net assets
- average dollar volume
- bid-ask spread 또는 median bid-ask spread
- NAV / market price / premium-discount
- 상장 상태, fund family, leverage / inverse 여부

진단 반영:

- `10. Operability / Cost / Liquidity`
- 일부 `9. Leveraged / Inverse ETF Suitability`
- provider coverage summary

### P2-2. ETF Holdings / Sector Look-through

목표:

- ETF 내부 holdings를 읽어 실제 exposure와 overlap을 계산한다.

핵심 evidence:

- fund ticker
- as-of date
- holding symbol / name / id
- weight %
- sector
- asset class
- country

진단 반영:

- `2. Asset Allocation Fit`
- `3. Concentration / Overlap / Exposure`
- holdings-level top concentration
- holdings overlap matrix

주의:

- holdings는 시점별로 바뀌므로 point-in-time 한계를 UI와 result에 남긴다.
- full holdings row를 JSONL에 저장하지 않고 DB 또는 loader 결과로 관리한다.

### P2-3. Macro / Sentiment Connector

목표:

- benchmark price-action proxy 대신 market-context snapshot을 붙인다.

1차 series:

- VIX 또는 VIX proxy
- yield curve spread
- credit spread

후속 optional:

- Fear & Greed 계열 sentiment index
- breadth / put-call / junk bond demand 계열 지표

진단 반영:

- `5. Regime / Macro Suitability`
- `6. Sentiment / Risk-On-Off Overlay`

주의:

- macro / sentiment는 trade signal이 아니다.
- 자동 매수 / 매도 판단이나 hard blocker로 쓰지 않는다.
- 데이터가 없으면 `NOT_RUN`, proxy만 있으면 `REVIEW`로 남긴다.

### P2-4. Stress Interpretation 고도화

목표:

- static stress window 결과를 숫자표에서 해석 가능한 evidence로 확장한다.

핵심 evidence:

- stress window별 portfolio return
- portfolio MDD
- benchmark spread
- recovery 여부
- component contribution
- exposure-based interpretation
- Final Review 질문 / trigger

진단 반영:

- `7. Stress / Scenario Diagnostics`
- `11. Robustness / Sensitivity / Overfit`의 일부 review gap

예시 output:

```text
2022 Rate Shock:
장기채 비중이 손실을 키웠지만 주식 노출 축소가 benchmark 대비 방어에 기여했습니다.
현재 후보가 여전히 duration에 크게 의존하면 금리 재상승 구간에서 재검토가 필요합니다.
```

### P2-5. Strategy-specific Sensitivity Runtime

이 항목은 P2 후반 또는 P3로 분리 가능하다.
사용자가 P2 범위에 포함하길 원하면 provider connector 이후 붙인다.

목표:

- 기존 runtime이 허용하는 작은 설정 변경으로 sensitivity를 실제 재계산한다.

예:

- GTAA: interval, MA window, score lookback
- GRS: lookback, top_n
- Equal Weight: rebalance frequency, ticker subset
- Mix: component drop-one, weight +/-5%p

주의:

- optimizer가 아니다.
- 새 전략 구현이 아니다.
- full result dataframe을 registry에 저장하지 않는다.

## 개발하지 않는 것

P2에서 하지 않는 일:

- live approval
- broker order
- 자동 리밸런싱
- 매수 / 매도 signal 생성
- 새 strategy family 구현
- external provider raw data를 UI에서 즉시 fetch
- full holdings row 또는 full macro series를 JSONL registry에 저장
- run_history JSONL commit

## 권장 아키텍처

```text
provider / existing DB
  -> finance/data/* collector
  -> finance_meta / finance_price snapshot tables
  -> finance/loaders/* read path
  -> app/web/backtest_practical_validation_connectors.py
  -> app/web/backtest_practical_validation_helpers.py diagnostics
  -> Practical Validation UI
  -> PRACTICAL_VALIDATION_RESULTS.jsonl compact evidence
  -> Final Review
```

핵심 원칙:

- UI는 remote provider를 직접 호출하지 않는다.
- DB / loader / connector adapter / diagnostics를 분리한다.
- provider data와 proxy data의 출처를 반드시 구분한다.
- 데이터가 없을 때는 통과가 아니라 `NOT_RUN` 또는 `REVIEW`다.

## 파일별 수정 계획

| 파일 | 작업 |
|---|---|
| `finance/data/db/schema.py` | ETF operability snapshot, holdings snapshot, macro series table 추가 |
| `finance/data/asset_profile.py` | 기존 profile 수집과 provider snapshot의 중복 boundary 검토. 큰 확장은 별도 collector가 더 적합 |
| `finance/data/etf_provider.py` | 신규 후보. ETF cost / liquidity / holdings provider collector |
| `finance/data/macro.py` | 신규 후보. macro / sentiment series collector |
| `finance/loaders/provider.py` 또는 `finance/loaders/asset_profile.py` | ETF operability / holdings / macro snapshot loader |
| `finance/loaders/__init__.py` | 새 loader public export |
| `app/web/backtest_practical_validation_connectors.py` | Practical Validation이 읽는 provider context adapter |
| `app/web/backtest_practical_validation_helpers.py` | diagnostics가 provider context를 우선 사용하고 proxy fallback 유지 |
| `app/web/backtest_practical_validation.py` | Provider Coverage / Stress Interpretation 표시 |
| `app/web/runtime/portfolio_selection_v2.py` | validation schema optional field 보강 |
| `.note/finance/code_analysis/DATA_DB_PIPELINE_FLOW.md` | 새 DB / loader flow가 생기면 갱신 |
| `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md` | Practical Validation 표시 흐름이 바뀌면 갱신 |
| `.note/finance/data_architecture/*` | 새 table 의미 / source boundary / PIT 한계 갱신 |

## 구현 순서

### 작업 단위 1. Provider schema / loader contract

목표:

- 먼저 DB schema와 loader output contract를 고정한다.
- provider data가 없어도 빈 snapshot을 안정적으로 반환한다.

검증:

- loader가 data 없음 상태에서 빈 DataFrame 또는 `NOT_RUN` context를 반환
- 기존 Practical Validation은 깨지지 않음

### 작업 단위 2. Cost / Liquidity / Operability 실제 evidence 연결

목표:

- 기존 `nyse_asset_profile` + price history ADV를 bridge로 사용한다.
- 별도 snapshot table이 준비되면 그 데이터를 우선한다.

검증:

- `SPY / QQQ / GLD / IEF / TLT` 같은 ETF는 가능한 field를 보여준다.
- coverage가 낮은 ETF는 `REVIEW` 또는 `NOT_RUN`으로 표시한다.

### 작업 단위 3. Practical Validation Provider Coverage UI

목표:

- 사용자가 "어떤 데이터가 실제 provider이고, 어떤 데이터가 proxy인지" 바로 이해하게 한다.

표시 예:

```text
Provider Coverage
Cost             REVIEW   expense ratio missing
Liquidity        PASS     ADV proxy available
Spread           REVIEW   bid-ask provider coverage partial
Holdings         NOT_RUN  holdings connector not configured
Macro            NOT_RUN  macro connector not configured
```

### 작업 단위 4. Macro / Sentiment connector

목표:

- VIX / yield curve / credit spread snapshot을 validation date 기준으로 읽는다.

검증:

- series가 없으면 `NOT_RUN`
- series가 있으면 snapshot date, source, value, interpretation이 표시됨

### 작업 단위 5. Stress Interpretation

목표:

- stress window별 숫자와 함께 해석 문장, 원인 추정, Final Review 질문을 만든다.

검증:

- 후보 기간 밖 stress는 `NOT_RUN`
- 후보 기간 안 stress는 return / MDD / benchmark spread / interpretation 표시

### 작업 단위 6. ETF holdings look-through

목표:

- holdings provider가 확정된 뒤 holdings-level overlap과 sector exposure를 계산한다.

검증:

- holdings coverage 없으면 proxy fallback 유지
- holdings coverage 있으면 ticker bucket proxy보다 holdings-based exposure를 우선 표시

## QA 체크리스트

구현 후 확인할 항목:

- [ ] provider data가 없는 상태에서도 Practical Validation 화면이 깨지지 않는다.
- [ ] `NOT_RUN`이 `PASS`처럼 보이지 않는다.
- [ ] provider snapshot과 DB price proxy의 출처가 UI와 result row에 남는다.
- [ ] full holdings row, full macro series, full dataframe은 JSONL에 저장하지 않는다.
- [ ] Final Review에서 provider gap / stress interpretation을 판단 근거로 읽을 수 있다.
- [ ] Selected Portfolio Dashboard가 기존 selected decision row를 계속 읽는다.
- [ ] `py_compile`이 통과한다.
- [ ] run_history / temp CSV / local generated artifact는 commit하지 않는다.

## 열려 있는 결정

| 결정 | 기본 제안 |
|---|---|
| ETF provider | 기존 yfinance profile field를 bridge로 쓰되, cost / holdings는 별도 provider snapshot 설계 |
| Holdings provider | 안정 source 확정 전 schema / loader contract 먼저 설계 |
| Macro source | FRED-compatible long-form series table을 우선 고려 |
| Sentiment source | VIX / credit spread / yield curve를 1차 sentiment proxy로 쓰고 Fear & Greed는 optional |
| Stress interpretation rule | rule-based template로 시작하고, 숫자 / exposure / component contribution 기반 문장 생성 |
| Sensitivity runtime 포함 여부 | provider connector 이후 P2 후반 또는 P3로 분리 가능 |

## 결론

P2는 새 전략을 만드는 작업이 아니라,
Practical Validation이 이미 가진 12개 diagnostics를 실제 provider data와 더 좋은 해석으로 보강하는 단계다.

첫 구현은 `Cost / Liquidity / ETF Operability Connector`가 가장 적합하다.
이미 `nyse_asset_profile`과 price history가 있으므로 bridge를 만들 수 있고,
동시에 provider coverage가 얼마나 부족한지도 UI에서 명확히 보여줄 수 있기 때문이다.
