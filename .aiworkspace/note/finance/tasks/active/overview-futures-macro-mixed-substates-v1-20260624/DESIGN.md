# Overview Futures Macro Mixed Substates V1 Design

## Target Mixed Contexts

The top-level scenario remains `혼재된 매크로 흐름` unless an existing directional scenario rule fires. Inside that scenario, the read model adds a Korean `sub_scenario` and `mixed_reason`.

Initial subtypes:

- `성장 약세 + 방어 확인 부족`: risk-on / growth are weak, but safe-haven demand is not strong enough for risk-off.
- `위험선호 약세 + 금리 부담 완화`: risk assets are weak while rate pressure is easing, so the message is not simple rate shock.
- `원자재/물가 약세 혼재`: inflation pressure is easing or commodities are weak, but the rest of the tape does not confirm risk-on.
- `달러/위험자산 충돌`: dollar pressure is elevated while risk-on is not decisively negative.
- `저신호 / 방향성 없음`: no axis is strong enough to describe the day.

## Data Flow

`generate_market_interpretation` already reads six score values plus key standardized symbols. It will keep existing directional `if/elif` order. Only the final fallback branch calls a helper that chooses a mixed subtype and returns additional fields.

## UI Flow

`_futures_market_brief_model` should surface the subtype without replacing the primary scenario. The hero remains clear:

```text
혼재된 매크로 흐름
성장 약세 + 방어 확인 부족
...
```

The subtype is supporting context, not a signal.

## Testing

Use `tests/test_service_contracts.py` futures macro tests. Add RED tests directly against `generate_market_interpretation` for representative score/symbol fixtures and `_futures_market_brief_model` for display copy.
