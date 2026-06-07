# Risks

Status: Completed
Last Verified: 2026-06-07

## Residual Risks

- `app/web/backtest_compare.py` remains large. This is accepted for closeout only because the next split candidates are now explicit.
- `app/web/overview_dashboard.py`, `app/runtime/final_selected_portfolios.py`, and `app/services/overview_market_intelligence.py` are still large and should be considered in future focused rounds.
- Physical task / phase archive migration remains intentionally deferred.
- `backtest-compare-9a-qa.png` is a generated QA screenshot from 9차 and must stay unstaged unless the user explicitly asks to keep it.

## Do Not Infer

- This closeout does not mean the entire product is done.
- This closeout does not approve live trading, broker order execution, account sync, auto rebalance, registry rewrite, or saved JSONL migration.
- This closeout does not remove the need for future product-direction decisions.
