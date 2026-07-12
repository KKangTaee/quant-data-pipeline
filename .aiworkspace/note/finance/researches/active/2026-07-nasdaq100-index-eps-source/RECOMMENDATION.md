# Recommendation

Status: Conditional - Access And License Verification Required
Last Updated: 2026-07-12

## One-Line Recommendation

GuruFocus는 기술적으로 가장 적합하지만 무료 Economic Data 호출과 내부 DB 저장 권한이 확인되기 전에는 개발 source로 승인하지 않는다.

## Final Recommendation

V1의 조건부 권장 조달 경로는 GuruFocus Economic Data API다.

1. `Nasdaq 100 PE Ratio` indicator `6778`의 일별 history를 수집한다.
2. 일별 값을 각 월의 마지막 유효 관측으로 downsample한다.
3. 동일 기준일의 NDX level을 결합한다.
4. `monthly_ttm_eps = ndx_level / trailing_pe`로 월별 TTM EPS proxy를 역산한다.
5. `Nasdaq 100 Earnings per Share` indicator `5870`의 분기 값을 교차검증용으로 저장한다.
6. 기존 FOMC SEP GDP+PCE 시나리오와 log(PER) 계산을 재사용한다.

## Cost And Usage Verdict

- 공개 indicator 페이지 조회는 무료다.
- 공개 웹페이지를 robot/scraping으로 반복 수집해 DB에 저장하는 방식은 GuruFocus Terms of Use 경계와 맞지 않으므로 사용하지 않는다.
- Data API 가격표에는 Free `$0`, 월 100 requests가 표시되지만, 같은 페이지에서 Economic Data를 `+$90/month` add-on 및 `$0.10/request` PAYG로도 표시한다.
- 따라서 free token이 indicators `6778`/`5870`의 실제 historical payload를 허용한다고 문서만으로 확정할 수 없다.
- PAYG는 Economic Data `$0.10/request`이지만 초기 `$100` credit top-up이 표시된다.
- Builder는 `$200/month billed annually`이며 Economic Data add-on은 `+$90/month`로 표시된다.
- 일반 Terms of Use는 개인/기관 내부 research를 허용하는 방향이지만, 외부 end-user 앱과 재배포는 commercial data license가 필요하다고 명시한다.
- 이 프로젝트가 사용자 본인/동일 entity의 내부 앱으로만 쓰이는 경우 적합 가능성이 높지만, API Data Agreement의 저장·파생값 표시·계약 종료 후 보유 조건을 별도로 확인해야 한다.

## Why This Route

- 구성 종목과 가중치를 직접 재구성하지 않아 survivorship/rebalance 오류를 줄인다.
- daily P/E history가 있으므로 60개월을 앞으로 기다리지 않고 즉시 backfill할 수 있다.
- API 문서가 indicator ID 기반 historical response를 제공한다.
- 공개 가격 신호상 enterprise provider보다 작은 비용으로 proof-of-source를 실행할 수 있다.

## Source Labels

- `eps_source`: `GuruFocus Nasdaq-100 trailing P/E 기반 역산 EPS`
- `eps_source_quality`: `third_party_provider_aggregate_derived`
- `pe_source`: `GuruFocus Nasdaq 100 PE Ratio`
- `eps_crosscheck_source`: `GuruFocus Nasdaq 100 Earnings per Share`
- `fallback_reason`: `공개된 Nasdaq 공식 index-level TTM EPS feed가 없어 provider aggregate trailing P/E로 역산합니다.`

## Quality Gates Before Implementation Approval

1. Free Data API account/token으로 indicators 6778/5870을 각각 1회 호출한다.
2. HTTP 200과 최근 60개월 이상의 date/value payload를 실제 확인한다.
3. Free plan에서 Economic Data가 차단되면 paid source를 사용자 승인 없이 구매하지 않는다.
4. P/E가 trailing actual인지 provider support에 서면 확인한다.
5. 로컬 DB 장기 저장, 파생 EPS 저장, 내부 앱 chart 표시, attribution 요구를 provider에 확인한다.
6. 계약 종료 후 raw/derived history 보유 가능 여부를 확인한다.
7. NDX official/FRED close와 같은 날 P/E를 결합해 derived EPS를 계산한다.
8. 분기 EPS와 derived EPS의 오차 분포를 측정한 뒤 warning/block threshold를 정한다.
9. missing/revision/negative/zero P/E 처리 계약을 테스트한다.

## Refresh Cadence

- NDX price: trading-day EOD
- GuruFocus P/E: daily 수집, monthly last-valid row materialize
- GuruFocus EPS cross-check: quarterly
- FOMC SEP: 기존 March/June/September/December vintage 수집 공유

## Upgrade Path

- FactSet 계약이 가능하면 `/ratios` 기반 NDX aggregate를 production primary로 승격한다.
- LSEG/Bloomberg entitlement가 이미 있다면 같은 60개월 샘플을 받아 GuruFocus와 비교한다.
- strict PIT 연구가 필요해질 때만 Nasdaq GIW/GIFFD weights + SEC available-at statements 자체 산출을 별도 데이터 과제로 연다.

## Not Recommended

- 현재 NDX 구성 종목을 5년 전체에 소급 적용
- QQQ holdings 2개 vintage로 과거 5년 합성
- public chart HTML scraping 또는 premium download 접근 우회
- quarterly EPS period-end를 실제 발표일로 간주
