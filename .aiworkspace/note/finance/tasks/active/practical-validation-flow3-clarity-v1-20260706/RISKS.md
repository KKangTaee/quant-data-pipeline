# Risks

## 2026-07-06 - Initial Risks

- Removing too much context from Flow 3 could make source/profile/replay context harder to find. Mitigation: keep Flow 1 / Flow 2 as the source of those details and keep Flow 3 focused on readiness and fix work.
- React component changes require rebuild and Browser QA.
- Generated screenshots, local run history, and other old untracked artifacts must not be staged.

## 2026-07-06 - Residual Risks

- The QA screenshot is a generated artifact and should remain untracked unless the user explicitly asks to commit it.
- `npm audit` still reports 2 dependency warnings in the existing React component dependency tree. This task did not change dependency versions.
