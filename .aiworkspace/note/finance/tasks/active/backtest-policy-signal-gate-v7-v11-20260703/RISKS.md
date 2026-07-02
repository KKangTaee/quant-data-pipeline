# Risks

- `검증 신호 · Policy Signals` UI를 줄일 때 기존 tests가 문자열 기반으로 nested tab 존재를 확인하고 있어 함께 갱신해야 한다.
- `promotion_decision=hold`를 완화하면 실제 final selection 승격과 혼동될 수 있으므로 copy와 snapshot schema에서 “검증 진입” 경계를 분명히 해야 한다.

## Mitigation

- V9에서 active render path의 nested tab 제거 여부를 test로 고정했다.
- V10에서 `can_enter_practical_validation`과 `can_move_to_compare`를 snapshot / source contract에 함께 저장해 조건부 2차 진입과 strict compare 가능 상태를 분리했다.
