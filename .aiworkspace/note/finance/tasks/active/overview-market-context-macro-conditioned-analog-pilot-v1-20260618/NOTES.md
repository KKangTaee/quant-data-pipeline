# Notes

Status: Active
Last Updated: 2026-06-18

## Observations

- The existing default comparison symbols already include `GLD`, so the pilot can use the same DB-backed price history load path without adding a loader or provider.
- The pilot filters existing broad anchors rather than building a separate scoring model.
- If GLD coverage is unavailable, the broad analog remains visible and only the pilot reports insufficient context.
- The UI keeps sample reduction explicit because macro conditioning can make the sample materially smaller.

## Copy Boundary

New copy avoids Korean terms requested as forbidden in Market Context body:

- 예측
- 추천
- 매수
- 매도
- 신호
- 가능성이 높다
