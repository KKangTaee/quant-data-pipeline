# Phase 4. Backtest Strategy Migration Notes

- Legacy broad `quality_snapshot` runner and display mapping remain for old saved runs and history replay.
- This phase does not delete broad yfinance factor code or tables.
- Quarterly prototypes remain available as explicit family variants, but they are not default and remain non-canonical.
- Browser QA initially hit an ImportError in the long-running pre-change Streamlit process; a clean server restart confirmed the code path imports and renders normally.
