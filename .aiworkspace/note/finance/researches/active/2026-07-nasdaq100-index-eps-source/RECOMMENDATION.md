# Recommendation

Status: Recommended - Public Filing Reconstruction Pilot
Last Updated: 2026-07-12

## One-Line Recommendation

계정·API token·데이터 구독 없이 진행하려면 QQQ SEC N-PORT와 SEC 기업 실적을 결합한 공개 공시 기반 재구성값을 V1 source로 사용한다.

## Final Recommendation

사용자가 account/token 없는 경로를 우선했으므로 V1의 권장 조달 경로를 공개 공시 기반 자체 재구성으로 변경한다.

1. SEC EDGAR에서 QQQ CIK `0001067839`의 분기별 N-PORT holdings를 수집한다.
2. 2020-12-31~2026-03-31 사이 확인된 22개 분기 snapshot의 종목·수량·평가액·비중을 저장한다.
3. 각 보유 종목의 filing-aware TTM actual EPS/net income을 SEC XBRL에서 계산한다.
4. 분기 snapshot 사이에는 보유 수량/비중을 월말 가격으로 drift시키고, 다음 분기 snapshot에서 다시 anchor한다.
5. 종목 earnings yield를 QQQ weight로 합산해 reconstructed trailing P/E를 만든다.
6. 현재 DB의 QQQ 가격으로 TTM EPS proxy와 FOMC SEP GDP+PCE 적정가 시나리오를 계산한다.
7. UI 명칭은 `Nasdaq-100 (QQQ proxy)` 또는 `QQQ 공개 공시 기반 재구성`으로 표시한다.

이 방식은 공식 Nasdaq index-level P/E가 아니다. 정확한 NDX level 표시가 필요하면 별도 가격 source의 자동 수집/사용 조건을 확인한 뒤 추가하며, V1은 이미 DB에 장기 이력이 있는 QQQ 가격으로 닫는 것이 안전하다.

## Verified Public Coverage

- SEC EDGAR 조회 API는 인증이나 API key가 필요 없다.
- QQQ N-PORT 22건이 2020-12-31부터 2026-03-31까지 분기별로 연속 확인됐다.
- 샘플 2025-03-31 N-PORT에는 101개 holding과 name, CUSIP, ISIN, quantity, USD value, portfolio weight가 포함됐다.
- QQQ 2024 annual filing은 complete holdings가 1·3분기 N-PORT에도 제출된다고 명시한다.
- SEC companyfacts/submissions는 10-K, 10-Q, 20-F 등의 XBRL actual을 인증 없이 제공한다.
- 현재 DB에는 QQQ 일봉 5,105건과 SEC statement 기반 데이터가 있어 신규 외부 계정 없이 pipeline을 확장할 수 있다.

## Cost And Usage Verdict

### Public reconstruction

- 계정: 불필요
- API token/key: 불필요
- 데이터 구독료: 없음
- 필요한 운영 준수: SEC automated access의 User-Agent와 fair-access 정책
- 대가: provider fee 대신 security mapping, ADR ratio, 복수 주식 클래스, 적자 기업, split/corporate action 처리 개발비가 든다.

### Direct aggregate provider option

- 공개 indicator 페이지 조회는 무료다.
- 공개 웹페이지를 robot/scraping으로 반복 수집해 DB에 저장하는 방식은 GuruFocus Terms of Use 경계와 맞지 않으므로 사용하지 않는다.
- Data API 가격표에는 Free `$0`, 월 100 requests가 표시되지만, 같은 페이지에서 Economic Data를 `+$90/month` add-on 및 `$0.10/request` PAYG로도 표시한다.
- 따라서 free token이 indicators `6778`/`5870`의 실제 historical payload를 허용한다고 문서만으로 확정할 수 없다.
- PAYG는 Economic Data `$0.10/request`이지만 초기 `$100` credit top-up이 표시된다.
- Builder는 `$200/month billed annually`이며 Economic Data add-on은 `+$90/month`로 표시된다.
- 일반 Terms of Use는 개인/기관 내부 research를 허용하는 방향이지만, 외부 end-user 앱과 재배포는 commercial data license가 필요하다고 명시한다.
- 이 프로젝트가 사용자 본인/동일 entity의 내부 앱으로만 쓰이는 경우 적합 가능성이 높지만, API Data Agreement의 저장·파생값 표시·계약 종료 후 보유 조건을 별도로 확인해야 한다.

