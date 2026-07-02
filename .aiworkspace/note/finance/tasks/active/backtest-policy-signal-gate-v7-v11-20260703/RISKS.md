# Risks

- `검증 신호 · Policy Signals` UI를 줄일 때 기존 tests가 문자열 기반으로 nested tab 존재를 확인하고 있어 함께 갱신해야 한다.
- `promotion_decision=hold`를 완화하면 실제 final selection 승격과 혼동될 수 있으므로 copy와 snapshot schema에서 “검증 진입” 경계를 분명히 해야 한다.
