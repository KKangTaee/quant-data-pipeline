# Practical Validation V2 P2 Connector And Stress Plan

## 목적

이 문서는 Practical Validation V2의 P2 개발 범위를 실행 가능한 개발 계획으로 정리한다.
기존 `PRACTICAL_VALIDATION_V2_REMAINING_IMPLEMENTATION_PLAN.md`가 전체 남은 구현 목록이라면,
이 문서는 그중 P2에 해당하는 미완성 검증 항목 정상화 작업을 어떤 순서로 개발할지 정한다.

P2의 본질은 provider connector 자체가 아니다.
P2는 12개 Practical Validation 진단 중 아직 proxy / `NOT_RUN` / 설명 부족으로 남아 있는 항목을
정상 검증 가능한 상태로 만드는 작업이다.

상세 provider / DB / loader 설계는
`PRACTICAL_VALIDATION_V2_PROVIDER_CONNECTOR_PLAN.md`를 기준으로 한다.

문서가 지나치게 늘어나지 않도록, P2 provider 데이터 수집 계획은 별도 문서로 분리하지 않는다.
ETF holdings, macro series, sentiment series의 collector / schema / loader 계획은
`PRACTICAL_VALIDATION_V2_PROVIDER_CONNECTOR_PLAN.md` 안에서 함께 관리한다.

P2 개발 순서는 diagnostic normalization first로 고정한다.
먼저 어떤 검증 항목이 정상화 대상인지 확정하고,
그 검증에 필요한 provider / FRED 데이터를 ingestion에서 DB에 저장한 뒤,
loader, Practical Validation connector, UI / diagnostics 해석을 연결한다.

## 쉽게 말하면

현재 Practical Validation은 이미 후보 source, 최신 runtime 재검증, curve provenance,
benchmark parity, rolling / stress / baseline / sensitivity 일부 계산을 갖고 있다.

하지만 아직 많은 진단이 아래처럼 proxy에 가깝다.

- ETF 운용성: 가격 / 거래량 proxy
- 자산군 노출: ticker 이름과 known bucket proxy
- macro / sentiment: benchmark 최근 움직임 proxy
- stress: 위기 구간 숫자는 계산하지만 "왜 약했는지" 해석은 약함

P2의 목표는 이 proxy evidence를 더 실제적인 데이터와 해석으로 승격해서,
검증 항목이 "막연히 통과 / 실패"가 아니라 "실제 근거 있음 / proxy만 있음 / 데이터 없어 NOT_RUN"으로 읽히게 만드는 것이다.

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

## P2 완료 기준

P2 완료는 "모든 ETF와 모든 provider를 완벽히 지원"한다는 뜻이 아니다.
아래가 충족되면 P2는 완료로 본다.

- P2 대상 검증 항목이 actual / proxy / bridge / `NOT_RUN`을 명확히 구분한다.
- 대표 ETF와 FRED macro series에서 실제 provider data 수집 / DB 저장 / loader read가 동작한다.
- 데이터가 없거나 provider가 미지원이면 화면과 result row에 명확한 `NOT_RUN` 또는 `REVIEW` reason이 남는다.
- full holdings row, full macro series, full raw response는 JSONL에 저장하지 않는다.
- Final Review에서 사용자가 어떤 검증이 충분하고 어떤 검증이 부족한지 판단할 수 있다.

## P2 작업 순서

```text
P2-0. 12개 진단 중 P2 대상 항목 확정
P2-1. 각 항목에 필요한 데이터 목록 확정
P2-2. ETF 운용성 / 비용 / 유동성 데이터 수집
P2-3. ETF holdings / exposure 데이터 수집
P2-4. macro / sentiment 데이터 수집
P2-5. Practical Validation 12개 진단에 연결
P2-6. stress / sensitivity 해석 보강
P2-7. QA: proxy / NOT_RUN 항목이 정상적으로 설명되는지 확인
```

## P2 대상 진단

