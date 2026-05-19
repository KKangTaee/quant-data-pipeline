# UI Engine Boundary Foundation Risks

Status: Active
Created: 2026-05-19

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Service layer becomes another mixed UI/runtime layer | High | Ban `streamlit` imports in `app/services`; service returns data only |
| First refactor changes user-visible behavior | High | Move dispatch only; keep session keys and history append in UI first |
| Compare extraction is too broad | High | Do Single Strategy first; split Compare after service pattern is proven |
| Practical Validation conflicts with active V2 work | Medium | First slice only moved source/result append and handoff contract; defer diagnostic formula and provider job changes |
| Registry JSONL gets rewritten accidentally | High | Only use existing append/load helpers; never bulk rewrite registries |
| Engine logic drifts during UI boundary work | Medium | Do not touch `finance/strategy.py`, `finance/engine.py`, `finance/transform.py`, `finance/performance.py` in first task |
| Path drift between `.note` and `.aiworkspace` persists | Medium | Track as cleanup candidate, but do not mix with first service extraction |
| `__pycache__` traces confuse service/API state | Low | Treat current source state as no service/API source files present; ignore generated caches |

## Non-Negotiable Boundaries

- No live trading scope.
- No frontend framework migration.
- No DB schema change.
- No provider remote fetch from UI.
- No generated artifact staging.
