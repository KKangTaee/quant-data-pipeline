# Overview Sentiment Common History Alignment Design

## 이걸 하는 이유?

현재 `6M / 1Y / 전체`는 두 그래프에 같은 cutoff를 적용하지만 각 그래프가 남은 관측점으로 x축 범위를 다시 계산한다. 그 결과 CNN은 약 1년, AAII는 약 6개월처럼 보이며 같은 기간을 비교한다는 인상을 주지 못한다.

AAII 공개 HTML은 최근 21주만 제공하지만 같은 공식 페이지가 로그인 없이 받을 수 있는 `sentiment.xls` 전체 이력을 연결한다. 2026-07-20 확인 기준 이 workbook에는 완전한 Bullish / Neutral / Bearish 관측 2,032주가 `1987-07-24~2026-07-16` 범위로 들어 있다. CNN 공식 JSON은 같은 날 251개 일간 headline 관측 `2025-07-21~2026-07-20`을 반환하고, 현재 DB 누적 범위는 `2025-06-04~2026-07-20`이다.

따라서 AAII 장기 이력을 보강한 뒤, 기본 비교 그래프는 CNN이 실제로 존재하는 공통 구간을 같은 x축으로 사용한다.

## 승인 범위

- 3차 독립 데이터 후보 검토는 시작하지 않는다.
- CNN / AAII 외 새 심리 지표를 추가하지 않는다.
- 1W / 1M estimator, 확률, trade/monitoring/validation signal을 추가하지 않는다.
- 이번 작업은 2차의 데이터 coverage와 그래프 비교 정확성 보정이다.

## 검토한 접근

### A. AAII XLS backfill + 공통 x축 — 채택

- AAII 공식 workbook 전체 이력을 canonical DB에 보강한다.
- 일상 PIT 수집은 workbook 최근 bounded window만 저장한다.
- `6M`, `1Y`, `공통 전체`가 두 그래프에 동일한 x축 domain을 전달한다.
- AAII가 가진 1987년 이후 장기 이력은 DB와 coverage 근거에 보존하되 기본 비교 그래프의 `공통 전체`는 CNN 시작일부터 표시한다.

장점은 데이터 가치와 비교 정확성을 모두 보존한다는 점이다. 단점은 AAII 단독 39년 그래프가 기본 화면에 직접 펼쳐지지 않는다는 점이며, coverage 문구로 보완한다.

### B. UI만 AAII 6개월에 맞추기 — 기각

두 그래프를 즉시 같은 길이로 만들 수 있지만 CNN 이력을 불필요하게 버리고 공식 AAII 장기 데이터를 계속 놓친다.

### C. source별 전체 이력을 독립 x축으로 유지 — 기각

각 source의 전체 history 탐색에는 유리하지만 사용자가 지적한 기간 비교 문제를 해결하지 못한다.

## 데이터 원천과 정규화

### AAII 공식 workbook

- URL: `https://www.aaii.com/files/surveys/sentiment.xls`
- sheet: `SENTIMENT`
- 공식 열: `Reported Date`, `Bullish`, `Neutral`, `Bearish`
- 저장 series: 기존 `AAII_BULLISH`, `AAII_NEUTRAL`, `AAII_BEARISH`, `AAII_BULL_BEAR_SPREAD`
- percent fraction은 현재 product 단위인 percent로 변환한다. 예: `0.449074 -> 44.9074`.
- `observation_date`는 workbook의 공식 `Reported Date`를 사용한다.
- 원본 날짜와 세 응답값은 `missing_fields_json` provenance에 보존한다.

### 일상 수집

- AAII primary path는 workbook을 읽어 최신 26주만 반환한다.
- immutable snapshot에 매일 39년 전체를 반복 저장하지 않는다.
- full workbook backfill은 별도 명시 함수로 한 번 실행하거나 필요할 때 갱신한다.
- workbook 실패 시 기존 HTML 최근 표를 보조 경로로 사용할 수 있다. HTML의 최근 Wednesday label은 공식 workbook 주차와 일치하도록 다음 날 anchor로 정규화하고 raw label을 provenance에 남긴다.

