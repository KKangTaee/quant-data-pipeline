# Nasdaq-100 Index EPS / P/E Source Benchmarks

Status: Complete
Last Updated: 2026-07-14

## Research Question

Nasdaq-100 가치평가 그래프에 필요한 60개월 trailing P/E와 current/monthly TTM EPS를 합법적이고 자동화 가능한 방식으로 어떻게 확보할 것인가?

## Selection Criteria

- NDX index-level aggregate 제공 여부
- 60개월 즉시 backfill 가능성
- API/파일 자동화 가능성
- 가격·EPS·P/E 기준일과 PIT 설명력
- 라이선스와 상대 비용
- 현재 DB와의 통합 난이도

## Benchmark Matrix

| Source | Direct NDX P/E | Direct NDX EPS | 60m Backfill | Automation | Cost Signal | Evidence | Fit |
|---|---:|---:|---:|---:|---|---|---|
| QQQ SEC N-PORT + SEC actual 자체 산출 | 직접 제공 아님 | 직접 제공 아님 | 가능(22 quarterly snapshots, 2020-12~2026-03) | SEC public API/XML | 무료, 계정/token 불필요 | Documented inputs + Inferred formula | no-auth V1 권장 |
| SEC actual + Tiingo EOD 보강 | 직접 제공 아님 | SEC에서 자체 계산 | 가능성이 높음 | SEC public API + Tiingo REST | 가격은 무료 계정/token, 월 500 symbols·일 1,000 calls, internal-only | Documented + catalog smoke | 현재 gap 복구 최우선 대안 |
| SEC N-PORT implied price anchor | 직접 제공 아님 | 직접 제공 아님 | 분기 공개 snapshot | SEC public filing/data set | 무료, 계정/token 불필요 | Observed local DB + Documented fields | anchor 검증/제한적 fallback |
| Alpha Vantage Free | 없음 | 없음 | delisted full history는 불가 | REST + free key | 무료 25 calls/day, full daily history는 premium | Documented | primary gap 복구 부적합 |
| SimFin Free | 없음 | constituent fundamentals | 5년 | API/bulk + free account | 무료, 5년 delayed/history | Documented | 119개월에는 부족 |
| GuruFocus Economic Data API | 일별 | 분기별 | 가능성이 높음(5Y/20Y chart 및 historical endpoint) | REST + account token | Economic Data는 base plan 제외 add-on `+$90/month` 또는 PAYG `$0.10/request`이며 PAYG 초기 `$100` top-up 필요 | Observed + Documented | 무료 후보 제외, 유료 선택지 |
| FactSet Benchmarks API | index ratios endpoint | per-share/aggregate content 기반 | 가능 | REST/SDK | entitlement/quote | Documented | Enterprise 최우선 |
| LSEG I/B/E/S Global Aggregates / Datastream | major index aggregate/valuation | actual/estimate aggregate 계열 | 가능성이 높음 | DSWS/FTP/SFTP | enterprise quote | Documented + NDX coverage는 확인 필요 | Enterprise 대안 |
| Bloomberg Data License | historical fundamentals/estimates/price | field entitlement에 따라 가능 | 가능성이 높음 | REST/SFTP/cloud | enterprise quote | Claimed; exact NDX field unknown | 교차검증/대안 |
| Nasdaq GIW/GIFFD + SEC 자체 산출 | 직접 제공 아님 | 직접 제공 아님 | weights entitlement가 있으면 가능 | Web service/file + SEC API | Nasdaq license + 구현비 | Documented/Inferred | 공식 구성 정밀화 |

## Source Notes

### QQQ SEC N-PORT + SEC Actual Self-Construction

- Category: free public filing reconstruction
- Verified coverage:
  - QQQ CIK `0001067839`
  - 22 quarterly N-PORT filings from 2020-12-31 through 2026-03-31
  - 2025-03-31 sample has 101 holdings with name/CUSIP/ISIN/quantity/value/weight
  - SEC EDGAR lookup APIs require no authentication or API key
- Formula candidate:

```text
security earnings yield = filing-aware TTM EPS / same-security month-end price
portfolio earnings yield = sum(QQQ weight × security earnings yield)
reconstructed P/E = 1 / portfolio earnings yield
reconstructed QQQ EPS = QQQ price / reconstructed P/E
```

