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

## Phase 3 Event Bridge

- React emits only action ids plus a nonce. Python remains the owner of provider calls, DB writes, run-history recording, and reruns.
- `_dispatch_market_movers_react_event` intentionally reuses the same `run_overview_*` facade functions and session result keys as the previous Streamlit buttons.
- Event nonce consumption is required because custom component values can remain available after a rerun; without it, a clicked action could repeat on the next render.
- Browser QA should use `reload` for bridge checks unless a later phase explicitly approves a live data collection click.

## Phase 4 Action Integration

- `render_market_movers_snapshot` now treats `react_event is None` as the fallback signal. Only that path renders the legacy Streamlit refresh bar.
- The React-rendered path calls `_render_market_movers_react_refresh_companion` so action results and daily auto-refresh mode remain available without duplicating the main action buttons.
- This phase intentionally does not migrate the top filter controls. Coverage, period, sector, top N, and ranking mode remain Streamlit-owned until the Phase 5 decision.

## Phase 5 Controls Decision

- Decision: keep top filters Streamlit-owned in this pilot. They feed `_load_market_movers_snapshot` before the React workbench payload is built, so moving them now would require a second pre-load component and a separate state synchronization pass.
- Initial contract kept only `summary_actions` migrated; Phase 6 supersedes that by moving `refresh_mode` into the React action strip as well.
- If a later pass migrates filters, it should start by introducing a dedicated pre-snapshot controls component rather than expanding the summary/action workbench payload in place.

## Phase 6 Refresh Mode Correction

- User feedback showed that leaving `방식` below the React card made the UI feel less coherent even after action buttons moved into the card.
- Correction: treat `refresh_mode` as part of the action strip, not as a top filter. It now lives in React while Coverage / Period / Sector / Top N / ranking mode remain Streamlit-owned.
- React emits `set_refresh_mode` with a value and nonce. Python validates the value against the current coverage/period options before updating `overview_market_movers_refresh_mode`.
