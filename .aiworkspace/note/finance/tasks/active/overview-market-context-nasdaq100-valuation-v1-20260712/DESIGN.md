# Overview Market Context Nasdaq-100 Valuation V1 Design

Status: Proposed — User Review Required
Last Updated: 2026-07-12

## Decision Summary

Market Context에 `Nasdaq-100 · QQQ proxy` option을 추가한다. 데이터는 유료 aggregate provider가 아니라 SEC QQQ holdings, SEC filing-aware diluted EPS, DB EOD price를 결합해 재구성한다. 결과는 trailing P/E와 EPS가 맞지만 `Nasdaq 공식 P/E/EPS`가 아니라 `공개 공시 기반 재구성값`이다.

Graph 2의 현재값과 적정가격은 NDX가 아니라 QQQ 가격 단위로 표시한다. 이 선택은 별도 NDX 가격 사용권 검토를 피하고 이미 DB에 있는 장기 QQQ EOD를 활용하기 위한 것이다.

## Alternatives Considered

### A. SEC QQQ Public Reconstruction — Selected

- QQQ N-PORT/N-30B-2 holdings
- SEC company filing actuals
- existing DB QQQ/component EOD
- existing FOMC SEP

장점은 account/token/subscription이 없고 historical membership을 실제 holdings snapshot으로 복원한다는 점이다. 단점은 공식 Nasdaq aggregate가 아니며 identifier, ADR, multi-class, coverage 계산을 직접 책임져야 한다.

### B. Direct Aggregate API — Deferred

GuruFocus/FactSet/LSEG 같은 provider에서 index P/E/EPS를 직접 받으면 가장 단순하지만 account/token/license가 필요하거나 무료 entitlement가 확인되지 않았다.

### C. Current Constituents Retroactive — Rejected

현재 QQQ 구성 종목을 과거 전체에 적용하면 survivorship bias가 생기므로 사용하지 않는다.

## Data Coverage Contract

확인된 공개 holdings history:

- QQQ N-PORT: 2019-09-30~2026-03-31, 27 quarterly snapshots
- QQQ N-30B-2 annual schedules: 최소 2014-09-30 이후 확인
- current Invesco public holdings: 최근 N-PORT 이후 gap 보조

사용 방식:

- 2019-09 이후: quarterly N-PORT anchor
- 2015-09~2018-09: annual N-30B-2 warmup anchor
- 최신 N-PORT 이후: current Invesco official snapshot

5년 history의 초기 rolling window에는 annual anchor가 포함될 수 있다. UI는 이를 strict historical index reconstruction이 아니라 `과거 시점 재구성`으로 표시한다.

## Monthly Reconstruction Formula

각 observation month에서 latest eligible holdings snapshot을 선택한다. snapshot 이후 월말까지 종목 가격 변화로 weight를 drift시키고 다시 정규화한다.

```text
drifted_value_i = snapshot_weight_i × month_end_price_i / snapshot_price_i
month_weight_i = drifted_value_i / Σ(drifted_value)
```

종목 TTM diluted EPS는 해당 월말까지 `available_at`이 확인된 SEC filing만 사용한다.

- single-quarter EPS: 약 3개월 duration fact
- Q4 EPS: FY EPS - Q1 - Q2 - Q3
- TTM EPS: latest four discrete quarters
- negative EPS: 제외하지 않고 negative earnings yield로 포함
- foreign issuer/ADR conversion이 불명확하면 missing coverage로 둠

```text
security_earnings_yield_i = TTM diluted EPS_i / month_end_price_i
covered_weight = Σ(month_weight_i where EPS and price are valid)
portfolio_earnings_yield = Σ(month_weight_i × security_earnings_yield_i) / covered_weight
reconstructed_trailing_pe = 1 / portfolio_earnings_yield
reconstructed_qqq_ttm_eps = QQQ month_end price / reconstructed_trailing_pe
```

covered weight가 95% 미만이거나 aggregate earnings yield가 양수가 아니면 그 달은 complete valuation row가 아니다. missing weight를 0 earnings로 간주하거나 임의 sector median으로 채우지 않는다.

공개 Nasdaq trailing P/E 관측값을 calibration fixture로 사용한다. production gate는 관측점 median absolute percentage error `<= 5%`, 각 관측점 최대 오차 `<= 10%`다. 이는 공식값 일치를 보장하는 기준이 아니라 proxy가 방향과 규모를 잃지 않았는지 차단하는 최소 품질 기준이다.

## Source And Persistence Architecture

```text
SEC QQQ N-PORT / N-30B-2 + current Invesco holdings
  -> finance/data/nasdaq100_valuation.py
  -> finance_meta.etf_holdings_snapshot

SEC detailed statements + component/QQQ EOD + stored holdings
  -> monthly reconstruction
  -> finance_meta.nasdaq100_monthly_valuation
  -> finance/loaders/nasdaq100_valuation.py
  -> app/services/overview/nasdaq100_valuation.py
  -> Market Context React selector
```

### Existing Table Extension

`finance_meta.etf_holdings_snapshot`에 optional identifier/timing fields를 추가한다.

- `cusip`
- `isin`
- `lei`
- `issuer_cik`
- `filing_date`

기존 provider rows는 null을 허용해 호환성을 유지한다. SEC rows는 CUSIP을 stable holding identity로 우선 사용한다.

### Derived Monthly Table