- Strong fit:
  - quarterly holdings cover the full requested five-year window without survivorship backfill
  - QQQ EOD and SEC statements already exist in the project
  - no account, token, paid plan, scraping, or access bypass
- Limit:
  - QQQ proxy is not the official Nasdaq aggregate
  - N-PORT is quarterly, so monthly rows require price drift between anchors
  - CUSIP/ISIN to ticker/CIK mapping, ADR ratios, multiple classes and foreign issuer EPS need explicit rules
  - 2023 special rebalance and tracking cash can create local deviations
  - public filings arrive after period end; UI must distinguish reconstructed history from contemporaneously available data
- Evidence label: Documented inputs + Inferred aggregate

### GuruFocus Economic Data API

- Category: lower-cost commercial time-series API
- Relevant workflow:
  - indicator `6778`: Nasdaq 100 PE Ratio, daily
  - indicator `5870`: Nasdaq 100 Earnings per Share, quarterly
  - `GET /economic/{nameOrId}`가 전체 historical date/value series를 반환
- Current consistency check:
  - Nasdaq official NDX 29,825.11 / GuruFocus P/E 31.89 = 935.25
  - GuruFocus quarterly EPS = 935.177
  - date가 완전히 같지 않은 단순 점검인데도 차이는 약 0.008%
- Strong fit:
  - graph 1은 일별 P/E를 월말로 downsample하면 즉시 60개 이상 확보 가능
  - graph 2 current EPS는 동일일 NDX/P/E로 역산 가능
  - 분기 EPS는 독립 sanity check로 사용 가능
- Limit:
  - aggregate 계산 방법과 release-vintage가 공개되지 않음
  - `EPS` indicator가 TTM인지 설명에 명시되지 않으므로, production label은 direct TTM으로 단정하지 않고 trailing P/E 기반 역산값을 primary로 사용해야 함
  - Economic Data는 무료 base entitlement가 아니며 유료 add-on/PAYG 승인 후에만 authenticated smoke 가능
  - 데이터 장기 저장/내부 chart 표시/계약 종료 후 보유 권한은 Data API Agreement 확인 필요
  - public indicator HTML scraping은 사용하지 않음
- Evidence label: Documented + current cross-check Inferred

#### 2026-07-14 access refresh

- 동적 가격표의 실제 feature cell을 확인한 결과 `Economic Data`는 Free/Builder/Commercial 기본 열 모두 `minus`이고, `Economic Indicator List`만 core check로 표시된다.
- Endpoint Explorer도 `Economic Data`를 `addon`, `Economic Indicator List`를 `core`로 분류한다.
- Free pricing summary에서 Economic Data 선택 시 `+$90/month`이며, PAYG 표에는 `$0.10/request`와 초기 `$100` credit top-up이 표시된다.
- `GET /data/economic/6778` 무인증 호출은 `401 Invalid token`을 반환하므로 Shiller 파일처럼 no-account/no-token으로 받을 수는 없다.
- indicator `6778`은 일별 Nasdaq-100 P/E, `5870`은 분기 Nasdaq-100 EPS를 공개 페이지에서 계속 제공한다.
- 따라서 Free token만으로 두 indicator의 historical detail을 수집하는 경로는 승인하지 않는다. 유료 add-on/PAYG를 선택할 때만 authenticated payload smoke를 수행한다.
- Data API Agreement는 subscribed product의 승인된 내부 product/business use를 허용하지만 raw API output의 공개·재판매·재배포를 금지한다. 계약 종료 뒤 장기 보유는 명시되지 않아 유료 도입 시 서면 확인이 필요하다.
- 현재 화면이 QQQ 가격 단위이면 `5870`의 NDX EPS를 직접 넣지 않는다. `6778` P/E를 월말 downsample하고 `QQQ price / P/E`로 QQQ-unit EPS proxy를 파생하며, `5870`은 NDX same-date identity check에만 사용한다.

### 2026-07-14 Free Alternative Recheck

