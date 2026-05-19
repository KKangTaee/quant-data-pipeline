# UI Engine Boundary Audit Risks

Status: Active
Created: 2026-05-19

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Starting with Compare makes the first service extraction too large | High | Start with Single Strategy runner |
| Moving history append in the first slice changes persistence behavior | Medium | Keep history append in UI runner initially |
| Service contract over-design delays useful separation | Medium | Use plain dataclass/dict-compatible result before Pydantic/FastAPI |
| Practical Validation extraction conflicts with active V2 | High | Defer until Single/Compare pattern is stable |
| Session state cleanup changes UX | High | Keep session state key names unchanged in first implementation |

## Open Questions

- Should `app/web/runtime/backtest.py` remain under `app/web/runtime`, or later move to `app/services` / `app/runtime` once wrappers are service-owned?
- Should request/result contracts use dataclasses first, or introduce Pydantic after the first extraction?
- Should run history append stay in UI forever, or move to service after explicit write contract is defined?
