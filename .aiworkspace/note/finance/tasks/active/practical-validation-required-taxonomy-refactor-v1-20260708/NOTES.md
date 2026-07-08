# Notes

## Taxonomy Decision

- `validation_efficacy`는 source 계약, latest replay, benchmark parity, provider freshness, PIT, survivorship, execution boundary를 다시 판정하지 않는다.
- `validation_efficacy`는 walk-forward, OOS holdout, regime split의 방법론 강도만 판정한다.
- 방법론 evidence가 아예 없으면 즉시 block이 아니라 `REVIEW`로 둔다. 실제 이동 차단은 owner module의 `NEEDS_INPUT` / `BLOCKED`가 담당한다.

