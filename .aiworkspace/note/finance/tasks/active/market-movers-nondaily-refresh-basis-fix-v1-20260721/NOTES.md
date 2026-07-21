# Notes

## Root Cause

- DB 최신 raw date는 2026-07-17이지만 최신 날짜들의 universe coverage가 임계치보다 작다.
- 랭킹용 `effective_end_date`는 정상적으로 2026-07-07로 fallback한다.
- UI preflight가 이 effective date를 수집 목표일로 다시 사용해 모든 symbol을 current로 오판했다.
- host local date 기반 `_market_movers_today()`도 NYSE 완료 거래일 의미와 일치하지 않았다.

## Implemented Decision

- EOD default target은 `latest_completed_nyse_session()`으로 통일한다.
- 비-Daily UI preflight의 저장된 `as_of_date`가 최신 완료 session과 다르면 다시 계산한다.
- 랭킹 basis는 기존 `effective_end_date`를 유지한다.
- 수동 가격 갱신 action은 target 수가 0이어도 제거하지 않는다.