| 검증 번호 | 검증 항목 | 현재 문제 | P2에서 정상화할 내용 |
|---:|---|---|---|
| 2 | Asset Allocation Fit | ticker 이름 기반 추정 | ETF holdings / asset class exposure 기반으로 보강 |
| 3 | Concentration / Overlap / Exposure | ETF wrapper와 weight 중심 추정 | holdings overlap, top holding concentration, exposure 중복 계산 |
| 5 | Regime / Macro Suitability | benchmark price-action proxy | FRED VIX / yield curve / credit spread snapshot 사용 |
| 6 | Sentiment / Risk-On-Off Overlay | proxy 또는 `NOT_RUN` | VIX / spread / yield curve 기반 market context 표시 |
| 7 | Stress / Scenario Diagnostics | 숫자 중심, 원인 해석 약함 | stress별 원인 해석, recovery, review trigger 추가 |
| 9 | Leveraged / Inverse ETF Suitability | ticker 기반 추정 | leverage / inverse / daily objective provider field 확인 |
| 10 | Operability / Cost / Liquidity | 가격 / 거래량 proxy | 비용, AUM, ADV, spread, premium/discount 확인 |
| 11 | Robustness / Sensitivity / Overfit | 단순 perturbation 일부 | sensitivity 결과와 과최적화 해석 보강 |

## P2-0 완료 산출물: 대상 진단 계약

상태: `completed`

P2-0은 실제 provider 수집 코드를 작성하기 전에,
어떤 검증 항목을 정상화할지와 각 항목이 어떤 데이터 상태를 가질 수 있는지 확정하는 단계다.
이 단계의 산출물은 아래 계약이다.

### 상태 / 출처 기준

| 구분 | 의미 | Practical Validation 표시 |
|---|---|---|
| `actual` | 공식 provider, FRED, 또는 DB snapshot에서 해당 검증에 필요한 핵심 데이터가 충분함 | 해당 domain의 `PASS` / `REVIEW` 판단 근거로 사용 |
| `bridge` | 기존 `nyse_asset_profile`, `nyse_price_history`처럼 목적 전용 provider는 아니지만 실제 DB에 있는 보조 데이터 | `REVIEW` 또는 보조 evidence로 표시 |
| `proxy` | ticker 이름, component weight, benchmark price-action처럼 추정에 가까운 계산 | `REVIEW` 우선. 통과처럼 보이지 않게 origin 표시 |
| `not_run` | connector, table, source, 기간, 또는 coverage가 없어 실행하지 못함 | `NOT_RUN`과 reason 표시 |
| `blocked` | 가격 부재, 거래 불가, execution boundary 위반처럼 검증을 계속하면 위험한 상태 | `BLOCKED` 후보로 표시 |

### 대상 진단별 데이터 계약

| 검증 | actual data 요구사항 | bridge / proxy fallback | `NOT_RUN` 또는 `REVIEW` 조건 | compact evidence |
|---|---|---|---|---|
| 2. Asset Allocation Fit | ETF holdings 기반 `asset_class`, `sector`, `country`, component target weight | ticker bucket, strategy family, component label | 핵심 ETF holdings가 없으면 `NOT_RUN`; 일부만 있으면 `REVIEW` | asset-class 비중, coverage count, missing ETF |
| 3. Concentration / Overlap / Exposure | holdings row의 `holding_id` / symbol / name / weight, top holding concentration | component weight concentration, ticker sector proxy | holdings overlap을 계산할 수 없으면 `NOT_RUN`; wrapper-level concentration만 있으면 `REVIEW` | top overlap, top concentration, coverage status |
| 5. Regime / Macro Suitability | FRED `VIXCLS`, `T10Y3M`, `BAA10Y` 기준일 snapshot | benchmark recent return / drawdown / volatility proxy | 기준일 근처 macro snapshot이 없으면 `NOT_RUN`; 일부 series만 있으면 `REVIEW` | series value, observation date, staleness |
| 6. Sentiment / Risk-On-Off Overlay | VIX / credit spread / yield curve 변화율과 level | benchmark risk-on/off proxy | macro-derived context가 없으면 `NOT_RUN`; proxy만 있으면 `REVIEW` | risk-on/off label, supporting series, stale count |
| 7. Stress / Scenario Diagnostics | portfolio / benchmark curve, stress calendar, component contribution, optional exposure / macro context | curve-only stress return / MDD | stress window가 후보 기간 밖이면 `NOT_RUN`; 원인 근거가 부족하면 `REVIEW` | stress return, MDD, benchmark spread, interpretation |
| 9. Leveraged / Inverse ETF Suitability | provider product metadata: leverage factor, inverse 여부, daily objective, holding-period note | ticker pattern, known ETF list | 상품 metadata가 없으면 `REVIEW`; ticker proxy도 없으면 `NOT_RUN` | flagged ETF, product type, mismatch reason |
| 10. Operability / Cost / Liquidity | expense ratio, AUM / net assets, ADV / dollar volume, spread, premium/discount, NAV / market price | DB volume ADV, `nyse_asset_profile` total_assets / bid / ask | 비용 / spread / AUM 중 핵심 field가 없으면 `REVIEW`; 거래 데이터 없으면 `NOT_RUN` 또는 `BLOCKED` | per-ETF cost/liquidity summary, missing fields |
| 11. Robustness / Sensitivity / Overfit | drop-one, weight +/- perturbation, window perturbation, optional runtime sensitivity result | local simple sensitivity, trial count, source metadata | sensitivity 계산 입력이 없으면 `NOT_RUN`; 단순 perturbation만 있으면 `REVIEW` | perturbation count, worst case, overfit review gap |

