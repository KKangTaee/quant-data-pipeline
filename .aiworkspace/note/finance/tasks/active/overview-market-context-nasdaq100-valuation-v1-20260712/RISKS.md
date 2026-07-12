# Overview Market Context Nasdaq-100 Valuation V1 Risks

Status: Active
Last Updated: 2026-07-12

| Risk | Impact | Mitigation |
|---|---|---|
| QQQ proxy vs official NDX aggregate | official P/E로 오인 | proxy/quality badge와 limitation 상시 표시 |
| pre-2019 annual holdings anchors | early 3/5-year rolling band 정밀도 저하 | anchor quality field와 history limitation 표시 |
| ADR/foreign issuer EPS units | EPS/price 단위 불일치 | explicit conversion만 허용, 불명확 weight는 missing |
| Alphabet/multi-class issuer | double count/incorrect per-share mapping | class-aware CUSIP mapping과 same-issuer EPS contract test |
| SEC EPS duration context | YTD fact를 single-quarter로 오인 | duration filter와 Q4 FY subtraction tests |
| negative earnings | vendor와 aggregate convention 차이 | negative yield 포함, public P/E median 5%/maximum 10% calibration gate |
| price split alignment | historical EPS/price mismatch | accession available-at와 raw close를 같은 시점 기준으로 결합 |
| historical holding symbol mapping | survivorship/coverage 저하 | CUSIP exact, SEC identity, reviewed overrides, coverage gate |
| current DB statements/prices missing | derived month gaps | missing weighted coverage를 명시하고 95% 미만 block |
| remote SEC format/rate changes | ingestion failure | User-Agent, bounded requests, fixture tests, latest good DB state 유지 |