- **Nasdaq/FRED/Alpha Vantage/nfin**: 무료 또는 무계정 NDX/QQQ 가격 이력은 제공하지만 historical index P/E/EPS는 제공하지 않는다.
- **Nasdaq research PDFs / Invesco QQQ fact sheet**: 장기 P/E chart 또는 분기 현재 P/E snapshot은 있으나 월별 machine-readable series/API가 아니다. Nasdaq chart의 underlying source도 Bloomberg/FactSet이므로 chart digitization을 production source로 사용하지 않는다.
- **Business Quant Free API**: SEC 기반 기업 TTM statements, CIK/CUSIP/ticker mapping, corporate actions를 무료 계정/API key로 제공해 constituent reconstruction 보조에는 유용하다. 다만 direct NDX aggregate가 없고, pricing table상 Free financial statement history는 3년이며 30 calls/day라 5년 direct 대체 원천은 아니다.
- **MacroMicro**: 월별 Nasdaq-100 forward P/E를 보여주지만 trailing P/E와 의미가 다르며 CSV/API 자동 통합은 유료 Business/API Essential/Custom 범위다. 로그아웃 화면에는 CSV 실행 control이 노출되지 않는다.
- **World PE Ratio**: 계정 없이 QQQ 기반 historical P/E chart를 보여주지만 documented API, 원천 계약, 자동 수집/재사용 허용 범위를 찾지 못했다. 사람용 cross-check만 허용한다.
- **Trendonify/VCP Scanner**: 공개 history가 있어도 Terms가 scraping/automated extraction을 금지하므로 collector 후보에서 제외한다.

결론적으로 `무료 + 60개월 + direct Nasdaq-100 aggregate + 자동화 + 내부 DB 저장 권리`를 동시에 만족한다고 검증된 외부 원천은 찾지 못했다. 무료 경로는 SEC QQQ N-PORT와 SEC actual을 결합한 자체 재구성뿐이다.

### 2026-07-14 Implementation Feasibility Recheck

#### Tiingo EOD free account

- 공식 EOD product는 raw/adjusted OHLC, dividend, split을 REST로 제공하고 최대 60년 이상 history를 표방한다.
- Starter는 `$0/month`, 시간당 50회, 일 1,000회, 월 1GB, 월 500 unique symbols이며 token이 필요하다. 23개 gap symbol backfill은 요청량 한도 안이다.
- 공식 `supported_tickers.zip`을 내려받아 local repair target과 대조한 결과 historical EOD가 필요한 23개 중 22개 exact symbol이 있었다: `ALXN`, `ANSS`, `ATVI`, `CA`, `CELG`, `CERN`, `CTXS`, `DISH`, `LLTC`, `MXIM`, `MYL`, `QRTEA`, `QVCA`, `SGEN`, `SHPG`, `SPLK`, `SRCL`, `VIAB`, `WBA`, `WFM`, `XLNX`, `YHOO`.
- exact `SYMC`는 없지만 successor `GEN` series가 1990년부터 존재한다. `SYMC -> NLOK -> GEN` alias를 issuer/name/date로 검증한 뒤만 사용한다.
- `CA`, `QRTEA`처럼 재사용 가능성이 있는 ticker는 symbol 문자열만 믿지 않고 name/start/end와 N-PORT identifier를 함께 검증한다.
- Tiingo fundamentals는 별도 add-on이므로 EOD만 보강하고 EPS canonical source는 SEC로 유지한다.
- free license는 개인 internal use에 한정된다. 다른 사용자에게 raw/derived Tiingo data를 표시하거나 공개 배포하려면 별도 license가 필요하다.

#### SEC reconstruction hardening

- 공식 SEC ticker-to-CIK 파일에서 현재 foreign/ADR target 16개 모두 CIK가 확인됐다. current identity 누락은 무료 public mapping으로 개선 가능하다.
- companyfacts smoke에서 ASML·BIDU·PDD·NXPI·AZN의 EPS 또는 net income/diluted shares fact가 확인됐다. non-USD/share, IFRS tag, 20-F cadence와 ADR ratio를 처리하면 기존 missing weight를 줄일 수 있다.
- 미국 상장 누락 종목만 복구하고 foreign/ADR는 계속 누락으로 둔 보수적 upper-bound 시뮬레이션도 119/119개월 coverage 95% 이상, 최저 96.319%를 만들었다.
- 단, 현재 FY-to-Q4 계산 오류와 split drift를 먼저 고치지 않으면 외부 데이터를 추가해도 잘못된 음수 EPS와 weight가 남는다.

#### N-PORT price anchor

- N-PORT position의 `market_value / shares`는 snapshot 시점의 실제 security-unit implied price다.
- local DB에서 historical EOD gap 23개 모두에 총 171개 implied-price anchor가 확인됐다.
- 이 값은 Tiingo payload 검증, symbol alias, split 검증에 강한 no-account 기준점이다.
- 현재 공개 N-PORT는 quarterly anchor만 제공하므로 anchor 사이 모든 월의 실제 EOD를 대체하지는 못한다. monthly public disclosure 확대도 2027/2028년으로 연기돼 현재 5년 backfill을 해결하지 않는다.

