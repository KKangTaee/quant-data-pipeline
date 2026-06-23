# Overview Primary Nav Pill V1 Design

## Current Structure

- `app/web/overview_dashboard.py` renders the primary selector in `_render_overview_tab_selector()`.
- The current implementation uses `st.segmented_control` with `st.radio` fallback.
- `OVERVIEW_DEEP_TAB_OPTIONS` and `_render_selected_overview_tab()` already provide the correct four-tab membership and lazy dispatch.

## Direction

Replace the default control with a custom `nav` block rendered through `st.markdown(..., unsafe_allow_html=True)`.

- Keep internal labels as `Market Context`, `Market Movers`, `Sentiment`, `Events`.
- Render user-facing main labels as `시장 맥락`, `변동 종목`, `심리`, `일정`.
- Keep the English label as a small secondary line so screenshots and existing user vocabulary remain recognizable.
- Use query parameter `overview_tab=<slug>` for clickable links, then sync it back to `st.session_state[OVERVIEW_DEEP_TAB_KEY]`.
- Keep fallback behavior: unknown query/session values return `Market Context`.

## Visual Rules

- No full-width segmented box.
- Left-aligned, wrapped, compact items.
- Active item uses quiet surface fill, left accent, and stronger text.
- Inactive items stay border-light and scannable.
- No decorative gradients or large hero-scale text.
