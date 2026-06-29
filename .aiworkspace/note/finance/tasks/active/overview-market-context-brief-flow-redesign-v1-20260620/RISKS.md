# Overview Market Context Brief Flow Redesign V1 Risks

## Active Risks

- Refresh action could regress into a job/status table surface in future edits; keep run diagnostics collapsed behind source-readiness copy.
- Market Context still uses Streamlit native select/date widgets, so the controls are visually separate from the HTML section even though they are now placed in the historical analog flow.
- The current batch refresh runs the existing broad Overview refresh facade. A future task can add more targeted source-specific buttons if the user wants less broad collection.

## Boundaries

- Do not stage generated screenshots, run history, run artifacts, `.DS_Store`, `.superpowers/`, registry JSONL, or saved JSONL.
- Do not add provider fetches in UI render.
- Do not add FRED / events / sentiment hard filtering.
