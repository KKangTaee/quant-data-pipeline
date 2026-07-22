# Today Contributor Performance Cards V1 Notes

## Decisions

- Today는 활성 종목 전체가 아니라 기여 상위 2개·하위 2개를 유지한다.
- `종목 누적 수익률`과 `포트폴리오 누적 기여`를 한 카드 안에서 다른 label로 표시한다.
- 종목 수익률은 lane의 flow-adjusted index를 사용하며 단순 평가액/최초 투자금 비율을 사용하지 않는다.
- 기존 Portfolio Monitoring 사용자 화면과 계산식은 변경하지 않는다.
- canonical contributor row는 `symbol`, `contribution_value`, `total_return`, `tone`이다. `value`는 Python compatibility alias이며 React의 표시·정렬 source가 아니다.
- `tone`은 contribution 부호, return tone은 `total_return` 부호를 각각 사용한다. 두 부호가 같다고 가정하지 않는다.
- `flow_adjusted_index`는 추가매수·일부매도 같은 외부 현금흐름을 단위가치에서 제거하므로 종목 성과를 나타낼 수 있다. `current_value / initial_capital - 1`은 현금흐름을 성과로 오인하므로 fallback으로 사용하지 않는다.

## Current Actual Example

- AMD contribution `+$11,915`
- RKLB contribution `+$4,319`
- TEM contribution `-$401`
- SOXX contribution `-$282`

위 금액은 수익률이 아니라 contribution이다. 실제 종목 return은 각 lane의 마지막 유효 flow-adjusted index에서 투영되며 2026-07-22 Browser QA에서 각각 AMD `+357.97%`, RKLB `+166.56%`, TEM `-21.46%`, SOXX `-7.84%`로 분리 표시됐다.

## Final Boundary

- contributor는 양수 상위 2개와 음수 하위 2개만 보여 주며 전체 보유 종목 목록이 아니다.
- 수익률 자료가 없으면 `수익률 자료 부족`으로 남기고 기여금은 계속 표시한다.
- Today는 저장 결과의 read-only projection이며 provider fetch, DB/schema write, monitoring signal, 주문·리밸런싱을 소유하지 않는다.
