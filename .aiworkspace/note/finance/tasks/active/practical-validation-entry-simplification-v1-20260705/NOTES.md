# Notes

## 2026-07-05 - Initial Assessment

- `Reference help - Backtest > Practical Validation` is rendered by `render_reference_contextual_help("practical_validation")` in `app/web/backtest_practical_validation/page.py`.
- `시장 심리 Context Overlay` is context-only on Practical Validation and does not affect gate, registry, saved setup, order, approval, or auto rebalance. It is rendered before source selection by `_render_market_sentiment_context_overlay()`.
- `검증 근거를 위한 후보 통제 화면` is the command center title in `render_practical_validation_workspace()`.
- Black rounded cards are owned by `app/web/backtest_practical_validation/components.py`, not the React Fix Queue component.

## 2026-07-05 - Implementation Note

The Practical Validation default entry now starts directly with a clear command center:

- title: `Final Review 이동 전 검증 상태`
- detail: the user should first see whether the candidate can move to Final Review and what needs to be fixed

The sentiment service remains available for other surfaces, but the Practical Validation default entry does not render it because it is not a validation input.

Both the Python-rendered Practical Validation visual shell and the React Fix Queue component now use white square surfaces.
