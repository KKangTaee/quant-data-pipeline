# ETF Rerun Matrix Workbench 4B Design

## Read Model

`app/services/backtest_etf_rerun_matrix.py` owns the Streamlit-free contract.

- `build_etf_rerun_matrix_plan()` returns target strategies, scenario rows, counts, and storage boundaries.
- `run_etf_rerun_matrix(strategy_key, runner_map=None)` runs only the selected strategy scenarios.
- default runners call existing DB-backed runtime functions.
- tests inject runner functions so the service contract can be verified without DB or Streamlit.

## UI Flow

Backtest Analysis renders:

1. Strategy Evidence Inventory / Direction Panel
2. Strict Annual ETF Bridge
3. Risk-On Governance
4. ETF Evidence Expansion
5. ETF Current Anchor Workbench
6. ETF Rerun Matrix Workbench

The 4B panel shows scenario plan first. A strategy selectbox plus explicit button runs the selected matrix and stores results in `st.session_state`.

## Persistence Boundary

The service returns compact dictionaries only. It must not import or call run-history appenders, registry writers, saved setup writers, provider snapshot collectors, validation result writers, final review writers, or monitoring writers.
