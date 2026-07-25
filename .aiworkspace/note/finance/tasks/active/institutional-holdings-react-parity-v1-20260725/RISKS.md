# Institutional Holdings React Parity V1 Risks

## Active Risks

### React Event Rerun Can Lose Local Context

Manager selection, security search, refresh and price collection cross the Streamlit boundary. The implementation must preserve active workspace, disclosure and pending intent until the matching replacement payload arrives.

### Refresh Presentation Migration

Moving the existing Streamlit refresh expander into React must preserve dataset inputs, explicit execution, result feedback and failure handling without turning the normal surface into an operations console.

### Large Source Refactor

The existing TSX and CSS are large and contain mature chart / holdings interactions. Component extraction and visual changes must be separated enough that regressions can be located and reviewed.

### Component Height / Mobile Layout

The custom component relies on dynamic frame height. New disclosures, result messages and responsive stacks must continue to trigger correct `Streamlit.setFrameHeight()` behavior without internal clipping.

### Research Rail / Drawer State Parity

Desktop rail and tablet/mobile drawer must control the same manager and destination state. Breakpoint changes, drawer close and server payload replacement must not reset the current view or leave keyboard focus in a hidden surface.

### Existing Dirty Worktree

Registry, saved portfolio, run history and many generated QA artifacts already exist in the worktree. They must not be staged or modified by this task.

## Deferred Risks

- Standalone React SPA / API migration is a product-wide architecture decision, not this UI task.
- Historical 13F backfill and security-master coverage remain separate data dependencies.
- Current custom price chart remains in place; chart-library migration is not part of visual parity.