### P2-0 확정 사항

- P2는 위 8개 진단을 우선 정상화한다.
- 1, 4, 8, 12번 진단은 P2의 주 대상이 아니다. 다만 provider context가 생기면 보조 evidence를 받을 수 있다.
- 데이터 수집은 P2-2 이후 단계의 구현 수단이다. P2-0에서는 source / storage / fallback 계약만 고정한다.
- full holdings row, full macro series, full raw provider response는 `PRACTICAL_VALIDATION_RESULTS.jsonl`에 저장하지 않는다.
- JSONL에는 coverage, compact evidence, missing reason, staleness, source reference만 저장한다.

## P2-1 완료 산출물: schema / ingestion field 계약

상태: `completed`

P2-1은 P2-0에서 정한 진단 계약을 실제 수집 / 저장 / 로딩 가능한 데이터 계약으로 바꾸는 단계다.
이 단계에서는 제품 코드를 수정하지 않고, 다음 구현에서 추가할 table, business key, 필수 field,
fallback 판정 기준을 먼저 고정한다.

### P2-1 기준 table 경계

| table | 역할 | 직접 정상화하는 진단 | business key |
|---|---|---|---|
| `finance_meta.etf_operability_snapshot` | ETF 비용, 규모, spread, NAV / premium-discount, leverage / inverse 상품 정보를 저장 | 9, 10 | `(symbol, as_of_date, source)` |
| `finance_meta.etf_holdings_snapshot` | ETF 내부 보유종목 row를 저장 | 2, 3 | `(fund_symbol, as_of_date, source, holding_id)` |
| `finance_meta.etf_exposure_snapshot` | holdings에서 집계한 asset class / sector / country exposure를 저장 | 2, 3, 7 | `(fund_symbol, as_of_date, source, exposure_type, exposure_name)` |
| `finance_meta.macro_series_observation` | FRED 계열 market-context series를 long-form으로 저장 | 5, 6, 7 | `(series_id, observation_date, source)` |

기존 table은 새 provider table의 대체물이 아니라 bridge / proxy source로만 사용한다.

| 기존 데이터 | P2에서 쓰는 방식 | 한계 |
|---|---|---|
| `finance_price.nyse_price_history` | ADV / dollar volume / benchmark price-action proxy | 비용, spread, holdings, NAV를 직접 알 수 없음 |
| `finance_meta.nyse_asset_profile` | `total_assets`, `bid`, `ask`, `fund_family`, `status` bridge | coverage가 낮고 expense ratio / holdings / premium-discount 없음 |

### 검증별 actual 최소조건