#### Rejected free alternatives

- Alpha Vantage는 free key와 delisted listing catalog는 유용하지만 daily full history가 premium이고 무료 호출량도 25/day라 historical delisted EOD primary source가 될 수 없다.
- SimFin Free는 API/bulk를 제공하지만 fundamentals/chart history가 5년이라 60개월 rolling band를 포함한 119개월 input window에 부족하다.
- direct public chart scraping은 앞선 약관·방법론 문제 때문에 계속 제외한다.

### MacroMicro Nasdaq-100 Forward P/E

- Public series observation:
  - series `23955`의 공식 제목은 `US - NASDAQ 100 Index - Forward PE Ratio`다.
  - frequency는 Month이고 최신 월·값은 로그아웃 상태에서도 표시된다.
  - 페이지 DOM에는 CSV 동의 모달이 포함되지만, 로그아웃 상태의 실제 visible control은 Share/Custom/Image/DIY/Enlarge뿐이며 CSV download trigger는 노출되지 않는다.
- Free/account boundary:
  - 공식 Help Center는 Free member를 제한된 chart viewing/save 용도로 설명하고, raw CSV는 Free/Prime/Max에 포함되지 않는다고 명시한다.
  - raw CSV download는 MM Business, 자동 API는 MM API Essential 또는 Custom 범위다.
  - 2026-07-14 표시 가격은 Business AI 연 `$6,000`, API Essential 연 `$5,000`이며 API Essential은 full historical data와 월 5,000 calls/downloads를 표방한다.
- Exact-series entitlement gap:
  - 공식 FAQ는 MacroMicro 자체 compiled exclusive indicator는 Custom에서만 download/API 가능하고 일부 partner data는 계약상 download/API가 불가능할 수 있다고 설명한다.
  - 공개 화면만으로 series `23955`가 Business/API Essential 목록에 실제 포함되는지 확정할 수 없다. 유료 검토 시 series ID를 지정해 payload sample, history 시작월, revision 정책, 내부 DB retention, 파생 차트 권한을 서면 확인해야 한다.
- Metric compatibility:
  - 현재 QQQ graph는 실제 희석 TTM EPS에서 계산한 trailing P/E 분포다.
  - MacroMicro 값은 예상 이익에 기초한 forward P/E이므로 기존 1/3/5년 중심·표준편차와 EPS/SEP 시나리오에 결측 대체값으로 섞을 수 없다.
  - 사용하려면 `Nasdaq-100 Forward P/E`라는 별도 analyst-consensus valuation track으로 분리하고 source/methodology를 다시 승인해야 한다.
- License boundary:
  - Terms는 사전 서면 동의 없는 data download와 재가공·배포를 금지하고, 일반 subscription data의 commercial-profit use와 derivative works도 제한한다.
  - 따라서 공개 chart scraping, 숨겨진 CSV modal 호출, undocumented endpoint 재현은 production collector 후보가 아니다.
- Verdict: **무료·무계정 trailing P/E source로 기각**. 유료 별도 forward-valuation 기능은 series entitlement와 서면 사용권을 받은 뒤에만 기술 검토 가능하다.

### Public Historical Chart Sites

- World PE Ratio는 QQQ 기반 Nasdaq-100 월별 P/E를 1990년부터 HTML chart data로 노출한다.
  - 장점: 계정 없이 5년 이상을 기술적으로 읽을 수 있다.
  - 한계: 원천 provider, aggregate earnings 산식, revision/PIT 계약, 자동 수집/재사용 권리가 명확하지 않다.
  - 판정: 사람용 교차검증만 허용하고 production collector에는 사용하지 않는다.
- Trendonify는 1990년부터의 월별 Nasdaq-100 P/E 표를 공개한다.
  - 한계: Terms가 사전 서면 허가 없는 scraping/crawling/automated extraction을 명시적으로 금지한다.
  - 판정: 자동 수집 source에서 제외한다.
- VCP Scanner는 SEC filings와 개별 종목 financials로 계산한 Nasdaq-100 P/E history를 공개한다.
  - 한계: Terms가 bulk scraping/harvesting을 금지하고, 공개값도 다른 provider보다 materially 높아 방법론 일치가 필요하다.
  - 판정: 화면 수동 교차검증 외에는 사용하지 않는다.

