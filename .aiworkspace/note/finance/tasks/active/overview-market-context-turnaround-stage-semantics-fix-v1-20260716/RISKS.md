# Overview Market Context Turnaround Stage Semantics Fix V1 Risks

Last Updated: 2026-07-16

## Guarded Risks

1. EPS unit fix could change multiple issuers at once; query-spy and actual AAPL plus negative-EPS fixtures must cover it.
2. `이미 양수`를 transition MET으로 저장하면 history semantics가 왜곡된다; UI-local display state로만 둔다.
3. profitable-but-flat operating margin must not look like a loss or data failure.
4. copy change must preserve color-independent status text and 420px layout.
5. existing S&P/PER payload and selected-analysis switch must not regress.

## Closed By Verification

- actual negative-EPS company Browser QA는 RIVN으로 완료했다.
- repository-wide 1100-test run은 기존과 같은 4 failures와 154 Streamlit reimport isolation errors로 분류했다.

## Residual

- monolithic discovery의 Streamlit module isolation 오류와 다른 영역 assertion 4건은 이 task 범위 밖의 기존 baseline이다.
- 새 unit alias를 추가할 때는 duration fact unit allowlist와 public-loader query test를 함께 갱신해야 한다.
