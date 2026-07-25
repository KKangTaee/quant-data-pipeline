# Notes

Last Updated: 2026-07-25

## Diagnosis

- `render_economic_cycle()`은 cached DB model과 React component만 렌더링하며 action을
  소비하지 않는다.
- `run_economic_cycle_intramonth_refresh`는 incremental collection, closed-month
  rollover, intramonth materialization을 이미 제공한다.
- 2026-07-21 row는 2026-07-16 source data를 사용해 QA 시 materialize된 결과이며,
  자동 background refresh의 결과가 아니다.
- `python-dotenv` dependency는 이미 설치되어 있다.
- tracked `.gitignore`와 shared `.git/info/exclude`가 `.env` 계열을 보호하며 세 worktree의
  물리적 `.env`는 Git에서 제외된다.

## Decisions

- API key value는 tracked 문서, run log, commit, screenshot에 기록하지 않는다.
- 세 worktree 각각 물리적 `.env`를 둔다.
- latest target은 공휴일 추정 없이 weekday 규칙으로 결정한다.
- `LIMITED`라도 target row가 persisted되면 usable partial success로 취급한다.
- cache invalidation은 persisted postcondition을 통과한 경우에만 수행한다.
- 최신 상태에서는 action을 숨기고 freshness basis만 표시한다.
- 실제 2026-07-25 실행은 17-series pipeline이 usable `partial_success`를 반환했고
  target 2026-07-24 row를 저장했다.
