# Notes

- 이 문제는 최근 React local item selection 변경의 회귀가 아니다. 기존 position event V1의
  stock-only 경계와 ETF fixed-shares 등록 허용이 처음부터 불일치했다.
- DB migration 없이 기존 ETF item의 `input_shares`, `entry_close`, `initial_capital`을 사용할 수 있다.
- `fixed_notional`의 fractional virtual units는 실제 보유 수량 원장으로 승격하지 않는다.
- `is_position_ledger_item()`이 command, valuation, selected projection의 단일 shape 판정기다.
- 종료된 stock/ETF는 원장 숫자와 이력을 read-only로 유지하고, 실제 원장이 없는 항목만 숫자 카드·거래 이력을 숨긴다.
- 기존 QQQ/SOXX는 별도 backfill이나 migration 없이 저장된 `input_shares`를 사용했다.
