# Risks

- Browser QA may be limited if Streamlit app startup or local DB access is slow in this worktree.
- Existing untracked QA images and run history must not be staged.
- React component build artifacts under `frontend/build/` are product assets for custom components; generated QA screenshots remain untracked.
