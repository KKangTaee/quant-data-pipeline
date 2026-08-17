# Institutional Holdings Hybrid Quarter Review V1 Risks

- SEC submissions and archive structures can vary; parser fixtures must cover namespace and
  document-name differences without guessing missing holdings.
- `13F-HR/A` may restate or add holdings. Treating every latest accession as a full replacement
  would corrupt effective portfolios.
- Watchlist managers do not necessarily file on the same day; partial progress must not be
  represented as complete-quarter universe coverage.
- The full SEC bulk ZIP is large and contains millions of holding rows. Actual QA should not
  repeatedly download/rewrite it when a local verified ZIP is available.
- Existing manager `latest_accession_number` consumers assume one accession owns a complete latest
  portfolio. The implementation plan must identify and update every affected query before enabling
  amendment-composed effective quarters.
- CUSIP/ticker resolution is incomplete and current-state rather than historical PIT. Performance
  coverage must remain explicit and missing weight must not become zero return.
- 13F cannot reconstruct cash, shorts, most derivatives, fees, hedge structure or intra-quarter
  trading. The proxy must not be labeled actual manager return.
- Using quarter-end holdings to measure the already-ended quarter would introduce look-ahead.
  This design instead uses the previous report weights over the following quarter and labels the
  filing-to-filing metric separately.

## Closeout

- 구현/검증 blocker는 없다. 위 항목은 13F 자체의 지속적인 해석 한계와 다음 분기 운영
  주의사항으로 남는다.
- Actual QA에서 SEC archive의 flat XML filename과 notice-only 제출 최신성 문제를 발견해
  회귀 테스트와 함께 수정했다.
- 독립 리뷰에서 bulk notice/empty pointer, non-common/raw-close proxy, startup clock, replay와
  transition selector gap을 발견했고 모두 focused regression과 actual DB/Browser 재검증으로
  수정했다.
- 이후 재리뷰에서 older bulk pointer rollback, partial information table, due target/actual
  freshness 혼동을 발견했다. Pointer는 report period/filing date 단조성을 지키고, parsed row
  count가 `tableEntryTotal`과 정확히 일치하지 않는 filing은 portfolio/freshness에서 제외한다.
- 저장 가격의 `adj_close`가 없는 common-equity와 PRN/채권성·우선주성 class는 성과 coverage에서
  제외한다. 따라서 실제 운용수익이 아니라 계산 가능한 common-equity sleeve만 의미한다.
- Repo-wide pytest는 unrelated Streamlit singleton/Overview/Backtest/Today baseline 362건이
  남아 있다. 이 task의 3개 focused suite는 green이며 broader baseline은 owning task에서 다룬다.
