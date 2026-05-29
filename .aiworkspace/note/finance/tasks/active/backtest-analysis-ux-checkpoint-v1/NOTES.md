# Backtest Analysis UX Checkpoint V1 Notes

## Findings

- `Runtime Payload` is rendered openly in `app/web/backtest_single_runner.py`, making the normal run path feel developer-oriented.
- `Latest Backtest Run` currently mixes reading order and available views in adjacent text blocks, which weakens hierarchy.
- `Practical Validation Handoff` is placed before the strategy result and can read like a validation metric instead of a next action.
- `Real-Money > 현재 판단` still says `5단계 Compare 진입 평가` and `4단계 blocker`, which conflicts with the current 4-stage product flow.

## Terminology Decision

- `Stage`: product workflow screen, such as Backtest Analysis, Practical Validation, Final Review, Selected Portfolio Dashboard.
- `검증 체크포인트`: evidence/check layer inside or across stages, such as Result Integrity, Candidate Readiness, Practical Evidence, Final Decision Gate, Monitoring Check.
