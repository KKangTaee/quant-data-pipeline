# Risks

- ETF도 split/dividend를 가질 수 있으므로 stock과 동일한 split-first 수량·배당 현금 계약을
  회귀 테스트로 고정해야 한다.
- eligibility 문구만 바꾸고 valuation의 `position_eligible`을 빠뜨리면 action은 보이지만
  원장 계산은 계속 비는 부분 수정이 된다.
- existing fixed-notional ETF를 수량 원장으로 오인하면 가상 fractional units가 실제 보유량처럼
  표시되므로 세 조건의 교집합을 서버에서 검증해야 한다.
