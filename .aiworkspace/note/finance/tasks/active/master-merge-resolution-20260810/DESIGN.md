# Master Merge Resolution Design

## Integration Direction

- 경제 사이클은 `economic_cycle_v3`의 관측 국면·최근 변화·현재 전환·freshness 계약을
  current product 기준으로 유지한다.
- 물가·정책 경로는 cycle payload에 렌더 직전 합성되는 독립 `inflation_policy_v1`
  탭과 command bridge로 보존한다.
- 공용 `fred_vintages` refactor 위에서 경제 사이클 incremental fetch의 최대 4 worker와
  catalog-order DB write를 유지한다.
- Overview automation에는 경제 사이클 자산 경로와 inflation-policy raw context의
  평일 일일 job을 모두 등록한다.
- 문서는 current code ownership과 DB meaning을 canonical 문서에, 완료 이력은 task와
  root handoff log에 둔다.
