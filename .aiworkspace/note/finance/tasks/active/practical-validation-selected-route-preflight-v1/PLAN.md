# Practical Validation Selected-route Preflight v1

## 이걸 하는 이유?

Practical Validation을 통과해 Final Review로 이동한 뒤, Final Review selected-route gate에서 같은 validation evidence 부족으로 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장이 막히는 흐름이 있었다.

사용자 관점에서는 Final Review로 넘어갔다는 사실이 “선정 저장까지 가능한 후보”처럼 보일 수 있으므로, selected-route 저장을 막을 deterministic evidence gap은 Practical Validation 단계에서 먼저 차단한다.

## Scope

- Practical Validation result 생성 시 Final Review selection gate policy를 preflight로 계산한다.
- selected-route policy가 `blocked` 또는 `hold_or_re_review`이면 `final_review_gate.can_save_and_move=False`로 둔다.
- 차단 사유를 validation module / Fix Queue / gate metadata에 노출한다.
- Final Review와 Selected Portfolio Dashboard의 live approval / order / broker boundary는 변경하지 않는다.

## Out Of Scope

- live approval, 주문, broker/account 연동, 자동 리밸런싱
- registry cleanup 또는 기존 selected row migration
- strategy/backtest 성과 로직 변경
