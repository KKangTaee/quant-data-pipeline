# Design

`run_overview_economic_cycle_refresh`는 이미 월간 목표 `target`과 요청일
`refresh_reference`를 분리한다. Snapshot 조회·공식 국면 완료 판정은 `target`을
유지하고, 두 `asset_freshness_loader` 호출만 `refresh_reference`를 사용한다.
UI read model의 `market_reference`와 일치하는 현재 날짜 검사로 복구한다.

회귀 테스트는 실제 `build_asset_pathway_freshness`와 in-memory 수집 전후 자료를
조합한다. 외부 수집·DB만 대체해 이전 월말 자료를 최신으로 오판하는 경우,
갱신 후 최신 판정, 수집이 개선하지 못한 경우의 실패 판정을 검증한다.

스키마·수집 대상·월간 국면·React UI·일별/주별 허용 지연은 변경하지 않는다.
