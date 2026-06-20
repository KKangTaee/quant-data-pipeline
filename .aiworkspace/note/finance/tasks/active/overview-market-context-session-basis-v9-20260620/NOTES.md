# Notes

## User Problem

- On Saturday / US market holiday periods, Market Context still says `오늘의 시장 브리프`.
- Intraday snapshot age can make the tab suggest refresh even when a new market snapshot cannot exist because the market is closed.
- The brief should anchor to the last market session / last stored market basis and make that clear.

## Decision

- Market Context needs an explicit session basis contract.
- `오늘의 시장 브리프` is appropriate only during an open trading session.
- Closed sessions should display `마지막 거래일 시장 브리프` or equivalent, with the actual stored basis date/time visible.
- Intraday stale caused only by closed-session elapsed time should become closed-session reference context, not an actionable current issue.
