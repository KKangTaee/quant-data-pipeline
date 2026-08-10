# Notes

- 현재 exact net hike buckets는 16.428571%, 26.428571%, 6.428571%이며 합계는
  49.285714%다.
- 기존 PolicyPathPanel은 각 bucket을 정수 반올림해 16% / 26% / 6%로 표시하므로
  사용자가 합산하면 48%로 보인다.
- `net_move_probabilities`는 회의 순서가 아니라 연말 정책금리의 순변화 분포다.
- 실제 DB에는 `2026-08-03T03:15:00` overall/inflation/policy/rates/reverse/equity/
  recession READY snapshot이 있었지만, 기본 loader가 더 큰 origin 시각의 오래된
  `2026-08-03T23:59:59` LIMITED row를 선택하고 있었다.
- 기본 current 조회는 최근 갱신 current materialization, explicit `as_of_at` 조회는
  cutoff 이하 최신 origin이라는 두 의미를 분리했다.
- loader의 current/explicit-as-of 선택 의미가 바뀌어 `PROJECT_MAP.md`,
  `data/README.md`, `DATA_DB_PIPELINE_FLOW.md`를 동기화했다.
