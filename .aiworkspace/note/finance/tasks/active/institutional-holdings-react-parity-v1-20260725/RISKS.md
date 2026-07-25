# Institutional Holdings React Parity V1 Risks

## Resolved Risks

### React Event Rerun Can Lose Local Context

Manager/security/refresh/price events retain the existing pending intent. Mobile QA found that an open drawer could survive a rerun, so manager search/selection and dataset refresh now close it before the event.

### Refresh Presentation Migration

React preserves dataset label, URL, local ZIP, User-Agent, explicit execution and result feedback inside a collapsed data disclosure.

### Large Source Refactor

Only the studio shell/navigation was extracted. Mature allocation, holdings, chart and popularity implementations were retained and regression-tested.

### Component Height / Mobile Layout

1280/760/420 actual rendering showed no internal clipping or console warning. Existing `syncFrameHeightSoon` behavior remains.

### Research Rail / Drawer State Parity

Desktop and mobile use one destination list and active view. Drawer closes on destination and server-event actions; Escape returns focus to the menu trigger.

### Existing Dirty Worktree

Registry, saved portfolio, run history and many generated QA artifacts already exist in the worktree. They must not be staged or modified by this task.

## Deferred Risks

- Standalone React SPA / API migration is a product-wide architecture decision, not this UI task.
- Historical 13F backfill and security-master coverage remain separate data dependencies.
- Current custom price chart remains in place; chart-library migration is not part of visual parity.
- The component is still hosted in a Streamlit iframe, so its rail/drawer cannot remain fixed relative to the outer Streamlit scroll viewport. The implemented first-read and event paths are verified; a truly app-global persistent rail would require a product-wide shell change.
