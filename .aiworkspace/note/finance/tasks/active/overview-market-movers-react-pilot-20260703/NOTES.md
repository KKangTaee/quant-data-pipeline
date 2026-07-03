# Notes

## Phase 0 Contract

- `build_market_movers_react_workbench_payload` packages the existing unified summary model, current controls, and action descriptors into a JSON-serializable payload for the future React component.
- `market_movers_react_action_plan` maps React action ids to existing Python handler names and required parameters. It is intentionally a plan layer first; execution remains in later phases.
- Daily actions differ from EOD period actions because Daily uses quote snapshots while Weekly / Monthly / Yearly use EOD price history.

## Phase 1 Scaffold

- The Python wrapper returns `None` when `component_static/index.html` is missing, allowing the existing Streamlit/HTML renderer to remain the fallback path.
- The frontend scaffold is intentionally isolated under `app/web/streamlit_components/market_movers_workbench/` so the pilot does not imply a full app migration.

## Phase 2 Display Pilot

- The Market Movers summary now prefers the React custom component and falls back to `render_market_movers_unified_summary` only when the component build is unavailable.
- The React component renders the same summary contract that the existing HTML UI used: title, context, trust state, trust detail, five metric cells, and the action labels.
- Phase 2 keeps action buttons display-only. Python action execution and Streamlit rerun handling remain Phase 3 scope.
- Vite must use `base: "./"` for Streamlit custom components. Without it, the component iframe requests `/assets/...` from the Streamlit root and receives HTML, causing a strict MIME module load failure.