`finance_meta.nasdaq100_monthly_valuation`의 business key는 `(observation_month, proxy_symbol, source)`다.

주요 필드:

- `observation_month`
- `proxy_symbol` = `QQQ`
- `qqq_price`
- `reconstructed_ttm_eps`
- `trailing_pe`
- `earnings_yield`
- `coverage_weight_pct`
- `unmapped_weight_pct`
- `holding_snapshot_date`
- `holding_snapshot_quality` = `annual_anchor` / `quarterly_anchor` / `current_issuer_snapshot`
- `earnings_available_through`
- `data_quality` = `reconstructed_actual` / `partial` / `blocked`
- source identity, collected_at, error

원천 holdings와 derived monthly rows를 분리하며 repeat collection은 stable keys로 UPSERT한다.

## Holding Identity Resolution

순서는 다음과 같다.

1. CUSIP exact match against current/historical official QQQ rows
2. existing symbol/alias/SEC company ticker association
3. normalized issuer name match
4. reviewed explicit overrides for ADR, former ticker, and share class

자동 fuzzy match만으로 actual coverage를 올리지 않는다. unresolved holdings와 weight는 결과 evidence에 남긴다.

## Service Design

새 Nasdaq service는 S&P service의 index-neutral pure calculations를 재사용한다.

- 60개월 log(P/E) primary distribution
- 36개월 sensitivity
- `-2σ/-1σ/center/+1σ/+2σ`
- FOMC SEP GDP+PCE growth scenarios
- expected EPS × fair multiple QQQ band
- 1/3/5-year historical scenario

S&P source resolver와 Shiller provisional logic은 재사용하지 않는다. Nasdaq source contract는 reconstructed actual과 coverage evidence를 별도로 제공한다.

Read model metadata:

- `instrument.key = nasdaq100_qqq_proxy`
- `instrument.index_name = Nasdaq-100`
- `instrument.price_symbol = QQQ`
- `instrument.price_label = QQQ`
- `instrument.source_quality = public_filing_reconstructed_proxy`
- `instrument.official_index_aggregate = false`

## React Design

기존 화면 상단에 index selector를 추가한다.

```text
[ S&P 500 ] [ Nasdaq-100 · QQQ proxy ]
```

기본 선택은 기존 동작을 보존하도록 S&P 500이다. React는 index별 nested read model을 선택해 렌더링하며 계산하지 않는다. hard-coded `SPX`, `S&P 500`, `Shiller` copy는 instrument/source metadata로 바꾼다.

Nasdaq 선택 시:

- Graph 1: `최근 5년 Nasdaq-100 멀티플 구간`
- Graph 2: `FOMC 예상 실적 기반 QQQ 가격 시나리오`
- source badge: `SEC QQQ 보유내역 + SEC 기업 실적`
- quality badge: `공개 공시 기반 재구성`
- coverage: weighted coverage와 holdings basis date
- limitation: `Nasdaq 공식 index-level P/E/EPS가 아님`

운영 job/status/row count 패널은 추가하지 않는다.

## Error And Blocking Rules

- holdings history 부족: `INSUFFICIENT_HOLDINGS_HISTORY`
- identifier mapped weight 부족: `INSUFFICIENT_IDENTITY_COVERAGE`
- EPS/price weighted coverage <95%: `INSUFFICIENT_EARNINGS_COVERAGE`
- non-positive aggregate earnings yield: `NON_POSITIVE_AGGREGATE_EARNINGS`
- 60 complete months 부족: Graph 1 blocked
- 1/3/5 history point별 warmup 부족: 해당 period만 disabled/insufficient 표시
- S&P model은 Nasdaq failure와 독립적으로 계속 렌더링

## Automation

- SEC holdings discovery: quarterly/weekly-safe check
- current Invesco holdings: existing job cadence reuse
- component statements/prices: existing ingestion state를 읽고 missing coverage를 보고
- derived monthly materialization: Overview valuation job에서 daily rerun 가능
- UI render path는 remote call을 하지 않음

## Testing And QA

### Unit

- SEC Atom discovery and N-PORT XML normalization
- N-30B-2 schedule parser fixtures
- CUSIP/name/override mapping
- Q4 and TTM diluted EPS derivation
- negative EPS inclusion
- weight drift and 95% coverage gate
- idempotent UPSERT and schema sync

### Service Contract

- Nasdaq read model source/quality/basis fields
- 60m/36m log distribution
- FOMC QQQ scenarios
- 1/3/5 history options
- S&P independent render when Nasdaq blocked
- React selector and dynamic SPX/QQQ copy

### Integration / Browser

- actual DB backfill and derived row count/date/coverage smoke
- desktop and narrow viewport selector/hover/period QA
- screenshot 1장 generated artifact로 생성하되 stage하지 않음

## Acceptance Criteria

- account/token/subscription 없이 source backfill이 실행된다.
- 60개월 complete reconstructed P/E와 current QQQ EPS proxy가 생성된다.
- weighted coverage와 basis evidence가 UI에 표시된다.
- 공개 P/E calibration이 median 5%/maximum 10% gate를 통과한다.
- Graph 2 current QQQ band와 1/3/5-year history가 실제 숫자로 표시된다.
- 공식 Nasdaq aggregate 또는 analyst consensus로 오인시키는 copy가 없다.
- tests, DB smoke, Browser QA, docs sync, coherent Korean commit이 완료된다.
