# Backtest Analysis Direction Reset 4C Design

## UI Shape

Backtest Analysis should read in this order:

1. Short Korean purpose line.
2. Analysis mode selector.
3. Single Strategy or Portfolio Mix Builder working area.
4. A small `전략 개발 참고` section.
5. Reference / evidence / governance panels only when the user explicitly opens the reference board.

## Read Model

`app/services/backtest_analysis_research_board.py` will classify:

- Reference help
- Strategy Evidence Inventory / Direction Panel
- Strict Annual + GTAA / Equal Weight Bridge
- Risk-On Momentum 5D Governance
- ETF Evidence Expansion
- ETF Current Anchor Workbench
- ETF Rerun Matrix Workbench

The model does not read DB, registries, saved setup, or run history. It only describes placement and classification.

## Panel Policy

- Basic execution flow: visible by default.
- Research / evidence panels: hidden by default.
- If opened, panels are still read-only / session-only according to their existing contracts.
- No panel creates live approval, broker order, auto rebalance, registry write, saved setup write, run history rewrite, or provider snapshot.