### FactSet Benchmarks API

- Category: enterprise benchmark/index analytics
- Relevant workflow:
  - `/ratios`가 rolling constituents를 사용해 index-level profitability/valuation/coverage/leverage ratios를 집계
  - historical index price와 constituents endpoint도 제공
- Strong fit:
  - NDX trailing P/E가 entitlement에 포함되면 가장 직접적인 production source
  - Nasdaq 자체 earnings research가 FactSet을 사용하므로 cross-source alignment가 좋음
- Limit:
  - 인증과 별도 entitlement가 필요
  - 공개 가격이 없고 NDX identifier/metric sample을 계약 전에 확인해야 함
- Evidence label: Documented

### LSEG I/B/E/S Global Aggregates / Datastream

- Category: enterprise estimates and aggregate fundamentals
- Relevant workflow:
  - index/country/sector aggregate earnings와 valuation analysis
  - weekly/monthly refresh, 장기 history, DSWS/FTP 제공
  - LSEG는 Nasdaq-100 index data coverage도 별도로 명시
- Strong fit:
  - actual/estimate를 나눠 향후 analyst consensus와 자체 FOMC scenario를 비교하기 좋음
- Limit:
  - 공개 문서가 NDX trailing actual P/E field를 명시하지 않으므로 sample 확인이 필요
  - V1 목표는 consensus가 아니라 actual trailing 기준이므로 I/B/E/S estimates를 그대로 기준 EPS로 쓰면 안 됨
- Evidence label: Documented; exact field Unknown

### Bloomberg Data License

- Category: enterprise data platform
- Relevant workflow:
  - pricing, fundamentals, estimates, historical PIT data를 REST/SFTP/cloud로 제공
  - Nasdaq public research가 Bloomberg/FactSet 기반 NDX fundamentals를 사용
- Strong fit:
  - 기존 Bloomberg 계약이 있다면 field-level extraction과 cross-check가 가능
- Limit:
  - 공개 product page에서는 NDX trailing P/E/EPS mnemonic을 확인할 수 없음
  - 신규 도입만을 위해서는 비용과 계약 범위가 과함
- Evidence label: Claimed/Unknown

### Nasdaq GIW/GIFFD + SEC Self-Construction

- Category: official index composition plus public filing reconstruction
- Relevant workflow:
  - GIW: current/historical components, weights, limited corporate actions
  - GIFFD: 상세 weight/corporate-action/divisor 자료
  - SEC: filing-aware company actuals
- Formula candidate:

```text
constituent earnings yield = PIT TTM EPS / same-date price
index earnings yield = aggregate(weight × constituent earnings yield)
index P/E = 1 / index earnings yield
index EPS = NDX level / index P/E
```

- Strong fit:
  - 가장 투명한 자체 산출과 cross-check가 가능
- Limit:
  - 적자 기업 처리, ADR ratio, 복수 클래스, 통화, corporate action, 리밸런싱을 직접 재현해야 함
  - GIW/GIFFD도 license가 필요하며 public GIDS message spec에는 EPS/P/E field가 없음
  - 현재 QQQ holdings 2 vintages만으로 즉시 60개월을 만들 수 없음
- Evidence label: Documented inputs, Inferred formula

## Cross-Source Patterns

- 지수 가격은 공개/공식 경로가 많지만 historical index fundamentals는 대부분 라이선스 데이터다.
- QQQ 분기 holdings는 SEC에서 5년 이상 무료 backfill되므로, 공식 aggregate가 아니어도 no-auth reconstructed proxy는 가능하다.
- 빠른 구현은 direct aggregate P/E series를 받고 EPS를 `index/P/E`로 역산하는 방법이다.
- strict PIT backtest가 아니라 상대 가치평가/reconstructed scenario라면 provider history를 사용할 수 있지만, release vintage 부재를 반드시 표시해야 한다.
- enterprise provider는 가격보다 constituents/aggregate methodology/entitlement가 핵심 비용 항목이다.

## Architecture Implications

- source raw observations와 derived monthly rows를 분리한다.
- P/E와 EPS를 동시에 받더라도 같은 날짜 identity check를 저장한다.
- React는 provider나 API token을 알지 않고 source/quality/basis/fallback evidence만 표시한다.
