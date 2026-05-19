# Service Contract Tests Notes

## Findings

- `pytest` is not installed in `.venv`; use `unittest` to avoid adding tooling as part of this boundary task.
- Existing `tests/` only contains ignored `__pycache__` files, so this task creates the first source test file in the current worktree.
- Contract tests should avoid DB, provider fetch, Streamlit runtime, and JSONL registry writes.
