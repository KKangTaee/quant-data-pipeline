# Today Contributor Performance Cards V1 Notes

## Decisions

- Today는 활성 종목 전체가 아니라 기여 상위 2개·하위 2개를 유지한다.
- `종목 누적 수익률`과 `포트폴리오 누적 기여`를 한 카드 안에서 다른 label로 표시한다.
- 종목 수익률은 lane의 flow-adjusted index를 사용하며 단순 평가액/최초 투자금 비율을 사용하지 않는다.
- 기존 Portfolio Monitoring 사용자 화면과 계산식은 변경하지 않는다.

## Current Actual Example

- AMD contribution `+$11,915`
- RKLB contribution `+$4,319`
- TEM contribution `-$401`
- SOXX contribution `-$282`

위 금액은 수익률이 아니라 contribution이다. 정확한 종목 return은 구현 시 각 lane의 마지막 flow-adjusted index에서 투영한다.
