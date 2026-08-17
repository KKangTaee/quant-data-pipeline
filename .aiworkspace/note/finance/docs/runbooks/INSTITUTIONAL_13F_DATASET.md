# Institutional 13F Refresh Runbook

Status: Active
Last Verified: 2026-08-17

## Purpose

`Research > Institutional Holdings`의 관심 기관 최신 분기를 수동 갱신하고, 필요할 때
SEC official bulk ZIP으로 전체 dataset을 복구·재조정한다.

## When To Use

- 제출기한이 지난 새 분기를 관심 기관에 반영할 때
- 화면이 일부 기관만 반영된 `partial` 상태일 때
- 개별 EDGAR 반영 후 official bulk dataset으로 전체 universe를 reconciliation할 때
- SEC 403/429, malformed filing, local DB 오류를 진단할 때

화면 진입 자체는 SEC를 호출하지 않는다. 정상 갱신도 사용자가 버튼을 누른 뒤에만
외부 source discovery와 DB write를 실행한다.

## Prerequisites

- local MySQL과 `finance_meta.institutional_13f_*` schema
- descriptive SEC User-Agent

```bash
export SEC_USER_AGENT="quant-data-pipeline contact@example.com"
```

SEC source:

- Official datasets: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
- EDGAR API: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Fair access: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

## Normal UI Path

1. `Research > Institutional Holdings`를 연다.
2. 접힌 `데이터 기준`을 확인한다.
3. 최신 due 분기가 모두 제출 ledger에 있으면 버튼이 보이지 않고 `최신 보고 분기 반영 완료`다.
4. due/partial이면 `YYYY년 N분기 업데이트 확인 및 갱신`을 한 번 누른다.
5. job은 official bulk listing을 한 번 확인한다.
   - target filing window ZIP이 공개됐으면 bulk dataset을 적재한다.
   - 아직 공개되지 않았으면 curated watchlist의 exact report-period EDGAR filing만 적재한다.
6. 화면이 다시 열리면 report period와 `분기 리뷰`를 확인한다.

정상 버튼은 report period만 server에 전달한다. URL, ZIP path, User-Agent는 받지 않는다.
`13F-NT`는 제출 완료에는 포함하지만 holdings portfolio를 만들지 않는다. Non-notice filing은
parsed holdings count가 `tableEntryTotal`과 정확히 같아야 완료다. 불일치 filing은 filing-only
evidence로 저장하고 버튼 완료 판단·portfolio pointer·holding source에서 제외해 다음 수동
실행에서 다시 확인한다.

## Advanced Recovery Path

1. `Data > Data Operations`를 연다.
2. `SEC Form 13F 데이터셋 수집`을 선택한다.
3. official dataset URL 또는 이미 받은 local ZIP path를 입력한다.
4. dataset label과 descriptive User-Agent를 확인한다.
5. 한 번 실행한 뒤 Institutional Holdings에서 report period와 filing source를 검증한다.

Hybrid normal path는 같은 source URL/report period가 collection ledger에 있으면 bulk를 다시
다운로드하지 않고 `no_update`로 끝낸다. 대형 bulk ZIP의 수동 재현 QA는 검증된 local ZIP을 우선한다.

## Expected Result

```text
explicit click
  -> official bulk discovery
  -> bulk dataset OR curated EDGAR fallback
  -> accession-idempotent manager / filing / holding UPSERT
  -> amendment-aware effective quarter
  -> local due state + v3 quarter review
```

- 같은 accession 재실행은 새 holding row를 쓰지 않는다.
- EDGAR manager 하나의 실패는 다른 manager commit을 되돌리지 않는다.
- restatement는 base를 교체하고 `NEW HOLDINGS` amendment는 base에 추가한다.
- quarter-end/public-follow proxy는 `SH` common-equity의 저장 `adj_close`만 사용하고 coverage와 missing weight를 함께 표시한다. PRN/채권성·우선주성 class, option과 adjusted price가 없는 position은 fail-closed로 제외한다.
- 장기 실행 앱도 runtime loaded-at이 아니라 현재 날짜로 due를 다시 판단한다.
- EDGAR 요청은 submissions/index/XML 각각에 fair-access 간격을 적용한다.

## Verification

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py \
  tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q
.venv/bin/python -m py_compile finance/data/institutional_13f.py \
  finance/data/institutional_13f_edgar.py finance/loaders/institutional_13f.py \
  app/services/institutional_13f_refresh.py app/services/institutional_quarter_review.py \
  app/web/institutional_portfolios.py
(cd app/web/streamlit_components/institutional_portfolios_workbench && npm test && npm run typecheck && npm run build)
git diff --check
```

UI 변경이면 1280/760/420px에서 `분기 리뷰`, page-level overflow와 console error/warning을
확인한다. Screenshot과 local run history는 stage하지 않는다.

## Failure Handling

- SEC 403/429: 반복 호출하지 말고 User-Agent와 pacing을 확인한 뒤 나중에 한 번 재시도한다.
- Bulk candidate 없음: 정상적인 early-quarter 상태다. watchlist EDGAR fallback 결과를 확인한다.
- Primary XML 없음: submissions의 `primaryDocument` basename과 archive `index.json`의 flat
  XML filename을 대조한다. 문서가 둘 이상으로 모호하면 추측해 적재하지 않는다.
- 일부 manager 실패: 성공 manager는 보존하고 partial 상태에서 실패 CIK만 확인한다.
- Amendment type 불명확: last unambiguous base를 유지하고 경고를 표시한다.
- Price/identifier 누락: 0% 수익으로 채우지 않고 coverage를 낮춘다.

## Related Docs

- [Institutional Portfolios Flow](../flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md)
- [Data / DB Pipeline Flow](../architecture/DATA_DB_PIPELINE_FLOW.md)
- [Finance Data And Storage](../data/README.md)
- [Institutional Holdings Hybrid Quarter Review task](../../tasks/active/institutional-holdings-hybrid-quarter-review-v1-20260817/STATUS.md)
