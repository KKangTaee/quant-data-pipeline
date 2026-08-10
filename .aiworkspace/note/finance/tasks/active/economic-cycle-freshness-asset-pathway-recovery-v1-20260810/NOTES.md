# Notes

- 실제 manual refresh baseline: 96.836초, 75.616초.
- 2026-08-10 cycle snapshot은 최신이지만 asset pathway daily rows는 2026-07-27~31에 머물러 별도 freshness scope가 필요하다.
- delayed last-good measurement는 값·관측일·변화량을 표시하되 current signal eligibility는 false로 둔다.
- `STALE_SERIES`는 측정 부재가 아니라 갱신 지연이며, 현재 지지/반대 방향 집계에서는 `UNAVAILABLE`과 동일하게 제외한다.
- 근본 원인은 경기 국면 snapshot 최신성과 자산 경로 입력 최신성을 하나의 상태처럼 취급하고, stale 자산 row를 값 자체가 없는 것으로 조기 반환한 데 있었다.
- 경기 국면과 자산 경로는 서로 다른 cadence와 provider를 가지므로 `cycle_snapshot`과 `asset_pathways` freshness scope를 분리한다.
- 자산 전용 일일 job은 DGS2, DGS10, DFII10, T10YIE, VIXCLS, BAA10Y, EIA 주간 3종, futures 4종, S&P 가격 2종만 bounded하게 보강한다.
- 실제 갱신 뒤 DGS2/DGS10/실질금리/기대인플레이션/신용스프레드/VIX와 시장 가격 경로가 다시 표시됐다. S&P actual EPS는 공식 완료 분기 자료가 없으면 계속 제한 상태로 남는다.
