# Overview Context Refresh / Korean Copy V1 Risks

## Controlled

- The bundle can take time because it runs several provider-backed jobs sequentially; it is manual only.
- Partial failures are summarized and do not block other jobs in the bundle.
- The button uses existing Overview action wrappers and does not add direct UI provider fetch paths.

## Remaining

- Result UX is intentionally compact; source-level retry controls can be a 2차 task.
- Scheduler hardening remains a separate approval decision.