| 검증 | actual 판정 최소조건 | bridge / proxy 판정 | `NOT_RUN` 또는 `REVIEW` 기준 |
|---|---|---|---|
| 2. Asset Allocation Fit | 핵심 ETF의 holdings 또는 exposure가 target weight 기준 80% 이상 커버되고 `asset_class` exposure가 계산됨 | ticker bucket 또는 strategy family 기반 분류 | 50~80% coverage면 `REVIEW`, 50% 미만이면 `NOT_RUN` |
| 3. Concentration / Overlap / Exposure | holdings row에 `holding_id` 또는 fallback key, `weight_pct`가 있고 주요 ETF coverage가 80% 이상 | component weight concentration 또는 sector ticker proxy | holdings overlap 계산이 불가능하면 `NOT_RUN`, wrapper-level concentration만 있으면 `REVIEW` |
| 5. Regime / Macro Suitability | `VIXCLS`, `T10Y3M`, `BAA10Y`가 기준일 lookback 안에서 snapshot으로 로딩됨 | benchmark recent return / drawdown / volatility proxy | 일부 series만 있거나 stale이면 `REVIEW`, 전부 없으면 `NOT_RUN` |
| 6. Sentiment / Risk-On-Off Overlay | VIX level / change, credit spread, yield curve 중 2개 이상이 기준일 context로 계산됨 | benchmark risk-on/off proxy | macro-derived context가 1개 이하이면 `REVIEW` 또는 `NOT_RUN` |
| 7. Stress / Scenario Diagnostics | portfolio / benchmark curve와 stress calendar가 있고, 가능하면 exposure / macro context가 결합됨 | curve-only stress return / MDD | 후보 기간 밖 stress는 `NOT_RUN`, 원인 설명 근거가 부족하면 `REVIEW` |
| 9. Leveraged / Inverse ETF Suitability | provider product metadata가 leverage factor, inverse 여부, daily objective 여부를 확인 | ticker pattern / known leveraged ETF list | provider metadata가 없으면 `REVIEW`, ticker proxy도 없으면 `NOT_RUN` |
| 10. Operability / Cost / Liquidity | 비용, 규모, 유동성, spread, NAV/premium-discount 5개 묶음 중 3개 이상이 provider 또는 명시 source로 확인 | price history ADV, asset_profile AUM / bid / ask bridge | 핵심 비용 / 거래 가능성 근거가 부족하면 `REVIEW`, 가격 / 거래량도 없으면 `NOT_RUN` 또는 `BLOCKED` |
| 11. Robustness / Sensitivity / Overfit | drop-one, weight perturbation, window perturbation 중 2개 이상 계산되고 worst-case가 요약됨 | local simple perturbation 또는 trial count summary | 계산 입력이 부족하면 `NOT_RUN`, 단순 perturbation만 있으면 `REVIEW` |

### 수집 / 저장 판정 규칙

- official issuer 또는 FRED에서 온 row는 필요한 field coverage를 충족할 때만 `actual`로 쓴다.
- 기존 DB 가격 / 거래량 / asset profile에서 만든 값은 `bridge` 또는 `proxy`로 남기고 `actual`처럼 승격하지 않는다.
- provider가 일부 field만 주면 `partial` coverage로 저장하고 Practical Validation에서는 `REVIEW`로 읽는다.
- source 실패, 미지원 ticker, 기준일 부재는 수집 summary와 `NOT_RUN` reason으로 남긴다.
- full holdings row, full macro observation, raw provider response는 DB에 저장하고 JSONL result에는 compact evidence만 남긴다.

### 다음 구현 기준

P2-2부터는 이 계약을 기준으로 진행한다.

1. `finance/data/db/schema.py`에 위 4개 table schema를 추가한다.
2. ETF operability collector는 공식 provider row와 기존 DB bridge row의 출처를 분리한다.
3. holdings collector는 `holding_id`가 없을 때 provider별 fallback key를 안정적으로 만든다.
4. macro collector는 FRED `series_id`, `observation_date`, `source` 기준으로 UPSERT한다.
5. loader는 table이 비어 있어도 빈 context와 `NOT_RUN` reason을 안정적으로 반환한다.

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

### 진단 축 A. Cost / Liquidity / ETF Operability Connector

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

### 진단 축 B. ETF Holdings / Sector Look-through

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

### 진단 축 C. Macro / Sentiment Connector

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

### 진단 축 D. Stress Interpretation 고도화

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

### 진단 축 E. Robustness / Sensitivity 해석 보강

이 항목은 12개 진단 중 `11. Robustness / Sensitivity / Overfit`을 정상화하기 위한 보강이다.
runtime 재계산까지 포함할지는 구현 중 결정하되, P2에서는 최소한 sensitivity 결과와 해석이
사용자가 이해할 수 있게 표시되는 것을 목표로 한다.

