# Notes

- 실제 manual refresh baseline: 96.836초, 75.616초.
- 2026-08-10 cycle snapshot은 최신이지만 asset pathway daily rows는 2026-07-27~31에 머물러 별도 freshness scope가 필요하다.
- delayed last-good measurement는 값·관측일·변화량을 표시하되 current signal eligibility는 false로 둔다.
- `STALE_SERIES`는 측정 부재가 아니라 갱신 지연이며, 현재 지지/반대 방향 집계에서는 `UNAVAILABLE`과 동일하게 제외한다.
