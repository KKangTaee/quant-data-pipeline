# Reference Center React V1 Status

Status: Implementation Plan Ready / Execution Choice Pending
Date: 2026-07-20

## Progress

- Existing Reference / Glossary implementation and current product surfaces re-audited.
- User approved keeping Reference capability while removing the separate Guides / Glossary navigation split.
- User approved excluding legacy / developer glossary terms from the app and preserving them only in internal docs.
- Visual comparison completed; Search-first Hybrid option A selected.
- Information architecture, component/data boundary, error handling, drift guard, and QA design approved in conversation.
- Written spec created in `DESIGN.md` and approved by the user.
- File-by-file TDD implementation plan created in `PLAN.md` with nine commit-sized tasks.
- The plan fixes the execution order as catalog/contract, React workbench, navigation/contextual help, then legacy removal/docs/Browser QA.

## Roadmap State

- Overall implementation roadmap: `0/4차`
- Current completed stage: design approval, written specification, and executable TDD plan
- Next stage: choose plan execution mode, then begin Task 1 catalog RED/GREEN cycle

## Not Started

- No product code changes
- No Reference navigation changes
- No catalog migration
- No React component scaffolding
- No legacy renderer removal

## Next Action

Choose subagent-driven execution or inline execution, then start Task 1 without changing the approved scope.