목표:

- 단순 weight perturbation 또는 기존 runtime이 허용하는 작은 설정 변경 결과를 과최적화 검토 근거로 읽게 한다.

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
official provider / API / CSV / XLSX / yfinance fallback
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
- provider data는 ingestion에서 수집하고 MySQL에 저장한다.
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

### 작업 단위 1. P2 대상 검증 항목 / 필요 데이터 확정

목표:

- 12개 진단 중 P2에서 정상화할 항목을 확정한다.
- 각 항목에 필요한 actual data, proxy fallback, `NOT_RUN` 사유를 정의한다.
- provider source map과 DB schema는 이 진단 목표를 기준으로 설계한다.

주요 작업:

- P2 대상 진단: 2, 3, 5, 6, 7, 9, 10, 11
- 진단별 필요 데이터: holdings, exposure, macro, operability, product metadata, stress/sensitivity context
- ETF source map: iShares / BlackRock, SSGA / SPDR, Invesco, yfinance fallback
- Macro source map: FRED `VIXCLS`, `T10Y3M`, `BAA10Y` 우선
- schema: `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`, `macro_series_observation`
- collector skeleton: `finance/data/etf_provider.py`, `finance/data/macro.py`
- UPSERT 기준: symbol / as_of_date / source, 또는 series_id / observation_date / source

검증:

- schema sync가 반복 실행 가능
- 수집기가 빈 source / 실패 source를 실패 summary로 반환
- 기존 Practical Validation은 아직 외부 수집에 의존하지 않음
- 각 대상 진단마다 actual / proxy / `NOT_RUN` 상태 정의가 존재

### 작업 단위 2. Cost / Liquidity / Operability 데이터 수집

목표:

- ETF 비용, 규모, spread, NAV / premium-discount, 거래 가능성 snapshot을 DB에 저장한다.
- 공식 provider 값과 기존 DB bridge 값을 분리한다.

현재 구현 상태:

- P2-2A `implementation_complete`
- `etf_operability_snapshot` schema, 기존 DB 기반 `db_bridge` 수집, UPSERT 저장, loader read path를 추가했다.
- P2-2B `initial_implementation_complete`
- iShares / SSGA / Invesco official page 기반 row를 같은 table에 `source_type=official`로 저장한다.

주요 작업:

- P2-2A 완료: `nyse_price_history` 기반 ADV / dollar volume proxy 계산
- P2-2A 완료: `nyse_asset_profile` 기반 AUM / bid / ask bridge 저장
- P2-2A 완료: `coverage_status`를 `bridge`, `proxy`, `missing`으로 저장
- P2-2B 완료: iShares `AOR`, `IEF`, `TLT` official row 수집
- P2-2B 완료: SSGA / SPDR `SPY`, `BIL`, `GLD` official row 수집
- P2-2B 완료: Invesco `QQQ` official partial row 수집
- P2-2B 완료: official provider row에서 `actual`, `partial`, `missing`, `error` coverage 저장
- P2-2B 후속: QQQ의 AUM / NAV / spread actual endpoint와 initial source map 밖 ETF 확장

검증:

- P2-2A 기준으로 loader가 `etf_operability_snapshot`을 읽을 수 있다.
- P2-2B 기준으로 loader가 `source=ishares|ssga|invesco`, `source_type=official` row를 읽을 수 있다.
- provider table이 없거나 비어 있어도 loader는 빈 DataFrame을 반환한다.
- official provider field가 없는 항목은 `missing_fields_json`에 남는다.
- Practical Validation 화면 반영은 P2-5에서 진행한다.

### 작업 단위 3. ETF holdings / exposure 데이터 수집

목표:

- ETF 내부 holdings와 sector / asset class exposure를 DB에 저장한다.
- holdings가 없으면 추정으로 채우지 않고 `NOT_RUN` 또는 ticker proxy fallback으로 남긴다.

주요 작업:

- iShares AOR / IEF / TLT holdings CSV adapter
- SSGA SPY / GLD / BIL daily holdings XLSX adapter
- Invesco QQQ holdings endpoint 안정성 확인 및 adapter
- AOR 같은 ETF-of-ETF는 1차 holdings와 2차 look-through 가능 여부를 분리 기록

