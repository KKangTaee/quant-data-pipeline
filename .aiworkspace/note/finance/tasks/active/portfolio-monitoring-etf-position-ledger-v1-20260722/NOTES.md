# Notes

- 이 문제는 최근 React local item selection 변경의 회귀가 아니다. 기존 position event V1의
  stock-only 경계와 ETF fixed-shares 등록 허용이 처음부터 불일치했다.
- DB migration 없이 기존 ETF item의 `input_shares`, `entry_close`, `initial_capital`을 사용할 수 있다.
- `fixed_notional`의 fractional virtual units는 실제 보유 수량 원장으로 승격하지 않는다.