### canonical backfill

- workbook fetch와 parse가 성공한 뒤에만 DB transaction을 시작한다.
- workbook 최신일 이하의 기존 AAII canonical row를 공식 workbook view로 교체한다.
- workbook 최신일보다 이후인 prospective row는 삭제하지 않는다.
- 네 AAII series는 한 transaction에서 정렬한다.
- legacy canonical row를 과거 immutable PIT truth로 복제하지 않는다. backfill은 설명용 canonical history이며 PIT coverage 시작일은 기존 2026-07-20을 유지한다.

## 공통 그래프 기간

두 패널은 source coverage의 교집합으로 계산한 하나의 `xDomain = [start, end]`를 사용한다. CNN이 더 오래된 공식 값을 제공하지 못하면 AAII만 존재하는 과거 구간은 기본 비교 그래프에 노출하지 않는다.

- common start: `max(CNN canonical start, AAII canonical start)`
- common end: `min(CNN canonical end, AAII canonical end)`
- `6M`: `max(common start, common end에서 6개월 전)`부터 common end
- `1Y`: `max(common start, common end에서 12개월 전)`부터 common end
- `공통 전체`: common start부터 common end

AAII는 주간이므로 common end는 보통 AAII 최신 주차가 된다. 두 그래프 모두 그 날짜까지만 표시하며, 빈 날짜를 보간하거나 한쪽 선을 coverage 밖으로 연장하지 않는다.

버튼 문구는 `전체` 대신 `공통 전체`를 사용한다. coverage에는 다음 두 의미를 분리한다.

- 비교 구간: 현재 선택된 공통 x축 범위
- 보유 이력: CNN과 AAII 각각의 canonical 전체 범위와 관측 수

## 사용자 흐름

1. 사용자는 기본 `6M`에서 두 source가 모두 존재하는 같은 시작일/종료일만 비교한다.
2. `1Y`도 동일한 1년 x축을 사용한다.
3. `공통 전체`는 두 source가 함께 존재하는 가장 긴 비교 구간을 보여준다.
4. coverage 문구에서 AAII가 1987년부터 보존되어 있지만 공통 비교는 CNN 시작일에 제한됨을 확인한다.
5. AAII 응답 / Spread tab은 같은 공통 domain을 공유한다.

## 실패 처리

- workbook fetch/parse 실패 전에는 canonical AAII row를 변경하지 않는다.
- required column 또는 완전한 관측이 없으면 backfill을 중단한다.
- HTML fallback이 실패하면 기존 source failure batch 계약을 유지하고 값을 생성하지 않는다.
- backfill 이후 네 series의 row count/date range가 일치하지 않으면 transaction을 rollback한다.

## 변경 경계

- `finance/data/sentiment.py`: workbook parser/fetcher, bounded current read, full backfill row build
- `finance/data/sentiment_store.py`: scoped AAII canonical replacement transaction
- `app/jobs/ingestion_jobs.py`: 재사용 가능한 explicit backfill wrapper가 필요할 경우에만 추가
- `app/services/overview/sentiment.py`, `app/web/overview/sentiment_helpers.py`: common range/coverage payload
- `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`: shared x-domain과 `공통 전체` UI
- `tests/test_sentiment_pit.py`, `tests/test_service_contracts.py`, React tests: parser, bounded capture, replacement, payload, x-domain 회귀

## 완료 조건

- AAII canonical history가 공식 workbook 범위로 보강된다.
- 기존 immutable PIT start는 소급 변경되지 않는다.
- `6M / 1Y / 공통 전체`에서 CNN과 AAII SVG x축 domain이 동일하다.
- 모든 기간의 시작/끝은 두 canonical coverage의 교집합 안에 있다.
- 공통 전체의 시작은 두 canonical 시작일 중 늦은 날짜, 끝은 두 canonical 종료일 중 이른 날짜다.
- AAII 응답과 Spread가 동일 domain을 유지한다.
- desktop/420px Browser QA에서 coverage, hover, tab, overflow, console error를 확인한다.
- 1W/1M은 계속 `UNAVAILABLE`이다.
