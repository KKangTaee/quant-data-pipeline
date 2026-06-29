# Overview Market Context Brief Flow Redesign V2 Risks

## Remaining QA Risks

- Streamlit native expander styling for `필요 자료 보강` may still read as a box; accepted for V2 if it remains secondary and collapsed.
- Further source-specific refresh buttons are not implemented in V2; current action still uses the existing bounded Overview refresh facade.
- Browser QA confirmed the top Market Context surface is materially less card-grid-like, but deeper source-specific refresh UX remains a next candidate.

## Boundaries

- Do not stage generated screenshots.
- Do not stage `.DS_Store`, `.superpowers/`, `.playwright-mcp/`, run history, run artifacts, registry JSONL, or saved JSONL.
