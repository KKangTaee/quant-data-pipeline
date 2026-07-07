# Notes

- 사전 preset Top-N은 현재 후보군일 뿐이며 PIT Monthly 실행에서는 월별 구성 종목이 달라질 수 있다.
- Run 전 검증은 `이 후보군으로 모든 기간이 안전하다`는 의미가 되면 안 된다.
- Run 후 점검은 runtime이 실제로 제외하거나 사용하지 못한 티커 / 날짜를 기준으로 해야 한다.
- V1 post-run model은 `price_freshness.details`, result table의 `History Excluded Ticker`, `Liquidity Excluded Ticker`를 우선 evidence로 사용한다.
- `persistent_source_gap_or_symbol_issue` 같은 provider gap은 가격 refresh 버튼에서 제외하고 수동 확인 문제로 분리한다.
- 기존 pre-run readiness builder는 호환을 위해 남겼지만 strict annual Quality / Value / Quality+Value form에서는 더 이상 직접 호출하지 않는다.
