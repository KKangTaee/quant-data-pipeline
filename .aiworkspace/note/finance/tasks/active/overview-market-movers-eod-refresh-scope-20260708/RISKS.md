# Risks

- Browser QA may be limited if the local Streamlit server or React build is not available in this worktree.
- Existing dirty/untracked generated artifacts in the worktree must be left untouched.
- Browser screenshot capture stayed on the investigation panel even though DOM confirmed action text; use DOM QA evidence plus screenshot path for handoff.
