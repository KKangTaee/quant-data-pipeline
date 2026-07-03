# Status

## Phase 0 - Contract Freeze

- Status: complete.
- Added focused RED/GREEN contract for `build_market_movers_react_workbench_payload` and `market_movers_react_action_plan`.
- Scope is limited to payload/action contract; no rendered UI has changed yet.

## Phase 1 - Component Scaffold

- Status: complete.
- Added a Market Movers custom component Python wrapper with build-directory availability fallback.
- Added the React / Vite frontend scaffold under `app/web/streamlit_components/market_movers_workbench/`.
- Added `node_modules/` to `.gitignore`; build output uses `component_static/` instead of ignored `dist/`.

## Phase 2 - Display Summary Pilot

- Status: complete.
- Routed the Market Movers unified summary through the Streamlit custom component when the built React bundle exists.
- Kept the existing HTML summary as the fallback path when `component_static/index.html` is unavailable.
- Rendered the summary metrics and action strip inside React as a display-only pilot; action execution is still reserved for Phase 3.
- Browser QA confirmed the iframe renders non-empty text and the Vite bundle uses relative assets under Streamlit's component path.

## Phase 3 - React Event Bridge

- Status: complete.
- React action buttons now emit `{event: {id, nonce}}` through `Streamlit.setComponentValue`.
- Python dispatches React action events through the existing Overview action facade and the same session result keys used by the Streamlit buttons.
- React events are consumed once by nonce-backed session tokens to avoid repeated execution after Streamlit reruns.
- Browser QA used only the safe `화면 새로고침` action; provider collection actions were not clicked.

## Phase 4 - Action Strip Integration

- Status: complete.
- When the React workbench renders, the legacy Streamlit refresh button bar is no longer rendered.
- The fallback path still uses the legacy refresh bar when the React build is unavailable.
- A lightweight companion path keeps existing action result messages and daily auto-refresh mode support available without duplicating action buttons.
- Browser QA confirmed parent Streamlit action buttons were removed while React iframe action buttons remained visible.

## Phase 5 - Controls Migration Decision

- Status: complete.
- Top filters remain Streamlit-owned for this pilot because they determine the snapshot before the React workbench payload exists.
- Added `control_ownership` to the React payload and `data-control-mode="streamlit_owned"` to the rendered workbench section.
- Marked `summary_actions` as migrated and `coverage`, `period`, `sector`, `top_n`, `mode`, and `refresh_mode` as deferred.
- Browser QA confirmed the control ownership data attribute renders inside the iframe with no console errors.

## Phase 6 - Refresh Mode Integration Fix

- Status: complete.
- Moved the `방식` / refresh-mode selector into the React workbench action row.
- React now emits `set_refresh_mode` events and Python updates `overview_market_movers_refresh_mode` through the existing session-state boundary.
- The React-rendered companion no longer renders the legacy Streamlit `방식` select below the card.
- `control_ownership` now treats `refresh_mode` as migrated with `summary_actions`; top filters remain deferred.
