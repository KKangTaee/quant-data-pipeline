# Nasdaq-100 Index EPS / P/E Source Benchmarks

Status: Complete
Last Updated: 2026-07-12

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
| GuruFocus Economic Data API | 일별 | 분기별 | 가능성이 높음(5Y/20Y chart 및 historical endpoint) | REST | PAYG $0.10/request, Economic Data add-on +$90/month 표시 | Documented | V1 권장 |
| FactSet Benchmarks API | index ratios endpoint | per-share/aggregate content 기반 | 가능 | REST/SDK | entitlement/quote | Documented | Enterprise 최우선 |
| LSEG I/B/E/S Global Aggregates / Datastream | major index aggregate/valuation | actual/estimate aggregate 계열 | 가능성이 높음 | DSWS/FTP/SFTP | enterprise quote | Documented + NDX coverage는 확인 필요 | Enterprise 대안 |
| Bloomberg Data License | historical fundamentals/estimates/price | field entitlement에 따라 가능 | 가능성이 높음 | REST/SFTP/cloud | enterprise quote | Claimed; exact NDX field unknown | 교차검증/대안 |
| Nasdaq GIW/GIFFD + SEC 자체 산출 | 직접 제공 아님 | 직접 제공 아님 | weights entitlement가 있으면 가능 | Web service/file + SEC API | Nasdaq license + 구현비 | Documented/Inferred | 장기 독립성, V1 비권장 |

## Source Notes

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
  - 데이터 장기 저장/표시 권한은 Data API Agreement 확인 필요
- Evidence label: Documented + current cross-check Inferred

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
- 빠른 구현은 direct aggregate P/E series를 받고 EPS를 `index/P/E`로 역산하는 방법이다.
- strict PIT backtest가 아니라 상대 가치평가/reconstructed scenario라면 provider history를 사용할 수 있지만, release vintage 부재를 반드시 표시해야 한다.
- enterprise provider는 가격보다 constituents/aggregate methodology/entitlement가 핵심 비용 항목이다.

## Architecture Implications

- source raw observations와 derived monthly rows를 분리한다.
- P/E와 EPS를 동시에 받더라도 같은 날짜 identity check를 저장한다.
- React는 provider나 API token을 알지 않고 source/quality/basis/fallback evidence만 표시한다.