## Why This Route

- 5년 quarterly holdings history가 이미 존재해 앞으로 5년을 기다릴 필요가 없다.
- 현재 구성 종목을 과거에 소급하지 않으므로 survivorship bias를 줄인다.
- SEC filing date를 사용해 earnings look-ahead를 통제할 수 있다.
- 프로젝트의 기존 SEC/QQQ/SEP 자산과 `Ingestion -> DB -> Loader -> Service -> React` 경계를 그대로 활용한다.
- 계정, secret, 월 요청량, 공급자 결제 상태를 운영할 필요가 없다.

## Source Labels

- `eps_source`: `QQQ SEC 보유내역·SEC 기업 실적 기반 재구성 EPS`
- `eps_source_quality`: `public_filing_reconstructed_proxy`
- `pe_source`: `QQQ SEC N-PORT + SEC filing-aware actuals`
- `index_proxy`: `QQQ`
- `fallback_reason`: `무료 공개자료에는 Nasdaq 공식 index-level TTM EPS/P-E 이력이 없어 QQQ 보유내역과 SEC actual로 재구성합니다.`

## Quality Gates Before Implementation Approval

1. 22개 N-PORT 전부의 holdings parse 성공률과 weight 합계를 확인한다.
2. CUSIP/ISIN/LEI -> ticker/CIK security master mapping coverage를 측정한다.
3. 미국 10-K/10-Q와 foreign issuer 20-F/6-K의 TTM actual coverage를 별도로 측정한다.
4. ADR ratio와 Alphabet 같은 복수 클래스의 issuer earnings 중복 배분 규칙을 명시한다.
5. 적자 기업을 제외하지 않고 aggregate earnings에 포함하는 기본식을 검증한다.
6. 분기 snapshot 사이의 price drift와 2023 special rebalance 처리 규칙을 테스트한다.
7. 공개 Nasdaq 연구의 알려진 P/E 관측값으로 오차를 교차검증한다.
8. reconstructed coverage가 95% 미만이거나 calibration 오차가 threshold를 넘으면 graph를 warning 상태로 둔다.
9. missing/revision/negative/zero P/E 처리 계약과 collected_at/filing_available_at을 테스트한다.

## Refresh Cadence

- QQQ price: 기존 trading-day EOD
- QQQ N-PORT: 분기 공시 후 수집, historical backfill 22건
- SEC company actuals: filing ingestion cadence 공유
- reconstructed P/E/EPS: 월말 materialize
- FOMC SEP: 기존 March/June/September/December vintage 수집 공유

## Upgrade Path

- GuruFocus API access/license가 확인되면 reconstructed series의 저비용 교차검증 source로 사용한다.
- FactSet 계약이 가능하면 `/ratios` 기반 NDX aggregate를 production primary로 승격한다.
- LSEG/Bloomberg entitlement가 이미 있다면 같은 60개월 샘플과 공개 재구성값을 비교한다.
- 공식 NDX constituent/divisor 재현이 필요할 때만 Nasdaq GIW/GIFFD license를 검토한다.

## Not Recommended

- 현재 NDX 구성 종목을 5년 전체에 소급 적용
- QQQ holdings 2개 vintage로 과거 5년 합성
- public chart HTML scraping 또는 premium download 접근 우회
- quarterly EPS period-end를 실제 발표일로 간주
- 공개 재구성값을 `Nasdaq 공식 P/E`로 표시
