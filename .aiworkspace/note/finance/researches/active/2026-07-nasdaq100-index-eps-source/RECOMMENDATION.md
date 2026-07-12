# Recommendation

Status: Complete
Last Updated: 2026-07-12

## One-Line Recommendation

GuruFocus의 일별 NDX trailing P/E를 월말로 저장하고 NDX/P-E로 월별 EPS를 역산하되, 분기 EPS indicator를 교차검증으로 사용한다.

## Final Recommendation

V1의 권장 조달 경로는 GuruFocus Economic Data API다.

1. `Nasdaq 100 PE Ratio` indicator `6778`의 일별 history를 수집한다.
2. 일별 값을 각 월의 마지막 유효 관측으로 downsample한다.
3. 동일 기준일의 NDX level을 결합한다.
4. `monthly_ttm_eps = ndx_level / trailing_pe`로 월별 TTM EPS proxy를 역산한다.
5. `Nasdaq 100 Earnings per Share` indicator `5870`의 분기 값을 교차검증용으로 저장한다.
6. 기존 FOMC SEP GDP+PCE 시나리오와 log(PER) 계산을 재사용한다.

## Why This Route

- 구성 종목과 가중치를 직접 재구성하지 않아 survivorship/rebalance 오류를 줄인다.
- daily P/E history가 있으므로 60개월을 앞으로 기다리지 않고 즉시 backfill할 수 있다.
- API 문서가 indicator ID 기반 historical response를 제공한다.
- 공개 가격 신호상 enterprise provider보다 작은 비용으로 proof-of-source를 실행할 수 있다.

## Source Labels

- `eps_source`: `GuruFocus Nasdaq-100 trailing P/E 기반 역산 EPS`
- `eps_source_quality`: `licensed_provider_aggregate_derived`
- `pe_source`: `GuruFocus Nasdaq 100 PE Ratio`
- `eps_crosscheck_source`: `GuruFocus Nasdaq 100 Earnings per Share`
- `fallback_reason`: `공개된 Nasdaq 공식 index-level TTM EPS feed가 없어 provider aggregate trailing P/E로 역산합니다.`

## Quality Gates Before Implementation Approval

1. API trial/PAYG token으로 indicators 6778/5870 payload 구조를 확인한다.
2. 6778이 최근 60개월 이상의 date/value를 실제 반환하는지 확인한다.
3. P/E가 trailing actual인지 provider support에 서면 확인한다.
4. 로컬 DB 장기 저장과 앱 표시가 Data API Agreement에 허용되는지 확인한다.
5. NDX official/FRED close와 같은 날 P/E를 결합해 derived EPS를 계산한다.
6. 분기 EPS와 derived EPS의 오차 분포를 측정한 뒤 warning/block threshold를 정한다.
7. missing/revision/negative/zero P/E 처리 계약을 테스트한다.

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
