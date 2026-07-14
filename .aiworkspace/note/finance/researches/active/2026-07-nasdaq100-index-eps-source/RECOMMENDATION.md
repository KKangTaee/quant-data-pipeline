# Recommendation

Status: Recommended - Free Public Filing Reconstruction Only
Last Updated: 2026-07-14

## One-Line Recommendation

계정·API token·데이터 구독 없이 진행하려면 QQQ SEC N-PORT와 SEC 기업 실적을 결합한 공개 공시 기반 재구성값을 V1 source로 사용한다.

## 2026-07-14 Provider Refresh

GuruFocus 무료 가능성은 가격표의 동적 feature cell과 Data API Agreement를 직접 확인한 결과 기각한다.

1. **무료·무계정 조건 유지**
   - 기존 QQQ SEC N-PORT + SEC actual 재구성을 유지한다.
   - 공개 차트 HTML scraping은 출처·방법론·자동 수집 권리가 불충분하므로 source로 승격하지 않는다.
2. **GuruFocus 사용**
   - `Economic Indicator List`만 core/free이고, historical value endpoint인 `Economic Data`는 base plan에서 제외된 add-on이다.
   - Economic Data는 `+$90/month` 또는 PAYG `$0.10/request`이며 PAYG는 초기 `$100` credit top-up이 필요하다.
   - 따라서 무료 source 후보에서는 제외하고 사용자가 유료 도입을 별도로 승인할 때만 payload smoke와 계약 확인을 수행한다.
   - indicator `5870`의 NDX EPS는 QQQ-unit EPS와 단위가 다르므로 유료 도입 시에도 화면 값으로 직접 섞지 않고 provider identity check에만 사용한다.

유료 access가 승인되고 Data API Agreement의 내부 저장 범위를 충족하면 GuruFocus P/E를 primary로 전환하는 것은 기술적으로 가능하다. 현재 무료 조건에서는 이 전환을 진행하지 않는다.

### Free Alternative Verdict

- 무료 direct aggregate 외부 원천: 검증된 후보 없음
- 무료 가격 원천: FRED, Alpha Vantage, nfin 등이 있으나 EPS/P-E가 없어 문제를 해결하지 못함
- 무료 기업 재무 보조: Business Quant가 있으나 direct aggregate가 아니고 free history/call limit가 5년 전체 대체에 부족함
- 무료 공개 chart: 자동 수집/재사용 권리 또는 방법론이 불충분해 production source로 부적합
- 유효한 무료 production 경로: SEC EDGAR QQQ N-PORT + SEC issuer actual 자체 재구성

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
- Data API 동적 feature table에서 `Economic Data`는 모든 base plan에서 제외되고 `addon`으로 분류된다. Free의 월 100 requests는 Economic Data entitlement가 아니다.
- 무인증 호출은 401이며 free token만으로 indicators `6778`/`5870` detail을 수집하는 경로는 승인하지 않는다.
- PAYG는 Economic Data `$0.10/request`이지만 초기 `$100` credit top-up이 표시된다.
- Builder는 `$200/month billed annually`이며 Economic Data add-on은 `+$90/month`로 표시된다.
- Data API Agreement는 subscribed product의 승인된 internal product/business use를 허용하고 raw output 공개·재판매·재배포를 금지한다.
- 이 프로젝트가 사용자 본인/동일 entity의 내부 앱으로만 쓰이는 경우 유료 API는 계약상 가능성이 높지만, 계약 종료 후 DB retention과 외부 사용자 제공은 별도 서면 확인이 필요하다.

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

- GuruFocus 유료 Economic Data access/license가 승인되면 indicator `6778`을 primary P/E 후보로, reconstructed series를 교차검증/fallback으로 사용한다.
- FactSet 계약이 가능하면 `/ratios` 기반 NDX aggregate를 production primary로 승격한다.
- LSEG/Bloomberg entitlement가 이미 있다면 같은 60개월 샘플과 공개 재구성값을 비교한다.
- 공식 NDX constituent/divisor 재현이 필요할 때만 Nasdaq GIW/GIFFD license를 검토한다.

## Not Recommended

- 현재 NDX 구성 종목을 5년 전체에 소급 적용
- QQQ holdings 2개 vintage로 과거 5년 합성
- public chart HTML scraping 또는 premium download 접근 우회
- quarterly EPS period-end를 실제 발표일로 간주
- 공개 재구성값을 `Nasdaq 공식 P/E`로 표시