검증:

- holdings row count와 as-of date가 저장된다.
- exposure aggregation이 holdings weight 합계와 크게 어긋나지 않는다.
- full holdings row는 JSONL에 저장하지 않는다.

### 작업 단위 4. Macro / Sentiment 데이터 수집

목표:

- VIX / yield curve / credit spread snapshot을 DB에 저장한다.
- sentiment는 별도 composite crawling보다 FRED 기반 market-context proxy로 시작한다.

주요 작업:

- FRED `series/observations` collector
- 1차 series: `VIXCLS`, `T10Y3M`, `BAA10Y`
- optional series: HY OAS 등은 coverage 기간을 확인한 뒤 추가
- FRED API key는 hardcode하지 않고 env / config boundary로 둔다.

검증:

- 지정 기간 row count가 확인된다.
- 최신 observation date와 staleness가 계산된다.
- macro data가 없으면 Practical Validation에서 `NOT_RUN`으로 남길 수 있다.

### 작업 단위 5. Loader / Provider Coverage context

목표:

- 수집된 DB snapshot을 Practical Validation이 읽을 수 있는 context로 변환한다.
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

검증:

- provider table이 비어 있어도 빈 context 또는 `NOT_RUN`이 안정적으로 반환된다.
- provider snapshot과 DB price proxy 출처가 분리된다.

### 작업 단위 6. Practical Validation diagnostics / UI 연결

목표:

- provider context를 각 Practical Validation domain에 연결한다.
- 기존 proxy fallback은 유지하되, actual provider data가 있으면 우선 사용한다.

검증:

- operability / holdings / macro coverage가 화면과 result row에 compact evidence로 남는다.
- 기존 candidate / saved result / Final Review 흐름이 깨지지 않는다.

### 작업 단위 7. Stress Interpretation

목표:

- stress window별 숫자와 함께 해석 문장, 원인 추정, Final Review 질문을 만든다.

검증:

- 후보 기간 밖 stress는 `NOT_RUN`
- 후보 기간 안 stress는 return / MDD / benchmark spread / interpretation 표시

### 작업 단위 8. QA / P2 종료 판단

목표:

- P2 대상 진단이 정상화됐는지 확인한다.
- "데이터가 있어서 검증됨"과 "데이터가 없어서 `NOT_RUN`"이 화면과 result row에서 모두 명확한지 확인한다.

검증:

- provider table이 비어 있어도 Practical Validation이 깨지지 않는다.
- actual provider data가 있는 항목은 proxy보다 우선 사용된다.
- proxy만 가능한 항목은 `REVIEW` 또는 proxy origin으로 표시된다.
- 실행하지 못한 항목은 `NOT_RUN` reason이 남는다.
- Final Review에서 provider gap / stress gap / sensitivity gap을 판단 근거로 읽을 수 있다.

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
| ETF provider | 공식 issuer source 우선: iShares / BlackRock, SSGA / SPDR, Invesco. yfinance는 bridge / fallback |
| Holdings provider | iShares AOR / IEF / TLT CSV부터 구현하고, SSGA holdings XLSX와 Invesco QQQ endpoint를 같은 adapter 구조로 확장 |
| Macro source | FRED `series/observations` 기반 long-form series table |
| Sentiment source | FRED 기반 VIX / credit spread / yield curve를 1차 sentiment proxy로 쓰고 Fear & Greed는 optional |
| Stress interpretation rule | rule-based template로 시작하고, 숫자 / exposure / component contribution 기반 문장 생성 |
| Sensitivity runtime 포함 여부 | P2에서는 최소 해석 정상화, 실제 strategy-specific runtime sweep은 필요 시 후속으로 분리 가능 |

## 결론

P2는 새 전략을 만드는 작업이 아니라,
Practical Validation이 이미 가진 12개 diagnostics를 실제 provider data와 더 좋은 해석으로 보강하는 단계다.

첫 구현은 UI가 아니라 provider data collection foundation이다.
공식 provider / FRED 데이터를 ingestion에서 DB에 저장한 다음,
loader와 Practical Validation connector를 붙인다.
기존 `nyse_asset_profile`과 price history는 coverage gap을 설명하는 bridge / fallback으로 유지한다.
